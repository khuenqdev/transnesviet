bank $0F

define txt_spd	$0438
define pause		$0437
define line			$043D
define text_trigger $90
define sitaten			$91
define text_counter $92
define	buffer1 $93
define	line	$043D
define accent_table	$0D50
define stage		$5D

//#############
// NEW WRITE
//############
org $a000
newloc:
	LDA $0439
	STA $0438	
_8cbb:
	lda #$ff
	sta {text_trigger}
	JSR $8E50 //read text
	CMP #$F5
	BCS _8d00
	jsr check_accent
//	TAY
	LDA #$82
	JSR $8E3E
//	TYA
//	CMP #$B0
//	BCC _8cee
//	CMP #$C0
//	BCS _8ce2
//	SEC
//	SBC #$B0
//	TAY
//	LDA #$5D
//	STA $03A3,x
//	LDA $8FF8,y
//	STA $03A4,x
//	BNE _8cf6
_8ce2:
//	AND #$7F
//	STA $03A4,x
//	LDA #$5C  //dakuten
//	STA $03A3,x
//	BNE _8cf6
_8cee:
//	STA $03A4,x
//	LDA #$20  //space
//	STA $03A3,x //upper letter
_8cf6:
	TXA
	CLC
	ADC #$05
	STA $21
	INC $043A
	RTS	
_8d00:
	SEC
	SBC #$F5
	TAY
	BNE _8d22
	JSR $8E50 //read txt
	ASL
	TAX
	LDA $0C
	STA $043F
//	LDA $A000,x //MTE PTR
	lda $a500,x
	STA $0C
	LDA $0D
	STA $0440
//	LDA $A001,x
	lda $a501,x
	STA $0D
//	JMP $8CBB
	jmp _8cbb
_8d22:		//f6
	DEY
	BNE _8d32
	LDA $043F
	STA $0C
	LDA $0440
	STA $0D
//	JMP $8CBB
	jmp _8cbb
_8d32:		//f7
	DEY
	BNE _8d3c
	JSR $8E50 //read txt
	STA $0439  //speed value
	RTS
_8d3c:		//f8
	DEY
	BNE _8d45
	INC $043D //line
	lda #$00
	sta {text_counter}
	JMP $8E59
_8d45: //f9
	DEY
	BNE _8d5c
	LDA #$FC
	STA $043C
	LDX $043D //line
	LDA $9006,x
	STA $0438
	STY $043D
	lda #$00
	sta {text_counter}
	sta {text_trigger}
	sta {line}
	jsr clear_table
	JMP $8E59
_8d5c: //fa
	DEY
	BNE _8d66
	JSR $8E50 //read txt
	STA $0437
	RTS
_8d66: //fb
	DEY
	BEQ +
	JMP $8DF7
+
	STY $0438
	LDX $21
	JSR $8E50 //read txt
	STA $03A0,x
	STA $00
	INX
	JSR $8E50 //read txt
	STA $03A0,x
	STA $02
	INX
	JSR $8E50 //read txt
	STA $03A0,x
	STA $03
	INX
_8d8c:
	LDA ($0C),y
	BPL _8da0
	CMP #$B0
	BCC _8da0
	CMP #$C0
	BCS _8d9c
	LDA #$5D
	BNE _8da2
_8d9c:
	LDA #$5C
	BNE _8da2
_8da0:
	LDA #$20
_8da2:
	STA $03A0,x
	INX
	INY
	CPY $00
	BNE _8d8c
	LDA $00
	STA $03A0,x
	INX
	LDA $03
	CLC
	ADC #$20
	STA $03A1,x
	BCC _8dbd
	INC $02
_8dbd:
	LDA $02
	STA $03A0,x
	INX #2
	LDY #$00
_8dc6:
	LDA ($0C),y
	CMP #$A0
	BCC _8de0
	CMP #$C0
	BCS _8dde
	STY $04
	SEC
	SBC #$B0
	TAY
	LDA $8FF8,y
	LDY $04
	JMP $8DE0
_8dde:
	AND #$7F
_8de0:
	STA $03A0,x
	INX
	INY
	CPY $00
	BNE _8dc6
	STX $21
	LDA $00
	CLC
	ADC $0C
	STA $0C
	BCC _8df6
	INC $0D
_8df6:
	RTS
_8df7:
	DEY
	BNE _8e28
	LDA $0438
	BEQ _8e03
	DEC $0438
	RTS
_8e03:
	LDA #$88
	JSR $8E3E
	INX #3
	LDY #$07
	LDA #$20
_8e0f:
	STA $03A0,x
	INX
	DEY
	BPL _8e0f
	STX $21
	INC $043A
	LDA $043A
	EOR #$3D
	BNE _8df6
	STA $043C
	JMP $8E59
_8e28:
	DEY
	BNE _8e2f
	INC $043E
	RTS
_8e2f:
	DEY
	BNE _8e38
	LDA #$80
	STA $043E
	RTS
