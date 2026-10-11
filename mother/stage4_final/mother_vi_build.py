#!/usr/bin/env python3
"""
mother_vi_build.py - Stage 4 (final): build the Vietnamese MOTHER ROM.

  python mother_vi_build.py --rom mother.nes --script mother_script.json --tr translations --out out

Pipeline
  1. stage 2+3   : Vietnamese font + mark-row renderer           (mother_vi_renderer.build)
  2. expansion   : PRG 256 -> 512 KB, script reader moved to PRG (mother_vi_expand)
  3. script      : every translated segment is laid out (mother_vi_wrap), encoded
                   (mother_vi_codec) and packed into PRG banks $20-$3D; untranslated segments
                   keep their original bytes.
  4. names       : item / place / PSI / enemy names re-packed in bank $00 with all pointer tables
                   (bank $00 $9800 master table, bank $16 enemy table) rewritten; status names
                   written into their fixed 7-byte slots; guest-character name fields.
  5. UI strings  : window layouts edited in place (same byte length; see tr/vn_ui.py).
  6. outputs     : ROM, IPS (against the original ROM), build report (JSON) with every check.
"""
import argparse, glob, importlib.util, json, os, re, struct, sys, unicodedata, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mother_vi_renderer
from mother_vi_expand import expand, insert_script
from mother_vi_wrap import layout, word_cost
from mother_vi_codec import encode, check_lines
from mother_vi_font import MARK_RANGE

NAME_POOLS = [(0x0001, 0x05F8), (0x0630, 0x0A40), (0x0A50, 0x0B40)]   # bank $00 offsets
STATUS_BASE = 0x05F8
WIDTHS = {'battle_message': 21, 'enemy_check': 22, 'final_boss_speech': 21}

