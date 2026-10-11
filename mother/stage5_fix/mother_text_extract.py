
#!/usr/bin/env python3
"""
mother_text_extract.py  -  Text extractor for MOTHER (NES, English prototype "EARTH BOUND 1.00")
ROM: mother.nes  CRC32 ABBE02FA  (NES 2.0, mapper 4 / MMC3, PRG 256 KB + CHR 256 KB)

Stage 1 of the Vietnamese translation project: dump every piece of game text into
machine-readable (JSON), translator-friendly (CSV / TXT) and table (TBL) formats,
with enough metadata (offsets, pointers, entry points, length limits) for the
later re-insertion stage.

Usage:
    python mother_text_extract.py --rom mother.nes --out outdir
    python mother_text_extract.py --hexdump mother_hexdump.txt --out outdir

The module also exposes  decode(bytes)->str  and  encode(str)->bytes  (round-trip safe)
for use by the re-inserter.
"""
import argparse, csv, json, os, re, sys, zlib, hashlib
from collections import defaultdict, Counter

# --------------------------------------------------------------------------------------
# ROM loading
# --------------------------------------------------------------------------------------
EXPECTED_CRC = 0xABBE02FA

def rom_from_hexdump(path):
    data = bytearray()
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^([0-9A-Fa-f]{8}):\s+((?:[0-9A-Fa-f]{2}\s){1,16})', line)
        if not m:
            continue
        off = int(m.group(1), 16)
        if off != len(data):
            raise ValueError('hexdump discontinuity at %08X' % off)
        data += bytes(int(x, 16) for x in m.group(2).split())
    return bytes(data)

# --------------------------------------------------------------------------------------
# Character table (verified against the font page at CHR $1F800, tiles $80-$FF)
# --------------------------------------------------------------------------------------
CHARS = {
    0xA0: ' ', 0xA1: '!', 0xA2: '?', 0xA3: '‥', 0xA4: '$', 0xA5: '•', 0xA6: '"', 0xA7: "'",
    0xA8: '(', 0xA9: ')', 0xAA: ':', 0xAB: ';', 0xAC: ',', 0xAD: '-', 0xAE: '.', 0xAF: '/',
    0xBB: 'α', 0xBC: 'β', 0xBD: 'γ', 0xBE: 'π', 0xBF: 'Ω', 0xC0: '◆',
    0xDB: '┏', 0xDC: '▔', 0xDD: '┓', 0xDE: '⎸', 0xDF: '⎹', 0xE0: '➡',
    0xFB: '┗', 0xFC: '▁', 0xFD: '┛', 0xFE: '▬', 0xFF: '▶',
    0x94: '○', 0x95: '◉', 0x96: '♪',
}
for i in range(10):
    CHARS[0xB0 + i] = str(i)
for i in range(26):
    CHARS[0xC1 + i] = chr(ord('A') + i)
    CHARS[0xE1 + i] = chr(ord('a') + i)
REV = {v: k for k, v in CHARS.items()}

# Control codes. Byte classification comes from the ROM table at $C22C (bank $1E):
# a byte < $40 whose class value is < $0A is a control code; everything else prints a tile.
CTRL_ARGS = {0x00: 0, 0x01: 0, 0x02: 0, 0x03: 0, 0x04: 2, 0x05: 0,
             0x20: 2, 0x21: 2, 0x22: 2, 0x23: 4}
CTRL_INFO = {
    0x00: ('{end}',  'End of message (implicit at the end of each segment)'),
    0x01: ('\\n',    'New line (dialogue lines are double-spaced)'),
    0x02: ('{clear}', 'Message break / clear (mostly battle text: after {wait})'),
    0x03: ('{wait}', 'Wait for button (blinking prompt), then continue on a new page'),
    0x04: ('{goto:XXXX}', 'Jump: continue reading at CPU address XXXX'),
    0x05: ('{05}',   'No-op / continue (handler at $C9D2 does nothing)'),
    0x20: ('{pos:XX,YY}', 'Set print position (column XX, row YY) - window layouts'),
    0x21: ('{str:XXXX}', 'Insert the string stored at CPU address XXXX (names etc.)'),
    0x22: ('{rep:CC,NN}', 'Print tile CC repeated NN times (window borders / padding)'),
    0x23: ('{num:XXXX,NN,FF}', 'Print the NN-byte number at address XXXX (format flags FF)'),
}
# Friendly aliases for {str:XXXX} (inferred from context; see report)
STR_ALIAS = {
    0x7478: 'Ninten', 0x74B8: 'Ana', 0x74F8: 'Lloyd', 0x7538: 'Teddy',
    0x7689: 'FavFood', 0x0580: 'Actor', 0x0588: 'Target', 0x0590: 'BattleItem',
    0x670A: 'Leader', 0x6D00: 'Patient', 0x6D04: 'ShopItem', 0x6D20: 'User',
    0x6D24: 'UsedItem', 0x7420: 'Str7420',
}
ALIAS_REV = {v: k for k, v in STR_ALIAS.items()}

