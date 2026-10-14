#!/usr/bin/env python3
"""Stage 3 – Verify & render story text from a patched ROM.
Follows each op29 operand (scene_base + offset), checks every SJIS code exists
in the ROM font table, decodes pair glyphs back to text via pair_table.json,
compares with story_layout.json, and renders chosen messages as 12x12 glyphs
inside a 240px-wide (GBA screen) box.
usage: preview_story.py rom.gba out.png T0014 T0039 ..."""
import sys, json, struct
from PIL import Image, ImageDraw
rom=open(sys.argv[1],'rb').read(); out=sys.argv[2]; want=sys.argv[3:]
n=struct.unpack_from('<H',rom,0x433AE0)[0]
idx={c:i for i,c in enumerate(struct.unpack_from('<%dH'%n,rom,0x433AE4))}
S={s['id']:s['base'] for s in json.load(open('scenes.json',encoding='utf-8'))}
MSG=json.load(open('messages.json',encoding='utf-8'))
inv={int(v,16):k for k,v in json.load(open('pair_table.json',encoding='utf-8')).items()}
lay=json.load(open('story_layout.json',encoding='utf-8'))
def read(ref,scene):
    a=S[scene]+struct.unpack_from('<I',rom,ref)[0]; q=rom.index(0,a); b=rom[a:q]
    return [b[i]<<8|b[i+1] for i in range(0,len(b),2)]
bad=0; mism=0
for m in MSG:
    for ref,exp in zip(m['refs'],lay[m['mid']]):
        codes=read(ref,m['scene'])
        if any(c not in idx for c in codes): bad+=1
        txt=''.join(inv.get(c,'?') for c in codes).rstrip()
        if txt!=(exp if exp.strip() else '').rstrip(): mism+=1; print('MISMATCH',m['mid'],repr(txt),repr(exp))
print('lines checked',sum(len(m['refs']) for m in MSG),'missing-glyph lines',bad,'text mismatches',mism)
sel=[m for m in MSG if m['mid'] in want]
H=sum(len(m['refs'])*13+22 for m in sel)+4
img=Image.new('RGB',(250,H),(10,10,10)); dr=ImageDraw.Draw(img); y=4
for m in sel:
    dr.text((4,y),m['mid'],fill=(255,200,80)); y+=12
    dr.rectangle((4,y-1,244,y+len(m['refs'])*13+2),fill=(20,40,90),outline=(200,200,220))
    for ref in m['refs']:
        for x,c in enumerate(read(ref,m['scene'])):
            g=rom[0x437132+idx[c]*24:0x437132+idx[c]*24+24]
            for yy in range(12):
                bits=g[2*yy]<<8|g[2*yy+1]
                for xx in range(12):
                    if bits>>(15-xx)&1 and 6+x*12+xx<250: img.putpixel((6+x*12+xx,y+1+yy),(255,255,255))
        y+=13
    y+=10
img.resize((img.width*3,img.height*3),Image.NEAREST).save(out)
