import sys
sys.path.insert(0,'/home/claude/saiyuuki/tools')
from asm6502 import assemble
for f,o in (('window.asm',0x8000),('tramp.asm',0xC02A)):
    segs,lab=assemble(open('/home/claude/saiyuuki/src/'+f).read(),o)
    print(f,[(hex(a),len(b)) for a,b in segs]); print({k:hex(v) for k,v in lab.items() if k in('T_INIT','T_STEP','T_BLINK','T_CLEAR','common','entry','POOL','ROWTAB')})
