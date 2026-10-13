#!/usr/bin/env python3
"""Build Step 19: translate the first Thrasher boss-dialogue batch in-place.

Inputs: clean USA ROM, combined Step 18 IPS patch, and Step 17 glyph table.
This builder preserves each five-byte boss-record header, keeps the terminator at
its original byte offset, does not alter pointers, and includes only low-byte
Vietnamese glyphs (< $80) in this first runtime-context pilot.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SOURCE_SHA256 = '5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
STEP18_SHA256 = 'ec348dbc1d3e96d618c5e2f510340d31eab8c92483c890b4148d3abe949bf1e8'
SOURCE_SIZE = 262160
OUTPUT_SIZE = 278544
HEADER_SIZE = 16
PRG_SIZE = 131072
CHR_START = HEADER_SIZE + PRG_SIZE
TILE_SIZE = 16

# Absolute ROM file offsets include the 16-byte iNES header. The first five
# bytes of every selected record are special metadata and must be preserved.
RECORDS = [
    dict(id='BOSS_00/01', indexes=[0,1], start=0x09D81, length=29, prefix='3500020202',
         english='HEH HEH. I AM THRASHER,', vietnamese='HA HA! TA LÀ THRASHER,',
         note='Shared pointer used by both BOSS_00 and BOSS_01.'),
    dict(id='BOSS_02', indexes=[2], start=0x09D9E, length=25, prefix='3500030303',
         english='RULER OF THIS CITY.', vietnamese='CHÚA TỂ THÀNH PHỐ.',
         note='Shortened to fit the fixed record slot.'),
    dict(id='BOSS_03', indexes=[3], start=0x09DB7, length=25, prefix='35020B0980',
         english='BOW DOWN BEFORE ME', vietnamese='CÚI ĐẦU MAU LÊN!',
         note='Imperative preserved; wording adapted to fit without the unverified Ớ byte.'),
    dict(id='BOSS_04/05', indexes=[4,5], start=0x09DD0, length=31, prefix='3500060606',
         english="DON'T YOU KNOW I RULE THE", vietnamese='BIẾT CHƯA? TA CAI TRỊ',
         note='Shared pointer used by both BOSS_04 and BOSS_05; completed by BOSS_06.'),
    dict(id='BOSS_06', indexes=[6], start=0x09DEF, length=15, prefix='35020B0A80',
         english='STREETS', vietnamese='PHỐ NÀY!',
         note='Completes the preceding statement: “Biết chưa? Ta cai trị phố này!”'),
    dict(id='BOSS_07', indexes=[7], start=0x09DFE, length=25, prefix='3500080808',
         english='THOSE WHO OFFEND ME', vietnamese='KẺ NÀO XÚC PHẠM TA',
         note='Threat phrasing kept concise for the original slot.'),
    dict(id='BOSS_08', indexes=[8], start=0x09E17, length=15, prefix='3500000000',
         english='MUST DIE', vietnamese='ĐỀU CHẾT!',
         note='Continues the preceding threat: “Kẻ nào xúc phạm ta đều chết!”'),
]

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def parse_ips(data: bytes) -> list[tuple[int, bytes]]:
    if not data.startswith(b'PATCH'): raise ValueError('IPS header missing')
    p=5; out=[]
    while data[p:p+3] != b'EOF':
        if p+5 > len(data): raise ValueError('truncated IPS record')
        off=int.from_bytes(data[p:p+3],'big'); n=int.from_bytes(data[p+3:p+5],'big'); p+=5
        if n:
            block=data[p:p+n]; p+=n
            if len(block)!=n: raise ValueError('truncated IPS payload')
        else:
            if p+3>len(data): raise ValueError('truncated IPS RLE payload')
            n=int.from_bytes(data[p:p+2],'big'); val=data[p+2]; p+=3; block=bytes([val])*n
        out.append((off,block))
    p+=3
    if p != len(data): raise ValueError('trailing data after IPS EOF')
    return out

def apply_ips(src: bytes, patch: bytes) -> bytes:
    out=bytearray(src)
    for off,block in parse_ips(patch):
        if off+len(block)>len(out): out.extend(bytes(off+len(block)-len(out)))
        out[off:off+len(block)]=block
    return bytes(out)

def make_ips(records: list[tuple[int,bytes]]) -> bytes:
    out=bytearray(b'PATCH'); end=-1
    for off,block in sorted(records, key=lambda x:x[0]):
        if not block or len(block)>0xFFFF: raise ValueError(f'invalid IPS record at {off:#x}')
        if off < end: raise ValueError(f'overlapping IPS record at {off:#x}; previous ends {end:#x}')
        out += off.to_bytes(3,'big') + len(block).to_bytes(2,'big') + block
        end=off+len(block)
    out += b'EOF'
    return bytes(out)

def load_codes(map_csv: Path) -> dict[str,int]:
    with map_csv.open(encoding='utf-8-sig', newline='') as f: rows=list(csv.DictReader(f))
    codes={r['glyph']:int(r['text_byte'],16) for r in rows}
    if len(codes)!=67: raise ValueError(f'expected 67 mapped diacritics, got {len(codes)}')
    codes.update({chr(ord('A')+i):0x10+i for i in range(26)})
    codes.update({' ':0x00,"'":0x2A,'.':0x2B,',':0x2C,'?':0x75,'!':0x76})
    return codes

def encode(text: str, codes: dict[str,int]) -> bytes:
    data=bytearray()
    for ch in text:
        if ch not in codes: raise ValueError(f'unmapped glyph {ch!r} in {text!r}')
        value=codes[ch]
        if value >= 0x80:
            raise ValueError(f'this boss-text pilot must avoid >= $80 bytes; {ch!r} maps to {value:#04x}')
        # 0x35 is the special record/header marker and must not be emitted as text.
        if value == 0x35: raise ValueError('reserved header marker 0x35 emitted as text')
        data.append(value)
    return bytes(data)

def tile_pixels(raw: bytes):
    return [[((raw[y]>>(7-x))&1) | (((raw[y+8]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)]

def build_preview(rom: bytes, project: Path, codes: dict[str,int], manifests: list[dict]) -> None:
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
    except OSError: font=ImageFont.load_default()
    def get_tile(code: int) -> bytes:
        if code >= 0x80: return b'\0'*16
        off=CHR_START+(0x1E00+code)*TILE_SIZE
        return rom[off:off+16]
    W,H=780,250
    cards=[]
    for m in manifests:
        im=Image.new('RGB',(W,H),'black'); d=ImageDraw.Draw(im)
        d.text((12,10), f"{m['id']} — {m['english']}", font=font, fill='#aaaaaa')
        d.text((12,30), f"Vietnamese: {m['vietnamese']}", font=font, fill='#aaaaaa')
        text=m['vietnamese']
        x0=20; y0=125; scale=3; gap=3
        for char in text:
            code=codes[char]
            px=tile_pixels(get_tile(code))
            for y in range(8):
                for x in range(8):
                    if px[y][x]:
                        color='#fff' if px[y][x]==1 else '#bbb'
                        xx=x0+x*scale; yy=y0+y*scale
                        d.rectangle((xx,yy,xx+scale-1,yy+scale-1), fill=color)
            x0 += 8*scale+gap
        d.text((12,210), f"Encoded visible bytes: {m['encoded_text_bytes']} / content limit {m['content_limit']}; metadata preserved", font=font, fill='#888888')
        cards.append(im)
        im.save(project/'analysis'/f"step19_preview_{m['id'].replace('/','_')}.png")
    cols=2; cellw,cellh=390,125; rows=(len(cards)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cellw,rows*cellh),'#222222')
    for i,im in enumerate(cards): sheet.paste(im.resize((cellw,cellh)),((i%cols)*cellw,(i//cols)*cellh))
    sheet.save(project/'analysis/step19_boss_dialogue_preview_contact_sheet.png')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-rom',type=Path,default=Path('/mnt/data/Mighty Final Fight (USA).nes'))
    ap.add_argument('--base-ips',type=Path,default=None)
    ap.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--output-rom',type=Path,default=Path('/mnt/data/Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.nes'))
    ap.add_argument('--output-ips',type=Path,default=Path('/mnt/data/Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.ips'))
    args=ap.parse_args(); project=args.project; ad=project/'analysis'
    src=args.source_rom.read_bytes()
    if len(src)!=SOURCE_SIZE or sha(src)!=SOURCE_SHA256: raise SystemExit(f'clean ROM mismatch: {len(src)} bytes, {sha(src)}')
    base_path=args.base_ips or (ad/'step18_base_combined.ips')
    base_patch=base_path.read_bytes(); base_records=parse_ips(base_patch)
    step18=apply_ips(src,base_patch)
    if len(step18)!=OUTPUT_SIZE or sha(step18)!=STEP18_SHA256: raise SystemExit(f'Step 18 base mismatch: {len(step18)} bytes, {sha(step18)}')
    codes=load_codes(ad/'font_prototype_tiles_step17.csv')
    output=bytearray(step18); new_records=[]; manifests=[]
    used_starts=[]
    for r in RECORDS:
        start=r['start']; length=r['length']; prefix_len=len(bytes.fromhex(r['prefix']))
        if start in used_starts: raise SystemExit(f'duplicate source start {start:#x}')
        used_starts.append(start)
        original=step18[start:start+length]
        if len(original)!=length: raise SystemExit(f'{r["id"]}: source record out of bounds')
        if original[:prefix_len] != bytes.fromhex(r['prefix']):
            raise SystemExit(f'{r["id"]}: metadata prefix mismatch; got {original[:prefix_len].hex()}')
        if original[-1] != 0xFF: raise SystemExit(f'{r["id"]}: expected terminator at final slot byte')
        text_data=encode(r['vietnamese'],codes)
        body_capacity=length-prefix_len
        content_limit=body_capacity-1
        if len(text_data)>content_limit:
            raise SystemExit(f'{r["id"]}: text bytes {len(text_data)} exceed {content_limit}; {r["vietnamese"]!r}')
        # Preserve FF at the original terminator offset; fill unused payload with spaces.
        body=text_data + bytes(content_limit-len(text_data)) + b'\xff'
        patch_offset=start+prefix_len
        if step18[patch_offset:patch_offset+body_capacity] == body:
            raise SystemExit(f'{r["id"]}: unexpectedly already translated')
        output[patch_offset:patch_offset+body_capacity]=body
        new_records.append((patch_offset,body))
        m={**r,'file_offset':f'0x{start:06X}','text_offset':f'0x{patch_offset:06X}',
           'record_length':length,'metadata_bytes':prefix_len,'metadata_hex':r['prefix'].upper(),
           'body_capacity_including_ff':body_capacity,'content_limit':content_limit,
           'encoded_text_bytes':len(text_data),'remaining_content_bytes':content_limit-len(text_data),
           'used_extended_codes':False,'pointer_modified':False,
           'encoded_hex':text_data.hex(' ').upper(),'padding_spaces':content_limit-len(text_data)}
        manifests.append(m)
    out=bytes(output)
    patch=make_ips(base_records+new_records)
    if apply_ips(src,patch)!=out: raise SystemExit('combined IPS round-trip mismatch')
    if len(out)!=OUTPUT_SIZE: raise SystemExit(f'unexpected output size {len(out)}')
    if out[:5]!=step18[:5] or out[6:16]!=step18[6:16]: raise SystemExit('header changed relative to Step 18')
    # Only target body bytes may differ from Step 18; record headers and pointers must remain intact.
    allowed=[(o,o+len(b)) for o,b in new_records]
    for pos,(old,new) in enumerate(zip(step18,out)):
        if old!=new and not any(a<=pos<z for a,z in allowed):
            raise SystemExit(f'unexpected Step 19 changed byte at {pos:#x}')
    for r in RECORDS:
        start=r['start']; n=len(bytes.fromhex(r['prefix']))
        if out[start:start+n] != step18[start:start+n]: raise SystemExit(f'{r["id"]}: metadata altered')
        if out[start+r['length']-1] != 0xFF: raise SystemExit(f'{r["id"]}: original terminator offset changed')
    # Write outputs and project data.
    args.output_rom.parent.mkdir(parents=True,exist_ok=True); args.output_rom.write_bytes(out)
    args.output_ips.parent.mkdir(parents=True,exist_ok=True); args.output_ips.write_bytes(patch)
    (ad/'step19_translated_boss_records.json').write_text(json.dumps(manifests,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ad/'step19_translated_boss_records.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['id','indexes','file_offset','text_offset','record_length','metadata_hex','body_capacity_including_ff','content_limit','encoded_text_bytes','remaining_content_bytes','english','vietnamese','encoded_hex','note'])
        for m in manifests: w.writerow([m['id'],','.join(map(str,m['indexes'])),m['file_offset'],m['text_offset'],m['record_length'],m['metadata_hex'],m['body_capacity_including_ff'],m['content_limit'],m['encoded_text_bytes'],m['remaining_content_bytes'],m['english'],m['vietnamese'],m['encoded_hex'],m['note']])
    md=['# Step 19 — Thrasher boss-dialogue pilot','', 'This batch patches the first contiguous Thrasher boast/threat sequence, using the validated Step 18 opening ROM and the existing low-byte glyph tiles. The game’s five-byte per-record metadata prefixes and all pointers remain untouched. Duplicate indexes are called out because they share the same pointers.','', '## Translations','']
    for m in manifests:
        md += [f"### {m['id']} (indexes {', '.join(map(str,m['indexes']))})", '', f"**English:** {m['english']}", '', f"**Vietnamese:** {m['vietnamese']}", '', f"Slot:** {m['encoded_text_bytes']} text bytes / {m['content_limit']} content bytes; {m['padding_spaces']} trailing space(s).**", '', m['note'], '']
    md += ['## Important scope note','', 'This pilot deliberately avoids text codes `$80-$8F`, since the high-byte R1-routing hook is presently verified only in the opening text path. Every custom Vietnamese glyph in these seven strings uses a text code below `$80`. The active R0 font bank during boss dialogue still needs confirmation in FCEUX; test the patched boss conversation before extending the batch.', '', '## ROM changes', '', 'Only the seven target payload ranges change relative to Step 18. The five-byte metadata headers, fixed-length record ends, pointer table, expanded CHR data, opening text and helper remain unchanged.', '']
    (ad/'step19_boss_dialogue_pilot.md').write_text('\n'.join(md),encoding='utf-8')
    build_preview(out,project,codes,manifests)
    report={
      'step':19,'title':'First Thrasher boss-dialogue pilot','status':'static_build_passed_emulator_test_required',
      'source_sha256':sha(src),'step18_base_sha256':sha(step18),'output_sha256':sha(out),'ips_sha256':sha(patch),
      'source_bytes':len(src),'output_bytes':len(out),'output_chr_units_8k':out[5],
      'step18_base_patch_bytes':len(base_patch),'combined_ips_bytes':len(patch),'combined_ips_records':len(parse_ips(patch)),
      'ips_roundtrip_exact':apply_ips(src,patch)==out,'record_count':len(manifests),'target_indexes':[i for r in RECORDS for i in r['indexes']],
      'shared_pointer_indexes':{'BOSS_00/BOSS_01':0x9D71,'BOSS_04/BOSS_05':0x9DC0},
      'metadata_prefixes_preserved':True,'terminator_offsets_preserved':True,'pointers_modified':False,
      'only_target_payloads_changed_vs_step18':True,'all_text_fits':all(m['encoded_text_bytes']<=m['content_limit'] for m in manifests),
      'all_codes_below_0x80':True,'runtime_r0_bank_in_boss_context':'Not yet observed; user FCEUX test required.',
      'records':manifests,'emulator_test':'Not run by build script.'}
    (ad/'step19_build_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    log=['STEP 19 STATIC VALIDATION',f'Clean source SHA-256: {sha(src)}',f'Step 18 base SHA-256: {sha(step18)}',f'Output SHA-256: {sha(out)}',f'Output size: {len(out)} bytes',f'Combined IPS: {len(patch)} bytes; records={len(parse_ips(patch))}',f'Exact clean-source IPS round trip: {apply_ips(src,patch)==out}',f'Records translated: {len(manifests)}', 'Metadata prefixes preserved: YES','Terminator positions preserved: YES','Text pointers changed: NO','Unexpected byte changes outside target payloads vs Step 18: NONE','Codes >= 0x80 in this batch: NONE','FCEUX boss-context R0 bank: NOT YET OBSERVED','FCEUX test: NOT RUN by builder; user test required.','']
    for m in manifests: log.append(f"{m['id']}: {m['encoded_text_bytes']}/{m['content_limit']} content bytes; indexes={','.join(map(str,m['indexes']))}; PASS")
    (ad/'step19_build_validation.txt').write_text('\n'.join(log)+'\n',encoding='utf-8')
    checks=f"{sha(out)}  {args.output_rom.name}\n{sha(patch)}  {args.output_ips.name}\n"
    args.output_rom.with_suffix(args.output_rom.suffix+'.sha256.txt').write_text(checks,encoding='utf-8')
    # Include the trace tool with no registerread usage, for older FCEUX builds.
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
