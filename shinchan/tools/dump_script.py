# Export original Japanese + Vietnamese translation side by side (TSV)
import sys; sys.path.insert(0,'/home/claude/w')
from extract import groups,rd,G
from jtab import decode
import tr
seen=set()
with open('script_ja_vi.tsv','w',encoding='utf-8') as f:
    f.write('addr\ttype\tjapanese\tvietnamese\n')
    for g in range(7):
        for p in groups[g]:
            if p in G or p in seen: continue
            seen.add(p); ja=decode(rd(p))
            if ja.startswith('[VAR') and ja.endswith(']/'): continue
            kind,vi=('story',tr.D[p]) if p in tr.D else ('bubble',tr.D1[p]) if p in tr.D1 else ('clear',tr.D1BIG[p])
            f.write('%04X\t%s\t%s\t%s\n'%(p,kind,ja,vi))
print(len(seen))
