#!/usr/bin/env python3
from pathlib import Path
import hashlib, zlib, json, sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "Mighty Final Fight (USA).nes")
b = p.read_bytes()
if b[:4] != b"NES\x1A":
    raise SystemExit("Invalid iNES signature")
info = {
    "file": str(p),
    "size": len(b),
    "header": b[:16].hex(),
    "prg_16k_pages": b[4],
    "chr_8k_pages": b[5],
    "mapper": (b[6] >> 4) | (b[7] & 0xF0),
    "flags6": f"0x{b[6]:02X}",
    "flags7": f"0x{b[7]:02X}",
    "body_crc32": f"{zlib.crc32(b[16:]) & 0xFFFFFFFF:08X}",
    "body_md5": hashlib.md5(b[16:]).hexdigest(),
    "body_sha1": hashlib.sha1(b[16:]).hexdigest(),
}
print(json.dumps(info, indent=2))
