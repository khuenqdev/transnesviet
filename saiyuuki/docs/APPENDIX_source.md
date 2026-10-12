# Appendix – Source code

Complete listings of the ROM-side code and the main build tool. Other tools are in `tools/`.

## `src/tramp.asm`

```asm
; ============================================================================
;  Fixed-bank trampolines (placed in the free space at $C02A of the fixed bank)
; ============================================================================
RET    = $0491
MODE   = $0493
SAV04  = $0498
SAV05  = $0499
TDONE  = $04F9
TPOS   = $04F8
SAV02  = $04F0          ; 4 bytes: engine $02..$05
SWITCH = $FCAA          ; engine bank switch  (A = bank, returns A = old bank)
ENQ    = $FF76
WENTRY = $8001

        .org $C02A
BUSTAB: .db 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15   ; bus-conflict table, 16 banks

; --- site stubs (JSR targets patched into bank 3) ---
T_INIT: LDA $51                     ; price rows 154..178 and the yen kanji (186) keep the original drawing
        CMP #186
        BEQ ti_pass
        CMP #154
        BCC ti_go
        CMP #179
        BCS ti_go
ti_pass:JMP ENQ
ti_go:  LDX #0
        BEQ common
T_STEP: LDX #1
        BNE common
T_BLINK:LDX #2
        BNE common
T_CLEAR:LDX #3
        BNE common
; --- title screen: called instead of JSR $C4A2 in the bank-6 main loop ---
T_MAIN: LDA $FD
        CMP #3                      ; 3 = title screen idle
        BNE tm_rst
        LDA TDONE
        BNE tm_go
        LDX #4
        JSR common
        BCS tm_go
        LDA #1
        STA TDONE
tm_go:  JMP $C4A2
tm_rst: LDA #0
        STA TDONE
        STA TPOS
        JMP $C4A2
common: STX MODE
        LDA $02
        STA SAV02
        LDA $03
        STA SAV02+1
        LDA $04
        STA SAV02+2
        STA SAV04
        LDA $05
        STA SAV02+3
        STA SAV05
        LDA #8                      ; modes 2/3 do not need row data: bank 8
        CPX #2
        BCS cm_sw
        LDA $51                     ; bank = 8 + row/32
        LSR A
        LSR A
        LSR A
        LSR A
        LSR A
        CLC
        ADC #8
cm_sw:  JSR SWITCH
        PHA
        JSR WENTRY
        PLA
        JSR SWITCH
        LDA SAV02
        STA $02
        LDA SAV02+1
        STA $03
        LDA SAV02+2
        STA $04
        LDA SAV02+3
        STA $05
        LDA RET
        LSR A                       ; bit0 -> carry
        RTS
```

## `src/window.asm`

