#!/usr/bin/env python3
"""Minimal 6502 disassembler for NES ROMs. usage: dis6502.py rom.nes bank start end [--base 0x8000]
bank: PRG bank number (16KB); addresses are CPU addresses. Fixed bank = last bank at $C000."""
import sys
OPS={}
def _a(m,ops):
    for k,v in ops.items(): OPS[v]=(k,m)
_a('imp',dict(BRK=0x00,CLC=0x18,CLD=0xD8,CLI=0x58,CLV=0xB8,DEX=0xCA,DEY=0x88,INX=0xE8,INY=0xC8,NOP=0xEA,PHA=0x48,PHP=0x08,PLA=0x68,PLP=0x28,RTI=0x40,RTS=0x60,SEC=0x38,SED=0xF8,SEI=0x78,TAX=0xAA,TAY=0xA8,TSX=0xBA,TXA=0x8A,TXS=0x9A,TYA=0x98))
_a('acc',dict(ASL=0x0A,LSR=0x4A,ROL=0x2A,ROR=0x6A))
for n,b in dict(ORA=0x01,AND=0x21,EOR=0x41,ADC=0x61,STA=0x81,LDA=0xA1,CMP=0xC1,SBC=0xE1).items():
    OPS[b]=(n,'izx');OPS[b+0x10]=(n,'izy');OPS[b+0x04]=(n,'zp');OPS[b+0x14]=(n,'zpx');OPS[b+0x08]=(n,'imm');OPS[b+0x18]=(n,'aby');OPS[b+0x0C]=(n,'abs');OPS[b+0x1C]=(n,'abx')
del OPS[0x89]
for n,b in dict(ASL=0x06,ROL=0x26,LSR=0x46,ROR=0x66,DEC=0xC6,INC=0xE6).items():
    OPS[b]=(n,'zp');OPS[b+0x10]=(n,'zpx');OPS[b+8]=(n,'abs');OPS[b+0x18]=(n,'abx')
OPS.update({0xA2:('LDX','imm'),0xA6:('LDX','zp'),0xB6:('LDX','zpy'),0xAE:('LDX','abs'),0xBE:('LDX','aby'),
0xA0:('LDY','imm'),0xA4:('LDY','zp'),0xB4:('LDY','zpx'),0xAC:('LDY','abs'),0xBC:('LDY','abx'),
0x86:('STX','zp'),0x96:('STX','zpy'),0x8E:('STX','abs'),0x84:('STY','zp'),0x94:('STY','zpx'),0x8C:('STY','abs'),
0xE0:('CPX','imm'),0xE4:('CPX','zp'),0xEC:('CPX','abs'),0xC0:('CPY','imm'),0xC4:('CPY','zp'),0xCC:('CPY','abs'),
0x24:('BIT','zp'),0x2C:('BIT','abs'),0x4C:('JMP','abs'),0x6C:('JMP','ind'),0x20:('JSR','abs')})
for n,b in dict(BPL=0x10,BMI=0x30,BVC=0x50,BVS=0x70,BCC=0x90,BCS=0xB0,BNE=0xD0,BEQ=0xF0).items(): OPS[b]=(n,'rel')
LEN={'imp':1,'acc':1,'imm':2,'zp':2,'zpx':2,'zpy':2,'izx':2,'izy':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
def dis1(mem,pc,get):
    op=get(pc)
    if op not in OPS: return '.db $%02X'%op,1
    n,m=OPS[op];l=LEN[m];b=[get(pc+i) for i in range(1,l)]
    v=b[0] if l==2 else (b[0]|b[1]<<8 if l==3 else 0)
    f={'imp':'','acc':' A','imm':' #$%02X'%v,'zp':' $%02X'%v,'zpx':' $%02X,X'%v,'zpy':' $%02X,Y'%v,'izx':' ($%02X,X)'%v,'izy':' ($%02X),Y'%v,
       'abs':' $%04X'%v,'abx':' $%04X,X'%v,'aby':' $%04X,Y'%v,'ind':' ($%04X)'%v,'rel':' $%04X'%((pc+2+(v-256 if v>127 else v))&0xffff)}[m]
    return n+f,l
def main():
    rom=open(sys.argv[1],'rb').read()[16:]
    bank=int(sys.argv[2]);s=int(sys.argv[3],16);e=int(sys.argv[4],16)
    nb=len(rom)//0x4000
    def get(a):
        if a>=0xC000: return rom[(nb-1)*0x4000+a-0xC000]
        return rom[bank*0x4000+a-0x8000]
    pc=s
    while pc<e:
        t,l=dis1(rom,pc,get)
        print('%04X  %-12s %s'%(pc,' '.join('%02X'%get(pc+i) for i in range(l)),t));pc+=l
if __name__=='__main__': main()
