# Minimal two-pass 6502 assembler (labels, .DB/.DW, <lo >hi, +/- expressions)
import re, sys
sys.path.insert(0, '/home/claude/w')
from nes import OPS
REV = {}
for op, (mode, name, cyc) in OPS.items():
    if name != 'ILL': REV[(name, mode)] = op
SZ = {'imp':1,'acc':1,'imm':2,'zp':2,'zpx':2,'zpy':2,'izx':2,'izy':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
BRANCH = {'BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'}
def assemble(src, org, labels=None):
    ext = dict(labels or {}); lines=[]
    for raw in src.split('\n'):
        line = raw.split(';')[0].rstrip()
        if line.strip(): lines.append(line)
    def val(expr, labs, p2):
        expr = expr.strip(); lo=hi=False
        if expr.startswith('<'): lo=True; expr=expr[1:]
        elif expr.startswith('>'): hi=True; expr=expr[1:]
        total=0
        for sign, term in re.findall(r'([+-]?)\s*([^+-]+)', expr):
            term=term.strip()
            if term.startswith('$'): v=int(term[1:],16)
            elif term.isdigit(): v=int(term)
            elif term in labs: v=labs[term]
            elif term in ext: v=ext[term]
            else:
                if p2: raise KeyError('undefined label '+term)
                v=0x8000
            total += -v if sign=='-' else v
        if lo: total&=0xFF
        if hi: total=(total>>8)&0xFF
        return total
    labs={}
    for pss in (1,2):
        pc=org; out=bytearray()
        for line in lines:
            m=re.match(r'^([A-Za-z_]\w*):(.*)$', line.strip())
            if m:
                if pss==1: labs[m.group(1)]=pc
                line=m.group(2)
                if not line.strip(): continue
            parts=line.strip().split(None,1)
            mn=parts[0].upper(); arg=parts[1].strip() if len(parts)>1 else ''
            if mn=='.DB':
                for a in arg.split(','): out.append(val(a,labs,pss==2)&0xFF); pc+=1
                continue
            if mn=='.DW':
                for a in arg.split(','):
                    v=val(a,labs,pss==2); out+=bytes([v&0xFF,v>>8]); pc+=2
                continue
            if mn in BRANCH:
                t=val(arg,labs,pss==2); off=t-(pc+2)
                if pss==2 and not -128<=off<=127: raise ValueError('branch out of range: '+line)
                out+=bytes([REV[(mn,'rel')],off&0xFF]); pc+=2; continue
            if arg=='' or arg.upper()=='A':
                mode='acc' if (mn,'acc') in REV and arg.upper()=='A' else 'imp'
                if (mn,mode) not in REV: mode='acc'
                out.append(REV[(mn,mode)]); pc+=1; continue
            if arg.startswith('#'):
                v=val(arg[1:],labs,pss==2); out+=bytes([REV[(mn,'imm')],v&0xFF]); pc+=2; continue
            m=re.match(r'^\((.+)\),\s*[Yy]$',arg)
            if m: v=val(m.group(1),labs,pss==2); out+=bytes([REV[(mn,'izy')],v]); pc+=2; continue
            m=re.match(r'^\((.+),\s*[Xx]\)$',arg)
            if m: v=val(m.group(1),labs,pss==2); out+=bytes([REV[(mn,'izx')],v]); pc+=2; continue
            m=re.match(r'^\((.+)\)$',arg)
            if m: v=val(m.group(1),labs,pss==2); out+=bytes([REV[(mn,'ind')],v&0xFF,v>>8]); pc+=3; continue
            idx=None
            m=re.match(r'^(.+),\s*([XxYy])$',arg)
            if m: arg,idx=m.group(1),m.group(2).upper()
            v=val(arg,labs,pss==2)
            zp_ok = v<0x100 and not re.search(r'[A-Za-z_]',arg.replace('$',''))
            if idx is None: mode='zp' if zp_ok and (mn,'zp') in REV else 'abs'
            elif idx=='X': mode='zpx' if zp_ok and (mn,'zpx') in REV else 'abx'
            else: mode='zpy' if zp_ok and (mn,'zpy') in REV else 'aby'
            op=REV[(mn,mode)]
            out+= bytes([op,v&0xFF]) if SZ[mode]==2 else bytes([op,v&0xFF,v>>8])
            pc+=SZ[mode]
    return bytes(out), labs
