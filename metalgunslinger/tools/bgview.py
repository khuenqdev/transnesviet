#!/usr/bin/env python3
"""Stage 5 – render an LZ77 BG (tiles + 32x32 map + palette) from ROM.
usage: bgview.py rom tiles_off map_off pal_off out.png [pal_base_index]"""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import decompress
from PIL import Image
def load_bg(d,toff,moff,poff):
    tiles,_=decompress(d,toff); mp,_=decompress(d,moff); pal,_=decompress(d,poff); return tiles,mp,pal
def render(tiles,mp,pal,palbase=0):
    P=[struct.unpack_from('<H',pal,i*2)[0] for i in range(len(pal)//2)]
    col=lambda c:((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
    im=Image.new('RGB',(256,256))
    for i in range(min(1024,len(mp)//2)):
        e=struct.unpack_from('<H',mp,i*2)[0]; t=e&0x3FF; pb=(e>>12)-palbase
        for y in range(8):
            for x in range(8):
                sx=7-x if e&0x400 else x; sy=7-y if e&0x800 else y; o=t*32+sy*4+sx//2
                if o>=len(tiles): continue
                c=(tiles[o]>>4) if sx&1 else tiles[o]&15; idx=pb*16+c
                if c and 0<=idx<len(P): im.putpixel(((i%32)*8+x,(i//32)*8+y),col(P[idx]))
    return im
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read(); a=[int(x,0) for x in sys.argv[2:5]]
    pb=int(sys.argv[6]) if len(sys.argv)>6 else 0
    render(*load_bg(d,*a),pb).resize((512,512),Image.NEAREST).save(sys.argv[5])
