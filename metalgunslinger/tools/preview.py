#!/usr/bin/env python3
"""Stage 2 – Render text exactly as stored in a (patched) ROM: follows each menu
pointer, decodes SJIS codes, looks glyphs up in the ROM's own font table and
draws them 12x12 (as the game does). usage: preview.py rom.gba out.png"""
import sys, json, struct
from PIL import Image, ImageDraw
rom=open(sys.argv[1],'rb').read()
CODES,GLY=0x433AE4,0x437132
n=struct.unpack_from('<H',rom,0x433AE0)[0]
idx={c:i for i,c in enumerate(struct.unpack_from('<%dH'%n,rom,CODES))}
M=json.load(open('menu.json',encoding='utf-8'))
W=40*12; lines=[]
for i,m in enumerate(M):
    a=struct.unpack_from('<I',rom,m['refs'][0])[0]-0x08000000
    q=rom.index(0,a); b=rom[a:q]; rows=[[]]; j=0
    while j<len(b):
        if b[j]==0x0D: rows.append([]); j+=1
        elif b[j]>=0x80: rows[-1].append(b[j]<<8|b[j+1]); j+=2
        else: j+=1
    lines.append(('M%03d'%i,rows))
H=sum(len(r)*13+6 for _,r in lines)
img=Image.new('RGB',(W+60,H),(16,24,48)); dr=ImageDraw.Draw(img); y=0
for k,rows in lines:
    dr.text((2,y+2),k,fill=(120,140,180))
    for r in rows:
        for x,c in enumerate(r):
            g=idx.get(c); 
            if g is None: continue
            gl=rom[GLY+g*24:GLY+g*24+24]
            for yy in range(12):
                bits=gl[2*yy]<<8|gl[2*yy+1]
                for xx in range(12):
                    if bits>>(15-xx)&1: img.putpixel((60+x*12+xx,y+yy),(255,255,255))
        y+=13
    y+=6
img=img.resize((img.width*2,img.height*2),Image.NEAREST); img.save(sys.argv[2]); print(img.size)
