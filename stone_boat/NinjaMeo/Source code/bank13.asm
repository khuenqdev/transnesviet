bank $13
define	save_bank $4c
define save_a	$4d
define	table		$0192
define	pos_table	$01D0

org $A000
bank11_code:
//HACK INPUT
	LDA $16
	cmp #$28	//restore ninpo
	bne +
	lda #$ff
	sta $40
	jmp return_home
+
	cmp #$24		//change ninpo
	bne +
	inc $3d
	lda $3d
	and #$03
	beq write_1
	sta $3d
	jmp return_home
write_1:
	lda #$01
	sta $3d
	jmp return_home
+
	cmp #$60	//change char
	bne +
	inc $3b
	lda $3b
	cmp #$07
	bcs write_0
	sta $3b
	jmp return_home
write_0:
	lda #$00
	sta $3b
	jmp return_home
+
	cmp #$a0	//help
	bne +
	lda #$c0
	sta $41
+
return_home:
	LDA $16
	AND #$01
	BNE _d28d
	LDA $16
	AND #$02
	BEQ _d27d
	lda #$04
	sta {save_bank}
	lda #$d2
	sta $0191
	lda #$7a
	sta $0190	
	jmp back_to_original_title
_d27d:
	lda #$04
	sta {save_bank}
	lda #$d2
	sta $0191
	lda #$7d
	sta $0190	
	jmp back_to_original_title	
_d28d:
	lda #$04
	sta {save_bank}
	lda #$d2
	sta $0191
	lda #$8d
	sta $0190	
	jmp back_to_original_title	
	
	