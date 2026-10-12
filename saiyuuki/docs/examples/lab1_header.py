#!/usr/bin/env python3
"""Lab 1 - read the iNES header of a ROM.   usage: python3 lab1_header.py game.nes"""
import sys
rom = open(sys.argv[1], 'rb').read()
assert rom[:4] == b'NES\x1a', 'not an iNES file'
prg_banks, chr_banks, f6, f7 = rom[4], rom[5], rom[6], rom[7]
mapper = (f6 >> 4) | (f7 & 0xF0)
nes2 = (f7 & 0x0C) == 0x08
print('PRG-ROM : %d x 16 KB = %d KB' % (prg_banks, prg_banks * 16))
print('CHR-ROM : %d x 8 KB  %s' % (chr_banks, '(0 => the game uses CHR-RAM: graphics live inside PRG)' if chr_banks == 0 else ''))
print('mapper  :', mapper, '(2 = UNROM: switch the 16 KB window at $8000, last bank fixed at $C000)' if mapper == 2 else '')
print('mirror  :', 'vertical' if f6 & 1 else 'horizontal', '| battery:', bool(f6 & 2), '| trainer:', bool(f6 & 4), '| NES 2.0:', nes2)
print('file size %d = 16 + %d' % (len(rom), len(rom) - 16))
for b in range(prg_banks):
    d = rom[16 + b * 0x4000: 16 + (b + 1) * 0x4000]
    print('bank %2d  first bytes %s  free(0xFF) bytes: %d' % (b, d[:4].hex(' '), d.count(0xFF)))
