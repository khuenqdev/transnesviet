#!/usr/bin/env python3
"""Apply the Step 6 font smoke-test IPS to the exact clean source ROM.

This creates a local diagnostic ROM from the user's own clean ROM. The project
archive distributes only the small IPS patch, not the complete copyrighted ROM.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

EXPECTED_BASE_SHA256 = '5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26'
EXPECTED_PATCHED_SHA256 = '32bd2083b7ccca9e9b7760cc90876253f211d24d55c3c0554dc6c9f38ff0eabc'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_ips(source: bytes, patch: bytes) -> bytes:
    if not patch.startswith(b'PATCH'):
        raise ValueError('Patch does not begin with IPS header')
    out = bytearray(source)
    i = 5
    while True:
        if patch[i:i+3] == b'EOF':
            i += 3
            break
        if i + 5 > len(patch):
            raise ValueError('Truncated IPS record header')
        offset = int.from_bytes(patch[i:i+3], 'big'); i += 3
        length = int.from_bytes(patch[i:i+2], 'big'); i += 2
        if length:
            if i + length > len(patch):
                raise ValueError('Truncated IPS record data')
            payload = patch[i:i+length]; i += length
        else:
            if i + 3 > len(patch):
                raise ValueError('Truncated IPS RLE record')
            count = int.from_bytes(patch[i:i+2], 'big')
            value = patch[i+2]; i += 3
            payload = bytes([value]) * count
        if offset + len(payload) > len(out):
            out.extend(b'\0' * (offset + len(payload) - len(out)))
        out[offset:offset+len(payload)] = payload
    if i != len(patch):
        raise ValueError('Unexpected bytes after IPS EOF')
    return bytes(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True, help='Path to clean Mighty Final Fight (USA).nes')
    ap.add_argument('--patch', type=Path, default=Path(__file__).resolve().parents[1] / 'analysis' / 'Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.ips')
    ap.add_argument('--output', type=Path, default=Path('Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.nes'))
    args = ap.parse_args()
    base = args.rom.read_bytes()
    actual_base_hash = sha256(base)
    if actual_base_hash != EXPECTED_BASE_SHA256:
        raise SystemExit(f'REFUSED: source ROM SHA-256 mismatch.\nExpected: {EXPECTED_BASE_SHA256}\nFound:    {actual_base_hash}')
    patched = apply_ips(base, args.patch.read_bytes())
    actual_patch_hash = sha256(patched)
    if actual_patch_hash != EXPECTED_PATCHED_SHA256:
        raise SystemExit(f'REFUSED: patched result checksum mismatch: {actual_patch_hash}')
    args.output.write_bytes(patched)
    print('PASS: clean ROM checksum matches')
    print(f'PASS: patched ROM checksum matches {actual_patch_hash}')
    print(f'Wrote local diagnostic ROM: {args.output.resolve()}')
    print('WARNING: diagnostic only. OPEN_02 says “À COUPLE DAYS LATER...” to test the font. Not a translation release.')

if __name__ == '__main__':
    main()
