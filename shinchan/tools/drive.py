import sys,pickle; sys.path.insert(0,'/home/claude/w')
from emu16 import NES16
from PIL import Image
A,B,SEL,START,UP,DOWN,LEFT,RIGHT=1,2,4,8,16,32,64,128
class D:
    def __init__(s,rom): s.n=NES16(rom)
    def run(s,k=1,pad=0):
        for _ in range(k): s.n.pad[0]=pad; s.n.run_frame()
    def press(s,b,hold=3,after=10): s.run(hold,b); s.run(after,0)
    def shot(s,fn): Image.fromarray(s.n.render()).resize((512,480),Image.NEAREST).save(fn)
