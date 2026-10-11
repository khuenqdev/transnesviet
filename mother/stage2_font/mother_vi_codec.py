#!/usr/bin/env python3
"""
mother_vi_codec.py - Stage 2: Vietnamese text <-> MOTHER byte encoding.

Extends the stage-1 codec (mother_text_extract.Codec): all tags ({wait}, {Ninten},
{num:...}, \\n ...) and the existing table are unchanged; Vietnamese letters are
encoded with mother_vi_font.encode_char (mark prefix byte $80-$8D + base glyph).

  encode(text, terminate=True) -> bytes        (raises on unknown characters)
  decode(data)                 -> str          (inverse; marks re-composed)
  check_lines(text, limit)     -> list of over-long lines (marks take no column)

Run as a script for the self-test.
"""
import re, sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mother_text_extract import Codec, CHARS, REV
from mother_vi_font import encode_char, decode_bytes, GLYPHS, MARK_RANGE, NEW

VI_CODES = {k for k, v in GLYPHS.items()}
_TAG = re.compile(r'(\{[^}]*\}|\n)')

def encode(text, terminate=True, warnings=None):
    out = bytearray()
    for part in _TAG.split(unicodedata.normalize('NFC', text)):
        if not part:
            continue
        if part == '\n' or part.startswith('{'):
            out += Codec.encode(part, terminate=False)
            continue
        for ch in part:
            if ch in REV and REV[ch] not in VI_CODES:
                out.append(REV[ch])
                continue
            b = encode_char(ch, warnings)
            if b is None:
                raise ValueError('character %r (U+%04X) cannot be encoded' % (ch, ord(ch)))
            out += b
    if terminate:
        out.append(0x00)
    return bytes(out)

def _byte_char(b):
    return CHARS.get(b, '{%02X}' % b)

def decode(data, codec=None):
    """Decode bytes produced by encode(). Uses the stage-1 tokenizer for control codes."""
    if codec is None:
        raise ValueError('pass a stage-1 Codec (needs the ROM control-code class table)')
    text = []; run = bytearray()
    def flush():
        if run:
            text.append(decode_bytes(bytes(run), _byte_char)); run.clear()
    for off, kind, b, args in codec.tokens(data, 0, stop_at_end=False):
        if kind == 't':
            run.append(b)
        else:
            flush()
            text.append(codec.decode(bytes([b]) + args))
    flush()
    return ''.join(text)

def visible_len(line):
    return len(re.sub(r'\{[^}]*\}', '', line))   # Vietnamese letters are 1 column each (NFC)

def check_lines(text, limit=22):
    bad = []
    for page in unicodedata.normalize('NFC', text).split('{wait}'):
        for ln in page.split('\n'):
            if visible_len(ln) > limit:
                bad.append((visible_len(ln), ln))
    return bad

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import json, zlib
    rom = open(sys.argv[1] if len(sys.argv) > 1 else 'mother.nes', 'rb').read()
    P = rom[16:16 + 0x40000]
    codec = Codec(P[0x3C000 + 0x22C:0x3C000 + 0x22C + 64])
    fails = 0
    # 1. every Vietnamese letter round-trips (capital dot-below fallbacks excepted)
    from mother_vi_font import all_vietnamese_letters, CAP_DOT_FALLBACK
    n_ok = 0
    for ch in all_vietnamese_letters():
        w = []
        b = encode(ch, terminate=False, warnings=w)
        back = decode(b, codec)
        expect = ch
        if w:
            expect = unicodedata.normalize('NFC', ch.lower())
        if back != expect:
            print('ROUND-TRIP FAIL', ch, b.hex(), back); fails += 1
        else:
            n_ok += 1
    print('letters round-trip: %d ok' % n_ok)
    # 2. backwards compatibility: every stage-1 string re-encodes to its original bytes
    J = json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'mother_script.json', encoding='utf-8'))
    n = 0
    for s in J['script_segments']:
        raw = bytes.fromhex(s['raw_hex'])
        if encode(s['text'], terminate=not s['falls_through_to_next']) != raw:
            print('COMPAT FAIL', s['seg']); fails += 1
        n += 1
    for p in J['prg_strings']:
        if encode(p['text'], terminate=False) != bytes.fromhex(p['raw_hex']):
            print('COMPAT FAIL', p['key']); fails += 1
        n += 1
    print('stage-1 strings re-encoded identically: %d' % (n - fails))
    # 3. sample sentence
    s = '◆{Ninten} ơi, đừng sợ!\n Mẹ ở đây rồi.{wait}◆Ừ, Ộ, Ặc... Ổn chứ?\n'
    b = encode(s)
    print('sample:', b.hex().upper())
    print('decoded:', repr(decode(b[:-1], codec)))
    assert decode(b[:-1], codec) == s
    print('ALL TESTS PASSED' if not fails else '%d FAILURES' % fails)
    sys.exit(1 if fails else 0)
