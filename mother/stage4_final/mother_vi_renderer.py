#!/usr/bin/env python3
"""
mother_vi_renderer.py - Stage 3: mark-row text renderer for MOTHER (NES) Vietnamese.

Adds support for the stage-2 encoding (mark byte $80-$8D placed BEFORE a glyph; the mark is
drawn one tile row ABOVE that glyph and takes no column) to the game's text engine.

How the original engine works (bank $1E/$1F, verified with the emulator):
  * $C83D builds one text row into the PPU buffer page $0400 as entries
        [05][len][hi][lo][tiles...]      (split at the nametable edge)
    $C86D builds the "gap" row above a window line (borders + spaces).
  * Dialogue/battle text ($C707) builds the line into a 41-byte record ($0433, $045C, ...),
    appends "clear row below" fill entries [08][len][hi][lo][A0] and types it one char per frame.
  * Scrolling ($C7C1/$C7D4) moves every record up one row twice and re-sends it to the NMI.
  * NMI ($F79F) walks the buffer and dispatches on the entry type via the table at $F8C1.

Patch (hooks in the fixed banks; the NMI work lives in free space of PRG bank $1B):
  1. $C855  JSR TXTCLS : a mark byte is appended inline to the current entry (no column used,
                         $7E/$7B untouched) and the entry type becomes $0C ("text with marks").
  2. $C887  JSR GAPCLS : in gap rows, mark bytes are skipped (no column); code at $C74A.
  3. $C72C  typewriter : instead of appending "clear row below" fill entries, every record entry
                         becomes type $0B ("dialogue line"). This frees the 10 bytes the fills
                         used, so a 22-column line can carry up to 10 marks in the unchanged
                         41-byte record.
  4. $C762/$C7A4       : the typewriter sends a mark as a one-byte type-$0C entry (the NMI puts
                         it one row up); the cursor does not advance; no "blip" sound for marks.
  5. $C9AB/$C9B4       : fixed-width field printer (names in Name/State windows, {num}):
                         marks inline / skipped in gap rows; field width counted in columns.
  6. $C7C9/$C7DE       : scroll. The original moved every record up one row twice and used the
                         shifted fill entries to wipe the line leaving the top. The first record of
                         each pass (the line leaving the window, $7F<>0) now becomes type $0D =
                         "clear its text row" instead of moving (moving it would put its marks on
                         the window border).
  7. $F7D1  JMP NEWDISP: NMI types >= $0B go through a trampoline that maps bank $1B at $8000
                         (saving/restoring the MMC3 shadows $EE/$F6 exactly like the game's own
                         NMI command $0A) and runs NMIH, which walks the rest of the buffer:
                           frame A  $0B/$0C : text row only (fast)        -> type +$10
                           frame B  $1B     : mark row + cleared row below -> type $0B
                                    $1C     : marks only (sparse)          -> type $0C
                         Splitting over two frames keeps vblank use at or below the game's own
                         worst case (measured: see stage-3 report).
RAM: $0105-$010F (bottom of the stack page; never touched by the game in an emulator run).
Fixed-bank space: $FEA2-$FF3F (all 158 free bytes) + bytes freed at $C72C and $C7DE.

Usage:
  python mother_vi_renderer.py --rom mother.nes --out outdir [--test-message]
"""
import argparse, os, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asm6502 import assemble
import mother_vi_font

FIX_FREE = 0xFEA2          # bank $1F free space $FEA2-$FF3F (158 bytes of $FF)
FIX_FREE_END = 0xFF40
NMI_BANK = 0x1B            # PRG bank holding the NMI handler (free $FF area at +$1488..)
NMI_ORG = 0x9500           # mapped at $8000 via R6 -> bank offset +$1500

def prg_off(bank, cpu):
    return bank * 0x2000 + (cpu & 0x1FFF)

def fixed_off(cpu):          # $C000-$DFFF -> bank $1E, $E000-$FFFF -> bank $1F
    return prg_off(0x1E if cpu < 0xE000 else 0x1F, cpu)

