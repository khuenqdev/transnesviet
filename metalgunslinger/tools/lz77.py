#!/usr/bin/env python3
"""GBA BIOS LZ77 (type 0x10) decompress / compress (VRAM-safe: min disp 2)."""
def decompress(d,off):
    assert d[off]==0x10
    size=d[off+1]|d[off+2]<<8|d[off+3]<<16; out=bytearray(); p=off+4
    while len(out)<size:
        f=d[p]; p+=1
        for i in range(8):
            if len(out)>=size: break
            if f&0x80:
                b1,b2=d[p],d[p+1]; p+=2; n=(b1>>4)+3; disp=((b1&15)<<8|b2)+1
                for _ in range(n): out.append(out[-disp])
            else: out.append(d[p]); p+=1
            f<<=1
    return bytes(out[:size]), p-off
def compress(data):
    out=bytearray([0x10,len(data)&255,(len(data)>>8)&255,(len(data)>>16)&255]); i=0; n=len(data)
    while i<n:
        fp=len(out); out.append(0); flags=0
        for b in range(8):
            if i>=n: break
            best=0;bd=0
            for disp in range(2,min(4096,i)+1):
                l=0
                while l<18 and i+l<n and data[i+l-disp]==data[i+l]: l+=1
                if l>best: best,bd=l,disp
                if best==18: break
            if best>=3: flags|=0x80>>b; v=bd-1; out+=bytes([((best-3)<<4)|(v>>8),v&255]); i+=best
            else: out.append(data[i]); i+=1
        out[fp]=flags
    while len(out)%4: out.append(0)
    return bytes(out)
