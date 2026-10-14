#!/usr/bin/env python3
"""Stage 5 – repaint small Japanese text on BG tile graphics (pause screen labels / portrait caption).
A rect of the tilemap is composed to pixels, cleared to the per-row background colour and redrawn
with a compact 3x5 caps font (fill colours copied from the old text). Tiles inside the rect must not
be used outside it in any of the given maps (checked)."""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import decompress
from collections import Counter
MINI={'A':['.#.','#.#','###','#.#','#.#'],'B':['##.','#.#','##.','#.#','##.'],'C':['.##','#..','#..','#..','.##'],
'D':['##.','#.#','#.#','#.#','##.'],'E':['###','#..','##.','#..','###'],'I':['###','.#.','.#.','.#.','###'],
'L':['#..','#..','#..','#..','###'],'M':['#...#','##.##','#.#.#','#...#','#...#'],'N':['#..#','##.#','#.##','#..#','#..#'],
'O':['.#.','#.#','#.#','#.#','.#.'],'R':['##.','#.#','##.','#.#','#.#'],'S':['.##','#..','.#.','..#','##.'],
'T':['###','.#.','.#.','.#.','.#.'],'Y':['#.#','#.#','.#.','.#.','.#.'],' ':['..','..','..','..','..']}
def mini_mask(txt,gap=1):
    pts=set(); x=0
    for ch in txt:
        g=MINI[ch]
        for y,r in enumerate(g):
            for xx,c in enumerate(r):
                if c=='#': pts.add((x+xx,y))
        x+=len(g[0])+gap
    return pts,x-gap
def lum(c): return ((c&31)*3+((c>>5)&31)*6+((c>>10)&31))*8/10
class BG:
    def __init__(s,d,toff,moffs,poff):
        s.toff=toff; t,s.tlen=decompress(d,toff); s.tiles=bytearray(t)
        s.maps=[decompress(d,m)[0] for m in moffs]; pal,_=decompress(d,poff)
        s.pal=[struct.unpack_from('<H',pal,i*2)[0] for i in range(len(pal)//2)]
    def entry(s,m,cx,cy): return struct.unpack_from('<H',s.maps[m],(cy*32+cx)*2)[0]
    def get(s,m,x,y):
        e=s.entry(m,x//8,y//8); t=e&0x3FF; sx=x%8; sy=y%8
        if e&0x400: sx=7-sx
        if e&0x800: sy=7-sy
        o=t*32+sy*4+sx//2; b=s.tiles[o]; return (b>>4 if sx&1 else b&15),e>>12,o,sx&1
    def put(s,m,x,y,c):
        _,_,o,hi=s.get(m,x,y); s.tiles[o]=(s.tiles[o]&0x0F)|(c<<4) if hi else (s.tiles[o]&0xF0)|c
    def check_unique(s,m,rect):
        x0,y0,x1,y1=rect; inside=Counter(); outside=Counter()
        for mi,mp in enumerate(s.maps):
            for i in range(len(mp)//2):
                cx,cy=i%32,i//32; t=struct.unpack_from('<H',mp,i*2)[0]&0x3FF
                (inside if (mi==m and x0//8<=cx<=x1//8 and y0//8<=cy<=y1//8) else outside)[t]+=1
        bad=[t for t in inside if outside[t]]
        if bad: raise ValueError('rect tiles used elsewhere: %s'%bad)
    def repaint(s,m,rect,txt,LUM=180,top=None,bgc=None,left=None):
        x0,y0,x1,y1=rect; s.check_unique(m,rect)
        px={(x,y):s.get(m,x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)}
        colr=lambda v: s.pal[(v[1]*16+v[0])%len(s.pal)]
        bright=[v[0] for v in px.values() if v[0] and lum(colr(v))>=LUM]
        if not bright: raise ValueError('no text in rect')
        fc=Counter(bright).most_common(); fill=max(set(bright),key=lambda c: lum(colr((c,px[(x0,y0)][1]))))
        shade=fc[0][0] if fc[0][0]!=fill else (fc[1][0] if len(fc)>1 else fill)
        for y in range(y0,y1+1):
            row=[px[(x,y)][0] for x in range(x0,x1+1) if not px[(x,y)][0] or lum(colr(px[(x,y)]))<100]
            bg=Counter(row).most_common(1)[0][0] if row else 0
            if bgc is not None: bg=bgc
            for x in range(x0,x1+1): s.put(m,x,y,bg)
        msk,w=mini_mask(txt)
        if w>x1-x0+1: raise ValueError('too wide %s %d>%d'%(txt,w,x1-x0+1))
        ox=x0 if left is None else left; oy=(y0 if top is None else top)
        for (x,y) in msk: s.put(m,ox+x,oy+y,fill if y<3 else shade)
        return w
