#!/usr/bin/env python3
"""Stage 3 – Full builder: menu (Stage 2) + story/tutorial/credits (Stage 3).
usage: build_vi.py metal_gunslinger.gba menu_vi.tsv story_vi.txt out.gba [--check]

story_vi.txt format, one message per line:   T0123 | part / part / ...
 * Dialogue messages (JP starts with 「 or 『): each part = one paragraph
   (JP paragraph = line not starting with an ideographic space). Each
   paragraph is word-wrapped into <= the JP paragraph's line count, max 38
   half-width chars per line, continuation lines indented by 1 space;
   unused lines become blank.
 * Other messages (intro*, tutorial, credits, '・' pauses): each part = one
   screen line, count must equal the JP line count. Leading spaces kept.
Text for op29 line i of scene S is written to free space 0x79AA00+ and the
op29 operand is set to (new_addr - scene_base)."""
import sys, json, csv, struct, unicodedata, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from vi_codec import PairCodec
from vi_font import glyph, CHARSET
MAXW=36   # 18 cells: the 19th cell is hidden under the box frame (verified in emulator, Stage 4)
def jp_paragraphs(lines):
    paras=[]
    for l in lines:
        if not l.startswith('\u3000') or not paras: paras.append([l])
        else: paras[-1].append(l)
    return paras
def is_dialogue(m): return m['jp'][0][:1] in '「『' and m['end_op']==0x2A and m['scene']!=45
def wrap(text,k):
    words=text.split(' '); lines=[]; cur=''
    for w in words:
        cand=(cur+' '+w) if cur else w
        lim=MAXW if not lines else MAXW-1
        if len(cand)<=lim: cur=cand
        else:
            if not cur: return None
            lines.append(cur); cur=w
    if cur: lines.append(cur)
    if any(len(l)>(MAXW if i==0 else MAXW-1) for i,l in enumerate(lines)) or len(lines)>k: return None
    # balance: if fits in n lines, try to equalise (min max width) for nicer boxes
    n=len(lines)
    if n>1:
        best=lines; 
        for lim in range(max(len(l) for l in lines)-1, 10, -1):
            t=[];c=''
            for w in words:
                cand=(c+' '+w) if c else w
                if len(cand)<= (lim if not t else lim-1): c=cand
                else:
                    if not c: t=None;break
                    t.append(c);c=w
            if t is None: break
            t.append(c)
            if len(t)>n: break
            best=t
        lines=best
    return [lines[0]]+[' '+l for l in lines[1:]]+['']*(k-len(lines))

def load_story(path):
    out={}
    for ln in open(path,encoding='utf-8'):
        ln=ln.rstrip('\n')
        if not ln.strip() or ln.startswith('#'): continue
        k,_,v=ln.partition(' | ')
        out[k.strip()]=[unicodedata.normalize('NFC',p) for p in v.split(' / ')]
    return out

def layout(m,parts):
    """returns list of screen lines (len == len(m['refs'])) or raises ValueError"""
    if is_dialogue(m):
        jps=jp_paragraphs(m['jp'])
        if len(parts)!=len(jps): raise ValueError(f'paragraphs {len(parts)} != JP {len(jps)}')
        res=[]
        for p,jp in zip(parts,jps):
            w=wrap(p.strip(),len(jp))
            if w is None: raise ValueError(f'overflow ({len(jp)} lines): {p}')
            res+=w
        return res
    if len(parts)!=len(m['jp']): raise ValueError(f'lines {len(parts)} != JP {len(m["jp"])}')
    for p in parts:
        if len(p)>MAXW: raise ValueError(f'line too long {len(p)}: {p}')
    return parts

