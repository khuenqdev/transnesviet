#!/usr/bin/env python3
"""Stage 2 – Build patched ROM: Vietnamese menu/system text + Vietnamese font.
usage: insert_stage2.py metal_gunslinger.gba menu_vi.tsv out.gba
 - checks each translated line fits the original on-screen width
   (Japanese full-width char = 2 half-width VI chars)
 - encodes with PairCodec, writes strings to free space 0x6BDBB0,
   repoints all absolute pointers, writes pair glyphs into the font."""
import sys, json, csv, struct, unicodedata
sys.path.insert(0,__file__.rsplit('/',1)[0])
from vi_codec import PairCodec
from vi_font import glyph
rom_p,tsv,out=sys.argv[1:4]
rom=open(rom_p,'rb').read(); d=bytearray(rom)
M=json.load(open('menu.json',encoding='utf-8')); S=json.load(open('scenes.json',encoding='utf-8'))
used=set(''.join(x['text'] for s in S for x in s['strings']))|set(''.join(m['text'] for m in M))
vi={r['id']:r['vi'] for r in csv.DictReader(open(tsv,encoding='utf-8'),delimiter='\t')}
codec=PairCodec(rom,used)
def jpw(t): return sum(1 if ord(c)<0x80 else 2 for c in t)
FREE=0x6BDBB0; p=FREE; warn=0
for i,m in enumerate(M):
    k='M%03d'%i
    if k not in vi or not vi[k].strip(): continue
    t=unicodedata.normalize('NFC',vi[k]); lim=max(jpw(l) for l in m['text'].split('\r'))
    jl=m['text'].split('\r'); vl=t.split('<br>')
    if len(vl)!=len(jl): print('WARN line count',k,len(jl),'->',len(vl)); warn+=1
    for l in vl:
        w=len(l)+(len(l)%2)
        if w>lim: print(f'WARN width {k}: {w}>{lim} {l!r}'); warn+=1
    raw=codec.encode(t)
    d[p:p+len(raw)+1]=raw+b'\0'
    for r in m['refs']: struct.pack_into('<I',d,r,0x08000000+p)
    p=(p+len(raw)+1+3)&~3
codec.write_font(d,glyph); codec.save()
open(out,'wb').write(d)
print(f'strings written: {sum(1 for i in range(len(M)) if "M%03d"%i in vi)}  bytes: {p-FREE}  pairs: {len(codec.table)}  free slots left: {len(codec.pool)}  warnings: {warn}')
