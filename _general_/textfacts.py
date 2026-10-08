#!/usr/bin/env python3
"""nes_text.py - Text facts of a NES / Famicom ROM (usage: see TEXTFACTS.md)."""
import sys

import romfacts as R
import textfacts_core as T


class NES(T.Platform):
    name = "NES / Famicom"
    vwf_hint = "(NES: almost always fixed 8x8; a VWF has to draw into CHR-RAM tiles)"

    def setup_args(self, ap):
        ap.add_argument("--bank-size", type=lambda s: int(s, 0), help="PRG bank size in bytes (default: from the mapper)")

    def load(self, data, args):
        f = R.analyze_nes(data)
        mapper = int(dict(f.hw)["Mapper"].split()[0])
        self.bank = args.bank_size or f.banks[0][2]
        self.n = max(1, len(f.image) // self.bank)
        self.any = args.any_bank
        fixed_txt = R.NES_MAPPERS.get(mapper, ("", 0, ""))[2]
        if self.bank >= 0x8000:
            self.fixed = set(range(self.n)) if self.n == 1 else set()
        elif self.bank == 0x4000:
            self.fixed = {self.n - 1} if "last" in fixed_txt else set()
            if mapper == 1 and self.n == 32:
                self.fixed.add(15)  # SUROM: each 256 KB half has its own fixed bank
        else:
            self.fixed = {self.n - 1, self.n - 2} if "two" in fixed_txt else ({self.n - 1} if "last" in fixed_txt else set())
        self._addr = f.addr if not args.bank_size else (lambda o: f"{o // self.bank:02X}:{0x8000 + o % self.bank:04X}")
        self.notes = [f"PRG image {len(f.image) // 1024} KB, mapper {mapper}, {self.n} bank(s) of {self.bank // 1024} KB, "
                      f"fixed bank(s): {', '.join(f'{b:02X}' for b in sorted(self.fixed)) or 'none'}. "
                      "Offsets in this report are PRG offsets (file offset - 16).",
                      "Pointers are 16-bit little-endian CPU addresses; the bank is implied by the code that reads them."]
        return f.image

    def addr(self, o):
        return self._addr(o)

    def keys(self, f):
        b, off = f // self.bank, f % self.bank
        if self.bank >= 0x8000:
            return [(0x8000 + off, f"fixed {b:02X}" if b in self.fixed else b)]
        if self.bank == 0x4000:
            return [(0xC000 + off, f"fixed {b:02X}")] if b in self.fixed else [(0x8000 + off, b)]
        if b in self.fixed:
            return [((0xE000 if b == self.n - 1 else 0xC000) + off, f"fixed {b:02X}")]
        return [(0x8000 + off, b), (0xA000 + off, b)]

    def allowed(self, o, ctx):
        return isinstance(ctx, str) or self.any or ctx == o // self.bank

    def resolve(self, v, ctx):
        b = int(ctx[-2:], 16) if isinstance(ctx, str) else ctx
        if self.bank >= 0x8000:
            base = 0x8000
        elif isinstance(ctx, str):
            base = 0xC000 if self.bank == 0x4000 or b == self.n - 2 else 0xE000
        else:
            base = 0x8000 if v < 0xA000 or self.bank == 0x4000 else 0xA000
        return b * self.bank + v - base if base <= v < base + self.bank else None

    def formats(self, args):
        return [T.PtrFormat("16-bit LE (CPU address)", 2, self.keys, allowed=self.allowed, resolve=self.resolve)]

    def code_patterns(self, args):
        return [T.CodePattern("LDA/LDX/LDY #lo ... #hi", rb"[\xA9\xA2\xA0](.)(?:[\x85\x86\x84].|[\x8D\x8E\x8C]..)?[\xA9\xA2\xA0](.)",
                              "16-bit LE (CPU address)", value=lambda m: m.group(1)[0] | (m.group(2)[0] << 8))]


if __name__ == "__main__":
    sys.exit(T.run(NES()))
