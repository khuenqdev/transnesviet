#!/usr/bin/env python3
"""Stage 5 – BPS patch create/apply (beat format; SourceRead/TargetRead actions, CRC32 checked).
  bps.py create original.gba patched.gba out.bps
  bps.py apply  original.gba patch.bps out.gba"""
import sys, zlib
def enc(n):
    out=bytearray()
    while True:
        x=n&0x7F; n>>=7
        if n==0: out.append(0x80|x); return bytes(out)
        out.append(x); n-=1
def dec(b,p):
    data=0; shift=1
    while True:
        x=b[p]; p+=1; data+=(x&0x7F)*shift
        if x&0x80: return data,p
        shift<<=7; data+=shift
def create(src,tgt,meta=b''):
    assert len(src)==len(tgt)
    out=bytearray(b'BPS1')+enc(len(src))+enc(len(tgt))+enc(len(meta))+meta
    i=0; n=len(tgt)
    while i<n:
        j=i
        while j<n and src[j]==tgt[j]: j+=1
        if j>i: out+=enc(((j-i-1)<<2)|0); i=j; continue
        j=i
        while j<n and (src[j]!=tgt[j] or (j+1<n and src[j+1]!=tgt[j+1])): j+=1
        if j==i: j=i+1
        out+=enc(((j-i-1)<<2)|1)+tgt[i:j]; i=j
    out+=zlib.crc32(src).to_bytes(4,'little')+zlib.crc32(tgt).to_bytes(4,'little')
    out+=zlib.crc32(out).to_bytes(4,'little'); return bytes(out)
def apply(src,patch):
    assert patch[:4]==b'BPS1' and zlib.crc32(patch[:-4])==int.from_bytes(patch[-4:],'little'),'bad patch'
    p=4; ss,p=dec(patch,p); ts,p=dec(patch,p); ms,p=dec(patch,p); p+=ms
    assert len(src)==ss and zlib.crc32(src)==int.from_bytes(patch[-12:-8],'little'),'source ROM does not match'
    out=bytearray(); sro=tro=0; end=len(patch)-12
    while p<end:
        d,p=dec(patch,p); cmd=d&3; ln=(d>>2)+1
        if cmd==0: out+=src[len(out):len(out)+ln]
        elif cmd==1: out+=patch[p:p+ln]; p+=ln
        elif cmd==2:
            o,p=dec(patch,p); sro+=(-1 if o&1 else 1)*(o>>1); out+=src[sro:sro+ln]; sro+=ln
        else:
            o,p=dec(patch,p); tro+=(-1 if o&1 else 1)*(o>>1)
            for _ in range(ln): out.append(out[tro]); tro+=1
    assert len(out)==ts and zlib.crc32(out)==int.from_bytes(patch[-8:-4],'little'),'target CRC mismatch'
    return bytes(out)
if __name__=='__main__':
    c,x,y,z=sys.argv[1:5]; X=open(x,'rb').read(); Y=open(y,'rb').read()
    open(z,'wb').write(create(X,Y,b'Metal Gunslinger - Viet hoa') if c=='create' else apply(X,Y)); print('ok',z)
