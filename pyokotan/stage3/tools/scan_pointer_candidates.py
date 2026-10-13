#!/usr/bin/env python3
"""Scan candidate address sequences and audit whether targets look like text.

This is deliberately heuristic. For the leading candidate sequence in this
ROM, the table bytes live in PRG bank 8 and its $94xx targets resolve into the
same bank only under that assumed bank mapping. The target data looks binary,
not like ASCII/kana strings, so candidates are not promoted to text pointers.
"""
from __future__ import annotations
import argparse, json, zlib
from pathlib import Path
HEADER = 16


def load_prg(path: Path):
    raw = path.read_bytes()
    if raw[:4] != b"NES\x1a": raise ValueError("Not an iNES ROM")
    if (raw[7] & 0x0C) != 0x08: raise ValueError("Expected NES 2.0 header")
    pm = raw[9] & 0x0F
    if pm == 0x0F: raise ValueError("Unsupported NES 2.0 exponent-sized PRG")
    n = (raw[4] | (pm << 8)) * 0x4000
    return raw, raw[HEADER:HEADER+n]


def score_ascii(buf):
    if not buf: return 0.0
    return sum(32 <= b <= 126 for b in buf) / len(buf)


def scan(prg, min_items=4, max_gap=0x100, limit=100):
    rows=[]
    for off in range(0, len(prg)-2*min_items+1, 2):
        vals=[int.from_bytes(prg[off+2*i:off+2*i+2], 'little') for i in range(min_items)]
        if not all(0x8000 <= v <= 0xFFFF for v in vals): continue
        deltas=[vals[i+1]-vals[i] for i in range(len(vals)-1)]
        if not all(1 <= d <= max_gap for d in deltas): continue
        end=off+2*min_items; run=vals[:]
        while end+2 <= len(prg):
            n=int.from_bytes(prg[end:end+2], 'little')
            if not 0x8000 <= n <= 0xFFFF or not 1 <= n-run[-1] <= max_gap: break
            run.append(n); end+=2
        rows.append((len(run), off, run))
    rows.sort(key=lambda x:(x[0], -sum(x[2][i+1]-x[2][i] for i in range(len(x[2])-1))/max(1,len(x[2])-1)), reverse=True)
    selected=[]; spans=[]
    for count, off, vals in rows:
        end=off+2*count
        if any(not (end<=a or off>=b) for a,b in spans): continue
        selected.append((off, vals)); spans.append((off,end))
        if len(selected)>=limit: break
    return selected


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('rom',type=Path)
    ap.add_argument('--out',type=Path,default=Path('outputs/pointer_candidate_audit.json'))
    args=ap.parse_args(); raw,prg=load_prg(args.rom)
    candidates=[]
    for off, vals in scan(prg):
        row={'table_prg_offset':f'0x{off:05X}','table_file_offset':f'0x{HEADER+off:05X}',
             'count':len(vals),'target_cpu_addresses':[f'0x{v:04X}' for v in vals],
             'table_prg_8k_bank':off//0x2000,
             'confidence':'low; monotonic address-shaped words only'}
        # The first important group has its targets in CPU $8000-$9FFF; show the
        # physical interpretation only under a clearly stated bank assumption.
        if off//0x2000 == 8 and vals and all(0x8000 <= v < 0xA000 for v in vals[:min(6,len(vals))]):
            audits=[]
            for v in vals[:8]:
                target=0x10000+(v-0x8000)  # same bank-8 assumption
                chunk=prg[target:target+24]
                audits.append({'cpu_target':f'0x{v:04X}','assumed_prg_offset_if_bank8':f'0x{target:05X}',
                               'bytes_hex':chunk.hex(' ').upper(),'ascii_printable_ratio_24':round(score_ascii(chunk),3)})
            row['same_bank8_target_audit']=audits
            if audits and max(x['ascii_printable_ratio_24'] for x in audits) < 0.4:
                row['assessment']='targets look like binary/layout data under same-bank assumption, not ordinary ASCII strings; text-pointer role unconfirmed'
        candidates.append(row)
    out={'schema_version':'2.0','rom':args.rom.name,'rom_crc32':f'{zlib.crc32(raw)&0xFFFFFFFF:08X}',
         'method':'Little-endian 16-bit words in $8000-$FFFF with monotonically increasing targets and gaps <= 0x100.',
         'important_caveat':'These are address-shaped sequences, not proven pointer tables. Mapper 69 bank register state is required to resolve target addresses.',
         'candidate_count':len(candidates),'candidates':candidates}
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {args.out}: {len(candidates)} unverified address-sequence candidates.')
if __name__=='__main__': main()
