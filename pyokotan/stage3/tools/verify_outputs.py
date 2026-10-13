#!/usr/bin/env python3
"""Verify package outputs against the analyzed Pyokotan NES ROM."""
from __future__ import annotations
import argparse, json, zlib
from pathlib import Path
from extract_text import load_rom, load_tbl

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path); ap.add_argument('--tbl',type=Path,required=True)
    ap.add_argument('--dump',type=Path,required=True)
    args=ap.parse_args()
    raw,header,prg,chr_rom,mapper,submapper=load_rom(args.rom)
    actual=zlib.crc32(prg+chr_rom)&0xFFFFFFFF
    if actual != 0x4339865C: raise SystemExit(f'ERROR: unexpected PRG+CHR CRC32 {actual:08X}')
    tbl=load_tbl(args.tbl)
    if tbl.get(0x20) != ' ': raise SystemExit('ERROR: .tbl space code 0x20 must map to exactly one space')
    d=json.loads(args.dump.read_text(encoding='utf-8'))
    if d.get('rom_fingerprint',{}).get('crc32_prg_plus_chr') != f'{actual:08X}':
        raise SystemExit('ERROR: text dump fingerprint does not match input ROM')
    checked=0
    for group in ('text_records','metadata_records'):
        for r in d.get(group,[]):
            nbytes=len(r.get('raw_hex','').split())
            if nbytes != r.get('byte_length'):
                raise SystemExit(f'ERROR: raw byte length mismatch for {r.get("id")}')
            if group=='text_records' and len(r.get('original_text','')) != r.get('byte_length'):
                raise SystemExit(f'ERROR: decoded character count mismatch for {r.get("id")}')
            checked+=1
    print(f'OK: ROM fingerprint {actual:08X}; .tbl spaces preserved; {checked} dump records checked; mapper {mapper}.')
if __name__=='__main__':main()
