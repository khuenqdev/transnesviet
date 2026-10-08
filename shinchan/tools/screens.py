import re,sys
sys.path.insert(0,'/home/claude/w')
rom=open('/home/claude/w/orig.nes','rb').read()
CHR=rom[16+0x20000:]
SRCBASE=0x78*0x400
def decomp(src,count):
    d=CHR[SRCBASE:SRCBASE+0x2000]; p=src; marker=d[p]; p+=1; out=[]
    while len(out)<count:
        b=d[p]; p+=1
        if b==marker:
            v=d[p]; n=d[p+1]; p+=2; out+= [v]*n if n else [v]*256
        else: out.append(b)
    return out[:count], p
def find_calls():
    res=[]
    for bank in range(8):
        data=rom[16+bank*0x4000:16+(bank+1)*0x4000]
        base=0x8000 if bank<7 else 0xC000
        for m in re.finditer(rb'\x20\x05\xD9',data):
            seg=data[max(0,m.start()-40):m.start()]; vals={}
            for mm in re.finditer(rb'\xA9(.)\x85(.)',seg,re.S): vals[mm.group(2)[0]]=mm.group(1)[0]
            res.append((bank,base+m.start(),vals))
    return res
