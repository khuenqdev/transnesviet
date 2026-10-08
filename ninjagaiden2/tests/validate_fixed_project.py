#!/usr/bin/env python3
"""Static validation of the release ROMs/patches (run:  python3 tests/validate_fixed_project.py)."""
from pathlib import Path
import hashlib, importlib.util, sys

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / 'release'
spec = importlib.util.spec_from_file_location('b', ROOT / 'source' / 'build_vietnamese_fixed.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
sys.path.insert(0, str(ROOT / 'source'))
from apply_ips import apply as apply_ips_file

base = b.BASE.read_bytes()
text = (R / 'Ninja_Gaiden_II_Vietnamese_Text_FIXED.nes').read_bytes()
play = (R / 'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.nes').read_bytes()
assert len(base) == len(text) == len(play) == 262160
assert hashlib.sha1(base).hexdigest() == b.EXPECTED_SHA1

# 1. every glyph is a printable code ($00-$7F); controls untouched
for ch, code in b.CUSTOM.items():
    assert 0 <= code < 0x80, (ch, code)
    assert code not in b.PROTECTED, (ch, code)
for key, s in b.TEXT.items():
    enc = b.encode(s)
    assert enc[-1] == 0xA6, key
    body = b.strip_tokens(s)
    for ch in body:
        if ch in b.CUSTOM:
            assert b.CUSTOM[ch] < 0x80
# 2. credits text and the protected glyph tiles are byte-identical to the original
assert text[b.CREDITS[0]:b.CREDITS[1]] == base[b.CREDITS[0]:b.CREDITS[1]]
for c in b.PROTECTED:
    s = b.tile_off(c)
    assert text[s:s + 16] == base[s:s + 16], hex(c)
# 3. only CHR tiles $40+code of custom glyphs changed in CHR; PRG changes are text blocks only
chr0 = b.CHR0
changed_chr = {(i - chr0) // 16 for i in range(chr0, len(base)) if base[i] != text[i]}
assert changed_chr <= {0x40 + c for c in b.CUSTOM.values()}, 'unexpected CHR change'
# 4. playlist = text ROM + exactly three PRG areas
diff = [i for i in range(len(text)) if text[i] != play[i]]
areas = {'title AND': (0x1D74B, 0x1D74C), 'title exit': (0x1D761, 0x1D765),
         'hook': (0x1FFF3, 0x1FFF3 + len(b.asm_hook_a())),
         'driver': (b.b5(b.DRIVER), b.b5(b.DRIVER) + len(b.asm_driver()))}
for i in diff:
    assert any(lo <= i < hi for lo, hi in areas.values()), hex(i)
assert play[b.fo(0xD738):b.fo(0xD738) + 6] == bytes.fromhex('A5 13 29 30 D0 13')   # LDA/AND #$30/BNE intact
assert play[b.fo(0xD751):b.fo(0xD751) + 4] == bytes.fromhex('20 E3 FF EA')
assert play[b.fo(0xC832):b.fo(0xC832) + 3] == base[b.fo(0xC832):b.fo(0xC832) + 3]   # cutscene call untouched
# 5. IPS round trip
tmp = ROOT / 'release' / '.tmp_check.nes'
for ips, expect in (('Ninja_Gaiden_II_Vietnamese_Text_FIXED.ips', text),
                    ('Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.ips', play),
                    ('Ninja_Gaiden_II_Vietnamese_Cumulative_FIXED.ips', play)):
    apply_ips_file(b.BASE, R / ips, tmp); assert tmp.read_bytes() == expect, ips
apply_ips_file(R / 'Ninja_Gaiden_II_Vietnamese_Text_FIXED.nes', R / 'Ninja_Gaiden_II_Vietnamese_Playlist_ONLY_FIXED.ips', tmp)
assert tmp.read_bytes() == play; tmp.unlink()
print('PASS')
print('Text SHA1    ', hashlib.sha1(text).hexdigest())
print('Playlist SHA1', hashlib.sha1(play).hexdigest())
print('Glyph cells  ', len(b.CUSTOM), ' dropped:', ''.join(b.DROPPED))
