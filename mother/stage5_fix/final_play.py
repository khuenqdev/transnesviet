
import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mmc3 import MMC3
from mother_vi_preview import press, idle, screen
from PIL import Image
rom=open(sys.argv[1],'rb').read(); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
n=MMC3(rom); shots=[]
def cp(name):
    img=screen(n); shots.append(name); Image.fromarray(img).resize((512,480),Image.NEAREST).save(os.path.join(out,'%02d_%s.png'%(len(shots),name)))
idle(n,400); press(n,'START',4,120); press(n,'START',4,120); press(n,'A',4,120)
idle(n,200); press(n,'START',4,150); press(n,'A',4,150); cp('naming_prompt')
for _ in range(5):
    for b in ['A','A','D','D','D','D','R','A']: press(n,b,3,12)
    idle(n,60)
cp('name_confirm')
press(n,'A',3,30)
for i in range(8):
    idle(n,150)
    if i==3: press(n,'A',3,10)
    if i==1: cp('intro_1')
cp('intro_2')
for i in range(30):
    press(n,'A',2,90)
    if i in (2,6,10,14): cp('opening_%d'%i)
cp('field_menu')
pickle.dump(n,open(os.path.join(out,'field.pkl'),'wb'))
press(n,'A',2,200); cp('talk_nobody')
press(n,'A',2,60); press(n,'A',2,60)
press(n,'D',2,30); press(n,'A',2,120); cp('goods')
press(n,'B',2,60); press(n,'B',2,60)
press(n,'R',2,30); press(n,'D',2,30); press(n,'A',2,120); cp('state')
print('ok',shots)
