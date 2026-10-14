bank $12
define	save_bank $4c
define save_a	$4d
define	table		$0192
define	pos_table	$01D0

org $A000
bank11_code:
	LDA $0484,x
	AND #$20
	STA $03
	LDY $048D,x
	cpy #$74
	bne +	
	ldx #$00
-
	lda yattaro,x
	sta {table},x
	inx
	cmp #$ff
	bne -
back:
	lda #$8b
	sta $0191
	lda #$e3
	sta $0190
	lda #$0a
	sta {save_bank}
	lda #$92
	sta $00
	lda #$01
	sta $01
//	jsr write_pos_table
	jmp back_to_original_title
+
	cpy #$da
	bne +
	ldx #$00
-
	lda pururun,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$7c
	bne +
	ldx #$00
-
	lda sukasi,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$dd
	bne +
	ldx #$00
-
	lda karamaru,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$db
	bne +
	ldx #$00
-
	lda konnokami,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$dc
	bne +
	ldx #$00
-
	lda gennari,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back		
+	
	cpy #$ee
	bne +
	ldx #$00
-
	lda riki,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$e7
	bne +
	ldx #$00
-
	lda usahime,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$ec
	bne +
	ldx #$00
-
	lda gotton,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$e4
	bne +
	ldx #$00
-
	lda otama,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$eb
	bne +
	ldx #$00
-
	lda mietoru,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$e5
	bne +
	ldx #$00
-
	lda omitsu,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$ed
	bne +
	ldx #$00
-
	lda nekky,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$e8
	bne +
	ldx #$00
-
	lda oyako,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back
+
	cpy #$e6
	bne +
	ldx #$00
-
	lda wanko,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back	
+
	cpy #$33
	bne +
	ldx #$00
-
	lda purple,x
	sta {table},x
	inx
	cmp #$ff
	bne -
	jmp back		
+
	lda #$8b
	sta $0191
	lda #$d9
	sta $0190
	lda #$0a
	sta {save_bank}
	jmp back_to_original_title

	
write_pos_table:
	ldx #$00
-
	lda oam_pos,x
	sta {pos_table},x
	inx
	cpx #$10
	bne -
	rts

oam_pos:
	db $E8, $F0, $F8, $00, $08, $10, $18, $20, $28, $30, $38, $40, $48, $50, $58, $60


yattaro:
	db $99, $5a, $03
	db $a6, $49, $03
	db $b9, $48, $03
	db $b9, $47, $03
	db $a6, $4a, $03
	db $b7, $4b, $03
	db $c1, $5b, $03, $ff
pururun:
	db $90, $5a, $03
	db $ba, $49, $03
	db $b7, $48, $03
	db $ba, $47, $03
	db $b7, $4a, $03
	db $ba, $4b, $03
	db $b3, $5b, $03, $ff
sukasi:
	db $93, $5a, $03
	db $ba, $49, $03
	db $b0, $48, $03
	db $a6, $47, $03
	db $b8, $4a, $03
	db $ae, $4b, $03, $ff
karamaru:
	db $0b, $5a, $03
	db $26, $49, $03
	db $37, $48, $03
	db $26, $47, $03
	db $32, $4a, $03
	db $26, $4b, $03
	db $37, $5b, $03
	db $3a, $51, $03, $ff

konnokami:
	db $03, $00, $03
	db $26, $01, $03
	db $cf, $01, $02
	db $34, $02, $03
	db $2c, $04, $03
	db $2e, $05, $03
	db $26, $06, $03
	db $d0, $06, $02, $ff

gennari:
	db $11, $5a, $03
	db $3a, $49, $03
	db $26, $48, $03
	db $f1, $48, $04
	
	db $2c, $4a, $03
	db $2e, $4b, $03
	db $26, $5b, $03
	db $d0, $5b, $02, $ff
	
riki:
	db $92, $00, $03
	db $aE, $01, $04
	db $b0, $02, $03
	db $aE, $03, $04
	db $b3, $04, $03
	db $b4, $05, $04
	db $b8, $06, $03
	db $ae, $0d, $04
	db $b3, $1c, $03, $ff
	
usahime:
	db $95, $00, $03
	db $b8, $01, $03
	db $a6, $02, $03
	db $ad, $03, $03
	db $ae, $04, $03
	db $b2, $05, $03
	db $c8, $06, $03, $ff
gotton:
	db $07, $00, $03
	db $34, $01, $03
	db $39, $02, $03
	db $39, $03, $03
	db $34, $04, $03
	db $33, $05, $03, $ff
otama:
	db $0f, $5a, $03
	db $39, $49, $03
	db $26, $48, $03
	db $32, $47, $03
	db $26, $4a, $03, $ff
	
mietoru:
	db $0d, $00, $03
	db $2e, $01, $03
	db $c8, $02, $03
	db $39, $03, $03
	db $34, $04, $03
	db $37, $05, $03
	db $3a, $06, $03, $ff
omitsu:
	db $8f, $80, $03
	db $b2, $81, $03
	db $ae, $82, $03
	db $b9, $83, $03
	db $b8, $84, $03
	db $ba, $85, $03, $ff
nekky:
	db $0e, $80, $03
	db $48, $81, $03
	db $30, $82, $03
	db $30, $83, $03
	db $3e, $84, $03, $ff
oyako:
	db $5e, $00, $03
	db $72, $02, $03
	db $66, $03, $03
	db $f1, $03, $04
	db $68, $05, $03
	db $74, $06, $03
	db $73, $0d, $03, $ff
wanko:
	db $57, $00, $03
	db $66, $01, $03
	db $73, $02, $03
	db $70, $03, $03
	db $74, $04, $03, $ff
purple:
	db $14, $00, $03
	db $2e, $01, $03
	db $cf, $01, $02
	db $26, $02, $03, $ff
	
	