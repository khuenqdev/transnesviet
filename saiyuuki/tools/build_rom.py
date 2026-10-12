#!/usr/bin/env python3
"""Build the Vietnamese ROM of Saiyuuki World.
usage: build_rom.py [out.nes]
Inputs : rom/original.nes, src/window.asm, src/tramp.asm, tools/viet_font.py, tools/vi_script.py
"""
import sys, os, struct
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from asm6502 import assemble
import viet_font as vf
import importlib, vi_script
importlib.reload(vi_script)

ORIG = open(ROOT + '/rom/original.nes', 'rb').read()
OUT = sys.argv[1] if len(sys.argv) > 1 else ROOT + '/build/saiyuuki_vi.nes'
BANK = 0x4000
prg = [bytearray(ORIG[16 + i * BANK:16 + (i + 1) * BANK]) for i in range(8)]
N = 213

# ---------------------------------------------------------------- parse original rows
b3 = prg[3]
w16 = lambda a: b3[a - 0x8000] | b3[a - 0x8000 + 1] << 8
orig = []
for i in range(N):
    p = w16(0x9E77 + 2 * i); fl = b3[p - 0x8000]; ln = b3[p - 0x8000 + 1]; q = p + 2; addr = None
    if fl & 0x10:
        addr = w16(q); q += 2
    orig.append(dict(i=i, flags=fl, len=ln, addr=addr, data=bytes(b3[q - 0x8000:q - 0x8000 + ln])))

# ---------------------------------------------------------------- code
def asm_file(name, org, syms=None):
    return assemble(open(ROOT + '/src/' + name).read(), org, syms)
wsegs, wlab = asm_file('window.asm', 0x8000)
assert max(a + len(b) for a, b in wsegs if a < 0x8600) <= 0x8600, 'window code overlaps ROWTAB'
tsegs, tlab = asm_file('tramp.asm', 0xC02A)

# ---------------------------------------------------------------- row bitmaps
DOWN = vf.render('▼')
def to_columns(bm, ncols):
    W = len(bm[0]) if bm and bm[0] else 0
    cols = []
    for c in range(ncols):
        col = bytearray(12)
        for y in range(12):
            v = 0
            for x in range(8):
                px = c * 8 + x
                if px < W and bm[y][px]:
                    v |= 0x80 >> x
            col[y] = v
        cols.append(bytes(col))
    return cols

PASS = set(range(154, 179)) | {186}   # price digit rows + yen kanji keep the original drawing
import viet_font8 as vf8
def to_columns8(bm, ncols):
    W = len(bm[0]) if bm and bm[0] else 0
    cols = []
    for c in range(ncols):
        col = bytearray(8)
        for y in range(8):
            v = 0
            for x in range(8):
                px = c * 8 + x
                if px < W and bm[y][px]:
                    v |= 0x80 >> x
            col[y] = v
        cols.append(bytes(col))
    return cols
SMALLMAX = {183: 3, 187: 3, 188: 3, 184: 4, 185: 4}   # status-screen slot widths (columns); items: 5

rowinfo = {}      # i -> dict(flags, n12, n8, dx8, d12, d8)
report = []
for r in orig:
    i = r['i']
    if i in PASS:
        continue
    text = vi_script.TEXT.get(i, '')
    small = vi_script.SMALL.get(i)
    wait = bool(r['data']) and r['data'][-1] == 0xB3
    info = dict(flags=0, n12=0, n8=0, dx8=0, d12=b'', d8=b'')
    if small is not None:
        stext, dx = small
        bm8 = vf8.render(stext); W8 = len(bm8[0]); n8 = (W8 + 7) // 8
        mx = SMALLMAX.get(i, 5)
        if n8 > mx:
            report.append('row %d small too wide: %d cols > %d  %r' % (i, n8, mx, stext))
        info.update(flags=info['flags'] | 2, n8=n8, dx8=dx & 0xFF, d8=b''.join(to_columns8(bm8, n8)))
    if text.strip():
        bm = vf.render(text); W = len(bm[0])
        maxw = (224 if r['flags'] & 0x10 else 136) - (8 if wait else 0)
        if W > maxw:
            report.append('row %d too wide: %d > %d  %r' % (i, W, maxw, text))
        nt = (W + 7) // 8
        if wait:
            wa = len(DOWN[0])
            full = [bm[y] + [0] * (nt * 8 - W) + [0] + DOWN[y] + [0] * (8 - 1 - wa) for y in range(12)]
            ncols = nt + 1
        else:
            full = bm; ncols = nt
        info.update(flags=info['flags'] | 1, n12=ncols, d12=b''.join(to_columns(full, ncols)))
    elif small is None:
        info['flags'] = 0x80                 # blank row (wipes the line)
    rowinfo[i] = info
