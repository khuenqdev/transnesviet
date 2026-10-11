#!/usr/bin/env python3
"""Build an 8x8 Vietnamese uppercase font prototype from Mighty Final Fight's A-Z tiles.

This script only emits analysis assets (PNG/CSV/JSON/raw tile data). It does not modify a ROM.
Usage: python3 build_font_prototype_step5.py [clean_rom.nes] [project_dir]
"""
from pathlib import Path
import argparse, csv, json, hashlib, zlib, unicodedata
from PIL import Image, ImageDraw, ImageFont

EXPECTED_SIZE = 262160
EXPECTED_BODY_CRC = 0x3F78037C
BASE_CHR_OFFSET = 16 + 131072
TILE_BYTES = 16

def decode_tile(chrd, tid):
    t = chrd[tid*TILE_BYTES:(tid+1)*TILE_BYTES]
    pixels = []
    for y in range(8):
        row=[]
        for x in range(8):
            val = ((t[y] >> (7-x)) & 1) | (((t[y+8] >> (7-x)) & 1) << 1)
            row.append(1 if val else 0)
        pixels.append(row)
    return pixels

def encode_tile(pixels):
    out=bytearray(16)
    for y in range(8):
        for x in range(8):
            if pixels[y][x]: out[y] |= 1 << (7-x)
    return bytes(out)

def source_shape(chrd, letter):
    tid = 0x1E00 + 0x10 + ord(letter) - ord('A')
    p = decode_tile(chrd, tid)
    # Existing glyphs use rows 1-7 and columns up to 7. Crop away only the blank top row,
    # then shrink to a 6 x 5 core so two upper rows and one lower row remain for Vietnamese marks.
    crop = [row[1:8] for row in p[1:8]]  # 7x7
    # Nearest-neighbor resize to 6x5; deterministic and preserves blocky pixel-art edges.
    resized=[]
    for y in range(5):
        sy=min(6, int(y*7/5))
        row=[]
        for x in range(6):
            sx=min(6, int(x*7/6))
            row.append(crop[sy][sx])
        resized.append(row)
    return resized

