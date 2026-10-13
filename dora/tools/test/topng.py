import sys,glob
from PIL import Image
for f in glob.glob(sys.argv[1]+'/*.ppm'):
    Image.open(f).save(f[:-4]+'.png')
