#!/usr/bin/env python3
"""Search the PRG image for little-endian CPU addresses of known ASCII rows.

Raw matches are candidates only: an address-shaped word inside code or data is
not automatically a live pointer. This script intentionally scans only PRG ROM.
"""
from pathlib import Path
import argparse, csv, json, hashlib

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path); ap.add_argument('--outdir',type=Path,default=Path('outputs'))
    a=ap.parse_args(); raw=a.rom.read_bytes()
    if raw[:4]!=b'NES\x1a': raise SystemExit('Not an iNES ROM')
    h=raw[:16]; size=(h[4]|((h[9]&15)<<8))*0x4000
    prg=raw[16:16+size]
    if len(prg)!=0x20000: raise SystemExit('Expected the 128 KiB Pyokotan PRG image')
    rows=[]; base=0x1DE86; stride=0x22
    for n in range(12):
        off=base+n*stride
        cpu=0xC000+(off-0x1C000) if off<0x1E000 else 0xE000+(off-0x1E000)
        needle=cpu.to_bytes(2,'little'); found=[]; pos=0
        while True:
            pos=prg.find(needle,pos)
            if pos<0: break
            # Look at bytes around each match and tag mapped fixed-bank offsets.
            bank=pos//0x2000
            found.append({'prg_offset':f'0x{pos:05X}','bank_8k':bank,
                          'cpu_address_if_fixed_map':f'0x{(0xC000+pos-0x1C000) if pos<0x1E000 else (0xE000+pos-0x1E000):04X}' if pos>=0x1C000 else None,
                          'context_hex':prg[max(0,pos-4):min(len(prg),pos+6)].hex(' ').upper(),
                          'note':'Raw byte occurrence only; code/data/pointer meaning is unconfirmed'})
            pos+=1
        rows.append({'row':n,'prg_target':f'0x{off:05X}','cpu_row_address_under_reset_map':f'0x{cpu:04X}',
                     'target_word_le_hex':needle.hex(' ').upper(),'raw_prg_match_count':len(found),'matches':found})
    result={'schema_version':'1.0','rom':a.rom.name,'rom_sha1':hashlib.sha1(raw).hexdigest(),
            'method':'Search the 128 KiB PRG region for little-endian CPU start addresses of the 12 fixed-width ASCII rows.',
            'total_raw_matches':sum(x['raw_prg_match_count'] for x in rows), 'rows':rows,
            'interpretation':'No raw matches strongly reduces the chance of a simple table of direct row-start pointers. Matches that exist are unconfirmed and may be false positives. The game could compute row addresses from a base plus a stride, keep pointers outside PRG, or access them through a banked/data-driven routine.'}
    a.outdir.mkdir(parents=True,exist_ok=True)
    j=a.outdir/'pyokotan_row_pointer_value_scan_v4.json'; j.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    c=a.outdir/'pyokotan_row_pointer_value_scan_v4.csv'
    with c.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['row','prg_target','cpu_row_address_under_reset_map','target_word_le_hex','raw_prg_match_count','match_prg_offsets','match_contexts'])
        for r in rows:
            w.writerow([r['row'],r['prg_target'],r['cpu_row_address_under_reset_map'],r['target_word_le_hex'],r['raw_prg_match_count'], ';'.join(m['prg_offset'] for m in r['matches']), ';'.join(m['context_hex'] for m in r['matches'])])
    print(f'Wrote {j} and {c}; total raw matches: {result["total_raw_matches"]}')
if __name__=='__main__': main()
