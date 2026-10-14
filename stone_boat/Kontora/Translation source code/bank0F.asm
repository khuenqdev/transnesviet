bank $0F
org $F989
	LDA $8000
	STA $07EC //save current bank
_F98F:
	STY $8000
	INY
	STY $A000
	RTS
	
org $F99D
	PHA
	TYA
	PHA
	LDA $8000
	STA $07ED
	LDY #$12
	JSR $F98F //change to bank $02
	PLA
	TAY
	PLA
	RTS
org $F9AF
	PHA
	TYA
	PHA
	LDY $07ED
	JSR $F98F
	PLA
	TAY
	PLA
	RTS
org $F9BC
	PHA
	LDA $1B
	ORA #$80
	STA $1B
	PLA
	JSR $F99D //change to bank $02
	JSR $87A2 //bank $02 
	JSR $F9AF
	LDA $1B
	AND #$7F
	STA $1B
	RTS
	
//###########
// AREA TEXT POINTER
//##########
	
org $F578
	dw $F614 //1 player
	dw $F614 //1 player
	dw $F61F //2 player
	dw $F606 //player select
	dw $F5C6 //area:
	dw $F5C6 //area:
	dw $F666
	dw $F62B //rest
	dw $F635 //rest
	dw $F63F //hi (score)
	dw $F64C //1P
	dw $F659 //2P
	dw $F5C6  //area:
	dw gameover
	dw continue
	dw $F5DD //game over
	dw $F5E9 //game over
	dw jungle
	dw base1
	dw waterfall
	dw base2
	dw snowfield
	dw energy_field
	dw hangar
	dw alien
	dw $F6E1
	dw $F6F2
	dw $F703
	dw $F714
	dw $F725
	dw $F736
	dw $F747
	dw $F758
	dw $F769
	dw $F77A
	dw $F78B
	dw $F7A0
	dw $F7E4
	dw $F7F6
	
table "ANSI.tbl"

org $FB40
jungle:
	dw $EC20
	db "RUNG GIA"
	db $FD
	dw $CD20
	db $83
	db $FD
	dw $D320
	db $33
	db $FE
base1:
	dw $EC20
	db "CAN CU 1"
	db $FD
	dw $CD20
	db $3B
	db $FD
	dw $D120
	db $82
	db $FE
waterfall:
	dw $EC20
	db "THAC NUOC"
	db $FD
	dw $CE20
	db $32
	db $FD
	dw $D220
	db $81, $82
	db $FE
base2:
	dw $EC20
	db "CAN CU 2"
	db $FD
	dw $CD20
	db $3B
	db $FD
	dw $D120
	db $82
	db $FE
snowfield:
	dw $EC20
	db $92
	db "ONG TUYET"
	db $FD
	dw $CD20
	db $38
	db $FD
	dw $D420
	db $37
	db $FE
energy_field:
	dw $EC20
	db "KHU TU TRUONG"
	db $FD
	dw $D120
	db $83
	db $FD
	dw $D520
	db $81, $83
	db $FE	
hangar:
	dw $EC20
	db "KHO CHUA"
	db $FD
	dw $D220
	db $82
	db $FE
alien:
	dw $EC20
	db "HANG O ALIEN"
	db $FD
	dw $D120
	db $39
	db $FE
gameover:
	dw $2A22
	db "HET MANG"
	db $FD
	dw $0B22
	db $37
	db $FD
	dw $4F22
	db $80
	db $FE
	
org $F689
continue:
	dw $8C22
	db "CHIEN TIEP"
	db $FD
	dw $CC22
	db "NGHI CHOI"
	db $FD
	dw $6F22
	db $37, $00, $00, $00, $00, $37
	db $FD
	dw $AF22	
	db $34, $00, $00, $00, $81
	db $FE



//####################
// FONT
//###################
bank $1F
org $0800
	incbin "fontvn.bin"
bank $17
org $1800
	incbin "fontvn2.bin"	
	
bank $10
org $8000
	incbin "fontvn3.bin"	

bank $13
org $8C00
	incbin "fontvn4.bin"	

bank $14
org $9C00
	incbin "fontvn5.bin"	
	
bank $18
org $0400
	incbin "fontvn6.bin"	
	
org $0000
	incbin "title1.bin"
	incbin "title2.bin"
	incbin "title3.bin"
	incbin "title4.bin"
	
bank $1C
org $1000
	incbin "title5.bin"
	incbin "title6.bin"
	incbin "title7.bin"
	
bank $13
org $00
	incbin "title8.bin"
	incbin "title9.bin"
	incbin "title10.bin"
	
bank $17
org $1400
	incbin "title11.bin"
	
org $1C00
	incbin "title12.bin"
bank $1F
org $00
	incbin "title13.bin"

