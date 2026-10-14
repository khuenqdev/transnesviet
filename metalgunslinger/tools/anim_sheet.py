#!/usr/bin/env python3
"""Stage 5 – render frame 0 of every animation of every ANIM sprite resource into review sheets.
usage: anim_sheet.py rom outprefix"""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); import anim
from PIL import Image, ImageDraw
d=open(sys.argv[1],'rb').read(); R=anim.find_resources(d)
col=lambda c:((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
items=[]
for r in R:
    P=[struct.unpack_from('<H',r['palette'],i*2)[0] for i in range(len(r['palette'])//2)]; seen=set()
    for (ai,f,pl) in anim.frames(d,r['anim']):
        if pl in seen or f>0: continue
        seen.add(pl); ps=anim.pieces(d,pl)
        if not ps: continue
        img=anim.compose(r,ps)
        if not img: continue
        xs=[k[0] for k in img]; ys=[k[1] for k in img]; x0,y0=min(xs),min(ys); W,H=max(xs)-x0+1,max(ys)-y0+1
        if W>240 or H>160: continue
        im=Image.new('RGB',(W,H),(60,0,60))
        for (x,y),(pb,c) in img.items():
            i=pb*16+c; im.putpixel((x-x0,y-y0),col(P[i]) if i<len(P) else col(P[c]))
        items.append(('%06X/%d'%(r['gfx'],ai),im))
print(len(R),'resources',len(items),'frames')
x=y=0; rowh=0; W=1000; sheets=[]; S=Image.new('RGB',(W,1300),(20,20,20)); dr=ImageDraw.Draw(S)
for lab,im in items:
    w,h=max(im.width,70),im.height+10
    if x+w>W: x=0; y+=rowh+4; rowh=0
    if y+h>1300: sheets.append(S); S=Image.new('RGB',(W,1300),(20,20,20)); dr=ImageDraw.Draw(S); x=y=0; rowh=0
    dr.text((x,y),lab,fill=(255,255,0)); S.paste(im,(x,y+10)); x+=w+4; rowh=max(rowh,h)
sheets.append(S)
for i,s in enumerate(sheets): s.save('%s_%02d.png'%(sys.argv[2],i))
print(len(sheets),'sheets')
