#!/usr/bin/env python3
"""Proportional Vietnamese pixel font for the Saiyuuki World dialog box.
Cell: 12 rows. Baseline row 9 (last x-height row). Caps/ascenders rows 3-9, x-height rows 5-9, descenders rows 10-11.
Diacritics are composed programmatically (NFD) so every Vietnamese letter + tone is supported."""
import unicodedata
CELL_H=12
def G(s): return [r.strip() for r in s.strip('\n').split('\n')]
CAP={ # 7 rows, top row 3
'A':'.###.\n#...#\n#...#\n#####\n#...#\n#...#\n#...#','B':'####.\n#...#\n#...#\n####.\n#...#\n#...#\n####.',
'C':'.###.\n#...#\n#....\n#....\n#....\n#...#\n.###.','D':'####.\n#...#\n#...#\n#...#\n#...#\n#...#\n####.',
'E':'#####\n#....\n#....\n####.\n#....\n#....\n#####','F':'#####\n#....\n#....\n####.\n#....\n#....\n#....',
'G':'.###.\n#...#\n#....\n#.###\n#...#\n#...#\n.###.','H':'#...#\n#...#\n#...#\n#####\n#...#\n#...#\n#...#',
'I':'###\n.#.\n.#.\n.#.\n.#.\n.#.\n###','J':'..##\n...#\n...#\n...#\n#..#\n#..#\n.##.',
'K':'#...#\n#..#.\n#.#..\n##...\n#.#..\n#..#.\n#...#','L':'#....\n#....\n#....\n#....\n#....\n#....\n#####',
'M':'#...#\n##.##\n#.#.#\n#.#.#\n#...#\n#...#\n#...#','N':'#...#\n##..#\n##..#\n#.#.#\n#..##\n#..##\n#...#',
'O':'.###.\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.','P':'####.\n#...#\n#...#\n####.\n#....\n#....\n#....',
'Q':'.###.\n#...#\n#...#\n#...#\n#.#.#\n#..#.\n.##.#','R':'####.\n#...#\n#...#\n####.\n#.#..\n#..#.\n#...#',
'S':'.####\n#....\n#....\n.###.\n....#\n....#\n####.','T':'#####\n..#..\n..#..\n..#..\n..#..\n..#..\n..#..',
'U':'#...#\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.','V':'#...#\n#...#\n#...#\n#...#\n#...#\n.#.#.\n..#..',
'W':'#...#\n#...#\n#...#\n#.#.#\n#.#.#\n##.##\n#...#','X':'#...#\n#...#\n.#.#.\n..#..\n.#.#.\n#...#\n#...#',
'Y':'#...#\n#...#\n.#.#.\n..#..\n..#..\n..#..\n..#..','Z':'#####\n....#\n...#.\n..#..\n.#...\n#....\n#####'}
LOW_X={ # 5 rows, top row 5
'a':'.##.\n...#\n.###\n#..#\n.###','c':'.###\n#...\n#...\n#...\n.###','e':'.##.\n#..#\n####\n#...\n.###',
'm':'##.#.\n#.#.#\n#.#.#\n#.#.#\n#.#.#','n':'###.\n#..#\n#..#\n#..#\n#..#','o':'.##.\n#..#\n#..#\n#..#\n.##.',
'r':'#.#\n##.\n#..\n#..\n#..','s':'.###\n#...\n.##.\n...#\n###.','u':'#..#\n#..#\n#..#\n#..#\n.###',
'v':'#...#\n#...#\n.#.#.\n.#.#.\n..#..','w':'#...#\n#...#\n#.#.#\n#.#.#\n.#.#.','x':'#..#\n#..#\n.##.\n#..#\n#..#','z':'####\n...#\n.##.\n#...\n####',
'i':'#\n#\n#\n#\n#'}
LOW_DESC={ # 7 rows (x-height + 2 desc), top row 5
'g':'.###\n#..#\n#..#\n.###\n...#\n#..#\n.##.','p':'###.\n#..#\n#..#\n###.\n#...\n#...\n#...','q':'.###\n#..#\n#..#\n.###\n...#\n...#\n...#',
'y':'#..#\n#..#\n#..#\n.###\n...#\n#..#\n.##.','j':'.#\n..\n.#\n.#\n.#\n.#\n.#\n.#\n#.'}
LOW_ASC={ # 7 rows top row 3
'b':'#...\n#...\n###.\n#..#\n#..#\n#..#\n###.','d':'...#\n...#\n.###\n#..#\n#..#\n#..#\n.###','f':'.##\n#..\n###\n#..\n#..\n#..\n#..',
'h':'#...\n#...\n###.\n#..#\n#..#\n#..#\n#..#','k':'#...\n#...\n#..#\n#.#.\n##..\n#.#.\n#..#','l':'#\n#\n#\n#\n#\n#\n#'}
LOW_T=G('.#.\n###\n.#.\n.#.\n.#.\n..#')  # t: 6 rows top row 4
DIG={'0':'.##.\n#..#\n#..#\n#..#\n#..#\n#..#\n.##.','1':'.#.\n##.\n.#.\n.#.\n.#.\n.#.\n###','2':'.##.\n#..#\n...#\n..#.\n.#..\n#...\n####',
'3':'.##.\n#..#\n...#\n.##.\n...#\n#..#\n.##.','4':'...#\n..##\n.#.#\n#..#\n####\n...#\n...#','5':'####\n#...\n###.\n...#\n...#\n#..#\n.##.',
'6':'.##.\n#...\n###.\n#..#\n#..#\n#..#\n.##.','7':'####\n...#\n..#.\n..#.\n.#..\n.#..\n.#..','8':'.##.\n#..#\n#..#\n.##.\n#..#\n#..#\n.##.',
'9':'.##.\n#..#\n#..#\n.###\n...#\n...#\n.##.'}
PUNCT={ # (rows, top)
'.':('#',9),',':('.#\n#.',9),'!':('#\n#\n#\n#\n#\n.\n#',3),'?':('.##.\n#..#\n...#\n..#.\n.#..\n....\n.#..',3),
':':('#\n.\n.\n.\n#',5),';':('.#\n..\n..\n.#\n#.',5),'-':('###',7),"'":('#\n#',3),'"':('#.#\n#.#',3),
'(':('.#\n#.\n#.\n#.\n#.\n#.\n.#',3),')':('#.\n.#\n.#\n.#\n.#\n.#\n#.',3),'/':('..#\n..#\n.#.\n.#.\n#..\n#..',4),'~':('.#.#\n#.#.',6),
'+':('.#.\n###\n.#.',6),'%':('#..#\n...#\n..#.\n.#..\n#...\n#..#',4),'*':('#.#\n.#.\n#.#',4),'=':('###\n...\n###',6),
'▼':('#######\n.#####.\n..###..\n...#...',5),'…':('...\n...\n#.#.#',9),
}
ACUTE=G('.#\n#.');GRAVE=G('#.\n.#');HOOK=G('##\n.#');TILDE=G('.#.#\n#.#.')
CIRC=G('.#.\n#.#');BREVE=G('#.#\n.#.')
TONES={'́':ACUTE,'̀':GRAVE,'̉':HOOK,'̃':TILDE}
def _bm(rows): return [[1 if c=='#' else 0 for c in r] for r in rows]
def base_glyph(ch):
    """returns (rows(list of strings), top)"""
    if ch in CAP: return G(CAP[ch]),3
    if ch in LOW_X: return G(LOW_X[ch]),5
    if ch in LOW_DESC: 
        r=G(LOW_DESC[ch]); return r,(5 if ch!='j' else 3)
    if ch in LOW_ASC: return G(LOW_ASC[ch]),3
    if ch=='t': return LOW_T,4
    if ch in DIG: return G(DIG[ch]),3
    if ch in PUNCT:
        r,t=PUNCT[ch]; return G(r),t
    raise KeyError(ch)
