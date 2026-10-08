import sys,zlib
def make_ips(a,b):
    out=bytearray(b'PATCH'); i=0; n=len(b)
    while i<n:
        if i<len(a) and a[i]==b[i]: i+=1; continue
        j=i
        while j<n and j-i<0xFFFF and (j>=len(a) or a[j]!=b[j] or (j+1<n and (j+1>=len(a) or a[j+1]!=b[j+1]))): j+=1
        if i==0x454F46: i-=1
        out+=i.to_bytes(3,'big')+(j-i).to_bytes(2,'big')+b[i:j]; i=j
    out+=b'EOF'; return bytes(out)
def apply_ips(a,p):
    r=bytearray(a); k=5
    while p[k:k+3]!=b'EOF':
        o=int.from_bytes(p[k:k+3],'big'); s=int.from_bytes(p[k+3:k+5],'big'); k+=5
        if s==0: rl=int.from_bytes(p[k:k+2],'big'); v=p[k+2]; k+=3; data=bytes([v])*rl
        else: data=p[k:k+s]; k+=s
        if len(r)<o+len(data): r+=bytes(o+len(data)-len(r))
        r[o:o+len(data)]=data
    return bytes(r)
if __name__=='__main__':
    a=open(sys.argv[1],'rb').read(); b=open(sys.argv[2],'rb').read()
    p=make_ips(a,b); assert apply_ips(a,p)==b
    open(sys.argv[3],'wb').write(p); print(len(p),'bytes, verified, target CRC32 %08X'%zlib.crc32(b))
