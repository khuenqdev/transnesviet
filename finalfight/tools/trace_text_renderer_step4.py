#!/usr/bin/env python3
"""Static Step 4 verifier for Mighty Final Fight's text-to-PPU path.

Usage: python3 trace_text_renderer_step4.py <clean_rom.nes> [project_dir]
This does not emulate the game or patch ROM bytes.
"""
from pathlib import Path
import argparse, csv, json, zlib, hashlib

EXPECTED_BODY_CRC = 0x3F78037C
EXPECTED_SIZE = 262160

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', type=Path)
    ap.add_argument('project_dir', type=Path, nargs='?', default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    data = args.rom.read_bytes()
    if len(data) != EXPECTED_SIZE:
        raise SystemExit(f'Wrong ROM size: {len(data)}; expected {EXPECTED_SIZE}')
    body_crc = zlib.crc32(data[16:]) & 0xffffffff
    if body_crc != EXPECTED_BODY_CRC:
        raise SystemExit(f'Wrong ROM body CRC32: {body_crc:08X}; expected {EXPECTED_BODY_CRC:08X}')
    prg = data[16:16+131072]
    chr_data = data[16+131072:]
    signatures = {
       'ppu_queue_writer': (0x1C1FD, bytes.fromhex('a2008619bd8007301b8d0620bd81078d0620bc8207bd83078d0720e88810f6e8e8e8d0e060')),
       'nmi_chr_0_1_banks': (0x1C1BC, bytes.fromhex('a9008d0080a9788d0180a9018d0080a97a8d0180')),
       'ppuctrl_shadow_init': (0x1FEB6, bytes.fromhex('a98885ff')),
    }
    results = {}
    for name, (off, sig) in signatures.items():
        actual = prg[off:off+len(sig)]
        results[name] = {'offset': f'0x{off:05X}', 'expected': sig.hex(' '), 'actual': actual.hex(' '), 'pass': actual == sig}
    if not all(x['pass'] for x in results.values()):
        raise SystemExit('At least one ROM byte signature did not match: ' + ', '.join(k for k,v in results.items() if not v['pass']))
    def nonzero(tid):
        tile = chr_data[tid*16:tid*16+16]
        return sum(1 for y in range(8) for x in range(8) if (((tile[y] >> (7-x)) & 1) | (((tile[y+8] >> (7-x)) & 1) << 1)))
    codes = list(range(0x30,0x60)) + list(range(0x7C,0x8F))
    bad = [f'0x{0x1E00+c:04X}' for c in codes if nonzero(0x1E00+c)]
    print(f'ROM body CRC32: {body_crc:08X}')
    print(f'ROM SHA256: {hashlib.sha256(data).hexdigest()}')
    for name, r in results.items(): print(f'{name}: {"PASS" if r["pass"] else "FAIL"} ({r["offset"]})')
    print(f'Candidate blank slots: {len(codes)-len(bad)}/{len(codes)}')
    if bad: print('Nonblank candidate tile(s): ' + ', '.join(bad))
    print('STATIC FINDING: the queue writer stores $0783,X directly to $2007.')
    print('STATIC FINDING: NMI writes MMC3 CHR registers 0/1 = 0x78/0x7A; $FEB6 initializes PPUCTRL shadow to 0x88.')
    print('LIMITATION: static check only; it does not prove no screen references these tile IDs and does not produce a patched ROM.')
if __name__ == '__main__': main()
