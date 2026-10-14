bank $11

define	save_bank $4c
define save_a	$4d


org $A000
bank11_code:
	lda $40
	beq +
	jsr write_go
	jmp back_to_original_title
+
	jsr write_screen
	jmp back_to_original_title
	
write_go:
	ldx #$02
	jsr _ryu
	lda #$04
	sta {save_bank}
	lda #$85
	sta $0191
	lda #$42
	sta $0190
	lda #$04
	sta {save_a}
	rts
	
write_screen:
	tax
	lda #$84
	STA $24
	lda #$80  //tile oam bank
	sta $28
	lda #$82
	sta $23
	lda $1c
	and #$7f
	sta $2000
	jsr _ryu
	lda #$7a		//original tile
	sta $0190
	lda #$82
	sta $0191
	lda #$11
	sta {save_bank}
	rts

_ryu:	
	lda frame_pointer,x
	STA $00
	lda frame_pointer+1,x
	STA $01
	BIT $2002
	LDY #$00
begin:
	LDA ($00),y
	BEQ +
	CMP #$FE
	bne normal_write
	jsr read
	LDA ($00),y
	TAX
	jsr read
	LDA ($00),y
	STA $2006
	jsr read
	LDA ($00),y
	STA $2006
	INY
	LDA ($00),y
-
	STA $2007
	DEX
	BNE -
	jsr read
	jmp begin
normal_write:
	STA $03
	jsr read
	LDA ($00),y
	STA $2006
	jsr read
	LDA ($00),y
	STA $2006
-
	jsr read
	LDA ($00),y
	STA $2007
	DEC $03
	BNE -
	jsr read
	jmp begin
read:
	INY
	BNE +
	INC $01
+
	RTS
	
frame_pointer:
	dw title
	dw game_over

table "title.tbl"

title:
	db $06	//start
	db $22, $2D
	db $40, $41, $42, $43, $44, $45
	db $06
	db $22, $4D
	db $50, $51, $52, $53, $54, $55
	
	db $05		//password
	db $22, $6D
	db $46, $47, $48, $49, $4A
	db $05
	db $22, $8D
	db $56, $57, $58, $59, $5A
	
	db $1b
	db $22, $c3
	db $1b
	db "sotsu agency   "
	db $1b
	db "tecmo 1991"
	
	db $04
	db $22, $a5
	db $1d, $00, $00, $1d
	
	db $15
	db $23, $06
	db "ban dich viet van cua"
	
	db $01
	db $22, $e7
	db $4b
	
	db $01
	db $23, $2b
	db $5d
	
	db $01
	db $23, $31
	db $5d
	
	db $09
	db $22, $f1
	db $5b, $00, $00, $00, $5c, $00, $00, $00, $4b
	
	db $15
	db $23, $46
	db "stoneboat studio 2022"
	
	db $10
	db $20, $48
	db $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $2a, $2b, $2c, $2d, $2e, $2f //sentai
	db $10
	db $20, $68
	db $30, $31, $32, $33, $34, $35, $36, $37, $38, $39, $3a, $3b, $3c, $3d, $3e, $3f
	
	db $10		//samxidu
	db $20, $85
	db $60, $61, $62, $63, $64, $65, $66, $67, $68, $69, $6a, $6b, $6c, $6d, $6e, $6f
	db $10
	db $20, $a5
	db $70, $71, $72, $73, $74, $75, $76, $77, $78, $79, $7a, $7b, $7c, $7d, $7e, $7f	
	db $10
	db $20, $c5
	db $80, $81, $82, $83, $84, $85, $86, $87, $88, $89, $8a, $8b, $8c, $8d, $8e, $8f
	db $10
	db $20, $e5
	db $90, $91, $92, $93, $94, $95, $96, $97, $98, $99, $9a, $9b, $9c, $9d, $9e, $9f	
	
	db $04
	db $20, $95
	db $a0, $a1, $a2, $a3
	db $04
	db $20, $b5
	db $b0, $b1, $b2, $b3
	
	db $04
	db $20, $d5
	db $a4, $a5, $a6, $a7
	db $04
	db $20, $f5
	db $b4, $b5, $b6, $b7
	
	db $01
	db $20, $f9
	db $b9
	
	db $05
	db $21, $07
	db $C0, $C1, $C2, $C3, $C4	//sukasi
	db $05
	db $21, $27
	db $d0, $d1, $d2, $d3, $d4
	db $05
	db $21, $47
	db $c5, $c6, $c7, $c8, $c9
	db $05
	db $21, $67
	db $d5, $d6, $d7, $d8, $d9
	db $05
	db $21, $87
	db $ca, $cb, $cc, $cd, $ce
	db $05
	db $21, $a7
	db $da, $db, $dc, $dd, $de
	
	db $0d 	//aian
	db $21, $ca
	db $e0, $e1, $e2, $e3, $e4, $e5, $e6, $e7, $e8, $e9, $ea, $eb, $ec
	db $0d
	db $21, $ea
	db $f0, $f1, $f2, $f3, $f4, $f5, $f6, $f7, $f8, $f9, $fa, $fb, $fc	

	db $02	//heart
	db $21, $4e
	db $ba, $bb
	db $02
	db $21, $6e
	db $bc, $bd
	
	db $06		//attribute
	db $23, $C9
	db $11, $11, $14, $15, $05, $05
	
	db $02
	db $23, $d1
	db $ff, $ff
	
	db $05
	db $23, $d9
	db $aa, $aa, $aa, $aa, $aa
	
	db $01
	db $23, $d3
	db $55
	
	db $00
	