_8e38:
	LDA #$00
	STA $0436
	lda #$00
	sta {line}
	sta {text_counter}
	sta {text_trigger}
	jsr clear_table
	RTS
	
clear_table:
	lda #$00
	ldx #$80
-
	sta {accent_table},x
	dex
	bne -
	rts
	

	
prepare:
	pha
	lda {line}
	asl #5
	sta {buffer1}
	lda {text_counter}
	inc {text_counter}
	clc
	adc {buffer1}
	tax
	pla
	rts	

write_table1:
	pha
	lda #$00
	sta {accent_table},x
	pla
	rts
write_table2:
	pha
	lda #$ff
	sta {accent_table},x
	pla
	rts
	
check_upper:
	pha
	lda {line}
	beq +
	txa
	sec
	sbc #$20
	tax
	lda {accent_table},x
	beq +
	sec
	jmp _s
+
	clc
_s:
	pla
	rts
	
check_accent:
	jsr prepare
	cmp #$4f
	bcs +
here:
	jsr write_table1
	jsr check_upper
	bcs _a1
	ldx $21
	sta $03a4,x
	lda #$4c
	sta $03a3,x
return:
	lda #$4c
	sta {sitaten}
	rts
_a1:
	ldx $21
	sta $03a4,x
	lda #$71
	sta $03a3,x
	jmp return
+
	cmp #$5c
	bcs +
	sec
	sbc #$4f
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _b1
	ldx $21
	lda accent1,y
	sta $03a4,x
	lda accent1+1,y
	sta $03a3,x
	jmp return
_b1:
	ldx $21
	lda accent11,y
	sta $03a4,x
	lda accent11+1,y
	sta $03a3,x
	jmp return
+
	cmp #$6b
	bcs +
	sec
	sbc #$5c
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _c1
	ldx $21
	lda accent2,y
	sta $03a4,x
	lda accent2+1,y
	sta $03a3,x
	jmp return
_c1:
	ldx $21
	lda accent12,y
	sta $03a4,x
	lda accent12+1,y
	sta $03a3,x
	jmp return		
+
	cmp #$74
	bcs +
	sec
	sbc #$6b
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _d1
	ldx $21
	lda accent3,y
	sta $03a4,x
	lda accent3+1,y
	sta $03a3,x
	jmp return
_d1:
	ldx $21
	lda accent13,y
	sta $03a4,x
	lda accent13+1,y
	sta $03a3,x
	jmp return	
+
	cmp #$7a
	bcs +
	jsr write_table1
	jsr check_upper
	bcs _e1
	ldx $21
	lda #$34 //õ
	sta $03a4,x
	lda #$52
	sta $03a3,x
	jmp return
_e1:
	ldx $21
	lda #$34 //õ nặng
	sta $03a4,x
	lda #$64
	sta $03a3,x
	jmp return
+
	cmp #$8a
	bcs +
	sec
	sbc #$7a
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _f1
	ldx $21
	lda accent4,y
	sta $03a4,x
	lda accent4+1,y
	sta $03a3,x
	jmp return
_f1:
	ldx $21
	lda accent14,y
	sta $03a4,x
	lda accent14+1,y
	sta $03a3,x
	jmp return
+
	cmp #$a0
	bcs +
	sec
	sbc #$8a
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _g1
	ldx $21
	lda accent5,y
	sta $03a4,x
	lda accent5+1,y
	sta $03a3,x
	jmp return
_g1:
	ldx $21
	lda accent15,y
	sta $03a4,x
	lda accent15+1,y
	sta $03a3,x
	jmp return	
+
	cmp #$a1
	bcs +
	jsr write_table1
	jsr check_upper
	bcs _h1
	ldx $21
	lda #$52 //ỹ
	sta $03a3,x
	lda #$3e
	sta $03a4,x
	jmp return
_h1:
	ldx $21
	lda #$64 //ỹ nặng
	sta $03a3,x
	lda #$3e
	sta $03a4,x
	jmp return
+
	cmp #$ad
	bcs +
	sec
	sbc #$a1
	asl
	tay
	jsr write_table2
	jsr check_upper
	bcs _i1
	ldx $21
	lda accent6,y
	sta $03a4,x
	lda accent6+1,y
	sta $03a3,x
kage:
	lda #$71
	sta {sitaten}
	rts
_i1:
	ldx $21
	lda accent16,y
	sta $03a4,x
	lda accent16+1,y
	sta $03a3,x
	jmp kage
+
	cmp #$af
	bcs +
	sec
	sbc #$ad
	asl
	tay
	jsr write_table1
	jsr check_upper
	bcs _j1
	ldx $21
	lda accent7,y
	sta $03a4,x
	lda accent7+1,y
	sta $03a3,x	
	jmp return
_j1:
	ldx $21
	lda accent17,y
	sta $03a4,x
	lda accent17+1,y
	sta $03a3,x	
	jmp return
