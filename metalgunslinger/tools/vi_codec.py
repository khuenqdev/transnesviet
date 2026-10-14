#!/usr/bin/env python3
"""Stage 2 – Vietnamese pair encoder (DTE-in-font).
Text is split per line into 2-char pairs; each distinct pair gets one unused
glyph slot of the game's 12x12 SJIS font. The slot's bitmap is overwritten
with the two 6-px Vietnamese glyphs; the text stores the slot's SJIS code.
Pair table is persistent (pair_table.json) so later stages extend it.
Slot pool: kanji codes >=0x889F NOT used by any original Japanese text,
highest codes (JIS level 2) first."""
import json, struct, os, unicodedata
FONT_COUNT_OFF,CODES,GLY,GS=0x433AE0,0x433AE4,0x437132,24

class PairCodec:
    def __init__(self, rom, used_chars, table_path='pair_table.json'):
        self.rom=rom; self.path=table_path
        n=struct.unpack_from('<H',rom,FONT_COUNT_OFF)[0]
        self.codes=list(struct.unpack_from('<%dH'%n,rom,CODES))
        self.index={c:i for i,c in enumerate(self.codes)}
        used_codes={int.from_bytes(ch.encode('cp932'),'big') for ch in used_chars if len(ch.encode('cp932'))==2}
        self.pool=[c for c in reversed(self.codes) if c>=0x889F and c not in used_codes]
        self.table={}
        if os.path.exists(table_path):
            self.table={k:int(v,16) for k,v in json.load(open(table_path,encoding='utf-8')).items()}
        taken=set(self.table.values()); self.pool=[c for c in self.pool if c not in taken]
    @staticmethod
    def norm(t): return unicodedata.normalize('NFC',t)
    def encode_line(self,line):
        line=self.norm(line)
        if len(line)%2: line+=' '
        out=b''
        for i in range(0,len(line),2):
            p=line[i:i+2]
            if p not in self.table:
                if not self.pool: raise RuntimeError('out of font slots')
                self.table[p]=self.pool.pop(0)
            out+=struct.pack('>H',self.table[p])
        return out
    def encode(self,text,nl=b'\r'):
        return nl.join(self.encode_line(l) for l in text.split('<br>'))
    def write_font(self,rom_out,glyph_fn):
        for p,code in self.table.items():
            L,R=glyph_fn(p[0]),glyph_fn(p[1]); i=self.index[code]; raw=b''
            for y in range(12):
                bits=0
                for x in range(6):
                    if L[y][x]: bits|=1<<(15-x)
                    if R[y][x]: bits|=1<<(9-x)
                raw+=struct.pack('>H',bits)
            rom_out[GLY+i*GS:GLY+(i+1)*GS]=raw
    def save(self):
        json.dump({k:'%04X'%v for k,v in self.table.items()},open(self.path,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