_cache={}
def glyph(ch):
    """Return (bitmap rows list[list[int]] of CELL_H rows, advance). bitmap width may exceed base width (marks)."""
    if ch in _cache: return _cache[ch]
    if ch==' ': g=([[0]*3 for _ in range(CELL_H)],3); _cache[ch]=g; return g
    special_d = ch in 'đĐ'
    nfd=unicodedata.normalize('NFD','D' if ch=='Đ' else 'd' if ch=='đ' else ch)
    base=nfd[0]; marks=nfd[1:]
    rows,top=base_glyph(base); w=len(rows[0])
    upper=base.isupper()
    cv=[[0]*(w+6) for _ in range(CELL_H)]; ox=2  # offset so marks may extend left
    for i,r in enumerate(rows):
        for x,c in enumerate(r):
            if c=='#' and top+i<CELL_H: cv[top+i][ox+x]=1
    vowel=None;tone=None;dot=False;horn=False
    for m in marks:
        if m=='̂': vowel=CIRC
        elif m=='̆': vowel=BREVE
        elif m=='̛': horn=True
        elif m=='̣': dot=True
        elif m in TONES: tone=TONES[m]
    if special_d:
        # crossbar on d/D
        if ch=='đ': 
            for x in range(ox-1,ox+w): cv[4][x]=1
        else:
            cv[6][ox-1]=1
    if horn:
        topy=top
        cv[topy][ox+w]=1; cv[topy+1][ox+w]=1
        # widen w for horn
    def put(mk,x0,y0):
        for yy,r in enumerate(mk):
            for xx,c in enumerate(r):
                if c=='#' and 0<=y0+yy<CELL_H: cv[y0+yy][x0+xx]=1
    cx=ox+(w-1)//2  # center column of stem/body
    def left(mk): return cx-(len(mk[0])-1)//2 if len(mk[0])%2==1 else cx-(len(mk[0])//2-1) if w>1 else cx
    xtop=top
    if upper:
        if vowel and tone:
            put(vowel,left(vowel),1); put(tone,left(vowel)+len(vowel[0]),0)
        elif vowel: put(vowel,left(vowel),1)
        elif tone: put(tone,left(tone),0)
    else:
        if vowel and tone:
            put(vowel,left(vowel),3); put(tone,left(tone)+ (1 if len(tone[0])==2 else 0),0)
        elif vowel: put(vowel,left(vowel),3)
        elif tone: put(tone,left(tone),2 if base!='i' else 2)
    if dot:
        dy=11
        cv[dy][cx]=1
    # trim columns
    cols=[x for x in range(len(cv[0])) if any(cv[y][x] for y in range(CELL_H))]
    x0,x1=min(cols),max(cols)
    bm=[row[x0:x1+1] for row in cv]
    width=x1-x0+1
    # advance: ink width + 1 gap (base letters), but ensure marks don't collide: use ink width
    g=(bm,width+1)
    _cache[ch]=g; return g
