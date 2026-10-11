#!/usr/bin/env python3
"""
mother_vi_stage5.py - Stage 5: name-entry screens + opening story with full tones.

Called by mother_vi_build.build() after the stage-4 work (see apply()).

1. Opening story (bank $19 text, copied to PRG-RAM $6000-$67FF before the naming screen)
   * bank $14 $9B1E  DEC $77 -> NOP NOP : the story is printed double-spaced, so the stage-3
     renderer can draw tone marks in the free row above each line.
   * INTRO1 at RAM $64D0 (unchanged pointer, bank $14 $9AB5/$9AB7),
     INTRO2 right after it (pointer bank $14 $9ACC/$9ACE),
     relocated naming error message after INTRO2 (pointer bank $14 $9CE7/$9CE9).
     Verified: nothing but the initial copy writes RAM $6000-$67FF during naming + intro.
2. Name-entry screens
   * Screen streams CHR $17866-$178FF (copied to RAM $6C66-$6CFF) rebuilt in Vietnamese:
     Back/End/Previous line, names + "Favorite food", "Is this OK? Yes No" box.
     Block pointers: bank $14 $9B70 ($6C66, unchanged), $9AD6, $9ADD.
   * Keyboard grid RAM $6470 (bank $19 $33C70): Đ đ Ơ ơ Ư ư added.
"""
import importlib.util, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mother_vi_codec import encode
from mother_vi_font import MARK_RANGE

P0 = 16
B14 = 0x14 * 0x2000
B19 = 0x19 * 0x2000

def p14(cpu):                    # PRG offset of bank $14 code at $8000-$9FFF
    return B14 + (cpu - 0x8000)

def ram19(addr):                 # PRG offset of bank $19 data copied to RAM $6000-$67FF
    return 0x33800 + (addr - 0x6000)

INTRO_RAM_START = 0x64D0
INTRO_RAM_END = 0x6800           # exclusive
CHR_LAYOUT = 0x17800             # CHR offset copied to RAM $6C00
LAYOUT_EDIT_START = 0x6C66       # first byte rebuilt (Back/End/Previous block)
LAYOUT_EDIT_END = 0x6D00         # exclusive

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def cols(text):
    return len(re.sub(r'\{[^}]*\}', '', unicodedata.normalize('NFC', text)))

def marks(b):
    return sum(1 for x in b if MARK_RANGE[0] <= x <= MARK_RANGE[1])

def patch_bytes(rom, off, old, new, report, what):
    cur = bytes(rom[P0 + off:P0 + off + len(old)])
    if cur != old:
        report['errors'].append('stage5 %s: unexpected bytes at PRG $%05X: %s' % (what, off, cur.hex()))
        return False
    rom[P0 + off:P0 + off + len(new)] = new
    return True