# --------------------------------------------------------------------------------------------
# 6502 sources
# --------------------------------------------------------------------------------------------
FIXED_SRC = """
; ---------------- NMI dispatcher (replaces ASL/TAX/LDA tbl/PHA/... at $F7D1) -------------
NEWDISP:
    CMP #$0B
    BCS VIET
    ASL A
    TAX
    LDA $F8C2,X
    PHA
    LDA $F8C1,X
    PHA
    RTS
VIET:
    LDA $EE
    PHA
    LDA $F6
    PHA
    LDA #NMIBANK
    LDX #$06
    JSR $FFD0
    JSR NMIH
    PLA
    LDX #$06
    JSR $FFD0
    PLA
    STA $EE
    ORA $EF
    STA $8000
    JMP $F7CA
; ---------------- C = 1 if A is a mark byte ($80-$8D) ------------------------------------
ISMARK:
    CMP #$8E
    BCS NOTMK
    CMP #$80
    RTS
NOTMK:
    CLC
    RTS
; ---------------- append mark A inline to the current entry; entry type -> $0C -----------
MARKAPP:
    STA $0400,X
    INX
    TXA
    PHA
    LDX $E6
    INC $0401,X
    LDA #$0C
    STA $0400,X
    PLA
    TAX
    RTS
; ---------------- main text loop ($C855): marks take no column ---------------------------
TXTCLS:
    JSR ISMARK
    BCC TXGO
    JSR MARKAPP
    INY
    STY $7A
    PLA
    PLA
    JMP $C853
TXGO:
    JMP $CA5C
; ---------------- fixed-width field loop ($C9AB, names/numbers) -------------------------
FLDCLS:
    JSR ISMARK
    BCC TXGO
    JSR MARKAPP
    INY
    PLA
    PLA
    JMP $C9A5
; ---------------- fixed-width field, gap row ($C9B4): skip marks -------------------------
FLDGAP:
    JSR ISMARK
    BCC FGGO
    INY
    PLA
    PLA
    JMP $C9A5
FGGO:
    JMP $CA7C
; ---------------- typewriter: a mark is sent as a 1-byte type-$0C entry ------------------
TWH1:
    STA $0404
    JSR ISMARK
    LDA #$05
    BCC W1T
    LDA #$0C
W1T:
    STA $0400
    LDA $0404
    BCC W1X
    LDA #$A0
W1X:
    RTS
TWH2:
    LDA $0404
    JSR ISMARK
    BCS W2R
    INC $0403
W2R:
    RTS
"""

