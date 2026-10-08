#!/usr/bin/env python3
"""Ninja Gaiden II (USA) -> Vietnamese, fixed build (rev 3).

Outputs (in ../release):
  Ninja_Gaiden_II_Vietnamese_Text_FIXED.nes / .ips
  Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.nes / .ips
  (+ .tbl / .ext / glyph dump / manifest / plain-text script)

What the game's dialog engine actually does (found by emulation, see README):
  * Only byte values $00-$7F are printable glyphs.  Everything >= $80 is a
    control code (newline $A0, page $A1, end $A6, ...).  So every Vietnamese
    glyph must live in $00-$7F.
  * Printable code C is drawn from CHR-ROM tile  $40 + C   (C < $80).
    (The text banks are mapped [1,2,0,3]; for C < $80 this is linear.)
  * The credits block (untranslated English) still needs its own letters, so
    those codes are protected.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, zlib, re, json, unicodedata, importlib.util, collections

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'source'
REF = ROOT / 'reference' / 'spanish_extracted'
OUT = ROOT / 'release'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'base' / 'Ninja Gaiden II - The Dark Sword of Chaos (USA).nes'
EXPECTED_SHA1 = '269478947a5bc518551ab5d7b4687653006e243c'
CHR0 = 0x10 + 0x20000          # file offset of CHR-ROM
CREDITS = (0x15BD1, 0x15F20)   # untranslated English credit strings

spec = importlib.util.spec_from_file_location('translation_data', SRC / 'translation_data.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
T = mod.T

UP = {chr(65 + i): 1 + i for i in range(26)}
LO = {chr(97 + i): 0x21 + i for i in range(26)}
DIG = {str(i): 0x50 + i for i in range(10)}
PUNC = {' ': 0x3F, '!': 0x41, '"': 0x42, "'": 0x45, ',': 0x4C, '-': 0x4D, '.': 0x4E, '/': 0x4F,
        ':': 0x5A, '?': 0x5F, '&': 0x46, '%': 0x47, '(': 0x48, ')': 0x49, '*': 0x4A, '+': 0x4B,
        '$': 0x44, '<': 0x5C, '>': 0x5E, '[': 0x1B, ']': 0x1D, '_': 0x63, '=': 0xA0, '^': 0xA1,
        '¨': 0x65}

# Printable codes whose glyphs are still needed by the untranslated credits.
PROTECTED = {0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0x0C,0x0D,0x0E,0x0F,0x10,
             0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x3F,0x4C,0x4D,0x4E,0x52,0x60,0x61,0x62,0x63,0x64}
# Codes verified (emulator frame diff over intro, 15 cutscenes, endings, gameplay) to be
# invisible outside the dialog text.  The last group appears for a single bottom-edge
# (overscan) frame during the ending-credit transition, so it is used last.
LAST_RESORT = [0x50, 0x54, 0x56, 0x58, 0x59, 0x5A, 0x70]

# Characters that cannot get a glyph (only 63 free cells exist; $60-$62 draw the "II" of
# "NINJA-II" in the credits); each falls back to its base letter.  Chosen as the least frequent in the script.
DROPPED = {'Í': 'I', 'Ý': 'Y', 'Ơ': 'O', 'Ư': 'U', 'ỹ': 'y', 'ẹ': 'e',
           'ễ': 'e', 'ụ': 'u', 'õ': 'o'}


def plain(text):
    for k, v in DROPPED.items():
        text = text.replace(k, v)
    return text


TEXT = {k: plain(v) for k, v in T.items()}


def diacritics(ch):
    EXPLICIT = {'ă': ('a', {'breve'}), 'â': ('a', {'circumflex'}), 'ê': ('e', {'circumflex'}),
                'ô': ('o', {'circumflex'}), 'ơ': ('o', {'horn'}), 'ư': ('u', {'horn'}),
                'đ': ('d', {'bar'}), 'Ă': ('A', {'breve'}), 'Â': ('A', {'circumflex'}),
                'Ê': ('E', {'circumflex'}), 'Ô': ('O', {'circumflex'}), 'Ơ': ('O', {'horn'}),
                'Ư': ('U', {'horn'}), 'Đ': ('D', {'bar'})}
    if ch in EXPLICIT:
        return EXPLICIT[ch]
    n = unicodedata.normalize('NFD', ch)
    if len(n) == 1:
        return ch, set()
    names = {'́': 'acute', '̀': 'grave', '̂': 'circumflex', '̆': 'breve',
             '̛': 'horn', '̉': 'hook', '̃': 'tilde', '̣': 'dot'}
    marks = set()
    for m in n[1:]:
        if m not in names:
            return None
        marks.add(names[m])
    return n[0], marks


def strip_tokens(s):
    return re.sub(r'~[0-9A-Fa-f]+~', '', s)


# ---- glyph / code allocation -------------------------------------------------------------
freq = collections.Counter()
for s in TEXT.values():
    freq.update(strip_tokens(s))
needs_glyph = [ch for ch in freq
               if ch not in UP and ch not in LO and ch not in DIG and ch not in PUNC
               and diacritics(ch) is not None]
needed_codes = {c for ch in freq for tbl in (UP, LO, PUNC) for k, c in tbl.items() if k == ch}
pool = [c for c in range(0x80) if c not in needed_codes and (c not in PROTECTED)]
pool = [c for c in pool if c not in LAST_RESORT] + [c for c in LAST_RESORT if c in pool]
if len(needs_glyph) > len(pool):
    raise SystemExit(f'need {len(needs_glyph)} glyph cells, only {len(pool)} free')
order = sorted(needs_glyph, key=lambda c: (-freq[c], c))        # frequent glyphs -> safest cells
CUSTOM = {ch: code for ch, code in zip(order, pool)}


def encode(s):
    out = bytearray(); i = 0
    while i < len(s):
        if s[i] == '~':
            j = s.find('~', i + 1)
            if j < 0:
                raise ValueError(f'bad token in {s!r}')
            out.append(int(s[i + 1:j], 16)); i = j + 1; continue
        ch = s[i]
        for tbl in (UP, LO, DIG, PUNC, CUSTOM):
            if ch in tbl:
                out.append(tbl[ch]); break
        else:
            raise ValueError(f'No one-byte mapping for {ch!r}')
        i += 1
    return bytes(out)


# ---- font ---------------------------------------------------------------------------------
def tile_off(code):
    assert code < 0x80
    return CHR0 + (0x40 + code) * 16


def accent(g, kind):
    patterns = {'acute': [(0, [1]), (1, [2]), (2, [3])], 'grave': [(0, [6]), (1, [5]), (2, [4])],
                'circumflex': [(0, [3, 4]), (1, [2, 5]), (2, [1, 6])],
                'breve': [(0, [3, 4]), (1, [2, 5]), (2, [1, 6])],
                'horn': [(1, [1]), (2, [1]), (3, [2])],
                'hook': [(0, [6, 5]), (1, [6]), (2, [5])],
                'tilde': [(0, [1, 2, 5, 6]), (1, [3, 4]), (2, [2, 5])], 'dot': [(7, [3, 4])]}
    for row, bits in patterns[kind]:
        for b in bits:
            g[row] &= ~(1 << b)
    return g


def make_glyph(orig, ch):
    base, marks = diacritics(ch)
    code = LO.get(base, UP.get(base))
    s = tile_off(code)
    g = bytearray(orig[s:s + 16])
    if 'bar' in marks:
        for row in (3, 4):
            for bit in (2, 3, 4, 5):
                g[row] &= ~(1 << bit)
        marks = marks - {'bar'}
    for k in ('circumflex', 'breve', 'horn'):
        if k in marks:
            g = accent(g, k)
    for k in ('acute', 'grave', 'hook', 'tilde', 'dot'):
        if k in marks:
            g = accent(g, k)
    return g


def apply_font(data, orig):
    payload = bytearray(); manifest = {}
    for ch, code in sorted(CUSTOM.items(), key=lambda kv: kv[1]):
        g = make_glyph(orig, ch)
        s = tile_off(code); data[s:s + 16] = g; payload.extend(g)
        manifest[ch] = {'code': f'{code:02X}', 'chr_tile': f'{0x40 + code:02X}', 'glyph': g.hex()}
    (OUT / 'vietnamese_glyphs_8x8_fixed.chr').write_bytes(payload)
    return manifest


# ---- text ---------------------------------------------------------------------------------
def parse_entries():
    out = []
    for line in (REF / 'ninjagaideniithedarkswordofchaosnesAlt2.ext').read_text(encoding='utf-8').splitlines():
        m = re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
        if m:
            out.append((int(m.group(1), 16), int(m.group(3)), int(m.group(4)), m.group(2)))
    return out


def apply_text(data):
    entries = [e for e in parse_entries() if e[0] < CREDITS[0]]
    if len(entries) != len(T):
        raise ValueError((len(entries), len(T)))
    report = []
    for addr, src_len, cap, src in entries:
        key = f'{addr:08X}'; txt = TEXT[key]; enc = encode(txt)
        if not enc or enc[-1] != 0xA6:
            raise ValueError(f'{key}: missing A6')
        if len(enc) > cap:
            raise ValueError(f'{key}: {len(enc)}>{cap}')
        data[addr:addr + cap] = enc[:-1] + bytes([0x3F]) * (cap - len(enc)) + bytes([0xA6])
        report.append({'addr': key, 'capacity': cap, 'used': len(enc), 'text': txt})
    return report


def make_tbl():
    base = (REF / 'ninjagaideniithedarkswordofchaosnesAlt2.tbl').read_text(encoding='utf-8').splitlines()
    mine = set(CUSTOM.values())
    lines = [x for x in base if not re.match(r'^[0-9A-Fa-f]{2}=', x) or int(x[:2], 16) not in mine]
    lines += ['', '; Vietnamese precomposed glyphs. Printable codes are $00-$7F only; $80+ are engine controls.']
    for ch, code in sorted(CUSTOM.items(), key=lambda kv: kv[1]):
        lines.append(f'{code:02X}={ch}')
    (OUT / 'ninjagaideniithedarkswordofchaosnesAlt2_VI_FIXED.tbl').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def make_ext():
    src = REF / 'ninjagaideniithedarkswordofchaosnesAlt2.ext'
    cur = None; result = []
    for line in src.read_text(encoding='utf-8').splitlines():
        m = re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
        if m:
            cur = m.group(1); cap = int(m.group(4)); result.append(line); continue
        if cur is not None and (line.startswith('"') or line.startswith('~') or line.startswith('==')):
            result.append(TEXT[cur] + f'#{cap}' if cur in TEXT else line)
            cur = None; continue
        result.append(line)
    (OUT / 'vi_ninjagaideniithedarkswordofchaosnesAlt2_FIXED.ext').write_text('\n'.join(result) + '\n', encoding='utf-8')


# ---- SELECT cutscene playlist -------------------------------------------------------------
# Title loop at $D738:  LDA $13 / AND #$10 / BNE $D751     ($13 = new button presses)
# Title exit  $D751:    LDA #0 / STA $48 / JSR $974A / INC $CB / JMP $C820  (cutscene #$CB)
#
# 1. AND #$10 -> AND #$30 so SELECT also leaves the title loop (1 byte changed).
# 2. LDA #0 / STA $48 (4 bytes) -> JSR hookA / NOP.  hookA (fixed bank, $FFE3) either does the
#    original two instructions and returns (START) or, for SELECT, drops its return address,
#    maps PRG bank 5 at $A000 and jumps to the driver.
# 3. The driver ($BBAE, free space of PRG bank 5, the cutscene engine bank) plays seeds
#    1..$0E itself, then runs the normal start path for seed $0F, which continues into
#    the game.  Its only state lives on the stack (cutscene init wipes zero page $D8-$EF),
#    and no original instruction is split.
HOOK_A = 0xFFE3
DRIVER = 0xBBAE


def fo(cpu):            # fixed bank ($C000-$FFFF) CPU address -> file offset
    return 0x10 + 0x1C000 + (cpu - 0xC000)


def b5(cpu):            # PRG bank 5 mapped at $A000 -> file offset
    return 0x10 + 0xA000 + (cpu - 0xA000)


def asm_hook_a():
    return bytes.fromhex(
        'A5 13 29 20 F0 0A'      # LDA $13 / AND #$20 / BEQ normal
        '68 68'                  # PLA PLA            (never returns)
        'A9 05 20 11 C0'         # LDA #5 / JSR $C011 (PRG bank 5 -> $A000)
        '4C AE BB'               # JMP driver
        'A9 00 85 48 60')        # normal: LDA #0 / STA $48 / RTS


def asm_driver():
    c = bytearray()
    c += bytes.fromhex('A9 01')                     # LDA #1            first seed
    loop = len(c)
    c += bytes.fromhex('48')                        # PHA               seed lives on the stack
    c += bytes.fromhex('A9 00 85 48 20 4A 97')      # title-exit prelude: LDA #0/STA $48/JSR $974A
    c += bytes.fromhex('68 48 85 CB')               # PLA/PHA/STA $CB
    c += bytes.fromhex('A9 00 85 1F 8D 00 E0')      # as $C820
    c += bytes.fromhex('A9 80 85 2E')
    c += bytes.fromhex('A9 05 20 11 C0')
    c += bytes.fromhex('A5 CB 20 00 A0')            # LDA $CB / JSR $A000   (cutscene)
    c += bytes.fromhex('A9 04 20 00 C0')            # restore $8000 bank like the original code
    c += bytes.fromhex('68 18 69 01 C9 0F')         # PLA / CLC / ADC #1 / CMP #$0F
    c += bytes([0x90, (loop - (len(c) + 2)) & 0xFF])  # BCC loop
    c += bytes.fromhex('A9 00 85 48 20 4A 97')      # prelude for the last seed
    c += bytes.fromhex('A9 0F 85 CB 4C 20 C8')      # seed $0F through the normal path
    return bytes(c)


def playlist_patch(data):
    assert data[fo(0xD738):fo(0xD738) + 6] == bytes.fromhex('A5 13 29 10 D0 13')
    assert data[fo(0xD751):fo(0xD751) + 4] == bytes.fromhex('A9 00 85 48')
    assert all(x == 0xFF for x in data[fo(HOOK_A):fo(0xFFFA)])
    assert all(x == 0xFF for x in data[b5(DRIVER):b5(DRIVER) + 0x80])
    data[fo(0xD73B)] = 0x30
    data[fo(0xD751):fo(0xD751) + 4] = b'\x20' + HOOK_A.to_bytes(2, 'little') + b'\xEA'
    h = asm_hook_a(); d = asm_driver()
    assert len(h) <= 0xFFFA - HOOK_A
    data[fo(HOOK_A):fo(HOOK_A) + len(h)] = h
    data[b5(DRIVER):b5(DRIVER) + len(d)] = d
    return {'title_loop': '$D73B AND #$10 -> #$30', 'title_exit': '$D751 -> JSR $FFE3',
            'hook_a': f'$FFE3 ({len(h)} bytes, fixed bank free area)',
            'driver': f'$BBAE in PRG bank 5 ({len(d)} bytes)', 'seeds': '01..0F'}


def ips(old, new):
    out = bytearray(b'PATCH'); i = 0
    while i < len(old):
        if old[i] == new[i]:
            i += 1; continue
        s = i; i += 1
        while i < len(old) and old[i] != new[i] and i - s < 0xFF00:
            i += 1
        if s == 0x454F46:  # would collide with the 'EOF' marker
            s -= 1
        out += s.to_bytes(3, 'big') + (i - s).to_bytes(2, 'big') + new[s:i]
    return bytes(out + b'EOF')


def main():
    orig = BASE.read_bytes()
    if hashlib.sha1(orig).hexdigest() != EXPECTED_SHA1:
        raise SystemExit('base mismatch')
    data = bytearray(orig)
    report = apply_text(data)
    font = apply_font(data, orig)
    text_rom = bytes(data)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Text_FIXED.nes').write_bytes(text_rom)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Text_FIXED.ips').write_bytes(ips(orig, text_rom))
    make_tbl(); make_ext()
    pl = playlist_patch(data)
    play_rom = bytes(data)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.nes').write_bytes(play_rom)
    pips = ips(orig, play_rom)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.ips').write_bytes(pips)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Cumulative_FIXED.ips').write_bytes(pips)
    (OUT / 'Ninja_Gaiden_II_Vietnamese_Playlist_ONLY_FIXED.ips').write_bytes(ips(text_rom, play_rom))
    meta = {'base_sha1': hashlib.sha1(orig).hexdigest(), 'base_crc32': f'{zlib.crc32(orig) & 0xffffffff:08X}',
            'text_sha1': hashlib.sha1(text_rom).hexdigest(), 'text_crc32': f'{zlib.crc32(text_rom) & 0xffffffff:08X}',
            'playlist_sha1': hashlib.sha1(play_rom).hexdigest(), 'playlist_crc32': f'{zlib.crc32(play_rom) & 0xffffffff:08X}',
            'rom_size': len(play_rom), 'story_blocks': len(report), 'custom_glyph_count': len(CUSTOM),
            'dropped_to_base_letter': DROPPED, 'custom_glyphs': font, 'playlist': pl}
    (OUT / 'build_manifest_fixed.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'translation_vietnamese_FIXED.txt').write_text(
        '# Ninja Gaiden II — Vietnamese fixed-width translation\n'
        '# Characters Í Ý Ơ Ư ỹ ẹ ễ ụ õ have no free glyph cell and print as I Y O U y e e u o.\n\n'
        + '\n'.join(f'@{r["addr"]} {r["text"]}' for r in report) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in meta.items() if k != 'custom_glyphs'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