```asm
; ============================================================================
;  Saiyuuki World - Vietnamese patch : "window" code (identical in banks 8..14)
;  Lives at $8000 in every data bank; runs while that bank is mapped.
;  Called from the fixed-bank trampoline (tramp.asm) with MODE set.
;
;  Row record in the data bank (6-byte header + bitmaps):
;     +0 flags  bit0 = 12-px bitmap present, bit1 = 8-px bitmap present, bit7 = blank row
;     +1 n12    tile columns of the 12-px bitmap  (12 bytes / column)
;     +2 n8     tile columns of the 8-px bitmap   ( 8 bytes / column)
;     +3 dx8    signed column offset of the 8-px strip
;     +4,+5     offset of the 8-px data from the start of the record
; ============================================================================
RET    = $0491          ; 0 = ok, 1 = PPU buffer full -> engine retries
PROG   = $0492          ; columns already drawn for the current row (retry support)
MODE   = $0493          ; 0 row start, 1 typewriter step, 2 blink-erase, 3 clear lines
LINE   = $0494
STEP   = $0495
CLS    = $0496          ; 0/1 dialog line, 2 small strip slot, 3 banner, $FF none
SAV04  = $0498          ; engine $04/$05 at hook time
SAV05  = $0499
PROGR  = $049A
TT     = $049B
FLG    = $049C
N12    = $049D
N8     = $049E
DX8    = $049F
SBASE  = $04A0
SMAX   = $04A1
D12L   = $04A2
D12H   = $04A3
D8L    = $04A4
D8H    = $04A5
NTL    = $04A6
NTH    = $04A7
PIDX   = $04A8
PAD    = $04A9
CNT    = $04AA
STAGE  = $04B0          ; 32 bytes
NTB    = $04D0          ; 2 bytes
ENQ    = $FF76

        .org $8000
        .db 0                       ; bank id (patched by the builder)
        JMP entry                   ; $8001
        .org $8010
entry:  LDA MODE
        BNE en_1
        JMP do_init
en_1:   CMP #1
        BNE en_2
        JMP do_step
en_2:   CMP #2
        BNE en_3
        JMP do_blink
en_3:   CMP #3
        BNE en_4
        JMP do_clear
en_4:   JMP do_title

; ---- classify: CLS (+LINE) from SAV04/05 -------------------------------------
classify:
        LDA #$FF
        STA CLS
        LDA SAV05
        CMP #$21
        BNE cl_slot
        LDA SAV04
        AND #$E0
        CMP #$40
        BEQ cl_0
        CMP #$80
        BEQ cl_1
cl_slot:
        LDA SAV05                   ; banner row at $2101
        CMP #$21
        BNE cl_s0
        LDA SAV04
        CMP #$01
        BNE cl_s0
        LDA #3
        STA CLS
        RTS
cl_s0:  LDX #0
cl_sl:  LDA SLOTS+1,X
        BEQ cl_end
        CMP SAV05
        BNE cl_sn
        LDA SLOTS,X
        CMP SAV04
        BNE cl_sn
        LDA SLOTS+2,X
        STA SBASE
        LDA SLOTS+3,X
        STA SMAX
        LDA #2
        STA CLS
        RTS
cl_sn:  INX
        INX
        INX
        INX
        BNE cl_sl
cl_end: RTS
cl_0:   LDA #0
        STA LINE
        STA CLS
        RTS
cl_1:   LDA #1
        STA LINE
        STA CLS
        RTS

; ---- setrow: read the header of the current row, D12/D8 pointers ----------------
setrow: LDA $51
        AND #31
        ASL A
        TAX
        LDA ROWTAB,X
        STA $02
        LDA ROWTAB+1,X
        STA $03
        LDY #0
        LDA ($02),Y
        STA FLG
        INY
        LDA ($02),Y
        STA N12
        INY
        LDA ($02),Y
        STA N8
        INY
        LDA ($02),Y
        STA DX8
        INY
        LDA ($02),Y
        STA D8L
        INY
        LDA ($02),Y
        STA D8H
        CLC                         ; D8 = rec + off8
        LDA D8L
        ADC $02
        STA D8L
        LDA D8H
        ADC $03
        STA D8H
        CLC                         ; D12 = rec + 6
        LDA $02
        ADC #6
        STA D12L
        LDA $03
        ADC #0
        STA D12H
        RTS

; ---- ptr12: $02/$03 = D12 + STEP*12  (A,X,Y clobbered) -----------------------
ptr12:  LDA D12L
        STA $02
        LDA D12H
        STA $03
        LDX STEP
        BEQ p12x
p12l:   CLC
        LDA $02
        ADC #12
        STA $02
        BCC p12c
        INC $03
p12c:   DEX
        BNE p12l
p12x:   RTS

ptr8:   LDA D8L
        STA $02
        LDA D8H
        STA $03
        LDX STEP
        BEQ p8x
p8l:    CLC
        LDA $02
        ADC #8
        STA $02
        BCC p8c
        INC $03
p8c:    DEX
        BNE p8l
p8x:    RTS

; ---- tilepair: draw the 12-px column at ($02) into pool pair PIDX ------------------
;      PAD: 0 = background below the text, 1 = box border below the text
;      NTL/NTH = nametable address of the top tile.  carry set = buffer full
tilepair:
        LDY #0
tp_top: LDA #$FF
        STA STAGE,Y
        LDA ($02),Y
        EOR #$FF
        STA STAGE+8,Y
        INY
        CPY #8
        BNE tp_top
        LDX #0
        LDY #8
tp_bot: LDA #$FF
        STA STAGE+16,X
        LDA ($02),Y
        EOR #$FF
        STA STAGE+24,X
        INX
        INY
        CPX #4
        BNE tp_bot
        LDA PAD
        BNE tp_b1
        LDA #$FF
        LDX #3
tp_b0:  STA STAGE+20,X
        STA STAGE+28,X
        DEX
        BPL tp_b0
        BMI tp_pat
tp_b1:  LDX #3
tp_b1l: LDA B1P0,X
        STA STAGE+20,X
        LDA B1P1,X
        STA STAGE+28,X
        DEX
        BPL tp_b1l
tp_pat: LDX PIDX
        LDA POOL,X
        STA TT
        STA NTB
        CLC
        ADC #1
        STA NTB+1
        LDA TT
        LSR A
        LSR A
        LSR A
        LSR A
        STA $05
        LDA TT
        ASL A
        ASL A
        ASL A
        ASL A
        STA $04
        LDA #<STAGE
        STA $02
        LDA #>STAGE
        STA $03
        LDY #32
        JSR ENQ
        BCS tp_f
        LDA #<NTB
        STA $02
        LDA #>NTB
        STA $03
        LDA NTH
        STA $05
        LDA NTL
        STA $04
        LDY #$82
        JSR ENQ
tp_f:   RTS

; ---- draw_step: dialog column STEP on line LINE -------------------------------------
draw_step:
        LDA STEP
        CMP N12
        BCC ds_ok
        CLC
        RTS
ds_ok:  JSR ptr12
        LDA LINE
        STA PAD
        BEQ ds_p0
        LDA #17
ds_p0:  CLC
        ADC STEP
        STA PIDX
        LDA #$21
        STA NTH
        LDA LINE
        BEQ ds_n0
        LDA #$40
ds_n0:  CLC
        ADC #$47                    ; $47 (line 0) / $87 (line 1)  = text starts at column 7
        ADC STEP
        STA NTL
        JMP tilepair

; ---- draw_big: banner column STEP (12-px, address = SAV + STEP) ------------------------
draw_big:
        LDA STEP
        CMP N12
        BCC db_ok
        CLC
        RTS
db_ok:  JSR ptr12
        LDA #0
        STA PAD
        LDA STEP
        STA PIDX
        CLC
        LDA SAV04
        ADC STEP
        STA NTL
        LDA SAV05
        ADC #0
        STA NTH
        JMP tilepair

; ---- draw_small: 8-px strip column STEP -----------------------------------------------------
draw_small:
        LDA STEP
        CMP N8
        BCC dsm_ok
        CLC
        RTS
dsm_ok: CMP SMAX
        BCC dsm_ok2
        CLC
        RTS
dsm_ok2:
        JSR ptr8
        LDY #0
dsm_l:  LDA #$FF
        STA STAGE,Y
        LDA ($02),Y
        EOR #$FF
        STA STAGE+8,Y
        INY
        CPY #8
        BNE dsm_l
        LDA SBASE
        CLC
        ADC STEP
        TAX
        LDA SPOOL,X
        STA TT
        STA NTB
        LSR A
        LSR A
        LSR A
        LSR A
        STA $05
        LDA TT
        ASL A
        ASL A
        ASL A
        ASL A
        STA $04
        LDA #<STAGE
        STA $02
        LDA #>STAGE
        STA $03
        LDY #16
        JSR ENQ
        BCS dsm_f
        LDX #0                      ; address = SAV + signed DX8 + STEP
        LDA DX8
        BPL dsm_p
        LDX #$FF
dsm_p:  CLC
        LDA SAV04
        ADC DX8
        STA NTL
        TXA
        ADC SAV05
        STA NTH
        CLC
        LDA NTL
        ADC STEP
        STA NTL
        BCC dsm_n
        INC NTH
dsm_n:  LDA #<NTB
        STA $02
        LDA #>NTB
        STA $03
        LDA NTH
        STA $05
        LDA NTL
        STA $04
        LDY #1
        JSR ENQ
dsm_f:  RTS

; ------------------------------------------------------------------ mode 0
do_init:
        JSR classify
        LDA CLS
        CMP #$FF
        BNE di_c
        JMP ret_ok
di_c:   JSR setrow
        LDA FLG
        BPL di_nb
        LDA CLS                     ; blank row: wipe a dialog line
        CMP #2
        BCS ret_ok0
        JSR clear_line
        BCC ret_ok0
        JMP di_fail0
ret_ok0:JMP ret_ok
di_nb:  LDA CLS                     ; choose the bitmap kind / count
        CMP #2
        BEQ di_small
        CMP #3
        BEQ di_ban
        LDA FLG
        AND #1
        BEQ ret_ok0
        LDA $53                     ; dialog: engine step count (1 when typewriter)
        STA CNT
        LDA #0
        STA PAD
        BEQ di_go
di_ban: LDA FLG
        AND #1
        BEQ ret_ok0
        LDA N12
        STA CNT
        BNE di_go
di_small:
        LDA FLG
        AND #2
        BEQ ret_ok0
        LDA N8
        STA CNT
di_go:  LDA PROGR                   ; resume only if PROG belongs to this row
        CMP $51
        BEQ di_res
        LDA #0
        STA PROG
di_res: LDA $51
        STA PROGR
        LDA PROG
        STA STEP
di_loop:
        LDA STEP
        CMP CNT
        BCS di_done
        LDA CLS
        CMP #2
        BEQ di_ds
        CMP #3
        BEQ di_db
        JSR draw_step
        JMP di_chk
di_ds:  JSR draw_small
        JMP di_chk
di_db:  JSR draw_big
di_chk: BCS di_fail
        INC STEP
        BNE di_loop
di_done:
        LDA #0
        STA PROG
ret_ok: LDA #0
        STA RET
        RTS
di_fail:
        LDA STEP
        STA PROG
di_fail0:
        LDA #1
        STA RET
        RTS

; ------------------------------------------------------------------ mode 1
do_step:
        JSR classify
        LDA CLS
        CMP #2
        BCS ret_ok
        JSR setrow
        LDA $54
        STA STEP
        JSR draw_step
        BCS st_fail
        JMP ret_ok
st_fail:
        LDA #1
        STA RET
        RTS

; ------------------------------------------------------------------ mode 2
do_blink:
        JSR classify
        LDA CLS
        CMP #2
        BCS ret_ok
        LDA #$9C
        STA NTB
        LDA LINE
        BEQ bl_0
        LDA #$9E
        STA NTB+1
        BNE bl_g
bl_0:   LDA #$9C
        STA NTB+1
bl_g:   LDA #<NTB
        STA $02
        LDA #>NTB
        STA $03
        LDA #$21
        STA $05
        LDA LINE
        BEQ bl_n0
        LDA #$40
bl_n0:  CLC
        ADC #$47
        ADC $54
        STA $04
        LDY #$82
        JSR ENQ
        BCS st_fail
        JMP ret_ok

; ------------------------------------------------------------------ mode 3
do_clear:
        JSR classify
        LDA CLS
        CMP #2
        BCS ret_ok
        JSR clear_line
        JMP ret_ok

; clear_line: LINE already set. Writes 20 blank tiles on both tile rows of the line
clear_line:
        LDA #<C9C
        STA $02
        LDA #>C9C
        STA $03
        LDA #$21
        STA $05
        LDA LINE
        BNE cl_l1
        LDA #$46
        STA $04
        LDY #20
        JSR ENQ
        BCS cl_f
        LDA #$66
        STA $04
        LDY #20
        JSR ENQ
        RTS
cl_l1:  LDA #$86
        STA $04
        LDY #20
        JSR ENQ
        BCS cl_f
        LDA #<C9E
        STA $02
        LDA #>C9E
        STA $03
        LDA #$A6
        STA $04
        LDY #20
        JSR ENQ
cl_f:   RTS


; ------------------------------------------------------------------ mode 4 : title text
; Uploads the 26 pattern tiles + 2 nametable rows of the Vietnamese title line (data in bank 8 at TDATA).
TPOS   = $04F8
TCNT   = $04AB
TID    = TDATA                      ; 26 tile ids
TNT0   = TDATA+26                   ; 13 bytes  (row 25)
TNT1   = TDATA+39                   ; 13 bytes  (row 26)
TPAT   = TDATA+52                   ; 26*16 bytes
do_title:
        LDA #3
        STA TCNT
dt_l:   LDX TPOS
        CPX #26
        BCS dt_nt
        TXA                         ; source = TPAT + X*16
        LSR A
        LSR A
        LSR A
        LSR A
        STA $03
        TXA
        ASL A
        ASL A
        ASL A
        ASL A
        CLC
        ADC #<TPAT
        STA $02
        LDA $03
        ADC #>TPAT
        STA $03
        LDA TID,X                   ; PPU address = tile*16
        LSR A
        LSR A
        LSR A
        LSR A
        STA $05
        LDA TID,X
        ASL A
        ASL A
        ASL A
        ASL A
        STA $04
        LDY #16
        JSR ENQ
        BCS dt_more
        INC TPOS
        DEC TCNT
        BNE dt_l
        BEQ dt_more
dt_nt:  CPX #26
        BNE dt_n1
        LDA #<TNT0
        STA $02
        LDA #>TNT0
        STA $03
        LDA #$29
        BNE dt_nw
dt_n1:  CPX #27
        BNE dt_end
        LDA #<TNT1
        STA $02
        LDA #>TNT1
        STA $03
        LDA #$49
dt_nw:  STA $04
        LDA #$23
        STA $05
        LDY #13
        JSR ENQ
        BCS dt_more
        INC TPOS
        JMP dt_l
dt_end: LDA #0
        STA RET
        RTS
dt_more:
        LDA #1
        STA RET
        RTS

; ---- constants ----
B1P0:   .db $00,$FF,$00,$FF         ; bottom border rows 4-7, plane 0
B1P1:   .db $FF,$00,$FF,$FF         ;                          plane 1
C9C:    .ds 20,$9C
C9E:    .ds 20,$9E
; status-screen strip slots: addr lo, addr hi, first pool tile, max columns
SLOTS:  .db $61,$20,0,3,   $6D,$20,3,3,   $77,$20,6,3
        .db $65,$21,9,4,   $75,$21,13,4
        .db $B5,$21,17,5,  $35,$22,22,5,  $B5,$22,27,5,  $35,$23,32,5
        .db $C5,$21,37,5,  $05,$22,42,5,  $45,$22,47,5,  $85,$22,52,5,  $C5,$22,57,5,  $05,$23,62,5
        .db 0,0,0,0
POOL:   .db $B0,$B2,$BF,$C1,$C3,$C5,$C7,$C9,$CC,$CE,$D0,$D2,$D4,$D6,$D8,$DA,$DC
        .db $DE,$E0,$E2,$E4,$E6,$E8,$EA,$EC,$EE,$F0,$F2,$F4,$F6,$F8,$FA,$FC,$FE
SPOOL:  .db $B0,$B1,$B2,$B3,$BF,$C0,$C1,$C2,$C3,$C4,$C5,$C6,$C7,$C8,$C9,$CA,$CC,$CD,$CE,$CF,$D0,$D1,$D2,$D3,$D4,$D5,$D6,$D7,$D8,$D9,$DA,$DB,$DC,$DD
        .db $DE,$DF,$E0,$E1,$E2,$E3,$E4,$E5,$E6,$E7,$E8,$E9,$EA,$EB,$EC,$ED,$EE,$EF,$F0,$F1,$F2,$F3,$F4,$F5,$F6,$F7,$F8,$F9,$FA,$FB,$FC,$FD,$FE,$FF


TDATA   = $B800
        .org $8600
ROWTAB: .ds 64,$00                  ; 32 row pointers (filled by the builder)
```