write_oam:
	ldx #$00
-
	lda oam_table,x
	sta $0200,x
	inx
	cpx #$F8
	bne -
	rts
	
oam_table:
	db $9d, $ea, $00, $5c	//pawn

	db $80, $c1, $03, $18	//yattaro
	db $80, $c2, $03, $20
	db $80, $c3, $03, $28
	db $80, $c4, $03, $30
	
	db $88, $d0, $00, $10
	db $88, $d1, $00, $18
	db $88, $d2, $00, $20
	db $88, $d3, $00, $28
	db $88, $d4, $00, $30
	
	db $90, $c5, $00, $10
	db $90, $c6, $00, $18
	db $90, $c7, $00, $20
	db $90, $c8, $00, $28
	db $90, $c9, $00, $30
	
	db $98, $d5, $01, $10
	db $98, $d6, $01, $18
	db $98, $d7, $01, $20
	db $98, $d8, $01, $28
	db $98, $d9, $01, $30
	
	db $a0, $ca, $01, $10
	db $a0, $cb, $01, $18
	db $a0, $cc, $01, $20
	db $a0, $cd, $01, $28
	db $a0, $ce, $01, $30
	
	db $a8, $da, $01, $10
	db $a8, $db, $01, $18
	db $a8, $dc, $01, $20
	db $a8, $dd, $01, $28
	db $a8, $de, $01, $30
	
	db $50, $E0, $00, $90  //pururun
	db $50, $E1, $00, $98
	db $50, $E2, $00, $a0
	db $50, $E3, $00, $a8
	db $50, $E4, $00, $b0
	
	db $58, $F0, $00, $90
	db $58, $F1, $00, $98
	db $58, $F2, $00, $a0
	db $58, $F3, $00, $a8
	db $58, $F4, $00, $b0
	
	db $60, $e5, $00, $90
	db $60, $e6, $00, $98
	db $60, $e7, $00, $a0
	db $60, $e8, $00, $a8
	db $60, $e9, $00, $b0
	
	db $68, $f5, $00, $90
	db $68, $f6, $00, $98
	db $68, $f7, $00, $a0
	db $68, $f8, $00, $a8
	db $68, $f9, $00, $b0
	
	db $70, $ff, $00, $88
	db $70, $eb, $00, $90
	db $70, $ec, $00, $98
	db $70, $ed, $00, $a0
	db $70, $ee, $00, $a8
	db $70, $ef, $00, $b0
	
	db $78, $fa, $00, $88
	db $78, $fb, $00, $90
	db $78, $fc, $00, $98
	db $78, $fd, $00, $a0
	db $78, $fe, $00, $a8
	db $78, $ff, $00, $ff
	
	db $ff, $00, $00, $ff //end
	db $ff, $00, $00, $ff
	
table "ansi.tbl"
game_over:
	db $01
	db $21, $28
	db $B0
	db $FE
	db $14
	db $21, $29
	db $B1
	db $01
	db $21, $3D
	db $B4
	db $01
	db $21, $48
	db $B2
	db $FE, $14
	db $21, $49
	db $4C
	db $01
	db $21, $5D
	db $B6
	db $07
	db $21, $62
	db $B0, $B1, $B1, $B1, $B1, $B4, $B2
	db $FE, $14
	db $21, $69
	db $4C
	db $FE, $14
	db $21, $89
	db $4C
	db $FE, $14
	db $21, $A9
	db $4C
	db $FE, $14
	db $21, $C9
	db $4C
	db $FE, $14
	db $21, $E9
	db $4C
	db $FE, $14
	db $22, $09
	db $4C
	db $FE, $14
	db $22, $29
	db $4C
	db $FE, $14
	db $22, $49
	db $B9
	db $07
	db $21, $82
	db $B2, $4C, $4C, $4C, $4C, $B6, $B2
	db $07
	db $21, $A2
	db $B2, $4C, $4C, $4C, $4C, $B6, $B2
	db $07
	db $21, $C2
	db $B2, $4C, $4C, $4C, $4C, $B6, $B2
	db $07
	db $21, $E2
	db $B2, $4C, $4C, $4C, $4C, $B6, $B2
	db $07
	db $22, $02
	db $B8, $B9, $B9, $B9, $B9, $BC, $B2
	db $01
	db $22, $28
	db $B2
	db $01
	db $22, $48
	db $B8
	db $01
	db $21, $7D
	db $B6
	db $01
	db $21, $9D
	db $B6
	db $01
	db $21, $BD
	db $B6
	db $01
	db $21, $DD
	db $B6
	db $01
	db $21, $FD
	db $B6
	db $01
	db $22, $1D
	db $B6	
	db $01
	db $22, $3D
	db $B6	
	db $01
	db $22, $5D
	db $BC
	db $08
	db $21, $8F
	db "Het mang"
	db $01
	db $21, $70
	db $54
	db $01
	db $21, $B4
	db $71
	db $11
	db $21, $CA
	db "Ch", $4D, "i tiep  Mat ma"
	db $01
	db $21, $B1
	db $54
	db $05
	db $21, $B6
	db $53, "   ", $52
	db $01
	db $21, $F6
	db $71	
	
	db $00

	
