#!/usr/bin/env python3
"""Lab 3 - dump the dialog table of Saiyuuki World (needs rom/original.nes; uses tools/jtable.py).
A pointer table at $9E77 (bank 3) holds 213 little-endian addresses; every record is [flags][len]([addr])[tile codes...]."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
from jtable import dec
rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'rom', 'original.nes'), 'rb').read()[16:]
bank3 = rom[3 * 0x4000:4 * 0x4000]                      # bank 3 is mapped at $8000, so file offset = address - $8000
w16 = lambda a: bank3[a - 0x8000] | bank3[a - 0x8000 + 1] << 8
for i in range(int(sys.argv[2]) if len(sys.argv) > 2 else 20):
    p = w16(0x9E77 + 2 * i)
    flags, ln = bank3[p - 0x8000], bank3[p - 0x8000 + 1]
    q = p + 2
    if flags & 0x10: q += 2
    codes = bank3[q - 0x8000:q - 0x8000 + ln]
    print('%3d  rec=$%04X flags=$%02X len=%2d  %s | %s' % (i, p, flags, ln, codes.hex(' '), dec(codes)))
