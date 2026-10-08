# Vietnamese uppercase font (2-tile-high text: upper "mark" tile + letter tile)
# Style follows glyphs.py: 2-px vertical strokes, col 0 blank.
import unicodedata
BL = "........"
L = {}
def g(ch, *rows):
    assert len(rows) == 6, ch
    for r in rows: assert len(r) == 8, (ch, r)
    L[ch] = list(rows)
g('A', "...###..", "..##.##.", ".##...##", ".#######", ".##...##", ".##...##")
g('B', ".######.", ".##...##", ".######.", ".##...##", ".##...##", ".######.")
g('C', "..#####.", ".##...##", ".##.....", ".##.....", ".##...##", "..#####.")
g('D', ".#####..", ".##..##.", ".##...##", ".##...##", ".##..##.", ".#####..")
g('E', ".######.", ".##.....", ".#####..", ".##.....", ".##.....", ".######.")
g('F', ".######.", ".##.....", ".#####..", ".##.....", ".##.....", ".##.....")
g('G', "..#####.", ".##.....", ".##.####", ".##...##", ".##...##", "..#####.")
g('H', ".##...##", ".##...##", ".#######", ".##...##", ".##...##", ".##...##")
g('I', "..####..", "...##...", "...##...", "...##...", "...##...", "..####..")
g('J', "....####", ".....##.", ".....##.", ".##..##.", ".##..##.", "..####..")
g('K', ".##..##.", ".##.##..", ".####...", ".##.##..", ".##..##.", ".##...##")
g('L', ".##.....", ".##.....", ".##.....", ".##.....", ".##.....", ".######.")
g('M', ".##...##", ".###.###", ".#######", ".##.#.##", ".##...##", ".##...##")
g('N', ".##...##", ".###..##", ".####.##", ".##.####", ".##..###", ".##...##")
g('O', "..#####.", ".##...##", ".##...##", ".##...##", ".##...##", "..#####.")
g('P', ".######.", ".##...##", ".##...##", ".######.", ".##.....", ".##.....")
g('Q', "..#####.", ".##...##", ".##...##", ".##.#.##", ".##..##.", "..###.##")
g('R', ".######.", ".##...##", ".##...##", ".######.", ".##..##.", ".##...##")
g('S', "..#####.", ".##.....", "..#####.", "......##", ".##...##", "..#####.")
g('T', ".######.", "...##...", "...##...", "...##...", "...##...", "...##...")
g('U', ".##...##", ".##...##", ".##...##", ".##...##", ".##...##", "..#####.")
g('V', ".##...##", ".##...##", ".##...##", "..##.##.", "..##.##.", "...###..")
g('W', ".##...##", ".##...##", ".##.#.##", ".#######", ".###.###", ".##...##")
g('X', ".##...##", "..##.##.", "...###..", "...###..", "..##.##.", ".##...##")
g('Y', ".##..##.", ".##..##.", "..####..", "...##...", "...##...", "...##...")
g('Z', ".######.", ".....##.", "....##..", "...##...", "..##....", ".######.")
g('Đ', "..####..", "..##.##.", ".####.##", "..##..##", "..##.##.", "..####..")
g('Ơ', "......##", "..####..", ".##..##.", ".##..##.", ".##..##.", "..####..")
g('Ư', "......##", ".##..##.", ".##..##.", ".##..##.", ".##..##.", "..####..")
g('0', "..####..", ".##..##.", ".##.###.", ".###.##.", ".##..##.", "..####..")
g('1', "...##...", "..###...", "...##...", "...##...", "...##...", "..####..")
g('2', "..####..", ".##..##.", ".....##.", "...##...", "..##....", ".######.")
g('3', ".#####..", ".....##.", "..####..", ".....##.", ".....##.", ".#####..")
g('4', "....##..", "...###..", "..#.##..", ".#..##..", ".######.", "....##..")
g('5', ".######.", ".##.....", ".#####..", ".....##.", ".##..##.", "..####..")
g('6', "..####..", ".##.....", ".#####..", ".##..##.", ".##..##.", "..####..")
g('7', ".######.", ".....##.", "....##..", "...##...", "...##...", "...##...")
g('8', "..####..", ".##..##.", "..####..", ".##..##.", ".##..##.", "..####..")
g('9', "..####..", ".##..##.", ".##..##.", "..#####.", ".....##.", "..####..")
g('!', "...##...", "...##...", "...##...", "...##...", "........", "...##...")
g('?', "..####..", ".##..##.", "....##..", "...##...", "........", "...##...")
g('.', BL, BL, BL, BL, BL, "...##...")
g(',', BL, BL, BL, BL, "...##...", "...##...")
g('-', BL, BL, "..####..", BL, BL, BL)
g(':', BL, "...##...", BL, BL, "...##...", BL)
g('…', BL, BL, BL, BL, BL, ".##.##.#")
g('~', BL, "..##...#", ".#..#.#.", ".....#..", BL, BL)
g("'", "...##...", "...##...", "..##....", BL, BL, BL)
g('"', ".##.##..", ".##.##..", ".#..#...", BL, BL, BL)
g('%', ".##...##", ".##..##.", "....##..", "...##...", "..##.##.", ".##..##.")
g('/', "......##", ".....##.", "....##..", "...##...", "..##....", ".##.....")
g('(', "....##..", "...##...", "..##....", "..##....", "...##...", "....##..")
g(')', "..##....", "...##...", "....##..", "....##..", "...##...", "..##....")
g('+', BL, "...##...", ".######.", "...##...", BL, BL)
g('♥', ".##.##..", "########", "########", ".######.", "..####..", "...##...")
g('♪', "...####.", "...#..#.", "...#..#.", ".###.##.", "####.##.", ".##.....")
g(' ', BL, BL, BL, BL, BL, BL)
DOTBELOW = {'Ạ':'A','Ẹ':'E','Ị':'I','Ọ':'O','Ụ':'U','Ỵ':'Y','Ợ':'Ơ','Ự':'Ư'}
def dot_row(base):
    cols=[c for r in L[base] for c in range(8) if r[c]=='#']
    c=(min(cols)+max(cols))//2
    if base in ('Ơ','Ư'): c=3
    return ''.join('#' if c<=i<=c+1 else '.' for i in range(8))
