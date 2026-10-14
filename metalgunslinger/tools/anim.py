#!/usr/bin/env python3
"""Stage 5 – generic parser for the game's sprite resources:
  [LZ77 4bpp tiles][LZ77 palette(s)]['ANIM' u16 ? u16 nanim ...]
  anim table @+0x4C: nanim x {u16 w,u16 h,u16 nframes,u16 flags,u32 ptr->frames}
  frame (36 bytes): {u32 ptr->piece list,u16 duration,u16 flags,u32 0,u16 w,u16 h,u32 0,4 x u32 hitbox ptrs}
  piece list: u16 n, n x {u16 attr0, u16 attr1, u16 attr2hi(palette/prio), u16 tile}
Piece rendering follows OAM rules (lower index on top)."""
import sys,struct,re
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import decompress
SIZES={(0,0):(8,8),(0,1):(16,16),(0,2):(32,32),(0,3):(64,64),(1,0):(16,8),(1,1):(32,8),(1,2):(32,16),(1,3):(64,32),(2,0):(8,16),(2,1):(8,32),(2,2):(16,32),(2,3):(32,64)}
u16=lambda d,o: struct.unpack_from('<H',d,o)[0]; u32=lambda d,o: struct.unpack_from('<I',d,o)[0]
def lz_ending_at(d,end,lo,hi,maxback=0x20000):
    """find 4-aligned LZ77 block whose padded end == end and decompressed size in [lo,hi]"""
    for q in range(end-8,max(0,end-maxback),-4):
        if d[q]!=0x10: continue
        sz=d[q+1]|d[q+2]<<8|d[q+3]<<16
        if not lo<=sz<=hi: continue
        try: raw,ln=decompress(d,q)
        except Exception: continue
        if (q+ln+3)&~3==end: return q,ln,raw
    return None
def find_resources(d):
    res=[]
    for m in re.finditer(b'ANIM',d):
        A=m.start()
        if A%4: continue
        pal=lz_ending_at(d,A,32,512,0x400)
        if not pal: continue
        gfx=lz_ending_at(d,pal[0],32,0x10000)
        if not gfx: continue
        res.append(dict(anim=A,gfx=gfx[0],gfx_len=gfx[1],tiles=gfx[2],pal=pal[0],palette=pal[2]))
    return res
def pieces(d,plist):
    n=u16(d,plist); out=[]
    if n==0 or n>64: return out
    for k in range(n):
        a0,a1,a2,t=struct.unpack_from('<4H',d,plist+2+k*8)
        key=(a0>>14,a1>>14)
        if key not in SIZES: return []
        w,h=SIZES[key]; x=a1&0x1FF; x=x-512 if x>=256 else x; y=a0&0xFF; y=y-256 if y>=128 else y
        out.append(dict(x=x,y=y,w=w,h=h,tile=t&0x3FF,pal=(a2>>12)&15,hflip=bool(a1&0x1000),vflip=bool(a1&0x2000),off=plist+2+k*8))
    return out
def frames(d,A):
    nanim=u16(d,A+4); out=[]
    for i in range(nanim):
        e=A+0x4C+i*12; nf=u16(d,e+4); fp=u32(d,e+8)-0x08000000
        if not (0<=fp<len(d)) or nf>64: continue
        for f in range(nf):
            fr=fp+f*36; pl=u32(d,fr)-0x08000000
            if 0<=pl<len(d): out.append((i,f,pl))
    return out
def compose(r,P):
    """-> {(x,y):(pal,c)} of opaque pixels"""
    img={}; tiles=r['tiles']
    for p in reversed(P):
        tw=p['w']//8
        for py in range(p['h']):
            for px in range(p['w']):
                sx=p['w']-1-px if p['hflip'] else px; sy=p['h']-1-py if p['vflip'] else py
                o=(p['tile']+(sy//8)*tw+(sx//8))*32+(sy%8)*4+(sx%8)//2
                if o>=len(tiles): continue
                c=tiles[o]>>4 if sx&1 else tiles[o]&15
                if c: img[(p['x']+px,p['y']+py)]=(p['pal'],c)
    return img
def compose_idx(r,P):
    """like compose but keeps transparent (0) pixels too: {(x,y):(pal,c)}"""
    img={}; tiles=r['tiles']
    for p in reversed(P):
        tw=p['w']//8
        for py in range(p['h']):
            for px in range(p['w']):
                sx=p['w']-1-px if p['hflip'] else px; sy=p['h']-1-py if p['vflip'] else py
                o=(p['tile']+(sy//8)*tw+(sx//8))*32+(sy%8)*4+(sx%8)//2
                if o>=len(tiles): continue
                c=tiles[o]>>4 if sx&1 else tiles[o]&15; k=(p['x']+px,p['y']+py)
                if c or k not in img: img[k]=(p['pal'],c)
    return img