if report:
    print('\n'.join(report))
    if '--strict' in sys.argv: sys.exit(1)

def row_len(i):
    inf = rowinfo[i]
    return max(1, inf['n12'] or inf['n8'])
def row_wait(i, r):
    return bool(r['data']) and r['data'][-1] == 0xB3 and rowinfo[i]['n12'] > 0

# ---------------------------------------------------------------- bank 3 records
# overlap packing: non-wait records only carry their header, data bytes overlap later records
ptrs = [0] * N
BASE = 0xA021; END = 0xAB0B
full = set()
while True:
    recs = []
    for r in orig:
        i = r['i']
        if i in PASS:
            body = bytes([r['flags'], r['len']]) + (struct.pack('<H', r['addr']) if r['addr'] else b'') + r['data']
            recs.append((i, body, None)); continue
        ln = row_len(i)
        wait = row_wait(i, r)
        h = bytes([r['flags'], ln]) + (struct.pack('<H', r['addr']) if r['addr'] else b'')
        if wait:
            recs.append((i, h + bytes(ln - 1) + b'\xB3', 'wait'))
        elif i in full:
            recs.append((i, h + bytes(ln), None))
        else:
            recs.append((i, h, ln))
    stream = bytearray()
    for i, body, extra in recs:
        ptrs[i] = BASE + len(stream)
        stream += body
    stream += bytes(40)
    bad = [i for i, body, extra in recs if extra not in (None, 'wait')
           and stream[ptrs[i] - BASE + len(body) + extra - 1] == 0xB3]
    if not bad:
        break
    full.update(bad)
if BASE + len(stream) > END:
    raise SystemExit('bank 3 records overflow: %d bytes' % (BASE + len(stream) - END))
b3[BASE - 0x8000:BASE - 0x8000 + len(stream)] = stream
for i in range(N):
    b3[0x9E77 - 0x8000 + 2 * i] = ptrs[i] & 255
    b3[0x9E77 - 0x8000 + 2 * i + 1] = ptrs[i] >> 8

# ---------------------------------------------------------------- engine hooks (bank 3)
def patch_jsr(bank, site, target):
    off = site - 0x8000
    assert prg[bank][off] == 0x20 and prg[bank][off + 1] == 0x76 and prg[bank][off + 2] == 0xFF, hex(site)
    prg[bank][off + 1] = target & 255; prg[bank][off + 2] = target >> 8
patch_jsr(3, 0xAB96, tlab['T_INIT'])
patch_jsr(3, 0xAC1B, tlab['T_STEP'])
patch_jsr(3, 0xACA3, tlab['T_BLINK'])
patch_jsr(3, 0xACD9, tlab['T_CLEAR'])
patch_jsr(3, 0xACE7, tlab['T_CLEAR'])
_o = 0x81C6 - 0x8000
assert prg[6][_o:_o + 3] == bytes([0x20, 0xA2, 0xC4]), 'bank 6 main-loop call not found'
prg[6][_o + 1] = tlab['T_MAIN'] & 255; prg[6][_o + 2] = tlab['T_MAIN'] >> 8

