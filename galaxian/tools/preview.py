import sys
from PIL import Image
import numpy as np
import importlib, glyphs; importlib.reload(glyphs)
from glyphs import G
rom=open('galaxian.nes','rb').read(); chrr=rom[16+8192:]
def font_tile(t):
    b=chrr[0x1000+t*16:0x1000+t*16+16]
    return [[((b[r]|b[r+8])>>(7-c))&1 for c in range(8)] for r in range(8)]
ASCII={' ':0x10,'-':0x2B,'.':0x2C,':':0xA3}
for i,ch in enumerate('0123456789'): ASCII[ch]=i
for i in range(26): ASCII[chr(65+i)]=0x11+i
def glyph(ch):
    if ch in G: return [[1 if x=='#' else 0 for x in r] for r in G[ch]]
    if ch==':': 
        b=chrr[0x1000+0xA3*16:0x1000+0xA3*16+8]; return [[(b[r]>>(7-c))&1 for c in range(8)] for r in range(8)]
    return font_tile(ASCII[ch])
def render(lines,S=4):
    W=max(len(l) for l in lines)*8; H=len(lines)*16
    img=np.zeros((H,W,3),np.uint8)
    for li,l in enumerate(lines):
        for ci,ch in enumerate(l):
            gl=glyph(ch)
            for r in range(8):
                for c in range(8):
                    if gl[r][c]: img[li*16+4+r,ci*8+c]=(236,106,100) if li%2==0 else (176,98,236)
    im=Image.fromarray(img).resize((W*S,H*S),Image.NEAREST)
    return im
lines=["NGƯỜI 1  ĐIỂM CAO  NGƯỜI 2","NHIỆM VỤ: DIỆT SINH VẬT LẠ","   CHÚNG TA LÀ GALAXIAN","      - BẢNG ĐIỂM -","   ĐỘI HÌNH  LAO XUỐNG","       60          150 ĐIỂM",
"         1 NGƯỜI CHƠI","    BẢO LƯU MỌI QUYỀN","         KẾT THÚC","         SẴN SÀNG","        TẠM NGƯNG","ÀẢẠÚỤÌỌẬỆỘỂẾỀỐƯƠỜẴĐ"]
render(lines,int(sys.argv[1]) if len(sys.argv)>1 else 3).save('preview.png')
