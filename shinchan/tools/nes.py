# Minimal NES (NROM) emulator for analysis: 6502 core + simple PPU (nametable/OAM level)
import numpy as np

class NES:
    def __init__(self, rom):
        hdr = rom[:16]
        # NES2.0 exponent form handled by caller: assume PRG size given
        self.prg_size = len(rom) - 16 - 8192
        self.prg = bytearray(rom[16:16 + self.prg_size])
        self.chr = bytearray(rom[16 + self.prg_size:16 + self.prg_size + 8192])
        self.mirror_h = (hdr[6] & 1) == 0
        self.ram = bytearray(0x800)
        self.vram = bytearray(0x800)
        self.pal = bytearray(32)
        self.oam = bytearray(256)
        self.ctrl = 0; self.mask = 0; self.status = 0; self.oamaddr = 0
        self.w = 0; self.v = 0; self.t = 0; self.fx = 0; self.rbuf = 0
        self.scroll_x = 0; self.scroll_y = 0
        self.pad = [0, 0]; self.padshift = [0, 0]; self.strobe = 0
        self.nmi_pending = False
        self.cycles = 0
        self.a = self.x = self.y = 0; self.sp = 0xFD; self.p = 0x24
        self.pc = self.rd16(0xFFFC)
        self.bg_tiles_written = {}   # (pt, tile) usage gathered at frame end
        self.writes_log = None
        self.frame_bgpt = 1; self.frame_sppt = 0

    # ---------------- memory -----------------
    def nt_index(self, addr):
        addr = (addr - 0x2000) & 0xFFF
        table = addr // 0x400
        off = addr & 0x3FF
        if self.mirror_h:
            phys = (table // 2)
        else:
            phys = table & 1
        return phys * 0x400 + off

    def ppu_read(self, addr):
        addr &= 0x3FFF
        if addr < 0x2000: return self.chr[addr]
        if addr < 0x3F00: return self.vram[self.nt_index(addr)]
        return self.pal[self.pal_idx(addr)]

    def pal_idx(self, addr):
        i = addr & 0x1F
        if i in (0x10, 0x14, 0x18, 0x1C): i -= 0x10
        return i

    def ppu_write(self, addr, val):
        addr &= 0x3FFF
        if addr < 0x2000: return
        if addr < 0x3F00:
            self.vram[self.nt_index(addr)] = val
            if self.writes_log is not None: self.writes_log.append((addr, val))
        else:
            self.pal[self.pal_idx(addr)] = val

    def rd(self, a):
        if a < 0x2000: return self.ram[a & 0x7FF]
        if a < 0x4000:
            r = a & 7
            if r == 2:
                v = self.status; self.status &= 0x7F; self.w = 0; return v
            if r == 4: return self.oam[self.oamaddr]
            if r == 7:
                addr = self.v & 0x3FFF
                if addr < 0x3F00:
                    v = self.rbuf; self.rbuf = self.ppu_read(addr)
                else:
                    v = self.ppu_read(addr); self.rbuf = self.ppu_read(addr - 0x1000)
                self.v = (self.v + (32 if self.ctrl & 4 else 1)) & 0x7FFF
                return v
            return 0
        if a < 0x4020:
            if a == 0x4016 or a == 0x4017:
                i = a - 0x4016
                v = self.padshift[i] & 1
                if not self.strobe: self.padshift[i] = (self.padshift[i] >> 1) | 0x80
                return v | 0x40
            return 0
        if a >= 0x8000: return self.prg[(a - 0x8000) % self.prg_size]
        return 0

    def wr(self, a, v):
        if a < 0x2000: self.ram[a & 0x7FF] = v; return
        if a < 0x4000:
            r = a & 7
            if r == 0:
                if (v & 0x80) and not (self.ctrl & 0x80) and (self.status & 0x80): self.nmi_pending = True
                self.ctrl = v; self.t = (self.t & 0xF3FF) | ((v & 3) << 10)
            elif r == 1: self.mask = v
            elif r == 3: self.oamaddr = v
            elif r == 4: self.oam[self.oamaddr] = v; self.oamaddr = (self.oamaddr + 1) & 0xFF
            elif r == 5:
                if self.w == 0: self.scroll_x = v; self.fx = v & 7; self.t = (self.t & 0xFFE0) | (v >> 3)
                else: self.scroll_y = v; self.t = (self.t & 0x8C1F) | ((v & 7) << 12) | ((v >> 3) << 5)
                self.w ^= 1
            elif r == 6:
                if self.w == 0: self.t = (self.t & 0x00FF) | ((v & 0x3F) << 8)
                else: self.t = (self.t & 0xFF00) | v; self.v = self.t
                self.w ^= 1
            elif r == 7:
                self.ppu_write(self.v, v)
                self.v = (self.v + (32 if self.ctrl & 4 else 1)) & 0x7FFF
            return
        if a == 0x4014:
            base = v << 8
            for i in range(256): self.oam[(self.oamaddr + i) & 0xFF] = self.rd(base + i)
            self.cycles += 513
            return
        if a == 0x4016:
            self.strobe = v & 1
            if self.strobe: self.padshift = [self.pad[0], self.pad[1]]
            return

    def rd16(self, a): return self.rd(a) | (self.rd((a + 1) & 0xFFFF) << 8)

    # ---------------- CPU -----------------
    def push(self, v): self.ram[0x100 + self.sp] = v; self.sp = (self.sp - 1) & 0xFF
    def pop(self): self.sp = (self.sp + 1) & 0xFF; return self.ram[0x100 + self.sp]

    def nz(self, v):
        self.p = (self.p & 0x7D) | (v & 0x80) | (0 if v else 2); return v

    def nmi(self):
        self.push(self.pc >> 8); self.push(self.pc & 0xFF); self.push((self.p | 0x20) & 0xEF)
        self.p |= 4; self.pc = self.rd16(0xFFFA); self.cycles += 7

    def adc(self, m):
        c = self.p & 1; r = self.a + m + c
        ov = (~(self.a ^ m) & (self.a ^ r) & 0x80)
        self.p = (self.p & 0x3C) | (1 if r > 0xFF else 0) | (0x40 if ov else 0)
        self.a = self.nz(r & 0xFF)

    def cmp(self, reg, m):
        r = (reg - m) & 0x1FF
        self.p = (self.p & 0x7C) | (1 if reg >= m else 0)
        self.nz(r & 0xFF)

    def step(self):
        pc = self.pc
        op = self.rd(pc)
        mode, name, cyc = OPS[op]
        pc = (pc + 1) & 0xFFFF
        addr = None
        if mode == 'imp' or mode == 'acc':
            pass
        elif mode == 'imm': addr = pc; pc += 1
        elif mode == 'zp': addr = self.rd(pc); pc += 1
        elif mode == 'zpx': addr = (self.rd(pc) + self.x) & 0xFF; pc += 1
        elif mode == 'zpy': addr = (self.rd(pc) + self.y) & 0xFF; pc += 1
        elif mode == 'abs': addr = self.rd16(pc); pc += 2
        elif mode == 'abx': addr = (self.rd16(pc) + self.x) & 0xFFFF; pc += 2
        elif mode == 'aby': addr = (self.rd16(pc) + self.y) & 0xFFFF; pc += 2
        elif mode == 'ind':
            p = self.rd16(pc); pc += 2
            addr = self.rd(p) | (self.rd((p & 0xFF00) | ((p + 1) & 0xFF)) << 8)
        elif mode == 'izx':
            z = (self.rd(pc) + self.x) & 0xFF; pc += 1
            addr = self.ram[z] | (self.ram[(z + 1) & 0xFF] << 8)
        elif mode == 'izy':
            z = self.rd(pc); pc += 1
            addr = ((self.ram[z] | (self.ram[(z + 1) & 0xFF] << 8)) + self.y) & 0xFFFF
        elif mode == 'rel':
            off = self.rd(pc); pc += 1
            addr = (pc + (off - 256 if off > 127 else off)) & 0xFFFF
        else:
            raise Exception('bad mode')
        self.pc = pc & 0xFFFF
        self.cycles += cyc
        n = name
        if n == 'LDA': self.a = self.nz(self.rd(addr))
        elif n == 'LDX': self.x = self.nz(self.rd(addr))
        elif n == 'LDY': self.y = self.nz(self.rd(addr))
        elif n == 'STA': self.wr(addr, self.a)
        elif n == 'STX': self.wr(addr, self.x)
        elif n == 'STY': self.wr(addr, self.y)
        elif n == 'TAX': self.x = self.nz(self.a)
        elif n == 'TAY': self.y = self.nz(self.a)
        elif n == 'TXA': self.a = self.nz(self.x)
        elif n == 'TYA': self.a = self.nz(self.y)
        elif n == 'TSX': self.x = self.nz(self.sp)
        elif n == 'TXS': self.sp = self.x
        elif n == 'INX': self.x = self.nz((self.x + 1) & 0xFF)
        elif n == 'INY': self.y = self.nz((self.y + 1) & 0xFF)
        elif n == 'DEX': self.x = self.nz((self.x - 1) & 0xFF)
        elif n == 'DEY': self.y = self.nz((self.y - 1) & 0xFF)
        elif n == 'INC': v = (self.rd(addr) + 1) & 0xFF; self.wr(addr, v); self.nz(v)
        elif n == 'DEC': v = (self.rd(addr) - 1) & 0xFF; self.wr(addr, v); self.nz(v)
        elif n == 'ADC': self.adc(self.rd(addr))
        elif n == 'SBC': self.adc(self.rd(addr) ^ 0xFF)
        elif n == 'AND': self.a = self.nz(self.a & self.rd(addr))
        elif n == 'ORA': self.a = self.nz(self.a | self.rd(addr))
        elif n == 'EOR': self.a = self.nz(self.a ^ self.rd(addr))
        elif n == 'CMP': self.cmp(self.a, self.rd(addr))
        elif n == 'CPX': self.cmp(self.x, self.rd(addr))
        elif n == 'CPY': self.cmp(self.y, self.rd(addr))
        elif n == 'BIT':
            m = self.rd(addr)
            self.p = (self.p & 0x3D) | (m & 0xC0) | (0 if (self.a & m) else 2)
        elif n in ('ASL', 'LSR', 'ROL', 'ROR'):
            v = self.a if mode == 'acc' else self.rd(addr)
            c = self.p & 1
            if n == 'ASL': nc = v >> 7; v = (v << 1) & 0xFF
            elif n == 'LSR': nc = v & 1; v = v >> 1
            elif n == 'ROL': nc = v >> 7; v = ((v << 1) | c) & 0xFF
            else: nc = v & 1; v = (v >> 1) | (c << 7)
            self.p = (self.p & 0xFE) | nc; self.nz(v)
            if mode == 'acc': self.a = v
            else: self.wr(addr, v)
        elif n == 'JMP': self.pc = addr
        elif n == 'JSR':
            r = (self.pc - 1) & 0xFFFF; self.push(r >> 8); self.push(r & 0xFF); self.pc = addr
        elif n == 'RTS':
            lo = self.pop(); hi = self.pop(); self.pc = ((hi << 8) | lo) + 1 & 0xFFFF
        elif n == 'RTI':
            self.p = (self.pop() & 0xEF) | 0x20; lo = self.pop(); hi = self.pop(); self.pc = (hi << 8) | lo
        elif n == 'PHA': self.push(self.a)
        elif n == 'PHP': self.push(self.p | 0x30)
        elif n == 'PLA': self.a = self.nz(self.pop())
        elif n == 'PLP': self.p = (self.pop() & 0xEF) | 0x20
        elif n == 'BPL': self.br(not (self.p & 0x80), addr)
        elif n == 'BMI': self.br(self.p & 0x80, addr)
        elif n == 'BVC': self.br(not (self.p & 0x40), addr)
        elif n == 'BVS': self.br(self.p & 0x40, addr)
        elif n == 'BCC': self.br(not (self.p & 1), addr)
        elif n == 'BCS': self.br(self.p & 1, addr)
        elif n == 'BNE': self.br(not (self.p & 2), addr)
        elif n == 'BEQ': self.br(self.p & 2, addr)
        elif n == 'CLC': self.p &= 0xFE
        elif n == 'SEC': self.p |= 1
        elif n == 'CLI': self.p &= 0xFB
        elif n == 'SEI': self.p |= 4
        elif n == 'CLD': self.p &= 0xF7
        elif n == 'SED': self.p |= 8
        elif n == 'CLV': self.p &= 0xBF
        elif n == 'NOP': pass
        elif n == 'BRK':
            self.pc = (self.pc + 1) & 0xFFFF
            self.push(self.pc >> 8); self.push(self.pc & 0xFF); self.push(self.p | 0x30)
            self.p |= 4; self.pc = self.rd16(0xFFFE)
        else:
            raise Exception('illegal opcode %02X at %04X' % (op, pc - 1))

    def br(self, cond, addr):
        if cond: self.pc = addr; self.cycles += 1

    # ---------------- frame -----------------
    def run_frame(self, hook=None):
        # vblank start
        self.status |= 0x80
        if self.ctrl & 0x80: self.nmi()
        start = self.cycles
        vbl_end = start + 2273
        snapped = False
        while self.cycles - start < 29781:
            if self.nmi_pending:
                self.nmi_pending = False; self.nmi()
            if self.cycles >= vbl_end and not snapped:
                snapped = True
                self.status &= 0x7F
                self.frame_scroll = (self.scroll_x, self.scroll_y, self.ctrl & 3)
                # snapshot pattern table used for BG at render start
                self.frame_bgpt = 1 if self.ctrl & 0x10 else 0
                self.frame_sppt = 1 if self.ctrl & 0x08 else 0
            if hook: hook(self)
            self.step()
        self.status &= 0x3F

    # ---------------- render -----------------
    NES_PAL = None
    def tile_pixels(self, pt, tile):
        base = pt * 0x1000 + tile * 16
        lo = self.chr[base:base + 8]; hi = self.chr[base + 8:base + 16]
        out = np.zeros((8, 8), np.uint8)
        for r in range(8):
            for c in range(8):
                b = 7 - c
                out[r, c] = ((lo[r] >> b) & 1) | (((hi[r] >> b) & 1) << 1)
        return out

    def render_nt(self, nt_addr, pt=None):
        if pt is None: pt = 1 if self.ctrl & 0x10 else 0
        img = np.zeros((240, 256, 3), np.uint8)
        cache = {}
        for ty in range(30):
            for tx in range(32):
                t = self.ppu_read(nt_addr + ty * 32 + tx)
                at = self.ppu_read(nt_addr + 0x3C0 + (ty // 4) * 8 + tx // 4)
                sh = ((ty % 4) // 2) * 4 + ((tx % 4) // 2) * 2
                palno = (at >> sh) & 3
                if t not in cache: cache[t] = self.tile_pixels(pt, t)
                px = cache[t]
                for r in range(8):
                    for c in range(8):
                        ci = px[r, c]
                        col = self.pal[0] if ci == 0 else self.pal[palno * 4 + ci]
                        img[ty * 8 + r, tx * 8 + c] = NESPAL[col & 0x3F]
        return img

    def render_sprites(self, img, sx=0, sy=0):
        pt = 1 if self.ctrl & 0x08 else 0
        for i in range(63, -1, -1):
            y, t, a, x = self.oam[i * 4:i * 4 + 4]
            if y >= 0xEF: continue
            px = self.tile_pixels(pt, t)
            if a & 0x40: px = px[:, ::-1]
            if a & 0x80: px = px[::-1, :]
            for r in range(8):
                for c in range(8):
                    ci = px[r, c]
                    if ci == 0: continue
                    yy = y + 1 + r; xx = x + c
                    if 0 <= yy < 240 and 0 <= xx < 256:
                        img[yy, xx] = NESPAL[self.pal[16 + (a & 3) * 4 + ci] & 0x3F]
        return img

NESPAL = [(84,84,84),(0,30,116),(8,16,144),(48,0,136),(68,0,100),(92,0,48),(84,4,0),(60,24,0),(32,42,0),(8,58,0),(0,64,0),(0,60,0),(0,50,60),(0,0,0),(0,0,0),(0,0,0),
(152,150,152),(8,76,196),(48,50,236),(92,30,228),(136,20,176),(160,20,100),(152,34,32),(120,60,0),(84,90,0),(40,114,0),(8,124,0),(0,118,40),(0,102,120),(0,0,0),(0,0,0),(0,0,0),
(236,238,236),(76,154,236),(120,124,236),(176,98,236),(228,84,236),(236,88,180),(236,106,100),(212,136,32),(160,170,0),(116,196,0),(76,208,32),(56,204,108),(56,180,204),(60,60,60),(0,0,0),(0,0,0),
(236,238,236),(168,204,236),(188,188,236),(212,178,236),(236,174,236),(236,174,212),(236,180,176),(228,196,144),(204,210,120),(180,222,120),(168,226,144),(152,226,180),(160,214,228),(160,162,160),(0,0,0),(0,0,0)]

# ---------------- opcode table -----------------
OPS = {}
def _d(name, mode, op, cyc): OPS[op] = (mode, name, cyc)
_tbl = """
ADC imm 69 2,ADC zp 65 3,ADC zpx 75 4,ADC abs 6D 4,ADC abx 7D 4,ADC aby 79 4,ADC izx 61 6,ADC izy 71 5,
AND imm 29 2,AND zp 25 3,AND zpx 35 4,AND abs 2D 4,AND abx 3D 4,AND aby 39 4,AND izx 21 6,AND izy 31 5,
ASL acc 0A 2,ASL zp 06 5,ASL zpx 16 6,ASL abs 0E 6,ASL abx 1E 7,
BCC rel 90 2,BCS rel B0 2,BEQ rel F0 2,BMI rel 30 2,BNE rel D0 2,BPL rel 10 2,BVC rel 50 2,BVS rel 70 2,
BIT zp 24 3,BIT abs 2C 4,BRK imp 00 7,
CLC imp 18 2,CLD imp D8 2,CLI imp 58 2,CLV imp B8 2,
CMP imm C9 2,CMP zp C5 3,CMP zpx D5 4,CMP abs CD 4,CMP abx DD 4,CMP aby D9 4,CMP izx C1 6,CMP izy D1 5,
CPX imm E0 2,CPX zp E4 3,CPX abs EC 4,CPY imm C0 2,CPY zp C4 3,CPY abs CC 4,
DEC zp C6 5,DEC zpx D6 6,DEC abs CE 6,DEC abx DE 7,DEX imp CA 2,DEY imp 88 2,
EOR imm 49 2,EOR zp 45 3,EOR zpx 55 4,EOR abs 4D 4,EOR abx 5D 4,EOR aby 59 4,EOR izx 41 6,EOR izy 51 5,
INC zp E6 5,INC zpx F6 6,INC abs EE 6,INC abx FE 7,INX imp E8 2,INY imp C8 2,
JMP abs 4C 3,JMP ind 6C 5,JSR abs 20 6,
LDA imm A9 2,LDA zp A5 3,LDA zpx B5 4,LDA abs AD 4,LDA abx BD 4,LDA aby B9 4,LDA izx A1 6,LDA izy B1 5,
LDX imm A2 2,LDX zp A6 3,LDX zpy B6 4,LDX abs AE 4,LDX aby BE 4,
LDY imm A0 2,LDY zp A4 3,LDY zpx B4 4,LDY abs AC 4,LDY abx BC 4,
LSR acc 4A 2,LSR zp 46 5,LSR zpx 56 6,LSR abs 4E 6,LSR abx 5E 7,NOP imp EA 2,
ORA imm 09 2,ORA zp 05 3,ORA zpx 15 4,ORA abs 0D 4,ORA abx 1D 4,ORA aby 19 4,ORA izx 01 6,ORA izy 11 5,
PHA imp 48 3,PHP imp 08 3,PLA imp 68 4,PLP imp 28 4,
ROL acc 2A 2,ROL zp 26 5,ROL zpx 36 6,ROL abs 2E 6,ROL abx 3E 7,
ROR acc 6A 2,ROR zp 66 5,ROR zpx 76 6,ROR abs 6E 6,ROR abx 7E 7,
RTI imp 40 6,RTS imp 60 6,
SBC imm E9 2,SBC zp E5 3,SBC zpx F5 4,SBC abs ED 4,SBC abx FD 4,SBC aby F9 4,SBC izx E1 6,SBC izy F1 5,
SEC imp 38 2,SED imp F8 2,SEI imp 78 2,
STA zp 85 3,STA zpx 95 4,STA abs 8D 4,STA abx 9D 5,STA aby 99 5,STA izx 81 6,STA izy 91 6,
STX zp 86 3,STX zpy 96 4,STX abs 8E 4,STY zp 84 3,STY zpx 94 4,STY abs 8C 4,
TAX imp AA 2,TAY imp A8 2,TSX imp BA 2,TXA imp 8A 2,TXS imp 9A 2,TYA imp 98 2
"""
for item in _tbl.replace('\n', '').split(','):
    item = item.strip()
    if not item: continue
    nm, md, op, cy = item.split()
    _d(nm, md, int(op, 16), int(cy))
for i in range(256):
    if i not in OPS: OPS[i] = ('imp', 'ILL', 2)
