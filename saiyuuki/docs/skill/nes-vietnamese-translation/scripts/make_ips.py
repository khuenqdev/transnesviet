#!/usr/bin/env python3
"""Create an IPS patch (original.nes -> patched.nes). The patched ROM is larger (256 KB); IPS handles that
by simply adding records past the original end.  usage: make_ips.py original.nes patched.nes out.ips"""
import sys
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
out = bytearray(b'PATCH'); i = 0; n = len(b)
def rec(off, data):
    if off == 0x454F46: raise SystemExit('offset collides with EOF marker')
    out.extend(off.to_bytes(3, 'big') + len(data).to_bytes(2, 'big') + data)
while i < n:
    if i < len(a) and a[i] == b[i]: i += 1; continue
    j = i
    while j < n and j - i < 0xFFFF and (j >= len(a) or a[j] != b[j] or (j + 1 < n and j + 1 < len(a) and a[j + 1] != b[j + 1] and False)): j += 1
    # extend over short equal gaps (<8) to save record overhead
    k = j
    while k < n and k - i < 0xFFFF:
        g = k
        while g < n and g < len(a) and a[g] == b[g] and g - k < 8: g += 1
        if g < n and g - k < 8 and (g >= len(a) or a[g] != b[g]): k = g; 
        else: break
        while k < n and (k >= len(a) or a[k] != b[k]) and k - i < 0xFFFF: k += 1
    j = max(j, k)
    if i == 0x454F46: i -= 1
    rec(i, b[i:j]); i = j
out.extend(b'EOF')
if len(b) > len(a): out.extend(len(b).to_bytes(3, 'big'))
open(sys.argv[3], 'wb').write(out); print('IPS', len(out), 'bytes')