NMI_SRC = """
; Entered from the NMI buffer walker with Y = index of an entry whose type is >= $0B.
; This routine then walks the rest of the buffer itself (types 05/0B/0C/0D/1B/1C) so that it can
; split the work of an entry with marks over TWO frames (vblank time is limited):
;   frame A: type 0B/0C -> text row (marks skipped);
;            the entry becomes 1B/1C and the walk stops WITHOUT releasing the buffer
;            (bit 7 set on the first entry type -> original walker strips it and stops, $E5 kept)
;   frame B: type 1B -> full mark row (marks + spaces) + cleared row below / 1C -> marks only;
;            type restored to 0B/0C
; Returns Y; the trampoline jumps back to the original walker at $F7CA.
; RAM: $0106 type index, $0107 pending, $0108 type, $0109 len, $010A hi, $010B lo,
;      $010C data start, $010D mark count/pend/column, $010E glyph count, $010F mark-row hi
NMIH:
    LDA #$00
    STA $0107
LOOP:
    LDA $0400,Y
    BEQ ATEND
    CMP #$05
    BEQ DO5
    CMP #$0B
    BEQ DOA
    CMP #$0C
    BEQ DOA
    CMP #$0D
    BEQ DOCLR
    CMP #$1B
    BEQ DOB
    CMP #$1C
    BEQ DOB
    JSR FLUSH
    RTS
ATEND:
    LDA $0107
    BEQ ENDRET
    LDY $E6
    LDA $0400,Y
    ORA #$80
    STA $0400,Y
ENDRET:
    RTS
DO5:
    JSR $F9EF
    JMP LOOP
DOCLR:
    JSR HDR
    JSR SETTXT
    LDX $0109
    JSR CLRSCAN
    JMP LOOP
DOB:
    JSR HDR
    JSR PHASEB
    JMP LOOP
DOA:
    JSR HDR
    JSR TEXTROW
    LDA $0108
    CMP #$0B
    BNE DOA2
    JMP DOA3
DOA2:
    LDA $010D
    BNE DOA3
    JMP LOOP
DOA3:
    LDX $0106
    LDA $0400,X
    ORA #$10
    STA $0400,X
    INC $0107
    JMP LOOP
; ---- frame B work for one entry (header already parsed) ---------------------------------
PHASEB:
    LDX $0106
    LDA $0400,X
    AND #$EF
    STA $0400,X
    CMP #$0B
    BNE PBS
    JSR MROW
    JMP CLRBELOW
PBS:
    JMP SPARSE
; ---- parse entry header at Y ----------------------------------------------------------
HDR:
    STY $0106
    LDA $0400,Y
    STA $0108
    INY
    LDA $0400,Y
    STA $0109
    INY
    LDA $0400,Y
    STA $010A
    INY
    LDA $0400,Y
    STA $010B
    INY
    STY $010C
    RTS
SETTXT:
    LDA $010A
    STA $2006
    LDA $010B
    STA $2006
    RTS
; ---- text row: glyphs only; counts marks ($010D) and glyphs ($010E) ---------------------
TEXTROW:
    JSR SETTXT
    LDA #$00
    STA $010D
    LDX $0109
    BEQ T1E
T1:
    LDA $0400,Y
    CMP #$8E
    BCS T1G
    CMP #$80
    BCC T1G
    INC $010D
    JMP T1N
T1G:
    STA $2007
T1N:
    INY
    DEX
    BNE T1
T1E:
    LDA $0109
    SEC
    SBC $010D
    STA $010E
    RTS
; ---- row below: $010E spaces ----------------------------------------------------------
CLRBELOW:
    LDA $010B
    CLC
    ADC #$20
    TAX
    LDA $010A
    ADC #$00
    STA $2006
    STX $2006
    LDX $010E
    BEQ CBE
    LDA #$A0
CB1:
    STA $2007
    DEX
    BNE CB1
CBE:
    RTS
; ---- write a space for every glyph of the entry (X = len, PPU address set) -------------
CLRSCAN:
    TXA
    BEQ CSE
CS1:
    LDA $0400,Y
    CMP #$8E
    BCS CSG
    CMP #$80
    BCS CSN
CSG:
    LDA #$A0
    STA $2007
CSN:
    INY
    DEX
    BNE CS1
CSE:
    RTS
; ---- full mark row: mark or space above every glyph -----------------------------------
MROW:
    LDY $010C
    LDA $010B
    SEC
    SBC #$20
    TAX
    LDA $010A
    SBC #$00
    STA $2006
    STX $2006
    LDA $0109
    STA $010E
    LDX $0109
    BEQ MRE
M1:
    LDA $0400,Y
    CMP #$8E
    BCS MG
    CMP #$80
    BCC MG
    STA $2007
    DEC $010E
    INY
    DEX
    BEQ MRE
    INY
    DEX
    BNE M1
MRE:
    RTS
MG:
    LDA #$A0
    STA $2007
    INY
    DEX
    BNE M1
    RTS
; ---- sparse marks: each mark alone, one row above its glyph ---------------------------
SPARSE:
    LDY $010C
    LDA $010B
    SEC
    SBC #$20
    STA $010D
    LDA $010A
    SBC #$00
    STA $010F
    LDX $0109
    BEQ S1E
S1:
    LDA $0400,Y
    CMP #$8E
    BCS S1G
    CMP #$80
    BCC S1G
    PHA
    LDA $010F
    STA $2006
    LDA $010D
    STA $2006
    PLA
    STA $2007
    JMP S1N
S1G:
    INC $010D
S1N:
    INY
    DEX
    BNE S1
S1E:
    RTS
; ---- unknown entry type while frame-B work is pending: do it now -----------------------
FLUSH:
    LDA $0107
    BEQ FLE
    STY $0105
    LDY $E6
FL1:
    CPY $0105
    BCS FLD
    LDA $0400,Y
    CMP #$1B
    BEQ FLB
    CMP #$1C
    BEQ FLB
    INY
    TYA
    SEC
    ADC #$02
    ADC $0400,Y
    TAY
    JMP FL1
FLB:
    JSR HDR
    JSR PHASEB
    JMP FL1
FLD:
    LDY $0105
    LDA #$00
    STA $0107
FLE:
    RTS
"""

# In-place patches: (cpu address, expected original bytes, new source or bytes)
TYPEWRITER_SRC = """
    LDA #$0B
    STA $0400,X
    LDA $0401,X
    STA $7E
    LDA $0403,X
    STA $0403
    LDA $0402,X
    STA $0402
    TXA
    CLC
    ADC #$04
    TAX
    JMP $C75F
; gap-row builder hook lives in the bytes freed above (no fill entries any more)
GAPCLS:
    JSR ISMARK
    BCC GPGO
    INY
    STY $7A
    PLA
    PLA
    JMP $C885
GPGO:
    JMP $CA7C
"""
SCROLL_SRC = """
    LDA $7F
    BEQ SH
    LDA #$0D
    STA $0400,X
    BNE NEXT
SH:
    JSR $C80E
NEXT:
    TXA
    CLC
    ADC #$04
    ADC $0401,X
    TAX
    BCC $C7D9
"""

ORIG = {   # cpu: original bytes (verified before patching)
    0xF7D1: bytes.fromhex('0aaabdc2f848bdc1f84860'),
    0xC855: bytes.fromhex('205cca'),
    0xC887: bytes.fromhex('207cca'),
    0xC762: bytes.fromhex('8d0404'),
    0xC7A4: bytes.fromhex('ee0304'),
    0xC72C: bytes.fromhex('a908990004bd0104857e990104a9a099040418bd03048d03046920990304'
                          'bd02048d020469009902048a186904aa98186905a8'),
    0xC7DE: bytes.fromhex('4905d011057fd003200ec88a1869047d0104aa90e6200ec88a186905aa90dc'),
    0xC7C9: bytes.fromhex('867f'),
    0xC9AB: bytes.fromhex('205cca'),
    0xC9B4: bytes.fromhex('207cca'),
}

