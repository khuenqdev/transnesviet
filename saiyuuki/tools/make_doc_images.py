#!/usr/bin/env python3
"""Generate every figure used by docs/ (screenshots are produced separately by the node harnesses)."""
import os, sys
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = ROOT + '/work/'; O = ROOT + '/docs/img/'
sys.path.insert(0, ROOT + '/tools')
import viet_font as vf, viet_font8 as vf8
FONT = None
for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf'):
    if os.path.exists(p): FONT = p
def font(sz): return ImageFont.truetype(FONT, sz) if FONT else ImageFont.load_default()

# ------------------------------------------------------------ screenshot pairs
def pair(a, b, out, la='Original (Japanese)', lb='Vietnamese patch', scale=2, crop=None):
    A = Image.open(W + a).convert('RGB'); B = Image.open(W + b).convert('RGB')
    if crop: A = A.crop(crop); B = B.crop(crop)
    A = A.resize((A.width * scale, A.height * scale), Image.NEAREST); B = B.resize((B.width * scale, B.height * scale), Image.NEAREST)
    pad = 36; g = 16
    im = Image.new('RGB', (A.width + B.width + g * 3, A.height + pad + g), (30, 30, 36))
    d = ImageDraw.Draw(im)
    im.paste(A, (g, pad)); im.paste(B, (A.width + 2 * g, pad))
    d.text((g, 8), la, fill=(255, 255, 255), font=font(18)); d.text((A.width + 2 * g, 8), lb, fill=(255, 220, 120), font=font(18))
    im.save(O + out); print(out)
pair('fin_title_jp_t.ppm', 'fin_title_vi_t.ppm', 'fig01_title.png')
pair('npc150_1425.ppm', 'fin_dlg_vi_f300.ppm', 'fig02_dialog.png')
pair('fin_shop_jp_a.ppm', 'fin_shop_vi_a.ppm', 'fig03_shop.png')
pair('fin_stat_jp_x.ppm', 'fin_stat_vi_x.ppm', 'fig04_status.png')

# ------------------------------------------------------------ helpers
def box(ax, x, y, w, h, txt, fc='#e8eefc', ec='#355', fs=9, bold=False, tc='black'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', color=tc, wrap=True)
def arrow(ax, p, q, txt=None, c='#333', fs=8, off=(0, 0.08), style='-|>'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=14, lw=1.4, color=c))
    if txt: ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], txt, ha='center', va='bottom', fontsize=fs, color=c)
def newfig(w, h, xl, yl):
    f, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, xl); ax.set_ylim(0, yl); ax.axis('off'); return f, ax
def save(f, name): f.savefig(O + name, dpi=130, bbox_inches='tight', facecolor='white'); plt.close(f); print(name)

# ------------------------------------------------------------ fig05 ROM layout
f, ax = newfig(12, 6.2, 12, 6.2)
ax.text(6, 5.95, 'PRG-ROM layout: original (128 KB) → patched (256 KB)', ha='center', fontsize=13, fontweight='bold')
ax.text(0.2, 5.5, 'Original: 8 banks × 16 KB', fontsize=10, fontweight='bold')
cols = ['#dfe8ff'] * 7 + ['#ffe9c8']
labs = ['0', '1', '2', '3\ndialog engine\n+ row table', '4\nNMI helper ($AB54)', '5', '6\nmain loop', '7 (fixed)\nengine core\nFF5F table']
for i in range(8):
    box(ax, 0.2 + i * 1.45, 4.3, 1.35, 1.0, 'bank ' + labs[i], fc=cols[i] if i != 3 else '#fff2b3', fs=7.5)
