#!/usr/bin/env python3
"""Conservative static text extractor for Pyokotan no Dai Meiro (NES).

This script extracts the one clearly recognizable fixed-stride 32-byte label
block found in the supplied ROM, plus the clear ASCII HUD template. It does NOT
claim to extract every Japanese message: the Japanese character map and
runtime PRG/CHR bank selection must be verified before treating the dump as a
complete script.

Usage:
  python tools/extract_text.py pyokotan.nes --tbl pyokotan.tbl --out pyokotan_text_dump.json
"""
from __future__ import annotations
import argparse, hashlib, json, struct, zlib
from pathlib import Path

HEADER_SIZE = 16
EXPECTED_BODY_CRC32 = 0x4339865C
PRG_SIZE = 0x20000
FIXED_TABLE_START = 0x1DE86  # PRG-relative
FIXED_TABLE_STRIDE = 0x22
FIXED_TABLE_PAYLOAD = 0x20
FIXED_TABLE_COUNT = 12
HUD_START = 0x943F  # PRG-relative, points at 'SCORE'
HUD_LENGTH = 31     # bounded by the '#' separator in the template


def load_rom(path: Path):
    raw = path.read_bytes()
    if len(raw) < HEADER_SIZE or raw[:4] != b"NES\x1a":
        raise ValueError("Input is not a valid iNES/NES 2.0 ROM image (missing NES\\x1a header).")
    header = raw[:HEADER_SIZE]
    nes2 = (header[7] & 0x0C) == 0x08
    if not nes2:
        raise ValueError("This extractor currently expects NES 2.0; this ROM uses another iNES header format.")
    prg_msb = header[9] & 0x0F
    chr_msb = (header[9] >> 4) & 0x0F
    if prg_msb == 0x0F or chr_msb == 0x0F:
        raise ValueError("NES 2.0 exponent-multiplier sizes are not handled by this script.")
    prg_size = (header[4] | (prg_msb << 8)) * 0x4000
    chr_size = (header[5] | (chr_msb << 8)) * 0x2000
    end_prg = HEADER_SIZE + prg_size
    end_chr = end_prg + chr_size
    if end_chr > len(raw):
        raise ValueError(f"Header requests {end_chr} bytes, but ROM has {len(raw)} bytes.")
    prg = raw[HEADER_SIZE:end_prg]
    chr_rom = raw[end_prg:end_chr]
    mapper = (header[6] >> 4) | (header[7] & 0xF0) | ((header[8] & 0x0F) << 8)
    submapper = (header[8] >> 4) if nes2 else 0
    return raw, header, prg, chr_rom, mapper, submapper


