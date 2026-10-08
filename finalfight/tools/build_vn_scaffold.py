#!/usr/bin/env python3
from pathlib import Path
import json, zlib, sys

EXPECTED_BODY_CRC = 0x3F78037C

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_vn_scaffold.py <clean_rom.nes> <layout_verified.json>")
    rom=Path(sys.argv[1]); layout=Path(sys.argv[2])
    b=rom.read_bytes()
    if (zlib.crc32(b[16:]) & 0xffffffff) != EXPECTED_BODY_CRC:
        raise SystemExit("Wrong clean ROM body CRC32.")
    cfg=json.loads(layout.read_text(encoding="utf-8"))
    required=["opening","boss_dialogue","credits"]
    missing=[x for x in required if x not in cfg["verified_pointer_tables"]]
    if missing: raise SystemExit("Missing verified table(s): "+", ".join(missing))
    print("Verified tables:")
    for x in required:
        t=cfg["verified_pointer_tables"][x]
        print(f"  {x}: {t['count']} entries; {t['low_cpu']} / {t['high_cpu']}")
    print("Build is still intentionally blocked until the font-tile lookup is verified.")
if __name__=="__main__":
    main()
