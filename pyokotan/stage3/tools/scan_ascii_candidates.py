#!/usr/bin/env python3
"""Inventory printable ASCII runs and score potentially human-readable strings.

The scanner intentionally keeps two outputs distinct:
- all_printable_runs: any run of printable bytes >= --min-length (lots of graphic/data false positives)
- readable_candidates: a conservative heuristic shortlist, not confirmed dialogue.
Only ASCII 0x20-0x7E is decoded; extended glyph bytes are left for a verified .tbl.
"""
from __future__ import annotations
import argparse, csv, json, re, zlib
from pathlib import Path
HEADER = 16

def read_rom(path: Path):
    raw = path.read_bytes()
    if raw[:4] != b'NES\x1a': raise SystemExit('ERROR: not an iNES ROM')
    if (raw[7] & 0x0C) != 0x08: raise SystemExit('ERROR: expected NES 2.0 ROM')
    pm = raw[9] & 0x0F; cm = (raw[9] >> 4) & 0x0F
    if pm == 0x0F or cm == 0x0F: raise SystemExit('ERROR: exponent-size NES 2.0 headers not supported')
    prg_size = (raw[4] | (pm << 8)) * 0x4000
    return raw, raw[HEADER:HEADER + prg_size]

def iter_runs(prg: bytes, min_len: int):
    i = 0
    while i < len(prg):
        if 0x20 <= prg[i] <= 0x7E:
            j = i + 1
            while j < len(prg) and 0x20 <= prg[j] <= 0x7E: j += 1
            if j - i >= min_len:
                s = prg[i:j].decode('ascii')
                alpha = sum(ch.isalpha() for ch in s) / len(s)
                digit = sum(ch.isdigit() for ch in s) / len(s)
                spaces = s.count(' ') / len(s)
                punctuation = sum(ch in " .,:;!?'-_/()[]" for ch in s) / len(s)
                repeated_max = max((len(m.group(0)) for m in re.finditer(r'(.)\1+', s)), default=1)
                tokens = re.findall(r'[A-Za-z]{2,}', s)
                nontrivial = sum(len(set(t.lower())) >= 2 and not re.fullmatch(r'(.)\1+', t.lower()) for t in tokens)
                # Heuristic only: repeated sprite/tile patterns and high-entropy strings score poorly.
                score = alpha * 1.7 + min(len(tokens), 6) * 0.09 + spaces * 0.45 + punctuation * 0.25 - (repeated_max / len(s)) * 1.4
                cpu_bank = i // 0x2000
                yield {
                    'prg_offset': f'0x{i:05X}', 'file_offset': f'0x{HEADER+i:05X}',
                    'prg_8k_bank': cpu_bank, 'bank_offset': f'0x{i % 0x2000:04X}',
                    'length': len(s), 'text_ascii': s, 'alpha_ratio': round(alpha, 3),
                    'digit_ratio': round(digit, 3), 'space_ratio': round(spaces, 3),
                    'repeated_run_max': repeated_max, 'word_tokens': tokens,
                    'nontrivial_word_count': int(nontrivial), 'readability_score': round(score, 3),
                    'heuristic_candidate': bool(alpha >= 0.45 and len(set(s)) >= 4 and nontrivial >= 2 and (spaces > 0 or punctuation > 0.1) and repeated_max / len(s) < 0.35 and score > 1.1),
                    'warning': 'Printable-byte run only; may be graphics, lookup data, or non-text payload.'
                }
            i = j
        else: i += 1

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom', type=Path)
    ap.add_argument('--out-json', type=Path, default=Path('outputs/ascii_run_census.json'))
    ap.add_argument('--out-csv', type=Path, default=Path('outputs/ascii_run_census.csv'))
    ap.add_argument('--min-length', type=int, default=5)
    args = ap.parse_args()
    raw, prg = read_rom(args.rom)
    rows = list(iter_runs(prg, args.min_length))
    shortlist = sorted((r for r in rows if r['heuristic_candidate']), key=lambda r: (r['readability_score'], r['length']), reverse=True)
    result = {
        'schema_version': '1.0', 'rom': args.rom.name,
        'rom_crc32': f'{zlib.crc32(raw)&0xFFFFFFFF:08X}',
        'method': 'Contiguous PRG bytes 0x20-0x7E; then conservative readability heuristic.',
        'warning': 'Not a text extractor. Printable runs frequently occur inside compressed, tiled, or structured binary data.',
        'all_printable_run_count': len(rows), 'heuristic_candidate_count': len(shortlist),
        'all_printable_runs': rows, 'readable_candidates': shortlist,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open('w', newline='', encoding='utf-8-sig') as f:
        fields = list(rows[0].keys()) if rows else ['prg_offset']
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows:
            out = dict(r); out['word_tokens'] = ' '.join(out['word_tokens']); w.writerow(out)
    print(f'Wrote {len(rows)} printable runs; {len(shortlist)} heuristic candidates.')
if __name__ == '__main__': main()
