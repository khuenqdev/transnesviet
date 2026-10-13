import sys
from PIL import Image
d=sys.argv[1]; names=sys.argv[2].split(','); cols=int(sys.argv[3]) if len(sys.argv)>3 else 4
ims=[Image.open('%s/%s.png'%(d,n)) for n in names]
rows=(len(ims)+cols-1)//cols
w=Image.new('RGB',(256*cols,240*rows));[w.paste(im,(256*(i%cols),240*(i//cols))) for i,im in enumerate(ims)]
w.save('%s/sheet.png'%d)
