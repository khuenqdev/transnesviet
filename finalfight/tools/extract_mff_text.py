#!/usr/bin/env python3
from pathlib import Path
import argparse, re, hashlib, zlib

A = {i: chr(ord("A") + i - 0x10) for i in range(0x10, 0x2A)}
P = {0x00: " ", 0x2A: "?", 0x2B: ".", 0x2C: ",", 0x2D: "'", 0x2E: "!", 0x2F: "-"}
CTRL = {x: f"<CTRL{x:02X}>" for x in range(0x70, 0x7A)}
def decode(raw: bytes) -> str:
    out = []
    for b in raw:
        if b in A: out.append(A[b])
        elif b in P: out.append(P[b])
        elif b == 0xFE: out.append("\n")
        elif b == 0xFF: out.append("<END>")
        elif b in CTRL: out.append(CTRL[b])
        else: out.append(f"[{b:02X}]")
    return "".join(out)

def find_bytes(blob: bytes, needle: bytes):
    return [m.start() for m in re.finditer(re.escape(needle), blob)]

def enc(s: str) -> bytes:
    out = bytearray()
    for ch in s:
        if ch == " ": out.append(0)
        elif "A" <= ch <= "Z": out.append(0x10 + ord(ch) - ord("A"))
        elif ch == "?": out.append(0x2A)
        elif ch == ".": out.append(0x2B)
        elif ch == ",": out.append(0x2C)
        elif ch == "'": out.append(0x2D)
        elif ch == "!": out.append(0x2E)
        elif ch == "-": out.append(0x2F)
        else: raise ValueError(f"Unsupported character: {ch!r}")
    return bytes(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("mff_extracted.txt"))
    args = ap.parse_args()

    data = args.rom.read_bytes()
    if data[:4] != b"NES\x1A":
        raise SystemExit("Not an iNES ROM.")
    body = data[16:]
    if len(body) != 0x40000:
        raise SystemExit(f"Unexpected ROM body size: {len(body):#x}")
    if f"{zlib.crc32(body)&0xffffffff:08X}" != "3F78037C":
        raise SystemExit("ROM body CRC does not match the expected USA dump.")

    prg = body[:0x20000]
    checks = [
        ("opening", "THIS IS METRO CITY."),
        ("boss", "I AM SUPERIOR."),
        ("credits", "STAFF"),
    ]
    report = []
    for name, phrase in checks:
        pos = find_bytes(prg, enc(phrase))
        report.append(f"{name}: " + ", ".join(f"file=0x{p+16:06X}" for p in pos))

    report.append("")
    for start, end, name in [
        (6970, 7886, "OPENING_AND_ENDING"),
        (40400, 43000, "BOSS_AND_ENCOUNTER"),
        (75744-16, 76188-16, "CREDITS"),
    ]:
        raw = prg[start:end]
        report.append(f"===== {name} file=0x{start+16:06X}-0x{end+15:06X} =====")
        report.append(decode(raw))
        report.append("")

    args.output.write_text("\n".join(report), encoding="utf-8")
    print(args.output)

if __name__ == "__main__":
    main()
