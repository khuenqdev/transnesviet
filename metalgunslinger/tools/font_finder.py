#!/usr/bin/env python3
"""Heuristic search for an SJIS-ordered bitmap font: looks for the start of
SJIS row 0x81 (　、。，．・：；？！) – blank glyph followed by small bottom-aligned
punctuation glyphs – for several glyph sizes / bit depths."""
import sys
d=open(sys.argv[1] if len(sys.argv)>1 else 'metal_gunslinger.gba','rb').read()
N=len(d)
def bottom_heavy(b,rows):
    rb=len(b)//rows
    top=b[:rb*(rows//2)]; bot=b[rb*(rows//2):]
    return any(bot) and not any(top)
cands=[]
for G,rows in [(8,8),(18,12),(24,12),(32,16),(64,16),(72,12),(128,16),(32,8)]:
    zero=bytes(G)
    i=d.find(zero)
    cnt=0
    while 0<=i<N-G*8:
        if all(d[i+G*k:i+G*(k+1)]!=zero for k in (1,2,3,4)) and \
           all(bottom_heavy(d[i+G*k:i+G*(k+1)],rows) for k in (1,2,3,4)) and \
           any(d[i+G*5:i+G*6]) and any(d[i+G*9:i+G*10]):
            cands.append((G,hex(i))); cnt+=1
            if cnt>5: break
        i=d.find(zero,i+1)
print(cands[:40])