+
	cmp #$b0
	bne +
	jsr write_table1
	jsr check_upper
	bcs _k1
	ldx $21
	lda #$72
	sta $03a4,x
	lda #$4c
	sta $03a3,x
	sta {sitaten}
	rts
_k1:
	ldx $21
	lda #$72
	sta $03a4,x
	lda #$71
	sta $03a3,x
	sta {sitaten}
	rts
+	
	jmp here
	


accent1:
	dw $4f26  //á
	dw $5026 //à
	dw $5126  //ả
	dw $5226	//ã
	dw $5326	//â
	dw $5426	//ấ
	dw $5526 //ầ
	dw $5626 //ẩ
	dw $5726  //ẫ
accent11:
	dw $6126  //á nặng
	dw $6226 //à nặng
	dw $6326  //ả nặng
	dw $6426	//ã nặng
	dw $6526	//â nặng
	dw $6626	//ấ nặng
	dw $6726 //ầ nặng
	dw $6826 //ẩ nặng
	dw $6b26  //ẫ nặng
	
accent2:
	dw $5c26 //ă
	dw $5d26 //ắ
	dw $5e26 //ằ
	dw $5f26 //ẳ
	dw $6026 //ẵ
	dw $4f2e //í
	dw $502e //ì
	dw $512e //ỉ
	dw $522e //ĩ
	dw $4f48 //é
	dw $5048 //è
	dw $5148 //ẻ
	dw $5248 //ẽ
	
accent12:
	dw $6c26 //ă nặng
	dw $6d26 //ắ nặng
	dw $6e26 //ằ nặng
	dw $6f26 //ẳ nặng
	dw $7026 //ẵ nặng
	dw $612e //í nặng
	dw $622e //ì nặng
	dw $632e //ỉ nặng
	dw $642e //ĩ nặng
	dw $6148 //é nặng
	dw $6248 //è nặng
	dw $6348 //ẻ nặng
	dw $6448 //ẽ nặng
	
accent3:
	dw $5348 //ê
	dw $5448 //ế
	dw $5548 //ề
	dw $5648 //ể
	dw $5748 //ễ
	dw $4f34 //ó
	dw $5034 //ò
	dw $5134 //ỏ

accent13:
	dw $6548 //ê nặng
	dw $6648 //ế nặng
	dw $6748 //ề nặng
	dw $6848 //ể nặng
	dw $6b48 //ễ nặng
	dw $6134 //ó nặng
	dw $6234 //ò nặng
	dw $6334 //ỏ nặng

accent4:
	dw $5334 //ô 
	dw $5434 //ố
	dw $5534 //ồ
	dw $5634 //ổ
	dw $5734 //ỗ
	dw $4f4d //ớ
	
accent14:
	dw $6534 //ô  nặng
	dw $6634 //ố nặng
	dw $6734 //ồ nặng
	dw $6834 //ổ nặng
	dw $6b34 //ỗ nặng
	dw $614d //ớ nặng
	
accent5:
	dw $504d //ờ
	dw $514d //ở
	dw $524d //ỡ
	dw $4f3a //ú
	dw $503a //ù
	dw $513a //ủ
	dw $523a //ũ
	dw $4f4e //ứ
	dw $504e //ừ
	dw $514e //ử
	dw $524e //ữ
	dw $4f3e //ý
	dw $503e //ỳ
	dw $513e //ỷ
accent15:
	dw $624d //ờ nặng
	dw $634d //ở nặng
	dw $644d //ỡ nặng
	dw $613a //ú nặng
	dw $623a //ù nặng
	dw $633a //ủ nặng
	dw $643a //ũ nặng
	dw $614e //ứ nặng
	dw $624e //ừ nặng
	dw $634e //ử nặng
	dw $644e //ữ nặng
	dw $613e //ý nặng
	dw $623e //ỳ nặng
	dw $633e //ỷ	 nặng
	
accent6:
	dw $4c26 //ạ
	dw $5326 //ậ
	dw $5c26 //ặ
	dw $4c2e //ị
	dw $4c48 //ẹ
	dw $5348 //ệ
	dw $4c34 //ọ
	dw $5334 //ộ
	dw $4c4d //ợ
	dw $4c3a //ụ
	dw $4c4e //ự
	dw $4c3e //ỵ
accent16:
	dw $7126 //ạ	 nặng
	dw $6526 //ậ	 nặng
	dw $6c26 //ặ	 nặng
	dw $712e //ị	 nặng
	dw $7148 //ẹ	 nặng
	dw $6548 //ệ	 nặng
	dw $7134 //ọ nặng
	dw $6534 //ộ nặng
	dw $714d //ợ nặng
	dw $713a //ụ	 nặng
	dw $714e //ự	 nặng
	dw $713e //ỵ	 nặng
	
accent7:
	dw $530F //Ô
	dw $5301 //Â
accent17:
	dw $650F //Ô nặng
	dw $6501 //Â nặng
