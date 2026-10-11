
#!/usr/bin/env python3
"""
mother_vi_wrap.py - layout of translated text for MOTHER (NES).

Translations are written as plain pages separated by {wait}; this module word-wraps them to the
game's window rules and returns text in the stage-1 tag format (ready for mother_vi_codec.encode).

Dialogue style (English source starts with "◆"):  "◆" + first line, continuation lines start with
" ", every page ends with "\\n" (same as the English), max 22 columns and max 10 mark bytes/line.
Battle style (no "◆"):  lines start at column 0, max 20 columns (longest English battle line is
21), no trailing "\\n" unless the English had one.
Explicit "\\n" in the translation forces a line break.
Tags count with the widest value they can print (TAG_WIDTH) so lines never overflow in game.
"""
import re, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mother_vi_codec import encode
from mother_vi_font import MARK_RANGE

TAG_WIDTH = {'Ninten': 7, 'Ana': 7, 'Lloyd': 7, 'Teddy': 7, 'Leader': 7, 'User': 7, 'Patient': 7,
             'FavFood': 7, 'Actor': 11, 'Target': 11, 'UsedItem': 11, 'ShopItem': 11,
             'BattleItem': 11, 'Str7420': 16}
TAG_MARKS = 2            # assumed mark bytes inside an inserted name
_TOK = re.compile(r'\{[^}]*\}|\S+|\s')

def tag_width(tag):
    name = tag[1:-1]
    if name in TAG_WIDTH: return TAG_WIDTH[name]
    if name.startswith('num:'):
        n = int(name.split(',')[1], 16)
        return {1: 3, 2: 5, 3: 8}.get(n, 8)
    if name in ('wait', 'clear', 'end') or name.startswith(('pos:', 'goto:', 'rep:')): return 0
    return 1                                              # {XX} raw tile

def word_cost(w):
    """(columns, marks) of a word that may contain tags."""
    cols = marks = 0
    for part in re.split(r'(\{[^}]*\})', w):
        if not part: continue
        if part.startswith('{'):
            cols += tag_width(part)
            if part[1:-1] in TAG_WIDTH: marks += TAG_MARKS
        else:
            cols += len(part)
            b = encode(part, terminate=False)
            marks += sum(1 for x in b if MARK_RANGE[0] <= x <= MARK_RANGE[1])
    return cols, marks

def wrap_page(page, width, max_marks, first_prefix, cont_prefix):
    lines = []
    for forced in page.split('\n'):
        words = forced.split()
        cur = ''; cw = len(first_prefix if not lines else cont_prefix); cm = 0
        prefix = first_prefix if not lines else cont_prefix
        cur = prefix
        base = cw
        for w in words:
            wc, wm = word_cost(w)
            need = wc + (0 if cur == prefix else 1)
            if cur != prefix and (cw + need > width or cm + wm > max_marks):
                lines.append(cur); cur = cont_prefix; cw = len(cont_prefix); cm = 0
                need = wc
            if cw + need > width or wm > max_marks:
                raise ValueError('word too long for a line: %r' % w)
            cur += ('' if cur == cont_prefix or cur == prefix else ' ') + w
            cw += need; cm += wm
        lines.append(cur)
        first_prefix = cont_prefix
    return lines

def layout(vn, en, width=None):
    """Lay out translation `vn` following the conventions of the English text `en`."""
    vn = unicodedata.normalize('NFC', vn).strip()
    dialogue = en.lstrip().startswith('◆') or vn.startswith('◆')
    if width is None:
        width = 22 if dialogue else 20
    trailing = en.endswith('\n')
    pages = vn.split('{wait}')
    out = []
    for i, p in enumerate(pages):
        p = p.strip(' ')
        if dialogue:
            bullet = p.startswith('◆')
            body = p[1:] if bullet else p
            lines = wrap_page(body.strip(), width, 10, '◆' if bullet else ' ', ' ')
        else:
            pre = ' ' if en.startswith(' ') else ''
            lines = wrap_page(p.strip(), width, 10, pre, pre)
        txt = '\n'.join(lines)
        if trailing or (dialogue and i < len(pages) - 1):
            txt += '\n'
        out.append(txt)
    return '{wait}'.join(out)
