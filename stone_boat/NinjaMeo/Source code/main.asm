arch nes.cpu
header
banksize $2000

define txt_spd	$0438
define pause		$0437
define line			$043D
define text_trigger $B0
define sitaten			$B1

incsrc "bank01.asm"
incsrc "bank03.asm"
incsrc "bank07.asm"
incsrc "bank0E.asm"
incsrc "bank0F.asm"
incsrc "bank10.asm"
incsrc "bank11.asm"
incsrc "bank12.asm"
incsrc "bank13.asm"
incsrc "bank1E.asm"
incsrc "bank1F.asm"
