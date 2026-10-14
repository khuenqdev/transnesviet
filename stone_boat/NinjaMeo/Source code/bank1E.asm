bank $1E

define	buffer1 $93

define	save_bank $4c
define save_a	$4d


//#####################
// FRAME NAME
//####################
org $3CD69
//	lda #$e9  //pos
	
//LOAD NAME
org $3CD69
	lda #$07
	STA $03A0
	LDA #$26
	STA $03A1
	lda #$e9
	STA $03A2
	LDA $3A //char
	jsr cal
//	ASL #2
//	CLC
	sbc $3A
	TAY	
	LDX #$00
-
	lda main_name,y
	STA $03A3,x
	INY
	INX
	cpx #$07
	BNE -
	lda #$b3
	nop #3
	
//##################
// CURSOR POS
//################
org $3CFAC
	db $3f, $c7
	db $45, $b7
	db $86, $c7
	db $a5, $b7
	db $c5, $c7
	
//##############
// HACK INPUT
//#############
org $D26E
	lda #$13		//7 bytes
	sta {save_bank}
	jmp new_title
	