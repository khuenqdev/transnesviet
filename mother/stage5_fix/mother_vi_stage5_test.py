#!/usr/bin/env python3
"""Stage-5 emulator test: python mother_vi_stage5_test.py mother_vi.nes outdir
Plays: naming screen, types 'Đưn' with the new keys, enters the reserved name 'Mary' (error message),
confirm screen and the opening story. Saves numbered screenshots."""
import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mmc3 import MMC3
from mother_vi_preview import press, idle, screen
from PIL import Image
rom=open(sys.argv[1],'rb').read(); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
n=MMC3(rom); k=[0]
def cp(name):
    k[0]+=1; Image.fromarray(screen(n)).resize((512,480),Image.NEAREST).save(os.path.join(out,'%02d_%s.png'%(k[0],name)))
    print(name, 'name buf', bytes(n.ram[0x580:0x588]).hex(), flush=True)
def keys(seq):
    for b in seq: press(n,b,3,12)
idle(n,400); press(n,'START',4,120); press(n,'START',4,120); press(n,'A',4,120)
idle(n,200); press(n,'START',4,150); press(n,'A',4,150); cp('naming_boy')
# name 1: Đ ư n  (Đ row1 col7, ư row3 col14, n row2 col14)
keys(['D']+['R']*7+['A']); keys(['D','D']+['R']*7+['A']); keys(['U','A'])
cp('typed_name1')
keys(['U','U']+['L']*14); keys(['D','D','D','D','R','A']); idle(n,60)
cp('naming_girl')
# name 2: Mary -> reserved -> error
keys(['R']*13+['A']); keys(['D','D']+['L']*13+['A']); keys(['D']+['R']*3+['A']); keys(['R']*8+['A'])
keys(['U','U','U']+['L']*11+['D','D','D','D','R','A']); idle(n,40)
cp('error_message')
press(n,'A',3,60); idle(n,30); cp('after_error')
pickle.dump(n,open(os.path.join(out,'after_error.pkl'),'wb'))
# finish name 2 and others with "AA"
keys(['A','A','D','D','D','D','R','A']); idle(n,60)
for _ in range(3):
    keys(['A','A','D','D','D','D','R','A']); idle(n,60)
cp('confirm')
press(n,'A',3,30)
for i in range(10):
    idle(n,150)
    if i==2: cp('intro_1')
    if i==4: cp('intro_1b'); press(n,'A',3,10)
    if i==7: cp('intro_2')
pickle.dump(n,open(os.path.join(out,'intro_end.pkl'),'wb'))
print('done',flush=True)
