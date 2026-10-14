#!/usr/bin/env python3
"""IPS patch create/apply.
  ips.py create original.gba patched.gba out.ips
  ips.py apply  original.gba patch.ips out.gba"""
import sys
def create(a,b):
    assert len(a)==len(b)
    out=bytearray(b'PATCH'); i=0; n=len(a)
    while i<n:
        if a[i]==b[i]: i+=1; continue
        j=i
        while j<n and j-i<0xFFFF and (a[j]!=b[j] or (j+1<n and a[j+1]!=b[j+1] and j+1-i<0xFFFF)): j+=1
        s=i
        if s==0x454F46: s-=1      # avoid the 'EOF' marker offset
        out+=s.to_bytes(3,'big')+(j-s).to_bytes(2,'big')+b[s:j]; i=j
    return bytes(out+b'EOF')
def apply(a,p):
    d=bytearray(a); assert p[:5]==b'PATCH'; i=5
    while p[i:i+3]!=b'EOF':
        o=int.from_bytes(p[i:i+3],'big'); sz=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if sz: d[o:o+sz]=p[i:i+sz]; i+=sz
        else:
            rl=int.from_bytes(p[i:i+2],'big'); d[o:o+rl]=p[i+2:i+3]*rl; i+=3
    return bytes(d)
if __name__=='__main__':
    c,x,y,z=sys.argv[1:5]; X=open(x,'rb').read(); Y=open(y,'rb').read()
    open(z,'wb').write(create(X,Y) if c=='create' else apply(X,Y)); print('ok',z)
