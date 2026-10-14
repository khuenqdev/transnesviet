bank $09
define buffer1 $0197
define buffer11	$0350
define buffer2	$0198
define buffer12	$0351
define counter	$0199
define save_x	$019A
define save_x1	$0352
define save_x2  $0353
define counter2 $0354
define line2		$0355
define save_bank	$019B
define line			$48
define speed2	$47
define counter_table $0390
//###################
// AFTER MISSION
//##################
org $A04A
	LDA #$0F  //text pos
	STA $48
	STA $4A
	LDA #$21
	STA $49
	STA $4B
	LDY #$00
	STY $46
	INY
	STA $47

org $A165
	DEC {speed2}
	BNE end_0165
	LDA #$03
	STA {speed2}
	LDA $30
	ASL
	TAY
	LDA $A1D6,y
	STA $00
	LDA $A1D7,y
//	STA $01
//	LDY $46
	jmp text_trigger2
	nop
return2:
	LDA ($00),y
	CMP #$FF
	BEQ _A1D4
	STA $08
	CMP #$F0
	BNE _A18A
	INY
_A18A:
	LDX $21
	LDA #$01
	STA $0700,x
	LDA $4B
	STA $0701,x //tex pos
	LDA $4A
	STA $0702,x
	LDA ($00),y
	STA $0703,x
	BEQ _A1A7
	LDA #$10
	JSR $F9BC
_A1A7:
	LDA #$FF
	STA $0704,x
	TXA
	CLC
	ADC #$05
	STA $21
	INY
	STY $46
	INC $4A
	LDA $08
	CMP #$F0
	BNE end_0165
	LDA $48
	CLC
	ADC #$40
	STA $48
	STA $4A
	LDA $49
	ADC #$00
	STA $49
	STA $4B
	LDA #$03
	STA {speed2}	
end_0165:
	CLC
	RTS
_A1D4:
	SEC
	RTS
_A1D6:  //mission pointer




//################
// NEW CODE
//###################
org $AB70
new_loc:
	LDA $23
	BEQ +
	JMP $CBC0
+
	LDY #$00
	STY $08
_CB3B:
	LDA $08
	CMP #$3F
	BNE +
	jsr function1
+
	LDX $0700,y
	BEQ +
	LDA $FF
	AND #$18
	ORA $CB2A,x
	STA $2000
	INY
	LDA $2002
	LDA $0700,y
	STA $08
	STA $2006
	INY
	LDA $0700,y
	STA $2006
	INY
	CPX #$03
	BEQ _CB7C  //write graphic string1
	CPX #$04
	BCS _CBAF //write graphic string2
	BNE _CB9E  //write single text
_CB7C:
	LDA $0700,y
	STA $09
-
	INY
	LDA $0700,y
	STA $2007
	DEC $09
	BNE -
+
	LDA #$00
	STA $0700
	STA $21
	LDA $FF
	STA $2000
	RTS
_CB99:
	LDA #$FF
-
	jsr check_accent
	STA $2007
_CB9E:
	LDA $0700,y
	INY
	CMP #$FF
	BNE -
	LDA $0700,y
	CMP #$06
	BCS _CB99
	BCC _CB3B
_CBAF:
	LDX $0700,y
	INY
	LDA $0700,y
	INY
-
	STA $2007
	DEX
	BNE -
	JMP $CB3B
	
write_pallet:
	lda #$3f
	sta $2006
	lda #$00
	sta $2006
	lda #$0f
	sta $2007
	lda #$32
	sta $2007
	rts
	
	
check_accent:
	pha
	lda {buffer2}
	cmp #$ff
	beq +
	cmp #$fe
	beq no_change_bank
	pla
	rts
	
+
	lda #$3e
	sta $07f7
no_change_bank:
	lda #$00
	sta {buffer2}
	pla
	cmp #$29
	bcs +
	pha
	jsr prepare
	lda #$00
	sta {counter_table},x
	pla
	rts
+
	cmp #$5f
	bcs  +
	sec
	sbc #$29
	asl
	tax
	stx {save_x}
	lda accent1,x
	sta $2007
	lda $0702
	sec
	sbc #$20
	pha
	lda $0701
	sbc #$00
	sta $2006
	pla
	sta $2006
	jsr check_line
	bcs write_sec1
	ldx {save_x}
	lda accent1+1,x
	jmp end_accent1
write_sec1:
	ldx {save_x}
	lda accent4+1,x
end_accent1:
	pha
	jsr prepare
	lda #$00
	sta {counter_table},x
	pla
	rts
