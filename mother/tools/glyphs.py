# Vietnamese accented capitals, 8x8, drawn in the style of the game's font
# (2-px strokes, col 0 kept blank, baseline on row 7). '#' = pixel.
G = {}
def g(name, *rows):
    rows=[r.replace(' ','') for r in rows]
    assert len(rows)==8, name
    for r in rows: assert len(r)==8,(name,r)
    G[name]=rows

# base 5-row shapes (cols 0..7)
A5=["...###..","..##.##.",".##...##",".#######",".##...##"]
E5=[".######.",".##.....",".#####..",".##.....",".######."]
O5=["..#####.",".##...##",".##...##",".##...##","..#####."]
U5=[".##...##",".##...##",".##...##",".##...##","..#####."]
I5=["..######","....##..","....##..","....##..","..######"]
BL="........"
def top(mark2, base):        # 2 rows of marks, 1 blank row, 5-row letter
    return mark2+[BL]+base
def topx(mark3, base):       # 3 rows of marks, 5-row letter
    return mark3+base
DOT="....##.."
def dot(base):               # letter rows 1..5 (top aligned), dot on row 7
    return [BL]+base+[BL,DOT]

ACUTE=[".....##.","....##.."]
GRAVE=["..##....","...##..."]
HOOK =["...###..",".....##.","....##.."]
CIRC =["...##...","..#..#.."]

G['Đ']=[BL,"..####..","..##.##.",".####.##","..##..##","..##..##","..##.##.","..####.."]
G['À']=top(GRAVE,A5)
G['Ả']=topx(HOOK,A5)
G['Ạ']=dot(A5)
G['Ú']=top(ACUTE,U5)
G['Ụ']=dot(U5)
G['Ì']=top(GRAVE,I5)
G['Ọ']=dot(O5)
# circumflex + dot: hat rows 0-1, letter rows 2-6, dot row 7
G['Ậ']=CIRC+A5+[DOT]
G['Ệ']=CIRC+E5+[DOT]
G['Ộ']=CIRC+["..#####.",".##...##",".##...##","..#####.",BL]+[DOT]
# circumflex + tone: hat on the left, tone on the right
G['Ể']=["...#.##.","..#.#..#",".....##."]+E5
G['Ế']=["...#..##","..#.##..",BL]+E5
G['Ề']=["...#.##.","..#.#.##",BL]+E5
G['Ố']=["...#..##","..#.##..",BL]+O5
# horn letters (narrower body, horn on the right)
G['Ư']=[".......#",".##..##.",".##..##.",".##..##.",".##..##.",".##..##.",".##..##.","..####.."]
G['Ơ']=[".......#","..#####.",".##..##.",".##..##.",".##..##.",".##..##.",".##..##.","..####.."]
G['Ờ']=["..##...#","...##.#.","........","..####..",".##..##.",".##..##.",".##..##.","..####.."]
# breve + tilde
G['Ẵ']=["...##.#.","..#.##..","..#...#.","...###..","..##.##.",".##...##",".#######",".##...##"]
