#!/usr/bin/env python3
"""Stage 4 – redraw speaker name labels with Latin names in the original style:
gold plate rebuilt from original plate texture, white bold caps (shaded) + dark outline.
Keeps the exact sprite piece layout / tile count of every label.
usage: label_maker.py metal_gunslinger.gba preview.png"""
import sys, random
sys.path.insert(0,__file__.rsplit('/',1)[0]); import labels
F5={'A':['.###.','#...#','#...#','#####','#...#','#...#','#...#'],'B':['####.','#...#','#...#','####.','#...#','#...#','####.'],
'C':['.###.','#...#','#....','#....','#....','#...#','.###.'],'D':['####.','#...#','#...#','#...#','#...#','#...#','####.'],
'E':['#####','#....','#....','####.','#....','#....','#####'],'F':['#####','#....','#....','####.','#....','#....','#....'],
'G':['.###.','#...#','#....','#.###','#...#','#...#','.###.'],'H':['#...#','#...#','#...#','#####','#...#','#...#','#...#'],
'I':['###','.#.','.#.','.#.','.#.','.#.','###'],'K':['#...#','#..#.','#.#..','##...','#.#..','#..#.','#...#'],
'L':['#....','#....','#....','#....','#....','#....','#####'],'M':['#...#','##.##','#.#.#','#.#.#','#...#','#...#','#...#'],
'N':['#...#','##..#','#.#.#','#.#.#','#..##','#...#','#...#'],'O':['.###.','#...#','#...#','#...#','#...#','#...#','.###.'],
'P':['####.','#...#','#...#','####.','#....','#....','#....'],'R':['####.','#...#','#...#','####.','#.#..','#..#.','#...#'],
'S':['.####','#....','#....','.###.','....#','....#','####.'],'T':['#####','..#..','..#..','..#..','..#..','..#..','..#..'],
'U':['#...#','#...#','#...#','#...#','#...#','#...#','.###.'],'W':['#...#','#...#','#...#','#.#.#','#.#.#','##.##','#...#'],
'Y':['#...#','#...#','.#.#.','..#..','..#..','..#..','..#..'],'Z':['#####','....#','...#.','..#..','.#...','#....','#####'],
'?':['.###.','#...#','....#','..##.','..#..','.....','..#..'],'-':['...','...','...','###','...','...','...'],' ':['...']*7}
def text_mask(txt,bold=True,gap=1):
    cols=[]
    for i,ch in enumerate(txt):
        gl=F5[ch]; w=len(gl[0]); m=[[gl[y][x]=='#' for x in range(w)] for y in range(7)]
        if bold and ch!=' ': m=[[r[x] or (x>0 and r[x-1]) for x in range(w)]+[r[w-1]] for r in m]; w+=1
        for x in range(w): cols.append([m[y][x] for y in range(7)])
        if i<len(txt)-1: cols+=[[False]*7]*gap
    return cols
def plate_rows(d):
    pool=[[] for _ in range(16)]
    for g in labels.LABELS:
        img,_=labels.to_index_image(labels.load(d,g)); W=len(img[0])
        for y in range(16):
            for x in range(10,W-10):
                if img[y][x] in (3,4,5,6,7,9,10,12): pool[y].append(img[y][x])
    return pool
def make(d,g,txt,pool,seed=1):
    lab=labels.load(d,g); img,origin=labels.to_index_image(lab); H,W=len(img),len(img[0])
    for bold,gap,m in ((True,1,8),(True,1,7),(True,1,6),(False,1,7),(False,1,6),(False,0,6)):
        cols=text_mask(txt,bold,gap); L,R=m,W-m
        if len(cols)+2<=R-L: break
    else: raise ValueError('label text too long: '+txt)
    L0,R0=8,W-8; rnd=random.Random(seed)
    for y in range(1,15):
        for x in range(L0,R0):
            if img[y][x]>=0: img[y][x]=rnd.choice(pool[y]) if pool[y] else 5
    tx=L+((R-L)-len(cols))//2; ty=4; fill=set()
    for i,col in enumerate(cols):
        for y in range(7):
            if col[y]: fill.add((ty+y,tx+i))
    for (y,x) in list(fill):
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                p=(y+dy,x+dx)
                if p not in fill and 0<=p[0]<H and 0<=p[1]<W and img[p[0]][p[1]]>=0: img[p[0]][p[1]]=1
    for (y,x) in fill: img[y][x]=14 if y<ty+4 else (13 if y<ty+6 else 11)
    return lab,img,origin
NAMES={0x5D6E78:'BILLY',0x5D82E0:'MAPIYA',0x5DB258:'MABEL',0x5DECCC:'DOC',0x5E2CD0:'SUN DANCE',0x5E55A8:'HAWK',
       0x5E7C38:'FAY',0x5E87EC:'SAM',0x5E9E1C:'BABAG-GUN',0x5ED1A8:'MYNA MYNA',0x5F00AC:'DALTON',0x5F447C:'ZEED',
       0x5F476C:'???',0x5F4A1C:'PERLA NEGRA'}
if __name__=='__main__':
    from PIL import Image
    d=open(sys.argv[1],'rb').read(); pool=plate_rows(d)
    S=Image.new('RGB',(2*300,7*40),(20,20,20))
    for i,(g,t) in enumerate(NAMES.items()):
        lab,img,o=make(d,g,t,pool,seed=g); x,y=(i%2)*300,(i//2)*40
        S.paste(labels.render(lab),(x+2,y+2)); S.paste(labels.render(lab,img),(x+140,y+2))
    S.resize((S.width*2,S.height*2),Image.NEAREST).save(sys.argv[2])
