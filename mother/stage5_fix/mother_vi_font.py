
#!/usr/bin/env python3
"""
mother_vi_font.py - Stage 2: Vietnamese font + text encoding for MOTHER (NES)

Strategy: MARK-ROW rendering (dialogue/menus in MOTHER are double-spaced, so the
blank tile row above every text line is free for diacritics).
  * Main row : existing Latin font + 18 new glyphs (horn letters, đ/Đ, dotless i,
               dot-below vowels).
  * Mark row : 14 mark tiles (tones, breve, circumflex and their combinations).
  * Encoding : a mark is a PREFIX byte ($80-$8D) placed before the base glyph.
               Stage 3 renderer: on a byte in $80-$8D, remember it and draw it one
               row above the next printed glyph (cursor does not advance).

Glyph metrics follow the game's real font (CHR $1F800): 1-px strokes, colour
index 2, capitals rows 0-6, lowercase x-height rows 2-6, row 7 for descenders,
column 7 blank.  Marks occupy rows 1-6 of the mark tile (row 7 kept blank).

Usage:
  python mother_vi_font.py --rom mother.nes --out outdir
     -> outdir/mother_vi_font_test.nes  (CHR glyphs injected)
        outdir/mother_vi_font.ips       (same, as IPS patch)
        outdir/mother_vi.tbl, mother_vi_charmap.json, mother_vi_font_sheet.png
"""
import argparse, json, os, struct, unicodedata, zlib

# --------------------------------------------------------------------------
# 1. Glyph pixel art ('#' = colour 2, '.' = transparent)
# --------------------------------------------------------------------------
B = '........'
GLYPHS = {}          # code -> (name, rows)

def G(code, name, *rows):
    rows = list(rows)
    assert len(rows) == 8 and all(len(r) == 8 for r in rows), name
    assert all(r[7] == '.' for r in rows), name + ': column 7 must stay blank'
    GLYPHS[code] = (name, rows)

# ---- mark-row tiles ($80-$8D) ------------------------------------------------
G(0x80, 'MARK_ACUTE',      B, B, B, B, '....#...', '...#....', B, B)
G(0x81, 'MARK_GRAVE',      B, B, B, B, '..#.....', '...#....', B, B)
G(0x82, 'MARK_HOOK',       B, B, B, '..##....', '....#...', '...#....', B, B)
G(0x83, 'MARK_TILDE',      B, B, B, B, '..##.#..', '.#.##...', B, B)
G(0x84, 'MARK_BREVE',      B, B, B, B, '.#...#..', '..###...', B, B)
G(0x85, 'MARK_CIRC',       B, B, B, B, '...#....', '..#.#...', B, B)
G(0x86, 'MARK_BREVE_ACUTE', B, B, '....#...', '...#....', B, '.#...#..', '..###...', B)
G(0x87, 'MARK_BREVE_GRAVE', B, B, '..#.....', '...#....', B, '.#...#..', '..###...', B)
G(0x88, 'MARK_BREVE_HOOK',  B, '..##....', '....#...', '...#....', B, '.#...#..', '..###...', B)
G(0x89, 'MARK_BREVE_TILDE', B, B, '..##.#..', '.#.##...', B, '.#...#..', '..###...', B)
G(0x8A, 'MARK_CIRC_ACUTE',  B, B, B, '......#.', '.....#..', '..#.....', '.#.#....', B)
G(0x8B, 'MARK_CIRC_GRAVE',  B, B, B, '.....#..', '......#.', '..#.....', '.#.#....', B)
G(0x8C, 'MARK_CIRC_HOOK',   B, B, '....##..', '......#.', '.....#..', '..#.....', '.#.#....', B)
G(0x8D, 'MARK_CIRC_TILDE',  B, B, '..##.#..', '.#.##...', B, '...#....', '..#.#...', B)

