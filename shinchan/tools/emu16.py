# Mapper 16 (Bandai FCG/LZ93D50) extension of the supplied nes.py core
import numpy as np
from nes import NES, NESPAL
class NES16(NES):
    def __init__(self, rom):
        hdr=rom[:16]
        pu=hdr[4]|((hdr[9]&0x0F)<<8); cu=hdr[5]|((hdr[9]&0xF0)<<4)
        self.prg_size=pu*0x4000; self.nprg=pu
        self.prg=bytearray(rom[16:16+self.prg_size]); self.chr=bytearray(rom[16+self.prg_size:16+self.prg_size+cu*0x2000])
        self.prgbank=0; self.chrreg=[0]*8; self.mirr=1
        self.ram=bytearray(0x800); self.vram=bytearray(0x800); self.pal=bytearray(32); self.oam=bytearray(256)
        self.ctrl=self.mask=self.status=self.oamaddr=0
        self.w=self.v=self.t=self.fx=self.rbuf=0; self.scroll_x=self.scroll_y=0
        self.pad=[0,0]; self.padshift=[0,0]; self.strobe=0
        self.nmi_pending=False; self.cycles=0
        self.a=self.x=self.y=0; self.sp=0xFD; self.p=0x24; self.mirror_h=True
        self.writes_log=None; self.frame_bgpt=1; self.frame_sppt=0; self.wram=bytearray(0x2000)
        self.pc=self.rd16(0xFFFC)
    def nt_index(self,addr):
        addr=(addr-0x2000)&0xFFF; table=addr//0x400; off=addr&0x3FF; m=self.mirr
        phys = table&1 if m==0 else (table>>1)&1 if m==1 else 0 if m==2 else 1
        return phys*0x400+off
    def chr_addr(self,addr): return (self.chrreg[addr>>10]*0x400+(addr&0x3FF))%len(self.chr)
    def ppu_read(self,addr):
        addr&=0x3FFF
        if addr<0x2000: return self.chr[self.chr_addr(addr)]
        if addr<0x3F00: return self.vram[self.nt_index(addr)]
        return self.pal[self.pal_idx(addr)]
    def rd(self,a):
        if a>=0xC000: return self.prg[(self.nprg-1)*0x4000+a-0xC000]
        if a>=0x8000: return self.prg[(self.prgbank%self.nprg)*0x4000+a-0x8000]
        if a>=0x6000: return self.wram[a-0x6000]
        return NES.rd(self,a)
    def wr(self,a,v):
        if a>=0x8000:
            r=a&0x0F
            if r<8: self.chrreg[r]=v
            elif r==8: self.prgbank=v&0x0F
            elif r==9: self.mirr=v&3
            return
        if a>=0x6000: self.wram[a-0x6000]=v; return
        NES.wr(self,a,v)
    def tile_pixels(self,pt,tile):
        a0=self.chr_addr(pt*0x1000+tile*16); lo=self.chr[a0:a0+8]; hi=self.chr[a0+8:a0+16]
        out=np.zeros((8,8),np.uint8)
        for r in range(8):
            for c in range(8): out[r,c]=((lo[r]>>(7-c))&1)|(((hi[r]>>(7-c))&1)<<1)
        return out
    def render(self):
        pt=1 if self.ctrl&0x10 else 0; img=np.zeros((240,256,3),np.uint8); cache={}
        base=0x2000+(self.ctrl&3)*0x400
        for ty in range(30):
            for tx in range(32):
                t=self.ppu_read(base+ty*32+tx); at=self.ppu_read(base+0x3C0+(ty//4)*8+tx//4)
                pn=(at>>(((ty%4)//2)*4+((tx%4)//2)*2))&3
                if t not in cache: cache[t]=self.tile_pixels(pt,t)
                cols=np.array([NESPAL[self.pal[0]&0x3F]]+[NESPAL[self.pal[pn*4+i]&0x3F] for i in (1,2,3)],np.uint8)
                img[ty*8:ty*8+8,tx*8:tx*8+8]=cols[cache[t]]
        return img
