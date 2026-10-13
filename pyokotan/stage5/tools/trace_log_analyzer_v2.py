#!/usr/bin/env python3
"""Analyze Pyokotan FCEUX trace v2 CSV, including active mapper and PPU tile context.

Works with v1 trace CSVs too, but physical-bank/tile derivations require v2 columns.
Usage: python trace_log_analyzer_v2.py pyokotan_runtime_trace_v2.csv --outdir outputs
"""
from __future__ import annotations
import argparse, csv, json, hashlib
from collections import Counter, defaultdict
from pathlib import Path

PRG_BANKS=16
CHR_1K_BANKS=128

def parse_num(s):
    if s is None or s=='': return None
    s=str(s).strip()
    try: return int(s,16) if s.lower().startswith('0x') else int(s)
    except ValueError: return None

def parse_trace(path: Path):
    events=[]
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        fields=set(reader.fieldnames or [])
        required={'frame','event','address','value','pc'}
        if not required.issubset(fields):
            raise SystemExit('ERROR: trace is missing one or more required columns: frame,event,address,value,pc')
        for rownum,row in enumerate(reader,2):
            frame=parse_num(row.get('frame')); address=parse_num(row.get('address')); value=parse_num(row.get('value')); pc=parse_num(row.get('pc'))
            if frame is None or not row.get('event'): continue
            item={'line':rownum,'frame':frame,'event':row['event'],'address':address,'value':value,'pc':pc,
                  'size':parse_num(row.get('size')) or 1,'raw':row}
            for k in ['mapper_command','mapper_register','prg_8000_raw','prg_a000_raw','prg_c000_raw',
                      'chr0_raw','chr1_raw','chr2_raw','chr3_raw','chr4_raw','chr5_raw','chr6_raw','chr7_raw',
                      'ppu_ctrl','ppu_addr_current','ppu_addr_write_target','ppu_latch_high_next']:
                item[k]=parse_num(row.get(k))
            events.append(item)
    return events

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('trace_csv',type=Path)
    ap.add_argument('--outdir',type=Path,default=Path('outputs'))
    a=ap.parse_args(); events=parse_trace(a.trace_csv); a.outdir.mkdir(parents=True,exist_ok=True)
    evcounts=Counter(e['event'] for e in events)
    text=[e for e in events if e['event']=='text_region_read']
    text_addr=Counter(e['address'] for e in text if e['address'] is not None)
    text_val=Counter(e['value'] for e in text if e['value'] is not None)
    bank_context=Counter(e['prg_c000_raw'] for e in text if e['prg_c000_raw'] is not None)
    prg_offsets=[]
    for e in text:
        a_cpu=e['address']; raw_bank=e['prg_c000_raw']
        if a_cpu is None: continue
        guessed=None; basis='unknown: bank register not observed in this trace yet'
        if 0xC000<=a_cpu<=0xDFFF and raw_bank is not None:
            guessed=(raw_bank%PRG_BANKS)*0x2000+(a_cpu-0xC000); basis='heuristic: raw command-B bank modulo this ROM 16-bank PRG size'
        elif 0xE000<=a_cpu<=0xFFFF:
            guessed=(PRG_BANKS-1)*0x2000+(a_cpu-0xE000); basis='fixed last 8 KiB PRG bank'
        prg_offsets.append({'frame':e['frame'],'pc':f'0x{e["pc"]:04X}' if e['pc'] is not None else None,
          'cpu_address':f'0x{a_cpu:04X}','value':f'0x{e["value"]:02X}' if e['value'] is not None else None,
          'prg_c000_bank_raw':f'0x{raw_bank:02X}' if raw_bank is not None else None,
          'physical_prg_offset_guess':f'0x{guessed:05X}' if guessed is not None else None,'basis':basis})
    mapper_rows=[e for e in events if e['event'] in ('mapper_command_write','mapper_parameter_write','mapper_write')]
    command_values=Counter(e['value'] for e in mapper_rows if e['event']=='mapper_command_write' and e['value'] is not None)
    params=Counter((e['mapper_register'],e['value']) for e in mapper_rows if e['event']=='mapper_parameter_write' and e['value'] is not None)
    ppu=[e for e in events if e['event']=='ppu_register_write']
    ppu2007=[]; chrcontext=Counter(); nametable_values=Counter(); rendered_groups=defaultdict(Counter)
    for e in ppu:
        if e['address'] is None or (e['address']%8)!=7 or e['value'] is None: continue
        target=e.get('ppu_addr_write_target')
        if target is None: continue
        row={'frame':e['frame'],'pc':f'0x{e["pc"]:04X}' if e['pc'] is not None else None,
             'ppu_address':f'0x{target:04X}','tile_or_data_value':f'0x{e["value"]:02X}',
             'ppu_ctrl':f'0x{e["ppu_ctrl"]:02X}' if e['ppu_ctrl'] is not None else None,
             'is_nametable_tile_write':0x2000<=target<=0x2FFF,
             'pattern_table_base_guess':None,'chr_window':None,'chr_bank_raw':None,
             'physical_chr_bank_1k_guess':None,'physical_tile_index_guess':None,'physical_chr_offset_guess':None,
             'mapping_confidence':'not derived'}
        if 0x2000<=target<=0x2FFF:
            nametable_values[e['value']]+=1
            ctrl=e['ppu_ctrl']
            if ctrl is not None:
                base=0x1000 if (ctrl&0x10) else 0x0000
                pat_addr=base+(e['value']*16)
                window=pat_addr//0x400
                rawbank=e.get(f'chr{window}_raw')
                row['pattern_table_base_guess']=f'0x{base:04X}'
                row['chr_window']=window
                row['chr_bank_raw']=f'0x{rawbank:02X}' if rawbank is not None else None
                if rawbank is not None:
                    bank_eff=rawbank%CHR_1K_BANKS
                    tile_in_bank=(pat_addr%0x400)//16
                    tile_idx=bank_eff*64+tile_in_bank
                    chr_off=tile_idx*16
                    row['physical_chr_bank_1k_guess']=bank_eff
                    row['physical_tile_index_guess']=f'0x{tile_idx:04X}'
                    row['physical_chr_offset_guess']=f'0x{chr_off:05X}'
                    row['mapping_confidence']='bank-register-derived estimate; verify PPUCTRL, latch alignment, and hardware mapping in trace'
                    chrcontext[(window,rawbank,e['value'])]+=1
                else:
                    row['mapping_confidence']='nametable byte observed, but CHR bank for selected pattern-table window was not captured yet'
        ppu2007.append(row)
    # CSV of all PPU $2007 writes with target-address derivations.
    ppu_csv=a.outdir/'pyokotan_ppu_tile_writes_v2.csv'
    pfields=['frame','pc','ppu_address','tile_or_data_value','ppu_ctrl','is_nametable_tile_write','pattern_table_base_guess','chr_window','chr_bank_raw','physical_chr_bank_1k_guess','physical_tile_index_guess','physical_chr_offset_guess','mapping_confidence']
    with ppu_csv.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=pfields); w.writeheader(); w.writerows(ppu2007)
    po=a.outdir/'pyokotan_text_read_bank_context_v2.json'
    po.write_text(json.dumps({'source_file':a.trace_csv.name,'read_count':len(prg_offsets),'read_contexts':prg_offsets,
      'note':'Offsets are estimates. $E000-$FFFF is treated as the fixed final PRG bank; $C000-$DFFF uses observed command-B raw bank reduced modulo 16 physical PRG banks.'},indent=2)+'\n',encoding='utf-8')
    report={'schema_version':'2.0','source_file':a.trace_csv.name,'events_total':len(events),'event_counts':dict(evcounts),
      'text_region_reads':len(text),'text_region_addresses_most_read':[{'address':f'0x{k:04X}','count':v} for k,v in text_addr.most_common(100)],
      'text_region_values_read':[{'value_hex':f'0x{k:02X}','count':v} for k,v in text_val.most_common()],
      'text_read_prg_c000_bank_raw_counts':[{'raw_bank':f'0x{k:02X}','count':v} for k,v in bank_context.most_common()],
      'text_read_bank_context_output':po.name,
      'mapper_event_count':len(mapper_rows),'mapper_command_values':[{'value':f'0x{k:02X}','count':v} for k,v in command_values.most_common()],
      'mapper_parameter_values':[{'command':f'0x{cmd:X}' if cmd is not None else None,'value':f'0x{val:02X}','count':count} for (cmd,val),count in params.most_common()],
      'ppu_register_writes':len(ppu),'ppu_2007_writes':len(ppu2007),'ppu_nametable_tile_writes':sum(1 for x in ppu2007 if x['is_nametable_tile_write']),
      'ppu_nametable_tile_values':[{'tile_value':f'0x{k:02X}','count':v} for k,v in nametable_values.most_common()],
      'ppu_tile_write_csv':ppu_csv.name,
      'limitations':['This report only summarizes the trace supplied by the user; no ROM runtime trace is synthesized here.',
        'The PPU address latch estimate can lose sync if writes to $2005/$2006 are missed or mirrored differently.',
        'Physical CHR offset guesses require the PPUCTRL background pattern-table selection and a captured CHR-bank register for that window.',
        'PRG bank estimates reflect this ROM’s 16-bank capacity and the observed raw command-B value; mapper mirroring/masking should be checked against a trace.']}
    out=a.outdir/'pyokotan_runtime_trace_summary_v2.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'trace_rows':len(events),'text_reads':len(text),'ppu_2007_writes':len(ppu2007),'outdir':str(a.outdir)},indent=2))

if __name__=='__main__': main()
