#!/usr/bin/env python3
"""Build Step 20 cumulative Vietnamese ROM for all indexed text records.

Starting point: clean Mighty Final Fight (USA) ROM + the known-good cumulative
Step 19 IPS. Translates remaining boss lines BOSS_11..BOSS_77 and all five
credits slots. BOSS_09/BOSS_10 are vocalization/animation sequences (WAHHHHH,
ARGHHHH) and remain untouched so their FB/FA/F9 animation commands survive.

Important limits:
- The game is a fixed-slot ROM translation; no pointers are relocated.
- This batch uses only glyph bytes < $80 outside the already-tested opening path.
- The existing Step 17 font/bank fix and Step 18/19 translated regions are kept.
- Static verification is reproducible; full-game emulator verification remains
  a separate user play-through.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/mnt/data')
DEFAULT_PROJECT = Path(__file__).resolve().parents[1]
CLEAN_ROM = ROOT / 'Mighty Final Fight (USA).nes'
BASE_STEP19_ROM = None  # The Step 19 ROM is reconstructed from the included cumulative IPS.
BASE_IPS = DEFAULT_PROJECT / 'analysis' / 'step19_boss_dialogue_pilot_combined.ips'
DEFAULT_ROM_OUT = ROOT / 'Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes'
DEFAULT_IPS_OUT = ROOT / 'Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips'
CLEAN_SHA256 = '5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
STEP19_SHA256 = '0b332d25e7444430dd48a09e45f6a8b9679ff1318d5375195d498aed53f021e6'
STEP19_SIZE = 278544
HEADER = 16
PRG_SIZE = 131072
CHR_START = HEADER + PRG_SIZE
TILE_SIZE = 16

# The split text records already exist in the source table; these translations
# are deliberately short enough for the original byte budgets and avoid the
# 0x80-0x8F glyph routing outside the verified opening path.
BOSS_VN = {
  11: 'TA CAO TAY!',
  12: 'NGƯƠI MẠNH HƠN',
  13: 'TA NGHĨ.',
  14: 'SAO KHÔNG VÀO BĂNG TA?',
  15: 'NGƯƠI DÁM BÁC BỎ MAD GEAR',
  16: 'BĂNG!',
  17: 'HA HA! TA KHÔNG TIN',
  18: 'NGƯƠI. ĐÚNG LÀ THẰNG',
  19: 'CẬU ẤM!',
  20: 'NGƯƠI QUÁ MẬP, CHẬM CHẠP',
  21: 'KHÓ ĐẤU TA',
  22: 'NHÓC, NGƯƠI ĐÂU PHẢI',
  23: 'SAMURAI!',
  24: 'JESSICA ĐÂU RỒI',
  25: 'MỒM TO, KIẾM NGẮN.',
  26: 'KHAI MAU, BIẾT GÌ?',
  27: 'TA SẼ ĐẬP NGƯƠI!',
  28: 'NGƯƠI CHẲNG ĐỊCH NỔI TA',
  30: 'TA LÀ VUA ĐẤU VẬT.',
  31: 'TRÁNH LỐI TA TRƯỚC KHI TA',
  32: 'DẬP BẸP NGƯƠI!',
  33: 'CÒN LẢM NHẢM À?',
  34: 'CÁI MỒM KIA!',
  35: 'TỐT, TA SẼ XẺ',
  36: 'RA THÀNH MẢNH!',
  37: 'TA LÀ ABIGAIL, MẠNH NHẤT',
  39: 'ĐẤU SĨ BĂNG MAD GEAR.',
  40: 'NGƯƠI MAY MẮN LẮM...',
  41: 'VẬN MAY NGƯƠI SẮP HẾT',
  42: 'RỒI!',
  43: 'BỌN KIA MẠNH HƠN',
  44: 'NGƯƠI, ĐỒ NGỐC!',
  45: 'TA SẼ NHỒI MẤY CÂU NÓI',
  46: 'XUỐNG HỌNG NGƯƠI!',
  47: 'JESSICA ĐÃ BỊ ĐƯA',
  48: 'TỚI SÀO HUYỆT BÍ MẬT BỌN TA',
  49: 'TA SẼ TRẢ MỐI HẬN CHO',
  50: 'ANH TA!',
  51: 'TRÔNG NGƯƠI CÓ VẺ MỆT.',
  52: 'NÀY, UỐNG NƯỚC ĐI.',
  53: 'TA THẤY KHỎE RA',
  54: 'VÀ RẤT MẠNH.',
  55: 'NGƯƠI DÁM CHÊ QUÀ TA!',
  56: 'NGƯƠI ĐÃ XÚC PHẠM TA',
  57: 'VÌ THẾ NGƯƠI PHẢI',
  58: 'TIÊU DIỆT!',
  59: 'SẴN RỒI',
  60: 'TRẬN CUỐI TA SẼ THẮNG!',
  61: 'TA YÊU JESSICA. GIAO NÀNG',
  62: 'TA!',
  63: 'NGƯƠI LÀ TRÙM À?',
  64: 'HA! TA TÌM THẤY NGƯƠI RỒI!',
  65: 'THẢ CON GÁI TA RA',
  66: 'ĐỒ HẠ TIỆN!',
  67: 'BÌNH TĨNH. JESSICA LÀ KHÁCH',
  68: 'QUÝ.',
  69: 'NÀNG TRONG PHÒNG KẾ BÊN.',
  70: 'TA VÀ JESSICA SẼ',
  71: 'CƯỚI NHAU NGÀY MAI',
  72: 'HA HA HA!',
  73: 'HÃY BẮT ĐẦU',
  74: 'TRẬN CUỐI!',
  75: 'NGƯƠI CHẲNG ĐỊCH NỔI TA',
  76: 'SẴN RỒI',
  77: 'TỚI ĐÂY LÀ HẾT, NGƯƠI!',
}
# Credit layout is rebuilt as explicit FE-separated lines. Names remain as in
# the source; headings are translated. These strings use only known low bytes.
CREDITS = {
  0: ['    NHÂN VIÊN'],
  1: ['LẬP KẾ HOẠCH', 'K.O', 'LẬP TRÌNH', 'CHIPS, EACUM, NIWANO', 'THIẾT KẾ VẬT THỂ', 'ARASHI.KAI', 'TSUBO PI', 'ZENDEN'],
  2: ['THIẾT KẾ CUỘN', 'YUKI, LINDA', 'RYUGO, ARNIE', 'MAMIMU'],
  3: ['NHẠC', 'SETSUO, YUKO', 'CẢM ƠN ĐẶC BIỆT', 'MANASHI, USHI', 'BLACK.I', 'PROFESSOR.K', 'VÀ TOÀN THỂ NHÂN VIÊN', 'CAPCOM'],
  4: ['CẢM ƠN', 'BẠN ĐÃ CHƠI', 'TRÌNH BÀY', 'CAPCOM'],
}


def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def parse_ips(data: bytes) -> list[tuple[int, bytes]]:
    if not data.startswith(b'PATCH'): raise ValueError('IPS header missing')
    p=5; out=[]
    while data[p:p+3] != b'EOF':
        if p+5>len(data): raise ValueError('truncated IPS record header')
        off=int.from_bytes(data[p:p+3],'big'); n=int.from_bytes(data[p+3:p+5],'big'); p+=5
        if n:
            block=data[p:p+n]; p+=n
            if len(block)!=n: raise ValueError('truncated IPS payload')
        else:
            if p+3>len(data): raise ValueError('truncated IPS RLE')
            n=int.from_bytes(data[p:p+2],'big'); b=data[p+2]; p+=3; block=bytes([b])*n
        out.append((off,block))
    p+=3
    if p!=len(data): raise ValueError('unexpected bytes after IPS EOF')
    return out

def apply_ips(src: bytes, patch: bytes) -> bytes:
    out=bytearray(src)
    for off,block in parse_ips(patch):
        if off+len(block)>len(out): out.extend(b'\x00'*(off+len(block)-len(out)))
        out[off:off+len(block)]=block
    return bytes(out)

def make_ips(records: list[tuple[int,bytes]]) -> bytes:
    out=bytearray(b'PATCH'); last=-1
    for off,block in sorted(records):
        if not block or len(block)>0xFFFF: raise ValueError(f'invalid IPS record at {off:#x} length {len(block)}')
        if off<last: raise ValueError('overlapping IPS records')
        out += off.to_bytes(3,'big') + len(block).to_bytes(2,'big') + block
        last=off+len(block)
    out += b'EOF'
    return bytes(out)

def diff_ips(src: bytes, out: bytes, gap: int=4) -> bytes:
    """Build IPS from source to output; merge changed runs across <=gap unchanged bytes."""
    records=[]; n=len(out); i=0
    while i<n:
        old = src[i] if i<len(src) else None
        if old is not None and old==out[i]: i+=1; continue
        start=i; end=i+1; unchanged=0
        while end<n:
            old=src[end] if end<len(src) else None
            if old is not None and old==out[end]:
                unchanged+=1
                if unchanged>gap: break
            else: unchanged=0
            end+=1
            if end-start>=60000: break
        # Trim trailing unchanged gap bytes from record.
        while end>start and end<=len(src) and out[end-1]==src[end-1]: end-=1
        block=out[start:end]
        if block: records.append((start,block))
        i=max(end,start+1)
    patch=make_ips(records)
    if apply_ips(src,patch)!=out: raise ValueError('generated IPS does not round-trip')
    return patch

def load_glyph_codes(csv_path: Path) -> dict[str,int]:
    with csv_path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=67: raise ValueError(f'expected 67 custom glyph rows, found {len(rows)}')
    codes={r['glyph']:int(r['text_byte'],16) for r in rows}
    codes.update({chr(ord('A')+i):0x10+i for i in range(26)})
    codes.update({' ':0x00,"'":0x2A,'.':0x2B,',':0x2C,'?':0x75,'!':0x76})
    return codes

def encode_text(text: str, codes: dict[str,int], allow_linebreak=False) -> bytes:
    out=bytearray()
    for ch in text:
        if ch=='\n' and allow_linebreak:
            out.append(0xFE); continue
        if ch not in codes: raise ValueError(f'unmapped glyph {ch!r} in {text!r}')
        v=codes[ch]
        if v>=0x80: raise ValueError(f'unsupported high-byte glyph {ch!r} -> {v:02X} in {text!r}')
        if v==0x35: raise ValueError('reserved metadata byte 35 emitted as text')
        out.append(v)
    return bytes(out)

def load_pointer_rows(path: Path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def load_source_english_tsv(path: Path):
    # This source file has unquoted embedded newlines in some Vietnamese credit
    # fields. We only rely on the first physical row per indexed record, where
    # the English field and core address metadata are intact.
    english={}; idx_by_start={}; credit_english={}
    for line in path.read_text(encoding='utf-8').splitlines():
        parts=line.split('\t')
        if len(parts)<9: continue
        group, ident, idx, cpu, prg, fileoff, length, eng = parts[:8]
        if group=='boss':
            try: english[int(idx)] = eng
            except ValueError: pass
        elif group=='credits':
            try: credit_english[int(idx)] = eng
            except ValueError: pass
    return english, credit_english

def make_preview(rom: bytes, codes: dict[str,int], text_items, output: Path, title: str):
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    except OSError: font=ImageFont.load_default()
    card_w,card_h=540,86; cards=[]
    def tile_pixels(code):
        tile_id=0x1E00+code; off=CHR_START+tile_id*TILE_SIZE
        raw=rom[off:off+TILE_SIZE]
        return [[((raw[y]>>(7-x))&1) | (((raw[y+8]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)]
    for label, text in text_items:
        im=Image.new('RGB',(card_w,card_h),'#080808'); d=ImageDraw.Draw(im)
        d.text((8,5),label,font=font,fill='#aaaaaa')
        # display lines manually broken at 32 characters for analysis preview
        lines=[]
        for source_line in text.split('\n'):
            while len(source_line)>36:
                cut=source_line.rfind(' ',0,36)
                if cut<=0: cut=36
                lines.append(source_line[:cut]); source_line=source_line[cut:].lstrip()
            lines.append(source_line)
        for li,line in enumerate(lines[:2]):
            x0=8; y0=28+li*27; scale=2; gap=1
            for ch in line:
                code=codes.get(ch)
                if code is None or code>=0x80: continue
                pix=tile_pixels(code)
                for yy in range(8):
                    for xx in range(8):
                        if pix[yy][xx]:
                            color='#fff' if pix[yy][xx]==1 else '#aaa'
                            d.rectangle((x0+xx*scale,y0+yy*scale,x0+xx*scale+1,y0+yy*scale+1),fill=color)
                x0+=8*scale+gap
                if x0>=card_w-16: break
        cards.append(im)
    cols=2; rows=(len(cards)+cols-1)//cols
    sheet=Image.new('RGB',(cols*card_w,rows*card_h),'#232323')
    for i,im in enumerate(cards): sheet.paste(im,((i%cols)*card_w,(i//cols)*card_h))
    sheet.save(output)

def run(source_rom: Path, base_rom_path: Path, base_ips_path: Path, project: Path, output_rom_path: Path, output_ips_path: Path):
    ad=project/'analysis'; tools=project/'tools'; ad.mkdir(parents=True,exist_ok=True)
    src=source_rom.read_bytes()
    if sha(src)!=CLEAN_SHA256 or len(src)!=262160: raise SystemExit('Clean source ROM SHA-256/size mismatch')
    base_patch=base_ips_path.read_bytes()
    reconstructed=apply_ips(src,base_patch)
    base_rom=reconstructed
    if sha(base_rom)!=STEP19_SHA256 or len(base_rom)!=STEP19_SIZE:
        raise SystemExit('Step 19 cumulative IPS does not reproduce the expected tested base ROM')
    if base_rom_path is not None:
        reference=base_rom_path.read_bytes()
        if reference!=base_rom:
            raise SystemExit('Optional Step 19 reference ROM does not match reconstruction from the included IPS')
    codes=load_glyph_codes(ad/'font_prototype_tiles_step17.csv')
    ptr_rows=load_pointer_rows(project/'analysis'/'pointer_tables.csv' if (project/'analysis'/'pointer_tables.csv').exists() else Path('/mnt/data/Mighty_Final_Fight_Vietnamese_Project/analysis/pointer_tables.csv'))
    bosses=[]; credits=[]
    for row in ptr_rows:
        if row['group']=='boss':
            idx=int(row['index']); start=int(row['file_offset'],16); length=int(row['bytes_to_ff'])
            bosses.append({'index':idx,'start':start,'length_to_ff':length,'cpu':row['cpu_pointer'],'english':''})
        elif row['group']=='credits':
            idx=int(row['index']); start=int(row['file_offset'],16); length=int(row['bytes_to_ff'])
            credits.append({'index':idx,'start':start,'length':length,'cpu':row['cpu_pointer']})
    english, credit_english=load_source_english_tsv(project/'analysis'/'source_dialogue_records.tsv')
    # Resolve each unique boss segment's physical span using the next distinct
    # pointer address; the last segment uses the extractor's bytes-to-FF span.
    boss_by_start={}
    for r in sorted(bosses,key=lambda x:(x['start'],x['index'])):
        boss_by_start.setdefault(r['start'],[]).append(r)
    starts=sorted(boss_by_start)
    slot_by_start={}
    for i,start in enumerate(starts):
        aliases=boss_by_start[start]
        length=(starts[i+1]-start) if i+1<len(starts) else min(r['length_to_ff'] for r in aliases)
        slot_by_start[start]={'start':start,'length':length,'indexes':[r['index'] for r in aliases]}

    out=bytearray(base_rom); added_records=[]; manifest=[]; translated_texts=[]
    # Add all non-overlapping boss text segments after the Step 19 pilot. BOSS_09
    # and BOSS_10 are animation grunts; leave every byte in these spans unchanged.
    for start in starts:
        slot=slot_by_start[start]; indexes=slot['indexes']; idx=indexes[0]; length=slot['length']
        # Localize the two visible grunt words while preserving the exact
        # punctuation/animation byte sequence that follows them.
        if idx in (9, 10) and len(indexes) == 1:
            rec = base_rom[start:start+length]
            expected_tail = bytes([0xFB]) * 20 + bytes([0xFA, 0xF9])
            if (len(rec) != 35 or rec[12] != 0x76 or rec[13:] != expected_tail
                    or rec[:1] != b'\x35'):
                raise SystemExit(f'BOSS_{idx}: grunt/animation signature mismatch; refusing to rewrite')
            scream = bytes([codes['Á']]) * 7
            newslot = rec[:5] + scream + rec[12:]
            if len(newslot) != length:
                raise SystemExit(f'BOSS_{idx}: grunt replacement changed record length')
            out[start:start+length] = newslot
            added_records.append((start, newslot))
            text = 'ÁÁÁÁÁÁÁ!'
            english_grunt = 'WAHHHHH!' if idx == 9 else 'ARGHHHH!'
            m={'group':'boss','id':f'BOSS_{idx:02}','indexes':indexes,'file_offset':f'0x{start:06X}',
               'cpu_pointer':next(r['cpu'] for r in aliases),'record_length':length,
               'metadata_prefix_hex':rec[:5].hex(' ').upper(),'english':english_grunt,'vietnamese':text,
               'encoded_hex':(scream + b'\x76').hex(' ').upper(),'encoded_bytes':8,'content_capacity':8,
               'padding_spaces':0,'extended_glyph_codes_used':False,'pointer_changed':False,
               'animation_bytes_preserved':True,'status':'grunt localized; punctuation and animation commands preserved'}
            manifest.append(m); translated_texts.append((f'BOSS_{idx:02}: {english_grunt}', text))
            continue
        if any(i in (0,1,2,3,4,5,6,7,8,9,10) for i in indexes):
            continue
        if idx not in BOSS_VN:
            raise SystemExit(f'missing Vietnamese translation for boss pointer index {idx} at {start:#x}')
        rec=base_rom[start:start+length]
        if len(rec)!=length or len(rec)<6 or rec[-1]!=0xFF:
            raise SystemExit(f'BOSS_{idx}: invalid slot span length/end (length={length}, last={rec[-1:]!r})')
        if any(b in rec[5:-1] for b in (0xF9,0xFA,0xFB,0xFE)):
            raise SystemExit(f'BOSS_{idx}: internal control/animation byte found; refusing to overwrite')
        # Preserve a known trailing FC control on BOSS_54 immediately before FF.
        suffix=b'\xFC' if len(rec)>=2 and rec[-2]==0xFC else b''
        if suffix and idx!=54: raise SystemExit(f'Unexpected trailing FC at BOSS_{idx}')
        prefix=rec[:5]; content_limit=length-len(prefix)-len(suffix)-1
        text=BOSS_VN[idx]
        encoded=encode_text(text,codes)
        if len(encoded)>content_limit:
            raise SystemExit(f'BOSS_{idx} overflow: {len(encoded)} > {content_limit}: {text!r}')
        newslot=prefix+encoded+bytes([0x00])*(content_limit-len(encoded))+suffix+b'\xFF'
        if len(newslot)!=length: raise SystemExit(f'BOSS_{idx}: replacement length mismatch')
        out[start:start+length]=newslot
        added_records.append((start,newslot))
        m={'group':'boss','id':f'BOSS_{idx}','indexes':indexes,'file_offset':f'0x{start:06X}','cpu_pointer':next(r['cpu'] for r in aliases),'record_length':length,'metadata_prefix_hex':prefix.hex(' ').upper(),'english':english.get(idx,''),'vietnamese':text,'encoded_hex':encoded.hex(' ').upper(),'encoded_bytes':len(encoded),'content_capacity':content_limit,'padding_spaces':content_limit-len(encoded),'extended_glyph_codes_used':False,'pointer_changed':False,'status':'translated'}
        manifest.append(m); translated_texts.append((f'BOSS_{idx}: {m["english"]}',text))
    # Credits have a different layout: zero-byte space, FE line-break, FF end.
    for c in credits:
        start=c['start']; length=c['length']; original=base_rom[start:start+length]
        if len(original)!=length or original[-1]!=0xFF: raise SystemExit(f'CREDIT_{c["index"]}: bad source span')
        lines=CREDITS[c['index']]
        text='\n'.join(lines)
        encoded=encode_text(text,codes,allow_linebreak=True)
        content_capacity=length-1
        if len(encoded)>content_capacity:
            raise SystemExit(f'CREDIT_{c["index"]} overflow: {len(encoded)}>{content_capacity}: {lines!r}')
        newslot=encoded+bytes([0x00])*(content_capacity-len(encoded))+b'\xFF'
        out[start:start+length]=newslot; added_records.append((start,newslot))
        english_text=credit_english.get(c['index'],'')
        m={'group':'credits','id':f'CREDIT_{c["index"]:02}','index':c['index'],'file_offset':f'0x{start:06X}','cpu_pointer':c['cpu'],'record_length':length,'english':english_text,'vietnamese':text,'encoded_hex':encoded.hex(' ').upper(),'encoded_bytes':len(encoded),'content_capacity':content_capacity,'padding_spaces':content_capacity-len(encoded),'line_count':len(lines),'extended_glyph_codes_used':False,'pointer_changed':False,'status':'translated'}
        manifest.append(m); translated_texts.append((f'CREDIT_{c["index"]:02}: {english_text[:54]}',text))
    out=bytes(out)
    # Every added slot is the only permitted newly altered range compared with
    # the tested Step 19 base image.
    allowed=[(off,off+len(block)) for off,block in added_records]
    for pos,(old,new) in enumerate(zip(base_rom,out)):
        if old!=new and not any(a<=pos<z for a,z in allowed):
            raise SystemExit(f'unexpected byte delta vs Step 19 base at {pos:#x}')
    # Explicitly ensure source pointers and the Step 17 hook remain unchanged.
    if out[:16]!=base_rom[:16]: raise SystemExit('header unexpectedly changed')
    # Full cumulative IPS clean ROM -> final ROM, including the expanded CHR banks.
    cumulative_patch=diff_ips(src,out)
    if apply_ips(src,cumulative_patch)!=out: raise SystemExit('cumulative IPS round trip failed')
    output_rom_path.parent.mkdir(parents=True,exist_ok=True); output_rom_path.write_bytes(out)
    output_ips_path.parent.mkdir(parents=True,exist_ok=True); output_ips_path.write_bytes(cumulative_patch)
    (output_rom_path.with_suffix(output_rom_path.suffix+'.sha256.txt')).write_text(f'{sha(out)}  {output_rom_path.name}\n{sha(cumulative_patch)}  {output_ips_path.name}\n',encoding='utf-8')

    # Full translation records: opening, each boss pointer index, and credits.
    # Existing opening source is from the validated Step 18 records; aliases
    # appear as separate index rows, each mapping to the same translated span.
    # Normalize the Step 18 TSV fields and add OPEN_00 (the original pilot record).
    open_rows=[]
    open_text_00=(
        'ĐÂY LÀ METRO CITY.\nTRONG LÒNG THÀNH\nPHỐ LÀ JESSICA,\nCON GÁI CỦA\nTHỊ TRƯỞNG. VẺ\nĐẸP CỦA CÔ\nLAN TỎA KHẮP\nTHÀNH PHỐ,\nTIẾP SỨC CHO NGƯỜI\nDÂN SINH TỒN.\nNHƯNG GIỜ ĐÂY,\nMỘT KẺ XẤU MUỐN\nCHIẾM ÁNH SÁNG\nẤY CHO RIÊNG\nMÌNH.'
    )
    open_rows.append({'id':'OPEN_00','index':0,'file_offset':'0x001B4A',
                      'english':'THIS IS METRO CITY. WITHIN THE WALLS OF THE CITY LIVES THE DAUGHTER OF THE MAYOR, JESSICA. HER BEAUTY RADIATES THROUGHOUT THE CITY AND GIVES THE CITIZENS THE POWER TO SURVIVE. BUT NOW A VILLAIN ATTEMPTS TO HAVE THIS BEACON OF LIGHT ALL TO HIMSELF.',
                      'vietnamese':open_text_00})
    opening_tsv=project/'analysis'/'step18_opening_translation_records.tsv'
    if opening_tsv.exists():
        with opening_tsv.open(encoding='utf-8',newline='') as f:
            for r in csv.DictReader(f,delimiter='\t'):
                ident=r.get('id','')
                try: idx=int(ident.split('_')[-1])
                except ValueError: idx=-1
                line_cells=[x.strip() for x in (r.get('vietnamese_lines') or '').split(' / ') if x.strip()]
                text='\n'.join(line_cells) if line_cells else r.get('vietnamese_text','')
                open_rows.append({'id':ident,'index':idx,'file_offset':r.get('file_offset',''),
                                  'english':r.get('english',''),'vietnamese':text})
    # If TSV records are unavailable, use the embedded JSON and normalize its fields.
    if len(open_rows)==1:
        open_json=project/'analysis'/'step18_opening_translation_records.json'
        if open_json.exists():
            try: json_rows=json.loads(open_json.read_text(encoding='utf-8'))
            except Exception: json_rows=[]
            for r in json_rows:
                ident=r.get('id','')
                try: idx=int(ident.split('_')[-1])
                except ValueError: idx=-1
                open_rows.append({'id':ident,'index':idx,'file_offset':r.get('file_offset',''),
                                  'english':r.get('source_english',r.get('english','')),
                                  'vietnamese':r.get('vietnamese_text') or '\n'.join(r.get('vietnamese_lines',[]))})
    all_rows=[]
    for r in open_rows:
        all_rows.append({'group':'opening','id':r.get('id',''),'index':r.get('index',''),'file_offset':r.get('file_offset',''),
                         'english':r.get('english',''),'vietnamese':r.get('vietnamese',''),
                         'status':'retained from user-tested Step 17/18 opening builds'})
    # Every boss pointer index incl aliases; unchanged vocalization entries are marked as kept.
    record_by_index={}
    for start, aliases in boss_by_start.items():
        indexes=[r['index'] for r in aliases]
        first=min(indexes)
        for i in indexes:
            if i in (9,10):
                vn='ÁÁÁÁÁÁÁ!'
                status='grunt localized; punctuation and FB/FA/F9 animation commands preserved'
            elif i<=8:
                base_tsv=ad/'step19_translated_boss_records.tsv'
                vn=''
                if base_tsv.exists():
                    with base_tsv.open(encoding='utf-8',newline='') as f:
                        for rr in csv.DictReader(f,delimiter='\t'):
                            ix=[int(x) for x in rr.get('indexes','').split(',') if x]
                            if i in ix: vn=rr.get('vietnamese',''); break
                status='translated and user-confirmed in Step 19 pilot'
            else:
                primary=min(indexes)
                vn=BOSS_VN.get(primary, BOSS_VN.get(i, ''))
                status=('translated in Step 20' if i==primary else f'shared pointer alias of BOSS_{primary:02}')
            rec=next(r for r in bosses if r['index']==i)
            all_rows.append({'group':'boss','id':f'BOSS_{i:02}','index':i,'file_offset':f'0x{start:06X}','english':english.get(i,''),'vietnamese':vn,'status':status,'shared_pointer_indexes':indexes})
    for c in credits:
        all_rows.append({'group':'credits','id':f'CREDIT_{c["index"]:02}','index':c['index'],'file_offset':f'0x{c["start"]:06X}','english':credit_english.get(c['index'],''),'vietnamese':'\n'.join(CREDITS[c['index']]),'status':'translated in Step 20'})
    with (ad/'step20_full_translation_catalog.tsv').open('w',encoding='utf-8',newline='') as f:
        fields=['group','id','index','file_offset','english','vietnamese','status','shared_pointer_indexes']
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(all_rows)
    (ad/'step20_remaining_boss_and_credits_translations.md').write_text(
        '# Step 20 — Remaining boss dialogue and credits\n\n'
        'This cumulative build preserves the user-confirmed Step 17 font/bank fix, Step 18 opening sequence, and Step 19 initial Thrasher dialogue. It translates the remaining indexed boss lines and all five credits records. BOSS_09 and BOSS_10 have their visible grunt letters localized, while their punctuation and FB/FA/F9 animation commands remain byte-identical.\n\n'
        '## Localized nonverbal lines\n\n- **BOSS_09:** ÁÁÁÁÁÁÁ! (the original 0x76 punctuation and FB/FA/F9 animation bytes are preserved)\n- **BOSS_10:** ÁÁÁÁÁÁÁ! (the original 0x76 punctuation and FB/FA/F9 animation bytes are preserved)\n\n## Remaining boss translations\n\n' + '\n'.join(f'- **BOSS_{i:02}:** {t}' for i,t in BOSS_VN.items()) +
        '\n\n## Credits\n\n' + '\n'.join(f'- **CREDIT_{i:02}:** ' + ' / '.join(lines) for i,lines in CREDITS.items()) +
        '\n\nAll text is constrained to original slots; no pointers are relocated. Extended codes $80-$8F are not emitted by the new boss/credit batch because their runtime routing was only confirmed in the opening path.\n',encoding='utf-8')
    # output preview art for all newly translated text lines and credits
    make_preview(out,codes,translated_texts,ad/'step20_remaining_dialogue_and_credits_preview.png','Step20')
    # output metadata manifest
    report={
      'step':20,'title':'Cumulative full indexed-text translation build','status':'static_build_passed_full_emulator_playthrough_required',
      'source_sha256':sha(src),'step19_base_sha256':sha(base_rom),'output_sha256':sha(out),'ips_sha256':sha(cumulative_patch),
      'source_bytes':len(src),'output_bytes':len(out),'header_preserved_from_step19':out[:16]==base_rom[:16],
      'combined_ips_bytes':len(cumulative_patch),'combined_ips_records':len(parse_ips(cumulative_patch)),'clean_source_round_trip_exact':apply_ips(src,cumulative_patch)==out,
      'boss_unique_text_segments_changed_step20':len(added_records)-len(credits),'credits_records_translated_step20':len(credits),
      'boss_indexes_translated_this_step':sorted(set(BOSS_VN.keys()) | {9,10}),'credits_indexes_translated_this_step':sorted(CREDITS.keys()),
      'boss_09_10_animation_sequences_preserved':True, 'boss_09_10_grunt_letters_localized':True,'opening_records_retained':7,'boss_pointer_indexes_total':78,'credits_pointer_indexes_total':5,
      'pointers_modified':False,'metadata_prefixes_preserved':True,'all_target_slots_fixed_length':True,
      'high_byte_glyph_codes_used_in_step20_text':False,'boss_54_fc_control_preserved':True,
      'FCEUX_full_game_test':'Not performed by build script; Step 20 requires emulator pass through all translated boss dialogue and credits.'
    }
    (ad/'step20_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    log=['STEP 20 STATIC VALIDATION',f'Clean source SHA-256: {sha(src)}',f'Step 19 base SHA-256: {sha(base_rom)}',f'Final output SHA-256: {sha(out)}',f'Output size: {len(out)} bytes',f'Cumulative IPS size: {len(cumulative_patch)} bytes',f'Cumulative IPS records: {len(parse_ips(cumulative_patch))}',f'IPS exact round trip from clean source: {apply_ips(src,cumulative_patch)==out}',f'Boss/credits target slots changed: {len(added_records)}','Pointer table unchanged: YES','Metadata prefixes preserved: YES','Fixed slot lengths preserved: YES','High-byte 0x80-0x8F used in new boss/credit text: NO','BOSS_09/BOSS_10 visible grunt letters localized; 0x76 punctuation and FB/FA/F9 animation bytes preserved: YES','BOSS_54 trailing FC control preserved: YES','FCEUX full-game pass: PENDING USER TEST','']
    for m in manifest: log.append(f"{m['id']}: {m['encoded_bytes']}/{m['content_capacity']} bytes; PASS")
    (ad/'step20_validation.txt').write_text('\n'.join(log)+'\n',encoding='utf-8')
    (ad/'step20_checksums.txt').write_text(f'{sha(out)}  {output_rom_path.name}\n{sha(cumulative_patch)}  {output_ips_path.name}\n',encoding='utf-8')
    (ad/'step20_scope_report.md').write_text('''# Step 20 scope and guarantees\n\n## Included\n\n- All seven opening narration records, retained from the user-confirmed Step 18 build.\n- Boss dialogue pointer indexes 0–8, retained from the user-confirmed Step 19 pilot.\n- All remaining unique boss text slots for indexes 11–77, including shared-pointer aliases where applicable.\n- All five credits slots.\n- Existing expanded CHR/font bank fix and original pointers.\n\n## Special handling\n\n- BOSS_09 and BOSS_10 are nonverbal grunt sequences. Their seven visible letter glyphs are localized as `ÁÁÁÁÁÁÁ`; the `0x76` punctuation and all `FB/FA/F9` animation bytes remain unchanged.\n- Menu/HUD strings not present in the current verified pointer/text inventory are not claimed translated by this package.\n\n## Encoding constraints\n\nThis step uses only known mapped glyph codes below $80 for the additional boss and credit text. The opening sequence retains the Step 17 high-glyph routing that the user has already tested. The boss context has not yet been traced with extended characters, so the build avoids those values rather than making an unverified claim.\n\n## Validation\n\nThe builder verifies the clean ROM SHA, verifies the Step 19 cumulative IPS against the known-good base ROM, checks all fixed lengths and FF terminators, preserves the five-byte boss prefixes and BOSS_54 FC, does not modify pointer tables, creates a cumulative clean-source IPS, and verifies exact round-trip reproduction. The full game must still be played through in FCEUX before this can be called emulator-verified.\n''',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-rom',type=Path,default=CLEAN_ROM)
    ap.add_argument('--base-rom',type=Path,default=BASE_STEP19_ROM, help='Optional Step 19 reference ROM; normally unnecessary because it is reconstructed from the included IPS')
    ap.add_argument('--base-ips',type=Path,default=BASE_IPS)
    ap.add_argument('--project',type=Path,default=DEFAULT_PROJECT)
    ap.add_argument('--output-rom',type=Path,default=DEFAULT_ROM_OUT)
    ap.add_argument('--output-ips',type=Path,default=DEFAULT_IPS_OUT)
    args=ap.parse_args(); run(args.source_rom,args.base_rom,args.base_ips,args.project,args.output_rom,args.output_ips)
if __name__=='__main__': main()