# ---- main-row glyphs ---------------------------------------------------------
DOT = '...#....'
G(0x8E, 'ơ', B, '......#.', '..####..', '.#...#..', '.#...#..', '.#...#..', '..###...', B)
G(0x8F, 'ư', B, '......#.', '.#...##.', '.#...#..', '.#...#..', '.#...#..', '..####..', B)
G(0x90, 'đ', '.....#..', '...####.', '..####..', '.#...#..', '.#...#..', '.#...#..', '..####..', B)
G(0x91, 'Ơ', '..###.#.', '.#...##.', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '..###...', B)
G(0x92, 'Ư', '###...#.', '.#...##.', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '..###...', B)
G(0x93, 'Đ', '####....', '.#..#...', '.#...#..', '###..#..', '.#...#..', '.#..#...', '####....', B)
G(0x97, 'ı', B, B, B, '...#....', '...#....', '...#....', '...##...', B)
G(0x98, 'ạ', B, B, '..###...', '.....#..', '..####..', '.#...#..', '..###.#.', DOT)
G(0x99, 'ẹ', B, B, '..###...', '.#...#..', '.#####..', '.#......', '..###...', DOT)
G(0x9A, 'ị', B, '...#....', B, '...#....', '...#....', '...#....', '...##...', DOT)
G(0x9B, 'ọ', B, B, '..###...', '.#...#..', '.#...#..', '.#...#..', '..###...', DOT)
G(0x9C, 'ụ', B, B, '.#...#..', '.#...#..', '.#...#..', '.#...#..', '..####..', DOT)
G(0x9D, 'ỵ', B, '.#...#..', '.#...#..', '.#...#..', '..####..', '.....#..', '..###...', '.#......')
G(0x9E, 'ợ', B, '......#.', '..####..', '.#...#..', '.#...#..', '.#...#..', '..###...', DOT)
G(0x9F, 'ự', B, '......#.', '.#...##.', '.#...#..', '.#...#..', '.#...#..', '..####..', DOT)
G(0xA3, 'Ạ', '..##....', '...#....', '..#.#...', '..#.#...', '.#####..', '.#...#..', '###.###.', DOT)
G(0xA5, 'Ọ', '..###...', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '..###...', DOT)
G(0xAB, 'Ụ', '###.###.', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '.#...#..', '..###...', DOT)

# Marks end on row 6 of the mark tile: 1 px gap above capitals, 3 px above lowercase
# (a 0 px gap merged the breve/hat with A/Ô apexes in the in-game preview).
MARK_RANGE = (0x80, 0x8D)
TILES_REPLACED = {   # code -> what the original tile was (all verified unused by text)
    **{c: 'unused ligature tile' for c in range(0x80, 0x90)},
    **{c: 'blank tile' for c in range(0x90, 0x94)},
    **{c: '"SMAAAASH!!" logo piece (only used by msg 1511, to be re-translated as text)' for c in range(0x97, 0xA0)},
    0xA3: "'‥' (unused)", 0xA5: "'•' (unused)", 0xAB: "';' (unused)",
}

# --------------------------------------------------------------------------
# 2. Unicode <-> byte encoding
# --------------------------------------------------------------------------
BASE = {}                                   # existing font (stage-1 table)
BASE.update({chr(ord('A') + i): 0xC1 + i for i in range(26)})
BASE.update({chr(ord('a') + i): 0xE1 + i for i in range(26)})
NEW = {v[0]: k for k, v in GLYPHS.items() if not v[0].startswith('MARK')}
TOP = {  # (vowel-mark, tone) -> mark tile
    ('', 'acute'): 0x80, ('', 'grave'): 0x81, ('', 'hook'): 0x82, ('', 'tilde'): 0x83,
    ('breve', ''): 0x84, ('circ', ''): 0x85,
    ('breve', 'acute'): 0x86, ('breve', 'grave'): 0x87, ('breve', 'hook'): 0x88, ('breve', 'tilde'): 0x89,
    ('circ', 'acute'): 0x8A, ('circ', 'grave'): 0x8B, ('circ', 'hook'): 0x8C, ('circ', 'tilde'): 0x8D,
}
COMB = {'\u0306': ('v', 'breve'), '\u0302': ('v', 'circ'), '\u031b': ('h', 'horn'),
        '\u0301': ('t', 'acute'), '\u0300': ('t', 'grave'), '\u0309': ('t', 'hook'),
        '\u0303': ('t', 'tilde'), '\u0323': ('t', 'dot')}
CAP_DOT_FALLBACK = {'Ẹ': 'ẹ', 'Ị': 'ị', 'Ỵ': 'ỵ', 'Ợ': 'ợ', 'Ự': 'ự'}