## `tools/build_rom.py`

```python
#!/usr/bin/env python3
"""Build the Vietnamese ROM of Saiyuuki World.
usage: build_rom.py [out.nes]
Inputs : rom/original.nes, src/window.asm, src/tramp.asm, tools/viet_font.py, tools/vi_script.py
"""
import sys, os, struct
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from asm6502 import assemble
import viet_font as vf
import importlib, vi_script
importlib.reload(vi_script)

ORIG = open(ROOT + '/rom/original.nes', 'rb').read()
OUT = sys.argv[1] if len(sys.argv) > 1 else ROOT + '/build/saiyuuki_vi.nes'
BANK = 0x4000
prg = [bytearray(ORIG[16 + i * BANK:16 + (i + 1) * BANK]) for i in range(8)]
N = 213

# ---------------------------------------------------------------- parse original rows
b3 = prg[3]
w16 = lambda a: b3[a - 0x8000] | b3[a - 0x8000 + 1] << 8
orig = []
for i in range(N):
    p = w16(0x9E77 + 2 * i); fl = b3[p - 0x8000]; ln = b3[p - 0x8000 + 1]; q = p + 2; addr = None
    if fl & 0x10:
        addr = w16(q); q += 2
    orig.append(dict(i=i, flags=fl, len=ln, addr=addr, data=bytes(b3[q - 0x8000:q - 0x8000 + ln])))

# ---------------------------------------------------------------- code
def asm_file(name, org, syms=None):
    return assemble(open(ROOT + '/src/' + name).read(), org, syms)
wsegs, wlab = asm_file('window.asm', 0x8000)
assert max(a + len(b) for a, b in wsegs if a < 0x8600) <= 0x8600, 'window code overlaps ROWTAB'
tsegs, tlab = asm_file('tramp.asm', 0xC02A)

# ---------------------------------------------------------------- row bitmaps
DOWN = vf.render('▼')
def to_columns(bm, ncols):
    W = len(bm[0]) if bm and bm[0] else 0
    cols = []
    for c in range(ncols):
        col = bytearray(12)
        for y in range(12):
            v = 0
            for x in range(8):
                px = c * 8 + x
                if px < W and bm[y][px]:
                    v |= 0x80 >> x
            col[y] = v
        cols.append(bytes(col))
    return cols

PASS = set(range(154, 179)) | {186}   # price digit rows + yen kanji keep the original drawing
import viet_font8 as vf8
def to_columns8(bm, ncols):
    W = len(bm[0]) if bm and bm[0] else 0
    cols = []
    for c in range(ncols):
        col = bytearray(8)
        for y in range(8):
            v = 0
            for x in range(8):
                px = c * 8 + x
                if px < W and bm[y][px]:
                    v |= 0x80 >> x
            col[y] = v
        cols.append(bytes(col))
    return cols
SMALLMAX = {183: 3, 187: 3, 188: 3, 184: 4, 185: 4}   # status-screen slot widths (columns); items: 5

rowinfo = {}      # i -> dict(flags, n12, n8, dx8, d12, d8)
report = []
for r in orig:
    i = r['i']
    if i in PASS:
        continue
    text = vi_script.TEXT.get(i, '')
    small = vi_script.SMALL.get(i)
    wait = bool(r['data']) and r['data'][-1] == 0xB3
    info = dict(flags=0, n12=0, n8=0, dx8=0, d12=b'', d8=b'')
    if small is not None:
        stext, dx = small
        bm8 = vf8.render(stext); W8 = len(bm8[0]); n8 = (W8 + 7) // 8
        mx = SMALLMAX.get(i, 5)
        if n8 > mx:
            report.append('row %d small too wide: %d cols > %d  %r' % (i, n8, mx, stext))
        info.update(flags=info['flags'] | 2, n8=n8, dx8=dx & 0xFF, d8=b''.join(to_columns8(bm8, n8)))
    if text.strip():
        bm = vf.render(text); W = len(bm[0])
        maxw = (224 if r['flags'] & 0x10 else 136) - (8 if wait else 0)
        if W > maxw:
            report.append('row %d too wide: %d > %d  %r' % (i, W, maxw, text))
        nt = (W + 7) // 8
        if wait:
            wa = len(DOWN[0])
            full = [bm[y] + [0] * (nt * 8 - W) + [0] + DOWN[y] + [0] * (8 - 1 - wa) for y in range(12)]
            ncols = nt + 1
        else:
            full = bm; ncols = nt
        info.update(flags=info['flags'] | 1, n12=ncols, d12=b''.join(to_columns(full, ncols)))
    elif small is None:
        info['flags'] = 0x80                 # blank row (wipes the line)
    rowinfo[i] = info
if report:
    print('\n'.join(report))
    if '--strict' in sys.argv: sys.exit(1)

def row_len(i):
    inf = rowinfo[i]
    return max(1, inf['n12'] or inf['n8'])
def row_wait(i, r):
    return bool(r['data']) and r['data'][-1] == 0xB3 and rowinfo[i]['n12'] > 0

# ---------------------------------------------------------------- bank 3 records
# overlap packing: non-wait records only carry their header, data bytes overlap later records
ptrs = [0] * N
BASE = 0xA021; END = 0xAB0B
full = set()
while True:
    recs = []
    for r in orig:
        i = r['i']
        if i in PASS:
            body = bytes([r['flags'], r['len']]) + (struct.pack('<H', r['addr']) if r['addr'] else b'') + r['data']
            recs.append((i, body, None)); continue
        ln = row_len(i)
        wait = row_wait(i, r)
        h = bytes([r['flags'], ln]) + (struct.pack('<H', r['addr']) if r['addr'] else b'')
        if wait:
            recs.append((i, h + bytes(ln - 1) + b'\xB3', 'wait'))
        elif i in full:
            recs.append((i, h + bytes(ln), None))
        else:
            recs.append((i, h, ln))
    stream = bytearray()
    for i, body, extra in recs:
        ptrs[i] = BASE + len(stream)
        stream += body
    stream += bytes(40)
    bad = [i for i, body, extra in recs if extra not in (None, 'wait')
           and stream[ptrs[i] - BASE + len(body) + extra - 1] == 0xB3]
    if not bad:
        break
    full.update(bad)
if BASE + len(stream) > END:
    raise SystemExit('bank 3 records overflow: %d bytes' % (BASE + len(stream) - END))
b3[BASE - 0x8000:BASE - 0x8000 + len(stream)] = stream
for i in range(N):
    b3[0x9E77 - 0x8000 + 2 * i] = ptrs[i] & 255
    b3[0x9E77 - 0x8000 + 2 * i + 1] = ptrs[i] >> 8

# ---------------------------------------------------------------- engine hooks (bank 3)
def patch_jsr(bank, site, target):
    off = site - 0x8000
    assert prg[bank][off] == 0x20 and prg[bank][off + 1] == 0x76 and prg[bank][off + 2] == 0xFF, hex(site)
    prg[bank][off + 1] = target & 255; prg[bank][off + 2] = target >> 8
patch_jsr(3, 0xAB96, tlab['T_INIT'])
patch_jsr(3, 0xAC1B, tlab['T_STEP'])
patch_jsr(3, 0xACA3, tlab['T_BLINK'])
patch_jsr(3, 0xACD9, tlab['T_CLEAR'])
patch_jsr(3, 0xACE7, tlab['T_CLEAR'])
_o = 0x81C6 - 0x8000
assert prg[6][_o:_o + 3] == bytes([0x20, 0xA2, 0xC4]), 'bank 6 main-loop call not found'
prg[6][_o + 1] = tlab['T_MAIN'] & 255; prg[6][_o + 2] = tlab['T_MAIN'] >> 8

# ---------------------------------------------------------------- title screen line
TITLE_TEXT = vi_script.TITLE
FREE_TILES = [1, 2, 3, 172, 173, 174, 175] + list(range(236, 256))     # BG tiles unused by the title nametable
TCOLS = 13
tbm = vf.render(TITLE_TEXT); TW = len(tbm[0])
assert TW <= TCOLS * 8 - 2, 'title text too wide: %d' % TW
# 16-row cell: glyph rows at y=2..13, 1-px black outline (colour 3), white ink (colour 1)
cell = [[0] * (TCOLS * 8) for _ in range(16)]
ox = (TCOLS * 8 - TW) // 2
ink = set((ox + x, 2 + y) for y in range(12) for x in range(TW) if tbm[y][x])
for (x, y) in ink:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < TCOLS * 8 and 0 <= yy < 16 and (xx, yy) not in ink:
                cell[yy][xx] = 3
for (x, y) in ink: cell[y][x] = 1
tid = []; tnt0 = []; tnt1 = []; tpat = bytearray()
for c in range(TCOLS):
    for half in range(2):
        t = FREE_TILES[2 * c + half]; tid.append(t)
        p0 = bytearray(8); p1 = bytearray(8)
        for yy in range(8):
            for xx in range(8):
                col = cell[half * 8 + yy][c * 8 + xx]
                if col & 1: p0[yy] |= 0x80 >> xx
                if col & 2: p1[yy] |= 0x80 >> xx
        tpat += p0 + p1
    tnt0.append(tid[-2]); tnt1.append(tid[-1])
TITLE_DATA = bytes(tid) + bytes(tnt0) + bytes(tnt1) + bytes(tpat)

# ---------------------------------------------------------------- fixed bank
fixed = bytearray(prg[7])
for a, b in tsegs:
    o = a - 0xC000
    assert all(x == 0xFF for x in fixed[o:o + len(b)]), 'fixed space not free'
    fixed[o:o + len(b)] = b
for site in (0xC15B, 0xC164, 0xFCA6, 0xFCBA):
    o = site - 0xC000
    assert fixed[o:o + 3] == bytes([0x9D, 0x5F, 0xFF]), hex(site)
    fixed[o + 1] = 0x2A; fixed[o + 2] = 0xC0
prg[7] = fixed

# ---------------------------------------------------------------- data banks 8..14
banks = []
for bi in range(7):
    bank = bytearray(b'\xFF' * BANK)
    for a, b in wsegs:
        bank[a - 0x8000:a - 0x8000 + len(b)] = b
    bank[0] = 8 + bi
    p = 0x8640
    for k in range(32):
        i = bi * 32 + k
        inf = rowinfo.get(i)
        if inf is None:
            inf = dict(flags=0x80, n12=0, n8=0, dx8=0, d12=b'', d8=b'')
        ptr = p
        off8 = 6 + len(inf['d12'])
        rec = bytes([inf['flags'], inf['n12'], inf['n8'], inf['dx8'], off8 & 255, off8 >> 8]) + inf['d12'] + inf['d8']
        bank[p - 0x8000:p - 0x8000 + len(rec)] = rec
        p += len(rec)
        assert p < 0xC000, 'bank %d overflow' % (8 + bi)
        bank[0x8600 - 0x8000 + 2 * k] = ptr & 255
        bank[0x8600 - 0x8000 + 2 * k + 1] = ptr >> 8
    if bi == 0:
        assert p <= 0xB800, 'bank 8 data collides with title data'
        bank[0xB800 - 0x8000:0xB800 - 0x8000 + len(TITLE_DATA)] = TITLE_DATA
    banks.append(bank)

allbanks = [bytearray(x) for x in prg[:7]] + [bytearray(prg[7])] + banks + [bytearray(prg[7])]
assert len(allbanks) == 16
hdr = bytearray(ORIG[:16]); hdr[4] = 16
rom = bytes(hdr) + b''.join(bytes(b) for b in allbanks)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(rom)
print('wrote', OUT, len(rom), 'bytes; bank3 records end $%04X' % (BASE + len(stream)))
```