+
	cmp #$65
	bcs +
	sec
	sbc #$5f
	asl
	tax
	lda accent2,x
	sta $2007
	lda $0702
	clc
	adc #$20
	pha
	lda $0701
	adc #$00
	sta $2006
	pla
	sta $2006
	lda accent2+1,x
	pha
	jsr prepare
	lda #$ff
	sta {counter_table},x
	pla
	rts
+
	sec
	sbc #$65
	sta {buffer1}
	asl
	clc
	adc {buffer1}
	tax
	sta {save_x}
	lda accent3,x
	sta $2007
	lda $0702
	clc
	adc #$20
	pha
	lda $0701
	adc #$00
	sta $2006
	pla
	sta $2006
	lda accent3+1,x
	sta $2007
	lda $0702
	sec
	sbc #$20
	pha
	lda $0701
	sbc #$00
	sta $2006
	pla
	sta $2006
	jsr check_line
	bcs +
	ldx {save_x}
	lda accent3+2,x
	jmp end_accent2
+
	ldx {save_x}
	lda accent5+2,x
end_accent2:
	pha
	jsr prepare
	lda #$ff
	sta {counter_table},x
	pla
	rts 
	
accent1:
	db $01, $2a //á
	db $01, $2b //à
	db $01, $2c //ả
	db $01, $2d //ã
	
	db $01, $2f //â
	db $01, $30//ấ
	db $01, $31 //ầ
	db $01, $32 //ẩ
	db $01, $33 //ẫ
	
	db $01, $34 //ă
	db $01, $35 //ắ
	db $01, $36 //ằ
	db $01, $37 //ẳ
	db $01, $38 //ẵ
	
	db $09, $2a //í
	db $09, $2b //ì
	db $09, $2c //ỉ
	db $09, $2d //ĩ
	
	db $0F, $2a //ó
	db $0F, $2b //ò
	db $0F, $2c //ỏ
	db $0F, $2d //õ
	
	db $0F, $2f //ô
	db $0F, $30 //ố
	db $0F, $31 //ồ
	db $0F, $32 //ổ
	db $0F, $33 //ỗ
	
	db $0F, $29 //ơ
	db $0F, $39 //ớ
	db $0F, $3a //ờ
	db $0F, $3b //ở
	db $0F, $3c //ỡ
	
	db $05, $2a //é
	db $05, $2b //è
	db $05, $2c //ẻ
	db $05, $2d //ẽ
	
	db $05, $2f //ê
	db $05, $30 //ế
	db $05, $31 //ề
	db $05, $32 //ể
	db $05, $33 //ễ
	
	db $15, $2a //ú
	db $15, $2b //ù
	db $15, $2c //ủ
	db $15, $2d //ũ
	
	db $15, $29 //ư
	db $15, $39 //ứ
	db $15, $3a //ừ
	db $15, $3b //ử
	db $15, $3c //ữ
	
	db $19, $2a //ý
	db $19, $2b //ỳ
	db $19, $2c //ỷ
	db $19, $2d //ỹ
	
accent2:
	db $01, $2e //ạ
	db $05, $2e //ẹ
	db $09, $2e //ị
	db $0F, $2e //ọ
	db $15, $2e //ụ
	db $19, $2e //ỵ
	
accent3:
	db $01, $2e, $2f //ậ
	db $01, $2e, $34 //ặ
	db $0F, $2e, $2f //ộ
	db $0F, $2e, $29 //ợ
	db $15, $2e, $29 //ự
	db $05, $2e, $2f //ệ
	
accent4:
	db $01, $3d //á .
	db $01, $3e //à .
	db $01, $d0 //ả .
	db $01, $c0 //ã .
	
	db $01, $c2 //â .
	db $01, $c3 //ấ .
	db $01, $c4 //ầ .
	db $01, $c5 //ẩ .
	db $01, $c6 //ẫ .
	
	db $01, $c7 //ă .
	db $01, $c8 //ắ .
	db $01, $c9 //ằ .
	db $01, $ca //ẳ .
	db $01, $cb //ẵ .
	
	db $09, $3d //í .
	db $09, $3e //ì .
	db $09, $d0 //ỉ .
	db $09, $c0 //ĩ .
	
	db $0F, $3d //ó .
	db $0F, $3e //ò .
	db $0F, $d0 //ỏ .
	db $0F, $c0 //õ .
	
	db $0F, $c2 //ô .
	db $0F, $c3 //ố .
	db $0F, $c4 //ồ .
	db $0F, $c5 //ổ .
	db $0F, $c6 //ỗ .
	
	db $0F, $c1 //ơ .
	db $0F, $cc //ớ .
	db $0F, $cd //ờ .
	db $0F, $ce //ở .
	db $0F, $cf //ỡ .
	
	db $05, $3d //é .
	db $05, $3e //è .
	db $05, $d0 //ẻ .
	db $05, $c0 //ẽ .
	
	db $05, $c2 //ê .
	db $05, $c3 //ế .
	db $05, $c4 //ề .
	db $05, $c5 //ể .
	db $05, $c6 //ễ .
	
	db $15, $3d //ú .
	db $15, $3e //ù .
	db $15, $d0 //ủ .
	db $15, $c0 //ũ .
	
	db $15, $c1 //ư .
	db $15, $cc //ứ .
	db $15, $cd //ừ .
	db $15, $ce //ử .
	db $15, $cf //ữ .
	
	db $19, $3d //ý .
	db $19, $3e //ỳ .
	db $19, $d0 //ỷ .
	db $19, $c0 //ỹ	 .
	
