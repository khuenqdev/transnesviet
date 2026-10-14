bank $03
org $B850
flaming:
	lda $c8e0,y
	sta $07f4,x
	lda $1f0
	bne +
	jmp $c8cc
+
	cpy #$28
	bne +
	lda #$40
	sta $07f4
	lda #$41
	sta $07f5
	jmp $c8cc
+
	cpy #$29
	bne +
	lda #$18
	sta $07f4
	lda #$3d
	sta $07f5
	jmp $c8cc
+
	cpy #$2a
	bne +
	lda #$19
	sta $07f4
	lda #$3f
	sta $07f5
	jmp $c8cc
+
	lda #$1a
	sta $07f4
	lda #$78
	sta $07f5
	jmp $c8cc