def build(rom,menu_tsv,story_p,outdir,check=False):
    d=bytearray(rom); base=os.path.dirname(os.path.abspath(story_p))
    M=json.load(open(os.path.join(base,'menu.json'),encoding='utf-8'))
    S=json.load(open(os.path.join(base,'scenes.json'),encoding='utf-8'))
    MSG=json.load(open(os.path.join(base,'messages.json'),encoding='utf-8'))
    sbase={s['id']:s['base'] for s in S}
    used=set(''.join(x['text'] for s in S for x in s['strings']))|set(''.join(m['text'] for m in M))
    story=load_story(story_p); errs=[]; okchars=set(CHARSET)
    for k,parts in story.items():
        bad=set(''.join(parts))-okchars
        if bad: errs.append(f'{k}: no glyph for {"".join(sorted(bad))}')
    laid={}
    for m in MSG:
        if m['mid'] in story:
            try: laid[m['mid']]=layout(m,story[m['mid']])
            except ValueError as e: errs.append(f"{m['mid']}: {e}")
    for m in MSG:   # Stage 4: intro panel lines (scene 1) max 20 chars
        if m['scene']==1 and m['mid'] in laid and m['mid'] not in ('T0012','T0013'):
            for l in laid[m['mid']]:
                if len(l)>20: errs.append(f"{m['mid']}: intro line >20: {l}")
    missing=[m['mid'] for m in MSG if m['mid'] not in story]
    print(f'messages translated {len(laid)}/{len(MSG)}  errors {len(errs)}  missing {len(missing)}')
    for e in errs: print('  ERR',e)
    if check or errs: return None
    codec=PairCodec(rom,used,table_path=os.path.join(outdir,'pair_table.json'))
    codec.table={}; codec.pool=[c for c in reversed(codec.codes) if c>=0x889F and c not in {int.from_bytes(ch.encode('cp932'),'big') for ch in used if len(ch.encode('cp932'))==2}]
    vi={r['id']:r['vi'] for r in csv.DictReader(open(menu_tsv,encoding='utf-8'),delimiter='\t')}
    p=0x6BDBB0
    for i,m in enumerate(M):
        t=vi.get('M%03d'%i)
        if not t: continue
        raw=codec.encode(unicodedata.normalize('NFC',t)); d[p:p+len(raw)+1]=raw+b'\0'
        for r in m['refs']: struct.pack_into('<I',d,r,0x08000000+p)
        p=(p+len(raw)+1+3)&~3
    p=0x79AA00; nlines=0
    for m in MSG:
        if m['mid'] not in laid: continue
        b=sbase[m['scene']]
        for ref,line in zip(m['refs'],laid[m['mid']]):
            raw=codec.encode_line(line if line.strip() else ' ')
            assert p+len(raw)+1<0x800000
            d[p:p+len(raw)+1]=raw+b'\0'; struct.pack_into('<I',d,ref,p-b)
            p=(p+len(raw)+1+3)&~3; nlines+=1
    u32=lambda o: struct.unpack_from('<I',d,o)[0]
    # Stage 4a: re-centre intro text windows (scene 1, opcode 0x67 <x|y<<16> <w|h<<16>)
    for m in MSG:
        if m['scene']!=1 or m['mid'] not in laid: continue
        r0=m['refs'][0]; o=r0-4
        while o>r0-80 and u32(o)!=0x67: o-=4
        if o<=r0-80: continue
        xy=u32(o+4); x=xy&0xFFFF
        if x>15: continue
        cells=max((len(l)+1)//2 for l in laid[m['mid']])
        p0,pw=(96,144) if x>=12 else (0,144)
        nx=max((p0+(pw-cells*12)//2+4)//8,(p0+7)//8)
        while nx*8+cells*12>p0+pw: nx-=1
        struct.pack_into('<I',d,o+4,(xy&0xFFFF0000)|nx)
    # Stage 4b: centred text boxes (opcode 0x77 <width_cells|rows<<16>, 0): width = VI cell count
    for m in MSG:
        if m['mid'] not in laid: continue
        r0=m['refs'][0]
        for o in range(r0-24,r0-4,4):
            if u32(o)==0x77 and u32(o+8)==0:
                v=u32(o+4); cells=max((len(l)+1)//2 for l in laid[m['mid']])
                if cells>20: raise ValueError(m['mid']+': centred line > 40 chars')
                struct.pack_into('<I',d,o+4,(v&0xFFFF0000)|cells)
    codec.write_font(d,glyph); codec.save()
    json.dump(laid,open(os.path.join(outdir,'story_layout.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(f'story lines written {nlines}, story bytes {p-0x79AA00}, pairs {len(codec.table)}, free slots {len(codec.pool)}')
    return d

if __name__=='__main__':
    rom_p,menu_tsv,story_p,out=sys.argv[1:5]
    d=build(open(rom_p,'rb').read(),menu_tsv,story_p,os.path.dirname(os.path.abspath(out)),'--check' in sys.argv)
    if d is None: sys.exit(0 if '--check' in sys.argv else 1)
    open(out,'wb').write(d)
