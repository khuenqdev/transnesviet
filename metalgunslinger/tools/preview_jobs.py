#!/usr/bin/env python3
"""Stage 5 – before/after preview of all sprite text jobs (applied sequentially, like the build).
usage: preview_jobs.py metal_gunslinger.gba out.png"""
import sys,struct; sys.path.insert(0,__file__.rsplit('/',1)[0]); import anim,sprite_text as st
from stage5_jobs import JOBS
from PIL import Image
d=bytearray(open(sys.argv[1],'rb').read())
R={r['gfx']:r for r in anim.find_resources(d)}
for r in R.values(): r['tiles']=bytearray(r['tiles'])
col=lambda c:((c&31)<<3|(c&31)>>2,((c>>5)&31)<<3,((c>>10)&31)<<3)
rows=[]
for g,an,txt,opt in JOBS:
    r=R[g]; ps,img,new,lost=st.repaint(d,r,an,txt,**opt)
    st.write_back(r,ps,img,new)
    after=dict(img)
    for k,c in new.items(): after[k]=(img[k][0],c)
    pal=[struct.unpack_from('<H',r['palette'],i*2)[0] for i in range(len(r['palette'])//2)]
    xs=[k[0] for k in img]; ys=[k[1] for k in img]; x0,y0=min(xs),min(ys)
    def mk(m):
        im=Image.new('RGB',(max(xs)-x0+1,max(ys)-y0+1),(60,0,60))
        for (x,y),(pb,c) in m.items():
            if c: im.putpixel((x-x0,y-y0),col(pal[(pb*16+c)%len(pal)]))
        return im
    rows.append((mk(img),mk(after)))
W=max(a.width for a,b in rows)*2+20; H=sum(a.height+4 for a,_ in rows)
S=Image.new('RGB',(W,H),(20,20,20)); y=0
for a,b in rows: S.paste(a,(0,y)); S.paste(b,(a.width+10,y)); y+=a.height+4
S.resize((S.width*3,S.height*3),Image.NEAREST).save(sys.argv[2]); print(len(rows),'jobs ok')
