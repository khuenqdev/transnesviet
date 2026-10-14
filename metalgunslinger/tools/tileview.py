#!/usr/bin/env python3
"""GBA tile viewer: render ROM bytes as 4bpp/8bpp/1bpp 8x8 tiles.
usage: tileview.py rom offset ntiles out.png [bpp=4] [cols=32] [scale=2]"""
import sys
from PIL import Image
rom,off,n,out=sys.argv[1],int(sys.argv[2],0),int(sys.argv[3]),sys.argv[4]
bpp=int(sys.argv[5]) if len(sys.argv)>5 else 4
cols=int(sys.argv[6]) if len(sys.argv)>6 else 32
sc=int(sys.argv[7]) if len(sys.argv)>7 else 2
d=open(rom,'rb').read(); ts=8*bpp
rows=(n+cols-1)//cols; img=Image.new('L',(cols*8,rows*8))
px=img.load()
for t in range(n):
    b=d[off+t*ts:off+(t+1)*ts]; tx,ty=(t%cols)*8,(t//cols)*8
    for i in range(64):
        if bpp==4: v=(b[i//2]>>(4*(i&1)))&15; v*=17
        elif bpp==8: v=b[i]
        elif bpp==2: v=((b[i//4]>>(2*(i&3)))&3)*85
        else: v=255 if b[i//8]>>(i&7)&1 else 0
        px[tx+i%8,ty+i//8]=v
img.resize((img.width*sc,img.height*sc),Image.NEAREST).save(out)
