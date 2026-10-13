#!/usr/bin/env python3
"""Independent validator for the Step 20 cumulative ROM and IPS.

Usage:
  python3 tools/validate_final_build_step20.py --source-rom "/path/to/Mighty Final Fight (USA).nes"

It verifies source identity, the IPS round-trip, artifact hashes, indexed text
catalog coverage, fixed file sizes, and preservation of grunt animation bytes.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
EXPECTED_CLEAN_SHA = '5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
EXPECTED_STEP19_SHA = '0b332d25e7444430dd48a09e45f6a8b9679ff1318d5375195d498aed53f021e6'
EXPECTED_FINAL_SHA = '03d2d05e2303e2b41a5213b248bdd3d20cfa478a8e473dd00734d42882e6bcbc'
EXPECTED_IPS_SHA = '2778df5a7eabad3ca66d32b2a9fc6e41f1b0b7a825daa8c174e43dbdc6b135b5'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_ips(patch: bytes) -> list[tuple[int, bytes]]:
    if not patch.startswith(b'PATCH'):
        raise ValueError('IPS header missing')
    out=[]; p=5
    while patch[p:p+3] != b'EOF':
        if p+5 > len(patch): raise ValueError('truncated IPS record')
        offset=int.from_bytes(patch[p:p+3], 'big')
        length=int.from_bytes(patch[p+3:p+5], 'big'); p+=5
        if length:
            block=patch[p:p+length]; p+=length
            if len(block)!=length: raise ValueError('truncated IPS payload')
        else:
            if p+3>len(patch): raise ValueError('truncated IPS RLE record')
            n=int.from_bytes(patch[p:p+2],'big'); value=patch[p+2]; p+=3
            block=bytes([value])*n
        out.append((offset,block))
    p+=3
    if p!=len(patch): raise ValueError('unexpected bytes after IPS EOF')
    return out


def apply_ips(source: bytes, patch: bytes) -> bytes:
    result=bytearray(source)
    for offset,block in parse_ips(patch):
        if offset+len(block)>len(result):
            result.extend(b'\x00'*(offset+len(block)-len(result)))
        result[offset:offset+len(block)]=block
    return bytes(result)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-rom', type=Path, required=True, help='Clean, unpatched USA ROM')
    ap.add_argument('--rom', type=Path, default=PROJECT/'release'/'Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes')
    ap.add_argument('--ips', type=Path, default=PROJECT/'release'/'Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips')
    ap.add_argument('--catalog', type=Path, default=PROJECT/'analysis'/'step20_full_translation_catalog.tsv')
    args=ap.parse_args()
    src=args.source_rom.read_bytes(); rom=args.rom.read_bytes(); patch=args.ips.read_bytes()
    errors=[]; checks={}
    checks['clean_source_sha256']=sha(src)
    checks['clean_source_hash_matches']=sha(src)==EXPECTED_CLEAN_SHA
    checks['final_rom_sha256']=sha(rom)
    checks['final_rom_hash_matches']=sha(rom)==EXPECTED_FINAL_SHA
    checks['ips_sha256']=sha(patch)
    checks['ips_hash_matches']=sha(patch)==EXPECTED_IPS_SHA
    checks['clean_source_size']=len(src)
    checks['final_rom_size']=len(rom)
    checks['rom_size_matches_expected']=len(src)==262160 and len(rom)==278544
    checks['ips_round_trip_matches_rom']=apply_ips(src,patch)==rom
    records=parse_ips(patch)
    checks['ips_record_count']=len(records)
    checks['ips_records_nonempty']=all(block for _,block in records)
    # All cataloged indexed records need a Vietnamese payload; aliases are rows
    # too, so users can review them by game index rather than only by pointer.
    with args.catalog.open(encoding='utf-8', newline='') as f:
        rows=list(csv.DictReader(f,delimiter='\t'))
    checks['catalog_rows']=len(rows)
    checks['catalog_group_counts']={g:sum(r.get('group')==g for r in rows) for g in ('opening','boss','credits')}
    checks['catalog_90_index_rows']=len(rows)==90 and checks['catalog_group_counts']=={'opening':7,'boss':78,'credits':5}
    checks['catalog_has_no_empty_vietnamese_text']=all(r.get('vietnamese','').strip() for r in rows)
    # Reconstruct Step 19 base, then compare the two animation slots: seven
    # visible grunt glyphs differ, while their punctuation/animation tails stay exact.
    base_patch=(PROJECT/'analysis'/'step19_boss_dialogue_pilot_combined.ips').read_bytes()
    base=apply_ips(src,base_patch)
    checks['step19_base_sha256']=sha(base)
    checks['step19_base_hash_matches']=sha(base)==EXPECTED_STEP19_SHA
    with (PROJECT/'analysis'/'pointer_tables.csv').open(encoding='utf-8-sig',newline='') as f:
        ptrs=list(csv.DictReader(f))
    grunt_results={}
    for idx in (9,10):
        r=next(r for r in ptrs if r['group']=='boss' and int(r['index'])==idx)
        start=int(r['file_offset'],16); length=35
        grunt_results[str(idx)]={
            'prefix_preserved':rom[start:start+5]==base[start:start+5],
            'localized_bytes':rom[start+5:start+12].decode('latin1')==(bytes([0x31])*7).decode('latin1'),
            'punctuation_and_animation_preserved':rom[start+12:start+length]==base[start+12:start+length],
        }
    checks['grunt_animation_preservation']=grunt_results
    checks['both_grunt_tails_preserved']=all(x['prefix_preserved'] and x['localized_bytes'] and x['punctuation_and_animation_preserved'] for x in grunt_results.values())
    checks['all_checks_passed']=all(v for k,v in checks.items() if isinstance(v,bool))
    report={'step':20,'title':'Independent final indexed-text artifact validation','status':'PASS' if checks['all_checks_passed'] else 'FAIL','checks':checks}
    report_path=PROJECT/'analysis'/'step20_independent_validation.json'
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    log=['STEP 20 INDEPENDENT VALIDATION',f"Status: {report['status']}"]
    for key,val in checks.items(): log.append(f'{key}: {json.dumps(val,ensure_ascii=False)}')
    (PROJECT/'analysis'/'step20_independent_validation.txt').write_text('\n'.join(log)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report['status']!='PASS': raise SystemExit(1)

if __name__=='__main__': main()
