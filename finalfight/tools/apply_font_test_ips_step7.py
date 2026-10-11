#!/usr/bin/env python3
"""Apply Step 7 accent-strip diagnostic IPS to matching clean ROM. Not a release patch."""
from pathlib import Path
import argparse,hashlib
EXPECTED_BASE_SHA256='5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
EXPECTED_OUTPUT_SHA256='00e2afb637bbd5d5bbe400b0c53c6a54452c19befe3fc3fd85b7c4766515054f'
def apply(src,p):
    if not p.startswith(b'PATCH'): raise ValueError('bad IPS header')
    out=bytearray(src); i=5
    while p[i:i+3]!=b'EOF':
        off=int.from_bytes(p[i:i+3],'big'); n=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if n: data=p[i:i+n]; i+=n
        else:
            n=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; data=bytes([v])*n
        if off+len(data)>len(out): out.extend(b'\0'*(off+len(data)-len(out)))
        out[off:off+len(data)]=data
    return bytes(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--rom',required=True,type=Path); ap.add_argument('--patch',type=Path,default=Path(__file__).resolve().parents[1]/'analysis'/'Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips'); ap.add_argument('--output',type=Path,default=Path('Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.nes')); a=ap.parse_args()
    base=a.rom.read_bytes(); bh=hashlib.sha256(base).hexdigest()
    if bh!=EXPECTED_BASE_SHA256: raise SystemExit(f'REFUSED: base SHA-256 mismatch: {bh}')
    out=apply(base,a.patch.read_bytes()); oh=hashlib.sha256(out).hexdigest()
    if oh!=EXPECTED_OUTPUT_SHA256: raise SystemExit(f'REFUSED: output SHA-256 mismatch: {oh}')
    a.output.write_bytes(out); print('PASS: base hash verified'); print('PASS: diagnostic output hash verified'); print(f'Wrote {a.output.resolve()}'); print('WARNING: accent-strip diagnostic only, not a translation release.')
if __name__=='__main__': main()