def lower_tile(ch):
    if ch==',': return L[','] + ["..##....", BL]
    if ch in DOTBELOW:
        b=DOTBELOW[ch]; return L[b]+[BL,dot_row(b)]
    return L[ch]+[BL,BL]
ACUTE=["....##..","...##..."]; GRAVE=["..##....","...##..."]
HOOK=["..###...","....##..","...##..."]; TILDE=["..##..#.",".#..##.."]
HAT=["...##...","..#..#.."]; BREVE=["..#..#..","...##..."]
def upper(top,bottom):
    rows=[BL]*8
    if bottom:
        rows[5:7]=bottom
        if top:
            start=max(0,4-len(top))
            for i,r in enumerate(top): rows[start+i]=r
    else:
        start=7-len(top)
        for i,r in enumerate(top): rows[start+i]=r
    return rows
def right(rows,n=1): return [('.'*n+r)[:8] for r in rows]
MARKS={
 'acute':upper(ACUTE,None),'grave':upper(GRAVE,None),'hook':upper(HOOK,None),'tilde':upper(TILDE,None),
 'hat':[BL]*5+HAT+[BL],'breve':[BL]*5+BREVE+[BL],
 'hat+acute':upper(right(ACUTE,1),HAT),'hat+grave':upper(right(GRAVE,2),HAT),
 'hat+hook':upper(right(HOOK,1),HAT),'hat+tilde':upper(TILDE,HAT),
 'breve+acute':upper(ACUTE,BREVE),'breve+grave':upper(GRAVE,BREVE),
 'breve+hook':upper(HOOK,BREVE),'breve+tilde':upper(TILDE,BREVE)}
CODE={}
order=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")+['Đ','Ơ','Ư']+list("ẠẸỊỌỤỴỢỰ")+['!','?','.',',','-',':','…','~',"'",'"']
for i,ch in enumerate(order): CODE[ch]=0xC0+i
MARKCODE={}
mk=['acute','grave','hook','tilde','hat','breve','hat+acute','hat+grave','hat+hook','hat+tilde','breve+acute','breve+grave','breve+hook','breve+tilde']
for i,m in enumerate(mk): MARKCODE[m]=0xF0+i
extra_slots=[0xA0,0xA1,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xA8,0xA9,0xAA,0xAB,0xB1,0xB2,0xB3,0xB4,0xB5,0xB6]
for s,ch in zip(extra_slots,list("0123456789")+['%','/','(',')','+','♥','♪']): CODE[ch]=s
CODE[' ']=0x00
HAT_OF={'Â':('A','hat'),'Ê':('E','hat'),'Ô':('O','hat'),'Ă':('A','breve')}
TONES={'\u0301':'acute','\u0300':'grave','\u0309':'hook','\u0303':'tilde'}
def decompose(ch):
    ch=ch.upper()
    if ch in CODE: return ch,None
    if ch in HAT_OF: return HAT_OF[ch]
    d=unicodedata.normalize('NFD',ch); base=d[0]
    tone=hat=None; dot=horn=False
    for c in d[1:]:
        if c=='\u0302': hat='hat'
        elif c=='\u0306': hat='breve'
        elif c=='\u031B': horn=True
        elif c=='\u0323': dot=True
        elif c in TONES: tone=TONES[c]
        else: raise ValueError('unknown combining %r in %r'%(c,ch))
    if horn: base={'O':'Ơ','U':'Ư'}[base]
    if dot: base={'A':'Ạ','E':'Ẹ','I':'Ị','O':'Ọ','U':'Ụ','Y':'Ỵ','Ơ':'Ợ','Ư':'Ự'}[base]
    mark = hat+'+'+tone if hat and tone else (hat or tone)
    return base,mark
def encode_char(ch):
    if ch=='đ': ch='Đ'
    b,m=decompose(ch)
    return ([MARKCODE[m]] if m else [])+[CODE[b]]
def two_rows(text):
    up=[];lo=[]
    for ch in text:
        if ch=='đ': ch='Đ'
        b,m=decompose(ch); up.append(MARKCODE[m] if m else 0); lo.append(CODE[b])
    return up,lo
def tile_bytes(rows):
    p=[]
    for r in rows:
        v=0
        for c in range(8):
            if r[c]=='#': v|=0x80>>c
        p.append(v)
    return bytes(p+p)
def build_chr(chr_data):
    chr_data=bytearray(chr_data)
    def put(bank1k,tile,rows):
        o=bank1k*0x400+(tile&0x3F)*16; chr_data[o:o+16]=tile_bytes(rows)
    for ch,code in CODE.items():
        if code==0: continue
        put(2 if code>=0xC0 else 1, code, lower_tile(ch))
    for m,code in MARKCODE.items(): put(2,code,MARKS[m])
    for code in (0xEF,0xFE,0xFF): put(2,code,[BL]*8)
    return chr_data
