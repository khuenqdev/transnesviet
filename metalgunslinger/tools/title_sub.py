#!/usr/bin/env python3
"""Stage 6 – replace the katakana subtitle under the title logo (メタルガン・スリンガー)
with 'TIẾNG VIỆT' (title BG1, 8bpp tiles LZ77 @0x5F9DC4, map LZ77 @0x5FC0F0).
Tiles of the subtitle are unique in the map (checked). Text: white fill + black 1-px outline,
3x5 caps with Vietnamese marks drawn into the free pixels above/below."""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import decompress
TILES,MAP=0x5F9DC4,0x5FC0F0
FILL,OUT,SHADE=191,1,133
G={'T':['###','.#.','.#.','.#.','.#.'],'I':['#','#','#','#','#'],'E':['###','#..','##.','#..','###'],
   'N':['#..#','##.#','#.##','#..#','#..#'],'G':['.##','#..','#.#','#.#','.##'],'V':['#.#','#.#','#.#','#.#','.#.'],' ':['..','..','..','..','..']}
def mask(txt,top):
    """-> set of (x,y) relative, width.  caps at rows top..top+4; marks above/below"""
    pts=set(); x=0
    for ch in txt:
        b={'Ế':'E','Ệ':'E'}.get(ch,ch); g=G[b]; w=len(g[0])
        for y,r in enumerate(g):
            for xx,c in enumerate(r):
                if c=='#': pts.add((x+xx,top+y))
        if ch in 'ẾỆ':                       # circumflex
            pts|={(x+1,top-3),(x,top-2),(x+2,top-2)}
        if ch=='Ế': pts|={(x+3,top-4),(x+3,top-5)}   # acute (right of the hat)
        if ch=='Ệ': pts.add((x+1,top+6))      # dot below
        x+=w+1
    return pts,x-1
def apply(d,orig):
    tiles,tlen=decompress(orig,TILES); tiles=bytearray(tiles); mp,_=decompress(orig,MAP)
    M=[struct.unpack_from('<H',mp,i*2)[0] for i in range(len(mp)//2)]
    def cell(x,y): return M[(y//8)*32+x//8]&1023
    def get(x,y): return tiles[cell(x,y)*64+(y%8)*8+x%8]
    def put(x,y,c):
        t=cell(x,y); assert t in range(161,169) or t in range(175,182), (x,y,t)
        tiles[t*64+(y%8)*8+x%8]=c
    from collections import Counter
    cnt=Counter(e&1023 for e in M); assert all(cnt[t]==1 for t in list(range(161,169))+list(range(175,182)))
    X0,X1=168,223                                  # row-11 subtitle tiles 175..181
    for x in range(X0,X1+1):                       # erase katakana (row 11 + last line of row 10)
        for y in range(87,96): put(x,y,0)
    top=89; m,w=mask('TIẾNG VIỆT',top); ox=(X0+X1+1)//2-w//2
    P={(x+ox,y) for x,y in m}
    for (x,y) in P:                                # outline
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                q=(x+dx,y+dy)
                if q not in P and X0<=q[0]<=X1 and 84<=q[1]<=95 and (q[1]>=87 or get(*q)==0): put(*q,OUT)
    for (x,y) in P: put(x,y,FILL if y<top+4 else SHADE)
    import gfx_insert; gfx_insert.log.clear(); gfx_insert.put_lz(d,TILES,tlen,bytes(tiles),'title subtitle')
    return list(gfx_insert.log)
if __name__=='__main__':
    o=open(sys.argv[1],'rb').read(); d=bytearray(o); print(apply(d,o)); open(sys.argv[2],'wb').write(d)