## `tools/make_ips.py`

```python
#!/usr/bin/env python3
"""Create an IPS patch (original.nes -> patched.nes). The patched ROM is larger (256 KB); IPS handles that
by simply adding records past the original end.  usage: make_ips.py original.nes patched.nes out.ips"""
import sys
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
out = bytearray(b'PATCH'); i = 0; n = len(b)
def rec(off, data):
    if off == 0x454F46: raise SystemExit('offset collides with EOF marker')
    out.extend(off.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data)
while i < n:
    if i < len(a) and a[i] == b[i]: i += 1; continue
    j = i
    while j < n and j - i < 0xFFFF and (j >= len(a) or a[j] != b[j] or (j + 1 < n and j + 1 < len(a) and a[j + 1] != b[j + 1] and False)): j += 1
    # extend over short equal gaps (<8) to save record overhead
    k = j
    while k < n and k - i < 0xFFFF:
        g = k
        while g < n and g < len(a) and a[g] == b[g] and g - k < 8: g += 1
        if g < n and g - k < 8 and (g >= len(a) or a[g] != b[g]): k = g; 
        else: break
        while k < n and (k >= len(a) or a[k] != b[k]) and k - i < 0xFFFF: k += 1
    j = max(j, k)
    if i == 0x454F46: i -= 1
    rec(i, b[i:j]); i = j
out.extend(b'EOF')
if len(b) > len(a): out.extend(len(b).to_bytes(3, 'big'))
open(sys.argv[3], 'wb').write(out); print('IPS', len(out), 'bytes')
```
