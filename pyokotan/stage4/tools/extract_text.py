#!/usr/bin/env python3
"""Extract currently validated text-like records from Pyokotan no Dai Meiro.

This is a conservative static extractor, not a complete script dumper. It
validates the supplied ROM fingerprint and preserves each record's raw bytes,
PRG-relative offset, absolute file offset, byte capacity, and trailing metadata.

Usage:
  python tools/extract_text.py pyokotan.nes --tbl pyokotan.tbl --out outputs/text_dump.json
"""
from __future__ import annotations
import argparse, hashlib, json, zlib
from pathlib import Path

HEADER_SIZE = 16
EXPECTED_BODY_CRC32 = 0x4339865C
PRG_SIZE = 0x20000
FIXED_TABLE_START = 0x1DE86
FIXED_TABLE_STRIDE = 0x22
FIXED_TABLE_PAYLOAD = 0x20
FIXED_TABLE_COUNT = 12
HUD_START = 0x943F
HUD_LENGTH = 31


def load_rom(path: Path):
    raw = path.read_bytes()
    if len(raw) < HEADER_SIZE or raw[:4] != b"NES\x1a":
        raise ValueError("Input is not an iNES/NES 2.0 ROM (missing NES\\x1a header).")
    h = raw[:HEADER_SIZE]
    if (h[7] & 0x0C) != 0x08:
        raise ValueError("Expected a NES 2.0 header for this ROM layout.")
    prg_msb, chr_msb = h[9] & 0x0F, (h[9] >> 4) & 0x0F
    if prg_msb == 0x0F or chr_msb == 0x0F:
        raise ValueError("NES 2.0 exponent-multiplier ROM sizing is not implemented.")
    prg_size = (h[4] | (prg_msb << 8)) * 0x4000
    chr_size = (h[5] | (chr_msb << 8)) * 0x2000
    end_prg, end_chr = HEADER_SIZE + prg_size, HEADER_SIZE + prg_size + chr_size
    if end_chr > len(raw):
        raise ValueError("ROM is shorter than the header-declared PRG+CHR sizes.")
    prg, chr_rom = raw[HEADER_SIZE:end_prg], raw[end_prg:end_chr]
    mapper = (h[6] >> 4) | (h[7] & 0xF0) | ((h[8] & 0x0F) << 8)
    return raw, h, prg, chr_rom, mapper, (h[8] >> 4)


def load_tbl(path: Path) -> dict[int, str]:
    """Load a .tbl while preserving mapped whitespace (especially ``20= ``).

    Do not call strip() on a whole line before splitting: that silently removes
    the significant trailing space from the space-character mapping and causes
    every extracted string to lose its spaces.
    """
    result: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        try:
            code = int(key.strip(), 16)
        except ValueError:
            continue
        if 0 <= code <= 255:
            result[code] = value  # Preserve leading/trailing whitespace in the mapping.
    return result


def decode(buf: bytes, mapping: dict[int, str]) -> str:
    return "".join(mapping.get(b, f"<{b:02X}>") for b in buf)


def record(id_, category, confidence, start, raw_bytes, mapping, limit, basis, **extra):
    decoded = decode(raw_bytes, mapping)
    r = {
        "id": id_, "category": category, "confidence": confidence,
        "offset": {"prg_relative": f"0x{start:05X}", "file_absolute": f"0x{HEADER_SIZE + start:05X}"},
        "byte_length": len(raw_bytes), "byte_length_limit": limit,
        "length_limit_basis": basis,
        "original_text": decoded, "display_text_trimmed": decoded.strip(),
        "raw_hex": raw_bytes.hex(" ").upper(),
    }
    r.update(extra)
    return r


