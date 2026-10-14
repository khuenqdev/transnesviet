bank $08
define char_num $0380
define pos_hi1	$0381
define pos_low1	$0382
define pos_hi2	$0383
define pos_low2 $0384


//############
// Ending text write
//###########
org $8505
	jmp write_ending
//	LDA $855B,y  //ptr
//	STA $00
	nop
return_ending:
	LDA $855C,y
	STA $01
	LDY $42
	INC $42
	LDA ($00),y
	BEQ _548
	CMP #$FF
	BEQ _54a
	CMP #$FE
	BEQ _54b
	LDX $21
	LDA #$01
	STA $0700,x
	STA $0701,x
	STA $0702,x
	INX #3
	LDA $44
	STA $0700,x
	INX
	LDA $43
	STA $0700,x
	INX
	LDA ($00),y
	STA $0700,x
	INX
	STX $21
	LDA #$10
	JSR $F9BC
_548:
	INC $43
_54a:
	RTS
_54b:
//	LDA $43
//	AND #$E0
	jmp line_cal
	nop
return3:
	STA $43
	LDA #$45
	LDX #$43
	JSR $C72D
	LDA #$01
	RTS


//#############
// Write text string to ram
//#############
org $993C
	TAY
	LDX $21
	LDA #$01
	STA $0700,x
	LDA $49
	STA $0702,x
	LDA $4A
	STA $0701,x
	TYA
	STA $0703,x
	LDA #$FF
	STA $0704,x
	TXA
	CLC
	ADC #$05
	STA $21
	INC $49
	RTS
	
//#############
// Text pos
//#############
org $97B6
	LDY #$00
	STY $47
	STY $48
	INY
	STY $43
_97BF:
	LDA $46
	ASL
	TAY
	LDA $97DB,y
	STA $00
	LDA $97DC,y
	STA $01
	LDA $48
	ASL
	TAY
	LDA ($00),y
	STA $49
	INY
	LDA ($00),y
//	STA $4A
//	RTS
	jmp line_code
//#######
//text pos pointer
//#########
org $97DB
	dw text_pos1
	dw text_pos2
	dw text_pos3

	
//############
// Text value
//###########
org $97FD
	 DEC $43 //text speed
	 BNE _9844
	 LDA #$03
	 STA $43
	 LDA $46
	 ASL
	 TAY
	 LDA $9848,y
	 STA $02
	 LDA $9849,y
//	 STA $03
	jmp text_trigger
//	 LDY $47
	nop
return:
	 INC $47
	 LDA ($02),y
	 CMP #$FF
	 BCS _9846
	 CMP #$FE
	 BCC _982C
	 INC $48
	 JSR $97BF
	 LDY $47
	 INC $47
	 LDA ($02),y
_982C:
	 STA $08
	AND #$7F
	BEQ _9839
	PHA
	LDA #$0E
	JSR $F9BC
	PLA
_9839:
	 JSR $993C //write to ram
	 LDA $08
	 BPL _9844
	 LDA #$30
	 STA $43
_9844:
	 CLC
	 RTS
_9846:
	 SEC
	 RTS
text_pointer: //$9848
 	dw $984E, $9886, $98EC
	
//##################
// BIG TEXT
//##################
org $8F6B
	ldy #$7a //change chr bank: text
	
org $8fa0
	lda #$05 	//spd

org $8FA8
	lda first_msg,y
	
org $9034
	lda #$ff
	sta $0198
	lda #$7a
	sta $07f4
	lda #$7b
	sta $07f5
	lda #$42
	sta $07f6
	lda #$3e
	sta $07f7
	lda {char_num}
	bne +
	lda #$20
	sta {pos_hi1}
	sta {pos_hi2}
	lda #$e4
	sta {pos_low1}
	sta {pos_low2}
	ldx #$00
	lda first_text,x
	sta $0e
	lda first_text+1,x
	sta $0f
+

	lda #$01
	sta $0700
	lda {pos_hi1}
	sta $0701
	lda {pos_low1}
	sta $0702
	ldy #$00
	lda ($0e),y
	cmp #$ff
	bne +
	lda #$80
	sta $41
	inc $46
	rts
