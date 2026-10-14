bank $05
org $B850
	lda $c8e0,y
	sta $07f4,x
	jmp $c8cc