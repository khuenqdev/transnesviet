# Galaxian (NES) Vietnamese translation builder
import zlib, json, sys
from glyphs import G

SRC = 'galaxian.nes'
rom = bytearray(open(SRC, 'rb').read())
orig = bytes(rom)
assert zlib.crc32(orig) & 0xFFFFFFFF == 0x8451DC60

PRG = 0x10            # file offset of $E000
CHR = 0x2010          # file offset of CHR $0000
def cpu2file(a): return PRG + (a - 0xE000)
def chr2file(a): return CHR + a

# ---------------------------------------------------------------- glyph slots
# 'both' = written to PT0 and PT1 at the same index; 0 / 1 = single table only.
SLOTS = json.load(open('slots.json'))
def put_tile(pt, idx, rows):
    base = chr2file(pt * 0x1000 + idx * 16)
    for r, row in enumerate(rows):
        bits = int(row.replace('#', '1').replace('.', '0'), 2)
        rom[base + r] = bits        # plane 0 -> colour 1 (same as the game's letters)
        rom[base + 8 + r] = 0x00    # plane 1 empty
TILE = {}                           # Vietnamese char -> {pt: tile}
for ch, (where, idx) in SLOTS.items():
    idx = int(idx, 16)
    pts = (0, 1) if where == 'both' else (int(where),)
    for pt in pts: put_tile(pt, idx, G[ch])
    TILE[ch] = {pt: idx for pt in pts}

# ---------------------------------------------------------------- text encoding
BASE = {' ': 0x10, '-': 0x2B, '.': 0x2C, '©': 0x2D, ':': 0xA3}
for i, c in enumerate('0123456789'): BASE[c] = i
for i in range(26): BASE[chr(65 + i)] = 0x11 + i
ALT = {'1': 0x0A, '2': 0x0B, '4': 0x0C, '7': 0x0D, '8': 0x0E, '9': 0x0F}   # letter-coloured digits

def enc(text, pt, altdigits=False):
    out = []
    for ch in text:
        if ch in TILE:
            assert pt in TILE[ch], (ch, pt, text)
            t = TILE[ch][pt]
        elif altdigits and ch in ALT: t = ALT[ch]
        else:
            t = BASE[ch]
        b = (t + 0x30) & 0xFF        # print routine subtracts $06D6 (=$30)
        assert b != 0x2A, text
        out.append(b)
    return out

# ---------------------------------------------------------------- strings
# (id, row, col, text, pattern-table(s) it is displayed with, alt-digit colour)
#  pt 'both' means it must render under PT0 *and* PT1.
S = [
 (0,  3, 0,  'NGƯỜI 1',                    'both', True),   # 1UP
 (1,  3, 9,  'ĐIỂM CAO',                   'both', False),  # HI-SCORE
 (2,  3, 19, 'NGƯỜI 2',                    'both', True),   # 2UP (title)
 (31, 3, 0,  'NGƯỜI 2',                    1,      True),   # 2UP (in game)
 (3,  7, 0,  'NHIỆM VỤ: DIỆT SINH VẬT LẠ', 1,      False),  # MISSION: DESTROY ALIENS
 (4,  9, 3,  'CHÚNG TA LÀ GALAXIAN',       1,      False),  # WE ARE THE GALAXIANS
 (5,  12, 6, '- BẢNG ĐIỂM -',              1,      False),  # - SCORE ADVANCE TABLE -
 (6,  14, 3, 'ĐỘI HÌNH  LAO XUỐNG',        1,      False),  # CONVOY  CHARGER
 (27, 17, 7, '60           ĐIỂM',          1,      False),  # 60 ... PTS
 (28, 19, 7, '50       100 ĐIỂM',          1,      False),
 (29, 21, 7, '40        80 ĐIỂM',          1,      False),
 (30, 23, 7, '30        60 ĐIỂM',          1,      False),
 (23, 17, 16, '150', 1, False), (24, 17, 16, '200', 1, False),
 (25, 17, 16, '300', 1, False), (26, 17, 16, '800', 1, False),
 (7,  16, 9, '1 NGƯỜI CHƠI',               0,      True),   # 1 PLAYER
 (8,  18, 9, '2 NGƯỜI CHƠI',               0,      True),   # 2 PLAYERS
 (9,  24, 2, '©1979 1984 NAMCO LTD.',      0,      True),   # unchanged
 (10, 26, 4, 'BẢO LƯU MỌI QUYỀN',          0,      False),  # ALL RIGHTS RESERVED
 (17, 18, 7, 'NGƯỜI CHƠI 1',               1,      True),   # PLAYER 1
 (18, 18, 7, 'NGƯỜI CHƠI 2',               1,      True),   # PLAYER 2
 (19, 20, 9, 'KẾT THÚC',                   1,      False),  # GAME  OVER
 (20, 20, 9, 'READY_VI',                   1,      False),  # READY  (filled below)
 (21, 20, 8, 'TẠM NGƯNG',                  1,      False),  # PAUSE (column patched at run time)
 (32, 20, 0, '', 1, False), (33, 18, 0, '', 1, False),
]
READY_VI = json.load(open('options.json'))['ready']
S = [(i, r, c, (READY_VI if t == 'READY_VI' else t), p, a) for (i, r, c, t, p, a) in S]

def build_string(row, col, text, pt, alt):
    pts = (0, 1) if pt == 'both' else (pt,)
    encs = [enc(text, p, alt) for p in pts]
    assert all(e == encs[0] for e in encs), ('glyph index differs between PTs', text)
    assert col + len(text) <= 26, text
    return bytes([row, col] + encs[0] + [0x2A])

