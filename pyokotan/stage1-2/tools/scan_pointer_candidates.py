#!/usr/bin/env python3
"""Heuristic 16-bit pointer-table candidate scanner for iNES/NES 2.0 PRG data.

The results are candidate offsets only. Mapper 69 banking means that target CPU
addresses cannot be resolved to unique ROM offsets without runtime bank state.
False positives are expected; never patch based only on these candidates.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

HEADER = 16

def get_prg(data: bytes) -> bytes:
    if len(data) < HEADER or data[:4] != b"NES\x1a":
        raise ValueError("Not an iNES/NES 2.0 ROM.")
    if (data[7] & 0x0C) != 0x08:
        raise ValueError("This scanner expects a NES 2.0 header.")
    high = data[9] & 0x0F
    if high == 0x0F:
        raise ValueError("PRG exponent-multiplier sizing is not handled.")
    size = (data[4] | (high << 8)) * 0x4000
    if HEADER + size > len(data):
        raise ValueError("Declared PRG size exceeds file size.")
    return data[HEADER:HEADER+size]

def scan(prg: bytes, min_items=4, max_gap=0x100):
    found = []
    for offset in range(0, len(prg) - min_items*2 + 1, 2):
        vals = [int.from_bytes(prg[offset+i*2:offset+i*2+2], 'little') for i in range(min_items)]
        if not all(0x8000 <= v <= 0xFFFF for v in vals):
            continue
        deltas = [vals[i+1]-vals[i] for i in range(len(vals)-1)]
        if not all(1 <= d <= max_gap for d in deltas):
            continue
        # Extend the run as long as addresses remain increasing by a modest gap.
        end = offset + min_items*2
        run_vals = list(vals)
        while end + 2 <= len(prg):
            nxt = int.from_bytes(prg[end:end+2], 'little')
            if not 0x8000 <= nxt <= 0xFFFF:
                break
            delta = nxt - run_vals[-1]
            if not 1 <= delta <= max_gap:
                break
            run_vals.append(nxt)
            end += 2
        found.append({
            'prg_offset': f'0x{offset:05X}',
            'file_offset': f'0x{HEADER+offset:05X}',
            'count': len(run_vals),
            'target_values': [f'0x{x:04X}' for x in run_vals],
            'deltas': [run_vals[i+1]-run_vals[i] for i in range(len(run_vals)-1)],
            'confidence': 'low; values fit an address-like pattern but have no confirmed text-code cross-reference',
        })
    # Deduplicate overlapping runs by preferring the most pointer-like sequences.
    found.sort(key=lambda r: (r['count'], -sum(r['deltas'])/max(1,len(r['deltas']))), reverse=True)
    selected = []
    used_spans = []
    for row in found:
        s = int(row['prg_offset'], 16)
        e = s + 2*row['count']
        if any(not (e <= a or s >= b) for a,b in used_spans):
            continue
        selected.append(row)
        used_spans.append((s,e))
        if len(selected) >= 100:
            break
    return selected

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path)
    ap.add_argument('--out',type=Path,default=Path('pointer_candidates.json'))
    ap.add_argument('--min-items',type=int,default=4)
    ap.add_argument('--max-gap',type=lambda x:int(x,0),default=0x100)
    args=ap.parse_args()
    data=args.rom.read_bytes(); prg=get_prg(data)
    rows=scan(prg,args.min_items,args.max_gap)
    output={
      'rom':args.rom.name,
      'method':'scan for consecutive little-endian 16-bit values in $8000-$FFFF with strictly increasing targets and modest gaps',
      'candidate_count':len(rows),
      'warning':'All hits are heuristic candidates. In mapper 69 ROMs, CPU address resolution depends on the active 8KB PRG bank. These results are not proof of text pointer tables.',
      'candidates':rows,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {args.out}: {len(rows)} low-confidence candidates.')
if __name__=='__main__': main()
