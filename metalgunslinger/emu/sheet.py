#!/usr/bin/env python3
"""contact sheet: sheet.py out.png cols img1.ppm ... (labels = filenames)"""
import sys
from PIL import Image, ImageDraw
out,cols=sys.argv[1],int(sys.argv[2]); fs=sys.argv[3:]
ims=[Image.open(f).convert('RGB') for f in fs]; rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*244,rows*174),(40,40,40)); d=ImageDraw.Draw(S)
for i,(f,im) in enumerate(zip(fs,ims)):
    x,y=(i%cols)*244,(i//cols)*174; S.paste(im,(x+2,y+12)); d.text((x+2,y),f.split('/')[-1],fill=(255,255,0))
S.resize((S.width*3//2,S.height*3//2),Image.NEAREST).save(out)
