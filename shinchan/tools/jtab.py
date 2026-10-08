J={}
hira="あいうえおかきくけこさしすせそたちつてとなにュねのはひふへほまみむめもらりるれろやゆよわをん"
for i,ch in enumerate(hira): J[0xC0+i]=ch
J[0xEE]='゜';J[0xEF]='゛'
for k,v in zip(range(0xF0,0x100),"!?ー、っゃゅょ〜‥‼「ぇャョ□"): J[k]=v
kata={0x8A:'ア',0x8B:'イ',0x8C:'ウ',0x94:'エ',0x95:'オ',0x96:'カ',0x97:'キ',0x98:'ク',0x99:'コ',0x9A:'サ',0x9B:'シ',
0xA0:'ス',0xA1:'セ',0xA2:'ソ',0xA3:'タ',0xA4:'チ',0xA5:'ッ',0xA6:'テ',0xA7:'ト',0xA8:'ニ',0xA9:'ネ',0xAA:'ハ',0xAB:'ヒ',
0xB0:'▼',0xB1:'ホ',0xB2:'マ',0xB3:'ミ',0xB4:'ム',0xB5:'メ',0xB6:'ラ',0xB7:'リ',0xB8:'ル',0xB9:'レ',0xBA:'ロ',0xBB:'ン',0xBF:'ツ'}
J.update(kata)
J[0x00]='　'
DAK={}
for a,b in zip("かきくけこさしすせそたちつてとはひふへほ","がぎぐげござじずぜぞだぢづでどばびぶべぼ"): DAK[a]=b
for a,b in zip("カキクケコサシスセソタチツテトハヒフヘホウ","ガギグゲゴザジズゼゾダヂヅデドバビブベボヴ"): DAK[a]=b
HAN={'は':'ぱ','ひ':'ぴ','ふ':'ぷ','へ':'ぺ','ほ':'ぽ','ハ':'パ','ヒ':'ピ','フ':'プ','ヘ':'ペ','ホ':'ポ'}
def decode(bs, ctrl=True):
    out=[];i=0
    while i<len(bs):
        b=bs[i]
        if b in (0xEF,0xEE) and i+1<len(bs):
            c=J.get(bs[i+1],'<%02X>'%bs[i+1])
            out.append(DAK.get(c,c+'゛') if b==0xEF else HAN.get(c,c+'゜')); i+=2; continue
        if ctrl:
            if b==0x2F: out.append('/');i+=1;continue
            if b==0x3F: out.append('⏎');i+=1;continue
            if b==0x20: out.append('[WAIT]');i+=1;continue
            if b==0x21: out.append('[TWAIT]');i+=1;continue
            if b==0x30: out.append('[NAME%02X]'%bs[i+1]);i+=2;continue
            if b in (0x31,0x32,0x33): out.append('[VAR%d]'%(b-0x30));i+=1;continue
            if 0x34<=b<=0x38: out.append('[NUM%d]'%(b-0x34));i+=1;continue
        out.append(J.get(b,'<%02X>'%b)); i+=1
    return ''.join(out)
