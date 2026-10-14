#!/usr/bin/env python3
"""Stage 3 – Group op29 text lines into on-screen messages.
A message = run of consecutive `29 <off>` instructions, terminated by 0x2A
(dialogue box: show & wait) or 0x69 (intro/credit line display).
Output messages.json: [{mid, scene, end_op, refs:[ref_addr...], jp:[line...]}]"""
import json,struct
d=open('metal_gunslinger.gba','rb').read()
S=json.load(open('scenes.json',encoding='utf-8'))
u32=lambda o:struct.unpack_from('<I',d,o)[0]
msgs=[]
for s in S:
    ref2txt={r:x['text'] for x in s['strings'] for r in x['refs']}
    cur=[]
    for r in sorted(ref2txt):
        cur.append(r)
        if r+8 not in ref2txt:
            msgs.append(dict(mid='T%04d'%len(msgs),scene=s['id'],end_op=u32(r+4),refs=cur,jp=[ref2txt[x] for x in cur])); cur=[]
json.dump(msgs,open('messages.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
with open('messages_jp.txt','w',encoding='utf-8') as f:
    last=None
    for m in msgs:
        if m['scene']!=last: f.write(f"\n## scene {m['scene']}\n"); last=m['scene']
        f.write(m['mid']+('' if m['end_op']==0x2a else '*')+' | '+' / '.join(m['jp'])+'\n')
print(len(msgs),'messages', sum(len(m['refs']) for m in msgs),'line-refs')
