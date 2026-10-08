#!/usr/bin/env python3
"""romfacts.py - collect the ROM / Hardware / Space facts of a retro game ROM.

Supported: NES/Famicom (.nes iNES/NES 2.0), Game Boy / Game Boy Color, Game Boy Advance,
SNES/Super Famicom (LoROM/HiROM/ExHiROM/SA-1, with or without copier header),
Mega Drive/Genesis (.bin/.md and interleaved .smd).

usage: python romfacts.py ROM [-o OUT] [--platform nes|gb|gba|snes|md] [--json]
                              [--min-free N] [--top N]
Only the Python standard library is needed.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import zlib

KB = 1024
MB = 1024 * 1024
TODO = "(fill in)"


def size_str(n):
    if n >= MB and n % (MB // 4) == 0:
        return f"{n / MB:g} MB ({n:,} bytes)"
    if n >= KB and n % KB == 0:
        return f"{n // KB} KB ({n:,} bytes)"
    return f"{n:,} bytes"


def hx(v, w=2):
    return f"${v:0{w}X}"


def text(raw, enc="ascii"):
    return raw.decode(enc, "replace").replace("\x00", " ").strip()


def be16(d, o):
    return (d[o] << 8) | d[o + 1]


def be32(d, o):
    return int.from_bytes(d[o:o + 4], "big")


def le16(d, o):
    return d[o] | (d[o + 1] << 8)


class Facts:
    """Collected facts: sections of (key, value) rows, banks for the free-space scan and notes."""

    def __init__(self, platform):
        self.platform = platform
        self.rom = []
        self.hw = []
        self.space = []
        self.notes = []
        # free-space scan: data (headerless image), list of (label, start, size), addr(offset) -> str
        self.image = b""
        self.banks = []
        self.addr = lambda off: f"{off:06X}"
        self.file_shift = 0  # bytes before the image in the original file (copier header etc.)
        self.headerless = None  # image without copier header, for No-Intro style hashes


# ---------------------------------------------------------------------------------------------
# common helpers

REGION_WORDS = ["Japan", "USA", "Europe", "World", "Asia", "Korea", "China", "Taiwan", "Brazil",
                "Australia", "Germany", "France", "Spain", "Italy", "Netherlands", "Sweden", "Canada", "Hong Kong"]


def filename_tags(path):
    name = os.path.basename(path)
    tags = re.findall(r"\(([^)]*)\)", name)
    flags = re.findall(r"\[([^\]]*)\]", name)
    regions = [t for t in tags if any(w in t for w in REGION_WORDS)]
    revs = [t for t in tags if re.match(r"(Rev\s*\w+|v\d+(\.\d+)*|Beta|Proto|Demo|Sample)", t, re.I)]
    return regions, revs, flags


def hashes(b):
    return (f"{zlib.crc32(b) & 0xFFFFFFFF:08X}", hashlib.md5(b).hexdigest(), hashlib.sha1(b).hexdigest())


def free_runs(image, min_len):
    """Runs of 0x00 or 0xFF of at least min_len bytes: list of (start, length, fill)."""
    pat = re.compile(rb"\x00{%d,}|\xFF{%d,}" % (min_len, min_len))
    return [(m.start(), m.end() - m.start(), image[m.start()]) for m in pat.finditer(image)]


def split_runs(runs, banks, min_len):
    """Cut runs at bank borders; returns per-bank lists."""
    per = [[] for _ in banks]
    for start, length, fill in runs:
        end = start + length
        for i, (_, bs, bl) in enumerate(banks):
            s, e = max(start, bs), min(end, bs + bl)
            if e - s >= min_len:
                per[i].append((s, e - s, fill))
    return per


# ---------------------------------------------------------------------------------------------
# NES

# mapper: (name, PRG bank size, fixed bank description, typical max PRG)
NES_MAPPERS = {
    0: ("NROM", 32 * KB, "none (no banking)", 32 * KB),
    1: ("MMC1 (SxROM)", 16 * KB, "last 16 KB at $C000 (PRG mode 3, default)", 512 * KB),
    2: ("UxROM", 16 * KB, "last 16 KB at $C000", 256 * KB),
    3: ("CNROM", 32 * KB, "none (CHR banking only)", 32 * KB),
    4: ("MMC3 (TxROM)", 8 * KB, "last 8 KB at $E000 (+ second-last at $C000 or $8000)", 512 * KB),
    5: ("MMC5 (ExROM)", 8 * KB, "configurable (8/16/32 KB modes)", 1024 * KB),
    7: ("AxROM", 32 * KB, "none (32 KB switching)", 256 * KB),
    9: ("MMC2 (PxROM)", 8 * KB, "last three 8 KB banks", 128 * KB),
    10: ("MMC4 (FxROM)", 16 * KB, "last 16 KB at $C000", 256 * KB),
    11: ("Color Dreams", 32 * KB, "none", 128 * KB),
    16: ("Bandai FCG", 16 * KB, "last 16 KB at $C000", 256 * KB),
    18: ("Jaleco SS88006", 8 * KB, "last 8 KB at $E000", 256 * KB),
    19: ("Namco 163", 8 * KB, "last 8 KB at $E000", 512 * KB),
    21: ("Konami VRC4", 8 * KB, "last two 8 KB banks", 256 * KB),
    22: ("Konami VRC2a", 8 * KB, "last two 8 KB banks", 256 * KB),
    23: ("Konami VRC2/VRC4", 8 * KB, "last two 8 KB banks", 256 * KB),
    24: ("Konami VRC6a", 16 * KB, "last 8 KB at $E000", 256 * KB),
    25: ("Konami VRC4/VRC2", 8 * KB, "last two 8 KB banks", 256 * KB),
    26: ("Konami VRC6b", 16 * KB, "last 8 KB at $E000", 256 * KB),
    33: ("Taito TC0190", 8 * KB, "last two 8 KB banks", 256 * KB),
    66: ("GxROM", 32 * KB, "none", 128 * KB),
    68: ("Sunsoft-4", 16 * KB, "last 16 KB at $C000", 256 * KB),
    69: ("Sunsoft FME-7", 8 * KB, "last 8 KB at $E000", 512 * KB),
    71: ("Camerica BF9093", 16 * KB, "last 16 KB at $C000", 256 * KB),
    73: ("Konami VRC3", 16 * KB, "last 16 KB at $C000", 128 * KB),
    75: ("Konami VRC1", 8 * KB, "last 8 KB at $E000", 128 * KB),
    85: ("Konami VRC7", 8 * KB, "last 8 KB at $E000", 512 * KB),
    206: ("Namco 118 (DxROM)", 8 * KB, "last two 8 KB banks", 128 * KB),
}


def nes_size(lsb, msb, unit):
    if msb == 0xF:  # NES 2.0 exponent-multiplier notation
        return (2 ** (lsb >> 2)) * ((lsb & 3) * 2 + 1)
    return ((msb << 8) | lsb) * unit


def analyze_nes(data):
    f = Facts("NES / Famicom")
    h = data[:16]
    f6, f7 = h[6], h[7]
    nes2 = (f7 & 0x0C) == 0x08
    dirty = not nes2 and any(h[12:16])
    mapper = (f6 >> 4) | (0 if dirty else (f7 & 0xF0))
    sub = None
    if nes2:
        mapper |= (h[8] & 0x0F) << 8
        sub = h[8] >> 4
        prg = nes_size(h[4], h[9] & 0x0F, 16 * KB)
        chr_ = nes_size(h[5], h[9] >> 4, 8 * KB)
    else:
        prg, chr_ = h[4] * 16 * KB, h[5] * 8 * KB
    trainer = bool(f6 & 4)
    prg_start = 16 + (512 if trainer else 0)
    name, bank, fixed, maxprg = NES_MAPPERS.get(mapper, (f"mapper {mapper} (unknown to this tool)", 16 * KB, TODO, None))
    bank = min(bank, prg) if prg else bank

    f.rom.append(("Header type", "NES 2.0 (16-byte header)" if nes2 else "iNES 1.0 (16-byte header)"
                  + (" - bytes 12-15 not zero (old 'DiskDude!' style), mapper high nibble ignored" if dirty else "")))
    f.rom.append(("Trainer", "yes (512 bytes before PRG)" if trainer else "no"))
    expect = prg_start + prg + chr_
    if expect != len(data):
        f.notes.append(f"File size {len(data):,} does not match header ({expect:,}); check the dump/header.")

    f.hw.append(("Platform / CPU / endian", "NES/Famicom / Ricoh 2A03 (6502, no decimal mode) / little-endian"))
    f.hw.append(("Mapper", f"{mapper} - {name}" + (f", submapper {sub}" if sub else "")))
    f.hw.append(("PRG-ROM", f"{size_str(prg)} at file offset {hx(prg_start, 4)}"))
    f.hw.append(("CHR", f"CHR-ROM {size_str(chr_)} at file offset {hx(prg_start + prg, 5)}" if chr_
                 else "CHR-RAM (no CHR-ROM; graphics/font are copied from PRG)"))
    mir = "four-screen" if f6 & 8 else ("vertical" if f6 & 1 else "horizontal")
    f.hw.append(("Mirroring", mir + " (header; mapper may override)"))
    f.hw.append(("Bank size / fixed bank(s)", f"{size_str(bank)} / {fixed}"))
    f.hw.append(("offset <-> address formula",
                 f"file = {prg_start} + bank*{hx(bank, 4)} + (cpu - window base); cpu window $8000-$FFFF; "
                 "vectors NMI/RESET/IRQ at $FFFA-$FFFF (last bank)"))
    last = data[prg_start + prg - 6:prg_start + prg] if prg >= 6 else b""
    if len(last) == 6:
        f.hw.append(("Vectors (last PRG bytes)", f"NMI {hx(le16(last, 0), 4)}  RESET {hx(le16(last, 2), 4)}  IRQ {hx(le16(last, 4), 4)}"))
    if nes2:
        ram = lambda n: (64 << n) if n else 0
        f.hw.append(("Save RAM", f"PRG-RAM {size_str(ram(h[10] & 15))}, PRG-NVRAM (battery) {size_str(ram(h[10] >> 4))}, "
                     f"CHR-RAM {size_str(ram(h[11] & 15))}, CHR-NVRAM {size_str(ram(h[11] >> 4))}"))
        f.hw.append(("Timing", ["NTSC", "PAL", "multi-region", "Dendy"][h[12] & 3]))
    else:
        f.hw.append(("Save RAM", ("battery-backed" if f6 & 2 else "no battery") + " (usually 8 KB at $6000-$7FFF)"))
    f.hw.append(("Header / ROM checksum", "none on this platform (the game may still check its save data)"))

    f.image = data[prg_start:prg_start + prg]
    f.file_shift = prg_start
    f.headerless = data[16:]
    n = max(1, prg // bank) if bank else 1
    f.banks = [(f"bank {i:02X}", i * bank, bank) for i in range(n)]

    def addr(off, bank=bank, n=n):
        b = off // bank
        if bank >= 32 * KB:
            base = 0x8000
        elif bank == 16 * KB:
            base = 0xC000 if (b == n - 1 and "last" in fixed) else 0x8000
        else:
            base = 0xE000 if (b == n - 1 and "last" in fixed) else (0xC000 if (b == n - 2 and "two" in fixed) else 0x8000)
        return f"{b:02X}:{base + off % bank:04X}"
    f.addr = addr
    f.max_size = maxprg
    f.size_now = prg
    if mapper == 1:
        f.notes.append("MMC1: 512 KB is possible with SUROM wiring (CHR register bit 4 selects the 256 KB half).")
    return f


# ---------------------------------------------------------------------------------------------
# Game Boy / Game Boy Color

GB_LOGO = bytes.fromhex("CEED6666CC0D000B03730083000C000D0008111F8889000EDCCC6EE6DDDDD999BBBB67636E0EECCCDDDC999FBBB9333E")
GB_TYPES = {
    0x00: "ROM ONLY", 0x01: "MBC1", 0x02: "MBC1+RAM", 0x03: "MBC1+RAM+BATTERY", 0x05: "MBC2", 0x06: "MBC2+BATTERY",
    0x08: "ROM+RAM", 0x09: "ROM+RAM+BATTERY", 0x0B: "MMM01", 0x0C: "MMM01+RAM", 0x0D: "MMM01+RAM+BATTERY",
    0x0F: "MBC3+TIMER+BATTERY", 0x10: "MBC3+TIMER+RAM+BATTERY", 0x11: "MBC3", 0x12: "MBC3+RAM", 0x13: "MBC3+RAM+BATTERY",
    0x19: "MBC5", 0x1A: "MBC5+RAM", 0x1B: "MBC5+RAM+BATTERY", 0x1C: "MBC5+RUMBLE", 0x1D: "MBC5+RUMBLE+RAM",
    0x1E: "MBC5+RUMBLE+RAM+BATTERY", 0x20: "MBC6", 0x22: "MBC7+SENSOR+RUMBLE+RAM+BATTERY", 0xFC: "POCKET CAMERA",
    0xFD: "BANDAI TAMA5", 0xFE: "HuC3", 0xFF: "HuC1+RAM+BATTERY",
}
GB_MAX = {"ROM ONLY": 32 * KB, "ROM+RAM": 32 * KB, "MBC1": 2 * MB, "MBC2": 256 * KB, "MBC3": 2 * MB, "MBC5": 8 * MB,
          "MBC6": 1 * MB, "MBC7": 2 * MB, "HuC1": 1 * MB, "HuC3": 2 * MB, "MMM01": 8 * MB}
GB_RAM = {0: 0, 1: 2 * KB, 2: 8 * KB, 3: 32 * KB, 4: 128 * KB, 5: 64 * KB}


def analyze_gb(data):
    cgb = data[0x143]
    f = Facts("Game Boy Color" if cgb & 0x80 else "Game Boy")
    title_raw = data[0x134:0x143] if cgb & 0x80 else data[0x134:0x144]
    title = text(title_raw.split(b"\x00")[0])
    ctype = data[0x147]
    tname = GB_TYPES.get(ctype, f"unknown {hx(ctype)}")
    rs = data[0x148]
    rom_size = (32 * KB) << rs if rs <= 8 else {0x52: 1152 * KB, 0x53: 1280 * KB, 0x54: 1536 * KB}.get(rs, 0)
    ram_size = GB_RAM.get(data[0x149], None)
    hchk = 0
    for b in data[0x134:0x14D]:
        hchk = (hchk - b - 1) & 0xFF
    gsum = (sum(data) - data[0x14E] - data[0x14F]) & 0xFFFF
    gstored = be16(data, 0x14E)

    f.rom.append(("Internal title", title or "(empty)"))
    f.rom.append(("Destination", {0: "Japan", 1: "overseas"}.get(data[0x14A], hx(data[0x14A]))))
    f.rom.append(("Version", str(data[0x14C])))
    lic = data[0x14B]
    f.rom.append(("Licensee", f"new code '{text(data[0x144:0x146])}'" if lic == 0x33 else f"old code {hx(lic)}"))
    f.rom.append(("Header type", "internal header $0100-$014F (no copier header)"))
    f.rom.append(("Nintendo logo", "OK" if data[0x104:0x134] == GB_LOGO else "MISMATCH (will not boot on hardware)"))

    f.hw.append(("Platform / CPU / endian", f"{f.platform} / Sharp SM83 (LR35902) / little-endian"))
    f.hw.append(("CGB / SGB flags", {0x80: "CGB-enhanced (works on DMG)", 0xC0: "CGB only"}.get(cgb, "DMG")
                 + (", SGB functions" if data[0x146] == 0x03 else "")))
    f.hw.append(("Mapper / MBC", f"{hx(ctype)} {tname}"))
    f.hw.append(("ROM size (header)", f"{hx(rs)} = {size_str(rom_size)}" + ("" if rom_size == len(data) else f"  (file is {size_str(len(data))})")))
    f.hw.append(("Bank size / fixed bank(s)", "16 KB / bank 0 fixed at $0000-$3FFF, switchable bank at $4000-$7FFF"))
    f.hw.append(("offset <-> address formula", "bank 0: file = addr;  bank n: file = n*$4000 + (addr - $4000);  "
                 "addr = $4000 + file % $4000, bank = file // $4000"))
    f.hw.append(("Entry point", f"$0100: {data[0x100:0x104].hex(' ').upper()}"))
    sram = "MBC2 built-in 512 x 4 bits" if "MBC2" in tname else (size_str(ram_size) if ram_size else "none")
    f.hw.append(("Save RAM", f"{sram} at $A000-$BFFF" + (", battery-backed" if "BATTERY" in tname else "")))
    f.hw.append(("Header checksum ($014D)", f"stored {hx(data[0x14D])}, computed {hx(hchk)} - "
                 + ("OK" if hchk == data[0x14D] else "MISMATCH: boot ROM will refuse to start")
                 + "; algorithm: x = x - byte - 1 over $0134-$014C"))
    f.hw.append(("Global checksum ($014E)", f"stored {hx(gstored, 4)}, computed {hx(gsum, 4)} - "
                 + ("OK" if gsum == gstored else "mismatch") + " (not checked by hardware)"))

    f.image = data
    f.banks = [(f"bank {i:02X}", i * 0x4000, 0x4000) for i in range((len(data) + 0x3FFF) // 0x4000)]
    f.addr = lambda off: f"{off // 0x4000:02X}:{(off if off < 0x4000 else 0x4000 + off % 0x4000):04X}"
    f.max_size = next((v for k, v in GB_MAX.items() if tname.startswith(k)), None)
    f.size_now = len(data)
    if f.max_size and f.max_size <= 2 * MB and len(data) >= f.max_size // 2:
        f.notes.append("Expansion: switching to MBC5 ($0147 = $19-$1E) allows up to 8 MB; patch bank writes ($2000 low, $3000 bit 8).")
    return f


# ---------------------------------------------------------------------------------------------
# Game Boy Advance

GBA_LOGO_HEAD = bytes.fromhex("24FFAE51699AA2213D84820A")
GBA_REGION = {"J": "Japan", "E": "USA / English", "P": "Europe", "D": "Germany", "F": "France", "I": "Italy",
              "S": "Spain", "H": "Netherlands", "K": "Korea", "C": "China", "X": "Europe (alt)", "Y": "Europe (alt)"}


def analyze_gba(data):
    f = Facts("Game Boy Advance")
    code = text(data[0xAC:0xB0])
    chk = 0
    for b in data[0xA0:0xBD]:
        chk = (chk - b) & 0xFF
    chk = (chk - 0x19) & 0xFF
    f.rom.append(("Internal title", text(data[0xA0:0xAC]) or "(empty)"))
    f.rom.append(("Game code", f"{code} (AGB-{code})" + (f", region letter '{code[3]}' = {GBA_REGION.get(code[3], '?')}" if len(code) == 4 else "")))
    f.rom.append(("Maker code", text(data[0xB0:0xB2])))
    f.rom.append(("Version", str(data[0xBC])))
    f.rom.append(("Header type", "internal header $00-$BF (no copier header)"))
    f.rom.append(("Nintendo logo", "OK (prefix)" if data[4:16] == GBA_LOGO_HEAD else "MISMATCH"))

    m = re.search(rb"(EEPROM|SRAM_F|SRAM|FLASH1M|FLASH512|FLASH)_V\d{3}", data)
    f.hw.append(("Platform / CPU / endian", "Game Boy Advance / ARM7TDMI (ARM + Thumb) / little-endian"))
    f.hw.append(("Mapper", "none: ROM mapped linearly at $08000000 (mirrors $0A000000, $0C000000), max 32 MB"))
    f.hw.append(("Bank size / fixed bank(s)", "no banking"))
    f.hw.append(("offset <-> address formula", "addr = $08000000 + file;  file = addr - $08000000; pointers are 32-bit little-endian"))
    entry = int.from_bytes(data[0:4], "little")
    if (entry >> 24) == 0xEA:
        f.hw.append(("Entry point", f"ARM branch to $0800{(8 + ((entry & 0xFFFFFF) << 2)) & 0xFFFFFF:04X}"))
    f.hw.append(("Save type", (m.group(0).decode() if m else "none found (no save, or custom)")
                 + " (EEPROM 512 B/8 KB, SRAM 32 KB, FLASH 64/128 KB at $0E000000)"))
    f.hw.append(("Complement check ($BD)", f"stored {hx(data[0xBD])}, computed {hx(chk)} - "
                 + ("OK" if chk == data[0xBD] else "MISMATCH: BIOS will refuse to start")
                 + "; algorithm: chk = -(sum $A0-$BC) - $19"))
    f.hw.append(("Fixed byte ($B2)", "OK ($96)" if data[0xB2] == 0x96 else f"{hx(data[0xB2])} (should be $96)"))

    f.image = data
    blk = MB
    f.banks = [(f"{i:02X}xxxxx", i * blk, blk) for i in range((len(data) + blk - 1) // blk)]
    f.addr = lambda off: f"{0x08000000 + off:08X}"
    f.max_size, f.size_now = 32 * MB, len(data)
    f.block_word = "1 MB block"
    return f


# ---------------------------------------------------------------------------------------------
# SNES

SNES_MAP = {0x20: "LoROM", 0x21: "HiROM", 0x22: "LoROM (S-DD1 / ExLoROM)", 0x23: "SA-1", 0x25: "ExHiROM", 0x2A: "SPC7110 (HiROM)"}
SNES_COPROC = {0x0: "DSP", 0x1: "SuperFX (GSU)", 0x2: "OBC1", 0x3: "SA-1", 0x4: "S-DD1", 0x5: "S-RTC",
               0xE: "other (Super Game Boy / Satellaview)", 0xF: "custom"}
SNES_CUSTOM = {0x00: "SPC7110", 0x01: "ST010/ST011", 0x02: "ST018", 0x10: "Cx4"}
SNES_REGION = ["Japan", "USA", "Europe", "Sweden/Scandinavia", "Finland", "Denmark", "France", "Netherlands", "Spain",
               "Germany", "Italy", "China", "Indonesia", "Korea", "Global", "Canada", "Brazil", "Australia"]


def snes_checksum(d):
    n = len(d)
    if n == 0:
        return 0
    p = 1 << (n.bit_length() - 1)
    if p == n:
        return sum(d) & 0xFFFF
    rest = d[p:]
    reps = p // len(rest) if p % len(rest) == 0 else 1
    return (sum(d[:p]) + snes_checksum(rest) * reps) & 0xFFFF


def snes_score(d, off, kind):
    if off + 0x40 > len(d):
        return -1
    h = d[off:off + 0x40]
    s = 0
    if le16(h, 0x1C) ^ le16(h, 0x1E) == 0xFFFF:
        s += 4
    mode = h[0x15] & 0xEF
    if (kind == "lo" and mode in (0x20, 0x22, 0x23)) or (kind == "hi" and mode in (0x21, 0x2A)) or (kind == "exhi" and mode == 0x25):
        s += 3
    if le16(h, 0x3C) >= 0x8000:
        s += 1
    if all(0x20 <= c < 0x7F or c >= 0xA0 for c in h[:0x15]):
        s += 1
    if 0x07 <= h[0x17] <= 0x0D:
        s += 1
    if h[0x19] < len(SNES_REGION):
        s += 1
    return s


def analyze_snes(data):
    f = Facts("SNES / Super Famicom")
    shift = 512 if len(data) % 1024 == 512 else 0
    d = data[shift:]
    cands = [(snes_score(d, 0x7FC0, "lo"), 0x7FC0, "lo"), (snes_score(d, 0xFFC0, "hi"), 0xFFC0, "hi"),
             (snes_score(d, 0x40FFC0, "exhi"), 0x40FFC0, "exhi")]
    score, ho, kind = max(cands)
    h = d[ho:ho + 0x40]
    mode = h[0x15]
    fast = bool(mode & 0x10)
    mname = SNES_MAP.get(mode & 0xEF, f"unknown {hx(mode)}")
    rtype = h[0x16]
    if rtype < 3:
        chip = ["ROM", "ROM+RAM", "ROM+RAM+battery"][rtype]
    else:
        parts = {3: "ROM+co", 4: "ROM+co+RAM", 5: "ROM+co+RAM+battery", 6: "ROM+co+battery"}.get(rtype & 0xF, f"{hx(rtype)}")
        co = SNES_COPROC.get(rtype >> 4, "?")
        if rtype >> 4 == 0xF and ho >= 1:
            co = SNES_CUSTOM.get(d[ho - 1], f"custom {hx(d[ho - 1])}")
        chip = parts.replace("co", co)
    rom_kb = 1 << h[0x17] if h[0x17] < 16 else 0
    ram_kb = (1 << h[0x18]) if h[0x18] and h[0x18] < 16 else 0
    comp, chk = le16(h, 0x1C), le16(h, 0x1E)
    calc = snes_checksum(d)

    f.rom.append(("Internal title", text(h[:0x15], "shift_jis") or "(empty)"))
    reg = h[0x19]
    f.rom.append(("Region (header)", f"{reg} = {SNES_REGION[reg] if reg < len(SNES_REGION) else '?'}"))
    f.rom.append(("Version", f"1.{h[0x1B]}"))
    if h[0x1A] == 0x33 and ho >= 0x10:
        x = d[ho - 0x10:ho]
        f.rom.append(("Maker / game code", f"{text(x[0:2])} / {text(x[2:6])} (extended header)"))
    else:
        f.rom.append(("Developer code", hx(h[0x1A])))
    f.rom.append(("Header type", ("512-byte copier header present (remove it; offsets below are without it)" if shift
                                  else "no copier header") + f"; internal header at file {hx(ho + shift, 6)} (score {score}/11)"))

    f.hw.append(("Platform / CPU / endian", "SNES / Ricoh 5A22 (65816) + SPC700 sound / little-endian"))
    f.hw.append(("Map mode", f"{hx(mode)} = {mname}, {'FastROM (3.58 MHz)' if fast else 'SlowROM (2.68 MHz)'}"))
    f.hw.append(("Chipset", f"{hx(rtype)} = {chip}"))
    f.hw.append(("ROM size (header)", f"{hx(h[0x17])} = {size_str(rom_kb * KB)}" + ("" if rom_kb * KB == len(d) else f"  (image is {size_str(len(d))})")))
    hi = kind != "lo" and "SA-1" not in mname
    if hi:
        f.hw.append(("Bank size / fixed bank(s)", "64 KB (HiROM); no fixed bank - code runs from any bank, vectors in bank $00 (= file $00FFE0)"))
        f.hw.append(("offset <-> address formula", "addr = ($C0 + file // $10000):(file % $10000)  (also $40-$7D, upper halves at $00-$3F:8000);  "
                     "file = (bank & $3F) * $10000 + addr" + ("; ExHiROM: file >= 4 MB maps to $40-$7D" if kind == "exhi" else "")))
    else:
        f.hw.append(("Bank size / fixed bank(s)", "32 KB (LoROM) at $8000-$FFFF; no fixed bank - vectors in bank $00 (= file $007FE0)"))
        f.hw.append(("offset <-> address formula", f"addr = (${'80' if fast else '00'} + file // $8000):($8000 + file % $8000);  "
                     "file = (bank & $7F) * $8000 + (addr - $8000)"))
    f.hw.append(("Vectors (emulation)", f"RESET {hx(le16(h, 0x3C), 4)}  NMI {hx(le16(h, 0x3A), 4)}  IRQ/BRK {hx(le16(h, 0x3E), 4)};  "
                 f"native NMI {hx(le16(h, 0x2A), 4)}"))
    sram = size_str(ram_kb * KB) if ram_kb else "none"
    f.hw.append(("Save RAM", f"{sram}" + (", battery-backed" if "battery" in chip else "")
                 + (" (LoROM: $70-$7D:0000; HiROM: $20-$3F:6000)" if ram_kb else "")))
    f.hw.append(("Checksum ($xxDE) / complement ($xxDC)", f"stored {hx(chk, 4)} / {hx(comp, 4)}, computed {hx(calc, 4)} - "
                 + ("OK" if calc == chk and (chk ^ comp) == 0xFFFF else "MISMATCH")
                 + "; 16-bit byte sum, non power-of-2 sizes mirrored; not checked by hardware"))
    if "SA-1" in mname or "SPC7110" in mname or "S-DD1" in chip or "SuperFX" in chip:
        f.notes.append(f"Coprocessor game ({chip}): the mapping, tools and expansion options differ from plain LoROM/HiROM.")

    f.image = d
    f.file_shift = shift
    f.headerless = d if shift else None
    bank = 0x10000 if hi else 0x8000
    f.banks = [(f"bank {i:02X}", i * bank, bank) for i in range((len(d) + bank - 1) // bank)]
    if hi:
        def addr(off):
            if kind == "exhi" and off >= 0x400000:
                return f"{0x40 + (off - 0x400000) // 0x10000:02X}:{off % 0x10000:04X}"
            return f"{0xC0 + off // 0x10000:02X}:{off % 0x10000:04X}"
    else:
        def addr(off):
            return f"{(0x80 if fast else 0) + off // 0x8000:02X}:{0x8000 + off % 0x8000:04X}"
    f.addr = addr
    f.max_size = {"lo": 4 * MB, "hi": 4 * MB, "exhi": 8 * MB}[kind] if "SA-1" not in mname else 8 * MB
    f.size_now = len(d)
    return f


# ---------------------------------------------------------------------------------------------
# Mega Drive / Genesis

def smd_deinterleave(data):
    body = data[512:]
    out = bytearray(len(body))
    for b in range(0, len(body), 0x4000):
        blk = body[b:b + 0x4000]
        half = len(blk) // 2
        out[b + 1:b + 2 * half:2] = blk[:half]   # first half = odd bytes
        out[b:b + 2 * half:2] = blk[half:2 * half]  # second half = even bytes
    return bytes(out)


def is_smd(data):
    return len(data) % 0x4000 == 512 and data[8] == 0xAA and data[9] == 0xBB


def analyze_md(data):
    smd = is_smd(data)
    d = smd_deinterleave(data) if smd else data
    system = text(d[0x100:0x110])
    f = Facts("Sega 32X" if "32X" in system else "Mega Drive / Genesis")
    calc = 0
    body = d[0x200:]
    if len(body) % 2:
        body += b"\x00"
    for i in range(0, len(body), 2):
        calc += (body[i] << 8) | body[i + 1]
    calc &= 0xFFFF
    stored = be16(d, 0x18E)
    rom_start, rom_end = be32(d, 0x1A0), be32(d, 0x1A4)
    region = text(d[0x1F0:0x1F3])

    f.rom.append(("System type", system))
    f.rom.append(("Copyright / date", text(d[0x110:0x120])))
    f.rom.append(("Domestic title", text(d[0x120:0x150], "shift_jis")))
    f.rom.append(("Overseas title", text(d[0x150:0x180], "shift_jis")))
    f.rom.append(("Serial / version", text(d[0x180:0x18E])))
    f.rom.append(("Region codes ($1F0)", region + "  (J = Japan, U = Americas, E = Europe; hex digit: bit0 JP-NTSC, bit2 US-NTSC, bit3 EU-PAL)"))
    f.rom.append(("Header type", "interleaved .smd (512-byte header + 16 KB interleaved blocks) - convert to .bin; values below use the de-interleaved image"
                  if smd else "raw .bin / .md (no copier header)"))

    f.hw.append(("Platform / CPU / endian", f"{f.platform} / Motorola 68000 + Z80 (sound) / big-endian"))
    mapper = "Sega SSF2 mapper needed (> 4 MB)" if len(d) > 4 * MB or "SSF" in system else "none (linear ROM, up to 4 MB)"
    f.hw.append(("Mapper", mapper))
    f.hw.append(("I/O devices ($190)", text(d[0x190:0x1A0])))
    f.hw.append(("ROM range (header)", f"{hx(rom_start, 6)}-{hx(rom_end, 6)}" + ("" if rom_end + 1 == len(d) else f"  (image is {size_str(len(d))})")))
    f.hw.append(("RAM range (header)", f"{hx(be32(d, 0x1A8), 6)}-{hx(be32(d, 0x1AC), 6)}"))
    f.hw.append(("Bank size / fixed bank(s)", "no banking for 68000 (Z80 sees ROM through a 32 KB window at $8000)"))
    f.hw.append(("offset <-> address formula", "addr = file (linear $000000-$3FFFFF); pointers are 32-bit big-endian; words/longs must be at even addresses"))
    f.hw.append(("Vectors", f"initial SSP {hx(be32(d, 0), 8)}, RESET {hx(be32(d, 4), 8)}, VBlank (lvl 6) {hx(be32(d, 0x78), 8)}"))
    if d[0x1B0:0x1B2] == b"RA":
        t = d[0x1B2]
        kind = {0: "16-bit (both bytes)", 2: "even bytes", 3: "odd bytes", 1: "serial EEPROM?"}[(t >> 3) & 3]
        f.hw.append(("Save RAM", f"'RA' type {t:02X}{d[0x1B3]:02X}: {kind}, " + ("battery-backed" if t & 0x40 else "not backed")
                     + f", {hx(be32(d, 0x1B4), 6)}-{hx(be32(d, 0x1B8), 6)} (enable via $A130F1)"))
    else:
        f.hw.append(("Save RAM", "none declared in header ($1B0 != 'RA'); game may still use SRAM/EEPROM"))
    f.hw.append(("Checksum ($18E)", f"stored {hx(stored, 4)}, computed {hx(calc, 4)} - " + ("OK" if calc == stored else "MISMATCH")
                 + "; sum of 16-bit words $200-end; not checked by hardware but MANY games check it at boot"))

    f.image = d
    f.file_shift = 0
    f.headerless = d if smd else None
    blk = 0x10000
    f.banks = [(f"{i * blk:06X}", i * blk, blk) for i in range((len(d) + blk - 1) // blk)]
    f.addr = lambda off: f"{off:06X}"
    f.max_size, f.size_now = (4 * MB if len(d) <= 4 * MB else 16 * MB), len(d)
    f.block_word = "64 KB block"
    if smd:
        f.notes.append("Free-space offsets refer to the de-interleaved .bin image, not to the .smd file.")
    return f


# ---------------------------------------------------------------------------------------------
# detection

def detect(data, ext):
    if data[:4] == b"NES\x1a":
        return "nes"
    if len(data) >= 0x150 and data[0x104:0x134] == GB_LOGO:
        return "gb"
    if len(data) >= 0xC0 and data[4:16] == GBA_LOGO_HEAD and data[0xB2] == 0x96:
        return "gba"
    if len(data) >= 0x200 and (data[0x100:0x104] == b"SEGA" or data[0x101:0x105] == b"SEGA" or is_smd(data)):
        return "md"
    if ext in (".sfc", ".smc", ".swc", ".fig"):
        return "snes"
    if ext in (".gb", ".gbc", ".sgb"):
        return "gb"
    if ext == ".gba":
        return "gba"
    if ext in (".md", ".gen", ".smd", ".bin", ".32x"):
        return "md"
    shift = 512 if len(data) % 1024 == 512 else 0
    d = data[shift:]
    if max(snes_score(d, 0x7FC0, "lo"), snes_score(d, 0xFFC0, "hi")) >= 7:
        return "snes"
    return None


ANALYZERS = {"nes": analyze_nes, "gb": analyze_gb, "gba": analyze_gba, "snes": analyze_snes, "md": analyze_md}


# ---------------------------------------------------------------------------------------------
# report

def build_report(path, data, platform, min_free, top):
    f = ANALYZERS[platform](data)
    regions, revs, flags = filename_tags(path)
    crc, md5, sha1 = hashes(data)
    rom = [("Title / region / revision", " / ".join([
        os.path.splitext(os.path.basename(path))[0],
        ", ".join(regions) or "region: see header",
        ", ".join(revs) or "Rev 0 (no tag)"])),
        ("File name / size", f"{os.path.basename(path)} / {size_str(len(data))}"),
        ("CRC32 / SHA-1 (file)", f"{crc} / {sha1}"),
        ("MD5 (file)", md5)]
    if f.headerless is not None:
        c2, m2, s2 = hashes(f.headerless)
        rom.append(("CRC32 / SHA-1 (no header)", f"{c2} / {s2}"))
    if flags:
        rom.append(("Dump flags (file name)", " ".join(f"[{x}]" for x in flags) + ("  ([!] = verified good dump)" if "!" in flags else "")))
    rom += f.rom
    rom.append(("Base patch used (if any)", TODO))

    hw = f.hw + [("Checked by game?", TODO + " (patch one byte in unused space and boot to test)")]

    runs = free_runs(f.image, min_free)
    per = split_runs(runs, f.banks, min_free)
    total = sum(l for r in per for _, l, _ in r)
    word = getattr(f, "block_word", "bank")
    rows = []
    for (label, bs, bl), rs in zip(f.banks, per):
        if not rs:
            continue
        free = sum(l for _, l, _ in rs)
        big = max(rs, key=lambda r: r[1])
        rows.append(f"{label:>10}  free {free:>8,} B in {len(rs):>3} run(s); largest {big[1]:>7,} B of {big[2]:02X} at "
                    f"file {big[0] + f.file_shift:06X} / {f.addr(big[0])}")
    allr = sorted((r for rs in per for r in rs), key=lambda r: -r[1])[:top]
    space = [("Scan settings", f"runs of $00 or $FF >= {min_free} bytes, split at {word} borders "
              "(filler runs may still be data - verify with a debugger)"),
             ("Total free (candidate)", f"{total:,} bytes of {size_str(len(f.image))} ({100 * total / max(1, len(f.image)):.1f}%)"),
             (f"Free ROM space per {word}", "\n".join(rows) if rows else "none found")]
    space.append((f"Largest {len(allr)} runs", "\n".join(
        f"file {s + f.file_shift:06X}  {f.addr(s):>11}  {l:>7,} B  fill {fl:02X}" for s, l, fl in allr) or "none"))
    space.append(("Free RAM", TODO + " (watch RAM in a debugger; look for areas never written)"))
    if getattr(f, "max_size", None):
        room = f.max_size - f.size_now
        plan = (f"current {size_str(f.size_now)}, platform/mapper limit about {size_str(f.max_size)}"
                + (f" -> up to {size_str(room)} can be added" if room > 0 else " -> already at the limit (change mapper/board)"))
    else:
        plan = "limit unknown for this mapper"
    space.append(("Expansion plan", plan + "; " + TODO))
    return f, {"ROM": rom, "Hardware": hw, "Space": space}


def render_text(path, f, sections):
    out = [f"ROM fact sheet - {os.path.basename(path)}", f"Platform: {f.platform}", ""]
    for name, rows in sections.items():
        out.append(f"== {name} ==")
        w = max(len(k) for k, _ in rows)
        for k, v in rows:
            lines = str(v).split("\n")
            out.append(f"{k.ljust(w)} : {lines[0]}")
            out += [" " * (w + 3) + line for line in lines[1:]]
        out.append("")
    if f.notes:
        out.append("== Notes ==")
        out += [f"- {n}" for n in f.notes]
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Collect ROM / Hardware / Space facts of a NES, GB/GBC, GBA, SNES or Mega Drive ROM.")
    ap.add_argument("rom")
    ap.add_argument("-o", "--out", help="output file (default: <rom>.facts.txt or <rom>.facts.json)")
    ap.add_argument("--platform", choices=sorted(ANALYZERS), help="force the platform instead of auto-detecting")
    ap.add_argument("--json", action="store_true", help="write JSON instead of text")
    ap.add_argument("--min-free", type=int, default=64, help="minimum run length counted as free space (default 64)")
    ap.add_argument("--top", type=int, default=20, help="number of largest free runs to list (default 20)")
    a = ap.parse_args(argv)

    with open(a.rom, "rb") as fh:
        data = fh.read()
    platform = a.platform or detect(data, os.path.splitext(a.rom)[1].lower())
    if not platform:
        sys.exit("could not detect the platform; use --platform nes|gb|gba|snes|md")
    f, sections = build_report(a.rom, data, platform, max(2, a.min_free), a.top)
    out = a.out or a.rom + (".facts.json" if a.json else ".facts.txt")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        if a.json:
            json.dump({"file": os.path.basename(a.rom), "platform": f.platform,
                       **{k: dict(v) for k, v in sections.items()}, "notes": f.notes}, fh, ensure_ascii=False, indent=2)
        else:
            fh.write(render_text(a.rom, f, sections))
    print(f"{f.platform}: wrote {out}")


if __name__ == "__main__":
    main()
