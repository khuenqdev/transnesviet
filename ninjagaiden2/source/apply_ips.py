#!/usr/bin/env python3
from pathlib import Path
import sys

def apply(src, ips, dst):
    b=bytearray(Path(src).read_bytes()); p=Path(ips).read_bytes(); assert p[:5]==b"PATCH"; i=5
    while p[i:i+3]!=b"EOF":
        off=int.from_bytes(p[i:i+3],"big"); i+=3
        ln=int.from_bytes(p[i:i+2],"big"); i+=2
        if ln:
            b[off:off+ln]=p[i:i+ln]; i+=ln
        else:
            rle=int.from_bytes(p[i:i+2],"big"); i+=2; v=p[i]; i+=1; b[off:off+rle]=bytes([v])*rle
    Path(dst).write_bytes(b)

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("usage: apply_ips.py base.nes patch.ips output.nes")
    apply(*sys.argv[1:])
