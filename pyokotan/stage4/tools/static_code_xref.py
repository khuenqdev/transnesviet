#!/usr/bin/env python3
"""Best-effort 6502 reachable-code disassembly and cross-reference audit.

Assumed initial map: PRG bank 14 at CPU $C000-$DFFF; last bank at $E000-$FFFF.
Because mapper state can change dynamically, results are an investigation aid,
not a proof that every decoded instruction is executed as shown.
"""
from __future__ import annotations
import argparse, csv, json, hashlib, zlib
from pathlib import Path

# Official and commonly-seen unofficial NMOS 6502 opcodes, arranged by opcode.
# Modes: imp, acc, imm, zp, zpx, zpy, abs, absx, absy, ind, indx, indy, rel.
ROWS = [
"BRK:imp ORA:indx KIL:imp SLO:indx NOP:zp ORA:zp ASL:zp SLO:zp PHP:imp ORA:imm ASL:acc ANC:imm NOP:abs ORA:abs ASL:abs SLO:abs",
"BPL:rel ORA:indy KIL:imp SLO:indy NOP:zpx ORA:zpx ASL:zpx SLO:zpx CLC:imp ORA:absy NOP:imp SLO:absy NOP:absx ORA:absx ASL:absx SLO:absx",
"JSR:abs AND:indx KIL:imp RLA:indx BIT:zp AND:zp ROL:zp RLA:zp PLP:imp AND:imm ROL:acc ANC:imm BIT:abs AND:abs ROL:abs RLA:abs",
"BMI:rel AND:indy KIL:imp RLA:indy NOP:zpx AND:zpx ROL:zpx RLA:zpx SEC:imp AND:absy NOP:imp RLA:absy NOP:absx AND:absx ROL:absx RLA:absx",
"RTI:imp EOR:indx KIL:imp SRE:indx NOP:zp EOR:zp LSR:zp SRE:zp PHA:imp EOR:imm LSR:acc ALR:imm JMP:abs EOR:abs LSR:abs SRE:abs",
"BVC:rel EOR:indy KIL:imp SRE:indy NOP:zpx EOR:zpx LSR:zpx SRE:zpx CLI:imp EOR:absy NOP:imp SRE:absy NOP:absx EOR:absx LSR:absx SRE:absx",
"RTS:imp ADC:indx KIL:imp RRA:indx NOP:zp ADC:zp ROR:zp RRA:zp PLA:imp ADC:imm ROR:acc ARR:imm JMP:ind ADC:abs ROR:abs RRA:abs",
"BVS:rel ADC:indy KIL:imp RRA:indy NOP:zpx ADC:zpx ROR:zpx RRA:zpx SEI:imp ADC:absy NOP:imp RRA:absy NOP:absx ADC:absx ROR:absx RRA:absx",
"NOP:imm STA:indx NOP:imm SAX:indx STY:zp STA:zp STX:zp SAX:zp DEY:imp NOP:imm TXA:imp XAA:imm STY:abs STA:abs STX:abs SAX:abs",
"BCC:rel STA:indy KIL:imp AHX:indy STY:zpx STA:zpx STX:zpy SAX:zpy TYA:imp STA:absy TXS:imp TAS:absy SHY:absx STA:absx SHX:absy AHX:absy",
"LDY:imm LDA:indx LDX:imm LAX:indx LDY:zp LDA:zp LDX:zp LAX:zp TAY:imp LDA:imm TAX:imp LAX:imm LDY:abs LDA:abs LDX:abs LAX:abs",
"BCS:rel LDA:indy KIL:imp LAX:indy LDY:zpx LDA:zpx LDX:zpy LAX:zpy CLV:imp LDA:absy TSX:imp LAS:absy LDY:absx LDA:absx LDX:absy LAX:absy",
"CPY:imm CMP:indx NOP:imm DCP:indx CPY:zp CMP:zp DEC:zp DCP:zp INY:imp CMP:imm DEX:imp AXS:imm CPY:abs CMP:abs DEC:abs DCP:abs",
"BNE:rel CMP:indy KIL:imp DCP:indy NOP:zpx CMP:zpx DEC:zpx DCP:zpx CLD:imp CMP:absy NOP:imp DCP:absy NOP:absx CMP:absx DEC:absx DCP:absx",
"CPX:imm SBC:indx NOP:imm ISC:indx CPX:zp SBC:zp INC:zp ISC:zp INX:imp SBC:imm NOP:imp SBC:imm CPX:abs SBC:abs INC:abs ISC:abs",
"BEQ:rel SBC:indy KIL:imp ISC:indy NOP:zpx SBC:zpx INC:zpx ISC:zpx SED:imp SBC:absy NOP:imp ISC:absy NOP:absx SBC:absx INC:absx ISC:absx",
]
OP={}
for ri,row in enumerate(ROWS):
    cells=row.split()
    assert len(cells)==16,(ri,len(cells))
    for ci,c in enumerate(cells):
        m,mode=c.split(':'); OP[ri*16+ci]=(m,mode)
