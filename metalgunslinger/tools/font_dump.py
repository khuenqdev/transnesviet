#!/usr/bin/env python3
"""Stage 1 – Dump the game's 12x12 1bpp Shift-JIS font.
Header @0x433ADC (ptr from code @0x002C9C): w=12,h=12, ... count=6951, 24 B/glyph
Code table (u16 LE SJIS, sorted) @0x433AE4, bitmaps @0x437132 (2 B per row, MSB-left).
Outputs: font_sheet.png (all glyphs), font_map.tsv (index, sjis, char, offset, used_in_script)"""
import struct, json, sys
from PIL import Image
ROM=sys.argv[1] if len(sys.argv)>1 else 'metal_gunslinger.gba'
d=open(ROM,'rb').read()
CODES,COUNT,GLY,GS=0x433AE4,struct.unpack_from('<H',d,0x433AE0)[0],0x437132,24
codes=struct.unpack_from('<%dH'%COUNT,d,CODES)
used=set()
try:
    for s in json.load(open('scenes.json',encoding='utf-8')):
        for x in s['strings']: used|=set(x['text'])
    for m in json.load(open('menu.json',encoding='utf-8')): used|=set(m['text'])
except FileNotFoundError: pass
cols=64; rows=(COUNT+cols-1)//cols
img=Image.new('L',(cols*13,rows*13),40); px=img.load()
with open('font_map.tsv','w',encoding='utf-8') as f:
    f.write('index\tsjis\tchar\tglyph_offset\tused_in_text\n')
    for i,c in enumerate(codes):
        try: ch=struct.pack('>H',c).decode('cp932')
        except: ch='?'
        f.write(f'{i}\t{c:04X}\t{ch}\t0x{GLY+i*GS:06X}\t{int(ch in used)}\n')
        g=d[GLY+i*GS:GLY+(i+1)*GS]
        for y in range(12):
            r=g[2*y]<<8|g[2*y+1]
            for x in range(12):
                px[(i%cols)*13+x,(i//cols)*13+y]=255 if r>>(15-x)&1 else (0 if ch in used else 20)
img.save('font_sheet.png')
print('glyphs',COUNT,'used by script',sum(1 for c in codes if struct.pack(">H",c).decode("cp932","replace") in used),'free slots',COUNT-len(used))