def encode_char(ch, warn=None):
    """Return the byte sequence for one Vietnamese/Latin letter (or None if not a letter we handle)."""
    if ch in BASE: return bytes([BASE[ch]])
    if ch in ('đ', 'Đ'): return bytes([NEW[ch]])
    nfd = unicodedata.normalize('NFD', ch)
    base, marks = nfd[0], nfd[1:]
    if base not in 'aeiouyAEIOUY' or not marks or any(m not in COMB for m in marks):
        return None
    vowel = tone = ''; horn = False
    for m in marks:
        kind, val = COMB[m]
        if kind == 'v': vowel = val
        elif kind == 'h': horn = True
        else: tone = val
    upper = base.isupper()
    if horn:
        if base.lower() not in 'ou': return None
        glyph = {'o': 'ơ', 'u': 'ư'}[base.lower()]
        if upper: glyph = glyph.upper()
    else:
        glyph = base
    if tone == 'dot':
        dotted = unicodedata.normalize('NFC', glyph + '\u0323')
        if dotted in CAP_DOT_FALLBACK:
            if warn is not None: warn.append('capital %s has no glyph; rendered as %s' % (dotted, CAP_DOT_FALLBACK[dotted]))
            dotted = CAP_DOT_FALLBACK[dotted]
        main = NEW[dotted]
        top_tone = ''
    else:
        if glyph == 'i' and tone: glyph = 'ı'          # dotless i under a tone mark
        main = NEW[glyph] if glyph in NEW else BASE[glyph]
        top_tone = tone
    out = bytearray()
    if (vowel, top_tone) != ('', ''):
        out.append(TOP[(vowel, top_tone)])
    out.append(main)
    return bytes(out)

def all_vietnamese_letters():
    vowels = 'aăâeêioôơuưy'
    tones = ['', '\u0301', '\u0300', '\u0309', '\u0303', '\u0323']
    out = []
    for v in vowels + vowels.upper():
        for t in tones:
            out.append(unicodedata.normalize('NFC', v + t))
    return out + ['đ', 'Đ']

def build_charmap():
    cm = {}
    for ch in all_vietnamese_letters():
        w = []
        b = encode_char(ch, w)
        assert b is not None, ch
        cm[ch] = {'bytes': b.hex().upper(), 'fallback': w[0] if w else ''}
    return cm

def decode_bytes(bs, base_decode):
    """Inverse helper: rebuild Unicode from (mark prefix + glyph) pairs; other bytes via base_decode."""
    inv_new = {v: k for k, v in NEW.items()}
    inv_top = {v: k for k, v in TOP.items()}
    tone_cm = {'acute': '\u0301', 'grave': '\u0300', 'hook': '\u0309', 'tilde': '\u0303'}
    vow_cm = {'breve': '\u0306', 'circ': '\u0302'}
    out = []; pending = None
    for b in bs:
        if MARK_RANGE[0] <= b <= MARK_RANGE[1]:
            pending = inv_top[b]; continue
        if b in inv_new: g = inv_new[b]
        else: g = base_decode(b)
        if g == 'ı': g = 'i'
        if pending:
            v, t = pending
            nfd = unicodedata.normalize('NFD', g)
            g = unicodedata.normalize('NFC', nfd[0] + (vow_cm.get(v, '')) + nfd[1:] + tone_cm.get(t, ''))
            pending = None
        out.append(g)
    return ''.join(out)

# --------------------------------------------------------------------------
# 3. CHR conversion / injection
# --------------------------------------------------------------------------
FONT_CHR = 0x1F800            # CHR offset of tile $80 of the font page (bank R4=$7E/R5=$7F)
COLOUR = 2                    # the game's font uses colour index 2 only

def tile_bytes(rows):
    lo = bytearray(8); hi = bytearray(8)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == '#':
                if COLOUR & 1: lo[r] |= 0x80 >> c
                if COLOUR & 2: hi[r] |= 0x80 >> c
    return bytes(lo + hi)

def inject(rom):
    rom = bytearray(rom)
    prg_size = rom[4] * 0x4000
    chr_file = 16 + prg_size
    changes = []
    for code, (name, rows) in GLYPHS.items():
        off = chr_file + FONT_CHR + (code - 0x80) * 16
        data = tile_bytes(rows)
        changes.append((off, data))
        rom[off:off + 16] = data
    return bytes(rom), changes

def make_ips(changes):
    out = bytearray(b'PATCH')
    for off, data in sorted(changes):
        out += struct.pack('>I', off)[1:] + struct.pack('>H', len(data)) + data
    out += b'EOF'
    return bytes(out)