LEN={'imp':1,'acc':1,'imm':2,'zp':2,'zpx':2,'zpy':2,'abs':3,'absx':3,'absy':3,'ind':3,'indx':2,'indy':2,'rel':2}
BRANCHES={'BCC','BCS','BEQ','BMI','BNE','BPL','BVC','BVS'}
TERMINATORS={'RTS','RTI','BRK','KIL'}
ABS_MODES={'abs','absx','absy','ind'}

class Mapper:
    def __init__(self, prg): self.prg=prg
    def phys(self, cpu):
        if 0xC000 <= cpu <= 0xDFFF: return 14*0x2000+(cpu-0xC000)
        if 0xE000 <= cpu <= 0xFFFF: return 15*0x2000+(cpu-0xE000)
        return None
    def byte(self, cpu):
        off=self.phys(cpu & 0xFFFF)
        return self.prg[off] if off is not None and off<len(self.prg) else None

def fmt_operand(mn, mode, raw, pc):
    b1=raw[1] if len(raw)>1 else 0; b2=raw[2] if len(raw)>2 else 0
    val=b1 | (b2<<8)
    if mode=='imp': return ''
    if mode=='acc': return 'A'
    if mode=='imm': return f'#$%02X'%b1
    if mode=='zp': return f'$%02X'%b1
    if mode=='zpx': return f'$%02X,X'%b1
    if mode=='zpy': return f'$%02X,Y'%b1
    if mode=='abs': return f'$%04X'%val
    if mode=='absx': return f'$%04X,X'%val
    if mode=='absy': return f'$%04X,Y'%val
    if mode=='ind': return f'($%04X)'%val
    if mode=='indx': return f'($%02X,X)'%b1
    if mode=='indy': return f'($%02X),Y'%b1
    if mode=='rel':
        target=(pc+2+(b1 if b1<128 else b1-256))&0xFFFF
        return f'$%04X'%target
    return '?'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rom',type=Path); ap.add_argument('--outdir',type=Path,default=Path('outputs'))
    ap.add_argument('--max-instructions',type=int,default=12000)
    a=ap.parse_args(); raw=a.rom.read_bytes()
    if raw[:4]!=b'NES\x1a': raise SystemExit('Not an iNES ROM')
    header=raw[:16]; prg_size=(header[4]|((header[9]&15)<<8))*0x4000
    prg=raw[16:16+prg_size]
    if len(prg)!=0x20000: raise SystemExit(f'Expected 128 KiB PRG; found {len(prg)} bytes')
    mp=Mapper(prg)
    vec={'nmi':int.from_bytes(prg[-6:-4],'little'),'reset':int.from_bytes(prg[-4:-2],'little'),'irq_brk':int.from_bytes(prg[-2:],'little')}
    # Reset vector, reset's statically observed JMP target, and interrupt handlers.
    seeds=[('reset_vector',vec['reset']),('nmi_vector',vec['nmi']),('irq_brk_vector',vec['irq_brk']),('reset_jump_target',0xD800)]
    todo=[pc for name,pc in seeds if mp.phys(pc) is not None]
    seen={}; edges=[]; refs=[]; stop_reasons={}
    while todo and len(seen)<a.max_instructions:
        pc=todo.pop()
        if pc in seen or mp.phys(pc) is None: continue
        rawins=[]
        opcode=mp.byte(pc)
        if opcode is None: continue
        mn,mode=OP[opcode]; n=LEN[mode]
        for k in range(n):
            bv=mp.byte((pc+k)&0xFFFF)
            rawins.append(0 if bv is None else bv)
        operand=fmt_operand(mn,mode,rawins,pc)
        target=None
        if mode=='rel': target=(pc+2+(rawins[1] if rawins[1]<128 else rawins[1]-256))&0xFFFF
        elif mode in ABS_MODES: target=rawins[1]|(rawins[2]<<8)
        phys=mp.phys(pc)
        row={'cpu_address':f'0x{pc:04X}','prg_offset':f'0x{phys:05X}','opcode':f'{opcode:02X}','bytes':' '.join(f'{x:02X}' for x in rawins),
             'mnemonic':mn,'mode':mode,'operand':operand,'target':f'0x{target:04X}' if target is not None else None}
        seen[pc]=row
        nextpc=(pc+n)&0xFFFF
        # Direct absolute-address references into the confirmed literal table payload/trailers.
        if mode in ABS_MODES and target is not None and ((0xDE86<=target<=0xDFFF) or (0xE000<=target<=0xE01D)):
            refs.append({'source_cpu':f'0x{pc:04X}','source_prg':f'0x{phys:05X}','mnemonic':mn,'mode':mode,'target_cpu':f'0x{target:04X}','operand':operand,
                         'target_kind':'fixed_ascii_table_or_2byte_trailer','confidence':'static direct operand in reachable-code candidate'})
        # Mapper 69 writes in code may change mapping; retain as findings.
        if mn=='STA' and mode in ('abs','absx','absy') and target is not None and 0x8000<=target<=0xBFFF:
            refs.append({'source_cpu':f'0x{pc:04X}','source_prg':f'0x{phys:05X}','mnemonic':mn,'mode':mode,'target_cpu':f'0x{target:04X}','operand':operand,
                         'target_kind':'potential_mapper_command_or_data_write','confidence':'address decode is broad; value may come from a register'})
        # Follow flow graph within the two bank windows whose mapping is modeled.
        if mn in TERMINATORS:
            continue
        if mn=='JMP':
            if mode=='abs' and target is not None and mp.phys(target) is not None:
                edges.append({'from':f'0x{pc:04X}','kind':'jmp','to':f'0x{target:04X}'})
                todo.append(target)
            else:
                stop_reasons[f'{pc:04X}']='indirect_or_unmapped_jmp'
            continue
        if mn=='JSR' and target is not None:
            edges.append({'from':f'0x{pc:04X}','kind':'jsr','to':f'0x{target:04X}'})
            if mp.phys(target) is not None: todo.append(target)
            else: stop_reasons[f'{pc:04X}']='jsr_target_outside_static_windows'
            if mp.phys(nextpc) is not None: todo.append(nextpc)
            continue
        if mn in BRANCHES:
            if target is not None and mp.phys(target) is not None:
                edges.append({'from':f'0x{pc:04X}','kind':'branch','to':f'0x{target:04X}'})
                todo.append(target)
            if mp.phys(nextpc) is not None: todo.append(nextpc)
            continue
        if mp.phys(nextpc) is not None: todo.append(nextpc)
    # Make table row audit independently of code reachability.
    table_rows=[]; start=0x1DE86; stride=0x22
    for i in range(12):
        off=start+i*stride; payload=prg[off:off+0x20]; trailer=prg[off+0x20:off+0x22]
        phys_addr=off
        cpu=0xC000+(off-14*0x2000) if off<15*0x2000 else 0xE000+(off-15*0x2000)
        trailer_word=int.from_bytes(trailer,'little')
        table_rows.append({'row':i,'prg_offset':f'0x{off:05X}','file_offset':f'0x{off+16:05X}',
          'cpu_start_under_reset_map':f'0x{cpu:04X}','cpu_payload_range':f'0x{cpu:04X}-0x{cpu+31:04X}',
          'payload_length':len(payload),'text_ascii':payload.decode('ascii','replace'),
          'trimmed':payload.decode('ascii','replace').strip(),'payload_hex':payload.hex(' ').upper(),
          'trailer_offset':f'0x{off+32:05X}','trailer_hex':trailer.hex(' ').upper(),'trailer_word_le':f'0x{trailer_word:04X}',
          'trailer_explanation':'unresolved two-byte value; do not treat as pointer until code reference confirms'})
    outdir=a.outdir; outdir.mkdir(parents=True,exist_ok=True)
    ins_list=sorted(seen.values(),key=lambda x:int(x['cpu_address'],16))
    (outdir/'pyokotan_reachable_disassembly_v4.json').write_text(json.dumps({'schema_version':'1.0','rom':a.rom.name,'rom_sha1':hashlib.sha1(raw).hexdigest(),'assumed_mapping':'bank 14 at $C000-$DFFF; bank 15 fixed at $E000-$FFFF','entry_seeds':[{'label':n,'cpu_address':f'0x{pc:04X}'} for n,pc in seeds], 'instruction_count':len(ins_list),'instructions':ins_list,'edges':edges,'stop_reasons':stop_reasons,'limitations':['6502 control-flow traversal is best-effort','bank switches may invalidate static CPU-to-PRG mapping after mapper writes','indirect jumps/calls and data-driven dispatch are unresolved']},indent=2)+'\n',encoding='utf-8')
    with (outdir/'pyokotan_reachable_disassembly_v4.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['cpu_address','prg_offset','opcode','bytes','mnemonic','mode','operand','target']);w.writeheader();w.writerows(ins_list)
    (outdir/'pyokotan_code_xrefs_v4.json').write_text(json.dumps({'schema_version':'1.0','rom_sha1':hashlib.sha1(raw).hexdigest(),'reference_count':len(refs),'references':refs,'summary':{'direct_references_to_candidate_ascii_table_or_trailers':sum(x['target_kind']=='fixed_ascii_table_or_2byte_trailer' for x in refs),'potential_mapper_writes':sum(x['target_kind']=='potential_mapper_command_or_data_write' for x in refs)},'limitations':['Only code reachable from seed vectors and reset JMP is traversed.','Data references made through zero-page pointers are not fully recovered.','Unmapped windows $8000-$BFFF and indirect dispatch are not traced.']},indent=2)+'\n',encoding='utf-8')
    (outdir/'pyokotan_fixed_table_row_audit_v4.json').write_text(json.dumps({'schema_version':'1.0','rom_sha1':hashlib.sha1(raw).hexdigest(),'table_prg_start':'0x1DE86','stride_bytes':34,'payload_bytes':32,'row_count':12,'mapping_basis':'reset routine writes mapper command $0B / data $1E; mapper 69 command $0B selects $C000 PRG bank; with 16 PRG banks wired, $1E resolves to bank 14. Last bank is fixed at $E000.','rows':table_rows},indent=2)+'\n',encoding='utf-8')
    summary={'rom':a.rom.name,'rom_sha1':hashlib.sha1(raw).hexdigest(),'mapper':69,'prg_8k_banks':16,'startup_bytes_at_FFD0':prg[0x1FFD0:0x1FFDD].hex(' ').upper(),'startup_disassembly_observed':'LDA #$0B; STA $8000; LDA #$1E; STA $A000; JMP $D800','mapper69_interpretation':'Command $0B selects PRG bank register for $C000-$DFFF; data $1E maps to physical bank 14 on a 16-bank image. $E000-$FFFF is fixed to final bank.','instructions_decoded':len(ins_list),'cross_references_found':len(refs),'table_data_direct_operands':sum(x['target_kind']=='fixed_ascii_table_or_2byte_trailer' for x in refs),'potential_mapper_writes':sum(x['target_kind']=='potential_mapper_command_or_data_write' for x in refs),'table_rows':table_rows,'conclusion':'Initial reset mapping is now strongly corroborated by actual mapper setup code, not only vector inference. This still does not prove how all strings are consumed or decode Japanese text.','sources':[{'title':'NESdev Wiki: Sunsoft FME-7 / Mapper 69','url':'https://www.nesdev.org/wiki/INES_Mapper_069'},{'title':'NES specs cartridge/mappers reference','url':'https://github.com/RigleGit/nes-specs/blob/main/cartridgesandmappers.md'}]}
    (outdir/'pyokotan_stage4_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'instruction_count':len(ins_list),'reference_count':len(refs),'table_direct_refs':summary['table_data_direct_operands'],'mapper_writes':summary['potential_mapper_writes'],'outdir':str(outdir)},indent=2))
if __name__=='__main__': main()
