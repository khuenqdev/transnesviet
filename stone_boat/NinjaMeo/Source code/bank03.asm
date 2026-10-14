bank $03
define	save_bank $4c
define save_a	$4d

//FIX FRAME

org $8de3
	db $4c
org $8de9
	db $4c
org $8dee
	db $4c
org $8DBE
	db $4c
org $8dc3
	db $4c, $4c, $4c, $4c, $4c, $4c, $4c
org $8dce
	db $4c
org $8DDC
	db $4c
org $8df0
	db $4c
org $8DF7
	db $4c
org $8e01
	db $4c
org $8E0B
	db $4c
org $8e15
	db $4c
org $8e1f
	db $4c
org $8e28
	db $4c
org $8e2e
	db $4c, $4c
org $8e34
	db $4c, $4c
org $8e3a
	db $4c
org $8e41
	db $4c
org $8e4b
	db $4c
org $8e55
	db $4c
org $8e5f
	db $4c
org $8e6d
	db $4c
org $8e96
	db $4c
org $8eaa
	db $4c
org $8eb4
	db $4c, $4c, $4c, $4c, $b6, $b2, $4c, $4c, $4c, $4c, $4c
org $8ec3
	db $4c
	
//################
// PASSWORD FRAME
//################
org $8634
	lda #$4c
	
org $8F88
	db $4C
org $8F96
	db $4C
org $8FA4
	db $4C
org $8FB2
	db $4C
org $8FC0
	db $4C
org $8FCE
	db $4C
org $8FDC
	db $4C
org $8FEA
	db $4C
	
org $9010
	db $01
	
//####################
// CHAR SELEC FRAME
//####################
org $8DA8
	db $01
	dw $2021
	db $B0
	
	db $FE
	db $1E
	dw $2121
	db $B1
	
	db $02
	dw $3F21
	db $B4, $B2
	
	db $FE
	db $11
	dw $4121
	db $4C
		
	db $05
	dw $5221
	db $53, $4C, $4C, $4C, $53
	
	db $FE
	db $08
	dw $5721
	db $4C
	
	db $02
	dw $5F21
	db $B6, $B2
	
	db $FE
	db $0A
	dw $6121
	db $4C
	
	db $0D
	dw $6B21
	db $03, $2D, $34, $33, $4C, $33, $2D, $26, $33, $4C, $3B, $26, $39

	db $FE
	db $08
	dw $7821
	db $4C
	
	db $02
	dw $7F21
	db $B6, $B2
	
	db $FE
	db $06
	dw $8121
	db $D3
	
	db $FE
	db $06
	dw $8721
	db $4C
	
	db $01
	dw $8D21
	db $71
	
	db $FE
	db $08
	dw $8E21
	db $4C
	
	db $01
	dw $9621
	db $71
	
	db $FE
	db $08
	dw $9721
	db $4C

	db $02
	dw $9F21
	db $B6, $B2
	
	db $FE
	db $06
	dw $A121
	db $D3
	
	db $FE
	db $18
	dw $A721
	db $4C
	
	db $02
	dw $BF21
	db $B6, $B2

	db $FE
	db $06
	dw $C121
	db $D3
	
	db $1A
	dw $C721
	db $4C
	db $19, $26, $39, $39, $26, $37, $41 //yattaro
	db $4C
	db $13, $3A, $30, $26, $38, $2E
	db $4C
	db $10, $3A, $37, $3A, $37, $3A, $33 //pururun
	db $4C, $B6, $B2
	
	db $FE
	db $06
	dw $E121
	db $D3
	
	db $FE
	db $18
	dw $E721
	db $4C
	
	db $02
	dw $FF21
	db $B6, $B2
	
	db $FE
	db $06
	dw $0122
	db $D3	
	
	db $FE
	db $18
	dw $0722
	db $4C
	
	db $02
	dw $1F22
	db $B6, $B2	

	db $FE
	db $1E
	dw $2122
	db $4C
	
	db $02
	dw $3F22
	db $B6, $B8		
	
	db $FE
	db $1E
	dw $4122
	db $B9
	
	db $01
	dw $5F22
	db $BC
	
	db $00

org $8F63		//attribute
	db $AA  //or $95
org $8F68
	db $65

org $83E5
	db $58	//cursor pos
	db $90
	db $CD
org $83AB
	ldx #$12		//oam pos
	
//#####################
//  TITLE SCREEN
//######################
org $8269
//	LDA #$7C	//title chr bank
	lda #$82
	STA $23
//	LDA #$7E
//	lda #$84
//	STA $24
//	LDA #$0B
//	STA $28
//	LDA #$00
//	JSR $880D
	LDA #$00
	sta {save_a}
	lda #$11
	sta {save_bank}
	jmp new_title
	nop #2
original_title:
	LDA #$03
	LDX #$5c
	LDY #$93	//cursor pos
//	JSR $8714
	jsr write_oam
	LDA #$09
	JSR $86CF
	LDA #$25
	JSR $8875
	LDX #$0D
	LDY #$FE
	JSR $86C8
	DEY
	BNE +
	DEX
	BNE +
	LDA #$02
	JSR $8875
	LDX #$5A
-
	JSR $86C8
	LDA $1A
	AND #$10
	BNE $1A
	DEX
	BNE -
	TXA
	RTS
+
	LDA $1A


org $8A05
//original title data

org $9090	//title bkg, OAM pallet
	db $21, $25, $30, $3B
	db $21, $38, $35, $15
	db $21, $0F, $36, $30
	db $21, $0F, $31, $30

	db $11, $0F, $25, $30
	db $11, $0F, $36, $30
	db $11, $0F, $22, $30
	db $11, $0F, $28, $30
	
org $890a	//pawn cursor
	db $ea
	
//#################
// TITLE SCREE PUSH STAR
//#################
org $62cd
	cmp #$9d //cursor pos
	
//##############
// Password text
//#############

org $69ef
	dw pasda
	dw psw_section
	dw sima_nagasi
	
	
	
table "ansi.tbl"
org $8a05
psw_section:
	db $17
	db $21, $64
	db "Mau nhap mat ma cho ta!"
	db $17
	db $21, $44
	db $4c, $4c, $4c, $4c, $4c, $4c, $53, $4c, $4c, $4c, $53, $4c, $4c, $4c, $52, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c
	db $05
	db $21, $8a
	db $71, $4c, $4c, $4c, $71
	
	db $0b
	db $23, $d1
	db $a5, $a5, $a5, $a5, $a5, $a5, $55, $55, $55, $aa, $59
	
	db $00

sima_nagasi:
	db $17
	db $21, $64
	db $1b
	db "ay ten nay ra "
	db $40
	db "ao!    "
	
	db $17
	db $21, $44
	db $4c, $50, $4c, $4c, $4c, $53, $4c, $4c, $4c, $50, $4c, $4c, $4c, $4c, $4c, $4c, $51, $4c, $4c, $4c, $4c, $4c, $4c
	db $17
	db $21, $84
	db $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c, $4c
	
	db $00
	
table "ansi.tbl"	
pasda:
	db $08
	db $21, $4D
	db $53, "   ", $52, "  ", $50
	db $01
	db $21, $8D
	db $71
	
	db $01
	db $2b, $db
	db $5a
	
	db $0A
	db $21, $6C
	db "Mat ma ne!"
	db $00
	
	
//###############
// Game over
//##############
org $69e9
//	dw game_over
	
org $853B
	lda #$11
	sta {save_bank}
	jmp new_title
original_go:		//$8542
	JSR $86CF
	


org $8547
	ldx #$70  //cursor pos
org $857b
	eor #$B0	//cursor range