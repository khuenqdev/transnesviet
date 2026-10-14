bank $0E
//#######################
// TEXT
//######################
org $CB30
	lda #$19
	sta $a000
	jmp new_loc
	

org $077C
	lda #$19
	sta $a000
	jmp init_buffer2
	
org $0bc0
	lda #$19
	sta $a000
	jmp secret_msg
	
//###########
// Opening pallet
//##########
org $122D
	db $20 //white
	
//#############
// CHEAT
//##############
org $1939
	nop #2  //no dec life
	
org $1862  //ammo hack
	lda #$19
	sta $a000
	jmp ammo	
	
org $13A0	//barrier
	LDA $B0,x
	nop #2
	
org $0109
//	lda #$07		//stage

//###############
// area text
//###############
org $CAC5
	PHA
	LDA #$02
	STA $03
	LDA #$01
	JSR $CB22
	PLA
	STA $02
	ASL
	TAX
	LDA $F578,x	//ptr
	STA $00
	LDA $F579,x
	STA $01
	LDX $21
	LDY #$00
-
	LDA ($00),y
	INY
	CMP #$FF
	BEQ _cb28
	CMP #$FE
	BEQ _cb06
	CMP #$FD
	BEQ _cb0a
	STA $0700,x
	LDA $02
	BPL _cb03
	LDA $03
	BNE _cb01
	STA $0700,x
	BEQ +
_cb01:
	DEC $03
+
_cb03:
	INX
	BNE -
_cb06:
	LDA #$FF
	BNE _cb24
_cb0a:
	LDA #$FF
	JSR $CB24
	LDA #$02
	STA $03
	LDA #$01
	JSR $CB24
	BNE -
	LDA #$FF
	BNE _cb22
	LDA #$00
	BEQ _cb22
_cb22:
	LDX $21
_cb24:
	STA $0700,x
	INX
_cb28:
	STX $21
	RTS
	
//##############
// TITLE
//#############
org $C93A
	LDA $C9B1,x
	STA $00
	LDA $C9B2,x
	STA $01
	JSR $F946
	STA $21
	STA $FC
	STA $FD
	LDA $2002
	LDY #$01
	LDA ($00),y
	STA $2006
	DEY
	LDA ($00),y
	STA $2006
	LDA #$02
	LDX #$00
	JSR $C72D
	LDY #$00
	LDA ($00),y
	CMP #$FF
	BEQ _c9ae
	CMP #$7F
	BEQ _c9a4
	TAY
	BPL _c992
	AND #$7F
	STA $02
	LDY #$01
-
	LDA ($00),y
	STA $2007
	CPY $02
	BEQ _c985
	INY
	BNE -
_c985:
	LDA #$01
	CLC
	ADC $02
_c98a:
	LDX #$00
	JSR $C72D
	JMP $C964
_c992:
	LDY #$01
	STA $02
	LDA ($00),y
	LDY $02
-
	STA $2007
	DEY
	BNE -
	LDA #$02
	BNE _c98a
_c9a4:
	LDA #$01
	LDX #$00
	JSR $C72D
	JMP $C94D
_c9ae:
	JMP $F916
dw $CA9B //block ptr
dw title
	
//##################
// FLAMING TITLE
//##################
org $C8C6
	jmp flaming