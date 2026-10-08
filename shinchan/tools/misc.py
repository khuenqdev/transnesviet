# Non-dialogue text: stage titles, title menu, game over, continue, names, settings, HUD
import sys, re
sys.path.insert(0, '/home/claude/w')
import vfont, rle, tr, build
from build import banks, put, get, expect, assemble, FIXED, CHR
from screens import find_calls, decomp
def rows2(text, width=None, align='left'):
    t=text.upper()
    if width is not None:
        pad=width-len(t); assert pad>=0, text
        t = ' '*(pad//2)+t+' '*(pad-pad//2) if align=='center' else t+' '*pad
    return vfont.two_rows(t)
def pkt(tiles): assert len(tiles)<128; return bytes([len(tiles)]+list(tiles))
class Free:
    def __init__(s,bank,start,end): s.bank=bank; s.p=start; s.end=end
    def add(s,data):
        a=s.p; assert a+len(data)<=s.end, ('free space exhausted', s.bank)
        put(s.bank,a,data); s.p+=len(data); return a
f3=Free(3, build.FREE3, 0xB0FF)
for c,(pt,at) in enumerate([(0xB7B3,0xB8C1),(0xB7F7,0xB8CD),(0xB848,0xB8D9),(0xB8AC,0xB8E5)]):
    for s,title in enumerate(tr.STAGES[c]):
        t=title.upper(); n=len(t); assert n<=18
        col=7+(18-n)//2; up,lo=vfont.two_rows(t)
        top=f3.add(pkt(up)); bot=f3.add(pkt(lo))
        put(3,pt+4*s,bytes([top&0xFF,top>>8,bot&0xFF,bot>>8]))
        put(3,at+4*s,bytes([(0x2100+col)&0xFF,0x21,(0x2120+col)&0xFF,0x21]))
f15=Free(FIXED,0xFBC0,0xFFF0)
def p15(tiles): return f15.add(pkt(tiles))
MENU=["CHẾ ĐỘ TRUYỆN","CHẾ ĐỘ VÔ TẬN","CHẾ ĐỘ ĐỐI KHÁNG"]
erase=[(3,28),(7,18),(8,14)]; ptrs=[]; addrs=[]
for i,item in enumerate(MENU):
    up,lo=vfont.two_rows(item.upper()); row=22+2*i; c0,w=erase[i]
    line=[0]*max(w,13+len(lo)-c0)
    for k,t in enumerate(lo): line[13-c0+k]=t
    ptrs+=[p15(up),p15(line)]; addrs+=[0x2000+(row-1)*32+13, 0x2000+row*32+c0]
expect(FIXED,0xF686,'92F69AF6B7F6B9F6CCF6CEF6')
put(FIXED,0xF686,b''.join(bytes([p&0xFF,p>>8]) for p in ptrs))
expect(4,0x869D,'AD22C322F422072334234823'.replace(' ',''))
put(4,0x869D,b''.join(bytes([a&0xFF,a>>8]) for a in addrs))
u1,l1=rows2("THUA RỒI!",15,'center'); u2,l2=rows2("KHÔNG BỎ CUỘC!",14,'center')
go=[p15(u1),p15(l1),p15(u2),p15(l2)]
expect(FIXED,0xF3A7,'AFF3BFF3CFF3DCF3'); put(FIXED,0xF3A7,b''.join(bytes([p&0xFF,p>>8]) for p in go))
expect(4,0x8A42,'A9EC'); put(4,0x8A42,bytes([0xA9,0xEA]))
expect(4,0x8A5F,'A90C'); put(4,0x8A5F,bytes([0xA9,0x0A]))
uc,lc=vfont.two_rows("TIẾP   THÔI"); cont=[p15(uc),p15(lc)]
expect(FIXED,0xF667,'6BF66EF6'); put(FIXED,0xF667,b''.join(bytes([p&0xFF,p>>8]) for p in cont))
OPP=["SHIRO","SHIRO","MISAE","MISAE","MASAO","NENE","KAZAMA","CÔ YOSHINAGA","CÔ MATSUZAKA","HIỆU TRƯỞNG","MẸ NENE","ACTION KAMEN","ACTION KAMEN"]
top_t=[];bot_t=[];cache={}
for nm in OPP:
    if nm not in cache:
        u,l=rows2(nm,12); cache[nm]=(p15(u),p15(l))
    top_t.append(cache[nm][0]); bot_t.append(cache[nm][1])
expect(FIXED,0xF404,'1EF41EF421F421F4')
put(FIXED,0xF404,b''.join(bytes([p&0xFF,p>>8]) for p in bot_t))
put(FIXED,0xF464,b''.join(bytes([p&0xFF,p>>8]) for p in top_t))
expect(4,0x8495,'A9F0'); put(4,0x8495,bytes([0xA9,0xEE]))
expect(4,0x84B6,'A910'); put(4,0x84B6,bytes([0xA9,0x0E]))
ord_top=[];ord_bot=[]
for o in ["MÀN 1","MÀN 2","MÀN 3","     "]:
    u,l=vfont.two_rows(o); ord_top.append(p15(u)); ord_bot.append(p15(l))
put(FIXED,0xF3E9,b''.join(bytes([p&0xFF,p>>8]) for p in ord_bot))
ordtop_tab=f15.add(b''.join(bytes([p&0xFF,p>>8]) for p in ord_top))
f4=Free(4,0xBEB8,0xC000)
ord_code,_=assemble("""
ORD:    LDA $%04X,Y
        STA $00
        LDA $%04X,Y
        STA $01
        LDA #$21
        STA $03
        LDA #$B3
        STA $04
        TYA
        PHA
        JSR $C4AE
        PLA
        TAY
        LDA $F3E9,Y
        STA $00
        LDA $F3EA,Y
        STA $01
        LDA #$21
        STA $03
        LDA #$D3
        STA $04
        JMP $C4AE
"""%(ordtop_tab,ordtop_tab+1), f4.p)
ORD_ADDR=f4.add(ord_code)
expect(4,0x8445,'B9E9F38D0000B9EAF38D0100A9218D0300A9D38D040020AEC4')
put(4,0x8445,bytes([0x20,ORD_ADDR&0xFF,ORD_ADDR>>8])+bytes([0xEA])*22)
expect(4,0x8474,'A977'); put(4,0x8474,bytes([0xA9,0x79]))
# ---- RLE screen layouts stored in CHR banks $78-$7F
SCR_BASE=0x78*0x400; screens={}
for bank,addr,v in find_calls():
    src=v[0]|v[1]<<8; cnt=v[4]|v[5]<<8; out,end=decomp(src,cnt)
    screens[src]={'bank':bank,'call':addr,'cnt':cnt,'map':list(out),'len':end-src}
def write(src,row,col,text,mark_row=True,clear=0):
    m=screens[src]['map']; up,lo=vfont.two_rows(text.upper())
    for k in range(clear):
        m[row*32+col+k]=0
        if mark_row: m[(row-1)*32+col+k]=0
    for k,(u,l) in enumerate(zip(up,lo)):
        m[row*32+col+k]=l
        if mark_row: m[(row-1)*32+col+k]=u
        else: assert u==0
def tile(src,row,col,t): screens[src]['map'][row*32+col]=t
write(0x1CEC,13,6,"",clear=20); write(0x1CEC,13,11,"NGHỈ CHÚT?")
write(0x1CEC,22,7,"  1P"); write(0x1CEC,22,18,"  2P")
write(0x0A7D,25,8,"",clear=16); write(0x0A7D,25,10,"TIẾP"); write(0x0A7D,25,18,"THÔI")
for s in (0x0DED,0x1721):
    write(s,7,5,"",clear=11); write(s,7,5,"TỐC ĐỘ KHỐI")
    write(s,11,5,"",clear=11); write(s,11,5,"LOẠI KHỐI")
    write(s,27,5,"",clear=23); write(s,27,5,"BẮT ĐẦU?"); write(s,27,18,"CHƠI"); write(s,27,24,"THÔI")
write(0x1721,15,5,"",clear=11); write(0x1721,15,5,"CẤP ĐỘ")
write(0x1721,19,5,"",clear=8); write(0x1721,19,5,"ĐỐI THỦ")
write(0x0DED,15,5,"",clear=23,mark_row=False); write(0x0DED,16,5,"",clear=23)
write(0x0DED,16,14,"MỐC THẮNG THUA")
for r in (18,21):
    write(0x0DED,r,7,"",clear=7); write(0x0DED,r,7,"NGƯỜI %d"%(1 if r==18 else 2))
write(0x0DED,23,5,"",clear=22); write(0x0DED,23,5,"TRÁI: GIẢM  PHẢI: TĂNG")
for c in range(19,24): tile(0x1421,14,c,0)
write(0x1421,16,6,"",clear=9); write(0x1421,16,6,"ĐỐI THỦ")
write(0x1421,20,14,"",clear=10); write(0x1421,20,14,"TIẾP TỤC"); tile(0x1421,20,23,0x44)
write(0x1421,23,14,"",clear=8); write(0x1421,23,14,"THÔI")
p=0x0400; newsrc={}
for s in sorted(screens):
    data=rle.compress(screens[s]['map'][:screens[s]['cnt']])
    assert rle.decompress(data,screens[s]['cnt'])[0]==screens[s]['map'][:screens[s]['cnt']]
    newsrc[s]=p; CHR[SCR_BASE+p:SCR_BASE+p+len(data)]=data; p+=len(data)
assert p<=0x2000, ('screen data overflow', hex(p))
for s,info in screens.items():
    bank,addr=info['bank'],info['call']; base=0x8000 if bank<FIXED else 0xC000
    if bank==7: bank=FIXED; base=0xC000
    seg=bytes(banks[bank][addr-40-base:addr-base]); lo_ok=hi_ok=False
    for m in re.finditer(rb'\xA9(.)\x85\x00',seg,re.S):
        if m.group(1)[0]==s&0xFF: banks[bank][addr-40+m.start()+1-base]=newsrc[s]&0xFF; lo_ok=True
    for m in re.finditer(rb'\xA9(.)\x85\x01',seg,re.S):
        if m.group(1)[0]==s>>8: banks[bank][addr-40+m.start()+1-base]=newsrc[s]>>8; hi_ok=True
    assert lo_ok and hi_ok, hex(s)
STATS={'screens_end':p,'free15':f15.end-f15.p,'free3':f3.end-f3.p}
