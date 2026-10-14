#!/usr/bin/env python3
"""Stage 1 – Pointer-map validation. Moves EVERY story + menu string to free
space (0x6BDBB0), repoints all op29 operands / absolute pointers, wipes the old
strings with 0x00, then re-parses via the new pointers and checks every line
decodes identically. Output ROM: test_relocated.gba (still Japanese)."""
import json, struct
d=bytearray(open('metal_gunslinger.gba','rb').read())
S=json.load(open('scenes.json',encoding='utf-8')); M=json.load(open('menu.json',encoding='utf-8'))
FREE,FREE_END=0x79AA00,0x800000
p=FREE; moved=[]
def put(raw):
    global p
    a=p; d[a:a+len(raw)+1]=raw+b'\0'; p=(a+len(raw)+1+3)&~3
    assert p<FREE_END; return a
for s in S:
    for x in s['strings']:
        raw=x['text'].encode('cp932'); a=put(raw)
        for r in x['refs']: struct.pack_into('<I',d,r,a-s['base'])
        d[x['addr']:x['addr']+x['len']]=bytes(x['len'])
        moved.append(('S',s['base'],x['refs'],x['text']))
for m in M:
    raw=m['text'].encode('cp932'); a=put(raw)
    for r in m['refs']: struct.pack_into('<I',d,r,0x08000000+a)
    d[m['addr']:m['addr']+m['len']]=bytes(m['len'])
    moved.append(('M',0,m['refs'],m['text']))
ok=0
for kind,base,refs,t in moved:
    for r in refs:
        v=struct.unpack_from('<I',d,r)[0]
        a=base+v if kind=='S' else v-0x08000000
        q=d.index(0,a); assert d[a:q].decode('cp932')==t; ok+=1
open('test_relocated.gba','wb').write(d)
print('verified refs',ok,'strings',len(moved),'free space used',hex(p-FREE))
