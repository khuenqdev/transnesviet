#!/usr/bin/env python3
"""Review sheets: crop the dialogue box area (y=96..160) of every page that shows a box."""
import glob,sys,os
from PIL import Image, ImageDraw
src,out=sys.argv[1],sys.argv[2]; per=int(sys.argv[3]) if len(sys.argv)>3 else 40
keep=[]
for f in sorted(glob.glob(src+'/s*_*.ppm')):
    im=Image.open(f).convert('RGB'); r,g,b=im.getpixel((120,150))
    if b>200 and r<160: keep.append((os.path.basename(f)[:-4],im.crop((0,96,240,160))))
os.makedirs(out,exist_ok=True); n=0
for i in range(0,len(keep),per):
    ch=keep[i:i+per]; rows=(len(ch)+1)//2; S=Image.new('RGB',(2*244,rows*76),(30,30,30)); dr=ImageDraw.Draw(S)
    for k,(nm,im) in enumerate(ch):
        x,y=(k%2)*244,(k//2)*76; dr.text((x+2,y),nm,fill=(255,255,0)); S.paste(im,(x+2,y+11))
    S.save('%s/sheet_%02d.png'%(out,n)); n+=1
print(len(keep),'pages with dialogue box,',n,'sheets')
