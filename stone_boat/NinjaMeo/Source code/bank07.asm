bank $07
define txt_spd	$0438
define pause		$0437
define line			$043D
define text_trigger $B0
define sitaten			$B1
define text_counter $B2
define stage		$5D

define	save_bank $4c
define save_a	$4d
define	pos_table	$01D0

//##############
// CONTROL CODE
//#############
//F5= MTE
//F7 = text speed
//F8=<line>
//F9=<clear page>
//FA=<wait>
//FB=<delchar>
//FC=<switch alphabet>
//FE=<stop kuchipaku>
//FD=<kuchipaku>
//FF=<end>

//##########################
// ENDING NAME
//#########################
org $EBD2
	lda #$12
	sta {save_bank}
	jmp new_title
original_ending:	//$8Bd9
	LDA $A039,y
	STA $00
	LDA $A12E,y
	STA $01
sprite_name:		//$8be3
	LDY #$00
	LDX $22
	
org $EC05
	//lda {pos_table},y
	

//#################
// TEXT
//################
org $8C92
	jsr check_bank
//	LDA #$0e	//prg bank 6 mapped to $A000-$BFFF
//	JSR $8B9E //switch bank
	nop #2
	LDA $043C
	CMP #$F5
	BCS a_8d00
	LDA $0438 //text speed
	BNE _8cb0
	LDA $0437 //pause
	BEQ _8cb4
	DEC $0437
	LDA #$09
	STA $0438
_8cb0:
	DEC $0438
	RTS
_8cb4:
	TAY
	jmp newloc
	nop
//	LDA $0439
//	STA $0438
a_8d00:
	jmp _8d00
	
org $8e38
	jmp _8e38

	
org $8B9E
	LDX #$07
	STX $36
	STX $8000	//Select 8 KB PRG ROM bank at $A000-$BFFF
	STA $8001  
	STA $2A
	RTS
	
org $8E3E
	LDX $21
	STA $03A0,x
	LDA $043B
	STA $03A1,x
	LDA $043A
	STA $03A2,x
	RTS	
org $8E50
	LDA ($0C),y
	INC $0C
	BNE +
	INC $0D
+
	RTS
	

	
	
	
	

	
//###################
// KAIWA FRAME
//##################
org $81EC
	JSR $8F6D
	LDA #$00
	STA $00
_81f3:
	JSR $820D
	LDY #$00
-
	LDA ($01),y //$9034
	STA $2007
	INY
	CPY #$0E
	BNE -
	INC $00
	LDA $00
	CMP #$20
	BNE _81f3
	JMP $81BE
_820D:
	LDA #$0C
	STA $2000
	LDA #$22
	STA $2006
	LDX $0000
	STX $2006
	LDA $900A,x
	TAX
	LDA $902A,x
	STA $01
	LDA $902B,x
	STA $02
	RTS

org $900A
	db $02, $04, $06
org $9027
	db $06, $08, $02

//frame background
org $9050
	db $58, $4C, $4C, $4C, $4C, $4C, $4C, $4C, $4C, $4C, $58, $78, $78, $78, $76, $4C
	db $4C, $4C, $4C, $4C, $4C, $4C, $4C, $4C, $76, $78, $78, $78, $59, $4C, $4C, $4C
	db $4C, $4C, $4C, $4C, $4C, $4C, $59, $78, $78, $78, $08, $08, $08, $08, $08, $08
	
//#########
// FIX PAGE CLEAR
//########
org $8E03
	lda #$89
	JSR $8E3E
	inx #3
	ldy #$08
	lda #$4c
-
	STA $03A0,x
	INX
	DEY
	BPL -
	STX $21
	INC $043A
	LDA $043A
	eor #$3f
	

//###########
// TEXT POS
//##########
org $9002
	db $22, $62, $A2, $E2


	
org $8F6D
	SEI
	LDA $1C
	AND #$7F
	STA $2000
	LDA $1D
	AND #$E6
	STA $2001
	RTS
	
	
bank $0E
org $BD1A
db $21, $21, $22, $23, $ff