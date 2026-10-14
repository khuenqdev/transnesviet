bank $1F
define txt_spd	$0438
define pause		$0437
define line			$043D
define text_trigger $90
define sitaten			$91
define text_counter $92
define	buffer1 $93
define stage		$5D
define	save_bank $4c
define save_a	$4d
define home	$0190

//##################
// NMI
//#################
org $1FCCD
	PHA
	TXA
	PHA
	TYA
	PHA
	LDA #$00
	STA $2003 //oam adr
	LDA #$02
	STA $4014 //oam dma
	LDA $1D
	STA $2001 
	LDA $1F
	BEQ _fd27 //no write
	LDY #$00
_fce7:
	LDA $03A0,y
	BEQ _fd16
	TAX
	BPL _fcf6
	AND #$7F
	TAX
	//LDA #$0C
	//BNE _fcc8	
	jmp new
	nop
_fcf6:
	LDA #$08
_fcc8:
	STA $2000
	INY
	LDA $03A0,y
	STA $2006
	INY
	LDA $03A0,y
	STA $2006
	INY
_fd0a:
	LDA $03A0,y
	STA $2007
	INY
	DEX
	BNE _fd0a
	BEQ  _fce7	
_fd16:
	STA $1F
	STA $21
	LDA $2002
	LDA #$3F
	STA $2006
	LDA #$00
	STA $2006
_fd27:
	STA $2006
	STA $2006
	LDA $1C
	STA $2000
	LDA $2002
	LDA $30
	STA $2005 //scroll
	LDA $34
	STA $2005
	LDA $20
	BEQ _fd4c //upper vram
	STA $C000
	STA $C001
	STA $E001 //disable irq
_fd4c:
	LDA #$00
	STA $066E
	LDA $067D
	STA $0683
	LDY #$05
	LDX #$05
_fd5b:
	STY $8000 //change bank
	LDA $23,x
	STA $8001
	DEY
	DEX
	BPL _fd5b
	LDY #$04
	LDA $16
_fd6b:
	STA $10
	LDA #$01
	STA $4016 //pad
	LDA #$00
	STA $4016
	LDX #$08
_fd79:
	LDA $4016
	LSR
	ROL $11
	AND #$01
	ORA $11
	STA $11
	DEX
	BNE _fd79
	CMP $10
	BEQ _fd8f
	DEY
	BNE _fd6b
_fd8f:
	LDA $16
	STA $18
	LDA $11
	EOR $16
	AND $11
	STA $1A
	LDA $11
	STA $16
	LDY #$04
	LDA $17
_fda3:
	STA $10
	LDA #$01
	STA $4016
	LDA #$00
	STA $4016
	LDX #$08
_fdb1:
	LDA $4017
	LSR
	ROL $11
	AND #$01
	ORA $11
	STA $11
	DEX
	BNE _fdb1
	CMP $10
	BEQ _fdc7
	DEY
	BNE _fda3
_fdc7:
	LDA $17
	STA $19
	LDA $11
	EOR $17
	AND $11
	STA $1B
	LDA $11
	STA $17
	INC $35
	JSR $FC9E
	LDA #$00
	STA $38
	JMP $FDEF
_fde3:
	BIT $17
	BMI _fdf3
	BVC _fdef
	LDA $35
	AND #$07
	BNE _fdf3
_fdef:
	LDA #$80
	STA $1E
_fdf3:
	PLA
	TAY
	PLA
	TAX
	PLA
	RTI
	
org $3ff10
new:
	lda #$0C
	sta $2000
	iny
	LDA $03A0,y
	STA $2006
	INY
	LDA $03A0,y
	STA $2006
	INY
-
	LDA $03A0,y
	STA $2007
	INY
	DEX
	BNE -
+
	lda {text_trigger}
	beq +
	lda {sitaten}
	sta $2007
	lda #$00
	sta {text_trigger}
	lda #$4c
	sta {sitaten}
+	
	jmp _fce7
	
check_bank:
	lda {stage}
	cmp #$06
	bcs +
	lda #$0e
	JSR $8B9E
	rts
+
	cmp #$0a
	bcs +
	lda #$0f
	JSR $8B9E
	rts
+
	lda #$10
	JSR $8B9E
	rts
	
cal:
	LDA $3A
	asl #3
	sec
	rts
	
main_name:
	db $19, $26, $39, $39, $26, $37, $41  //yattaro
	db $13, $3A, $30, $26, $38, $2E, $B3 //sukasi
	db $10, $3A, $37, $3A, $37, $3A, $33 //pururun
	
new_title:
	jsr switch_bank
	jmp bank11_code
	
switch_bank:
	lda #$07
	sta $8000
	lda {save_bank}
	sta $8001
	rts
	
org $3ff06
back_to_original_title:
	jsr switch_bank
	lda {save_a}
	jmp ({home})
	

	