#!/usr/bin/env python3
"""Print ROM metadata and generate a CHR tile atlas for a NES 2.0 image."""
from __future__ import annotations
import argparse, hashlib, zlib
from pathlib import Path
from PIL import Image, ImageDraw
HEADER=16

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('rom',type=Path)
 ap.add_argument('--out-dir',type=Path,default=Path('analysis_output'))
 args=ap.parse_args()
 raw=args.rom.read_bytes()
 if len(raw)<16 or raw[:4]!=b'NES\x1a': raise SystemExit('Not an iNES/NES 2.0 ROM.')
 h=raw[:16]
 if (h[7]&0x0c)!=0x08: raise SystemExit('This script expects a NES 2.0 header.')
 ps=(h[4]|((h[9]&0x0f)<<8))*0x4000
 cs=(h[5]|(((h[9]>>4)&0x0f)<<8))*0x2000
 if 16+ps+cs>len(raw): raise SystemExit('Declared sizes exceed file size.')
 prg=raw[16:16+ps]; chrrom=raw[16+ps:16+ps+cs]
 mapper=(h[6]>>4)|(h[7]&0xf0)|((h[8]&0x0f)<<8)
 args.out_dir.mkdir(parents=True,exist_ok=True)
 print(f'ROM file: {args.rom}')
 print(f'Size: {len(raw)} bytes; PRG: {ps} bytes ({ps//0x2000} x 8 KiB); CHR: {cs} bytes ({cs//0x2000} x 8 KiB)')
 print(f'Format: NES 2.0; mapper {mapper}; mirroring flag: {"vertical" if h[6]&1 else "horizontal"} (mapper may control actual mirroring)')
 print(f'CRC32 full: {zlib.crc32(raw)&0xffffffff:08X}; PRG+CHR: {zlib.crc32(prg+chrrom)&0xffffffff:08X}; SHA1: {hashlib.sha1(raw).hexdigest()}')
 vec_off=len(prg)-6
 print('NMI / RESET / IRQ vectors:', ', '.join(f'${int.from_bytes(prg[vec_off+i:vec_off+i+2],"little"):04X}' for i in (0,2,4)))
 # First 256 tiles from CHR bank 0: two-bitplane NES tile graphics.
 n=min(256,len(chrrom)//16); cols=16; scale=5; label_h=14; cell=8*scale+label_h; rows=(n+cols-1)//cols
 im=Image.new('RGB',(cols*cell,rows*cell),(245,245,245)); draw=ImageDraw.Draw(im)
 for idx in range(n):
  x=(idx%cols)*cell; y=(idx//cols)*cell
  tile=chrrom[idx*16:(idx+1)*16]
  for py in range(8):
   lo,hi=tile[py],tile[py+8]
   for px in range(8):
    bit=7-px; value=((lo>>bit)&1)|(((hi>>bit)&1)<<1); shade=[255,170,85,0][value]
    im.paste((shade,shade,shade),(x+px*scale,y+py*scale,x+(px+1)*scale,y+(py+1)*scale))
  draw.text((x+2,y+8*scale),f'{idx:02X}',fill=(0,0,0))
 atlas=args.out_dir/'chr_bank0_ascii_extended_atlas.png'; im.save(atlas)
 print(f'Wrote CHR atlas: {atlas}')
if __name__=='__main__': main()
