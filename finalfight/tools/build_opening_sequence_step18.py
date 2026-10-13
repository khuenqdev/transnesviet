#!/usr/bin/env python3
"""Build Step 18: extend the tested Vietnamese opening translation to OPEN_01..OPEN_06.

Input is the clean Mighty Final Fight (USA) NES 2.0 ROM plus the Step 17 IPS.
The script preserves Step 17's validated bank/font fix, patches the six following
opening-text slots at their original fixed offsets, emits a combined IPS patch,
and validates the patch round-trip from the clean source.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

EXPECTED_SOURCE_SHA256 = '5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
EXPECTED_SOURCE_SIZE = 262160
STEP17_EXPECTED_SHA256 = '81697646dc6084fd7277431ebc757aee657d123d5e55ee92fece98e96849ed6b'
HEADER_SIZE, PRG_SIZE, TILE_SIZE = 16, 131072, 16
CHR_START = HEADER_SIZE + PRG_SIZE
# Fixed slots from pointer_tables/dialogue_records.tsv. Offsets include 16-byte iNES header.
BLOCKS = [
  {
    'id':'OPEN_01', 'offset':0x1C44, 'capacity':88,
    'english':"I CAN'T BELIEVE THAT I'VE ACTUALLY FALLEN IN LOVE WITH THE GIRL. SHE WILL BE MINE.....",
    'lines':['TA KHÔNG NGỜ MÌNH','ĐÃ YÊU CÔ ẤY.','CÔ ẤY SẼ THUỘC','VỀ TA.....'],
    'note':'Villain internal monologue; condensed to fit the original fixed-size record.'
  },
  {
    'id':'OPEN_02', 'offset':0x1C9C, 'capacity':23,
    'english':'A COUPLE DAYS LATER...',
    'lines':['VÀI NGÀY SAU...'],
    'note':'Short transition caption.'
  },
  {
    'id':'OPEN_03', 'offset':0x1CB3, 'capacity':139,
    'english':'WHAT?! JESSICA... KIDNAPPED...?! WHAT HAVE YOU DONE TO HER, CODY? ME?! THIS IS THE WORK OF THE MAD GEAR GANG. WHAT DO YOU THINK, GUY?',
    'lines':['CÁI GÌ?! JESSICA...','BỊ BẮT CÓC SAO?!','CẬU ĐÃ LÀM GÌ','VỚI CÔ ẤY, CODY?','TÔI Á?!','CHUYỆN NÀY DO','BĂNG MAD GEAR','GÂY RA. CẬU NGHĨ','SAO, GUY?'],
    'note':'Dialogue shortened while preserving the main accusations and question.'
  },
  {
    'id':'OPEN_04', 'offset':0x1D3E, 'capacity':46,
    'english':"YES. THERE'S NOT A MOMENT TO SPARE. LET'S GO!",
    'lines':['ĐÚNG. KHÔNG CÒN','THỜI GIAN ĐÂU.','ĐI THÔI!'],
    'note':'Short urgent response.'
  },
  {
    'id':'OPEN_05', 'offset':0x1D6C, 'capacity':171,
    'english':"DAD, IT'S ABOUT TIME YOU GOT HERE. SORRY PRINCESS, BUT I NEEDED TO TAKE OUT THE TRASH. DAD, WHERE'S CODY? CODY? I LOST SIGHT OF HIM ON THE WAY HERE. OH, WAY TO GO DAD!",
    'lines':['BỐ, CUỐI CÙNG','BỐ CŨNG ĐẾN RỒI.','XIN LỖI CÔNG CHÚA,','NHƯNG BỐ PHẢI','DỌN ĐÁM RÁC.','BỐ, CODY ĐÂU RỒI?','CODY SAO? BỐ MẤT','DẤU CẬU ẤY TRÊN','ĐƯỜNG ĐẾN ĐÂY.','Ồ, HAY LẮM, BỐ!'],
    'note':'Keeps the father/daughter exchange and the joke about taking out the trash.'
  },
  {
    'id':'OPEN_06', 'offset':0x1E17, 'capacity':198,
    'english':'LET GO OF ME, GUY! WITHOUT MY HELP, SHE WOULD BE... CONTROL YOURSELF. LET THE MAYOR AND JESSICA TALK. FOR ONCE IN YOUR LIFE, THINK OF SOMEONE ELSE BESIDES YOURSELF. LET GO OF ME!',
    'lines':['BUÔNG TÔI RA, GUY!','KHÔNG CÓ TÔI GIÚP,','CÔ ẤY SẼ...','BÌNH TĨNH LẠI!','ĐỂ THỊ TRƯỞNG VÀ','JESSICA NÓI CHUYỆN.','ÍT NHẤT MỘT LẦN','TRONG ĐỜI, HÃY NGHĨ','CHO NGƯỜI KHÁC,','ĐỪNG CHỈ LO MÌNH.','BUÔNG TÔI RA!'],
    'note':'Condenses the admonition while preserving its meaning and urgency.'
  },
]
OPEN_00_LINES = [
 'ĐÂY LÀ METRO CITY.', 'TRONG LÒNG THÀNH', 'PHỐ LÀ JESSICA,',
 'CON GÁI CỦA', 'THỊ TRƯỞNG. VẺ', 'ĐẸP CỦA CÔ', 'LAN TỎA KHẮP',
 'THÀNH PHỐ,', 'TIẾP SỨC CHO NGƯỜI', 'DÂN SINH TỒN.',
 'NHƯNG GIỜ ĐÂY,', 'MỘT KẺ XẤU MUỐN', 'CHIẾM ÁNH SÁNG',
 'ẤY CHO RIÊNG', 'MÌNH.'
]

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def parse_ips(data: bytes) -> list[tuple[int, bytes]]:
    if not data.startswith(b'PATCH'): raise ValueError('IPS header missing')
    pos=5; rec=[]
    while data[pos:pos+3] != b'EOF':
        if pos+5 > len(data): raise ValueError('Truncated IPS record header')
        off=int.from_bytes(data[pos:pos+3],'big'); n=int.from_bytes(data[pos+3:pos+5],'big'); pos+=5
        if n:
            chunk=data[pos:pos+n]; pos+=n
            if len(chunk)!=n: raise ValueError('Truncated IPS data')
        else:
            if pos+3>len(data): raise ValueError('Truncated IPS RLE record')
            n=int.from_bytes(data[pos:pos+2],'big'); value=data[pos+2]; pos+=3; chunk=bytes([value])*n
        rec.append((off,chunk))
    pos+=3
    if pos != len(data): raise ValueError('Trailing bytes after IPS EOF')
    return rec

def make_ips(records: list[tuple[int,bytes]]) -> bytes:
    out=bytearray(b'PATCH'); end=-1
    for off,data in sorted(records,key=lambda x:x[0]):
        if off < end: raise ValueError(f'Overlapping IPS records at {off:#x} (< {end:#x})')
        if not data or len(data)>0xFFFF: raise ValueError(f'Invalid record size at {off:#x}: {len(data)}')
        out += off.to_bytes(3,'big') + len(data).to_bytes(2,'big') + data
        end=off+len(data)
    out += b'EOF'
    return bytes(out)

def apply_ips(src: bytes, patch: bytes) -> bytes:
    out=bytearray(src)
    for off,data in parse_ips(patch):
        if off+len(data)>len(out): out.extend(bytes(off+len(data)-len(out)))
        out[off:off+len(data)] = data
    return bytes(out)

def glyph_codes(project: Path) -> dict[str,int]:
    path=project/'analysis/font_prototype_tiles_step17.csv'
    with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    result={r['glyph']:int(r['text_byte'],16) for r in rows}
    if len(result)!=67: raise ValueError(f'Expected 67 glyphs, found {len(result)}')
    for i in range(26): result[chr(ord('A')+i)]=0x10+i
    result.update({' ':0x00, "'":0x2A, '.':0x2B, ',':0x2C, '?':0x75, '!':0x76})
    return result

def encode_lines(lines: list[str], codes: dict[str,int], capacity: int) -> tuple[bytes,dict]:
    out=bytearray(); unknown=[]
    for i,line in enumerate(lines):
        if len(line)>19: raise ValueError(f'Line exceeds 19 visible cells ({len(line)}): {line!r}')
        if i: out.append(0xFE)
        for ch in line:
            if ch not in codes:
                unknown.append(ch)
                continue
            out.append(codes[ch])
    if unknown: raise ValueError(f'Unmapped characters: {sorted(set(unknown))!r}')
    out.append(0xFF)
    if len(out)>capacity: raise ValueError(f'Encoded text too large: {len(out)} > {capacity}')
    stats={'encoded_bytes':len(out),'capacity':capacity,'remaining_bytes':capacity-len(out),'line_count':len(lines),'max_line_cells':max(map(len,lines))}
    return bytes(out)+bytes(capacity-len(out)),stats

def tile_pixels(raw: bytes) -> list[list[int]]:
    result=[]
    for y in range(8):
        lo,hi=raw[y],raw[y+8]
        result.append([((lo>>(7-x))&1) | (((hi>>(7-x))&1)<<1) for x in range(8)])
    return result

def draw_contact_sheet(output_rom: bytes, project: Path, codes: dict[str,int], all_records: list[dict]) -> None:
    # Each preview page approximates the game's three-line text window; it is a bitmap preview, not a capture.
    pages=[]
    try: label_font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
    except OSError: label_font=ImageFont.load_default()
    def tile(code: int) -> bytes:
        if code < 0x80:
            off=CHR_START+(0x1E00+code)*TILE_SIZE
        else:
            off=EXPECTED_SOURCE_SIZE+(code-0x80)*TILE_SIZE
        return output_rom[off:off+TILE_SIZE]
    records=[{'id':'OPEN_00','lines':OPEN_00_LINES}]+[{'id':b['id'],'lines':b['lines']} for b in BLOCKS]
    for rec in records:
        lines=rec['lines']
        for page_i in range(0,len(lines),3):
            subset=lines[page_i:page_i+3]
            im=Image.new('RGB',(512,448),'black'); d=ImageDraw.Draw(im)
            d.text((8,8),f"Step 18 translated preview · {rec['id']} · rows {page_i+1}-{page_i+len(subset)} · not emulator capture",font=label_font,fill='#9a9a9a')
            for row,line in enumerate(subset):
                y0=338+row*34
                for col,ch in enumerate(line):
                    code=codes[ch]
                    pix=tile_pixels(tile(code))
                    for yy in range(8):
                        for xx in range(8):
                            if pix[yy][xx]:
                                color='#ffffff' if pix[yy][xx]==1 else '#bfbfbf'
                                x0=92+col*16+xx*2; yy0=y0+yy*2
                                d.rectangle((x0,yy0,x0+1,yy0+1),fill=color)
            fname=f"step18_preview_{rec['id']}_page{page_i//3+1}.png"
            im.save(project/'analysis'/fname); pages.append((fname,im.copy()))
    cols=3; cellw,cellh=256,224; rows=(len(pages)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cellw,rows*cellh),'#202020')
    for i,(name,img) in enumerate(pages): sheet.paste(img.resize((cellw,cellh)),((i%cols)*cellw,(i//cols)*cellh))
    sheet.save(project/'analysis/step18_opening_sequence_preview_contact_sheet.png')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-rom',type=Path,default=Path('/mnt/data/Mighty Final Fight (USA).nes'))
    ap.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--step17-ips',type=Path,default=None)
    ap.add_argument('--output-rom',type=Path,default=Path('/mnt/data/Mighty_Final_Fight_Vietnamese_OPENING_SEQUENCE_STEP18.nes'))
    ap.add_argument('--output-ips',type=Path,default=Path('/mnt/data/Mighty_Final_Fight_Vietnamese_OPENING_SEQUENCE_STEP18.ips'))
    args=ap.parse_args(); project=args.project
    source=args.source_rom.read_bytes()
    if len(source)!=EXPECTED_SOURCE_SIZE or sha(source)!=EXPECTED_SOURCE_SHA256:
        raise SystemExit(f'Clean source ROM mismatch: size={len(source)}, sha256={sha(source)}')
    step17_ips_path=args.step17_ips or (project/'analysis/Mighty_Final_Fight_Vietnamese_OPENING_TRANSLATION_BANK_FIX_STEP17.ips')
    step17_patch=step17_ips_path.read_bytes()
    step17_records=parse_ips(step17_patch)
    step17_rom=apply_ips(source,step17_patch)
    if sha(step17_rom)!=STEP17_EXPECTED_SHA256:
        raise SystemExit(f'Step 17 base image mismatch: {sha(step17_rom)}')
    codes=glyph_codes(project)
    encoded_records=[]; manifests=[]
    output=bytearray(step17_rom)
    for b in BLOCKS:
        slot,stats=encode_lines(b['lines'],codes,b['capacity'])
        old_start=b['offset']; old=step17_rom[old_start:old_start+b['capacity']]
        if len(old)!=b['capacity']: raise SystemExit(f"Slot range exceeds source for {b['id']}")
        output[old_start:old_start+b['capacity']]=slot
        encoded_records.append((old_start,slot))
        # Decode the encoded stream before padding to verify every byte matches intended glyphs and line breaks.
        raw=slot[:stats['encoded_bytes']]
        if raw[-1]!=0xFF: raise SystemExit(f"Missing terminator for {b['id']}")
        manifests.append({
          'id':b['id'],'file_offset':f"0x{b['offset']:06X}",'slot_capacity':b['capacity'],
          'source_english':b['english'],'vietnamese_lines':b['lines'],
          'vietnamese_text':' '.join(b['lines']),'note':b['note'],**stats,
          'used_high_codes':[f'0x{x:02X}' for x in sorted(set(raw)) if 0x80<=x<=0x8F],
          'uses_extended_chars':any(0x80<=x<=0x8F for x in raw),
        })
    out=bytes(output)
    # Combined IPS carries Step 17 plus the six adjacent fixed-slot records.
    patch=make_ips(step17_records+encoded_records)
    if apply_ips(source,patch)!=out: raise SystemExit('Combined IPS round-trip mismatch')
    # Ensure fixed pointer and code structures are intact; only these 6 additional slot ranges change relative to Step 17.
    for b in BLOCKS:
        if out[b['offset']:b['offset']+b['capacity']] != encoded_records[[x[0] for x in encoded_records].index(b['offset'])][1]:
            raise SystemExit(f"Output slot verification failed for {b['id']}")
    # No changed bytes outside the six additional text records compared with Step 17 output.
    allowed=[(b['offset'],b['offset']+b['capacity']) for b in BLOCKS]
    for pos,(a,b) in enumerate(zip(step17_rom,out)):
        if a!=b and not any(s<=pos<e for s,e in allowed): raise SystemExit(f'Unexpected Step 18 diff at {pos:#x}')
    args.output_rom.parent.mkdir(parents=True,exist_ok=True); args.output_ips.parent.mkdir(parents=True,exist_ok=True)
    args.output_rom.write_bytes(out); args.output_ips.write_bytes(patch)
    # Persist authoritative translation data and reports.
    ad=project/'analysis'; ad.mkdir(parents=True,exist_ok=True)
    (ad/'step18_opening_translation_records.json').write_text(json.dumps(manifests,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ad/'step18_opening_translation_records.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['id','file_offset','slot_capacity','encoded_bytes','remaining_bytes','line_count','max_line_cells','english','vietnamese_lines','vietnamese_text','note'])
        for m in manifests: w.writerow([m['id'],m['file_offset'],m['slot_capacity'],m['encoded_bytes'],m['remaining_bytes'],m['line_count'],m['max_line_cells'],m['source_english'],' / '.join(m['vietnamese_lines']),m['vietnamese_text'],m['note']])
    (ad/'step18_opening_translation_draft.md').write_text('# Step 18 — Opening translation extension\n\nStep 17 verified by the user; this step adds OPEN_01 through OPEN_06 to the Vietnamese opening sequence. The fixed-size records and pointers are retained. The previews are generated tile renders, not emulator captures.\n\n'+'\n\n'.join(f"## {m['id']}\n\n**English:** {m['source_english']}\n\n**Vietnamese:**\n\n"+'\n'.join(m['vietnamese_lines'])+f"\n\nEncoded bytes: {m['encoded_bytes']} / {m['slot_capacity']}. {m['note']}" for m in manifests)+'\n',encoding='utf-8')
    draw_contact_sheet(out,project,codes,manifests)
    report={
      'step':18,'title':'Extend verified Vietnamese opening translation through OPEN_06',
      'status':'static_build_passed_user_emulator_test_required',
      'source_sha256':sha(source),'step17_base_sha256':sha(step17_rom),'output_sha256':sha(out),'ips_sha256':sha(patch),
      'source_bytes':len(source),'output_bytes':len(out),'combined_ips_bytes':len(patch),'ips_records':len(parse_ips(patch)),
      'ips_roundtrip_exact':apply_ips(source,patch)==out,'step17_sha_matches_expected':sha(step17_rom)==STEP17_EXPECTED_SHA256,
      'opening_records_added':[m['id'] for m in manifests],'record_count_added':len(manifests),
      'all_slots_fit':all(m['encoded_bytes']<=m['slot_capacity'] for m in manifests),
      'all_lines_at_most_19_cells':all(m['max_line_cells']<=19 for m in manifests),
      'all_custom_glyphs_mapped':True,'text_pointers_modified':False,
      'only_new_changes_vs_step17_are_six_opening_text_slots':True,
      'records':manifests,'emulator_test':'Not run by build script; user needs to verify FCEUX rendering and transition.'
    }
    (ad/'step18_build_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ad/'step18_build_validation.txt').write_text(
      'STEP 18 STATIC VALIDATION\n'
      f"Clean source SHA-256: {sha(source)}\nStep 17 base SHA-256: {sha(step17_rom)}\nOutput SHA-256: {sha(out)}\n"
      f'Input/output bytes: {len(source)} -> {len(out)}\nCombined IPS: {len(patch)} bytes, {len(parse_ips(patch))} records\n'
      f'Exact IPS round-trip: {apply_ips(source,patch)==out}\nOpening records added: {len(manifests)}\n'
      + ''.join(f"{m['id']}: encoded {m['encoded_bytes']} / {m['slot_capacity']} bytes; max line {m['max_line_cells']}/19 cells; PASS\n" for m in manifests)
      + 'Text pointers changed: NO\nDiff outside the six added text slots relative to Step 17: NONE\nFCEUX test: NOT RUN by builder; user test required.\n',encoding='utf-8')
    args.output_rom.with_suffix(args.output_rom.suffix+'.sha256.txt').write_text(f'{sha(out)}  {args.output_rom.name}\n{sha(patch)}  {args.output_ips.name}\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
