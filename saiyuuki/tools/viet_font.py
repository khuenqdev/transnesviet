#!/usr/bin/env python3
"""Proportional Vietnamese bitmap font for the Saiyuuki World translation.

Cell height is 12 pixel rows (one dialog-box text line):

    rows 0-3   : diacritics zone (tone marks / circumflex / breve)
    rows 4-10  : capitals & ascenders (7 rows); x-height letters occupy rows 6-10
    rows 11-13 : descenders (g j p q y) and dot-below (nang)

Glyphs are composed at run time: a base Latin letter + optional shape mark
(circumflex, breve, horn) + optional tone mark (sac, huyen, hoi, nga, nang).
Everything Vietnamese (all 134 vowel/tone combinations, d-bar) is therefore
available without a hand-drawn table.

API:
    glyph(ch)            -> (rows[12] of '01' strings, advance)   composed glyph
    render(text)         -> list of 14 int-lists (0/1), width W
    text_width(text)     -> width in pixels
"""
import unicodedata

H = 12
CAP_TOP = 3          # first row of capitals / ascenders
XH_TOP = 5           # first row of x-height letters
BASE = 9             # baseline row (last row of x-height / capitals)

# ----------------------------------------------------------------- base glyphs
# Each entry: (top_row, [row strings]).  '#' = ink.
def _g(top, rows):
    return (top, [r for r in rows.split()])

UP = {
 'A': _g(3, ".###. #...# #...# ##### #...# #...# #...#"),
 'B': _g(3, "####. #...# #...# ####. #...# #...# ####."),
 'C': _g(3, ".###. #...# #.... #.... #.... #...# .###."),
 'D': _g(3, "####. #...# #...# #...# #...# #...# ####."),
 'E': _g(3, "##### #.... #.... ####. #.... #.... #####"),
 'F': _g(3, "##### #.... #.... ####. #.... #.... #...."),
 'G': _g(3, ".###. #...# #.... #.### #...# #...# .###."),
 'H': _g(3, "#...# #...# #...# ##### #...# #...# #...#"),
 'I': _g(3, "### .#. .#. .#. .#. .#. ###"),
 'J': _g(3, "..## ...# ...# ...# #..# #..# .##."),
 'K': _g(3, "#...# #..#. #.#.. ##... #.#.. #..#. #...#"),
 'L': _g(3, "#.... #.... #.... #.... #.... #.... #####"),
 'M': _g(3, "#...# ##.## #.#.# #.#.# #...# #...# #...#"),
 'N': _g(3, "#...# ##..# ##..# #.#.# #..## #..## #...#"),
 'O': _g(3, ".###. #...# #...# #...# #...# #...# .###."),
 'P': _g(3, "####. #...# #...# ####. #.... #.... #...."),
 'Q': _g(3, ".###. #...# #...# #...# #.#.# #..#. .##.#"),
 'R': _g(3, "####. #...# #...# ####. #.#.. #..#. #...#"),
 'S': _g(3, ".#### #.... #.... .###. ....# ....# ####."),
 'T': _g(3, "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#.."),
 'U': _g(3, "#...# #...# #...# #...# #...# #...# .###."),
 'V': _g(3, "#...# #...# #...# #...# #...# .#.#. ..#.."),
 'W': _g(3, "#...# #...# #...# #.#.# #.#.# ##.## #...#"),
 'X': _g(3, "#...# #...# .#.#. ..#.. .#.#. #...# #...#"),
 'Y': _g(3, "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#.."),
 'Z': _g(3, "##### ....# ...#. ..#.. .#... #.... #####"),
}
LO = {
 'a': _g(5, ".##. ...# .### #..# .###"),
 'b': _g(3, "#... #... ###. #..# #..# #..# ###."),
 'c': _g(5, ".### #... #... #... .###"),
 'd': _g(3, "...# ...# .### #..# #..# #..# .###"),
 'e': _g(5, ".##. #..# #### #... .###"),
 'f': _g(3, ".## #.. ### #.. #.. #.. #.."),
 'g': _g(5, ".### #..# #..# .### ...# #..# .##."),
 'h': _g(3, "#... #... ###. #..# #..# #..# #..#"),
 'i': _g(3, "# . # # # # #"),
 'j': _g(3, ".# .. .# .# .# .# .# .# #."),
 'k': _g(3, "#... #... #..# #.#. ##.. #.#. #..#"),
 'l': _g(3, "# # # # # # #"),
 'm': _g(5, "##.#. #.#.# #.#.# #.#.# #.#.#"),
 'n': _g(5, "###. #..# #..# #..# #..#"),
 'o': _g(5, ".##. #..# #..# #..# .##."),
 'p': _g(5, "###. #..# #..# ###. #... #... #..."),
 'q': _g(5, ".### #..# #..# .### ...# ...# ...#"),
 'r': _g(5, "#.# ##. #.. #.. #.."),
 's': _g(5, ".### #... .##. ...# ###."),
 't': _g(4, ".#. ### .#. .#. .#. .##"),
 'u': _g(5, "#..# #..# #..# #..# .###"),
 'v': _g(5, "#...# #...# .#.#. .#.#. ..#.."),
 'w': _g(5, "#...# #...# #.#.# #.#.# .#.#."),
 'x': _g(5, "#..# #..# .##. #..# #..#"),
 'y': _g(5, "#..# #..# #..# .### ...# #..# .##."),
 'z': _g(5, "#### ...# .##. #... ####"),
}
DIGIT = {
 '0': _g(3, ".##. #..# #..# #..# #..# #..# .##."),
 '1': _g(3, ".#. ##. .#. .#. .#. .#. ###"),
 '2': _g(3, ".##. #..# ...# ..#. .#.. #... ####"),
 '3': _g(3, ".##. #..# ...# .##. ...# #..# .##."),
 '4': _g(3, "...# ..## .#.# #..# #### ...# ...#"),
 '5': _g(3, "#### #... ###. ...# ...# #..# .##."),
 '6': _g(3, ".##. #... ###. #..# #..# #..# .##."),
 '7': _g(3, "#### ...# ..#. ..#. .#.. .#.. .#.."),
 '8': _g(3, ".##. #..# #..# .##. #..# #..# .##."),
 '9': _g(3, ".##. #..# #..# .### ...# ...# .##."),
}
PUNCT = {
 '.': _g(9, "#"),
 ',': _g(9, "# #"),
 '!': _g(3, "# # # # # . #"),
 '?': _g(3, ".##. #..# ...# ..#. .#.. .... .#.."),
 ':': _g(6, "# . . . #"),
 ';': _g(6, "# . . . # #"),
 '-': _g(7, "###"),
 '–': _g(7, "####"),          # en dash
 '—': _g(7, "#####"),         # em dash
 "'": _g(3, "# #"),
 '’': _g(3, "# #"),
 '"': _g(3, "#.# #.#"),
 '(': _g(3, ".# #. #. #. #. #. .#"),
 ')': _g(3, "#. .# .# .# .# .# #."),
 '/': _g(3, "...# ...# ..#. ..#. .#.. .#.. #..."),
 '+': _g(5, ".#. ### .#."),
 '*': _g(4, "#.# .#. #.#"),
 '~': _g(7, ".#.# #.#."),
 '×': _g(6, "#.# .#. #.#"),    # multiplication sign
 '%': _g(3, "#..# ...# ..#. .#.. #... #..# ...."),
 '…': _g(9, "#.#.#"),        # ellipsis
 '▼': _g(5, "##### .###. ..#.."),   # down arrow (page-wait marker)
}

