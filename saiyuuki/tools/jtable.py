"""Tile-code -> character table for the Japanese text engine (font tiles $B0-$FF)."""
KANA={0xB0:' ',0xB1:'!',0xB3:'▼',0xBE:'×',0xC1:'。',0xC4:'、',0xC6:'を',0xC7:'ぁ',0xCB:'元',0xCC:'ゃ',0xCD:'ゅ',0xCE:'ょ',0xCF:'っ',0xD0:'ー',0xFE:'゛',0xFF:'゜',0x70:'·',0x71:'¦'}
for i,c in enumerate('0123456789'): KANA[0xB4+i]=c
for i,c in enumerate('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわん'): KANA[0xD1+i]=c
def dec(bs): return ''.join(KANA.get(b,'<%02X>'%b) for b in bs)
