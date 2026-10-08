#!/usr/bin/env python3
from pathlib import Path
import importlib.util, hashlib, zlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=ROOT/'base'/'Ninja Gaiden II - The Dark Sword of Chaos (USA).nes'
REF=ROOT/'reference'
REL=ROOT/'release'
DATA=HERE/'translation_data.py'

spec=importlib.util.spec_from_file_location('data',DATA); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
T=mod.T; VI_MAP=mod.VI_MAP
UP={chr(65+i):1+i for i in range(26)}; LO={chr(97+i):0x21+i for i in range(26)}
P={' ':0x3F,'!':0x41,'"':0x42,"'":0x45,',':0x4C,'-':0x4D,'.':0x4E,'/':0x4F,':':0x5A,'?':0x5F,'&':0x46,'%':0x47,'(':0x48,')':0x49,'*':0x4A,'+':0x4B,'$':0x44,'<':0x5C,'>':0x5E,'[':0x1B,']':0x1D,'_':0x63,'=':0xA0,'^':0xA1,'¨':0x65}
ROOT2=ROOT/'reference'/'spanish_extracted'
SRC=ROOT2/'ninjagaideniithedarkswordofchaosnesAlt2.ext'

def enc(s):
 import unicodedata
 out=bytearray(); i=0
 while i<len(s):
  if s[i]=='~':
   j=s.find('~',i+1); out.append(int(s[i+1:j],16)); i=j+1; continue
  ch=s[i]
  if ch in UP: out.append(UP[ch])
  elif ch in LO: out.append(LO[ch])
  elif ch in VI_MAP: out.append(VI_MAP[ch])
  elif ch=='Đ': out.append(UP['D'])
  elif ch=='đ': out.append(VI_MAP['đ'])
  elif ch in P: out.append(P[ch])
  else:
   b=''.join(c for c in unicodedata.normalize('NFD',ch) if unicodedata.category(c)!='Mn')
   if b in UP: out.append(UP[b])
   elif b in LO: out.append(LO[b])
   else: raise ValueError(f'no mapping {ch!r}')
  i+=1
 return bytes(out)

def entries():
 result=[]; cur=None
 for line in SRC.read_text(encoding='utf-8').splitlines():
  m=__import__('re').match(r';([0-9A-F]+)\{.*\}#\d+#(\d+)',line)
  if m: result.append((int(m.group(1),16),int(m.group(2))))
 return result

def text_only():
 base=BASE.read_bytes(); d=bytearray(base)
 for addr,cap in entries():
  if addr>=0x15BD1: continue
  s=T[f'{addr:08X}']; e=enc(s)
  if len(e)>cap: raise ValueError(f'{addr:X}: overflow {len(e)}/{cap}')
  d[addr:addr+cap]=e[:-1]+bytes([0x3F])*(cap-len(e))+bytes([0xA6])
 # English PRESENTS labels.
 presents=bytes(UP[c] for c in 'PRESENTS')
 for a in (0x85A6,0x85B7): d[a:a+8]=presents
 # Font.
 for code,ch in sorted(VI_MAP.items(), key=lambda kv:kv[1]):
  code=ch; tile=0x40+code; start=0x20010+tile*16
  # already present in source final builder: copy current bytes from final later
  pass
 return d

def apply_font(d):
 # Copy the custom glyph payload from the already-generated full build, preserving its exact bytes.
 full=(REL/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.nes').read_bytes()
 for code in sorted(VI_MAP.values()):
  st=0x20010+(0x40+code)*16; d[st:st+16]=full[st:st+16]

def ips(old,new):
 out=bytearray(b'PATCH'); i=0
 while i<len(old):
  if old[i]==new[i]: i+=1; continue
  s=i; i+=1
  while i<len(old) and old[i]!=new[i] and i-s<0xFF00: i+=1
  out += s.to_bytes(3,'big')+ (i-s).to_bytes(2,'big') + new[s:i]
 out += b'EOF'; return bytes(out)

def main():
 d=text_only(); apply_font(d)
 out=REL/'Ninja_Gaiden_II_Vietnamese_Text.nes'; out.write_bytes(d)
 (REL/'Ninja_Gaiden_II_Vietnamese_Text.ips').write_bytes(ips(BASE.read_bytes(),d))
 final=bytearray((REL/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.nes').read_bytes())
 # final minus text-only = playlist patch.
 (REL/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.ips').write_bytes(ips(d,final))
 (REL/'Ninja_Gaiden_II_Vietnamese_Cumulative.ips').write_bytes(ips(BASE.read_bytes(),final))
 print('text-only',hashlib.sha1(d).hexdigest(),f'{zlib.crc32(d)&0xffffffff:08X}')
 print('final',hashlib.sha1(final).hexdigest(),f'{zlib.crc32(final)&0xffffffff:08X}')
 print('text ips',len((REL/'Ninja_Gaiden_II_Vietnamese_Text.ips').read_bytes()))
 print('playlist ips',len((REL/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.ips').read_bytes()))
if __name__=='__main__':main()
