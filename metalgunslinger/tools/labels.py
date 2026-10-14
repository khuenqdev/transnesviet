#!/usr/bin/env python3
"""Stage 4 – speaker name labels (sprite resources).
Layout: [LZ77 4bpp tiles][LZ77 32-byte palette]['ANIM' header ... piece list: u16 n, n x (attr0,attr1,flags,tile)]
Each piece = OAM sprite (shape/size, signed x/y offset, first tile, 1D mapping). Lower index is drawn on top."""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import decompress
from PIL import Image
SIZES={(0,0):(8,8),(0,1):(16,16),(0,2):(32,32),(0,3):(64,64),(1,0):(16,8),(1,1):(32,8),(1,2):(32,16),(1,3):(64,32),(2,0):(8,16),(2,1):(8,32),(2,2):(16,32),(2,3):(32,64)}
LABELS=[0x5D6E78,0x5D82E0,0x5DB258,0x5DECCC,0x5E2CD0,0x5E55A8,0x5E7C38,0x5E87EC,0x5E9E1C,0x5ED1A8,0x5F00AC,0x5F447C,0x5F476C,0x5F4A1C]
def load(d,g):
    raw,gl=decompress(d,g); p=(g+gl+3)&~3; pal,pl=decompress(d,p); L=(p+pl+3)&~3
    assert d[L-4:L]==b'ANIM' or d[L:L+4]==b'ANIM', 'no ANIM'
    A=L if d[L:L+4]==b'ANIM' else L-4
    n=struct.unpack_from('<H',d,A+6)[0]; L=A+8
    while not (struct.unpack_from('<H',d,L)[0]==n and d[L+2]==0xF8 and d[L+3] in (0x00,0x40,0x80)): L+=2
    pieces=[]
    for k in range(n):
        a0,a1,fl,t=struct.unpack_from('<4H',d,L+2+k*8)
        w,h=SIZES[(a0>>14,a1>>14)]; x=a1&0x1FF; x=x-512 if x>=256 else x; y=a0&0xFF; y=y-256 if y>=128 else y
        pieces.append(dict(x=x,y=y,w=w,h=h,tile=t,hflip=bool(a1&0x1000),vflip=bool(a1&0x2000)))
    return dict(gfx=g,gfx_len=gl,pal=p,raw=raw,palette=[struct.unpack_from('<H',pal,i*2)[0] for i in range(16)],pieces=pieces)
def rgb(c): return ((c&31)<<3|(c&31)>>2,((c>>5)&31)<<3|((c>>5)&31)>>2,((c>>10)&31)<<3|((c>>10)&31)>>2)
def _px(p,px,py):
    sx=p['w']-1-px if p['hflip'] else px; sy=p['h']-1-py if p['vflip'] else py
    t=p['tile']+(sy//8)*(p['w']//8)+(sx//8); return t*32+(sy%8)*4+(sx%8)//2, sx&1
def bbox(lab):
    P=lab['pieces']; return min(p['x'] for p in P),min(p['y'] for p in P),max(p['x']+p['w'] for p in P),max(p['y']+p['h'] for p in P)
def to_index_image(lab):
    x0,y0,x1,y1=bbox(lab); img=[[-1]*(x1-x0) for _ in range(y1-y0)]; raw=lab['raw']
    for p in reversed(lab['pieces']):
        for py in range(p['h']):
            for px in range(p['w']):
                o,hi=_px(p,px,py)
                if o>=len(raw): continue
                c=raw[o]>>4 if hi else raw[o]&15; Y,X=p['y']-y0+py,p['x']-x0+px
                if c or img[Y][X]<0: img[Y][X]=c
    return img,(x0,y0)
def from_index_image(lab,img,origin):
    raw=bytearray(lab['raw']); x0,y0=origin; owner={}
    for i,p in enumerate(lab['pieces']):
        for py in range(p['h']):
            for px in range(p['w']): owner.setdefault((p['y']-y0+py,p['x']-x0+px),i)
    for i,p in enumerate(lab['pieces']):
        for py in range(p['h']):
            for px in range(p['w']):
                Y,X=p['y']-y0+py,p['x']-x0+px; c=img[Y][X]
                if c<0: continue
                if owner[(Y,X)]!=i: c=0
                o,hi=_px(p,px,py); raw[o]=(raw[o]&0x0F)|(c<<4) if hi else (raw[o]&0xF0)|c
    return bytes(raw)
def render(lab,img=None,scale=1):
    if img is None: img,_=to_index_image(lab)
    H,W=len(img),len(img[0]); im=Image.new('RGB',(W,H),(255,0,255)); P=[rgb(c) for c in lab['palette']]
    for y in range(H):
        for x in range(W):
            c=img[y][x]
            if c>0: im.putpixel((x,y),P[c])
            elif c==0: im.putpixel((x,y),(40,40,40))
    return im.resize((W*scale,H*scale),Image.NEAREST)