def render(text,maxw=None):
    """Render text to 12 x W bit matrix. returns rows (list of list int), width"""
    cols=[]
    for ch in text:
        bm,adv=glyph(ch)
        w=len(bm[0]) if ch!=' ' else 3
        for x in range(adv):
            cols.append([bm[y][x] if x<len(bm[0]) else 0 for y in range(CELL_H)])
    while cols and not any(cols[-1]): cols.pop()
    return [[c[y] for c in cols] for y in range(CELL_H)], len(cols)
def width(text): return render(text)[1]
if __name__=='__main__':
    from PIL import Image
    import sys
    lines=["Ngộ Không, hãy mau cứu Tam Tạng! ▼","ẤẦẨẪẬ ẮẰẲẴẶ ỚỜỞỠỢ ỨỪỬỮỰ ĐÊẾỀỂỄỆ","áàảãạ ăắằẳẵặ âấầẩẫậ éèẻẽẹ êếềểễệ","óòỏõọ ôốồổỗộ ơớờởỡợ úùủũụ ưứừửữự ýỳỷỹỵ","Thuật Pháp, Đường Tăng, Bát Giới 0123456789 gjpqy,.?!"]
    sc=3; H=len(lines)*(CELL_H+4)
    im=Image.new("RGB",(260*sc,H*sc),(0,0,0))
    for li,t in enumerate(lines):
        rows,w=render(t)
        for y in range(CELL_H):
            for x in range(w):
                if rows[y][x]:
                    for dy in range(sc):
                        for dx in range(sc): im.putpixel(((x+2)*sc+dx,(li*(CELL_H+4)+y)*sc+dy),(255,255,255))
        print(w,t)
    im.save(sys.argv[1] if len(sys.argv)>1 else '/home/claude/saiyuuki/work/fontsheet.png')