def write_tbl(path):
    from_stage1 = {0xA0: ' ', 0xA1: '!', 0xA2: '?', 0xA4: '$', 0xA6: '"', 0xA7: "'", 0xA8: '(',
                   0xA9: ')', 0xAA: ':', 0xAC: ',', 0xAD: '-', 0xAE: '.', 0xAF: '/', 0xBA: '⁰⁰',
                   0xBB: 'α', 0xBC: 'β', 0xBD: 'γ', 0xBE: 'π', 0xBF: 'Ω', 0xC0: '◆', 0xE0: '➡',
                   0x94: '○', 0x95: '◉', 0x96: '♪', 0xDB: '┏', 0xDC: '▔', 0xDD: '┓', 0xDE: '⎸',
                   0xDF: '⎹', 0xFB: '┗', 0xFC: '▁', 0xFD: '┛', 0xFE: '▬', 0xFF: '▶'}
    for i in range(10): from_stage1[0xB0 + i] = str(i)
    for ch, code in BASE.items(): from_stage1[code] = ch
    with open(path, 'w', encoding='utf-8') as f:
        f.write('; MOTHER (NES) - Vietnamese table (stage 2). Marks $80-$8D are PREFIX bytes drawn one row above the next glyph.\n')
        f.write('/00=<end>\n*01=<n>\n02=<clear>\n03=<wait>\n04=<goto>\n05=<05>\n20=<pos>\n21=<str>\n22=<rep>\n23=<num>\n')
        for code in sorted(set(from_stage1) | set(GLYPHS)):
            if code in GLYPHS:
                name = GLYPHS[code][0]
                f.write('%02X=%s\n' % (code, ('<%s>' % name) if name.startswith('MARK') else name))
            else:
                f.write('%02X=%s\n' % (code, from_stage1[code]))

def sheet_png(rom, path, scale=4):
    from PIL import Image, ImageDraw
    prg_size = rom[4] * 0x4000
    C = rom[16 + prg_size:]
    cw = 8 * scale + 16
    img = Image.new('RGB', (16 * cw, 8 * (cw + 2)), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    pal = [None, (90, 90, 90), (0, 0, 0), (150, 150, 150)]
    for t in range(0x80, 0x100):
        b = FONT_CHR + (t - 0x80) * 16
        k = t - 0x80; ox = (k % 16) * cw + 8; oy = (k // 16) * (cw + 2)
        new = t in GLYPHS
        dr.rectangle([ox - 2, oy + 10, ox + 8 * scale + 1, oy + 12 + 8 * scale + 1],
                     fill=(255, 236, 200) if new else (238, 238, 238))
        dr.text((ox, oy), '%02X' % t, fill=(200, 0, 0) if new else (0, 0, 160))
        for r in range(8):
            lo, hi = C[b + r], C[b + 8 + r]
            for c in range(8):
                v = ((lo >> (7 - c)) & 1) | (((hi >> (7 - c)) & 1) << 1)
                if v:
                    dr.rectangle([ox + c * scale, oy + 12 + r * scale, ox + c * scale + scale - 1,
                                  oy + 12 + r * scale + scale - 1], fill=pal[v])
    img.save(path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', required=True)
    ap.add_argument('--out', default='stage2_out')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rom = open(a.rom, 'rb').read()
    print('input CRC32 %08X' % (zlib.crc32(rom) & 0xFFFFFFFF))
    new, changes = inject(rom)
    open(os.path.join(a.out, 'mother_vi_font_test.nes'), 'wb').write(new)
    open(os.path.join(a.out, 'mother_vi_font.ips'), 'wb').write(make_ips(changes))
    write_tbl(os.path.join(a.out, 'mother_vi.tbl'))
    cm = build_charmap()
    json.dump({'strategy': 'mark-row (prefix mark byte + base glyph)',
               'mark_range': ['%02X' % MARK_RANGE[0], '%02X' % MARK_RANGE[1]],
               'glyphs': {'%02X' % k: v[0] for k, v in sorted(GLYPHS.items())},
               'replaced_tiles': {'%02X' % k: v for k, v in sorted(TILES_REPLACED.items())},
               'letters': cm}, open(os.path.join(a.out, 'mother_vi_charmap.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    sheet_png(new, os.path.join(a.out, 'mother_vi_font_sheet.png'))
    print('glyphs injected: %d tiles, output CRC32 %08X' % (len(changes), zlib.crc32(new) & 0xFFFFFFFF))

if __name__ == '__main__':
    main()
