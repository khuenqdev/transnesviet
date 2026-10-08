# Core build: PRG expansion 128->256 KB, dialogue engine patches, text bank, font
import sys
sys.path.insert(0, '/home/claude/w')
from asm6502 import assemble
import vfont, encoder, tr
from extract import groups, rd, G
from jtab import decode
ORIG = open('/home/claude/w/orig.nes', 'rb').read()
HDR = bytearray(ORIG[:16]); OPRG = ORIG[16:16+0x20000]; OCHR = ORIG[16+0x20000:]
NB = 16; TEXTBANK = 8; FIXED = 15
banks = [bytearray(OPRG[i*0x4000:(i+1)*0x4000]) for i in range(8)]
while len(banks) < NB:
    b = bytearray([0xFF])*0x4000; b[0] = len(banks); banks.append(b)
banks[15] = bytearray(OPRG[7*0x4000:8*0x4000])      # fixed bank stays the last one
def put(bank, addr, data):
    base = 0xC000 if bank == FIXED else 0x8000; o = addr-base
    assert 0 <= o and o+len(data) <= 0x4000, (bank, hex(addr), len(data))
    banks[bank][o:o+len(data)] = bytes(data)
def get(bank, addr, n=1):
    base = 0xC000 if bank == FIXED else 0x8000
    return bytes(banks[bank][addr-base:addr-base+n])
def expect(bank, addr, hexstr):
    want = bytes.fromhex(hexstr)
    assert get(bank, addr, len(want)) == want, (bank, hex(addr), get(bank, addr, len(want)).hex(), hexstr)
# ---- fixed bank trampolines (bank-switch to text bank and back)
FREE15 = 0xFB90
fixed_code, FL = assemble("""
TF:     LDA #$08
        STA $8008
        JSR $8808
        LDA #$03
        STA $8008
        RTS
TP:     LDA #$08
        STA $8008
        JSR $89D9
        LDA #$03
        STA $8008
        RTS
""", FREE15)
put(FIXED, FREE15, fixed_code)
# ---- bank 3 engine extensions (placed in the freed old text area)
NEW3 = 0x8C20
b3code, L3 = assemble("""
NEWCHK: CMP #$22
        BNE NC1
        LDA #$11
        STA $0600
        DEC $063D
        RTS
NC1:    CMP #$F0
        BCC NC2
        JMP $85F9
NC2:    JMP $862F
DISPX:  CMP #$11
        BNE DX1
        JSR PAGEWAIT
DX1:    JMP $8514
PAGEWAIT:
        JSR $80E4
        LDA $85
        ORA $87
        AND #$01
        BEQ PW1
        LDA #$A5
        STA $0670
        LDA #$09
        STA $061C
        LDA #$04
        STA $0600
PW1:    RTS
PBEND:  LDA $0670
        CMP #$A5
        BNE PB1
        LDA #$00
        STA $0670
        LDA #$03
        STA $0600
        LDA $0605
        STA $0603
        LDA $0606
        STA $0604
        LDA #$00
        STA $061B
        LDA #$02
        STA $061C
        RTS
PB1:    LDA #$80
        STA $0600
        RTS
CLRF:   LDA #$00
        STA $0670
        LDA #$04
        STA $0600
        RTS
CLR0:   LDA #$00
        STA $0607
        STA $0670
        RTS
""", NEW3)
put(3, NEW3, b3code); NEW3_END = NEW3+len(b3code)
def patch3(addr, orig_hex, src):
    expect(3, addr, orig_hex)
    code, _ = assemble(src, addr, {**L3, **FL})
    assert len(code) <= len(bytes.fromhex(orig_hex)), (hex(addr), code.hex())
    put(3, addr, code)
