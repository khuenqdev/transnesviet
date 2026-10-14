#!/usr/bin/env python3
"""Stage 1 – System/menu text (0x052E00-0x053A10): Shift-JIS strings referenced
by absolute GBA pointers (0x08xxxxxx). Finds every pointer to each string."""
import struct, json, sys
ROM=sys.argv[1] if len(sys.argv)>1 else 'metal_gunslinger.gba'
d=open(ROM,'rb').read()
LO,HI=0x52E00,0x53A10
out=[]; p=LO
while p<HI:
    if d[p]==0: p+=1; continue
    q=d.find(b'\0',p)
    raw=d[p:q]
    try: t=raw.decode('cp932')
    except: p=q+1; continue
    if any('\u3000'<=c<='\u9fff' or '\uff00'<=c<='\uffef' for c in t):
        pk=struct.pack('<I',0x08000000+p); refs=[]; i=d.find(pk)
        while i>=0:
            if i%4==0: refs.append(i)
            i=d.find(pk,i+1)
        out.append(dict(addr=p,len=len(raw),text=t,refs=refs))
    p=q+1
json.dump(out,open('menu.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(out),'strings; without pointer:',[ (hex(x['addr']),x['text']) for x in out if not x['refs']])
