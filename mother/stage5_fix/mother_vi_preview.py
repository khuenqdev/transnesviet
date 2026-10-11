
#!/usr/bin/env python3
"""
mother_vi_preview.py - Stage 2 verification for the Vietnamese font.

  python mother_vi_preview.py chart  ROM OUT.png
      Full Vietnamese alphabet laid out with the mark-row scheme, drawn from the ROM's CHR.

  python mother_vi_preview.py ingame ORIGINAL_ROM PATCHED_ROM OUTDIR
      Boots BOTH ROMs in the MMC3 emulator (mmc3.py) with the same scripted input
      (title -> file select -> naming -> intro -> bedroom -> Talk), checks that every
      checkpoint screen is pixel-identical (the replaced tiles are unused), then writes a
      Vietnamese test message into the real dialogue window using the mark-row layout
      that the stage-3 renderer will produce.  ~6 min per ROM in pure Python.
"""
import sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from mother_vi_codec import encode
from mother_vi_font import MARK_RANGE

FONT_CHR = 0x1F800

def layout(data, put, row, col, line_step=2):
    """Reference implementation of the stage-3 mark-row rule.
    put(r, c, tile). Marks ($80-$8D) are remembered and drawn at (r-1, c) of the next glyph."""
    r, c, pend = row, col, None
    for b in data:
        if b == 0x01:
            r += line_step; c = col; continue
        if b == 0x00:
            break
        if MARK_RANGE[0] <= b <= MARK_RANGE[1]:
            pend = b; continue
        put(r, c, b)
        if pend is not None:
            put(r - 1, c, pend); pend = None
        c += 1

def chart(rom_path, out_png, S=3):
    rom = open(rom_path, 'rb').read(); C = rom[16 + rom[4] * 0x4000:]
    def px(t):
        b = FONT_CHR + (t - 0x80) * 16
        return [[((C[b + r] >> (7 - c)) & 1) | (((C[b + 8 + r] >> (7 - c)) & 1) << 1) for c in range(8)] for r in range(8)]
    vowels = 'aăâeêioôơuưy'; tones = ['', '\u0301', '\u0300', '\u0309', '\u0303', '\u0323']
    blocks = []
    for vs, extra, title in ((vowels, 'đ', 'lowercase  -  none / sac / huyen / hoi / nga / nang'),
                             (vowels.upper(), 'Đ', 'UPPERCASE  (capital E I Y O+horn U+horn with nang -> lowercase form)')):
        lines = [' '.join(unicodedata.normalize('NFC', v + t) for t in tones) for v in vs] + [' ' + extra]
        blocks.append((lines, title))
    W = 27 * 8; H = 28 * 8
    img = Image.new('RGB', (W * 2 * S, (H + 16) * S), (0, 0, 0)); dr = ImageDraw.Draw(img)
    for k, (lines, title) in enumerate(blocks):
        x0 = k * W
        def put(r, c, t):
            if t < 0x80: return
            p = px(t)
            for y in range(8):
                for x in range(8):
                    if p[y][x]:
                        X = (x0 + c * 8 + x) * S; Y = (16 + r * 8 + y) * S
                        dr.rectangle([X, Y, X + S - 1, Y + S - 1], fill=(255, 255, 255))
        layout(encode('\n'.join(lines), terminate=False), put, 1, 1)
        dr.text((x0 * S + 8, 4), title, fill=(255, 200, 0))
    img.save(out_png)

# ---------------------------------------------------------------------------
BTN = {'A': 0x01, 'B': 0x02, 'SEL': 0x04, 'START': 0x08, 'U': 0x10, 'D': 0x20, 'L': 0x40, 'R': 0x80}

def press(n, b, hold, after):
    n.pad[0] = BTN[b]
    for _ in range(hold): n.run_frame()
    n.pad[0] = 0
    for _ in range(after): n.run_frame()

def idle(n, k):
    for _ in range(k): n.run_frame()

def screen(n):
    full = np.zeros((240, 512, 3), np.uint8)
    full[:, :256] = n.render_nt(0x2000, 0); full[:, 256:] = n.render_nt(0x2400, 0)
    sx = n.frame_scroll[0] if hasattr(n, 'frame_scroll') else 0
    return full[:, sx:sx + 256]

def play(rom_bytes, checkpoints):
    from mmc3 import MMC3
    n = MMC3(rom_bytes)
    idle(n, 400); press(n, 'START', 4, 120); press(n, 'START', 4, 120); press(n, 'A', 4, 120)
    idle(n, 200); press(n, 'START', 4, 150); press(n, 'A', 4, 150)
    checkpoints.append(('file_select_naming', screen(n)))
    for _ in range(5):                       # five names: "AA"
        for b in ['A', 'A', 'D', 'D', 'D', 'D', 'R', 'A']: press(n, b, 3, 12)
        idle(n, 60)
    checkpoints.append(('name_confirm', screen(n)))
    press(n, 'A', 3, 30)
    for i in range(8):
        idle(n, 150)
        if i == 3: press(n, 'A', 3, 10)
    checkpoints.append(('intro_text', screen(n)))
    for i in range(30): press(n, 'A', 2, 90)
    checkpoints.append(('field_menu', screen(n)))
    press(n, 'A', 2, 200)
    checkpoints.append(('dialogue', screen(n)))
    return n

def ingame(orig_path, patched_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    ca, cb = [], []
    play(open(orig_path, 'rb').read(), ca)
    nb = play(open(patched_path, 'rb').read(), cb)
    report = []
    for (name, a), (_, b) in zip(ca, cb):
        same = bool((a == b).all())
        report.append('%-20s %s' % (name, 'identical' if same else 'DIFFERENT'))
        Image.fromarray(b).resize((512, 480), Image.NEAREST).save(os.path.join(outdir, 'regress_%s.png' % name))
    # Vietnamese message in the real dialogue window (rows 19-26, cols 11-33 of the 64x30 map)
    def put(r, c, t):
        nt, cc = (0, c) if c < 32 else (1, c - 32)
        nb.vram[nt * 0x400 + r * 32 + cc] = t
    for r in range(19, 27):
        for c in range(11, 34): put(r, c, 0xA0)
    msg = '◆Anh ơi, em sợ quá!\n Cái đèn hình như\n đang sống dậy kìa!\n Ừ, Ở ĐÂY ẤY! Ặc!'
    layout(encode(msg, terminate=False), put, 20, 11)
    Image.fromarray(screen(nb)).resize((768, 720), Image.NEAREST).save(os.path.join(outdir, 'mother_vi_ingame_preview.png'))
    open(os.path.join(outdir, 'regression.txt'), 'w').write('\n'.join(report) + '\n')
    print('\n'.join(report))

if __name__ == '__main__':
    if sys.argv[1] == 'chart':
        chart(sys.argv[2], sys.argv[3])
    else:
        ingame(sys.argv[2], sys.argv[3], sys.argv[4])