def apply(orig, rom, tr_folder, report):
    """rom: bytearray (stage-4 build, PRG 512 KB). Modifies rom in place; returns info dict."""
    info = {}
    intro = _load(os.path.join(tr_folder, 'vn_intro.py'), 'vn_intro')
    naming = _load(os.path.join(tr_folder, 'vn_naming.py'), 'vn_naming')
    N = naming.NAMING

    # ------------------------------------------------------------------ 1. opening story
    errs = []
    if len(intro.INTRO1) > 13: errs.append('INTRO1 has %d lines (max 13)' % len(intro.INTRO1))
    if len(intro.INTRO2) > 3: errs.append('INTRO2 has %d lines (max 3)' % len(intro.INTRO2))
    for ln in intro.INTRO1:
        if cols(ln) > 28: errs.append('INTRO1 line too wide (%d): %s' % (cols(ln), ln))
    for ln in intro.INTRO2:
        if cols(ln) > 24: errs.append('INTRO2 line too wide (%d): %s' % (cols(ln), ln))
    b1 = encode('\n'.join(intro.INTRO1))            # 00-terminated
    b2 = encode('\n'.join(intro.INTRO2))
    err_lines = N['error']
    if len(err_lines) != 6: errs.append('error message must have 6 lines')
    for i, ln in enumerate(err_lines):
        if cols(ln) != 15: errs.append('error line %d must be 15 columns (%d)' % (i + 1, cols(ln)))
    if marks(encode(err_lines[4], terminate=False)):
        errs.append('error line 5 must not contain top marks')
    b3 = encode('\n'.join(err_lines))
    a1 = INTRO_RAM_START; a2 = a1 + len(b1); a3 = a2 + len(b2); end = a3 + len(b3)
    if end > INTRO_RAM_END: errs.append('story + error message = %d bytes, %d available'
                                        % (end - a1, INTRO_RAM_END - a1))
    if errs:
        report['errors'] += ['stage5 intro: ' + e for e in errs]
    else:
        # clear old text area, write new blocks
        for a in range(INTRO_RAM_START, INTRO_RAM_END):
            rom[P0 + ram19(a)] = 0xFF
        for a, blob in ((a1, b1), (a2, b2), (a3, b3)):
            rom[P0 + ram19(a):P0 + ram19(a) + len(blob)] = blob
        ok = patch_bytes(rom, p14(0x9B1E), bytes.fromhex('c677'), bytes.fromhex('eaea'), report, 'double spacing')
        ok &= patch_bytes(rom, p14(0x9AB5), bytes.fromhex('a2d0a064'),
                          bytes([0xA2, a1 & 0xFF, 0xA0, a1 >> 8]), report, 'intro1 ptr')
        ok &= patch_bytes(rom, p14(0x9ACC), bytes.fromhex('a27da066'),
                          bytes([0xA2, a2 & 0xFF, 0xA0, a2 >> 8]), report, 'intro2 ptr')
        ok &= patch_bytes(rom, p14(0x9CE7), bytes.fromhex('a998a263'),
                          bytes([0xA9, a3 & 0xFF, 0xA2, a3 >> 8]), report, 'error ptr')
        # the stale CHR copy of the story ($1ECD0) is not read by the game: restore it
        chr0 = P0 + rom[4] * 0x4000
        o_chr0 = P0 + orig[4] * 0x4000
        rom[chr0 + 0x1ECD0:chr0 + 0x1EEA0] = orig[o_chr0 + 0x1ECD0:o_chr0 + 0x1EEA0]
        info['intro'] = {'block1': '$%04X (%d bytes, %d lines)' % (a1, len(b1), len(intro.INTRO1)),
                         'block2': '$%04X (%d bytes)' % (a2, len(b2)),
                         'error_message': '$%04X (%d bytes)' % (a3, len(b3)),
                         'free_bytes_left': INTRO_RAM_END - end, 'patched': bool(ok)}

    # ------------------------------------------------------------------ 2. naming screens
    errs = []
    def chk(key, want_cols):
        if cols(N[key]) != want_cols:
            errs.append('%s must be %d columns (%d): %r' % (key, want_cols, cols(N[key]), N[key]))
    chk('back_end', 15); chk('previous', 15); chk('is_ok', 16); chk('yes_no', 16)
    if cols(N['fav_food']) > 18: errs.append('fav_food too wide')
    be = unicodedata.normalize('NFC', N['back_end']); pv = unicodedata.normalize('NFC', N['previous'])
    if [i for i, c in enumerate(be) if c == '◆'] != [2, 9]: errs.append('back_end: ◆ must be at columns 2 and 9')
    if [i for i, c in enumerate(pv) if c == '◆'] != [3]: errs.append('previous: ◆ must be at column 3')
    yn = unicodedata.normalize('NFC', N['yes_no'])
    if yn[5] == ' ' or yn[4] != ' ' or yn[9] == ' ' or yn[8] != ' ':
        errs.append('yes_no: words must start at columns 5 and 9')
    blk1 = encode('{pos:08,16}' + N['back_end'] + '\n' + N['previous'])           # ...00
    blk2 = encode('\n{pos:0F,05}{Ninten}\n{pos:0F,08}{Ana}\n{pos:0F,0B}{Lloyd}\n{pos:0F,0E}{Teddy}'
                  '\n{pos:03,11}' + N['fav_food'] + '{FavFood}')
    blk3 = encode('{pos:07,14}┏{rep:DC,10}┓\n{24}' + N['is_ok'] + '{25}\n{24}' + N['yes_no'] +
                  '{25}\n{24}{rep:A0,10}{25}') + encode('{pos:07,1A}┗{rep:FC,10}┛')
    # layout: blk1 | blk2 (starts with 01) | 01 | blk3
    s1 = LAYOUT_EDIT_START; s2 = s1 + len(blk1); s3 = s2 + len(blk2) + 1
    end = s3 + len(blk3)
    if end > LAYOUT_EDIT_END:
        errs.append('naming layout is %d bytes, %d available' % (end - s1, LAYOUT_EDIT_END - s1))
    if errs:
        report['errors'] += ['stage5 naming: ' + e for e in errs]
    else:
        chr0 = P0 + rom[4] * 0x4000
        base = chr0 + CHR_LAYOUT - 0x6C00
        region = bytearray([0xFF]) * (LAYOUT_EDIT_END - LAYOUT_EDIT_START)
        def put(a, blob):
            region[a - s1:a - s1 + len(blob)] = blob
        put(s1, blk1); put(s2, blk2); put(s3 - 1, b'\x01'); put(s3, blk3)
        old = orig[P0 + orig[4] * 0x4000 + CHR_LAYOUT + 0x66:P0 + orig[4] * 0x4000 + CHR_LAYOUT + 0x100]
        if bytes(rom[base + s1:base + LAYOUT_EDIT_END]) != old:
            report['errors'].append('stage5 naming: CHR layout region differs from the original')
        else:
            rom[base + s1:base + LAYOUT_EDIT_END] = region
            patch_bytes(rom, p14(0x9AD5), bytes.fromhex('a98b'), bytes([0xA9, s2 & 0xFF]), report, 'names ptr')
            patch_bytes(rom, p14(0x9ADC), bytes.fromhex('a9c0'), bytes([0xA9, s3 & 0xFF]), report, 'is-ok ptr')
            info['naming_layout'] = {'back_end_previous': '$%04X' % s1, 'names_favfood': '$%04X' % s2,
                                     'is_ok_box': '$%04X' % s3, 'bytes': end - s1,
                                     'free': LAYOUT_EDIT_END - end}
    # keyboard
    kb = naming.KEYBOARD
    kerr = []
    if len(kb) != 4: kerr.append('KEYBOARD needs 4 rows')
    rows = []
    for r in kb:
        b = encode(r, terminate=False)
        if len(b) != 15 or marks(b):
            kerr.append('keyboard row must be 15 single-tile letters: %r' % r)
        if any(x in (0xA1, 0xA2, 0xA3) for x in b):
            kerr.append('keyboard row may not contain ! ? or the A3 tile (command codes): %r' % r)
        rows.append(b)
    if kerr:
        report['errors'] += ['stage5 keyboard: ' + e for e in kerr]
    else:
        for i, b in enumerate(rows):
            off = 0x33C70 + 0x10 * i
            if rom[P0 + off + 15] != 0:
                report['errors'].append('stage5 keyboard: row %d terminator missing' % i); continue
            rom[P0 + off:P0 + off + 15] = b
        info['keyboard'] = kb
    return info
