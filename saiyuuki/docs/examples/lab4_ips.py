#!/usr/bin/env python3
"""Lab 4 - write and apply a minimal IPS patch by hand.  IPS = 'PATCH' + records(offset3, size2, data) + 'EOF'.
usage: python3 lab4_ips.py   (self-test on a fake ROM)"""
def make_ips(records):
    out = bytearray(b'PATCH')
    for off, data in records: out += off.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data
    return bytes(out + b'EOF')
def apply_ips(rom, ips):
    rom = bytearray(rom); assert ips[:5] == b'PATCH'; p = 5
    while ips[p:p + 3] != b'EOF':
        off = int.from_bytes(ips[p:p + 3], 'big'); n = int.from_bytes(ips[p + 3:p + 5], 'big'); p += 5
        if off + n > len(rom): rom.extend(bytes(off + n - len(rom)))      # patch may GROW the ROM
        rom[off:off + n] = ips[p:p + n]; p += n
    return bytes(rom)
if __name__ == '__main__':
    fake = bytes(range(16)) * 4
    ips = make_ips([(0x10, b'\xAA\xBB'), (0x50, b'\xCC' * 3)])      # second record is past the end -> ROM grows
    new = apply_ips(fake, ips)
    print(len(fake), '->', len(new), new[0x10:0x12].hex(), new[0x50:0x53].hex())