blobs = {i: build_string(r, c, t, p, a) for (i, r, c, t, p, a) in S}

# ---------------------------------------------------------------- pack into CHR text areas
PTR_TAB = 0x1480                    # $0300 in RAM; pointer for string n at +1+2n
n_ptrs = 35
ptr = lambda n: PTR_TAB + 1 + 2 * n
logo_ids = [11, 12, 13, 14, 15, 16, 22, 34]
def rdptr(n):
    f = chr2file(ptr(n)); return orig[f] | orig[f + 1] << 8
areas = [[0x14C7, 0x1500], [0x159C, 0x1600], [0x1700, 0x1800]]   # [start, end)
# keep logo strings exactly where they are (they live at $1500-$159B)
for n in logo_ids: assert 0x1500 <= rdptr(n) < 0x159C
# clear old text areas
for a, b in areas:
    for x in range(a, b): rom[chr2file(x)] = 0xFF
order = sorted(blobs, key=lambda i: -len(blobs[i]))
placed = {}
free = [list(x) for x in areas]
for i in order:
    L = len(blobs[i])
    for fr in free:
        if fr[1] - fr[0] >= L:
            placed[i] = fr[0]; fr[0] += L; break
    else:
        raise SystemExit('out of string space for %d' % i)
for i, a in placed.items():
    f = chr2file(a); rom[f:f + len(blobs[i])] = blobs[i]
    p = chr2file(ptr(i)); rom[p] = a & 0xFF; rom[p + 1] = a >> 8
used = sum(len(b) for b in blobs.values()); cap = sum(b - a for a, b in areas)
print('string bytes %d / %d' % (used, cap))

# ---------------------------------------------------------------- code patches
def patch_prg(cpu, expect, new):
    f = cpu2file(cpu)
    assert bytes(rom[f:f + len(expect)]) == bytes(expect), ('mismatch @%04X' % cpu, rom[f:f+len(expect)].hex())
    rom[f:f + len(new)] = bytes(new)

# PAUSE column: col = (clamp($84 - E4, $30, $D0) - $30) >> 3, stored into the string's column byte
pause_len = len('TẠM NGƯNG')
shift = (pause_len - 5) * 4                          # keep it centred (half the extra width, in px)
maxcol = 26 - pause_len
patch_prg(0xE384, [0x69, 0x84, 0xC9, 0x30, 0xB0, 0x02, 0xA9, 0x30, 0xC9, 0xD1, 0x90, 0x02, 0xA9, 0xD0],
          [0x69, 0x84 - shift, 0xC9, 0x30, 0xB0, 0x02, 0xA9, 0x30, 0xC9, 0x30 + maxcol * 8 + 1, 0x90, 0x02, 0xA9, 0x30 + maxcol * 8])
col_ram = placed[21] + 1 - 0x1180                     # RAM copy of PAUSE column byte
patch_prg(0xE398, [0x8D, 0x03, 0x06], [0x8D, col_ram & 0xFF, col_ram >> 8])

# GAME OVER fly-in sprites (PT0 tiles) -> "KẾT THÚC"
go_tiles = [BASE['K'], TILE['Ế'][0], BASE['T'], 0x10, BASE['T'], BASE['H'], TILE['Ú'][0], BASE['C']]
go_x = [0x60, 0x68, 0x70, 0x78, 0x80, 0x88, 0x90, 0x98]
patch_prg(0xFBDB, [0x17, 0x11, 0x1D, 0x15, 0x1F, 0x26, 0x15, 0x22, 0x58, 0x60, 0x68, 0x70, 0x88, 0x90, 0x98, 0xA0],
          go_tiles + go_x)

open('galaxian_vi.nes', 'wb').write(rom)
print('patched CRC32 %08X' % (zlib.crc32(rom) & 0xFFFFFFFF))
json.dump({str(k): '%04X' % v for k, v in placed.items()}, open('placed.json', 'w'))

# ---------------------------------------------------------------- IPS
def make_ips(a, b):
    out = bytearray(b'PATCH'); i = 0
    while i < len(b):
        if a[i] == b[i]: i += 1; continue
        j = i
        while j < len(b) and (j - i) < 0xFFFF and (a[j] != b[j] or (j + 1 < len(b) and a[j+1] != b[j+1] and j + 2 < len(b))):
            j += 1
        if i == 0x454F46: i -= 1                   # avoid 'EOF' offset
        out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + b[i:j]
        i = j
    out += b'EOF'; return bytes(out)
def apply_ips(a, p):
    a = bytearray(a); k = 5
    while p[k:k+3] != b'EOF':
        off = int.from_bytes(p[k:k+3], 'big'); ln = int.from_bytes(p[k+3:k+5], 'big'); k += 5
        if ln == 0:
            rl = int.from_bytes(p[k:k+2], 'big'); v = p[k+2]; k += 3; a[off:off+rl] = bytes([v]) * rl
        else:
            a[off:off+ln] = p[k:k+ln]; k += ln
    return bytes(a)
ips = make_ips(orig, bytes(rom))
assert apply_ips(orig, ips) == bytes(rom)
open('galaxian_vi.ips', 'wb').write(ips)
print('IPS %d bytes, %d changed bytes' % (len(ips), sum(1 for x, y in zip(orig, rom) if x != y)))