def load_translations(folder):
    T = {}
    for f in sorted(glob.glob(os.path.join(folder, 'vn_*.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for k, v in getattr(m, 'T', {}).items():
            if k in T:
                raise ValueError('duplicate key %s in %s' % (k, f))
            T[k] = v
    return T

def ui_cols(b):
    """Columns printed by a window string: tiles 1, {rep} n, marks/controls 0."""
    cols = 0; i = 0
    while i < len(b):
        x = b[i]
        if x in (0x22,) and i + 2 < len(b):
            cols += b[i + 2]; i += 3; continue
        if x in (0x20, 0x21, 0x04):
            i += 3; continue
        if x == 0x23:
            i += 5; continue
        if MARK_RANGE[0] <= x <= MARK_RANGE[1] or x in (0x00, 0x01, 0x02, 0x03, 0x05):
            i += 1; continue
        cols += 1; i += 1
    return cols

def count_marks(b):
    return sum(1 for x in b if MARK_RANGE[0] <= x <= MARK_RANGE[1])

def lay(vn, seg):
    """Translation -> game text (tag format)."""
    if vn.startswith('RAW:'):
        return unicodedata.normalize('NFC', vn[4:])
    en = seg['text']
    if vn.startswith('"') and '\n◆' in vn:          # item description: "Name"\n◆text
        head, body = vn.split('\n', 1)
        return unicodedata.normalize('NFC', head) + '\n' + layout(body, '◆' + en.split('◆', 1)[1])
    return layout(vn, en, WIDTHS.get(seg['category']))

def check_text(text, limit):
    probs = []
    for page in text.split('{wait}'):
        for ln in page.split('\n'):
            cols = sum(word_cost(w)[0] for w in re.split(r'(\s)', ln) if w) if ln else 0
            marks = count_marks(encode(re.sub(r'\{[^}]*\}', '', ln), terminate=False))
            if cols > limit or marks > 10:
                probs.append('%d cols/%d marks: %s' % (cols, marks, ln))
    return probs

def build(rom_path, script_path, tr_folder, outdir):
    os.makedirs(outdir, exist_ok=True)
    orig = open(rom_path, 'rb').read()
    J = json.load(open(script_path, encoding='utf-8'))
    T = load_translations(tr_folder)
    report = {'warnings': [], 'untranslated': [], 'errors': []}

    rom, _ = mother_vi_renderer.build(orig)                 # font + renderer (stage 2/3)
    rom = bytearray(expand(rom))                             # PRG 512 KB + PRG text reader

    # ---------------- script ----------------
    segs = []; n_tr = 0
    for s in J['script_segments']:
        raw = bytes.fromhex(s['raw_hex'])
        k = s['seg']
        if k in T:
            try:
                text = lay(T[k], s)
                limit = 28 if s['category'] in ('ending', 'anti_piracy') else (
                        WIDTHS.get(s['category'], 22))
                for p in check_text(text, limit):
                    report['warnings'].append('%s: %s' % (k, p))
                data = encode(text, terminate=not s['falls_through_to_next'])
                n_tr += 1
            except Exception as e:
                report['errors'].append('%s: %s' % (k, e)); data = raw
        else:
            data = raw
            if s['category'] not in ('empty', 'placeholder', 'staff_credits'):
                report['untranslated'].append(k)
        segs.append({'ids': s['ids'], 'data': data, 'falls_through': s['falls_through_to_next']})
    rom, pk = insert_script(rom, segs)
    report['script'] = {'segments_translated': n_tr, 'bytes': pk.used(),
                        'banks_used': '%02X-%02X' % (0x20, pk.bank)}

    # ---------------- names (bank $00) ----------------
    P0 = 16
    by_off = {}
    for p in J['prg_strings']:
        by_off.setdefault(p['prg_offset'], p)
    names = [p for p in J['prg_strings'] if p['category'] in ('item_name', 'place_name', 'psi_name', 'enemy_name')
             and int(p['prg_offset'], 16) != STATUS_BASE]
    # gather pointer locations: master table + enemy table
    refs = {}
    for n in range(256):
        ro = 0x1800 + 8 * n
        w = rom[P0 + ro] | rom[P0 + ro + 1] << 8
        refs.setdefault(w - 0x8000, []).append(ro)
    for n in range(122):
        ro = 0x2C000 + n * 0x20 + 0x18
        w = rom[P0 + ro] | rom[P0 + ro + 1] << 8
        refs.setdefault(w - 0x8000, []).append(ro)
    blobs = []
    for p in names:
        off = int(p['prg_offset'], 16); k = p['key']
        txt = T.get(k, p['text'])
        b = encode(txt, terminate=False)
        cols = len(unicodedata.normalize('NFC', txt))
        if cols > 11:
            report['errors'].append('%s: name "%s" is %d columns (max 11)' % (k, txt, cols)); b = bytes.fromhex(p['raw_hex'])
        if k not in T:
            report['untranslated'].append(k)
        blobs.append((off, b + b'\x00'))
    # clear pools, then pack
    for a, e in NAME_POOLS:
        for i in range(a, e):
            if not (STATUS_BASE <= i < STATUS_BASE + 0x38):
                rom[P0 + i] = 0
    pool_i = 0; pos = NAME_POOLS[0][0]; newaddr = {}
    for off, b in blobs:
        while pos + len(b) > NAME_POOLS[pool_i][1]:
            pool_i += 1
            if pool_i >= len(NAME_POOLS):
                raise RuntimeError('bank $00 name space exhausted')
            pos = NAME_POOLS[pool_i][0]
        rom[P0 + pos:P0 + pos + len(b)] = b
        newaddr[off] = pos; pos += len(b)
    for off, new in newaddr.items():
        for ro in refs.get(off, []):
            w = 0x8000 + new
            rom[P0 + ro] = w & 0xFF; rom[P0 + ro + 1] = w >> 8
    report['names'] = {'count': len(blobs), 'bytes': sum(len(b) for _, b in blobs),
                       'pool_bytes': sum(e - a for a, e in NAME_POOLS)}
    # status names: fixed 6-byte slots
    for i in range(8):
        off = STATUS_BASE + 7 * i; k = 'P%05X' % off
        if k in T:
            b = encode(T[k], terminate=False)
            if len(b) > 6:
                report['errors'].append('%s: status name too long' % k); continue
            rom[P0 + off:P0 + off + 6] = b + b'\xA0' * (6 - len(b))
    # guest character names: 8-byte field
    for k in ('P31F78', 'P31FB8', 'P31FF8'):
        if k in T:
            off = int(k[1:], 16); b = encode(T[k], terminate=False)
            if len(b) > 7:
                report['errors'].append('%s: character name too long (%d bytes)' % (k, len(b))); continue
            rom[P0 + off:P0 + off + 8] = b + b'\x00' * (8 - len(b))

    # ---------------- UI strings in place ----------------
    ui = T.get('__UI__', {}) if isinstance(T.get('__UI__'), dict) else {}
    for k, txt in ui.items():
        if k.startswith('X'):                         # raw region not split by stage 1
            off = int(k[1:], 16); old = encode(txt[0], terminate=False); new = encode(txt[1], terminate=False)
            if bytes(rom[P0 + off:P0 + off + len(old)]) != old or len(new) != len(old) or ui_cols(new) != ui_cols(old):
                report['errors'].append('UI %s: mismatch' % k); continue
            rom[P0 + off:P0 + off + len(old)] = new; continue
        p = by_off.get(k[1:])
        if not p:
            report['errors'].append('UI %s unknown' % k); continue
        old = bytes.fromhex(p['raw_hex']); new = encode(txt, terminate=False)
        if p['category'] == 'naming' and len(new) <= len(old):      # free text: pad with spaces
            new = new + b'\xA0' * (len(old) - len(new))
            off = int(k[1:], 16); rom[P0 + off:P0 + off + len(old)] = new; continue
        if len(new) != len(old) or ui_cols(new) != ui_cols(old):
            report['errors'].append('UI %s: %d bytes/%d cols, must be %d/%d' % (
                k, len(new), ui_cols(new), len(old), ui_cols(old))); continue
        off = int(k[1:], 16)
        rom[P0 + off:P0 + off + len(old)] = new
    # ---------------- opening story (PRG bank $19 + its CHR copy) ----------------
    intro_py = os.path.join(tr_folder, 'vn_intro.py')
    if os.path.exists(intro_py):
        spec = importlib.util.spec_from_file_location('vn_intro', intro_py)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        a1 = 0x33CD0; e1 = orig.index(0, 16 + a1) - 16; e2 = orig.index(0, 16 + e1 + 1) - 16
        old = orig[16 + a1:16 + e2]
        b1 = encode('\n'.join(m.INTRO1), terminate=False)
        b2 = encode('\n'.join(m.INTRO2), terminate=False)
        n1, n2 = e1 - a1, e2 - e1 - 1
        if len(b1) > n1 or len(b2) > n2 or max(map(len, m.INTRO1 + m.INTRO2)) > 28:
            report['errors'].append('intro too long (%d/%d, %d/%d)' % (len(b1), n1, len(b2), n2))
        else:
            new = b1 + b'\xA0' * (n1 - len(b1)) + b'\x00' + b2 + b'\xA0' * (n2 - len(b2))
            rom[P0 + a1:P0 + e2] = new
            chr_copy = 16 + rom[4] * 0x4000 + 0x1ECD0
            if bytes(rom[chr_copy:chr_copy + len(old)]) == old:
                rom[chr_copy:chr_copy + len(old)] = new
                report['intro'] = 'PRG $33CD0 + CHR $1ECD0'
            else:
                report['intro'] = 'PRG $33CD0 (CHR copy differs, not touched)'
    rom = bytes(rom)
    open(os.path.join(outdir, 'mother_vi.nes'), 'wb').write(rom)
    ips = make_ips(orig, rom)
    open(os.path.join(outdir, 'mother_vi.ips'), 'wb').write(ips)
    report['rom'] = {'crc32': '%08X' % (zlib.crc32(rom) & 0xFFFFFFFF), 'size': len(rom),
                     'ips_bytes': len(ips)}
    json.dump(report, open(os.path.join(outdir, 'build_report.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return rom, report

def make_ips(orig, new):
    out = bytearray(b'PATCH'); i = 0; n = len(new)
    def same(i): return i < len(orig) and orig[i] == new[i]
    while i < n:
        if same(i):
            i += 1; continue
        j = i
        while j < n and not same(j) and j - i < 0xFFFF:
            j += 1
        # RLE for long constant runs
        start = i
        if start == 0x454F46:
            start -= 1
        chunk = new[start:j]
        if len(chunk) > 8 and len(set(chunk)) == 1:
            out += struct.pack('>I', start)[1:] + b'\x00\x00' + struct.pack('>H', len(chunk)) + chunk[:1]
        else:
            out += struct.pack('>I', start)[1:] + struct.pack('>H', len(chunk)) + chunk
        i = j
    return bytes(out + b'EOF')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', required=True); ap.add_argument('--script', required=True)
    ap.add_argument('--tr', default=os.path.join(HERE, 'translations'))
    ap.add_argument('--out', default='out')
    a = ap.parse_args()
    rom, rep = build(a.rom, a.script, a.tr, a.out)
    print(json.dumps({k: rep[k] for k in ('script', 'names', 'rom')}, indent=1))
    print('errors:', len(rep['errors']), 'warnings:', len(rep['warnings']), 'untranslated:', len(rep['untranslated']))
    for e in rep['errors'][:40]: print('  E', e)
    for w in rep['warnings'][:20]: print('  W', w)
