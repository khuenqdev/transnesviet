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