class Codec:
    def __init__(self, cls_table):
        self.cls = cls_table  # 64 bytes from $C22C

    def is_ctrl(self, b):
        return b < 0x40 and self.cls[b] < 0x0A

    def tokens(self, buf, start, stop_at_end=True, hard_end=None):
        """Yield (offset, kind, byte, args). Stops after a 00 if stop_at_end."""
        i = start
        n = len(buf) if hard_end is None else hard_end
        while i < n:
            b = buf[i]
            if self.is_ctrl(b):
                na = CTRL_ARGS.get(b, 0)
                yield i, 'c', b, bytes(buf[i + 1:i + 1 + na])
                i += 1 + na
                if b == 0 and stop_at_end:
                    return
            else:
                yield i, 't', b, b''
                i += 1

    def decode(self, data, show_end=False):
        out = []
        for _, kind, b, args in self.tokens(data, 0, stop_at_end=False):
            if kind == 't':
                out.append(CHARS.get(b, '{%02X}' % b))
                continue
            if b == 0x00:
                out.append('{end}' if show_end else '')
            elif b == 0x01:
                out.append('\n')
            elif b == 0x02:
                out.append('{clear}')
            elif b == 0x03:
                out.append('{wait}')
            elif b == 0x05:
                out.append('{05}')
            elif b == 0x04:
                out.append('{goto:%04X}' % (args[0] | args[1] << 8))
            elif b == 0x20:
                out.append('{pos:%02X,%02X}' % (args[0], args[1]))
            elif b == 0x21:
                a = args[0] | args[1] << 8
                out.append('{%s}' % STR_ALIAS[a] if a in STR_ALIAS else '{str:%04X}' % a)
            elif b == 0x22:
                out.append('{rep:%02X,%02X}' % (args[0], args[1]))
            elif b == 0x23:
                out.append('{num:%04X,%02X,%02X}' % (args[0] | args[1] << 8, args[2], args[3]))
        return ''.join(out)

    @staticmethod
    def encode(text, terminate=True):
        """Inverse of decode(). Raises ValueError on characters not in the table."""
        out = bytearray()
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '\n':
                out.append(0x01); i += 1; continue
            if ch == '{':
                j = text.index('}', i)
                tag = text[i + 1:j]; i = j + 1
                if re.fullmatch(r'[0-9A-Fa-f]{2}', tag):
                    out.append(int(tag, 16))
                elif tag == 'end':
                    out.append(0x00)
                elif tag == 'clear':
                    out.append(0x02)
                elif tag == 'wait':
                    out.append(0x03)
                elif tag.startswith('goto:'):
                    a = int(tag[5:], 16); out += bytes([0x04, a & 0xFF, a >> 8])
                elif tag.startswith('pos:'):
                    x, y = tag[4:].split(','); out += bytes([0x20, int(x, 16), int(y, 16)])
                elif tag.startswith('str:'):
                    a = int(tag[4:], 16); out += bytes([0x21, a & 0xFF, a >> 8])
                elif tag in ALIAS_REV:
                    a = ALIAS_REV[tag]; out += bytes([0x21, a & 0xFF, a >> 8])
                elif tag.startswith('rep:'):
                    c, n = tag[4:].split(','); out += bytes([0x22, int(c, 16), int(n, 16)])
                elif tag.startswith('num:'):
                    a, n, f = tag[4:].split(',')
                    a = int(a, 16); out += bytes([0x23, a & 0xFF, a >> 8, int(n, 16), int(f, 16)])
                else:
                    raise ValueError('unknown tag {%s}' % tag)
                continue
            if ch not in REV:
                raise ValueError('character %r (U+%04X) is not in the table' % (ch, ord(ch)))
            out.append(REV[ch]); i += 1
        if terminate:
            out.append(0x00)
        return bytes(out)

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def category_for(ids, text):
    """Script category from the message-ID range (ranges verified by inspection)."""
    if not text.strip():
        return 'empty'
    i = min(x for x in ids if x != 0) if any(ids) else 0
    if i == 0:
        return 'placeholder'
    for lo, hi, name in ((1, 999, 'dialogue'), (1000, 1299, 'item_description'),
                         (1300, 1499, 'enemy_check'), (1500, 1649, 'battle_message'),
                         (1650, 1699, 'final_boss_speech'), (1700, 1779, 'field_system'),
                         (1780, 1780, 'anti_piracy'), (1781, 1799, 'ending'),
                         (1800, 1999, 'staff_credits')):
        if lo <= i <= hi:
            return name
    return 'other'

