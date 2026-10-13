#!/usr/bin/env python3
"""Validate stage 5 static outputs against the supplied Pyokotan ROM."""
from pathlib import Path
import argparse, hashlib, json, csv, zlib

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('rom',type=Path); ap.add_argument('--outdir',type=Path,default=Path('outputs')); ap.add_argument('--refdir',type=Path,default=Path('reference')); a=ap.parse_args()
    raw=a.rom.read_bytes()
    expected='67fba2e82d78d512466d98bcc9fe11f8e229cb11'
    actual=hashlib.sha1(raw).hexdigest()
    if actual!=expected: raise SystemExit(f'ROM SHA-1 mismatch: {actual} != {expected}')
    inv=json.loads((a.outdir/'pyokotan_chr_tile_inventory_v5.json').read_text(encoding='utf-8'))
    summ=json.loads((a.outdir/'pyokotan_chr_inventory_summary_v5.json').read_text(encoding='utf-8'))
    dup=json.loads((a.outdir/'pyokotan_chr_exact_duplicates_v5.json').read_text(encoding='utf-8'))
    cat=json.loads((a.outdir/'pyokotan_font_candidate_catalog_v5.json').read_text(encoding='utf-8'))
    assert inv['chr_tiles_total']==8192 and len(inv['tile_records'])==8192
    assert summ['physical_chr_tiles']==8192 and summ['blank_tiles']==832 and summ['unique_exact_patterns']==4672
    assert len(cat['records'])==256
    assert len(dup['groups'])==summ['duplicate_pattern_groups']
    with (a.outdir/'pyokotan_chr_tile_inventory_v5.csv').open(newline='',encoding='utf-8-sig') as f:
        assert sum(1 for _ in csv.DictReader(f))==8192
    with (a.outdir/'pyokotan_chr_page_summary_v5.csv').open(newline='',encoding='utf-8-sig') as f:
        assert sum(1 for _ in csv.DictReader(f))==16
    imgs=list(a.refdir.glob('chr_physical_page_*.png'))
    assert len(imgs)>=17, f'Expected full and per-page atlases, found {len(imgs)}'
    for p in [a.outdir/'pyokotan_chr_tile_inventory_v5.json', a.outdir/'pyokotan_chr_inventory_summary_v5.json', a.outdir/'pyokotan_chr_exact_duplicates_v5.json', a.outdir/'pyokotan_font_candidate_catalog_v5.json']:
        json.loads(p.read_text(encoding='utf-8'))
    print(json.dumps({'rom_sha1':actual,'chr_tiles':len(inv['tile_records']),'unique_patterns':summ['unique_exact_patterns'],'blank_tiles':summ['blank_tiles'],'duplicate_groups':len(dup['groups']),'font_candidates':len(cat['records']),'atlas_files':len(imgs),'status':'PASS'},indent=2))
if __name__=='__main__': main()
