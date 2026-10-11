#!/usr/bin/env python3
"""Validate Step 5 font prototype outputs against the supplied clean ROM."""
from pathlib import Path
import csv, json, hashlib, zlib, sys

root=Path(__file__).resolve().parents[1]
rom_path=Path('/mnt/data/Mighty Final Fight (USA).nes')
rom=rom_path.read_bytes()
assert len(rom)==262160, f'ROM size mismatch: {len(rom)}'
assert zlib.crc32(rom[16:]) & 0xffffffff == 0x3F78037C, 'Source body CRC mismatch'
chrdata=rom[16+131072:]
a=root/'analysis'
with (a/'font_prototype_tiles_step5.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==67, f'expected 67 glyph rows, got {len(rows)}'
assert len({r['glyph'] for r in rows})==67, 'duplicate glyphs'
codes=[int(r['text_byte'],16) for r in rows]
assert len(set(codes))==67, 'duplicate byte codes'
assert 0x35 not in codes, '0x35 is reserved in boss segment/header layout'
assert next(r for r in rows if r['glyph']=='É')['text_byte']=='0x8F', 'É must be remapped to spare code 0x8F'
blob=(a/'font_prototype_tiles_step5.bin').read_bytes()
assert len(blob)==67*16, f'wrong tile blob length: {len(blob)}'
for i,r in enumerate(sorted(rows,key=lambda x:int(x['text_byte'],16))):
    b=bytes.fromhex(r['tile_bytes_hex'])
    assert len(b)==16, f'{r["glyph"]} tile length is not 16'
    assert b==blob[i*16:(i+1)*16], f'packed binary mismatch for {r["glyph"]}'
    assert any(b), f'blank generated glyph {r["glyph"]}'
    code=int(r['text_byte'],16); tid=0x1E00+code
    original=chrdata[tid*16:(tid+1)*16]
    assert len(original)==16 and not any(original), f'source tile 0x{tid:04X} is not blank'
validation=json.loads((a/'font_prototype_validation_step5.json').read_text(encoding='utf-8'))
assert validation['rom_modified'] is False
assert validation['prototype_tile_count']==67
assert validation['reserved_0x35_marker_occurrences']>0
assert validation['candidate_byte_occurrences_in_body_streams']==0, 'allocated codes appear in body streams; inspect audit before proceeding'
print('PASS source ROM identity: size 262160, body CRC32 3F78037C')
print('PASS 67 glyphs and 67 unique byte codes')
print('PASS reserved command byte 0x35 not allocated; É uses 0x8F')
print('PASS every allocated source CHR tile is blank; generated tile binary matches CSV')
print('PASS static raw-record audit has zero allocated-code matches in body streams')
print('PASS original ROM not modified; this validation does not replace emulator testing')