def line_widths(text):
    """Visible character count per line (tags count as 0 except names, which vary)."""
    res = []
    for page in text.split('{wait}'):
        for ln in page.split('\n'):
            vis = re.sub(r'\{[^}]*\}', '', ln)
            res.append(len(vis))
    return res

def prg_cpu(bank, off_in_bank, base=0x8000):
    return base + off_in_bank

# --------------------------------------------------------------------------------------
# Main extraction
# --------------------------------------------------------------------------------------
def extract(rom, outdir):
    os.makedirs(outdir, exist_ok=True)
    crc = zlib.crc32(rom) & 0xFFFFFFFF
    hdr = rom[:16]
    prg_size = 0x40000; chr_size = 0x40000
    P = rom[16:16 + prg_size]
    C = rom[16 + prg_size:16 + prg_size + chr_size]
    CHR_FILE = 16 + prg_size
    codec = Codec(P[0x3C000 + 0x22C:0x3C000 + 0x22C + 64])

    # ---------------- 1. Main script (CHR-ROM) ----------------
    TBL_BANK = 0x18; TBL_PRG = TBL_BANK * 0x2000; N_IDS = 2000
    TEXT_BASE = 0x20000                         # CHR offset of pointer value 0
    ptrs = []
    for i in range(N_IDS):
        o = TBL_PRG + 3 * i
        ptrs.append(P[o] | P[o + 1] << 8 | P[o + 2] << 16)

    ids_by_ptr = defaultdict(list)
    for i, v in enumerate(ptrs):
        ids_by_ptr[v].append(i)
    starts = sorted(ids_by_ptr)

    # block end for every start = offset just after its terminating 00
    def end_of(chr_off):
        last = None
        for off, kind, b, args in codec.tokens(C, chr_off):
            last = (off, kind, b, args)
        off, kind, b, args = last
        return off + 1 + len(args)

    seg_list = []
    abs_starts = [TEXT_BASE + v for v in starts]
    for k, a in enumerate(abs_starts):
        blk_end = end_of(a)
        nxt = abs_starts[k + 1] if k + 1 < len(abs_starts) else None
        if nxt is not None and nxt < blk_end:
            # verify the next entry point is on a token boundary
            bounds = {off for off, *_ in codec.tokens(C, a)}
            if nxt not in bounds:
                raise RuntimeError('entry point %05X not on token boundary' % nxt)
            seg_end = nxt; falls = True
        else:
            seg_end = blk_end; falls = False
        raw = C[a:seg_end]
        seg_list.append({'start': a, 'end': seg_end, 'falls_through': falls, 'raw': raw})

    segments = []
    for k, s in enumerate(seg_list):
        v = s['start'] - TEXT_BASE
        raw = s['raw']
        body = raw[:-1] if (not s['falls_through'] and raw and raw[-1] == 0) else raw
        text = codec.decode(body)
        # round-trip self test
        enc = Codec.encode(text, terminate=not s['falls_through'])
        if enc != raw:
            raise RuntimeError('round-trip failed for segment at CHR %05X' % s['start'])
        ids = ids_by_ptr[v]
        unused = (v == 0 and len(ids) > 1)
        lw = line_widths(text)
        segments.append({
            'seg': 'S%04d' % k,
            'ids': ids,
            'category': 'placeholder' if unused else category_for(ids, text),
            'chr_offset': '%05X' % s['start'],
            'file_offset': '%06X' % (CHR_FILE + s['start']),
            'pointer_value': '%05X' % v,
            'chr_bank_8k': '%02X' % (s['start'] // 0x2000),
            'length': len(raw),
            'falls_through_to_next': s['falls_through'],
            'pages': text.count('{wait}') + 1,
            'max_line_chars': max(lw) if lw else 0,
            'text': text,
            'raw_hex': raw.hex().upper(),
            'note': ('IDs pointing at offset 0 = unused/placeholder ("System Error!!!")' if unused else ''),
        })
    # free space inside the CHR text area
    covered = sorted((s['start'], s['end']) for s in seg_list)
    free = []; prev = TEXT_BASE
    for a, e in covered:
        if a > prev:
            free.append((prev, a))
        prev = max(prev, e)
    TEXT_AREA_END = 0x34020
    if prev < TEXT_AREA_END:
        free.append((prev, TEXT_AREA_END))

    # ---------------- 2. PRG strings ----------------
    prg_strings = []

    def add_prg(cat, off, raw, refs=None, maxlen=None, policy='relocatable', index=None, note=''):
        text = codec.decode(raw)
        enc = Codec.encode(text, terminate=False)
        if enc != raw:
            raise RuntimeError('PRG round-trip failed at %05X' % off)
        prg_strings.append({
            'key': 'P%05X' % off, 'category': cat, 'index': index,
            'prg_offset': '%05X' % off, 'file_offset': '%06X' % (off + 16),
            'bank': '%02X' % (off // 0x2000),
            'length': len(raw), 'max_length': maxlen if maxlen is not None else len(raw),
            'policy': policy, 'pointer_refs': refs or [], 'text': text,
            'raw_hex': raw.hex().upper(), 'note': note})

    def cstr(off):
        e = P.index(0, off)
        return P[off:e]

    # 2a. Master name table: bank $00, CPU $9800, 256 x 8-byte records, name ptr at +0 ($8000 window)
    seen = {}
    for n in range(256):
        ro = 0x1800 + 8 * n
        w = P[ro] | P[ro + 1] << 8
        if not (0x8001 <= w < 0x89DC):
            continue
        so = w - 0x8000
        if P[so - 1] != 0:
            continue
        seen.setdefault(so, []).append((n, ro))
    for so in sorted(seen):
        raw = cstr(so)
        if not raw:
            continue
        cat = 'item_name' if so < 0x03D3 else ('place_name' if so < 0x041E else 'psi_name')
        refs = ['bank00 $%04X (entry %02X)' % (0x8000 + ro, n) for n, ro in seen[so]]
        add_prg(cat, so, raw, refs, index=[n for n, _ in seen[so]])

    # 2b. Status-ailment names: fixed 7-byte slots (6 chars + 00) at bank $00 +$05F8
    for i in range(8):
        so = 0x05F8 + 7 * i
        add_prg('status_name', so, P[so:so + 6], maxlen=6, policy='in_place_fixed_6',
                index=i, note='Accessed as base+7*n: exactly 6 visible chars, pad with spaces')

    # 2c. Enemy names: table in bank $16 ($8000 window), 32-byte records, name ptr at +$18
    enemy = defaultdict(list)
    for n in range(122):
        ro = 0x2C000 + n * 0x20 + 0x18
        w = P[ro] | P[ro + 1] << 8
        so = w - 0x8000
        if 0x0630 <= so < 0x09DC and P[so - 1] == 0:
            enemy[so].append((n, ro))
    for so in sorted(enemy):
        raw = cstr(so)
        if raw:
            add_prg('enemy_name', so, raw,
                    ['bank16 $%04X (enemy %02X)' % (0x8000 + (ro - 0x2C000), n) for n, ro in enemy[so]],
                    index=[n for n, _ in enemy[so]])

    # 2d. Default names of guest characters (bank $18 character records, name field +$38, 8 bytes)
    for ro, who in ((0x31F40, 'Pippi'), (0x31F80, 'EVE'), (0x31FC0, 'Flying Man')):
        raw = cstr(ro + 0x38)
        add_prg('character_name', ro + 0x38, raw, maxlen=7, policy='in_place_field_8',
                note='%s: 8-byte name field in the character record at PRG %05X' % (who, ro))

    # 2e. Window / menu layouts and other UI strings (edit in place; same byte length)
    def split_region(cat, a, b, note):
        o = a
        while o < b:
            if P[o] == 0:
                o += 1; continue
            e = o
            while e < b and P[e] != 0:
                e += 1 + (CTRL_ARGS.get(P[e], 0) if codec.is_ctrl(P[e]) else 0)
            raw = P[o:e]
            if any(0xC1 <= x <= 0xFA for x in raw):
                add_prg(cat, o, raw, policy='in_place', note=note)
            o = e + 1

    split_region('battle_ui', 0x0D40, 0x0E80, 'Battle windows / command menu (bank $00). 00 here separates window rows.')
    split_region('field_menu', 0x11E8, 0x16A4, 'Field menus: Command, Goods, State, Setup... (bank $00)')
    split_region('system_ui', 0x26DD0, 0x26DF0, 'Yes/No box (bank $13)')
    split_region('system_ui', 0x278E8, 0x278FA, 'Window title (bank $13)')
    split_region('system_ui', 0x279D0, 0x279E0, 'Window title (bank $13)')
    split_region('name_entry', 0x27AB0, 0x27AD7, 'Name-entry keyboard (bank $13) - layout grid')
    split_region('file_select', 0x33894, 0x339F8, 'File-select menus (bank $19)')
    split_region('naming', 0x33B02, 0x33BF7, 'Naming prompts / error message (bank $19)')
    split_region('reserved_names', 0x33BF8, 0x33C6F,
                 'Names the player may not use (bank $19). "?" ends a name; max 7 chars.')
    split_region('name_entry', 0x33C70, 0x33CB0, 'Name-entry keyboard rows (bank $19)')
    split_region('intro', 0x33CD0, 0x33EA0, 'Opening story text (bank $19)')

    # ---------------- 3. Write outputs ----------------
    meta = {
        'rom': {'crc32': '%08X' % crc, 'sha1': hashlib.sha1(rom).hexdigest(), 'size': len(rom),
                'header_hex': hdr.hex().upper(), 'mapper': 4, 'prg_kb': 256, 'chr_kb': 256},
        'script_system': {
            'pointer_table': 'PRG bank $18, CPU $8000 (file %06X), %d entries x 3 bytes, little-endian 17-bit'
                             % (16 + TBL_PRG, N_IDS),
            'pointer_to_offset': 'CHR offset = $20000 + value  (file offset = $40010 + CHR offset)',
            'reader': 'bank $1E $CAA9: ID*3 -> ptr; NMI cmd $0A at $F99F reads 64 bytes via PPU $2007 into $0110',
            'chr_text_area': 'CHR $20000-$3401F', 'segments': len(segments),
            'unique_pointers': len(starts),
            'ids_unused_pointing_to_0': len(ids_by_ptr[0]) - 1,
            'free_space': [{'chr_from': '%05X' % a, 'chr_to': '%05X' % b, 'bytes': b - a} for a, b in free],
            'free_total': sum(b - a for a, b in free),
        },
        'control_codes': {'%02X' % k: {'tag': v[0], 'args': CTRL_ARGS[k], 'meaning': v[1]}
                          for k, v in CTRL_INFO.items()},
        'string_aliases': {'%04X' % k: v for k, v in STR_ALIAS.items()},
        'charset': {'%02X' % k: v for k, v in sorted(CHARS.items())},
    }
    with open(os.path.join(outdir, 'mother_script.json'), 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'script_segments': segments, 'prg_strings': prg_strings},
                  f, ensure_ascii=False, indent=1)

    # Readable script
    with open(os.path.join(outdir, 'mother_script_en.txt'), 'w', encoding='utf-8') as f:
        f.write('MOTHER (NES, EARTH BOUND 1.00 prototype) - full text dump\n')
        f.write('ROM CRC32 %08X | %d script segments | %d PRG strings\n' % (crc, len(segments), len(prg_strings)))
        f.write('Tags: \\n = new line, {wait} = button prompt/new page, {clear} = battle message break,\n')
        f.write('      {Ninten} {Ana} {Lloyd} {Teddy} {FavFood} {Actor} {Target}... = inserted names,\n')
        f.write('      {num:addr,bytes,fmt} = number, {XX} = raw tile byte, ◆ = speech bullet.\n')
        f.write('=' * 78 + '\n\n### PART 1 - MAIN SCRIPT (CHR-ROM)\n\n')
        for s in segments:
            ids = s['ids']
            idtxt = ('IDs %s' % ','.join('%04d' % i for i in ids)) if len(ids) <= 6 else \
                    'IDs %04d..(%d ids)' % (ids[0], len(ids))
            f.write('[%s] %s  CHR %s  file %s  len %d%s\n' % (
                s['seg'], idtxt, s['chr_offset'], s['file_offset'], s['length'],
                '  ->falls through to next segment' if s['falls_through_to_next'] else ''))
            f.write(s['text'] + '\n' + '-' * 40 + '\n')
        f.write('\n### PART 2 - PRG-ROM STRINGS\n\n')
        for p in prg_strings:
            f.write('[%s] %-15s PRG %s (file %s) len %d max %d %s\n%s\n%s\n' % (
                p['key'], p['category'], p['prg_offset'], p['file_offset'], p['length'],
                p['max_length'], p['policy'], p['text'], '-' * 40))

    # Translation worksheet (UTF-8 with BOM so Excel shows Vietnamese correctly)
    with open(os.path.join(outdir, 'mother_translation_sheet.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['key', 'source', 'category', 'ids_or_index', 'offset', 'orig_bytes', 'limit_rule',
                    'max_line_chars', 'pages', 'english', 'vietnamese', 'notes'])
        for s in segments:
            cat = s['category']
            ids = s['ids']
            w.writerow([s['seg'], 'CHR', cat,
                        ' '.join(map(str, ids)) if len(ids) <= 20 else '%d..(%d ids)' % (ids[0], len(ids)),
                        s['chr_offset'], s['length'],
                        'relocatable (pointer table)' + ('; falls through into next segment' if s['falls_through_to_next'] else ''),
                        s['max_line_chars'], s['pages'], s['text'], '', s['note']])
        for p in prg_strings:
            w.writerow([p['key'], 'PRG', p['category'],
                        ' '.join(map(str, p['index'])) if isinstance(p['index'], list) else ('' if p['index'] is None else p['index']),
                        p['prg_offset'], p['length'], '%s (max %d bytes)' % (p['policy'], p['max_length']),
                        max(line_widths(p['text'])), 1, p['text'], '', p['note']])

    # Thingy-style table file
    with open(os.path.join(outdir, 'mother.tbl'), 'w', encoding='utf-8') as f:
        f.write('; MOTHER (NES) English prototype - text table (verified against font CHR $1F800)\n')
        f.write('; Control codes (args in bytes): 00 end, 01 newline, 02 clear, 03 wait, 04 goto(2),\n')
        f.write(';   05 nop, 20 pos(2), 21 insert-string(2), 22 repeat-tile(2), 23 number(4)\n')
        f.write('/00=<end>\n*01=<n>\n02=<clear>\n03=<wait>\n04=<goto>\n05=<05>\n20=<pos>\n21=<str>\n22=<rep>\n23=<num>\n')
        for k, v in sorted(CHARS.items()):
            f.write('%02X=%s\n' % (k, v))

    return meta, segments, prg_strings


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--rom'); g.add_argument('--hexdump')
    ap.add_argument('--out', default='mother_text_out')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read() if a.rom else rom_from_hexdump(a.hexdump)
    crc = zlib.crc32(rom) & 0xFFFFFFFF
    if crc != EXPECTED_CRC:
        print('WARNING: CRC32 %08X differs from expected %08X' % (crc, EXPECTED_CRC))
    meta, segs, prg = extract(rom, a.out)
    print('segments: %d  (ids: %d)  prg strings: %d  free CHR text space: %d bytes' % (
        len(segs), sum(len(s['ids']) for s in segs), len(prg), meta['script_system']['free_total']))

if __name__ == '__main__':
    main()