+	
	cmp #$fe
	bne +
	lda {pos_low2}
	clc
	adc #$40
	sta {pos_low2}
	sta {pos_low1}
	lda #$00
	adc {pos_hi2}
	sta {pos_hi2}
	sta {pos_hi1}
	inc {char_num}
	inc $0e
	bne end
	lda $0f
	adc #$00
	sta $0f
end:
	rts
+
	inc {char_num}
	inc {pos_low1}
	sta $0703
	lda #$ff
	sta $0704
	lda #$00
	sta $0705
	lda #$0c
	sta $21
	inc $0e
	bne end1
	lda $0f
	adc #$00
	sta $0f
end1:
	rts
	
//####################
// STAFF ROLL
//###################
org $83EC
	LDA $42  //text ID
	INC $42
	ASL
	TAY
	LDA $85F8,y
	STA $00
	LDA $85F9,y
	BEQ _8457
	CMP #$01
	BEQ _8475
	STA $01
	LDY #$00
	LDA ($00),y  //length
	STA $03
	INY
	LDA ($00),y  //pos
	STA $02
	LDA #$20
	SEC
	SBC $02
	SBC $03
	STA $04
	LDX $21
	LDA #$01
	STA $0700,x
	STA $0702,x
	LDA #$20
	INX
	STA $0700,x
	INX
	LDA $44
	INX
	STA $0700,x
	LDA $43
	INX
	STA $0700,x
	INX
	JSR $8467
_8437:
	LDA $03
	BEQ _8446
	INY
	LDA ($00),y  //text
	STA $0700,x
	DEC $03
	INX
	BNE _8437
_8446:
	LDA $04
	STA $02
	JSR $8467
	STX $21
	LDX #$43
	LDA #$20
	JSR $C72D
-
	RTS
_8457:
	STA $2A
	STA $030A
	LDA #$03
	STA $2B
	LDA #$B0
	STA $FF
	JMP $C15B
_8467:
	LDA $02
	BEQ -
	LDA #$00
	STA $0700,x
	DEC $02
	INX
	BNE _8467
_8475:
	LDX #$07
_8477:
	LDA $8490,x
	STA $07C0,x
	DEX
	BPL _8477
	LDA #$10
	STA $36
	LDY #$40
	STY $07F4
	INY
	STY $07F5
	JMP $83EC
	
org $85F8		//text roll ID
	dw $86A0
	dw $86A0
	dw $86A2 //05: STAFF
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86BA //0C:Programmers: S.Umezaki
	dw $86C5 //0D: S.Kishiwada
	dw $86D2 //0E: K.Yamashita
	dw $86DF //0F: T.Danjo
	dw $86E9 //10: M.Ogawa
	dw $86A0
	dw $86A0
	dw $86F2 //14: Graphic designer
	dw $86A0
	dw $86A0
	dw $8705 //17: T.Ueyama
	dw $870F //18:S.Muraki
	dw $8719 //19: M.Fujiwara
	dw $8725 //1A: T.Nishikawa
	dw $8732 //1B: C.Ozawa
	dw $86A0
	dw $86A0
	dw $875D //1F:Sound Creators
	dw $86A0
	dw $86A0
	dw $876D //22:H.Maezawa
	dw $8778 //23: K.Sada
	dw $86A0
	dw $86A0
	dw $8780 //27:Special thanks
	dw $86A0
	dw $86A0
	dw $8793 //2A: K.Shimoide
	dw $879F //2B: N.Sato
	dw $87A7 //2C: AC Contra Team
	dw $86A0
	dw $86A0
	dw $873B //30: directed by
	dw $86A0
	dw $86A0	
	dw $8748  //33: Umechan
	dw $8751 //34: S.Kitamoto
	dw $86A0 
	dw $86A0
	dw $86A0
	dw translator1
	dw $86A0
	dw translator2
	dw sekishu
	dw wimsagn
	dw spc700
	dw jun2022
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0  
	dw $0100 //konami
	dw $87B7
	dw $87C4
	dw $87D2
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
	dw $86A0
