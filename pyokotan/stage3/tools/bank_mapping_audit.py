#!/usr/bin/env python3
"""Map selected physical PRG offsets to plausible CPU addresses for mapper 69.

This is a hypothesis audit, not an emulator bank-state dump. It shows which
mapping makes the vectors and adjacent fixed-width table layout fit naturally.
"""
from __future__ import annotations
import argparse, json, zlib
from pathlib import Path
HEADER=16

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('rom',type=Path); ap.add_argument('--out',type=Path,default=Path('outputs/bank_mapping_audit.json')); a=ap.parse_args()
    raw=a.rom.read_bytes()
    if raw[:4]!=b'NES\x1a' or (raw[7]&0x0C)!=0x08: raise SystemExit('Expected NES 2.0 iNES ROM')
    pm=a.rom.read_bytes()[9]&0x0F
    prg_size=(raw[4]|(pm<<8))*0x4000
    prg=raw[HEADER:HEADER+prg_size]
    if len(prg)<0x20000: raise SystemExit('Unexpectedly small PRG')
    vectors_off=len(prg)-6
    vectors={k:int.from_bytes(prg[vectors_off+i:vectors_off+i+2],'little') for k,i in [('nmi',0),('reset',2),('irq_brk',4)]}
    fixed_table_start=0x1DE86; stride=0x22; payload=0x20; count=12
    rows=[]
    for i in range(count):
        off=fixed_table_start+i*stride
        row=prg[off:off+payload]
        rows.append({'index':i,'prg_offset':f'0x{off:05X}','bank14_relative_offset':f'0x{off-0x1C000:04X}',
          'cpu_address_if_bank14_mapped_at_C000':f'0x{0xC000+(off-0x1C000):04X}',
          'file_offset':f'0x{HEADER+off:05X}','raw_ascii':''.join(chr(b) if 0x20<=b<=0x7e else f'<{b:02X}>' for b in row).strip(),
          'payload_crosses_into_next_bank':off+payload>0x1E000})
    def bank_offset_for_cpu(addr, bank, window_base):
        return bank*0x2000+(addr-window_base)
    vector_resolutions=[]
    for label,addr in vectors.items():
        if 0xC000<=addr<0xE000:
            off=bank_offset_for_cpu(addr,14,0xC000)
            vector_resolutions.append({'vector':label,'cpu_target':f'0x{addr:04X}','physical_offset_if_bank14_at_C000':f'0x{off:05X}',
              'is_in_bank14':off//0x2000==14})
        elif 0xE000<=addr<=0xFFFF:
            off=15*0x2000+(addr-0xE000)
            vector_resolutions.append({'vector':label,'cpu_target':f'0x{addr:04X}','physical_offset_if_bank15_fixed_at_E000':f'0x{off:05X}',
              'is_in_fixed_last_bank':off//0x2000==15})
        else:
            vector_resolutions.append({'vector':label,'cpu_target':f'0x{addr:04X}','resolution':'outside expected $C000/$E000 regions; requires bank-state investigation'})
    result={'schema_version':'1.0','rom':a.rom.name,'rom_crc32':f'{zlib.crc32(raw)&0xFFFFFFFF:08X}',
      'mapper':69,'prg_8k_bank_count':len(prg)//0x2000,
      'facts':{'nmi_vector':f'0x{vectors["nmi"]:04X}','reset_vector':f'0x{vectors["reset"]:04X}','irq_brk_vector':f'0x{vectors["irq_brk"]:04X}',
       'fixed_table_start_prg_offset':'0x1DE86','table_bank_index':fixed_table_start//0x2000,
       'table_bank_relative_offset':f'0x{fixed_table_start%0x2000:04X}',
       'table_straddles_bank14_to_bank15':fixed_table_start+11*stride+stride>0x1E000},
      'static_inference':{'candidate_mapping':'PRG bank 14 at CPU $C000-$DFFF; final PRG bank 15 at CPU $E000-$FFFF',
       'why':'NMI/IRQ targets $D88D/$D92A fall inside the $C000-$DFFF window and resolve into physical PRG bank 14 under this mapping; reset target $FFD0 resolves into the last/fixed bank. The fixed-width table starts at $DE86 and its last row extends into $E000, making the byte layout contiguous under this mapping.',
       'confidence':'strong static inference, not runtime-confirmed; mapper register state could change during execution and vectors can be handled by code that switches banks.'},
      'vector_resolutions':vector_resolutions,'fixed_table_rows':rows,
      'warning':'This is a hypothesized bank map. Confirm by logging mapper 69 writes and reads while the title/menu appears; do not use this alone to patch ROM bytes.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(f'Wrote {a.out}')
if __name__=='__main__':main()