def make_dump(rom_path: Path, tbl_path: Path) -> dict:
    raw, header, prg, chr_rom, mapper, submapper = load_rom(rom_path)
    if len(prg) != PRG_SIZE:
        raise ValueError(f"Expected 0x{PRG_SIZE:X} PRG bytes, found 0x{len(prg):X}.")
    mapping = load_tbl(tbl_path)
    body = raw[HEADER_SIZE:HEADER_SIZE + len(prg) + len(chr_rom)]
    body_crc = zlib.crc32(body) & 0xFFFFFFFF
    if body_crc != EXPECTED_BODY_CRC32:
        raise ValueError(f"ROM fingerprint mismatch: PRG+CHR CRC32 {body_crc:08X}; expected {EXPECTED_BODY_CRC32:08X}.")

    records = []
    for i in range(FIXED_TABLE_COUNT):
        start = FIXED_TABLE_START + i * FIXED_TABLE_STRIDE
        payload = prg[start:start + FIXED_TABLE_PAYLOAD]
        trailer = prg[start + FIXED_TABLE_PAYLOAD:start + FIXED_TABLE_STRIDE]
        if len(payload) != FIXED_TABLE_PAYLOAD or len(trailer) != 2:
            raise ValueError(f"ROM too short for fixed-width row {i} at 0x{start:X}.")
        records.append(record(
            f"fixed_label_{i:02d}", "fixed_width_ascii_row", "high for literal text bytes; runtime display context not confirmed",
            start, payload, mapping, FIXED_TABLE_PAYLOAD,
            "32-byte payload repeated at a 34-byte stride; the final 2 bytes are kept separate as opaque metadata.",
            trailing_metadata_hex=trailer.hex(" ").upper(),
            trailing_metadata_word_le=f"0x{int.from_bytes(trailer, 'little'):04X}",
            trailing_metadata_interpretation="unresolved; not established as a pointer, PPU address, or text terminator",
        ))

    hud = prg[HUD_START:HUD_START + HUD_LENGTH]
    records.append(record(
        "hud_template_score_life", "hud_or_nametable_template", "high for literal ASCII; editable boundary and use not runtime-confirmed",
        HUD_START, hud, mapping, HUD_LENGTH,
        "31-byte span ending with a '#' separator in the supplied ROM; editing capacity should be checked in an emulator."
    ))

    metadata = []
    for needle, label in [(b"DATE. 1992-12/20", "developer_build_date"), (b"01:10.20", "developer_build_time")]:
        pos = prg.find(needle)
        if pos >= 0:
            metadata.append(record(label, "embedded_developer_metadata", "high for literal bytes; player-visible use unconfirmed",
                                   pos, needle, mapping, len(needle), "Literal ASCII span only; not an editable field capacity."))

    vectors_off = len(prg) - 6
    vectors = {"nmi": f"0x{int.from_bytes(prg[vectors_off:vectors_off+2], 'little'):04X}",
               "reset": f"0x{int.from_bytes(prg[vectors_off+2:vectors_off+4], 'little'):04X}",
               "irq_brk": f"0x{int.from_bytes(prg[vectors_off+4:vectors_off+6], 'little'):04X}",
               "prg_relative_vector_offset": f"0x{vectors_off:05X}",
               "raw_hex": prg[vectors_off:vectors_off+6].hex(" ").upper()}

    return {
        "schema_version": "2.0",
        "game": {"title_english_catalog": "Pyokotan no Dai Meiro", "title_japanese": "ぴょこたんの大迷路",
                 "platform": "Famicom / NES", "region": "Japan", "release_year": 1993,
                 "publisher": "Sunsoft", "developer": "Japan System Supply"},
        "rom_fingerprint": {"source_filename": rom_path.name, "rom_size_bytes": len(raw),
            "header_hex": header.hex(" ").upper(), "format": "NES 2.0", "mapper": mapper, "submapper": submapper,
            "prg_rom_bytes": len(prg), "prg_8k_bank_count": len(prg)//0x2000,
            "chr_rom_bytes": len(chr_rom), "chr_8k_bank_count": len(chr_rom)//0x2000,
            "crc32_full_file": f"{zlib.crc32(raw)&0xFFFFFFFF:08X}", "crc32_prg_plus_chr": f"{body_crc:08X}",
            "crc32_prg": f"{zlib.crc32(prg)&0xFFFFFFFF:08X}", "crc32_chr": f"{zlib.crc32(chr_rom)&0xFFFFFFFF:08X}",
            "sha1_full_file": hashlib.sha1(raw).hexdigest()},
        "encoding_status": {
            "ascii_0x20_0x7e": "confirmed in embedded literal strings; tile glyph rendering may duplicate upper/lowercase shapes",
            "tile_indices_0x91_0x9f": "provisional visual readings ア–ソ from CHR atlas; verify code-to-tile route at runtime before injection",
            "tile_indices_0x90_and_0xb0": "both visually resemble a long-vowel dash ー; runtime mapping unverified",
            "other_extended_codes": "left as <XX> placeholders; no JIS X 0201 mapping is asserted",
            "important_correction": "Earlier starter table mapped 0xA1–0xDF as JIS X 0201 half-width katakana. The atlas does not justify that assumption; this v2 table removes that unsupported mapping."},
        "banking_and_vectors": {"mapper_note": "Mapper 69/FME-7 bank-switches 8 KiB PRG windows; CPU address to file offset requires active bank-register state.",
                                 "interrupt_vectors": vectors},
        "coverage": {"validated_literal_records": len(records), "developer_metadata_records": len(metadata),
                     "complete_dialogue_dump": False,
                     "note": "This ROM has not yet been run with a debugger or instrumented emulator in this workflow. No general dialogue pointer table is confirmed."},
        "text_records": records, "metadata_records": metadata,
        "next_runtime_steps": ["Trace a screen that shows Japanese kana while recording FME-7 PRG bank registers.",
            "Find the routine that converts text bytes to CHR tile IDs; compare it with the visible CHR atlas.",
            "Inspect the 12-row 0x1DE86 region and its 2-byte trailers in a CPU/PPU write trace before patching.",
            "Confirm control codes, string terminators, and display limits; only then extend the dump beyond literal ASCII rows."]
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom", type=Path)
    ap.add_argument("--tbl", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("outputs/text_dump.json"))
    args = ap.parse_args()
    out = make_dump(args.rom, args.tbl)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: {len(out['text_records'])} likely text/template records + {len(out['metadata_records'])} metadata records.")

if __name__ == "__main__":
    main()
