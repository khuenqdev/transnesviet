#!/usr/bin/env python3
"""Stage 1 – Metalgun Slinger (GBA, AAPJ) Shift-JIS script scanner.
Scans the ROM for runs of valid Shift-JIS text (null-terminated) and dumps
them to TSV/JSON with offset, byte length, terminator and decoded text.
Usage: python sjis_dump.py metal_gunslinger.gba out_prefix [min_jp_chars]"""
import sys, json, csv

def is_lead(b): return 0x81<=b<=0x9F or 0xE0<=b<=0xEF
def is_trail(b): return 0x40<=b<=0xFC and b!=0x7F

def scan(d, min_jp=2):
    res=[]; i=0; n=len(d)
    while i<n:
        j=i; jp=0; ok=True
        while j<n:
            b=d[j]
            if is_lead(b) and j+1<n and is_trail(d[j+1]):
                try: d[j:j+2].decode('cp932'); jp+=1; j+=2; continue
                except: break
            if b in (0x0A,0x0D) or 0x20<=b<0x7F: j+=1; continue
            break
        if jp>=min_jp and j<n and d[j]==0x00:
            raw=d[i:j]
            try:
                t=raw.decode('cp932')
                # filter: require kana/kanji ratio
                kana=sum(1 for c in t if '\u3040'<=c<='\u30ff' or '\u4e00'<=c<='\u9fff' or '\uff00'<=c<='\uffef' or '\u3000'<=c<='\u303f')
                if kana>=min_jp and kana*2>=len(t.replace('\n',''))*0.5:
                    res.append(dict(offset=i,length=len(raw),text=t))
                    i=j+1; continue
            except: pass
        i = j+1 if j>i else i+1
    return res

if __name__=='__main__':
    rom=open(sys.argv[1],'rb').read(); pre=sys.argv[2]
    mj=int(sys.argv[3]) if len(sys.argv)>3 else 2
    r=scan(rom,mj)
    for k,e in enumerate(r): e['id']=k
    json.dump(r,open(pre+'.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    with open(pre+'.tsv','w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t')
        w.writerow(['id','offset','bytes','text_jp','text_vi'])
        for e in r: w.writerow([e['id'],'0x%06X'%e['offset'],e['length'],e['text'].replace('\n','\\n'),''])
    print(len(r),'strings', sum(e['length'] for e in r),'bytes')