accent5:
	db $01, $2e, $c2 //ậ .
	db $01, $2e, $c7 //ặ .
	db $0F, $2e, $c2 //ộ .
	db $0F, $2e, $c1 //ợ .
	db $15, $2e, $c1 //ự .
	db $05, $2e, $c2 //ệ .

text_pos1:
	dw $2224, $2264, $22A4, $22E4
text_pos2:
	dw $21A4, $21E4, $2224, $2264, $22A4, $22E4, $2324, $2364
text_pos3:
	dw $21E4, $2224, $2264, $22A4, $22E4, $2324
	
text_trigger:
	sta $03
	lda #$ff
	sta {buffer2}
	ldy $47
	jmp return
text_trigger2:
	STA $01
	lda #$fe
	sta {buffer2}
	LDY $46
	jmp return2
	
check_accent2:
	lda {counter}
	sec
	sbc #$20
	lda {counter_table},x
	bne +
	ldx {save_x}
	clc
	rts
+
	ldx {save_x}
	sec
	rts

line_code:
	STA $4A
	lda #$00
	sta {counter}
	rts
	
prepare:
	lda {line}
	asl #5
	sta {buffer1}
	lda {counter}
	inc {counter}
	clc
	adc {buffer1}
	tax
	rts
check_line:
	lda {line}
	beq +
	sec
	sbc #$01
	asl #5
	adc {counter}
	tax
	lda {counter_table},x
	bne set_carry
+
	clc
	rts
set_carry:
	sec
	rts
	
init_buffer2:
	LDX #$00
-
	LDA $C793,y
	STA $07F0,x
	INY
	inx
	cpx #$08
	bne -
	lda #$00
	sta {buffer2}
	rts
	
ammo:
	lda $f1,x
	and #$0f
	clc
	adc $08
	tay
	lda $d870,y
	sta $c2,x
	lda $f1
	cmp #$28
	bne +
	lda #$00 //normal
	sta $aa
	rts
+
	cmp #$21
	bne +
	lda #$01 //rensha
	sta $aa
	rts
+
	cmp #$22
	bne +
	lda #$02 //spin
	sta $aa
	rts
+
	cmp #$24
	bne +
	lda #$03 //5 way
	sta $aa
	rts
+
	cmp #$2a
	bne +
	lda #$04 //laser
	sta $aa
	rts
+
	cmp #$a8
	bne +
	lda #$10 //normal hi
	sta $aa
	rts
+
	cmp #$a1
	bne +
	lda #$11 //rensha hi
	sta $aa
	rts
+
	cmp #$a4
	bne +
	lda #$12 //spin hi
	sta $aa
	rts 
+
	cmp #$a2
	bne +
	lda #$13 //5way hi
	sta $aa
	rts
+
	cmp #$a9
	bne +
	lda #$14 //laser hi
	sta $aa
	rts
+
	cmp #$aa
	bne +
	lda #$38 //all
	sta $aa
+
	rts
function1:
	STA $2006
	LDA #$00
	STA $2006
	STA $2006
	STA $2006
	rts
	
org $B860
-
	JMP $CB8C
secret_msg:
	LDX #$00
	LDA $FF
	AND #$18
	STA $02
_cbc8:
	LDY $0700,x
	BEQ -
	lda {buffer12}
	cmp #$ff
	bne +
	jmp kage
+	
	jsr taro
_cbe1:
	jsr jiro
-
	INX
	LDA $0700,x
	STA $2007
	DEY
	BNE -
	DEC $01
	BNE _cbe1
