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
