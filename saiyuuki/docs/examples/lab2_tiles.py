#!/usr/bin/env python3
"""Lab 2b - draw the 512 tiles of a VRAM dump as a PNG (left = table $0000, right = table $1000).
usage: python3 lab2_tiles.py out.vram tiles.png [scale]"""
import sys
from PIL import Image
v = open(sys.argv[1], 'rb').read(); sc = int(sys.argv[3]) if len(sys.argv) > 3 else 3
pal = [(0, 0, 0), (255, 255, 255), (160, 160, 160), (80, 80, 200)]
im = Image.new('RGB', (2 * 16 * 9 * sc, 16 * 9 * sc), (40, 0, 40))
for table in range(2):
    for t in range(256):
        base = table * 0x1000 + t * 16
        for y in range(8):
            p0, p1 = v[base + y], v[base + 8 + y]             # bit plane 0 byte, bit plane 1 byte
            for x in range(8):
                c = ((p0 >> (7 - x)) & 1) | (((p1 >> (7 - x)) & 1) << 1)
                X = table * 16 * 9 * sc + (t % 16) * 9 * sc + x * sc; Y = (t // 16) * 9 * sc + y * sc
                im.paste(pal[c], (X, Y, X + sc, Y + sc))
im.save(sys.argv[2]); print('saved', sys.argv[2])