ax.text(0.2, 3.85, 'Patched: 16 banks × 16 KB', fontsize=10, fontweight='bold')
for i in range(16):
    r, c = divmod(i, 8); x = 0.2 + c * 1.45; y = 2.45 - r * 1.35
    if i < 7: fc, t = '#dfe8ff', 'bank %d\n(unchanged)' % i
    if i == 3: fc, t = '#fff2b3', 'bank 3\n5 JSR hooks +\nnew compact\nrow records'
    if i == 6: fc, t = '#fff2b3', 'bank 6\n1 JSR hook\n(title $81C6)'
    if i == 7: fc, t = '#dfe8ff', 'bank 7\n(unused copy)'
    if 8 <= i <= 14: fc, t = '#c9f2d0', 'bank %d\nwindow code +\nrows %d-%d' % (i, (i - 8) * 32, min(212, (i - 8) * 32 + 31))
    if i == 8: t += '\n+ title data'
    if i == 15: fc, t = '#ffd0c8', 'bank 15 FIXED\nold bank 7 +\ntrampolines\nnew bus table'
    box(ax, x, y, 1.35, 1.2, t, fc=fc, fs=7)
ax.text(0.2, 0.15, 'yellow = patched in place · green = new data/code banks (identical code, different data) · red = fixed bank at $C000-$FFFF', fontsize=8)
save(f, 'fig05_rom_layout.png')

# ------------------------------------------------------------ fig06 CPU map / UNROM
f, ax = newfig(9, 5.2, 9, 5.2)
ax.text(4.5, 4.95, 'NES CPU address space with UNROM (mapper 2)', ha='center', fontsize=12, fontweight='bold')
rows = [('$0000-$07FF', 'RAM (2 KB)  –  $0700-$07FF = PPU write buffer', '#ffeed0'), ('$0491-$04FF', 'FREE RAM used by the patch (vars, staging)', '#c9f2d0'),
        ('$2000-$2007', 'PPU registers', '#e8e8e8'), ('$8000-$BFFF', 'SWITCHABLE 16 KB window  ← bank N (write N to ROM = bank select)', '#dfe8ff'),
        ('$C000-$FFFF', 'FIXED 16 KB  = last bank (15 in the patched ROM)', '#ffd0c8')]
for i, (a, t, c) in enumerate(rows):
    box(ax, 0.2, 3.9 - i * 0.85, 8.6, 0.7, a + '   ' + t, fc=c, fs=9)
ax.text(0.2, 0.0, 'Bus conflict: the ROM drives the data bus, so the written value must equal the ROM byte at that address → table where table[N]=N.', fontsize=8)
save(f, 'fig06_cpu_map.png')

# ------------------------------------------------------------ fig07 row record + flags
f, ax = newfig(12, 5.4, 12, 5.4)
ax.text(6, 5.15, 'Dialog row record (bank 3) and flag bits', ha='center', fontsize=13, fontweight='bold')
cells = [('flags', '#ffe9a8'), ('len', '#ffd0c8'), ('addr lo\n(if $10)', '#e0e0e0'), ('addr hi\n(if $10)', '#e0e0e0'), ('tile 0', '#dfe8ff'), ('tile 1', '#dfe8ff'), ('…', '#dfe8ff'), ('tile len-1\n($B3 = ▼)', '#dfe8ff')]
for i, (t, c) in enumerate(cells): box(ax, 0.3 + i * 1.45, 3.9, 1.35, 0.9, t, fc=c, fs=8)
ax.text(0.3, 3.6, 'pointer table at $9E77 (213 × 2 bytes) → records at $A021-$AB0A', fontsize=8.5)
bits = [('$80', 'wait for button, then clear box'), ('$40', 'typewriter (1 tile / 8 frames)'), ('$20', 'chain: continue with next row'), ('$10', 'explicit PPU address in record'),
        ('$08', 'start address from table $AD0C[$52&15]'), ('bits 2-0', 'unused by the engine')]