patch3(0x85B6, '200888', 'JSR TF')
patch3(0x8521, '20D989', 'JSR TP')
patch3(0x85EF, 'C9EFF006C9EEF002D036', 'JMP NEWCHK')
patch3(0x850D, 'C9A0D0034C1485', 'JMP DISPX')
patch3(0x8ACD, 'A9808D000660', 'JMP PBEND')
patch3(0x81C9, 'A9048D0006', 'JSR CLRF\nNOP\nNOP')
patch3(0x81DD, 'A90A', 'LDA #$0B')
patch3(0x82A2, 'A9048D0006', 'JSR CLRF\nNOP\nNOP')
patch3(0x8147, 'A94B', 'LDA #$84')
patch3(0x815B, 'A917', 'LDA #$18')
patch3(0x816A, 'A9008D0706', 'JSR CLR0\nNOP\nNOP')
patch3(0x81A1, 'A9008D0706', 'JSR CLR0\nNOP\nNOP')
patch3(0x80F8, 'A919', 'LDA #$3B')
patch3(0x8151, 'A928', 'LDA #$50')
patch3(0x811A, 'A928', 'LDA #$C0')
# ---- text bank
banks[TEXTBANK][0] = TEXTBANK
put(TEXTBANK, 0x87E9, get(3, 0x87E9, 0x8A43-0x87E9))
expect(TEXTBANK, 0x897A, 'C9EFF004C9EED038')
put(TEXTBANK, 0x897A, bytes.fromhex('C9F0B004903AEAEA'))
class Alloc:
    def __init__(s, start, end): s.p=start; s.end=end; s.cache={}
    def add(s, data, dedupe=True):
        data=bytes(data)
        if dedupe and data in s.cache: return s.cache[data]
        a=s.p; assert a+len(data) <= s.end, 'text bank full'
        put(TEXTBANK, a, data); s.p += len(data)
        if dedupe: s.cache[data]=a
        return a
DATA = 0x8A50; al = Alloc(DATA, 0xC000)
grp_tab = al.add(bytes(14), False)
sub_tabs = [al.add(bytes(2*len(groups[g])), False) for g in range(7)]
name_tab = al.add(bytes(2*len(tr.NAMES)), False)
for g in range(7): put(TEXTBANK, grp_tab+2*g, bytes([sub_tabs[g]&0xFF, sub_tabs[g]>>8]))
for i, nm in enumerate(tr.NAMES):
    b=[]
    for ch in nm.upper(): b += [0xEF] if ch==' ' else vfont.encode_char(ch)
    a=al.add(b+[0]); put(TEXTBANK, name_tab+2*i, bytes([a&0xFF, a>>8]))
expect(TEXTBANK, 0x89D9, 'A91A8502A98C8503'); put(TEXTBANK, 0x89D9, bytes([0xA9,grp_tab&0xFF,0x85,0x02,0xA9,grp_tab>>8,0x85,0x03]))
expect(TEXTBANK, 0x8A17, 'A9698500A98B8501'); put(TEXTBANK, 0x8A17, bytes([0xA9,name_tab&0xFF,0x85,0x00,0xA9,name_tab>>8,0x85,0x01]))
STATS = {'pages': {}}
empty = al.add([encoder.END])
for g in range(7):
    for i, p in enumerate(groups[g]):
        if p in G: a = empty
        else:
            s = decode(rd(p))
            if s in ('[VAR1]/','[VAR2]/','[VAR3]/'): a = al.add([0x30+int(s[4]), encoder.END])
            elif p in tr.D: bts,pg = encoder.encode(tr.D[p],23,3); a=al.add(bts); STATS['pages'][p]=len(pg)
            elif p in tr.D1: bts,pg = encoder.encode(tr.D1[p],14,1,False); a=al.add(bts)
            elif p in tr.D1BIG: bts,pg = encoder.encode(tr.D1BIG[p],22,3,False); a=al.add(bts)
            else: raise KeyError(hex(p))
        put(TEXTBANK, sub_tabs[g]+2*i, bytes([a&0xFF, a>>8]))
STATS['textbank_used'] = al.p-DATA
for a in range(NEW3_END, 0xB0FF): banks[3][a-0x8000] = 0xFF
FREE3 = NEW3_END
CHR = vfont.build_chr(OCHR)
def assemble_rom():
    hdr = bytearray(HDR); hdr[4] = NB & 0xFF; hdr[9] = (hdr[9]&0xF0) | (NB>>8)
    return bytes(hdr)+b''.join(bytes(b) for b in banks)+bytes(CHR)
