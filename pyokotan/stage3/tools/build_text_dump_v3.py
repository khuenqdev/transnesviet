#!/usr/bin/env python3
"""Create the v3 JSON dump from confirmed static records and explicit candidates."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from extract_text import make_dump, load_rom

CHARSET_SEQUENCE_SPANS = [
    (0x1E12F, 17, 'charset_sequence_punctuation'),
    (0x1E142, 17, 'charset_sequence_digits_and_punctuation'),
    (0x1E155, 18, 'charset_sequence_uppercase_A_to_O'),
    (0x1E168, 18, 'charset_sequence_uppercase_P_to_Z'),
    (0x1E17B, 18, 'charset_sequence_lowercase_a_to_o'),
    (0x1E18E, 15, 'charset_sequence_lowercase_p_to_z'),
]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path); ap.add_argument('--tbl',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path('outputs/pyokotan_text_dump_v3.json'))
    a=ap.parse_args()
    d=make_dump(a.rom,a.tbl)
    raw,header,prg,chrrom,mapper,submapper=load_rom(a.rom)
    seq=[]
    for offset,length,label in CHARSET_SEQUENCE_SPANS:
        chunk=prg[offset:offset+length]
        text=''.join(chr(b) if 0x20<=b<=0x7E else f'<{b:02X}>' for b in chunk)
        seq.append({'id':label,'category':'possible_character_set_or_diagnostic_sequence',
          'confidence':'high for raw printable bytes; purpose and runtime use unconfirmed',
          'offset':{'prg_relative':f'0x{offset:05X}','file_absolute':f'0x{16+offset:05X}',
                    'prg_8k_bank':offset//0x2000,'bank_offset':f'0x{offset%0x2000:04X}',
                    'cpu_address_if_fixed_bank15_at_E000':f'0x{0xE000+(offset%0x2000):04X}'},
          'byte_length':len(chunk),'byte_length_limit':None,
          'length_limit_basis':'Observed contiguous ASCII run only; not an editable text-field capacity.',
          'original_text':text,'display_text_trimmed':text.strip(),'raw_hex':chunk.hex(' ').upper(),
          'interpretation':'Looks like a printable character sweep/lookup or diagnostic sequence. It is not classified as player dialogue.'})
    d['schema_version']='3.0'
    d['bank_mapping_hypothesis']={
       'candidate_table_prg_offset':'0x1DE86','candidate_table_cpu_address':'0xDE86 if PRG bank 14 is mapped at $C000',
       'candidate_table_span':'0x1DE86-0x1E01D including row trailers',
       'support':'NMI $D88D and IRQ/BRK $D92A fit the $C000-$DFFF window and map into PRG bank 14 under this hypothesis; RESET $FFD0 maps into the final fixed bank 15 at $E000-$FFFF. The final row continues from physical bank 14 into bank 15, contiguous as CPU $DFFC-$E01D under that map.',
       'status':'strong static inference; not runtime confirmed'}
    d['coverage']['complete_dialogue_dump']=False
    d['coverage']['complete_dialogue_dump_reason']='Only observed ASCII-like static records and candidate diagnostic/charset sequences have been extracted. Game-specific Japanese tile-ID encoding, controls, pointers, dynamic nametable text, and active bank states remain to be traced.'
    d['charset_sequence_candidates']=seq
    d['runtime_trace_added_in_v3']={
       'tool':'tools/pyokotan_fceux_text_trace.lua',
       'candidate_read_range_cpu':'0xDE86-0xE01D',
       'logs':['candidate text-region data reads','mapper 69 writes in 0x8000-0xBFFF','PPU register writes in 0x2000-0x2007'],
       'status':'capture script supplied but not run in an emulator in this environment'}
    d['next_runtime_steps']=[
       'Run tools/pyokotan_fceux_text_trace.lua in FCEUX while booting from power-on, showing the title/menu, and opening text-bearing screens.',
       'Analyze the resulting CSV with tools/trace_log_analyzer.py; confirm the mapped CPU address and mapper register writes.',
       'Use PPU $2006/$2007 write sequences and data reads to identify the actual text rendering/lookup path.',
       'Only after runtime confirmation, map remaining Japanese tile IDs, control codes, terminators, and actual string limits.',
       'Then extend JSON extraction and plan a separate Vietnamese glyph/CHR patch with a reversible ROM patch script.'
    ]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {a.out}: {len(d["text_records"])} static text/template rows, {len(d["metadata_records"])} metadata records, {len(seq)} character-sequence candidates.')
if __name__=='__main__':main()
