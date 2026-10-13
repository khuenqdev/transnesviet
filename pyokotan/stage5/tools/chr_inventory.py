#!/usr/bin/env python3
"""Build a physical CHR-ROM tile inventory and high-resolution atlases.

This tool treats CHR ROM as raw 2bpp NES 8x8 tiles. The resulting tile index
is a physical ROM tile index, NOT proof that a game text byte maps to that tile.
Usage: python chr_inventory.py pyokotan.nes --outdir outputs --refdir reference
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, zlib
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HEADER=16
TILE_BYTES=16
TILE_PIXELS=64


def parse_rom(path: Path):
    raw=path.read_bytes()
    if len(raw)<16 or raw[:4] != b'NES\x1a':
        raise ValueError('ROM has no iNES/NES 2.0 signature')
    h=raw[:16]
    if (h[7]&0x0C)==0x08:
        p_msb=h[9]&0x0F; c_msb=(h[9]>>4)&0x0F
    else:
        p_msb=c_msb=0
    if p_msb==0x0F or c_msb==0x0F:
        raise ValueError('NES 2.0 exponent/multiplier ROM sizes are not implemented by this utility')
    psize=(h[4]|(p_msb<<8))*0x4000
    csize=(h[5]|(c_msb<<8))*0x2000
    chr_start=HEADER+psize
    chr_rom=raw[chr_start:chr_start+csize]
    if len(chr_rom)!=csize or not csize or csize%TILE_BYTES:
        raise ValueError(f'Unexpected CHR ROM size: declared {csize}, found {len(chr_rom)}')
    mapper=(h[6]>>4)|(h[7]&0xF0)|((h[8]&0x0F)<<8)
    return raw,h,chr_rom,chr_start,mapper


def decode_tile(tile: bytes):
    rows=[]
    for y in range(8):
        p0,p1=tile[y],tile[y+8]
        rows.append([((p0>>(7-x))&1)|(((p1>>(7-x))&1)<<1) for x in range(8)])
    return rows


def tile_bbox(pix):
    coords=[(x,y) for y in range(8) for x in range(8) if pix[y][x]]
    if not coords: return None
    xs=[p[0] for p in coords]; ys=[p[1] for p in coords]
    return [min(xs),min(ys),max(xs),max(ys)]


def tile_hash(tile: bytes):
    return hashlib.sha1(tile).hexdigest()[:16]


def draw_atlas(chr_rom: bytes, tile_first: int, count: int, scale: int, out: Path, cols: int=16):
    count=min(count,max(0,len(chr_rom)//16-tile_first))
    if count<=0: raise ValueError('Atlas start tile is beyond CHR ROM')
    label_h=16
    cell_w=8*scale
    cell_h=8*scale+label_h
    rows=math.ceil(count/cols)
    im=Image.new('RGB',(cols*cell_w,rows*cell_h),(250,250,250))
    d=ImageDraw.Draw(im); font=ImageFont.load_default()
    tile_count=len(chr_rom)//16
    for j in range(count):
        ti=tile_first+j; t=chr_rom[ti*16:ti*16+16]; pix=decode_tile(t)
        ox=(j%cols)*cell_w; oy=(j//cols)*cell_h
        d.text((ox+1,oy+1),f'{ti:04X}',fill=(20,20,20),font=font)
        for y in range(8):
            for x in range(8):
                v=pix[y][x]
                if v:
                    # Neutral grayscale palette: pattern plane values remain visually distinct.
                    shade={1:184,2:125,3:66}[v]
                    x0=ox+x*scale; y0=oy+label_h+y*scale
                    d.rectangle((x0,y0,x0+scale-1,y0+scale-1),fill=(shade,shade,shade))
    out.parent.mkdir(parents=True,exist_ok=True); im.save(out)
    return {'file':out.name,'tile_first':tile_first,'tile_count':count,'scale':scale,'cols':cols,'rows':rows,'width':im.width,'height':im.height}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path)
    ap.add_argument('--outdir',type=Path,default=Path('outputs'))
    ap.add_argument('--refdir',type=Path,default=Path('reference'))
    ap.add_argument('--all-bank-atlases',action='store_true',help='Create one thumbnail atlas per physical 8 KiB CHR page')
    a=ap.parse_args()
    raw,h,chr_rom,chr_start,mapper=parse_rom(a.rom)
    outdir=a.outdir; refdir=a.refdir; outdir.mkdir(parents=True,exist_ok=True); refdir.mkdir(parents=True,exist_ok=True)
    total=len(chr_rom)//16; groups=defaultdict(list); records=[]; bank_rows=[]
    # mapper 69 exposes eight 1 KiB CHR windows; also report physical 8 KiB pages for convenience.
    for ti in range(total):
        t=chr_rom[ti*16:ti*16+16]; pix=decode_tile(t)
        vals=[v for row in pix for v in row]
        nonzero=sum(v!=0 for v in vals)
        colors=sorted(set(vals))
        bbox=tile_bbox(pix)
        hsh=tile_hash(t); groups[hsh].append(ti)
        phys_off=ti*16
        r={
            'physical_tile_index':ti,
            'physical_chr_offset':f'0x{phys_off:05X}',
            'file_absolute_offset':f'0x{chr_start+phys_off:06X}',
            'physical_chr_8k_page':phys_off//0x2000,
            'tile_index_in_8k_page':(phys_off%0x2000)//16,
            'mapper_1k_chr_bank':phys_off//0x400,
            'tile_index_in_1k_bank':(phys_off%0x400)//16,
            'raw_hex':t.hex(' ').upper(),
            'sha1_16byte_prefix':hsh,
            'nonzero_pixels':nonzero,
            'nonzero_pixel_ratio':round(nonzero/64,4),
            'colors_used':' '.join(str(c) for c in colors),
            'color_count':len(colors),
            'bbox_xyxy': '' if bbox is None else ','.join(str(v) for v in bbox),
            'is_blank':nonzero==0,
            'exact_duplicate_count_pending':0,
            'exact_duplicate_indices_pending':''
        }
        records.append(r)
    for r in records:
        inds=groups[r['sha1_16byte_prefix']]
        r['exact_duplicate_count_pending']=len(inds)
        r['exact_duplicate_indices_pending']=' '.join(f'{i:04X}' for i in inds[:64])
    # User-friendly stable names.
    csv_path=outdir/'pyokotan_chr_tile_inventory_v5.csv'
    with csv_path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0].keys())); w.writeheader(); w.writerows(records)
    json_path=outdir/'pyokotan_chr_tile_inventory_v5.json'
    with json_path.open('w',encoding='utf-8') as f:
        json.dump({'schema_version':'1.0','rom':a.rom.name,'rom_sha1':hashlib.sha1(raw).hexdigest(),
          'mapper':mapper,'chr_rom_bytes':len(chr_rom),'chr_tiles_total':total,'tile_format':'NES 2bpp, 8x8 px, 16 bytes per tile',
          'warning':'Physical CHR tile indices are not proven to equal text bytes. Mapper 69 selects CHR in 1 KiB windows at runtime.',
          'tile_records':records},f,indent=2,ensure_ascii=False); f.write('\n')
    # Aggregate each physical 8KiB page (mapper exposes 1KiB banks, not 8KiB pages).
    for page in range(math.ceil(len(chr_rom)/0x2000)):
        sub=records[page*512:min((page+1)*512,len(records))]
        bank_rows.append({'physical_chr_8k_page':page,'chr_offset_start':f'0x{page*0x2000:05X}',
          'tile_start':page*512,'tile_count':len(sub),'nonblank_tiles':sum(not r['is_blank'] for r in sub),
          'unique_patterns':len({r['sha1_16byte_prefix'] for r in sub}),
          'mean_nonzero_pixel_ratio':round(sum(r['nonzero_pixel_ratio'] for r in sub)/max(1,len(sub)),4),
          'mapper_1k_chr_bank_range':f'{page*8:03d}-{page*8+7:03d}'})
    bank_csv=outdir/'pyokotan_chr_page_summary_v5.csv'
    with bank_csv.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(bank_rows[0].keys())); w.writeheader(); w.writerows(bank_rows)
    dup_groups=[{'sha1_16byte_prefix':k,'count':len(v),'physical_tile_indices':v} for k,v in groups.items() if len(v)>1]
    duplicate_json=outdir/'pyokotan_chr_exact_duplicates_v5.json'
    duplicate_json.write_text(json.dumps({'schema_version':'1.0','duplicate_group_count':len(dup_groups),'duplicate_tile_instances':sum(x['count'] for x in dup_groups),'groups':sorted(dup_groups,key=lambda x:(-x['count'],x['physical_tile_indices'][0]))},indent=2)+'\n',encoding='utf-8')
    atlas_meta=[]
    atlas_meta.append(draw_atlas(chr_rom,0,256,6,refdir/'chr_tiles_0000_00ff_upscaled.png'))
    atlas_meta.append(draw_atlas(chr_rom,256,256,6,refdir/'chr_tiles_0100_01ff_upscaled.png'))
    atlas_meta.append(draw_atlas(chr_rom,0,512,3,refdir/'chr_physical_page_00_full.png'))
    # Generate all 16 physical 8 KiB page atlases if requested; each is small enough to inspect.
    if a.all_bank_atlases:
        for page in range(math.ceil(len(chr_rom)/0x2000)):
            first=page*512; count=min(512,total-first)
            atlas_meta.append(draw_atlas(chr_rom,first,count,2,refdir/f'chr_physical_page_{page:02d}.png'))
    # Candidate text glyph catalog separates evidence levels and avoids pretending that tile indices are text codes.
    candidate_rows=[]
    provisional={0x90:'ー',0x91:'ア',0x92:'イ',0x93:'ウ',0x94:'エ',0x95:'オ',0x96:'カ',0x97:'キ',0x98:'ク',0x99:'ケ',0x9A:'コ',0x9B:'サ',0x9C:'シ',0x9D:'ス',0x9E:'セ',0x9F:'ソ',0xB0:'ー'}
    for ti in range(256):
        rr=records[ti]
        ch=''; status='unmapped_visual_candidate'
        if ti==0x20: ch=' '; status='ascii_confirmed_in_literal_data'
        elif 0x21<=ti<=0x7E:
            ch=chr(ti); status='ascii_confirmed_in_literal_data'
        elif ti in provisional:
            ch=provisional[ti]; status='provisional_visual_candidate_not_runtime_verified'
        elif rr['is_blank']:
            ch=''; status='blank_tile'
        candidate_rows.append({'tile_index_hex':f'{ti:02X}','candidate_character':ch,'mapping_status':status,
            'physical_chr_offset':rr['physical_chr_offset'],'nonzero_pixels':rr['nonzero_pixels'],
            'sha1_16byte_prefix':rr['sha1_16byte_prefix'],'comments':'Visual tile identity and runtime code-to-tile mapping are separate questions.'})
    can_csv=outdir/'pyokotan_font_candidate_catalog_v5.csv'
    with can_csv.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(candidate_rows[0].keys())); w.writeheader(); w.writerows(candidate_rows)
    can_json=outdir/'pyokotan_font_candidate_catalog_v5.json'
    can_json.write_text(json.dumps({'schema_version':'1.0','rom_sha1':hashlib.sha1(raw).hexdigest(),
      'count':len(candidate_rows),'records':candidate_rows,
      'note':'ASCII mappings are backed by literal embedded strings. The kana assignments are visual candidates from the atlas and are not a validated script encoding.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    summary={'schema_version':'1.0','rom':a.rom.name,'rom_sha1':hashlib.sha1(raw).hexdigest(),'mapper':mapper,
      'chr_rom_bytes':len(chr_rom),'physical_chr_tiles':total,'physical_chr_8k_pages':len(bank_rows),'mapper_1k_chr_bank_count':len(chr_rom)//0x400,
      'blank_tiles':sum(r['is_blank'] for r in records),'nonblank_tiles':sum(not r['is_blank'] for r in records),
      'unique_exact_patterns':len(groups),'duplicate_pattern_groups':len(dup_groups),
      'physical_page_summary':bank_rows,'atlas_outputs':atlas_meta,
      'interpretation':'CHR tile inventory and atlases provide visual evidence for physical glyph patterns. They do not by themselves prove that any dialogue byte directly equals a physical tile index; mapper 69 CHR bank state must be captured at runtime.'}
    (outdir/'pyokotan_chr_inventory_summary_v5.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'chr_tiles':total,'pages':len(bank_rows),'unique_patterns':len(groups),'blank_tiles':summary['blank_tiles'],'outdir':str(outdir)},indent=2))

if __name__=='__main__': main()
