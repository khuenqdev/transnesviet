import sys
sys.path.insert(0,'.')
from nes import OPS
rom=open('orig.nes','rb').read()
SZ={'imp':1,'acc':1,'imm':2,'zp':2,'zpx':2,'zpy':2,'izx':2,'izy':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
def bankread(bank,addr):
    if addr>=0xC000: return rom[16+7*0x4000+addr-0xC000]
    return rom[16+bank*0x4000+addr-0x8000]
def dis(bank,start,n=40):
    pc=start; lines=[]
    for _ in range(n):
        op=bankread(bank,pc); mode,name,_c=OPS[op]; sz=SZ[mode]
        b=[bankread(bank,pc+i) for i in range(sz)]
        if mode=='imm': a='#$%02X'%b[1]
        elif mode=='zp': a='$%02X'%b[1]
        elif mode=='zpx': a='$%02X,X'%b[1]
        elif mode=='zpy': a='$%02X,Y'%b[1]
        elif mode=='izx': a='($%02X,X)'%b[1]
        elif mode=='izy': a='($%02X),Y'%b[1]
        elif mode=='rel': o=b[1]-256 if b[1]>127 else b[1]; a='$%04X'%(pc+2+o)
        elif mode=='abs': a='$%04X'%(b[1]|b[2]<<8)
        elif mode=='abx': a='$%04X,X'%(b[1]|b[2]<<8)
        elif mode=='aby': a='$%04X,Y'%(b[1]|b[2]<<8)
        elif mode=='ind': a='($%04X)'%(b[1]|b[2]<<8)
        elif mode=='acc': a='A'
        else: a=''
        lines.append('%04X: %-9s %s %s'%(pc,' '.join('%02X'%x for x in b),name,a))
        pc+=sz
    print('\n'.join(lines))
if __name__=='__main__':
    dis(int(sys.argv[1]),int(sys.argv[2],16),int(sys.argv[3]) if len(sys.argv)>3 else 40)
