import sys, zlib, hashlib; sys.path.insert(0,'/home/claude/w')
import build, misc
rom=build.assemble_rom()
open('/home/claude/w/shinchan_vi.nes','wb').write(rom)
print('ROM',len(rom),'CRC32 %08X'%zlib.crc32(rom),'textbank used',build.STATS['textbank_used'],
      '| screens end $%X'%misc.STATS['screens_end'],'| free fixed',misc.STATS['free15'],'| free bank3',misc.STATS['free3'])