# ----------------------------------------------------------------- marks
MARK = {
 'acute':  ["..#", ".#.", ],           # drawn 2 rows tall, see _mark_px
 'grave':  ["#..", ".#."],
}
def _px(rows, dx, top):
    out = []
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '#':
                out.append((dx + x, top + y))
    return out

SHAPES = {
 'acute':  [".#", "#."],
 'grave':  ["#.", ".#"],
 'hook':   ["##", ".#"],
 'tilde':  [".#.#", "#.#."],
 'circ':   [".#.", "#.#"],
 'breve':  ["#.#", ".#."],
}

# tone -> shape name, shape name -> width
TONES = {'́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde', '̣': 'dot'}
MODS = {'̂': 'circ', '̆': 'breve', '̛': 'horn'}


def _decompose(ch):
    """'ế' -> ('e', ['circ'], 'acute') ; handles precomposed Vietnamese chars."""
    if ch in ('đ', 'Đ'):
        return ('d' if ch == 'đ' else 'D'), 'bar', None
    d = unicodedata.normalize('NFD', ch)
    base = d[0]
    mod = None
    tone = None
    for c in d[1:]:
        if c in MODS:
            mod = MODS[c]
        elif c in TONES:
            tone = TONES[c]
    return base, mod, tone


_cache = {}


