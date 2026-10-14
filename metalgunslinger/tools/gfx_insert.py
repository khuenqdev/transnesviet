#!/usr/bin/env python3
"""Stage 4 – put_lz: recompress raw; write in place if it fits (zero-padded), else append to free
graphics area 0x288000+ and repoint every aligned ROM pointer to the old block."""
import struct, sys
sys.path.insert(0,__file__.rsplit('/',1)[0]); from lz77 import compress
GFX_FREE=[0x288000]; GFX_END=0x3FF000; log=[]
def repoint(d,old,new):
    p=struct.pack('<I',0x08000000+old); q=struct.pack('<I',0x08000000+new); n=0; i=d.find(p)
    while i>=0:
        if i%4==0: d[i:i+4]=q; n+=1
        i=d.find(p,i+4)
    return n
def put_lz(d,old_off,old_len,raw,name=''):
    c=compress(raw)
    if len(c)<=old_len: d[old_off:old_off+old_len]=c+bytes(old_len-len(c)); log.append((name,'%06X'%old_off,'in place',len(c),old_len)); return old_off
    a=GFX_FREE[0]; assert a+len(c)<GFX_END; d[a:a+len(c)]=c; GFX_FREE[0]=(a+len(c)+3)&~3
    n=repoint(d,old_off,a); log.append((name,'%06X'%old_off,'moved->%06X (%d ptrs)'%(a,n),len(c),old_len))
    if n==0: raise RuntimeError('no pointer to %06X'%old_off)
    return a