for i, (b, t) in enumerate(bits):
    box(ax, 0.3 + (i % 2) * 5.9, 2.6 - (i // 2) * 0.85, 1.2, 0.65, b, fc='#fff2b3', fs=10, bold=True)
    ax.text(1.6 + (i % 2) * 5.9, 2.6 - (i // 2) * 0.85 + 0.3, t, fontsize=9, va='center')
ax.text(0.3, 0.1, 'Examples: $E0 = type + chain + wait (end of a page)   $C0 = type + wait, last row   $60 = type + chain   $40 = type, last row   $00 = instant', fontsize=8.5)
save(f, 'fig07_row_record.png')

# ------------------------------------------------------------ fig08 PPU buffer
f, ax = newfig(12, 4.8, 12, 4.8)
ax.text(6, 4.55, 'PPU write buffer ($0700) – what JSR $FF76 builds, what the NMI consumes', ha='center', fontsize=12, fontweight='bold')
for i, (t, c) in enumerate([('flags\n$40 | $08(+32)\n| $80(chain)', '#ffe9a8'), ('len\n(1-127)', '#ffd0c8'), ('PPU addr lo', '#e0e0e0'), ('PPU addr hi', '#e0e0e0'), ('data[0]', '#dfe8ff'), ('…', '#dfe8ff'), ('data[len-1]', '#dfe8ff')]):
    box(ax, 0.3 + i * 1.6, 3.0, 1.5, 1.0, t, fc=c, fs=8)
ax.text(0.3, 2.65, 'Caller sets: ($02/$03) = data pointer · ($04/$05) = PPU address · Y = length (bit 7 = increment by 32, i.e. vertical run) · JSR $FF76', fontsize=8.5)
ax.text(0.3, 2.3, 'Returns carry CLEAR = queued, carry SET = buffer full (the dialog engine retries on the next frame).', fontsize=8.5)
box(ax, 0.3, 0.5, 3.4, 1.2, 'main code\nJSR $FF76 → FD1E\nappends record at $0700+[$20]', fc='#dfe8ff', fs=8.5)
box(ax, 4.3, 0.5, 3.4, 1.2, 'NMI ($C100 → $C1CA)\nreads records, writes $2006/$2007\n≤128 bytes per frame (chain bit)', fc='#c9f2d0', fs=8.5)
box(ax, 8.3, 0.5, 3.4, 1.2, 'PPU\npattern table $0000-$1FFF (CHR-RAM)\nnametable $2000-$2FFF', fc='#ffd0c8', fs=8.5)
arrow(ax, (3.7, 1.1), (4.3, 1.1)); arrow(ax, (7.7, 1.1), (8.3, 1.1))
save(f, 'fig08_ppu_buffer.png')

# ------------------------------------------------------------ fig09 dialog box tile map from VRAM dump
v = open(W + 'npc.vram', 'rb').read()
rows_ = range(8, 16); cols_ = range(2, 30)
f, ax = plt.subplots(figsize=(13, 4.4)); ax.set_xlim(2, 30); ax.set_ylim(16, 7.5); ax.axis('off')
role = lambda r, c, t: ('#c9f2d0' if (r in (10, 11, 12, 13) and 6 <= c <= 25) else ('#ffe9a8' if (8 <= r <= 13 and 4 <= c <= 27) else '#e8e8e8'))
for r in rows_:
    for c in cols_:
        t = v[0x2000 + r * 32 + c]
        ax.add_patch(Rectangle((c, r), 1, 1, fc=role(r, c, t), ec='#888', lw=0.5))
        ax.text(c + 0.5, r + 0.5, '%02X' % t, ha='center', va='center', fontsize=6.5)
for r in range(8, 16): ax.text(1.6, r + 0.5, 'row %d' % r, ha='right', va='center', fontsize=7)
for c in range(2, 30, 2): ax.text(c + 0.5, 7.7, str(c), ha='center', fontsize=7)
ax.set_title('Nametable $2000 around the dialog box (tile ids). Green = text area (cols 6-25, rows 10-13). Row 13 = bottom border ($9E/$9F).', fontsize=10)
save(f, 'fig09_box_tilemap.png')

# ------------------------------------------------------------ fig10 2bpp tile
f, axs = plt.subplots(1, 4, figsize=(13, 3.6))
glyph_rows = ['00011000', '00100100', '01000010', '01111110', '01000010', '01000010', '01000010', '00000000']
pal = {0: '#3caaff', 1: '#ffffff', 2: '#2a50ff', 3: '#000000'}
def draw(ax, grid, title, colors=None, num=False):
    ax.set_xlim(0, 8); ax.set_ylim(8, 0); ax.axis('off'); ax.set_title(title, fontsize=10)
    for y in range(8):
        for x in range(8):
            val = grid[y][x]; ax.add_patch(Rectangle((x, y), 1, 1, fc=colors[val] if colors else ('#222' if val else '#fff'), ec='#999', lw=0.6))
            if num: ax.text(x + .5, y + .5, str(val), ha='center', va='center', fontsize=8, color='white' if val in (1, 3, 0) and colors is None else 'black')
p0 = [[int(c) for c in r] for r in ['11111111'] * 8]
p1 = [[1 - int(c) for c in r] for r in glyph_rows]            # ink = 0 in plane 1
px = [[p0[y][x] | (p1[y][x] << 1) for x in range(8)] for y in range(8)]
draw(axs[0], [[int(c) for c in r] for r in glyph_rows], 'glyph bitmap (1 = ink)')
draw(axs[1], p0, 'plane 0 bytes: $FF ×8', num=True)
draw(axs[2], p1, 'plane 1 bytes: ~glyph', num=True)
draw(axs[3], px, 'colour = p0 | p1<<1\n(1 = white ink, 3 = black bg)', colors=pal, num=True)
f.suptitle('One 8×8 tile = 16 bytes: 8 bytes plane 0, then 8 bytes plane 1', fontsize=12, fontweight='bold')
save(f, 'fig10_tile_2bpp.png')

# ------------------------------------------------------------ fig11 font cell anatomy
def bm_img(text, mod=vf, h=12, sc=14, guides=True):
    bm = mod.render(text); Wd = len(bm[0]); im = Image.new('RGB', (Wd * sc + 90, h * sc), (255, 255, 255)); d = ImageDraw.Draw(im)
    for y in range(h):
        for x in range(Wd):
            if bm[y][x]: d.rectangle([80 + x * sc, y * sc, 80 + (x + 1) * sc - 2, (y + 1) * sc - 2], fill=(20, 20, 20))
    return im
im = bm_img('Ểg Nặp Ọ')
im2 = Image.new('RGB', (im.width + 280, im.height), (255, 255, 255)); im2.paste(im, (0, 0)); d = ImageDraw.Draw(im2)
sc = 14
guide = [(0, 'rows 0-1: tone marks (capitals)'), (2, 'row 2: gap'), (3, 'row 3: capital / ascender top'), (5, 'row 5: x-height top'), (9, 'row 9: BASELINE'), (10, 'rows 10-11: descender (g p q y), nặng dot')]
for r, t in guide:
    d.line([(78, r * sc), (im.width, r * sc)], fill=(200, 60, 60), width=1); d.text((im.width + 8, r * sc - 2), t, fill=(160, 0, 0), font=font(11))
im2.save(O + 'fig11_font_cell.png'); print('fig11_font_cell.png')
# font sheets
os.system('cd %s/tools && python3 viet_font.py %s/fig12_font12.png >/dev/null && python3 viet_font8.py %s/fig12_font8.png >/dev/null' % (ROOT, O, O))

# ------------------------------------------------------------ fig13 hook flow
f, ax = newfig(12, 6.4, 12, 6.4)
ax.text(6, 6.15, 'Hook architecture: how one JSR $FF76 becomes a bitmap draw', ha='center', fontsize=13, fontweight='bold')
box(ax, 0.2, 4.6, 3.3, 1.2, 'BANK 3 (dialog engine)\nAB96 JSR $FF76  ← patched to\nJSR T_INIT / T_STEP / T_BLINK / T_CLEAR', fc='#fff2b3', fs=8.5)
box(ax, 4.2, 4.6, 3.6, 1.2, 'BANK 15 (fixed) tramp.asm\nsave $02-$05 → pick bank 8+row/32\nJSR $FCAA (switch) ; JSR $8001', fc='#ffd0c8', fs=8.5)
box(ax, 8.5, 4.6, 3.3, 1.2, 'BANK 8..14 window.asm @ $8000\nclassify → setrow → draw_step\n(compose 2 tiles from row bitmap)', fc='#c9f2d0', fs=8.5)
arrow(ax, (3.5, 5.2), (4.2, 5.2), 'JSR'); arrow(ax, (7.8, 5.2), (8.5, 5.2), 'JSR')
box(ax, 8.5, 2.7, 3.3, 1.1, 'JSR $FF76 ×2\n① 32 B pattern → CHR-RAM tile pair\n② 2 nametable bytes (vertical)', fc='#dfe8ff', fs=8.5)
arrow(ax, (10.15, 4.6), (10.15, 3.8))
box(ax, 4.2, 2.7, 3.6, 1.1, 'return: RET var → carry\n(bank restored, $02-$05 restored)', fc='#ffd0c8', fs=8.5)
arrow(ax, (8.5, 3.2), (7.8, 3.2)); arrow(ax, (4.2, 3.2), (3.5, 3.2)); 
box(ax, 0.2, 2.7, 3.3, 1.1, 'engine continues: BCC ok /\nBCS retry next frame\n(typewriter timer, ▼, chain…)', fc='#fff2b3', fs=8.5)
box(ax, 0.2, 0.6, 5.4, 1.4, 'Row data bank (per row):\nflags | n12 | n8 | dx8 | off8 | n12×12 bytes (12-px columns) | n8×8 bytes (8-px strip)', fc='#e8f6ff', fs=8.5)
box(ax, 6.4, 0.6, 5.4, 1.4, 'POOL tiles (68): $B0-$B3, $BF-$CA, $CC-$FF\nline 0 = 17 tile pairs, line 1 = 17 tile pairs\n(digits $B4-$BD, × $BE, yuan-kanji $CB are preserved)', fc='#e8f6ff', fs=8.5)
arrow(ax, (10.15, 2.7), (9.0, 2.0)); arrow(ax, (2.9, 2.7), (2.9, 2.0), style='-')
save(f, 'fig13_hook_flow.png')

# ------------------------------------------------------------ fig14 pool map
f, ax = plt.subplots(figsize=(13, 3.6)); ax.set_xlim(0, 18.5); ax.set_ylim(0, 5.4); ax.axis('off')
POOL = [0xB0, 0xB2, 0xBF, 0xC1, 0xC3, 0xC5, 0xC7, 0xC9] + list(range(0xCC, 0x100, 2))
for line in range(2):
    for c in range(17):
        t = POOL[line * 17 + c]
        for half in range(2):
            ax.add_patch(Rectangle((1.2 + c, 4.0 - line * 2.3 - half * 0.9), 1, 0.9, fc='#c9f2d0' if line == 0 else '#dfe8ff', ec='#555', lw=0.7))
            ax.text(1.7 + c, 4.45 - line * 2.3 - half * 0.9, '%02X' % (t + half), ha='center', va='center', fontsize=6.5)
ax.text(0.1, 4.5, 'line 0\ntop\n/bottom', fontsize=7.5, va='center'); ax.text(0.1, 2.2, 'line 1', fontsize=7.5, va='center')
for c in range(17): ax.text(1.7 + c, 5.15, str(c), ha='center', fontsize=7)
ax.text(9.5, 0.4, 'Each column = a vertical pair of tiles (top 8 px + bottom 4 px of text + 4 px padding / box border). 34 pairs = 68 tiles.', ha='center', fontsize=9)
ax.set_title('Dialog tile pool: (line, column) → tile pair', fontsize=11, fontweight='bold')
save(f, 'fig14_pool_map.png')

# ------------------------------------------------------------ fig15 record packing
f, ax = newfig(12, 4.6, 12, 4.6)
ax.text(6, 4.35, 'Compact record packing in bank 3 (why 213 longer rows still fit)', ha='center', fontsize=12, fontweight='bold')
ax.text(0.2, 3.7, 'Original: every record carries len placeholder bytes', fontsize=9)
x = 0.2
for t, w, c in [('F L', 0.5, '#ffe9a8'), ('kana ×len', 1.6, '#dfe8ff'), ('F L', 0.5, '#ffe9a8'), ('kana ×len', 2.2, '#dfe8ff'), ('F L', 0.5, '#ffe9a8'), ('kana ×len', 1.4, '#dfe8ff')]:
    box(ax, x, 2.8, w, 0.7, t, fc=c, fs=8); x += w + 0.05
ax.text(0.2, 2.2, 'Patched: engine only reads data[len-1] (the wait test "= $B3"), so non-wait rows keep just the 2-byte header and their', fontsize=9)
ax.text(0.2, 1.9, '"data" overlaps the following records; only rows ending in ▼ keep a real body with $B3 in the last byte.', fontsize=9)
x = 0.2
for t, w, c in [('F L', 0.5, '#ffe9a8'), ('F L', 0.5, '#ffe9a8'), ('F L', 0.5, '#ffe9a8'), ('F L  00 00 00 B3  (▼ row)', 2.6, '#ffd0c8'), ('F L', 0.5, '#ffe9a8'), ('F L', 0.5, '#ffe9a8')]:
    box(ax, x, 0.8, w, 0.7, t, fc=c, fs=7.5); x += w + 0.05
ax.text(0.2, 0.3, 'build_rom.py verifies byte[ptr+hdr+len-1] != $B3 for every non-wait row and pads if not.', fontsize=8.5)
save(f, 'fig15_record_packing.png')

# ------------------------------------------------------------ fig16 typewriter state machine
f, ax = newfig(12, 5.2, 12, 5.2)
ax.text(6, 4.95, 'Dialog engine, per frame ($AB0B) – simplified state machine', ha='center', fontsize=12, fontweight='bold')
box(ax, 0.2, 3.5, 2.6, 1.0, 'row start\n(read flags,len,addr)\nT_INIT hook', fc='#fff2b3', fs=8.5)
box(ax, 3.5, 3.5, 2.6, 1.0, 'typewriter?\nyes: draw col 0\nno: draw all cols', fc='#e8f6ff', fs=8.5)
box(ax, 6.8, 3.5, 2.6, 1.0, 'every 8th frame:\ndraw col $54\nT_STEP hook', fc='#fff2b3', fs=8.5)
box(ax, 10.0, 3.5, 1.8, 1.0, 'last col?', fc='#e8f6ff', fs=8.5)
arrow(ax, (2.8, 4.0), (3.5, 4.0)); arrow(ax, (6.1, 4.0), (6.8, 4.0)); arrow(ax, (9.4, 4.0), (10.0, 4.0))
box(ax, 7.4, 1.7, 2.2, 1.0, 'last byte = $B3?\nblink ▼ (T_BLINK /\nT_STEP)', fc='#ffd0c8', fs=8)
box(ax, 4.2, 1.7, 2.6, 1.0, 'button pressed?\nclear both lines\n(T_CLEAR ×2)', fc='#fff2b3', fs=8)
box(ax, 0.6, 1.7, 2.8, 1.0, '$20 chain → next row\n($51 += 1) else end', fc='#c9f2d0', fs=8)
arrow(ax, (10.9, 3.5), (9.6, 2.6)); arrow(ax, (7.4, 2.2), (6.8, 2.2)); arrow(ax, (4.2, 2.2), (3.4, 2.2))
ax.text(0.2, 0.7, 'Any hook returning carry set (PPU buffer full) makes the engine retry on the next frame – the patch keeps its own progress (PROG/PROGR vars).', fontsize=8.5)
save(f, 'fig16_engine_states.png')

# ------------------------------------------------------------ fig17 title free tiles
v = open(W + 'ti_t.vram', 'rb').read()
used = set(v[0x2000:0x2000 + 960]) | set(v[0x2400:0x2400 + 960])
f, ax = plt.subplots(figsize=(11, 5.4)); ax.set_xlim(0, 16); ax.set_ylim(16, 0); ax.axis('off')
for t in range(256):
    r, c = divmod(t, 16); ax.add_patch(Rectangle((c, r), 1, 1, fc='#cfd8e8' if t in used else '#7be08a', ec='#777', lw=0.5)); ax.text(c + .5, r + .5, '%02X' % t, ha='center', va='center', fontsize=6.5)
ax.set_title('Title screen: BG tiles referenced by its nametables (blue) vs free (green) – only 27 free tiles → one text line', fontsize=10)
save(f, 'fig17_title_free_tiles.png')

# ------------------------------------------------------------ fig18 build pipeline
f, ax = newfig(12, 4.6, 12, 4.6)
ax.text(6, 4.35, 'Build pipeline (tools/build_rom.py)', ha='center', fontsize=13, fontweight='bold')
bx = [(0.2, 2.8, 'original.nes\n(8 banks)', '#dfe8ff'), (2.7, 2.8, 'vi_script.py\n(TEXT/SMALL/TITLE)', '#fff2b3'), (5.2, 2.8, 'viet_font.py\nviet_font8.py', '#fff2b3'), (7.7, 2.8, 'window.asm\ntramp.asm\n(asm6502.py)', '#fff2b3')]
for x, y, t, c in bx: box(ax, x, y, 2.2, 1.0, t, fc=c, fs=8.5)
box(ax, 3.0, 1.2, 6.0, 1.0, 'build_rom.py: bitmaps → 12-byte columns · pack bank-3 records · patch 6 JSR sites · bus table · title data · banks 8-14 · 256 KB', fc='#c9f2d0', fs=8.5)
for x, y, t, c in bx: arrow(ax, (x + 1.1, 2.8), (6.0, 2.2), style='-|>')
box(ax, 9.4, 1.2, 2.4, 1.0, 'saiyuuki_vi.nes\n+ make_ips.py → .ips', fc='#ffd0c8', fs=8.5)
arrow(ax, (9.0, 1.7), (9.4, 1.7))
box(ax, 3.0, 0.0, 6.0, 0.8, 'tests: emu.mjs / ui_test.mjs / state_test.mjs (jsnes) → screenshots', fc='#e8f6ff', fs=8.5)
arrow(ax, (10.6, 1.2), (9.0, 0.5))
save(f, 'fig18_build_pipeline.png')

# ------------------------------------------------------------ fig19 status screen slots
f, ax = newfig(10, 5.4, 10, 5.4)
ax.text(5, 5.15, 'Status screen strips (8-px font, one tile row each)', ha='center', fontsize=12, fontweight='bold')
box(ax, 0.2, 3.8, 3.0, 1.0, 'MẠNG   ♥♥♥♥♥\n$2061 (3 cols)', fc='#e8f6ff', fs=8.5)
box(ax, 3.4, 3.8, 3.0, 1.0, 'BẠC   0 (yuan kanji)\n$206D (3 cols)', fc='#e8f6ff', fs=8.5)
box(ax, 6.6, 3.8, 3.0, 1.0, 'CÔNG\n$2077 (3 cols)', fc='#e8f6ff', fs=8.5)
box(ax, 0.2, 0.3, 4.4, 3.2, 'BẢO VẬT  ($2165)\nitem names at\n$21C5 $2205 $2245\n$2285 $22C5 $2305\n(5 cols each)', fc='#fff2b3', fs=9)
box(ax, 4.9, 0.3, 4.7, 3.2, 'VŨ KHÍ  ($2175)\nweapon names at\n$21B5 $2235 $22B5 $2335\n(5 cols each)', fc='#c9f2d0', fs=9)
save(f, 'fig19_status_slots.png')
print('done')
