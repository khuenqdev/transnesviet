
"""MMC3 (mapper 4) extension of the supplied minimal NES emulator - enough to boot MOTHER."""
try:
    from nes import NES, NESPAL
except ImportError:
    from emu import NES, NESPAL
import numpy as np

class MMC3(NES):
    def __init__(self, rom):
        self.rom = rom
        prg_kb = rom[4] * 16; chr_kb = rom[5] * 8
        self.P = bytearray(rom[16:16 + prg_kb * 1024])
        self.C = bytearray(rom[16 + prg_kb * 1024:16 + prg_kb * 1024 + chr_kb * 1024])
        self.R = [0, 2, 4, 5, 6, 7, 0, 1]; self.bsel = 0
        self.prgram = bytearray(0x2000)
        self.irq_latch = 0; self.irq_cnt = 0; self.irq_reload = False; self.irq_en = False; self.irq_line = False
        self.mirror_v = False
        self.nprg8 = len(self.P) // 0x2000
        self.log_banks = []
        super().__init__(rom[:16] + bytes(self.P[-0x2000:]) * 0 + bytes(16) )  # placeholder, fixed below
        # super() set prg/chr from wrong sizes; override what matters
        self.prg_size = len(self.P)
        self.ram = bytearray(0x800); self.vram = bytearray(0x800)
        self.a = self.x = self.y = 0; self.sp = 0xFD; self.p = 0x24
        self.pc = self.rd16(0xFFFC)

    # ---- mapping ----
    def prg_bank(self, a):
        slot = (a - 0x8000) >> 13
        last = self.nprg8 - 1; sec = self.nprg8 - 2
        mode = (self.bsel >> 6) & 1
        if slot == 0: b = sec if mode else self.R[6]
        elif slot == 1: b = self.R[7]
        elif slot == 2: b = self.R[6] if mode else sec
        else: b = last
        return (b % self.nprg8) * 0x2000 + (a & 0x1FFF)

    def chr_addr(self, addr):
        addr &= 0x1FFF
        if self.bsel & 0x80: addr ^= 0x1000
        if addr < 0x1000:
            r = addr >> 11; base = (self.R[r] & 0xFE) * 0x400; return (base + (addr & 0x7FF)) % len(self.C)
        r = 2 + ((addr - 0x1000) >> 10)
        return (self.R[r] * 0x400 + (addr & 0x3FF)) % len(self.C)

    def ppu_read(self, addr):
        addr &= 0x3FFF
        if addr < 0x2000: return self.C[self.chr_addr(addr)]
        if addr < 0x3F00: return self.vram[self.nt_index(addr)]
        return self.pal[self.pal_idx(addr)]

    def nt_index(self, addr):
        addr = (addr - 0x2000) & 0xFFF
        table = addr // 0x400; off = addr & 0x3FF
        phys = (table & 1) if self.mirror_v else (table // 2)
        return (phys & 1) * 0x400 + off

    def rd(self, a):
        if 0x6000 <= a < 0x8000: return self.prgram[a - 0x6000]
        if a >= 0x8000: return self.P[self.prg_bank(a)]
        return NES.rd(self, a)

    def wr(self, a, v):
        if 0x6000 <= a < 0x8000: self.prgram[a - 0x6000] = v; return
        if a >= 0x8000:
            even = (a & 1) == 0
            if a < 0xA000:
                if even: self.bsel = v
                else: self.R[self.bsel & 7] = v
            elif a < 0xC000:
                if even: self.mirror_v = (v & 1) == 0
            elif a < 0xE000:
                if even: self.irq_latch = v
                else: self.irq_reload = True
            else:
                if even: self.irq_en = False; self.irq_line = False
                else: self.irq_en = True
            return
        NES.wr(self, a, v)

    def clock_irq(self):
        if self.irq_cnt == 0 or self.irq_reload:
            self.irq_cnt = self.irq_latch; self.irq_reload = False
        else:
            self.irq_cnt -= 1
        if self.irq_cnt == 0 and self.irq_en: self.irq_line = True

    def irq(self):
        self.push(self.pc >> 8); self.push(self.pc & 0xFF); self.push((self.p | 0x20) & 0xEF)
        self.p |= 4; self.pc = self.rd16(0xFFFE); self.cycles += 7

    def run_frame(self, hook=None):
        self.status |= 0x80
        if self.ctrl & 0x80: self.nmi()
        start = self.cycles
        line_cyc = 113.667
        sl = 241
        self.status &= ~0x40 & 0xFF
        while self.cycles - start < 29781:
            if self.nmi_pending: self.nmi_pending = False; self.nmi()
            el = self.cycles - start
            cur = 241 + int(el / line_cyc)
            while sl < cur:
                sl += 1
                s = sl % 262
                if s == 261:
                    self.status &= 0x1F
                    self.frame_scroll = (self.scroll_x, self.scroll_y, self.ctrl & 3)
                    self.frame_bgpt = 1 if self.ctrl & 0x10 else 0
                    self.frame_bank = (list(self.R), self.bsel)
                if s < 240 and (self.mask & 0x18):
                    self.clock_irq()
                    if s == (self.oam[0] + 1) and (self.mask & 0x18): self.status |= 0x40
            if self.irq_line and not (self.p & 4):
                self.irq_line = False; self.irq()
            if hook: hook(self)
            self.step()
        self.status &= 0x3F

    def tile_pixels(self, pt, tile):
        base = pt * 0x1000 + tile * 16
        lo = [self.ppu_read(base + i) for i in range(8)]
        hi = [self.ppu_read(base + 8 + i) for i in range(8)]
        out = np.zeros((8, 8), np.uint8)
        for r in range(8):
            for c in range(8):
                b = 7 - c
                out[r, c] = ((lo[r] >> b) & 1) | (((hi[r] >> b) & 1) << 1)
        return out