# ---------------------------------------------------------------- title screen line
TITLE_TEXT = vi_script.TITLE
FREE_TILES = [1, 2, 3, 172, 173, 174, 175] + list(range(236, 256))     # BG tiles unused by the title nametable
TCOLS = 13
tbm = vf.render(TITLE_TEXT); TW = len(tbm[0])
assert TW <= TCOLS * 8 - 2, 'title text too wide: %d' % TW
# 16-row cell: glyph rows at y=2..13, 1-px black outline (colour 3), white ink (colour 1)
cell = [[0] * (TCOLS * 8) for _ in range(16)]
ox = (TCOLS * 8 - TW) // 2
ink = set((ox + x, 2 + y) for y in range(12) for x in range(TW) if tbm[y][x])
for (x, y) in ink:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            xx, yy = x + dx, y + dy
            if 0 <= xx < TCOLS * 8 and 0 <= yy < 16 and (xx, yy) not in ink:
                cell[yy][xx] = 3
for (x, y) in ink: cell[y][x] = 1
tid = []; tnt0 = []; tnt1 = []; tpat = bytearray()
for c in range(TCOLS):
    for half in range(2):
        t = FREE_TILES[2 * c + half]; tid.append(t)
        p0 = bytearray(8); p1 = bytearray(8)
        for yy in range(8):
            for xx in range(8):
                col = cell[half * 8 + yy][c * 8 + xx]
                if col & 1: p0[yy] |= 0x80 >> xx
                if col & 2: p1[yy] |= 0x80 >> xx
        tpat += p0 + p1
    tnt0.append(tid[-2]); tnt1.append(tid[-1])
TITLE_DATA = bytes(tid) + bytes(tnt0) + bytes(tnt1) + bytes(tpat)

# ---------------------------------------------------------------- fixed bank
fixed = bytearray(prg[7])
for a, b in tsegs:
    o = a - 0xC000
    assert all(x == 0xFF for x in fixed[o:o + len(b)]), 'fixed space not free'
    fixed[o:o + len(b)] = b
for site in (0xC15B, 0xC164, 0xFCA6, 0xFCBA):
    o = site - 0xC000
    assert fixed[o:o + 3] == bytes([0x9D, 0x5F, 0xFF]), hex(site)
    fixed[o + 1] = 0x2A; fixed[o + 2] = 0xC0
prg[7] = fixed

# ---------------------------------------------------------------- data banks 8..14
banks = []
for bi in range(7):
    bank = bytearray(b'\xFF' * BANK)
    for a, b in wsegs:
        bank[a - 0x8000:a - 0x8000 + len(b)] = b
    bank[0] = 8 + bi
    p = 0x8640
    for k in range(32):
        i = bi * 32 + k
        inf = rowinfo.get(i)
        if inf is None:
            inf = dict(flags=0x80, n12=0, n8=0, dx8=0, d12=b'', d8=b'')
        ptr = p
        off8 = 6 + len(inf['d12'])
        rec = bytes([inf['flags'], inf['n12'], inf['n8'], inf['dx8'], off8 & 255, off8 >> 8]) + inf['d12'] + inf['d8']
        bank[p - 0x8000:p - 0x8000 + len(rec)] = rec
        p += len(rec)
        assert p < 0xC000, 'bank %d overflow' % (8 + bi)
        bank[0x8600 - 0x8000 + 2 * k] = ptr & 255
        bank[0x8600 - 0x8000 + 2 * k + 1] = ptr >> 8
    if bi == 0:
        assert p <= 0xB800, 'bank 8 data collides with title data'
        bank[0xB800 - 0x8000:0xB800 - 0x8000 + len(TITLE_DATA)] = TITLE_DATA
    banks.append(bank)

allbanks = [bytearray(x) for x in prg[:7]] + [bytearray(prg[7])] + banks + [bytearray(prg[7])]
assert len(allbanks) == 16
hdr = bytearray(ORIG[:16]); hdr[4] = 16
rom = bytes(hdr) + b''.join(bytes(b) for b in allbanks)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(rom)
print('wrote', OUT, len(rom), 'bytes; bank3 records end $%04X' % (BASE + len(stream)))
