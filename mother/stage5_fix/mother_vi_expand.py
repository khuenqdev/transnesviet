
#!/usr/bin/env python3
"""
mother_vi_expand.py - Stage 4 engine work: move the script from CHR-ROM to an expanded PRG-ROM.

Why: the CHR text area has only 7,109 free bytes and CHR is at MMC3's 256 KB limit.  Vietnamese
needs ~1.4x the English bytes (mark bytes), so the script is moved to PRG and PRG is doubled.

  * PRG 256 KB -> 512 KB (header byte 4: $10 -> $20).  Banks $00-$1D stay where they are,
    fixed banks $1E/$1F are copied to $3E/$3F (MMC3 always maps the last two banks there);
    the originals are kept, so any R6/R7 write of $1E/$1F still finds the same code.
    Banks $20-$3D (240 KB) are free for the script.
  * Pointer table (bank $18, 2000 x 3 bytes) now holds [lo][hi][bank] = CPU address $8000-$9FFF
    in PRG bank `bank`.  Strings never cross an 8 KB bank boundary.
  * $CAE9 (bank $1E): the request to the NMI becomes [0A][bank][hi][lo] (was CHR bank/PPU addr).
  * $F99F (bank $1F): NMI command $0A maps the PRG bank at $8000 (R6), copies 64 bytes to
    $0110 and restores the bank and the $8000 shadow exactly like the original handler did.
The text interpreter, renderer and the rest of the engine are untouched.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asm6502 import assemble

BANK = 0x2000
TEXT_FIRST_BANK, TEXT_LAST_BANK = 0x20, 0x3D
PTR_TABLE = 0x18 * BANK
N_IDS = 2000

REQ_ORIG = bytes.fromhex('a50b4aa50a6a386a8d0104a50a290309088d0204a5098d0304')     # $CAE9, 25 bytes
NMI_ORIG = bytes.fromhex('a5ee48a5f448a5f548c8b90004a20420d0ff186901a20520d0ffc8b90004'
                         '8d0620c8b900048d0620c8ad0720a200ad07209d1001e8e04090f568a205'
                         '20d0ff68a20420d0ff6885ee05ef8d00804ccaf7')                 # $F99F, 80 bytes

REQ_SRC = """
    LDA $0B
    STA $0401
    LDA $0A
    STA $0402
    LDA $09
    STA $0403
"""
NMI_SRC = """
    LDA $EE
    PHA
    LDA $F6
    PHA
    INY
    LDX $0400,Y
    INY
    LDA $0400,Y
    STA $75
    INY
    LDA $0400,Y
    STA $74
    INY
    TYA
    PHA
    TXA
    LDX #$06
    JSR $FFD0
    LDY #$00
L:
    LDA ($74),Y
    STA $0110,Y
    INY
    CPY #$40
    BCC L
    PLA
    TAY
    PLA
    LDX #$06
    JSR $FFD0
    PLA
    STA $EE
    ORA $EF
    STA $8000
    LDA #$10
    STA $74
    LDA #$01
    STA $75
    JMP $F7CA
"""

def expand(rom):
    """rom: 256 KB-PRG ROM (stage-3 patched). Returns 512 KB-PRG ROM with the new text reader."""
    assert rom[4] == 0x10
    hdr = bytearray(rom[:16]); hdr[4] = 0x20
    P = bytearray(rom[16:16 + 0x40000]); C = rom[16 + 0x40000:]
    def patch(bank, cpu, orig, src):
        off = bank * BANK + (cpu & 0x1FFF)
        assert bytes(P[off:off + len(orig)]) == orig, 'unexpected bytes at $%04X' % cpu
        code, _ = assemble(src, cpu)
        assert len(code) <= len(orig)
        P[off:off + len(orig)] = code + bytes([0xEA]) * (len(orig) - len(code))
        return len(code)
    patch(0x1E, 0xCAE9, REQ_ORIG, REQ_SRC)
    patch(0x1F, 0xF99F, NMI_ORIG, NMI_SRC)
    newP = P[:0x40000] + bytes([0xFF]) * (0x1E * BANK) + P[0x1E * BANK:0x40000]
    assert len(newP) == 0x80000
    return bytes(hdr) + bytes(newP) + C

class TextPacker:
    """Places strings in PRG banks $20-$3D without crossing a bank boundary."""
    def __init__(self):
        self.bank = TEXT_FIRST_BANK; self.pos = 0; self.data = {}
    def place(self, blob):
        if len(blob) > BANK:
            raise ValueError('string longer than a bank')
        if self.pos + len(blob) > BANK:
            self.bank += 1; self.pos = 0
            if self.bank > TEXT_LAST_BANK:
                raise ValueError('out of text space')
        b, p = self.bank, self.pos
        self.data.setdefault(b, bytearray())
        self.data[b] += blob
        self.pos += len(blob)
        return b, 0x8000 + p
    def used(self):
        return sum(len(v) for v in self.data.values())
    def write(self, rom):
        rom = bytearray(rom)
        for b, blob in self.data.items():
            off = 16 + b * BANK
            rom[off:off + len(blob)] = blob
        return rom

def set_pointer(rom, msg_id, bank, cpu):
    off = 16 + PTR_TABLE + 3 * msg_id
    rom[off:off + 3] = bytes([cpu & 0xFF, cpu >> 8, bank])

def insert_script(rom, segments):
    """segments: list (in order) of dicts {ids:[...], data:bytes, falls_through:bool}.
    Fall-through chains are placed contiguously. Returns (rom, packer)."""
    rom = bytearray(rom); pk = TextPacker()
    i = 0
    while i < len(segments):
        j = i
        while segments[j]['falls_through']:
            j += 1
        chain = segments[i:j + 1]
        blob = b''.join(s['data'] for s in chain)
        bank, cpu = pk.place(blob)
        for s in chain:
            for mid in s['ids']:
                set_pointer(rom, mid, bank, cpu)
            cpu += len(s['data'])
        i = j + 1
    return pk.write(rom), pk
