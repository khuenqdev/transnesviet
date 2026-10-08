import sys; sys.path.insert(0,'.')
from jtab import decode
rom=open('/home/claude/w/orig.nes','rb').read()
def b3(a): return rom[16+3*0x4000+a-0x8000]
def w3(a): return b3(a)|b3(a+1)<<8
def rd(a):
    s=[]
    while True:
        c=b3(a)
        if c==0x30 or c in (0xEF,0xEE): s+=[c,b3(a+1)]; a+=2; continue
        s.append(c); a+=1
        if c==0x2F: break
    return s
G=[w3(0x8C1A+2*i) for i in range(7)]
groups={}
for g,ga in enumerate(G):
    ptrs=[]; a=ga; end=0x10000
    while a<end:
        p=w3(a); ptrs.append(p)
        if p>ga: end=min(end,p)
        a+=2
    groups[g]=ptrs
if __name__=='__main__':
    for g in range(7):
        print('=== group',g,hex(G[g]),'entries',len(groups[g]))
        for i,p in enumerate(groups[g]):
            print('%d.%03d %04X %s'%(g,i,p,decode(rd(p))))
