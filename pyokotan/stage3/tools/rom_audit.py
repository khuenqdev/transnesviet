#!/usr/bin/env python3
"""Print a reproducible fingerprint and bank-layout summary for the ROM."""
from pathlib import Path
import argparse, hashlib, json, zlib


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('rom',type=Path); ap.add_argument('--out',type=Path)
    a=ap.parse_args(); raw=a.rom.read_bytes()
    if len(raw)<16 or raw[:4]!=b'NES\x1a': raise SystemExit('ERROR: missing iNES header')
    h=raw[:16]
    if (h[7]&0x0C)!=0x08: raise SystemExit('ERROR: not a NES 2.0 header')
    pm,cm=h[9]&0x0F,(h[9]>>4)&0x0F
    if pm==0x0F or cm==0x0F: raise SystemExit('ERROR: NES 2.0 exponent sizing is not implemented')
    ps=(h[4]|(pm<<8))*0x4000; cs=(h[5]|(cm<<8))*0x2000
    prg=raw[16:16+ps]; chrrom=raw[16+ps:16+ps+cs]
    mapper=(h[6]>>4)|(h[7]&0xF0)|((h[8]&0x0F)<<8)
    v=prg[-6:]
    out={"filename":a.rom.name,"file_size":len(raw),"header_hex":h.hex(' ').upper(),"format":"NES 2.0",
         "mapper":mapper,"submapper":h[8]>>4,"prg_bytes":len(prg),"prg_8k_banks":len(prg)//0x2000,
         "chr_bytes":len(chrrom),"chr_8k_banks":len(chrrom)//0x2000,
         "crc32_file":f'{zlib.crc32(raw)&0xffffffff:08X}',
         "crc32_prg_chr":f'{zlib.crc32(prg+chrrom)&0xffffffff:08X}',
         "crc32_prg":f'{zlib.crc32(prg)&0xffffffff:08X}',"crc32_chr":f'{zlib.crc32(chrrom)&0xffffffff:08X}',
         "sha1":hashlib.sha1(raw).hexdigest(),
         "vectors":{"nmi":f'0x{int.from_bytes(v[:2],"little"):04X}',"reset":f'0x{int.from_bytes(v[2:4],"little"):04X}',
                    "irq_brk":f'0x{int.from_bytes(v[4:],"little"):04X}',"bytes_hex":v.hex(' ').upper()}}
    rendered=json.dumps(out,indent=2)
    if a.out: a.out.write_text(rendered+'\n',encoding='utf-8')
    print(rendered)
if __name__=='__main__': main()
