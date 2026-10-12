#!/usr/bin/env python3
"""Compact 8-pixel-high all-caps Vietnamese font (3x5 letters) used for the status-screen menus,
where only ONE tile row is available per text line.

cell: rows 0-1 diacritics, rows 2-6 letter body, row 7 dot-below (nang).
API mirrors viet_font:  render(text) -> 8 rows of 0/1 ;  text_width(text)
"""
import unicodedata
H = 8
def _g(rows): return rows.split()
L = {
 'A': _g(".#. #.# ### #.# #.#"), 'B': _g("##. #.# ##. #.# ##."), 'C': _g(".## #.. #.. #.. .##"),
 'D': _g("##. #.# #.# #.# ##."), 'E': _g("### #.. ##. #.. ###"), 'F': _g("### #.. ##. #.. #.."),
 'G': _g(".## #.. #.# #.# .##"), 'H': _g("#.# #.# ### #.# #.#"), 'I': _g("### .#. .#. .#. ###"),
 'J': _g("..# ..# ..# #.# .#."), 'K': _g("#.# #.# ##. #.# #.#"), 'L': _g("#.. #.. #.. #.. ###"),
 'M': _g("#.# ### ### #.# #.#"), 'N': _g("##. #.# #.# #.# #.#"), 'O': _g(".#. #.# #.# #.# .#."),
 'P': _g("##. #.# ##. #.. #.."), 'Q': _g(".#. #.# #.# ### .##"), 'R': _g("##. #.# ##. #.# #.#"),
 'S': _g(".## #.. .#. ..# ##."), 'T': _g("### .#. .#. .#. .#."), 'U': _g("#.# #.# #.# #.# ###"),
 'V': _g("#.# #.# #.# #.# .#."), 'W': _g("#.# #.# ### ### #.#"), 'X': _g("#.# #.# .#. #.# #.#"),
 'Y': _g("#.# #.# .#. .#. .#."), 'Z': _g("### ..# .#. #.. ###"),
 '0': _g(".#. #.# #.# #.# .#."), '1': _g(".#. ##. .#. .#. ###"), '2': _g("##. ..# .#. #.. ###"),
 '3': _g("##. ..# .#. ..# ##."), '4': _g("#.# #.# ### ..# ..#"), '5': _g("### #.. ##. ..# ##."),
 '6': _g(".## #.. ### #.# ###"), '7': _g("### ..# .#. .#. .#."), '8': _g("### #.# ### #.# ###"),
 '9': _g("### #.# ### ..# ##."),
}
P = {'-': ("", None), }
SH = {'acute': ["..#", ".#."], 'grave': ["#..", ".#."], 'hook': ["##.", ".#."],
      'tilde': [".##", "##."], 'circ': [".#.", "#.#"], 'breve': ["#.#", ".#."]}
SIDE = {'acute': [".#", "#."], 'grave': ["#.", ".#"], 'hook': ["##", ".#"], 'tilde': ["#.#", ".#."]}
TONES = {'́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde', '̣': 'dot'}
MODS = {'̂': 'circ', '̆': 'breve', '̛': 'horn'}
_cache = {}

def glyph(ch):
    if ch in _cache: return _cache[ch]
    if ch == ' ':
        r = (['00'] * H, 2); _cache[ch] = r; return r
    ch = ch.upper()
    simple = {'-': [(0, 4), (1, 4), (2, 4)], '.': [(0, 6)], ',': [(0, 6), (0, 7)], '!': [(0, 2), (0, 3), (0, 4), (0, 6)],
              '?': [(0, 2), (1, 2), (1, 3), (0, 5)], ':': [(0, 3), (0, 5)], "'": [(0, 2), (0, 3)]}
    if ch in simple:
        px = simple[ch]; w = max(x for x, _ in px) + 1
        g = [['0'] * w for _ in range(H)]
        for x, y in px: g[y][x] = '1'
        r = (["".join(a) for a in g], w + 1); _cache[ch] = r; return r
    if ch in ('Đ',):
        base, mod, tone = 'D', 'bar', None
    else:
        d = unicodedata.normalize('NFD', ch)
        base = d[0]; mod = tone = None
        for c in d[1:]:
            if c in MODS: mod = MODS[c]
            elif c in TONES: tone = TONES[c]
    rows = L[base]
    px = []
    w = 3
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '#': px.append((x, y + 2))
    if mod == 'bar':          # D-bar: stub on the left of the middle row
        px = [(x + 1, y) for x, y in px] + [(0, 4)]; px.append((2, 4)); w = 4
    if mod == 'horn':
        px.append((w, 3)); w += 1
    def put(shape, x0, y0):
        nonlocal px, w
        for y, r in enumerate(shape):
            for x, c in enumerate(r):
                if c == '#': px.append((x0 + x, y0 + y))
        w = max(w, x0 + len(shape[0]))
    if mod in ('circ', 'breve'):
        put(SH[mod], 0, 0)
        if tone in SIDE:
            put(SIDE[tone], w, 0)
    elif tone in SH:
        put(SH[tone], 0, 0)
    if tone == 'dot':
        px.append((w // 2 if w > 3 else 1, 7))
    g = [['0'] * w for _ in range(H)]
    for x, y in px: g[y][x] = '1'
    r = (["".join(a) for a in g], w + 1); _cache[ch] = r; return r

def render(text):
    cols = []
    for ch in text:
        rows, adv = glyph(ch)
        w = len(rows[0])
        for x in range(w): cols.append([int(rows[y][x]) for y in range(H)])
        for _ in range(adv - w): cols.append([0] * H)
    while cols and not any(cols[-1]): cols.pop()
    return [[c[y] for c in cols] for y in range(H)]

def text_width(text):
    return sum(glyph(c)[1] for c in text) - 1 if text else 0

if __name__ == '__main__':
    import sys
    from PIL import Image
    S = ["KHIÊN ĐỒNG GIÁP VÀNG ĐOẢN KIẾM", "ÀÁẢÃẠ ĂẰẮẲẴẶ ÂẦẤẨẪẬ ÈÉẺẼẸ ÊỀẾỂỄỆ", "ÌÍỈĨỊ ÒÓỎÕỌ ÔỒỐỔỖỘ ƠỜỚỞỠỢ ÙÚỦŨỤ ƯỪỨỬỮỰ ỲÝỶỸỴ",
         "NHƯ Ý BỔNG  THIẾT KIẾM  BẢO VẬT  VŨ KHÍ  MỆNH TIỀN ĐIỂM", "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 -.,!?"]
    sc = 5; ims = []
    for s in S:
        bm = render(s); W = len(bm[0])
        im = Image.new('RGB', (W * sc + 8, H * sc + 8))
        for y in range(H):
            for x in range(W):
                if bm[y][x]:
                    for dy in range(sc):
                        for dx in range(sc): im.putpixel((4 + x * sc + dx, 4 + y * sc + dy), (255, 255, 255))
        ims.append(im)
    Wm = max(i.width for i in ims); sh = Image.new('RGB', (Wm, sum(i.height for i in ims)))
    y = 0
    for i in ims: sh.paste(i, (0, y)); y += i.height
    sh.save(sys.argv[1] if len(sys.argv) > 1 else 'font8_preview.png'); print(sh.size)
