copy Test.nes ninjavn.nes

xkas -o ninjavn.nes main.asm 
atlas -d log.txt ninjavn.nes mtevn.txt
atlas -d log.txt ninjavn.nes mtevn2.txt
atlas -d log.txt ninjavn.nes mtevn3.txt
atlas -d log.txt ninjavn.nes kaiwavn.txt
atlas -d log.txt ninjavn.nes kaiwavn2.txt
atlas -d log.txt ninjavn.nes kaiwavn3.txt

pause

