#!/usr/bin/env python3
"""Render NES pattern tables from a 8KB/16KB VRAM dump to PNG (with tile index grid)
usage: chrdump.py vram.bin out.png [scale]"""
import sys
from PIL import Image, ImageDraw
v=open(sys.argv[1],'rb').read(); sc=int(sys.argv[3]) if len(sys.argv)>3 else 3
pal=[(0,0,0),(255,255,255),(160,160,160),(80,80,200)]
def tile(t,o):
    px=[]
    for y in range(8):
        a=v[o+t*16+y];b=v[o+t*16+y+8]
        px.append([((a>>(7-x))&1)|(((b>>(7-x))&1)<<1) for x in range(8)])
    return px
im=Image.new('RGB',(2*16*9*sc+10,16*9*sc),(40,0,40))
for pt in range(2):
    for t in range(256):
        px=tile(t,pt*0x1000)
        for y in range(8):
            for x in range(8):
                c=pal[px[y][x]]
                X=pt*(16*9*sc+10)+(t%16)*9*sc+x*sc; Y=(t//16)*9*sc+y*sc
                for dy in range(sc):
                    for dx in range(sc): im.putpixel((X+dx,Y+dy),c)
im.save(sys.argv[2])
