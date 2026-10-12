import sys
from PIL import Image
for p in sys.argv[1:]:
    im=Image.open(p); im=im.resize((im.width*2,im.height*2),Image.NEAREST); im.save(p[:-4]+'.png')
