#!/usr/bin/env python3
"""Stage 4 QA – test ROM where scene #2 (first in-game dialogue) is replaced by scene N.
usage: scene_jump.py in.gba out.gba N"""
import sys,struct
d=bytearray(open(sys.argv[1],'rb').read()); n=int(sys.argv[3])
struct.pack_into('<I',d,0x780000+8,struct.unpack_from('<I',d,0x780000+4*n)[0]); open(sys.argv[2],'wb').write(d)