def load_tbl(path: Path) -> dict[int, str]:
    mapping: dict[int, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if not line or line.lstrip().startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if len(key) != 2:
                continue
            try:
                code = int(key, 16)
            except ValueError:
                continue
            mapping[code] = value
    return mapping


def decode_with_tbl(buf: bytes, mapping: dict[int, str]) -> str:
    return "".join(mapping.get(value, f"<{value:02X}>") for value in buf)


def fixed_field_entry(prg: bytes, mapping: dict[int, str], index: int) -> dict:
    start = FIXED_TABLE_START + index * FIXED_TABLE_STRIDE
    field = prg[start:start + FIXED_TABLE_PAYLOAD]
    trailer = prg[start + FIXED_TABLE_PAYLOAD:start + FIXED_TABLE_STRIDE]
    if len(field) != FIXED_TABLE_PAYLOAD or len(trailer) != 2:
        raise ValueError(f"ROM too short for fixed field {index} at PRG offset 0x{start:X}.")
    decoded = decode_with_tbl(field, mapping)
    return {
        "id": f"fixed_label_{index:02d}",
        "category": "fixed_width_label_or_diagnostic_row",
        "confidence": "high for text content; medium for runtime display context",
        "prg_offset": f"0x{start:05X}",
        "file_offset": f"0x{HEADER_SIZE + start:05X}",
        "byte_length": len(field),
        "byte_length_limit": FIXED_TABLE_PAYLOAD,
        "length_limit_basis": "32-byte payload in a repeated 34-byte stride; the following 2 bytes are retained as unclassified metadata, not assumed to be a pointer",
        "original_text": decoded,
        "display_text_trimmed": decoded.strip(),
        "raw_hex": field.hex(" ").upper(),
        "trailing_metadata_hex": trailer.hex(" ").upper(),
        "trailing_metadata_interpretation": "unresolved; not confirmed to be a PRG pointer",
    }


def make_dump(rom_path: Path, tbl_path: Path) -> dict:
    raw, header, prg, chr_rom, mapper, submapper = load_rom(rom_path)
    mapping = load_tbl(tbl_path)
    body = raw[HEADER_SIZE:HEADER_SIZE + len(prg) + len(chr_rom)]
    body_crc = zlib.crc32(body) & 0xFFFFFFFF
    fixed_records = [fixed_field_entry(prg, mapping, i) for i in range(FIXED_TABLE_COUNT)]

    hud_raw = prg[HUD_START:HUD_START + HUD_LENGTH]
    if len(hud_raw) != HUD_LENGTH:
        raise ValueError("ROM too short for HUD template.")
    hud_decoded = decode_with_tbl(hud_raw, mapping)
    hud_record = {
        "id": "hud_template_score_life",
        "category": "hud_or_nametable_template",
        "confidence": "high for visible labels; medium for the exact editable-field boundary",
        "prg_offset": f"0x{HUD_START:05X}",
        "file_offset": f"0x{HEADER_SIZE + HUD_START:05X}",
        "byte_length": len(hud_raw),
        "byte_length_limit": HUD_LENGTH,
        "length_limit_basis": "bounded template span ending at a '#' marker; verify that marker's role in runtime before editing",
        "original_text": hud_decoded,
        "display_text_trimmed": hud_decoded.strip(),
        "raw_hex": hud_raw.hex(" ").upper(),
    }

    metadata_records = []
    for needle, label in [(b"DATE. 1992-12/20", "developer_build_date"), (b"01:10.20", "developer_build_time")]:
        pos = prg.find(needle)
        if pos >= 0:
            metadata_records.append({
                "id": label,
                "category": "embedded_developer_metadata",
                "confidence": "high for literal bytes; low for being player-visible",
                "prg_offset": f"0x{pos:05X}",
                "file_offset": f"0x{HEADER_SIZE + pos:05X}",
                "byte_length": len(needle),
                "byte_length_limit": len(needle),
                "length_limit_basis": "literal ASCII span only; not an editable text capacity",
                "original_text": needle.decode("ascii"),
                "display_text_trimmed": needle.decode("ascii"),
                "raw_hex": needle.hex(" ").upper(),
            })

    vectors_off = len(prg) - 6
    vectors = {
        "nmi": f"0x{int.from_bytes(prg[vectors_off:vectors_off+2], 'little'):04X}",
        "reset": f"0x{int.from_bytes(prg[vectors_off+2:vectors_off+4], 'little'):04X}",
        "irq_brk": f"0x{int.from_bytes(prg[vectors_off+4:vectors_off+6], 'little'):04X}",
        "vector_prg_offset": f"0x{vectors_off:05X}",
        "vector_bytes_hex": prg[vectors_off:vectors_off+6].hex(" ").upper(),
    }

    return {
        "schema_version": "1.0",
        "game": {
            "title_english_catalog": "Pyokotan no Dai Meiro",
            "title_japanese": "ぴょこたんの大迷路",
            "platform": "Famicom / NES",
            "region": "Japan",
            "release_year": 1993,
            "publisher": "Sunsoft",
            "developer": "Japan System Supply",
        },
        "rom_fingerprint": {
            "source_filename": rom_path.name,
            "rom_size_bytes": len(raw),
            "header_hex": header.hex(" ").upper(),
            "format": "NES 2.0",
            "mapper": mapper,
            "submapper": submapper,
            "prg_rom_bytes": len(prg),
            "prg_8k_bank_count": len(prg) // 0x2000,
            "chr_rom_bytes": len(chr_rom),
            "chr_8k_bank_count": len(chr_rom) // 0x2000,
            "crc32_full_file": f"{zlib.crc32(raw) & 0xFFFFFFFF:08X}",
            "crc32_prg_plus_chr": f"{body_crc:08X}",
            "crc32_prg": f"{zlib.crc32(prg) & 0xFFFFFFFF:08X}",
            "crc32_chr": f"{zlib.crc32(chr_rom) & 0xFFFFFFFF:08X}",
            "sha1_full_file": hashlib.sha1(raw).hexdigest(),
            "matches_reference_dump_fingerprint": body_crc == EXPECTED_BODY_CRC32,
        },
        "encoding_findings": {
            "confirmed_or_strongly_supported": [
                "Printable ASCII bytes 0x20–0x7E are present in the fixed-width label block, including game and mini-game labels.",
                "CHR bank 0 contains a readable ASCII-style tile range; the title/label bytes are consistent with ASCII codes.",
                "A Japanese glyph range is present in CHR bank 0. The supplied table maps 0xA1–0xDF as JIS X 0201 half-width katakana, but the runtime lookup path should be tested before injection.",
            ],
            "not_yet_confirmed": [
                "The full Japanese text code-to-tile mapping, especially codes 0x80–0x9F and 0xE0–0xFF.",
                "A complete pointer table for all in-game dialogue/text.",
                "Whether every detected label is shown during normal gameplay rather than a diagnostic/test path.",
            ],
        },
        "banking_and_vectors": {
            "mapper_note": "Mapper 69/Sunsoft FME-7 uses bank switching, so a CPU address cannot be converted to a unique file offset without the active PRG bank register state.",
            "interrupt_vectors": vectors,
            "reset_stub_at_prg_end": {
                "prg_offset": f"0x{len(prg)-0x30:05X}",
                "bytes_hex": prg[len(prg)-0x30:len(prg)-0x1E].hex(" ").upper(),
                "note": "The fixed-bank reset area contains mapper-register writes and a jump into a banked CPU window; runtime bank tracing is needed to follow text routines confidently.",
            },
        },
        "pointer_table_findings": {
            "confirmed_text_pointer_table": None,
            "fixed_width_text_structure": {
                "prg_offset_start": f"0x{FIXED_TABLE_START:05X}",
                "record_count": FIXED_TABLE_COUNT,
                "record_stride_bytes": FIXED_TABLE_STRIDE,
                "payload_bytes": FIXED_TABLE_PAYLOAD,
                "trailing_bytes_per_record": 2,
                "trailer_note": "Trailer values vary but are not safely interpretable as ROM pointers from static inspection alone.",
            },
            "unverified_banked_address_table_candidates": [
                {"prg_offset": "0x11376", "sample_targets": ["0x9436", "0x945D", "0x946A", "0x9477", "0x9484", "0x9491"], "assessment": "mixed/reused $94xx–$96xx address sequence; possible pointer/index table, text purpose unconfirmed"},
                {"prg_offset": "0x1139A", "sample_targets": ["0x94F9", "0x9520", "0x952D", "0x953A", "0x9543", "0x954C"], "assessment": "monotonic address-like sequence; likely data/code references, text purpose unconfirmed"},
                {"prg_offset": "0x113D2", "sample_targets": ["0x95CA", "0x9631", "0x9652", "0x9673", "0x9694", "0x96B5"], "assessment": "long monotonic address-like sequence; probable banked data table, text purpose unconfirmed"}
            ],
            "limitation": "No general pointer table is promoted to confirmed text-pointer status; these candidate address tables need runtime bank-state and cross-reference validation.",
        },
        "text_records": fixed_records + [hud_record],
        "metadata_records": metadata_records,
        "coverage_note": "This is a conservative first-pass static dump of confidently recognizable fields, not a claim that every Japanese message has been extracted. The remaining kana/kanji dialogue and text references need runtime tracing or a verified text routine before translation injection.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom", type=Path, help="Path to pyokotan.nes")
    ap.add_argument("--tbl", type=Path, default=Path(__file__).resolve().parents[1] / "pyokotan.tbl")
    ap.add_argument("--out", type=Path, default=Path("pyokotan_text_dump.json"))
    args = ap.parse_args()
    dump = make_dump(args.rom, args.tbl)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dump, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} ({len(dump['text_records'])} text records, {len(dump['metadata_records'])} metadata strings).")
    print("Coverage is conservative; see coverage_note in the JSON and rom_analysis.txt.")

if __name__ == "__main__":
    main()
