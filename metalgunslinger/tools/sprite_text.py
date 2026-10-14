#!/usr/bin/env python3
"""Stage 5 – repaint Japanese text inside ANIM sprite frames with Latin/Vietnamese caps,
preserving the original style.
 1. compose the frame (index colours), find text 'core' pixels (luminance >= LUM) inside an x-range
 2. erase: pixels within radius E of the core are refilled from the row's background colours
    (sampled outside the text, same palette); mostly-transparent rows are cleared to 0
 3. new text: bold 5x7 caps + Vietnamese marks; outline/glow colours copied from the original
    by distance to the old core (1..R px); fill shaded from the original core colours
 4. write back into tiles; a tile pixel receiving two different values -> error (shared tile)"""
import sys,struct,random,unicodedata
sys.path.insert(0,__file__.rsplit('/',1)[0]); import anim
from collections import Counter
CAP={'A':['.###.','#...#','#...#','#####','#...#','#...#','#...#'],'B':['####.','#...#','#...#','####.','#...#','#...#','####.'],
'C':['.###.','#...#','#....','#....','#....','#...#','.###.'],'D':['####.','#...#','#...#','#...#','#...#','#...#','####.'],
'E':['#####','#....','#....','####.','#....','#....','#####'],'G':['.###.','#...#','#....','#.###','#...#','#...#','.###.'],
'H':['#...#','#...#','#...#','#####','#...#','#...#','#...#'],'I':['###','.#.','.#.','.#.','.#.','.#.','###'],
'K':['#...#','#..#.','#.#..','##...','#.#..','#..#.','#...#'],'L':['#....','#....','#....','#....','#....','#....','#####'],
'M':['#...#','##.##','#.#.#','#.#.#','#...#','#...#','#...#'],'N':['#...#','##..#','#.#.#','#.#.#','#..##','#...#','#...#'],
'O':['.###.','#...#','#...#','#...#','#...#','#...#','.###.'],'P':['####.','#...#','#...#','####.','#....','#....','#....'],
'R':['####.','#...#','#...#','####.','#.#..','#..#.','#...#'],'S':['.####','#....','#....','.###.','....#','....#','####.'],
'T':['#####','..#..','..#..','..#..','..#..','..#..','..#..'],'U':['#...#','#...#','#...#','#...#','#...#','#...#','.###.'],
'V':['#...#','#...#','#...#','.#.#.','.#.#.','..#..','..#..'],'W':['#...#','#...#','#...#','#.#.#','#.#.#','##.##','#...#'],
'X':['#...#','#...#','.#.#.','..#..','.#.#.','#...#','#...#'],'Y':['#...#','#...#','.#.#.','..#..','..#..','..#..','..#..'],
'F':['#####','#....','#....','####.','#....','#....','#....'],'0':['.###.','#...#','#..##','#.#.#','##..#','#...#','.###.'],
'2':['.###.','#...#','....#','..##.','.#...','#....','#####'],' ':['...']*7,'-':['....','....','....','####','....','....','....'],
'.':['.','.','.','.','.','.','#'],'©':['.###.','#...#','#.#.#','##..#','#.#.#','#...#','.###.']}
TONE={'\u0301':['..#','.#.'],'\u0300':['#..','.#.'],'\u0309':['.##','..#','.#.'],'\u0303':['.#.#','#.#.']}
def glyph(ch):
    """-> set of (x,y) for one char; cap rows y=0..6, marks at y<0, dot below at y=8; and width"""
    if ch=='Đ': base=CAP['D']; pts={(x,y) for y,r in enumerate(base) for x,c in enumerate(r) if c=='#'}|{(0,3),(-1,3)}; return {(x+1,y) for x,y in pts},6
    dec=unicodedata.normalize('NFD',ch); b=dec[0]; marks=dec[1:]; rows=CAP[b]; w=len(rows[0])
    pts={(x,y) for y,r in enumerate(rows) for x,c in enumerate(r) if c=='#'}
    tone=[m for m in marks if m in TONE]; hat=[m for m in marks if m in '\u0302\u0306']; mid=w//2
    def put(pat,x0,y0):
        for yy,r in enumerate(pat):
            for xx,c in enumerate(r):
                if c=='#': pts.add((x0+xx,y0+yy))
    if '\u031b' in marks: pts|={(w,-1),(w,0)}; w+=1
    if hat:
        put(['.#.','#.#'] if hat[0]=='\u0302' else ['#.#','.#.'],mid-1,-3)
        if tone: put(TONE[tone[0]][-2:],mid+2,-4)
    elif tone:
        t=TONE[tone[0]]; put(t,mid-len(t[0])//2,-1-len(t))
    if '\u0323' in marks: pts.add((mid,8))
    return pts,w
def text_mask(txt,bold=True,gap=1):
    pts=set(); x=0
    for ch in unicodedata.normalize('NFC',txt):
        g,w=glyph(ch)
        if bold and ch!=' ': g=g|{(px+1,py) for px,py in g if py>=0 and py<=6}; w+=1
        pts|={(px+x,py) for px,py in g}; x+=w+gap
    return pts,x-gap
def lum(c): return ((c&31)*3+((c>>5)&31)*6+((c>>10)&31))*8/10*1.0
def repaint(d,res,anims,txt,xr=None,LUM=200,R=1,yoff=0,bold=None,seed=1,pieces=None,sy=1,captop=None,E=None,clear_all=False,noise=0.2):
    E=R if E is None else E
    pl=[p for a,f,p in anim.frames(d,res['anim']) if a==anims[0] and f==0][0]; ps=anim.pieces(d,pl)
    if pieces: ps=ps[:pieces]
    pal=[struct.unpack_from('<H',res['palette'],i*2)[0] for i in range(len(res['palette'])//2)]
    img=anim.compose_idx(res,ps)
    colr=lambda pc: pal[(pc[0]*16+pc[1])%len(pal)]
    core=[k for k,v in img.items() if v[1] and lum(colr(v))>=LUM and (xr is None or xr[0]<=k[0]<xr[1])]
    if not core: raise ValueError('no text core found')
    coreset=set(core)
    cx0=min(k[0] for k in core); cx1=max(k[0] for k in core); cy0=min(k[1] for k in core); cy1=max(k[1] for k in core)
    bx0,bx1,by0,by1=cx0-E,cx1+E,cy0-E,cy1+E
    if xr: bx0,bx1=xr[0],xr[1]-1
    xs=[k[0] for k in img]; fx0,fx1=min(xs),max(xs)
    if xr: fx0,fx1=xr[0],xr[1]-1
    def near_core(x,y,r):
        return any((x+dx,y+dy) in coreset for dx in range(-r,r+1) for dy in range(-r,r+1))
    rnd=random.Random(seed)
    tpal=Counter(img[k][0] for k in core).most_common(1)[0][0]
    pool={}; zeros=Counter()
    for (x,y),v in img.items():
        if not (by0<=y<=by1) or near_core(x,y,E+1): continue
        if (xr and not (fx0-16<=x<=fx1+16)): continue
        if v[1]==0: zeros[y]+=1
        elif v[0]==tpal: pool.setdefault(y,[]).append(v[1])
    for y in range(by0,by1+1):
        nz=len(pool.get(y,[]))
        if zeros[y]>=4*max(nz,1): pool[y]=[0]
    for y in range(by0,by1+1):
        if not pool.get(y):
            near=[yy for yy in pool if pool[yy] and pool[yy]!=[0]]
            pool[y]=pool[min(near,key=lambda yy:abs(yy-y))] if near else [0]
    if clear_all:
        bx0,bx1=fx0,fx1; ys_=[k[1] for k in img]; by0,by1=min(ys_),max(ys_)
        for y in range(by0,by1+1): pool.setdefault(y,[0])
    dist={}
    for (x,y),v in img.items():
        if (x,y) in coreset or not v[1]: continue
        for dd in range(1,R+1):
            if near_core(x,y,dd): dist.setdefault(dd,Counter())[v[1]]+=1; break
    ring={k:c.most_common(1)[0][0] for k,c in dist.items()}
    fc=Counter(img[k][1] for k in core); fill=fc.most_common(1)[0][0]
    bright=max(fc,key=lambda c: lum(colr((img[core[0]][0],c))))
    new={}
    for (x,y),v in img.items():
        if not (bx0<=x<=bx1 and by0<=y<=by1): continue
        P=pool[y]; dom=Counter(P).most_common(1)[0][0]
        if dom==0:
            if v[1]: new[(x,y)]=0
        elif (x,y) in coreset or near_core(x,y,E):
            nz=[c for c in P if c] or [dom]; md=Counter(nz).most_common(1)[0][0]
            new[(x,y)]=md if rnd.random()>=noise else rnd.choice(nz)
    for b,g in ((True,1),(False,1),(False,0)) if bold is None else ((bold,1),):
        m,w=text_mask(txt,b,g)
        if w<=fx1-fx0+1-2*R: break
    else: raise ValueError('text too wide: %s (%d > %d)'%(txt,w,fx1-fx0+1-2*R))
    if sy>1:
        m2=set()
        for (x,y) in m:
            if 0<=y<=6:
                for k in range(sy): m2.add((x,y*sy+k))
            elif y>6: m2.add((x,7*sy+(y-7)))
            else: m2.add((x,y))
        m=m2
    capH=7*sy
    ox=(bx0+bx1+1)//2-w//2 if xr else (cx0+cx1+1)//2-w//2
    ox=max(fx0+R,min(ox,fx1-R-w+1))
    oy=(cy0+cy1+1)//2-capH//2+yoff if captop is None else captop
    M={(x+ox,y+oy) for x,y in m}
    for (x,y) in list(img.keys()):
        if (x,y) in M: continue
        for dd in range(1,R+1):
            if any((x+dx,y+dy) in M for dx in range(-dd,dd+1) for dy in range(-dd,dd+1)):
                if dd in ring: new[(x,y)]=ring[dd]
                break
    lost=[p for p in M if p not in img]
    for (x,y) in M:
        if (x,y) in img: new[(x,y)]=bright if 0<=(y-oy)<sy*2 else fill
    return ps,img,new,lost
def write_back(res,ps,img,new):
    """apply new colour indices to tiles following piece layout; conflict -> ValueError"""
    tiles=res['tiles']; touched={}; owner={}
    for i,p in enumerate(ps):
        for py in range(p['h']):
            for px in range(p['w']): owner.setdefault((p['x']+px,p['y']+py),i)
    for i,p in enumerate(ps):
        tw=p['w']//8
        for py in range(p['h']):
            for px in range(p['w']):
                X,Y=p['x']+px,p['y']+py
                if (X,Y) not in new or owner[(X,Y)]!=i: continue
                c=new[(X,Y)]
                sx=p['w']-1-px if p['hflip'] else px; sy=p['h']-1-py if p['vflip'] else py
                o=(p['tile']+(sy//8)*tw+(sx//8))*32+(sy%8)*4+(sx%8)//2; hi=sx&1
                if o in touched and touched[o][hi]!=c and touched[o][hi] is not None: raise ValueError('tile conflict at %d'%o)
                touched.setdefault(o,[None,None])[hi]=c
                tiles[o]=(tiles[o]&0x0F)|(c<<4) if hi else (tiles[o]&0xF0)|c
    return {o//32 for o in touched}