def glyph(ch):
    """Return (rows, advance): rows = 12 strings of '0'/'1', all the same width."""
    if ch in _cache:
        return _cache[ch]
    if ch == ' ':
        res = (['0' * 3] * H, 3)
        _cache[ch] = res
        return res
    base, mod, tone = _decompose(ch)
    if base in UP:
        top, rows = UP[base]
        upper = True
    elif base in LO:
        top, rows = LO[base]
        upper = False
    elif base in DIGIT:
        top, rows = DIGIT[base]
        upper = True
    elif base in PUNCT:
        top, rows = PUNCT[base]
        upper = False
    else:
        raise KeyError('no glyph for %r' % ch)
    # base pixels
    px = _px(rows, 0, top)
    w = max(len(r) for r in rows)

    # i / j: dot is part of the glyph; remove it when a mark replaces it
    if base in ('i', 'j') and (mod or tone):
        px = [(x, y) for (x, y) in px if y >= 5]

    # d-bar / D-bar
    if mod == 'bar':
        if base == 'd':
            px.append((1, 4)); px.append((2, 4))
        else:  # D: extend bar to the left
            px = [(x + 1, y) for (x, y) in px]
            px.append((0, 6)); w += 1
    mods_dx = 0

    # horn
    if mod == 'horn':
        t = CAP_TOP - 1 if upper else XH_TOP - 1
        px += [(w - 1, t), (w, t), (w, t + 1)]
        w += 1

    # mark placement
    top_of_letter = CAP_TOP if upper else XH_TOP
    if base in ('i',) and not upper:
        top_of_letter = XH_TOP   # dotless i body starts at x-height
    cx = (w - 1) / 2.0

    def put(shape, ytop):
        nonlocal px, w, mods_dx
        rows_s = SHAPES[shape]
        mw = len(rows_s[0])
        x0 = int(round(cx - (mw - 1) / 2.0))
        if x0 < 0:
            # grow to the left
            px = [(x + (-x0), y) for (x, y) in px]
            w += -x0
            mods_dx += -x0
            x0 = 0
        px += _px(rows_s, x0, ytop)
        w = max(w, x0 + mw)

    if mod in ('circ', 'breve'):
        if tone in ('acute', 'grave', 'hook', 'tilde'):
            if upper:
                # capitals: no room above -> circumflex on row 1-2, tone side by side on rows 0-1
                put(mod, 1)
                mw = len(SHAPES[mod][0]); tw = len(SHAPES[tone][0])
                x0 = int(round(cx - (mw - 1) / 2.0)) + mw
                px += _px(SHAPES[tone], x0, 0)
                w = max(w, x0 + tw)
            else:
                put(mod, top_of_letter - 2)
                put(tone, 0)
        else:
            put(mod, top_of_letter - 2 if not upper else top_of_letter - 2)
    elif tone in ('acute', 'grave', 'hook', 'tilde'):
        put(tone, top_of_letter - 3)
    if tone == 'dot':
        # dot below, centred
        x0 = int(round(cx))
        px.append((x0 + (0), 11))
    # normalise: shift if any x<0 (shouldn't happen)
    minx = min(x for x, _ in px)
    if minx < 0:
        px = [(x - minx, y) for x, y in px]
        w -= minx
    maxx = max(x for x, _ in px)
    w = max(w, maxx + 1)
    grid = [['0'] * w for _ in range(H)]
    for x, y in px:
        if 0 <= y < H:
            grid[y][x] = '1'
    res = (["".join(r) for r in grid], w + 1)
    _cache[ch] = res
    return res


def render(text, kern=0):
    """Return list of 12 lists of 0/1 (pixel rows) for the whole string."""
    cols = []
    for ch in text:
        rows, adv = glyph(ch)
        w = len(rows[0])
        for x in range(w):
            cols.append([int(rows[y][x]) for y in range(H)])
        for _ in range(adv - w + kern):
            cols.append([0] * H)
    # trim trailing blank column
    while cols and not any(cols[-1]):
        cols.pop()
    return [[c[y] for c in cols] for y in range(H)]


def text_width(text):
    wsum = 0
    for ch in text:
        wsum += glyph(ch)[1]
    return wsum - 1 if text else 0


if __name__ == '__main__':
    import sys
    from PIL import Image
    samples = [
        "Aa Bb Cc Dd Đđ Ee Êê Gg Hh Ii Kk Ll Mm Nn Oo Ôô Ơơ Pp Qq Rr Ss Tt Uu Ưư Vv Xx Yy",
        "à á ả ã ạ ă ằ ắ ẳ ẵ ặ â ầ ấ ẩ ẫ ậ è é ẻ ẽ ẹ ê ề ế ể ễ ệ",
        "ì í ỉ ĩ ị ò ó ỏ õ ọ ô ồ ố ổ ỗ ộ ơ ờ ớ ở ỡ ợ",
        "ù ú ủ ũ ụ ư ừ ứ ử ữ ự ỳ ý ỷ ỹ ỵ",
        "ÀÁẢÃẠ ĂẰẮẲẴẶ ÂẦẤẨẪẬ ÈÉẺẼẸ ÊỀẾỂỄỆ ÌÍỈĨỊ",
        "ÒÓỎÕỌ ÔỒỐỔỖỘ ƠỜỚỞỠỢ ÙÚỦŨỤ ƯỪỨỬỮỰ ỲÝỶỸỴ",
        "Ngộ Không, ngươi đã đến rồi à? Ta là Ngưu Ma Vương!",
        "Tam Tạng pháp sư đang bị giam ở động Bàn Tơ.",
        "0123456789 .,!?:;-'\"()/ gjpqy",
    ]
    out = sys.argv[1] if len(sys.argv) > 1 else 'font_preview.png'
    sc = 4
    imgs = []
    for s in samples:
        bm = render(s)
        W = len(bm[0])
        im = Image.new('RGB', (W * sc + 8, 12 * sc + 8), (0, 0, 0))
        for y in range(12):
            for x in range(W):
                if bm[y][x]:
                    for dy in range(sc):
                        for dx in range(sc):
                            im.putpixel((4 + x * sc + dx, 4 + y * sc + dy), (255, 255, 255))
        imgs.append(im)
    Wm = max(i.width for i in imgs)
    sheet = Image.new('RGB', (Wm, sum(i.height for i in imgs)), (0, 0, 0))
    y = 0
    for i in imgs:
        sheet.paste(i, (0, y)); y += i.height
    sheet.save(out)
    print('saved', out, sheet.size)
