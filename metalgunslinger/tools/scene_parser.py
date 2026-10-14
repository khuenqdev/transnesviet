#!/usr/bin/env python3
"""Stage 1 – Metalgun Slinger story-script (scene) parser.
Scene pointer table @0x780000 (148 x u32 GBA ptr). Each scene:
  +0x00 u32 code start (0x4C), +0x04 u32 rel offset of string pool, ...
  Bytecode = stream of u32 words; opcode 0x29 <u32 rel> pushes a text line
  whose address = scene_base + rel. Strings are Shift-JIS, NUL-terminated,
  padded to 4 bytes.
Outputs scenes.json: per scene, every string + every reference location."""
import struct, json, sys
ROM=sys.argv[1] if len(sys.argv)>1 else 'metal_gunslinger.gba'
d=open(ROM,'rb').read()
TABLE=0x780000
u32=lambda o: struct.unpack_from('<I',d,o)[0]
ptrs=[]
o=TABLE
while True:
    v=u32(o)
    if not (0x08780000<=v<0x087A0000) or (ptrs and o>=ptrs[0]): break
    ptrs.append(v-0x08000000); o+=4
print('scenes:',len(ptrs))
bounds=sorted(set(ptrs))+[0x79A9C4]
scenes=[]
opstat={}
for idx,b in enumerate(ptrs):
    end=bounds[bounds.index(b)+1]
    # pass 1: walk aligned words, record operands of opcode 0x29 (text push)
    refs={}
    for w in range(b+0x4C, end-4, 4):
        if u32(w)==0x29:
            v=u32(w+4); s=b+v
            if b+0x4C<s<end and d[s-1]==0 and s>w+4:
                q=d.find(b'\0',s,end)
                try: t=d[s:q].decode('cp932')
                except: continue
                if q>s and any('\u3000'<=c<='\u9fff' or '\uff00'<=c<='\uffef' for c in t):
                    refs.setdefault(s,[]).append(w+4)
    pool=min(refs) if refs else end
    # keep only refs located in code (before pool)
    refs={s:[r for r in rl if r<pool] for s,rl in refs.items()}
    refs={s:rl for s,rl in refs.items() if rl}
    strs={}
    p=pool
    while p<end:
        q=d.find(b'\0',p,end)
        if q<0: break
        raw=d[p:q]
        if raw:
            try: strs[p]=raw.decode('cp932')
            except: strs[p]=None
        p=q+1
    for s in refs: opstat[s in strs]=opstat.get(s in strs,0)+1
    scenes.append(dict(id=idx,base=b,pool=pool,end=end,
        strings=[dict(addr=s,len=len(d[s:d.find(b'\0',s)]),text=t,refs=refs.get(s,[])) for s,t in strs.items()]))
json.dump(scenes,open('scenes.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('ref target is string start:',opstat)
ns=sum(len(s['strings']) for s in scenes)
unref=[(hex(x['addr']),x['text']) for s in scenes for x in s['strings'] if not x['refs']]
bad=[x for s in scenes for x in s['strings'] if x['text'] is None]
print('strings',ns,'unreferenced',len(unref),'undecodable',len(bad))
print(unref[:15])
