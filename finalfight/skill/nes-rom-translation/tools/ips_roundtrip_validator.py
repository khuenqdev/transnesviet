#!/usr/bin/env python3
"""Apply an IPS patch in memory and verify its expected output.

Usage: python3 ips_roundtrip_validator.py source.nes patch.ips expected.nes
Optional: --write PATH writes the reconstructed output only after a full parse.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def parse_ips(blob: bytes):
    if not blob.startswith(b"PATCH"):
        raise ValueError("IPS header missing")
    p = 5
    records = []
    while True:
        if p + 3 > len(blob):
            raise ValueError("Truncated IPS: no EOF marker")
        if blob[p:p+3] == b"EOF":
            p += 3
            break
        if p + 5 > len(blob):
            raise ValueError("Truncated IPS record header")
        offset = int.from_bytes(blob[p:p+3], "big")
        length = int.from_bytes(blob[p+3:p+5], "big")
        p += 5
        if length:
            if p + length > len(blob):
                raise ValueError(f"Truncated IPS payload at offset 0x{offset:X}")
            data = blob[p:p+length]
            p += length
        else:
            if p + 3 > len(blob):
                raise ValueError("Truncated IPS RLE record")
            run = int.from_bytes(blob[p:p+2], "big")
            value = blob[p+2]
            p += 3
            if run == 0:
                raise ValueError("IPS RLE run length zero")
            data = bytes([value]) * run
        records.append((offset, data))
    truncate_size = None
    if p < len(blob):
        if len(blob) - p != 3:
            raise ValueError("Unexpected bytes after IPS EOF/truncate-size field")
        truncate_size = int.from_bytes(blob[p:p+3], "big")
    return records, truncate_size

def apply_ips(source: bytes, records, truncate_size=None) -> bytes:
    out = bytearray(source)
    for off, data in records:
        end = off + len(data)
        if end > len(out):
            out.extend(b"\x00" * (end - len(out)))
        out[off:end] = data
    if truncate_size is not None:
        if truncate_size < len(out):
            del out[truncate_size:]
        elif truncate_size > len(out):
            out.extend(b"\x00" * (truncate_size - len(out)))
    return bytes(out)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("patch", type=Path)
    ap.add_argument("expected", type=Path)
    ap.add_argument("--write", type=Path, help="Write reconstructed bytes to this path")
    args = ap.parse_args()
    source, patch, expected = args.source.read_bytes(), args.patch.read_bytes(), args.expected.read_bytes()
    records, truncate = parse_ips(patch)
    rebuilt = apply_ips(source, records, truncate)
    report = {
        "source": str(args.source), "patch": str(args.patch), "expected": str(args.expected),
        "source_sha256": sha(source), "patch_sha256": sha(patch),
        "expected_sha256": sha(expected), "rebuilt_sha256": sha(rebuilt),
        "record_count": len(records), "truncate_size": truncate,
        "source_size": len(source), "expected_size": len(expected), "rebuilt_size": len(rebuilt),
        "round_trip_exact": rebuilt == expected,
    }
    print(json.dumps(report, indent=2))
    if args.write:
        args.write.write_bytes(rebuilt)
    return 0 if report["round_trip_exact"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
