import sys; sys.path.insert(0,'/home/claude/w')
import vfont
NL=0x3F; END=0x2F; PAGE=0x22
def wrap(text, width, maxlines=None):
    out_lines=[]
    for para in text.split('\n'):
        line=''
        for w in para.split(' '):
            cand = w if line=='' else line+' '+w
            if len(cand)<=width: line=cand
            else:
                if line: out_lines.append(line)
                while len(w)>width: out_lines.append(w[:width]); w=w[width:]
                line=w
        out_lines.append(line)
    if maxlines is None: return [out_lines]
    return [out_lines[i:i+maxlines] for i in range(0,len(out_lines),maxlines)]
def enc_line(line):
    b=[]
    for ch in line: b += [0] if ch==' ' else vfont.encode_char(ch)
    return b
def encode(text, width, maxlines, allow_pages=True):
    pages=wrap(text.upper(), width, maxlines)
    if not allow_pages and len(pages)>1: raise ValueError('does not fit: %r'%text)
    out=[]
    for pi,pg in enumerate(pages):
        if pi: out.append(PAGE)
        for li,l in enumerate(pg):
            if li: out.append(NL)
            out+=enc_line(l)
    out.append(END)
    return out, pages