def build(rom_in, with_font=True):
    rom = bytearray(rom_in)
    if with_font:
        rom = bytearray(mother_vi_font.inject(bytes(rom))[0])
    P0 = 16
    def put(off, data):
        rom[P0 + off:P0 + off + len(data)] = data
    def get(off, n):
        return bytes(rom[P0 + off:P0 + off + n])

    # 1. NMI handler in bank $1B
    nmi_code, nmi_labs = assemble(NMI_SRC, NMI_ORG)
    noff = prg_off(NMI_BANK, NMI_ORG)
    assert set(get(noff, len(nmi_code))) == {0xFF}, 'bank $1B target area is not free'
    put(noff, nmi_code)

    # 2. fixed-bank routines
    fx_code, fx = assemble(FIXED_SRC, FIX_FREE, {'NMIBANK': NMI_BANK, 'NMIH': nmi_labs['NMIH']})
    assert FIX_FREE + len(fx_code) <= FIX_FREE_END, 'fixed free space overflow (%d bytes)' % len(fx_code)
    assert set(get(fixed_off(FIX_FREE), len(fx_code))) == {0xFF}
    put(fixed_off(FIX_FREE), fx_code)

    # 3. hooks / in-place rewrites
    def patch(cpu, new):
        old = ORIG[cpu]
        cur = get(fixed_off(cpu), len(old))
        assert cur == old, 'unexpected bytes at $%04X: %s' % (cpu, cur.hex())
        assert len(new) <= len(old), '$%04X: patch longer than original' % cpu
        put(fixed_off(cpu), new + bytes([0xEA]) * (len(old) - len(new)))   # NOP-fill
    jsr = lambda a: bytes([0x20, a & 0xFF, a >> 8])
    jmp = lambda a: bytes([0x4C, a & 0xFF, a >> 8])
    patch(0xF7D1, jmp(fx['NEWDISP']))
    patch(0xC855, jsr(fx['TXTCLS']))
    patch(0xC762, jsr(fx['TWH1']))
    patch(0xC7A4, jsr(fx['TWH2']))
    patch(0xC9AB, jsr(fx['FLDCLS']))
    patch(0xC9B4, jsr(fx['FLDGAP']))
    tw, twl = assemble(TYPEWRITER_SRC, 0xC72C, {'ISMARK': fx['ISMARK']})
    patch(0xC72C, tw)
    fx['GAPCLS'] = twl['GAPCLS']
    patch(0xC887, jsr(fx['GAPCLS']))
    sc, _ = assemble(SCROLL_SRC, 0xC7DE)
    patch(0xC7DE, sc)
    patch(0xC7C9, bytes([0x85, 0x7F]))     # STX $7F -> STA $7F: first record of pass 1 is the line leaving
    info = {'nmi_handler': '$%04X bank $%02X (%d bytes)' % (NMI_ORG, NMI_BANK, len(nmi_code)),
            'fixed_code': '$%04X-$%04X (%d of 158 bytes)' % (FIX_FREE, FIX_FREE + len(fx_code) - 1, len(fx_code)),
            'labels': {k: '$%04X' % v for k, v in fx.items()}}
    return bytes(rom), info

def make_ips(orig, new):
    out = bytearray(b'PATCH'); i = 0; n = len(new)
    while i < n:
        if i < len(orig) and orig[i] == new[i]:
            i += 1; continue
        j = i
        while j < n and (j >= len(orig) or orig[j] != new[j]) and j - i < 0xFFFF:
            j += 1
        if i == 0x454F46:            # 'EOF' offset quirk
            i -= 1
        out += struct.pack('>I', i)[1:] + struct.pack('>H', j - i) + new[i:j]
        i = j
    return bytes(out + b'EOF')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', required=True)
    ap.add_argument('--out', default='stage3_out')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rom = open(a.rom, 'rb').read()
    new, info = build(rom)
    open(os.path.join(a.out, 'mother_vi_stage3.nes'), 'wb').write(new)
    open(os.path.join(a.out, 'mother_vi_stage3.ips'), 'wb').write(make_ips(rom, new))
    print('input  CRC32 %08X' % (zlib.crc32(rom) & 0xFFFFFFFF))
    print('output CRC32 %08X' % (zlib.crc32(new) & 0xFFFFFFFF))
    for k, v in info.items():
        print(k, v)

if __name__ == '__main__':
    main()
