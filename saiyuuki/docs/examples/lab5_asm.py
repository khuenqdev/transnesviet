#!/usr/bin/env python3
"""Lab 5 - assemble a tiny 6502 routine with tools/asm6502.py and disassemble it again with tools/dis6502.py."""
import sys, os
T = os.path.join(os.path.dirname(__file__), '..', '..', 'tools'); sys.path.insert(0, T)
from asm6502 import assemble
from dis6502 import dis1
src = '''
        .org $C000
start:  LDA #$00        ; clear A
        LDX #$10
loop:   STA $0300,X     ; fill 16 bytes of RAM with A
        INX
        BNE loop
        RTS
'''
segs, labels = assemble(src, 0xC000)
addr, code = segs[0]
print('machine code:', code.hex(' '))
pc = addr
while pc < addr + len(code):
    text, n = dis1(None, pc, lambda a: code[a - addr])
    print('$%04X  %-9s %s' % (pc, code[pc - addr:pc - addr + n].hex(' '), text)); pc += n
