#!/usr/bin/env python3
"""Build Step 7 refined glyph art + accent-strip diagnostic IPS for Mighty Final Fight.

Uses only the user's matching clean ROM locally. Distributes IPS, never a full ROM.
The Step 7 test replaces the first 13 characters of OPEN_02 with a sequence of
accented glyphs, at the same byte length, so one screenshot can review many marks.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, unicodedata, zlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_ROM_DEFAULT = Path('/mnt/data/Mighty Final Fight (USA).nes')
PROJECT_DEFAULT = Path(__file__).resolve().parents[1]
EXPECTED_SIZE = 262160
EXPECTED_BODY_CRC = 0x3F78037C
HEADER = 16
PRG_SIZE = 131072
CHR_START = HEADER + PRG_SIZE
TILE_BYTES = 16
OPEN_OFFSET = 0x1C9C
EXPECTED_OLD = bytes.fromhex('10 00 12 1e 24 1f 1b 14 00 13 10 28 22')
# À Á Â Ã È Ê Ì Í Ò Ó Ô Õ Ù -> text bytes based on 0x1E00+byte mapping.
TEST_GLYPHS = 'ÀÁÂÃÈÊÌÍÒÓÔÕÙ'
TEST_BYTES = bytes.fromhex('30 31 32 33 34 36 37 38 39 3A 3B 3C 3D')

def sha256(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def decode_tile(chrd: bytes, tid: int):
    t=chrd[tid*TILE_BYTES:(tid+1)*TILE_BYTES]
    return [[((t[y]>>(7-x))&1) | (((t[y+8]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)]
def encode_tile(p):
    out=bytearray(16)
    for y in range(8):
        for x in range(8):
            if p[y][x]: out[y] |= 1<<(7-x)
    # NES 2bpp: black/white pixels use bitplane 0; bitplane 1 remains zero.
    return bytes(out)
def source_shape(chrd, letter, height=5):
    tid=0x1E10+ord(letter)-ord('A')
    src=decode_tile(chrd,tid)
    crop=[r[1:8] for r in src[1:8]]
    result=[]
    for y in range(height):
        sy=min(6,int(y*7/height)); row=[]
        for x in range(6):
            sx=min(6,int(x*7/6)); row.append(1 if crop[sy][sx] else 0)
        result.append(row)
    return result

def decompose(g):
    if g=='Đ': return 'D',['STROKE']
    n=unicodedata.normalize('NFD',g); base=n[0]; marks=[]
    mapping={'\u0302':'CIRCUMFLEX','\u0306':'BREVE','\u0303':'TILDE','\u0300':'GRAVE','\u0301':'ACUTE','\u0309':'HOOK','\u0323':'DOT_BELOW','\u031b':'HORN'}
    for c in n[1:]: marks.append(mapping.get(c,'UNKNOWN_'+format(ord(c),'04X')))
    return base,marks

def draw_tone(p,tone,combined=False,modifier=None):
    # A compact 2x2 diagonal is easier to distinguish than the previous flat dash.
    if not combined:
        if tone=='GRAVE': p[0][2]=1; p[1][3]=1
        elif tone=='ACUTE': p[0][5]=1; p[1][4]=1
        elif tone=='TILDE': p[0][2]=1; p[0][4]=1; p[1][3]=1
        elif tone=='HOOK': p[0][3]=1; p[1][2]=1; p[1][3]=1
        return
    # When a roof modifier also exists, keep its peak at x=3 and move the tone
    # diagonally to a free outside edge.  Avoid glyph/control byte 0x35 entirely.
    if tone=='GRAVE': p[0][1]=1; p[1][0]=1
    elif tone=='ACUTE': p[0][6]=1; p[1][7]=1
    elif tone=='TILDE': p[0][1]=1; p[0][3]=1; p[1][0]=1
    elif tone=='HOOK': p[0][6]=1; p[1][6]=1; p[1][7]=1

def build_glyph(chrd,g):
    base,marks=decompose(g)
    if base not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': raise ValueError((g,base,marks))
    modifier=next((m for m in ('CIRCUMFLEX','BREVE','HORN') if m in marks),None)
    tone=next((m for m in ('GRAVE','ACUTE','HOOK','TILDE') if m in marks),None)
    composite=bool(modifier and tone)
    p=[[0]*8 for _ in range(8)]
    body_y=3 if composite else 2
    body_h=4 if composite else 5
    shape=source_shape(chrd,base,body_h)
    for y in range(body_h):
        for x in range(6): p[body_y+y][x+1]=shape[y][x]
    if 'STROKE' in marks:
        for x in range(1,7): p[4][x]=1
    if modifier=='HORN':
        # Attach horn to the upper-right of O/U without entering a neighboring cell.
        top=3 if composite else 2
        for y,x in ((top,6),(top+1,7),(top+2,7)):
            if y<7: p[y][x]=1
    elif modifier=='CIRCUMFLEX':
        if composite:
            p[1][3]=1; p[2][2]=1; p[2][4]=1
        else:
            p[0][3]=1; p[1][2]=1; p[1][4]=1
    elif modifier=='BREVE':
        if composite:
            p[1][3]=1; p[2][2]=1; p[2][4]=1
        else:
            p[1][2]=1; p[1][3]=1; p[1][4]=1
    if tone: draw_tone(p,tone,composite,modifier)
    if 'DOT_BELOW' in marks:
        p[7][3]=1; p[7][4]=1
    return p,base,marks

def make_ips(records):
    out=bytearray(b'PATCH')
    for off,data in sorted(records,key=lambda x:x[0]):
        out.extend(off.to_bytes(3,'big')); out.extend(len(data).to_bytes(2,'big')); out.extend(data)
    out.extend(b'EOF'); return bytes(out)
def apply_ips(src,patch):
    if not patch.startswith(b'PATCH'): raise ValueError('bad IPS header')
    out=bytearray(src); i=5
    while patch[i:i+3]!=b'EOF':
        if i+5>len(patch): raise ValueError('truncated IPS')
        off=int.from_bytes(patch[i:i+3],'big'); n=int.from_bytes(patch[i+3:i+5],'big'); i+=5
        if n==0:
            if i+3>len(patch): raise ValueError('truncated RLE')
            n=int.from_bytes(patch[i:i+2],'big'); b=patch[i+2]; i+=3; data=bytes([b])*n
        else:
            data=patch[i:i+n]; i+=n
        if off+len(data)>len(out): out.extend(b'\0'*(off+len(data)-len(out)))
        out[off:off+len(data)]=data
    i+=3
    if i!=len(patch): raise ValueError('trailing IPS data')
    return bytes(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--rom',type=Path,default=BASE_ROM_DEFAULT); ap.add_argument('--project',type=Path,default=PROJECT_DEFAULT); a=ap.parse_args()
    rom=a.rom.read_bytes(); project=a.project; analysis=project/'analysis'; analysis.mkdir(parents=True,exist_ok=True)
    if len(rom)!=EXPECTED_SIZE or rom[:4]!=b'NES\x1a': raise SystemExit('Source ROM is not expected iNES ROM/size')
    crc=zlib.crc32(rom[16:])&0xffffffff
    if crc!=EXPECTED_BODY_CRC: raise SystemExit(f'ROM identity mismatch: body CRC {crc:08X}')
    if rom[OPEN_OFFSET:OPEN_OFFSET+len(EXPECTED_OLD)]!=EXPECTED_OLD: raise SystemExit('OPEN_02 byte sequence mismatch; refusing to write test probe')
    chrd=rom[CHR_START:]
    src_csv=analysis/'font_prototype_tiles_step5.csv'
    with src_csv.open(encoding='utf-8-sig',newline='') as f: old=list(csv.DictReader(f))
    old_by_glyph={r['glyph']:r for r in old}
    new_entries=[]; records=[]; modified=bytearray(rom)
    for oldrow in old:
        glyph=oldrow['glyph']; code=int(oldrow['text_byte'],16); tid=0x1E00+code
        off=CHR_START+tid*TILE_BYTES
        orig=rom[off:off+TILE_BYTES]
        if len(orig)!=16 or any(orig): raise SystemExit(f'Target tile not blank: {glyph} at {off:#x}')
        pix,base,marks=build_glyph(chrd,glyph); data=encode_tile(pix)
        modified[off:off+16]=data; records.append((off,data))
        new_entries.append({'glyph':glyph,'unicode':oldrow['unicode'],'base_letter':base,'marks':'+'.join(marks) if marks else 'NONE','text_byte':f'0x{code:02X}','global_chr_tile':f'0x{tid:04X}','chr_file_offset':f'0x{off:06X}','tile_bytes_hex':data.hex(),'revision':'STEP7_DIAGONAL_TONE_MARKS','status':'VISUAL_CANDIDATE_REQUIRES_GAME_REVIEW'})
    modified[OPEN_OFFSET:OPEN_OFFSET+len(TEST_BYTES)]=TEST_BYTES
    records.append((OPEN_OFFSET,TEST_BYTES))
    modified=bytes(modified); patch=make_ips(records); roundtrip=apply_ips(rom,patch)
    if roundtrip!=modified: raise SystemExit('IPS round-trip does not equal expected diagnostic ROM')
    # Strict offset policy: CHR tile bytes and the 13-byte OPEN_02 probe only.
    allowed=set(range(OPEN_OFFSET,OPEN_OFFSET+len(TEST_BYTES)))
    for r in new_entries:
        off=int(r['chr_file_offset'],16); allowed.update(range(off,off+16))
    changed=[i for i,(x,y) in enumerate(zip(rom,modified)) if x!=y]
    if any(i not in allowed for i in changed): raise SystemExit('Unexpected modified ROM offset')
    if modified[:16]!=rom[:16]: raise SystemExit('ROM header changed')
    if any(modified[i]!=rom[i] for i in range(16,CHR_START) if not (OPEN_OFFSET <= i < OPEN_OFFSET+len(TEST_BYTES))): raise SystemExit('PRG changed unexpectedly outside the 13-byte probe')
    with (analysis/'font_prototype_tiles_step7.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(new_entries[0])); w.writeheader(); w.writerows(new_entries)
    (analysis/'font_prototype_tiles_step7.bin').write_bytes(b''.join(bytes.fromhex(r['tile_bytes_hex']) for r in sorted(new_entries,key=lambda r:int(r['text_byte'],16))))
    # Atlas using a native pixel grid plus captions.
    cellw,cellh,cols=100,112,8; rows=(len(new_entries)+cols-1)//cols
    atlas=Image.new('RGB',(cols*cellw,rows*cellh),(248,247,242)); d=ImageDraw.Draw(atlas)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except OSError: font=ImageFont.load_default()
    for i,r in enumerate(sorted(new_entries,key=lambda r:int(r['text_byte'],16))):
        x=(i%cols)*cellw; y=(i//cols)*cellh; d.rectangle((x,y,x+cellw-1,y+cellh-1),fill='white',outline=(220,220,220))
        data=bytes.fromhex(r['tile_bytes_hex']); p=decode_tile(data,0) if False else None
        for yy in range(8):
            for xx in range(8):
                on=(data[yy]>>(7-xx))&1
                color=(20,20,20) if on else (255,255,255)
                d.rectangle((x+8+xx*8,y+6+yy*8,x+15+xx*8,y+13+yy*8),fill=color)
        d.text((x+8,y+76),f"{r['glyph']}  {r['text_byte']}",font=font,fill=(20,20,20))
        d.text((x+8,y+91),r['marks'],font=font,fill=(70,70,70))
        d.text((x+8,y+101),r['global_chr_tile'],font=font,fill=(100,100,100))
    atlas.save(analysis/'font_prototype_step7.png')
    ips_path=analysis/'Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips'; ips_path.write_bytes(patch)
    report={'project_step':7,'artifact_type':'experimental Vietnamese accented-glyph diagnostic IPS, not translation release','source_rom':a.rom.name,'source_size_bytes':len(rom),'source_sha256':sha256(rom),'source_body_crc32':f'{crc:08X}','patched_diagnostic_sha256':sha256(modified),'ips_file':ips_path.name,'ips_size_bytes':len(patch),'ips_records':len(records),'glyph_tiles':len(new_entries),'glyph_tile_bytes':len(new_entries)*16,'probe':{'offset':f'0x{OPEN_OFFSET:06X}','original_bytes_hex':EXPECTED_OLD.hex(' '),'new_bytes_hex':TEST_BYTES.hex(' '),'glyph_sequence':TEST_GLYPHS,'same_length':len(EXPECTED_OLD)==len(TEST_BYTES),'effect':'replaces line “A COUPLE DAYS” with 13 accented glyphs; line 2 stays “LATER...”'},'checks':{'base_rom_identity_verified':True,'all_67_slots_blank_in_source':True,'roundtrip_ips_exact':roundtrip==modified,'header_unchanged':modified[:16]==rom[:16],'prg_unchanged_except_13_byte_probe':all(modified[i]==rom[i] for i in range(16,CHR_START) if not (OPEN_OFFSET<=i<OPEN_OFFSET+len(TEST_BYTES))),'only_candidate_chr_tiles_plus_13_byte_probe_changed':all(i in allowed for i in changed),'modified_offsets_count':len(changed)},'step6_user_screenshot_review':{'screenshot_received':True,'assessment':'The A->À probe appears at the intended first character; the grave tone appears as a small flat dash and needs a more diagonal mark. This supports the basic tile selection/render path for À, but does not validate all extended bytes or unrelated tile reuse.'},'emulator_tested_by_assistant':False,'user_reported_step6_screenshot':True,'release_ready':False,'warnings':['Experimental diagnostic only; not a translated ROM.','Step 7 accent sequence is not yet tested in an emulator.','All extended-byte codes still need dialogue-path compatibility testing.','All candidate blank tiles still need a full playthrough/other-screen reuse check.']}
    (analysis/'font_test_rom_report_step7.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Create screenshot crop + design comparison card.
    ss=Path('/mnt/data/Screenshot 2026-10-09 174150.png')
    if ss.exists():
        img=Image.open(ss).convert('RGB')
        crop=img.crop((106,335,132,362)).resize((260,270),Image.Resampling.NEAREST)
        crop.save(analysis/'step6_screenshot_glyph_zoom.png')
    # comparison card: source screenshot first glyph crop vs revised candidate tile
    card=Image.new('RGB',(820,270),(245,245,245)); cd=ImageDraw.Draw(card)
    try: head=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18); small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except OSError: head=small=ImageFont.load_default()
    cd.text((20,12),'STEP 6 observed output',font=head,fill=(0,0,0)); cd.text((440,12),'STEP 7 À tile candidate',font=head,fill=(0,0,0))
    if ss.exists():
        crop=Image.open(ss).convert('RGB').crop((110,339,126,360)).resize((128,168),Image.Resampling.NEAREST); card.paste(crop,(20,44))
    first=next(r for r in new_entries if r['glyph']=='À'); data=bytes.fromhex(first['tile_bytes_hex'])
    for y in range(8):
        for x in range(8):
            on=(data[y]>>(7-x))&1; col=(30,30,30) if on else (255,255,255)
            cd.rectangle((460+x*16,44+y*16,475+x*16,59+y*16),fill=col,outline=(200,200,200))
    cd.text((20,230),'Observed: tone appears too horizontal at native scale.',font=small,fill=(30,30,30)); cd.text((440,230),'Redrawn tone: two-pixel diagonal.',font=small,fill=(30,30,30))
    card.save(analysis/'step7_accent_mark_comparison.png')
    md=f'''# Step 7 — screenshot review and refined accent-strip test\n\n## User screenshot review\n\nThe supplied Step 6 screenshot shows that the first character was changed from `A` to the `À` candidate at the expected position. The accent is visible, but it looks like a short horizontal dash at display size. This is useful evidence that the candidate tile byte reached the renderer, while also revealing that the grave accent artwork should be redesigned. The screenshot does not prove every byte code is safe or that unused tiles are never referenced elsewhere.\n\n## What changed\n\n- Redesigned tone marks to use diagonal pixel strokes where space permits; composite glyphs with circumflex/breve/horn plus tone move the tone mark toward a free edge.\n- Rebuilt all {len(new_entries)} candidate glyph tiles and generated `font_prototype_step7.png`, CSV, and packed binary.\n- Created `Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips`, an experimental diagnostic patch. It writes the font tiles and replaces the first 13 characters of the opening line `A COUPLE DAYS` with `{TEST_GLYPHS}`. The next line `LATER...` is left unchanged. The edit remains 13 bytes long and does not move pointers.\n\n## Validation\n\n- Source ROM identity verified by size and body CRC32 `{crc:08X}`.\n- All 67 candidate target tiles are blank in the source ROM.\n- IPS application round-trips exactly to the expected diagnostic image.\n- iNES header is unchanged; PRG changes are limited to the 13-byte opening-line probe, and CHR changes are limited to candidate glyph tiles.\n\n## Limitations\n\nThe user screenshot is evidence for the Step 6 `À` test only. Step 7's 13-glyph strip has not yet been tested in an emulator. This remains a diagnostic patch, not a full translation release. Extended codes, other screens, credits, dialogue metadata, and glyph legibility still need validation.\n'''
    (analysis/'step7_screenshot_review_and_test_plan.md').write_text(md,encoding='utf-8')
    lines=['STEP 7 REFINED GLYPH + ACCENT STRIP BUILD',f'Source SHA-256: {sha256(rom)}',f'Patched diagnostic SHA-256: {sha256(modified)}',f'Body CRC32: {crc:08X}',f'Glyphs built: {len(new_entries)}; CHR payload: {len(new_entries)*16} bytes',f'Probe sequence: {TEST_GLYPHS}',f'IPS size: {len(patch)} bytes; records: {len(records)}',f'Changed file bytes: {len(changed)}','PASS: all 67 target tiles blank in clean source','PASS: test line replacement retains 13-byte length','PASS: IPS application reproduces expected diagnostic image exactly','PASS: iNES header unchanged','PASS: PRG unchanged except the 13-byte opening-line probe','PASS: changed offsets limited to the 67 candidate CHR tiles and 13-byte test probe','NOT TESTED: Step 7 IPS in Mesen/FCEUX','STATUS: experimental multi-glyph diagnostic; not a playable Vietnamese translation']
    (analysis/'step7_build_validation.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # create an apply helper with strict source and patched checksums
    helper=f'''#!/usr/bin/env python3\n"""Apply Step 7 accent-strip diagnostic IPS to matching clean ROM. Not a release patch."""\nfrom pathlib import Path\nimport argparse,hashlib\nEXPECTED_BASE_SHA256={sha256(rom)!r}\nEXPECTED_OUTPUT_SHA256={sha256(modified)!r}\ndef apply(src,p):\n    if not p.startswith(b'PATCH'): raise ValueError('bad IPS header')\n    out=bytearray(src); i=5\n    while p[i:i+3]!=b'EOF':\n        off=int.from_bytes(p[i:i+3],'big'); n=int.from_bytes(p[i+3:i+5],'big'); i+=5\n        if n: data=p[i:i+n]; i+=n\n        else:\n            n=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; data=bytes([v])*n\n        if off+len(data)>len(out): out.extend(b'\\0'*(off+len(data)-len(out)))\n        out[off:off+len(data)]=data\n    return bytes(out)\ndef main():\n    ap=argparse.ArgumentParser(); ap.add_argument('--rom',required=True,type=Path); ap.add_argument('--patch',type=Path,default=Path(__file__).resolve().parents[1]/'analysis'/'Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips'); ap.add_argument('--output',type=Path,default=Path('Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.nes')); a=ap.parse_args()\n    base=a.rom.read_bytes(); bh=hashlib.sha256(base).hexdigest()\n    if bh!=EXPECTED_BASE_SHA256: raise SystemExit(f'REFUSED: base SHA-256 mismatch: {{bh}}')\n    out=apply(base,a.patch.read_bytes()); oh=hashlib.sha256(out).hexdigest()\n    if oh!=EXPECTED_OUTPUT_SHA256: raise SystemExit(f'REFUSED: output SHA-256 mismatch: {{oh}}')\n    a.output.write_bytes(out); print('PASS: base hash verified'); print('PASS: diagnostic output hash verified'); print(f'Wrote {{a.output.resolve()}}'); print('WARNING: accent-strip diagnostic only, not a translation release.')\nif __name__=='__main__': main()\n'''
    helper_path=project/'tools'/'apply_font_test_ips_step7.py'; helper_path.write_text(helper,encoding='utf-8'); helper_path.chmod(0o755)
    print('\n'.join(lines))
if __name__=='__main__': main()