saburo:
	INX
	BNE _cbc8
	LDX $36
	BEQ +
	LDA $21
	CMP #$47
	BCS +
	LDA $FF
	AND #$18
	STA $2000
	LDA #$3F
	STA $2006
	LDA #$00
	STA $2006
	TAY
-
	LDA $07C0,y
	STA $2007
	INY
	DEX
	BNE -
	LDA #$3F
	STA $2006
	STX $2006
	STX $2006
	STX $2006
	STX $36
+
	RTS
	
kage:
	jsr taro
	jsr jiro
	INX
	LDA $0700,x
	jsr check_secret_msg
	STA $2007
	lda #$00
	sta {buffer12}
	jmp saburo
	
line_cal:
	inc {line2}
	lda #$00
	sta {counter2}
	LDA $43
	AND #$E0
	jmp return3

prepare2:
	lda {line2}
	asl #5
	sta {buffer11}
	lda {counter2}
	inc {counter2}
	clc
	adc {buffer11}
	tax
	rts
	
check_secret_msg:
	stx {save_x1}
	pha
	lda #$3e
	sta $07f7
	pla
	cmp #$29
	bcs +
	pha
	jsr prepare2
	lda #$00
	sta {counter_table},x
	ldx {save_x1}
	pla
	rts
+
	cmp #$5f
	bcs  +
	sec
	sbc #$29
	asl
	tax
	stx {save_x}
	lda accent1,x
	sta $2007
	lda $0704
	sec
	sbc #$20
	pha
	lda $0703
	sbc #$00
	sta $2006
	pla
	sta $2006
	jsr check2
	bcs toro
	ldx {save_x}
	lda accent1+1,x
	jmp inu
toro:
	ldx {save_x}
	lda accent4+1,x
inu:	
	pha
	jsr prepare2
	lda #$00
	sta {counter_table},x
	ldx {save_x1}
	pla
	rts
+
	cmp #$65
	bcs +
	sec
	sbc #$5f
	asl
	tax
	stx {save_x}
	lda accent2,x
	sta $2007
	lda $0704
	clc
	adc #$20
	pha
	lda $0703
	adc #$00
	sta $2006
	pla
	sta $2006
	lda accent2+1,x
	pha
	jsr prepare2
	lda #$ff
	sta {counter_table},x
	ldx {save_x1}
	pla
	rts
+
	sec
	sbc #$65
	sta {buffer11}
	asl
	clc
	adc {buffer11}
	tax
	stx {save_x}
	lda accent3,x
	sta $2007
	lda $0704
	clc
	adc #$20
	pha
	lda $0703
	adc #$00
	sta $2006
	pla
	sta $2006
	lda accent3+1,x
	sta $2007
	lda $0704
	sec
	sbc #$20
	pha
	lda $0703
	sbc #$00
	sta $2006
	pla
	sta $2006
	jsr check2
	bcs +
	ldx {save_x}
	lda accent3+2,x
	jmp tora
+
	ldx {save_x}
	lda accent5+2,x
tora:
	pha
	jsr prepare2
	lda #$ff
	sta {counter_table},x
	ldx {save_x1}
	pla
	rts 

check2:
	lda {line2}
	beq +
	sec
	sbc #$01
	asl #5
	adc {counter2}
	tax
	lda {counter_table},x
	bne set_carry2
+
	clc
	rts
set_carry2:
	sec
	rts
	
jiro:
	LDY $00
	INX
	LDA $0700,x
	STA $2006
	INX
	LDA $0700,x
	STA $2006
	rts
	
taro:
	LDA $02
	ORA $CB2A,y
	STA $2000
	INX
	LDA $0700,x
	STA $00
	INX
	LDA $0700,x
	STA $01
	RTS
	
write_ending:
	lda #$ff
	sta {buffer12}
	LDA $855B,y  //ptr
	STA $00
	jmp return_ending
	
first_text:
	db $de, $ad
	
org $BC30
first_msg:
	
//################
// FIX MAP
//##############
org $B19D
	db $00
org $b1a1
	db $00
org $b1a5
	db $03
org $b1a9
	db $13
org $B30c
	db $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00,

