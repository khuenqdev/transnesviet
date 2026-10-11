#!/usr/bin/env python3
"""
mother_vi_testrom.py - build a renderer TEST ROM (not for release).

  * Message 901 ("Who are you talking to?" - shown when Talk hits nobody) is repointed to a
    7-line Vietnamese test message placed in free CHR text space ($2F100), so it exercises
    the typewriter, marks on every combination, a {Ninten} name insert and window scrolling.
usage: python mother_vi_testrom.py STAGE3_ROM OUT_ROM
"""
import sys, os, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mother_vi_codec import encode, check_lines

TEST_ID = 901
TEST_CHR = 0x2F100           # inside the 4010-byte free block CHR $2F056-$2FFFF
TEST_MSG = ('◆{Ninten} ơi, em sợ quá!\n'
            ' Cái đèn hình như\n'
            ' đang sống dậy kìa!\n'
            ' Ừ, Ở ĐÂY ẤY! Ặc!\n'
            ' Tiếng Việt có dấu:\n'
            ' ắ ằ ẳ ẵ ặ ấ ầ ẩ ẫ ậ\n'
            ' Ở Ữ Ỷ Ễ Ộ đã xong.\n')

def marks_per_line(b):
    out = []; n = 0
    for x in b:
        if x == 0x01 or x == 0x00:
            out.append(n); n = 0
        elif 0x80 <= x <= 0x8D:
            n += 1
    return out

def build(rom):
    rom = bytearray(rom)
    assert not check_lines(TEST_MSG, 22), check_lines(TEST_MSG, 22)
    data = encode(TEST_MSG)
    assert max(marks_per_line(data)) <= 10, marks_per_line(data)
    chr0 = 16 + rom[4] * 0x4000
    assert set(rom[chr0 + TEST_CHR:chr0 + TEST_CHR + len(data)]) <= {0xFF, 0x00}
    rom[chr0 + TEST_CHR:chr0 + TEST_CHR + len(data)] = data
    v = TEST_CHR - 0x20000
    p = 16 + 0x18 * 0x2000 + 3 * TEST_ID
    rom[p:p + 3] = bytes([v & 0xFF, (v >> 8) & 0xFF, v >> 16])
    return bytes(rom), data

if __name__ == '__main__':
    r, data = build(open(sys.argv[1], 'rb').read())
    open(sys.argv[2], 'wb').write(r)
    print('test message %d bytes, marks/line %s, CRC32 %08X' % (len(data), marks_per_line(data), zlib.crc32(r) & 0xFFFFFFFF))
