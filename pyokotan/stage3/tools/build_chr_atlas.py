#!/usr/bin/env python3
"""Build an indexed 8x8 CHR tile atlas (Pillow required)."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('rom',type=Path); ap.add_argument('--out',type=Path,default=Path('outputs/chr_atlas.png')); ap.add_argument('--first',type=lambda s:int(s,0),default=0); ap.add_argument('--count',type=int,default=256); ap.add_argument('--scale',type=int,default=3); a=ap.parse_args()
    raw=a.rom.read_bytes(); h=raw[:16]
    if raw[:4]!=b'NES\x1a': raise SystemExit('Not an iNES ROM')
    pm,cm=h[9]&15,(h[9]>>4)&15
    if pm==15 or cm==15: raise SystemExit('NES 2.0 exponent-sized layout not supported')
    ps=(h[4]|(pm<<8))*0x4000; cs=(h[5]|(cm<<8))*0x2000; chrrom=raw[16+ps:16+ps+cs]
    # 16 tiles per row, 16 rows for 256 tiles; reserve top label strip in each cell.
    cols=16; cellw=8*a.scale; cellh=8*a.scale+12
    rows=(a.count+cols-1)//cols
    im=Image.new('RGB',(cols*cellw,rows*cellh),'white'); d=ImageDraw.Draw(im)
    font=ImageFont.load_default()
    for i in range(a.count):
        tile_idx=a.first+i; base=tile_idx*16
        if base+16>len(chrrom): break
        for y in range(8):
            p0,p1=chrrom[base+y],chrrom[base+y+8]
            for x in range(8):
                bit=7-x; val=((p0>>bit)&1)|(((p1>>bit)&1)<<1)
                if val:
                    x0=(i%cols)*cellw+x*a.scale; y0=(i//cols)*cellh+12+y*a.scale
                    shade={1:170,2:115,3:65}[val]
                    d.rectangle((x0,y0,x0+a.scale-1,y0+a.scale-1),fill=(shade,shade,shade))
        d.text(((i%cols)*cellw+1,(i//cols)*cellh+1),f'{tile_idx:03X}',fill='black',font=font)
    a.out.parent.mkdir(parents=True,exist_ok=True); im.save(a.out); print(f'Wrote {a.out}')
if __name__=='__main__': main()
