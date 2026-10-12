#!/usr/bin/env python3
"""Parse the dialog row table of Saiyuuki World (bank 3, ptr table $9E77, 213 rows)."""
import sys, json
sys.path.insert(0,__file__.rsplit('/',1)[0])
from jtable import dec
d=open(sys.argv[1] if len(sys.argv)>1 else '../rom/original.nes','rb').read()[16:]
b3=d[3*0x4000:4*0x4000]
w=lambda a:b3[a-0x8000]|b3[a-0x8000+1]<<8
N=213
rows=[]
for i in range(N):
    p=w(0x9E77+2*i); fl=b3[p-0x8000]; ln=b3[p-0x8000+1]; q=p+2; addr=None
    if fl&0x10: addr=w(q); q+=2
    txt=b3[q-0x8000:q-0x8000+ln]
    rows.append(dict(i=i,ptr=p,flags=fl,len=ln,addr=addr,end=q+ln,text=txt))
if __name__=='__main__':
    for r in rows:
        nxt=rows[r['i']+1]['ptr'] if r['i']+1<N else None
        print('%3d $%04X f=%02X len=%2d %s%s | %s'%(r['i'],r['ptr'],r['flags'],r['len'],('addr=%04X '%r['addr']) if r['addr'] else '          ',' ' if nxt in (None,r['end']) else '!GAP', dec(r['text'])))
