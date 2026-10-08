import re,zlib,hashlib
data=bytearray()
for line in open('/mnt/user-data/uploads/shinchan_hexdump.txt'):
    m=re.match(r'^([0-9A-F]{8}): ((?:[0-9A-F]{2} ?)+)',line)
    if not m: continue
    assert int(m.group(1),16)==len(data)
    data+=bytes(int(h,16) for h in m.group(2).split())
print(len(data),'%08X'%zlib.crc32(data))
open('orig.nes','wb').write(data)