org $B57C
	db $22, $23, $30, $31, $32, $33, $24, $25, $26, $27, $38, $39, $3A, $3B, $2C, $25, $26, $2F, $3C, $35, $36, $3F, $2C, $25, $26, $2F, $3C, $35, $36, $3F, $F7, $25, $F8, $2F, $34, $35, $36, $3F, $F7, $25, $F8, $2F, $34, $35, $36, $3F, $20, $21, $22, $23, $30, $31, $32, $33, $24, $25, $26, $27, $34, $35, $36, $37, $24, $25, $26, $27, $34, $35, $36, $37, $20, $21, $22, $23, $30, $31, $32, $33, $24, $25, $26, $2F, $34, $35, $36, $3F, $24, $25, $26, $2F, $34, $35, $36, $3F, $2C, $25, $26, $27, $3C, $35, $36, $37, $2C, $25, $26, $27, $3C, $35, $36, $37, $20, $21, $22, $23, $30, $31, $32, $33, $24, $25, $26, $27, $38, $39, $0C, $3B, $20, $21, $22, $23, $30, $31, $32, $33, $24, $25, $26, $27, $19, $39, $0C, $3B, $05, $05, $05, $05, $5F, $5F
	
//#######################
// STAFF ROLL
//#######################
org $BCD0
table "ANSI.tbl"
translator1:
	db $16, $05
	db "VIETNAMESE TRANSLATION"
translator2:
	db $0E, $09
	db "PROGRAMMING BY"
sekishu:
	db $11, $07
	db "STONE BOAT STUDIO"
wimsagn:
	db $0D, $09
	db "61856 WIMSAGN"
spc700:
	db $0F, $08
	db "RETROMAN SPC700"
jun2022:
	db $08, $0B
	db "JUN 2022"	

	
//###############
// TITLE
//##############
org $BD50
title:
db $00, $20, $4B, $00
db $8B, $30, $33, $34, $35, $36, $37, $3A, $3B, $3C, $3D, $3E
db $14, $00
db $8C, $3F, $40, $42, $44, $46, $47, $48, $4A, $55, $56, $57, $58
db $14, $00, $82, $5A, $5B, $1A, $00, $86, $81, $82, $83, $84, $85, $86
db $19, $00, $89, $90, $91, $92, $93, $94, $95, $96, $97, $98
db $17, $00
db $89, $A0, $A1, $A2, $A3, $A4, $A5, $A6, $A7, $A8
db $16, $00
db $84, $B0, $B1, $B2, $B3
db $02, $00
db $84, $60, $B6, $B7, $B8
db $16, $00
db $96, $89, $8A, $8B, $00, $00, $6C, $01, $02, $03, $04, $05, $06, $07, $08, $09, $0A, $0B, $0C, $0D, $0E, $0F, $7C
db $0A, $00
db $97, $99, $9A, $9B, $00, $00, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $1A, $1B, $1C, $1D, $1E, $1F, $6D, $6E
db $09, $00
db $98, $A9, $AA, $AB, $00, $00, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $2A, $2B, $2C, $2D, $2E, $2F, $7D, $7E, $7F, $08, $00, $98, $79, $7A, $7B, $BE, $00, $87, $88, $BB, $BC, $BD, $70, $71, $80, $5C, $5D, $5E, $5F, $6F, $B9, $BA, $AC, $AD, $AE, $AF, $09, $00, $8B, $61, $62, $63, $64, $65, $66, $67, $68, $69, $6A, $6B, $15, $00, $88, $60, $72, $73, $74, $75, $76, $77, $78, $47, $00, $85, $C4, $00, $D0, $D1, $D2, $1A, $00, $87, $D3, $D4, $D5, $E0, $E1, $E2, $E3, $0B, $00, $8B, $50, $4C, $41, $59, $00, $53, $45, $4C, $45, $43, $54, $04, $00, $85, $E4, $E5, $F0, $F1, $F2, $1A, $00, $88, $F3, $F4, $F5, $C5, $C6, $C7, $C8, $C9, $0C, $00, $88
db $31, $00, $50, $4C, $41, $59, $45, $52, $03, $00, $85, $CA, $CB, $CC, $CD, $CE, $03, $00, $82, $EF, $D6, $15, $00, $86, $D9, $DA, $DB, $DC, $DD, $DE, $04, $00, $81, $E6, $0B, $00, $90, $32, $00, $50, $4C, $41, $59, $45, $52, $53, $00, $E9, $EA, $EB, $EC, $ED, $EE, $04, $00, $81, $F6, $17, $00, $84, $D7, $D8, $E7, $E8, $32, $00, $8E, $51, $00, $4B, $4F, $4E, $41, $4D, $49, $00, $00, $31, $39, $38, $38
db $7E, $00, $0D, $00
db $84, $80, $A0, $A0, $20
db $04, $00
db $84, $08, $0A, $0A, $02
db $0B, $00
db $81, $04
db $04, $05
db $81, $05
db $05, $00
db $83, $CC, $FF, $F3
db $05, $00
db $83, $FF, $FF, $CC
db $11, $00
db $FF