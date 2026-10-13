#!/usr/bin/env python3
"""Read-only NES/iNES ROM preflight: hashes, header, mapper, and size checks.

Usage: python3 nes_rom_preflight.py game.nes [--json report.json]
This script never modifies the ROM.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, zlib
from pathlib import Path

HEADER_SIZE = 16

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def nes2_size(lsb: int, ms_nibble: int, unit: int) -> int:
    if ms_nibble != 0xF:
        return ((ms_nibble << 8) | lsb) * unit
    exponent = lsb >> 2
    multiplier = (lsb & 0x03) * 2 + 1
    return (1 << exponent) * multiplier

def inspect(path: Path) -> dict:
    raw = path.read_bytes()
    report = {
        "path": str(path.resolve()), "filename": path.name, "file_size": len(raw),
        "sha256": sha256(raw), "md5": hashlib.md5(raw).hexdigest(),
        "crc32_file": f"{zlib.crc32(raw) & 0xFFFFFFFF:08X}",
    }
    if len(raw) < HEADER_SIZE:
        report.update({"valid_header": False, "error": "File shorter than 16-byte iNES header"})
        return report
    h = raw[:HEADER_SIZE]
    if h[:4] != b"NES\x1a":
        report.update({"valid_header": False, "error": "Missing NES<1A> magic"})
        return report
    flags6, flags7 = h[6], h[7]
    nes2 = (flags7 & 0x0C) == 0x08
    trainer = bool(flags6 & 0x04)
    mirroring = "four-screen" if flags6 & 0x08 else ("vertical" if flags6 & 0x01 else "horizontal")
    if nes2:
        prg_bytes = nes2_size(h[4], h[9] & 0x0F, 16 * 1024)
        chr_bytes = nes2_size(h[5], (h[9] >> 4) & 0x0F, 8 * 1024)
        mapper = (flags6 >> 4) | (flags7 & 0xF0) | ((h[8] & 0x0F) << 8)
        submapper = h[8] >> 4
        header_format = "NES 2.0"
        console_type = flags7 & 0x03
    else:
        prg_bytes = h[4] * 16 * 1024
        chr_bytes = h[5] * 8 * 1024
        mapper = (flags6 >> 4) | (flags7 & 0xF0)
        submapper = None
        header_format = "iNES 1.0 (or archaic iNES; confirm reserved bytes)"
        console_type = flags7 & 0x03
    prg_start = HEADER_SIZE + (512 if trainer else 0)
    chr_start = prg_start + prg_bytes
    expected_size = chr_start + chr_bytes
    report.update({
        "valid_header": True, "header_hex": h.hex(" ").upper(), "header_format": header_format,
        "mapper": mapper, "submapper": submapper, "prg_bytes": prg_bytes,
        "chr_bytes": chr_bytes, "prg_16k_banks": prg_bytes // (16 * 1024),
        "chr_8k_banks": chr_bytes // (8 * 1024), "trainer_present": trainer,
        "trainer_bytes": 512 if trainer else 0, "mirroring": mirroring,
        "battery_backed": bool(flags6 & 0x02), "console_type_bits": console_type,
        "prg_start_file_offset": prg_start, "chr_start_file_offset": chr_start,
        "expected_file_size_from_header": expected_size, "size_matches_header": expected_size == len(raw),
        "trailing_or_missing_bytes": len(raw) - expected_size,
        "chr_ram_likely": chr_bytes == 0,
        "notes": ["This is a header-level preflight, not proof that the ROM's mapper implementation or game code is understood."]
    })
    return report

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rom", type=Path)
    p.add_argument("--json", type=Path, help="Optional report output path")
    args = p.parse_args()
    report = inspect(args.rom)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json:
        args.json.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.get("valid_header") else 1

if __name__ == "__main__":
    raise SystemExit(main())
