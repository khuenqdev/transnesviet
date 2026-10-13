#!/usr/bin/env python3
"""Summarize a CSV emitted by pyokotan_fceux_text_trace.lua."""
from __future__ import annotations
import argparse, csv, json, re
from collections import Counter
from pathlib import Path

def n(v):
    if v is None or v == '': return None
    return int(v, 0) if v.lower().startswith('0x') else int(v)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('trace_csv', type=Path)
    ap.add_argument('--out', type=Path, default=Path('outputs/runtime_trace_summary.json'))
    ap.add_argument('--filtered-csv', type=Path, default=Path('outputs/runtime_trace_interesting.csv'))
    args = ap.parse_args()
    events=[]
    with args.trace_csv.open(newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        required={'frame','event','address','value','pc'}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise SystemExit('ERROR: expected columns frame,event,address,value,pc')
        for row in reader:
            try:
                e={'frame':int(row['frame']), 'event':row['event'], 'address':n(row['address']), 'value':n(row['value']), 'pc':n(row['pc'])}
            except Exception as exc:
                continue
            e['raw']=row
            events.append(e)
    counts=Counter(e['event'] for e in events)
    addr_counts=Counter((e['event'],e['address']) for e in events)
    interesting=[e for e in events if e['event']=='text_region_read' or e['event']=='mapper_write' or e['event']=='ppu_register_write']
    text_reads=[e for e in events if e['event']=='text_region_read']
    mapper=[e for e in events if e['event']=='mapper_write']
    ppu=[e for e in events if e['event']=='ppu_register_write']
    report={
      'schema_version':'1.0','source_file':args.trace_csv.name,'events_total':len(events),
      'event_counts':dict(counts),
      'text_region_reads':len(text_reads),
      'text_region_addresses_most_read':[{'address':f'0x{a:04X}','count':c} for (ev,a),c in addr_counts.most_common() if ev=='text_region_read'][:100],
      'text_region_values_read': [{'value_hex':f'{v:02X}','count':c} for v,c in Counter(e['value'] for e in text_reads).most_common()],
      'mapper_writes':len(mapper),
      'mapper_write_samples':[{'frame':e['frame'],'pc':f'0x{e["pc"]:04X}','address':f'0x{e["address"]:04X}','value':f'{e["value"]:02X}'} for e in mapper[:500]],
      'ppu_register_writes':len(ppu),
      'ppu_write_samples':[{'frame':e['frame'],'pc':f'0x{e["pc"]:04X}','address':f'0x{e["address"]:04X}','value':f'{e["value"]:02X}'} for e in ppu[:500]],
      'interpretation_note':'This tool summarizes observed emulator activity only. A zero text-region read count does not prove the data is unused; the bank/address assumption may be wrong or the scene was not exercised.'
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    args.filtered_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.filtered_csv.open('w', newline='', encoding='utf-8-sig') as f:
       fields=['frame','event','address','value','pc']
       w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
       for e in interesting:
          w.writerow({'frame':e['frame'],'event':e['event'],'address':f'0x{e["address"]:04X}','value':f'0x{e["value"]:02X}','pc':f'0x{e["pc"]:04X}'})
    print(f'Parsed {len(events)} events; {len(text_reads)} reads in candidate text region. Wrote {args.out}')
if __name__ == '__main__': main()