def build_viet_glyph(chrd, glyph):
    nfd = unicodedata.normalize('NFD', glyph)
    if glyph == 'Đ':
        base='D'; marks=['STROKE']
    else:
        base=nfd[0]
        marks=[]
        for c in nfd[1:]:
            if c == '\u0302': marks.append('CIRCUMFLEX')
            elif c == '\u0306': marks.append('BREVE')
            elif c == '\u0303': marks.append('TILDE')
            elif c == '\u0300': marks.append('GRAVE')
            elif c == '\u0301': marks.append('ACUTE')
            elif c == '\u0309': marks.append('HOOK')
            elif c == '\u0323': marks.append('DOT_BELOW')
            elif c == '\u031b': marks.append('HORN')
            else: marks.append('UNKNOWN_'+format(ord(c),'04X'))
    if base not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        raise ValueError(f'Unsupported decomposed base for {glyph!r}: {base!r} ({marks})')
    p=[[0]*8 for _ in range(8)]
    shape=source_shape(chrd,base)
    # Character body in rows 2..6, six pixels wide in columns 1..6.
    for y in range(5):
        for x in range(6): p[y+2][x+1]=shape[y][x]
    # Uppercase Vietnamese D stroke.
    if 'STROKE' in marks:
        for x in range(1,7): p[4][x]=1
    if 'HORN' in marks:
        # Compact right-side horn; kept within the 8x8 cell.
        p[2][6]=1; p[3][7]=1; p[4][7]=1
    # A lower dot takes the last scanline. Center it so it is distinct from the body.
    if 'DOT_BELOW' in marks:
        p[7][3]=1; p[7][4]=1
    # Upper modifiers occupy row 1. They are deliberately compact to leave row 0 for tone.
    if 'CIRCUMFLEX' in marks:
        p[1][2]=1; p[1][4]=1; p[0][3]=1
    if 'BREVE' in marks:
        p[1][2]=1; p[1][3]=1; p[1][4]=1
    # Upper tone symbols. The shape is simplified to fit an 8x8 cell alongside a modifier.
    tone = next((m for m in ('ACUTE','GRAVE','HOOK','TILDE') if m in marks), None)
    if tone == 'ACUTE':
        p[0][4]=1; p[0][5]=1
    elif tone == 'GRAVE':
        p[0][2]=1; p[0][3]=1
    elif tone == 'HOOK':
        p[0][2]=1; p[0][3]=1; p[0][5]=1
    elif tone == 'TILDE':
        p[0][2]=1; p[0][4]=1; p[0][5]=1
    elif 'DOT_ABOVE' in marks:
        p[0][3]=1; p[0][4]=1
    return p, base, marks

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('rom',type=Path,nargs='?',default=Path('/mnt/data/Mighty Final Fight (USA).nes'))
    ap.add_argument('project_dir',type=Path,nargs='?',default=Path(__file__).resolve().parents[1])
    a=ap.parse_args()
    rom=a.rom.read_bytes()
    if len(rom)!=EXPECTED_SIZE: raise SystemExit(f'ROM size mismatch: {len(rom)} != {EXPECTED_SIZE}')
    body_crc=zlib.crc32(rom[16:]) & 0xffffffff
    if body_crc != EXPECTED_BODY_CRC: raise SystemExit(f'ROM body CRC mismatch: {body_crc:08X}')
    project=a.project_dir; analysis=project/'analysis'; analysis.mkdir(parents=True,exist_ok=True)
    chrd=rom[BASE_CHR_OFFSET:]
    alloc_path=analysis/'font_glyph_allocation_candidate_step4.csv'
    with alloc_path.open(encoding='utf-8-sig',newline='') as f: alloc=list(csv.DictReader(f))
    new=[r for r in alloc if r['allocation_status']=='CANDIDATE_EXTENDED_BYTE']
    entries=[]; tiles={}; unknown=[]
    for r in new:
        glyph=r['glyph']; code=int(r['text_byte_hex'],16)
        # 0x35 is a recurring boss-dialogue segment/header marker in the extracted records,
        # so it cannot be assigned to the printable glyph É. Move É to the spare blank tile/code 0x8F.
        if glyph == 'É': code = 0x8F
        global_tile = 0x1E00 + code
        source_tile = chrd[global_tile*TILE_BYTES:(global_tile+1)*TILE_BYTES]
        if any(source_tile): raise SystemExit(f'Proposed tile 0x{global_tile:04X} is not blank in source ROM')
        pix,base,marks=build_viet_glyph(chrd,glyph)
        data=encode_tile(pix)
        tiles[code]=data
        entries.append({
          'glyph':glyph,'unicode':f"U+{ord(glyph):04X}",'base_letter':base,
          'marks':'+'.join(marks) if marks else 'NONE','text_byte':f'0x{code:02X}',
          'global_chr_tile':f'0x{global_tile:04X}','chr_file_offset':f'0x{BASE_CHR_OFFSET+global_tile*TILE_BYTES:06X}',
          'tile_bytes_hex':data.hex(),'prototype_status':'PREVIEW_ONLY_NOT_EMULATOR_VALIDATED'
        })
        if any(m.startswith('UNKNOWN_') for m in marks): unknown.append(glyph)
    # Data blob contains exactly the proposed extended tiles in ascending byte-code order.
    sorted_entries=sorted(entries,key=lambda x:int(x['text_byte'],16))
    (analysis/'font_prototype_tiles_step5.bin').write_bytes(b''.join(tiles[c] for c in sorted(tiles)))
    (analysis/'font_prototype_tiles_step5.csv').write_text('',encoding='utf-8')
    with (analysis/'font_prototype_tiles_step5.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['glyph','unicode','base_letter','marks','text_byte','global_chr_tile','chr_file_offset','tile_bytes_hex','prototype_status'])
        w.writeheader(); w.writerows(sorted_entries)
    # Render large preview grid: 8x8 tile enlarged 8x; show source-like black pixels on warm paper.
    cols=8; cellw=104; cellh=108; rows=(len(sorted_entries)+cols-1)//cols
    img=Image.new('RGB',(cols*cellw,rows*cellh),(242,240,234)); d=ImageDraw.Draw(img)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except OSError: font=ImageFont.load_default()
    for i,e in enumerate(sorted_entries):
        x=(i%cols)*cellw; y=(i//cols)*cellh
        code=int(e['text_byte'],16); data=tiles[code]
        p=[[0]*8 for _ in range(8)]
        for yy in range(8):
            for xx in range(8): p[yy][xx]=1 if ((data[yy]>>(7-xx))&1) else 0
        for yy in range(8):
            for xx in range(8):
                color=(24,24,24) if p[yy][xx] else (255,255,255)
                d.rectangle((x+8+xx*8,y+5+yy*8,x+15+xx*8,y+12+yy*8),fill=color)
        d.text((x+8,y+74),f"{e['glyph']}  {e['text_byte']}",font=font,fill=(35,35,35))
        d.text((x+8,y+89),e['marks'],font=font,fill=(85,85,85))
        d.text((x+8,y+100),e['unicode'],font=font,fill=(110,110,110))
    img.save(analysis/'font_prototype_step5.png')
    # Source collision audit. In boss streams, records begin with a five-byte layout header whose first byte is 0x2B or 0x35; later render segments can begin with 0x35 plus four metadata bytes. Skip these header blocks, not just the first five bytes in every record.
    records_path=analysis/'dialogue_records.tsv'; audit_codes=set(tiles)|{0x35}
    raw_counts={c:0 for c in audit_codes}; body_counts={c:0 for c in audit_codes}; header_counts={c:0 for c in audit_codes}
    with records_path.open(encoding='utf-8-sig',newline='') as f:
        recs=list(csv.DictReader(f,delimiter='\t'))
    for rec in recs:
        try: raw=[int(x,16) for x in (rec.get('raw_hex') or '').split()]
        except Exception: raw=[]
        group=rec.get('group','')
        i=0
        while i < len(raw):
            b=raw[i]
            is_header = group=='boss' and (b==0x35 or (i==0 and b==0x2B))
            if is_header:
                for j in range(i,min(i+5,len(raw))):
                    v=raw[j]
                    if v in audit_codes:
                        raw_counts[v]+=1; header_counts[v]+=1
                i+=5
                continue
            if b in audit_codes:
                raw_counts[b]+=1; body_counts[b]+=1
            i+=1
    with (analysis/'byte_code_collision_audit_step5.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['byte','candidate_glyph','raw_record_occurrences','boss_header_occurrences','body_occurrences','status','note']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        glyph_by_code={int(e['text_byte'],16):e['glyph'] for e in sorted_entries}
        for c in sorted(audit_codes):
            if c==0x35:
                label='[RESERVED BOSS SEGMENT MARKER]'; status='DO_NOT_ASSIGN_PRINTABLE_GLYPH'
            else:
                label=glyph_by_code[c]
                status='BODY_OCCURRENCE_REQUIRES_REVIEW' if body_counts[c] else ('HEADER_ONLY_MATCHES' if header_counts[c] else 'NOT_SEEN_IN_CURRENT_DUMP')
            w.writerow({'byte':f'0x{c:02X}','candidate_glyph':label,'raw_record_occurrences':raw_counts[c],
                        'boss_header_occurrences':header_counts[c],'body_occurrences':body_counts[c],'status':status,
                        'note':'Initial 0x2B/0x35 layout header or later 0x35 segment marker is parsed with four following metadata bytes; static grouping still requires runtime confirmation.'})
    audit={'rom_body_crc32':f'{body_crc:08X}','rom_sha256':hashlib.sha256(rom).hexdigest(),'prototype_tile_count':len(tiles),
      'prototype_tile_bytes':len(tiles)*16,'source_tiles_modified':False,'rom_modified':False,
      'text_records_scanned':len(recs),'candidate_byte_occurrences_total_raw':sum(raw_counts[k] for k in tiles),
      'candidate_byte_occurrences_in_boss_headers':sum(header_counts[k] for k in tiles),
      'candidate_byte_occurrences_in_body_streams':sum(body_counts[k] for k in tiles),
      'reserved_0x35_marker_occurrences':raw_counts[0x35],
      'candidate_byte_occurrences_by_code_raw':{f'0x{k:02X}':raw_counts[k] for k in sorted(tiles)},
      'candidate_byte_occurrences_by_code_body':{f'0x{k:02X}':body_counts[k] for k in sorted(tiles)},
      'unknown_unicode_marks':unknown,
      'limitations':['This is a visual font prototype, not a game-tested font.','Tone marks and compressed uppercase bodies are intentionally compact; inspect preview for legibility.','No ROM is written or patched.','Raw record byte matches may include metadata/control and do not prove a code is safe in all text renderers.']}
    (analysis/'font_prototype_validation_step5.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=f'''# Step 5 — Vietnamese glyph artwork prototype\n\n## Outputs\n\n- `font_prototype_step5.png`: contact sheet of all {len(tiles)} proposed uppercase Vietnamese glyphs, enlarged from 8x8 pixels.\n- `font_prototype_tiles_step5.bin`: packed 16-byte-per-tile CHR data, ordered by ascending candidate text byte.\n- `font_prototype_tiles_step5.csv`: glyph, Unicode code point, candidate byte/tile, component marks, and tile bytes.\n- `byte_code_collision_audit_step5.csv`: separates candidate-byte matches in boss record headers from body-stream matches under the current dump layout.\n- `font_prototype_validation_step5.json`: ROM identity, reproducibility metadata, and limitations.\n\n## Method\n\nThe generator starts from this ROM's existing A-Z tiles, shrinks the uppercase body into rows 2-6, then draws compact Vietnamese marks within the remaining pixels. It creates precomposed single-tile glyphs so a text string remains one byte per displayed character. The proposed code and tile slots are taken from the Step 4 allocation CSV.\n\n## Status and limitations\n\nThis is a **visual prototype only**. The raw dump shows `0x35` as a recurring boss render-segment marker (and `0x2B` as an initial boss layout-header variant), so the prototype deliberately avoids assigning that byte to a glyph and places `É` at spare byte/tile `0x8F` instead. The generator does not modify the ROM and does not assert that any candidate byte is safe in all dialogue paths. The raw-byte audit is only a clue: a matching byte may be a header, a layout parameter, a control code, or body text. Before injection, the glyph shapes need a visual legibility review, and Mesen/FCEUX runtime checks must verify both glyph display and absence of unintended tile usage in other screens.\n\nROM body CRC32: `{body_crc:08X}`  \nROM SHA-256: `{hashlib.sha256(rom).hexdigest()}`  \nGlyph tiles generated: **{len(tiles)}** ({len(tiles)*16} bytes).  \nCandidate raw-record byte occurrences for allocated glyph codes: **{sum(raw_counts[k] for k in tiles)}** total; **{sum(header_counts[k] for k in tiles)}** occur in boss segment headers and **{sum(body_counts[k] for k in tiles)}** in body streams under the current dump layout. Reserved boss segment marker `0x35` occurs **{raw_counts[0x35]}** times in the dump and is not assigned to a glyph; `É` is remapped to spare byte/tile `0x8F`.\n'''
    (analysis/'font_prototype_step5.md').write_text(report,encoding='utf-8')
    print(f'PASS: verified ROM identity (body CRC32 {body_crc:08X})')
    print(f'PASS: generated {len(tiles)} 8x8 glyph tiles ({len(tiles)*16} bytes)')
    print(f'PASS: wrote preview, CSV, binary, audit, JSON, and report under {analysis}')
    print(f'ROM modified: no')
if __name__=='__main__': main()
