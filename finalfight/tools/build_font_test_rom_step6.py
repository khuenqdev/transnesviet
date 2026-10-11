#!/usr/bin/env python3
"""Build a reversible CHR-only diagnostic ROM/IPS for MFF Vietnamese font.

This is an experimental font asset injection, NOT a translated/playable ROM.
It writes only the 67 candidate blank tile slots listed in the Step 5 CSV.
Requires only Python's standard library.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, struct, zlib
from pathlib import Path

DEFAULT_ROM = Path('/mnt/data/Mighty Final Fight (USA).nes')
DEFAULT_PROJECT = Path(__file__).resolve().parents[1]
CSV_REL = Path('analysis/font_prototype_tiles_step5.csv')
HEADER_LEN = 16
PRG_SIZE = 128 * 1024
CHR_START = HEADER_LEN + PRG_SIZE
TILE_BYTES = 16
# Opening dialogue OPEN_02 begins at file offset 0x01C9C with byte 0x10 ('A').
# Change that one byte to 0x30 ('À') as a same-length render smoke test.
PROBE_OFFSET = 0x01C9C
PROBE_OLD = 0x10
PROBE_NEW = 0x30


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_patch_csv(path: Path):
    entries = []
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            tile_id = int(row['global_chr_tile'], 16)
            text_byte = int(row['text_byte'], 16)
            rom_offset = int(row['chr_file_offset'], 16)
            data = bytes.fromhex(row['tile_bytes_hex'])
            expected_offset = CHR_START + tile_id * TILE_BYTES
            if len(data) != TILE_BYTES:
                raise ValueError(f"{row['glyph']}: tile payload is {len(data)} bytes, expected {TILE_BYTES}")
            if rom_offset != expected_offset:
                raise ValueError(f"{row['glyph']}: CSV offset {rom_offset:#x} != computed {expected_offset:#x}")
            if tile_id != 0x1E00 + text_byte:
                raise ValueError(f"{row['glyph']}: tile mapping does not match hypothesized 0x1E00 + byte mapping")
            entries.append({
                'glyph': row['glyph'], 'unicode': row['unicode'], 'text_byte': text_byte,
                'tile_id': tile_id, 'rom_offset': rom_offset, 'data': data,
            })
    if len(entries) != 67:
        raise ValueError(f'Expected 67 glyphs; found {len(entries)}')
    if len({e['rom_offset'] for e in entries}) != len(entries):
        raise ValueError('Duplicate ROM offsets found')
    return sorted(entries, key=lambda e: e['rom_offset'])


def make_ips(entries, extras=()) -> bytes:
    out = bytearray(b'PATCH')
    records = [(e['rom_offset'], e['data']) for e in entries] + list(extras)
    for off, data in sorted(records, key=lambda rec: rec[0]):
        if off >= 0x1000000:
            raise ValueError(f'IPS offset too large: {off:#x}')
        out.extend(off.to_bytes(3, 'big'))
        out.extend(len(data).to_bytes(2, 'big'))
        out.extend(data)
    out.extend(b'EOF')
    return bytes(out)


def apply_ips(source: bytes, patch: bytes) -> bytes:
    if not patch.startswith(b'PATCH'):
        raise ValueError('Invalid IPS header')
    out = bytearray(source)
    i = 5
    while True:
        if patch[i:i+3] == b'EOF':
            i += 3
            break
        if i + 5 > len(patch):
            raise ValueError('Truncated IPS record header')
        off = int.from_bytes(patch[i:i+3], 'big'); i += 3
        length = int.from_bytes(patch[i:i+2], 'big'); i += 2
        if length == 0:
            if i + 3 > len(patch):
                raise ValueError('Truncated IPS RLE record')
            rle_len = int.from_bytes(patch[i:i+2], 'big'); value = patch[i+2]
            i += 3
            data = bytes([value]) * rle_len
        else:
            if i + length > len(patch):
                raise ValueError('Truncated IPS record data')
            data = patch[i:i+length]; i += length
        if off + len(data) > len(out):
            out.extend(b'\x00' * (off + len(data) - len(out)))
        out[off:off+len(data)] = data
    if i != len(patch):
        raise ValueError('Unexpected bytes after IPS EOF')
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', type=Path, default=DEFAULT_ROM)
    ap.add_argument('--project', type=Path, default=DEFAULT_PROJECT)
    args = ap.parse_args()
    project = args.project.resolve()
    analysis = project / 'analysis'
    original = args.rom.read_bytes()
    if len(original) != 262160:
        raise ValueError(f'Unexpected source size: {len(original)}')
    if original[:4] != b'NES\x1a':
        raise ValueError('Not an iNES-family ROM')
    entries = load_patch_csv(analysis / CSV_REL.name)
    if original[PROBE_OFFSET] != PROBE_OLD:
        raise ValueError(f'Expected OPEN_02 first byte 0x{PROBE_OLD:02X} at {PROBE_OFFSET:#x}; found 0x{original[PROBE_OFFSET]:02X}')
    for e in entries:
        prior = original[e['rom_offset']:e['rom_offset'] + TILE_BYTES]
        if len(prior) != TILE_BYTES or any(prior):
            raise ValueError(f"Target tile not blank in source ROM: {e['glyph']} at {e['rom_offset']:#x}")
    modified = bytearray(original)
    for e in entries:
        modified[e['rom_offset']:e['rom_offset'] + TILE_BYTES] = e['data']
    modified[PROBE_OFFSET] = PROBE_NEW
    modified = bytes(modified)
    patch = make_ips(entries, extras=[(PROBE_OFFSET, bytes([PROBE_NEW]))])
    roundtrip = apply_ips(original, patch)
    if roundtrip != modified:
        raise AssertionError('IPS round-trip did not reproduce generated ROM')
    # Ensure the header and PRG are byte-identical and there are no differences outside designated slots.
    if modified[:HEADER_LEN] != original[:HEADER_LEN]:
        raise AssertionError('iNES header changed')
    if any(modified[i] != original[i] for i in range(HEADER_LEN, CHR_START) if i != PROBE_OFFSET):
        raise AssertionError('PRG changed outside the one-byte text probe')
    allowed = {PROBE_OFFSET}
    for e in entries:
        allowed.update(range(e['rom_offset'], e['rom_offset'] + TILE_BYTES))
    changed = [i for i, (a, b) in enumerate(zip(original, modified)) if a != b]
    if any(i not in allowed for i in changed):
        raise AssertionError('Unexpected ROM offsets changed')
    # Re-check that each target tile matches the intended tile art.
    for e in entries:
        got = modified[e['rom_offset']:e['rom_offset']+TILE_BYTES]
        if got != e['data']:
            raise AssertionError(f"Mismatch for {e['glyph']}")
    # Distribute only the small reversible IPS patch, not a full game ROM.
    ips_out = analysis / 'Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.ips'
    ips_out.write_bytes(patch)
    report = {
        'project_step': 6,
        'artifact_type': 'font-render smoke-test IPS patch; not a translated ROM',
        'source_rom': args.rom.name,
        'source_size_bytes': len(original),
        'source_sha256': sha256(original),
        'source_prg_crc32': f'{zlib.crc32(original[HEADER_LEN:CHR_START]) & 0xffffffff:08X}',
        'source_chr_crc32': f'{zlib.crc32(original[CHR_START:]) & 0xffffffff:08X}',
        'in_memory_patched_rom_size_bytes': len(modified),
        'in_memory_patched_rom_sha256': sha256(modified),
        'full_rom_file_distributed': False,
        'output_prg_crc32': f'{zlib.crc32(modified[HEADER_LEN:CHR_START]) & 0xffffffff:08X}',
        'output_chr_crc32': f'{zlib.crc32(modified[CHR_START:]) & 0xffffffff:08X}',
        'ips_patch': ips_out.name,
        'ips_size_bytes': len(patch),
        'ips_record_count': len(entries) + 1,
        'text_render_probe': {'file_offset': f'0x{PROBE_OFFSET:06X}', 'original_byte': f'0x{PROBE_OLD:02X}', 'test_byte': f'0x{PROBE_NEW:02X}', 'intended_change': 'A -> À in OPEN_02 string “A COUPLE DAYS LATER...”', 'same_byte_length': True},
        'glyph_count': len(entries),
        'glyph_bytes_injected': sum(len(e['data']) for e in entries),
        'changed_file_bytes': len(changed),
        'modified_offsets_span': [min(allowed), max(allowed)],
        'changed_offsets_all_in_candidate_tiles': True,
        'ines_header_unchanged': modified[:HEADER_LEN] == original[:HEADER_LEN],
        'prg_unchanged_except_probe_byte': all(modified[i] == original[i] for i in range(HEADER_LEN, CHR_START) if i != PROBE_OFFSET),
        'target_slots_blank_in_source': True,
        'ips_roundtrip_exact_match': roundtrip == modified,
        'emulator_tested': False,
        'production_ready': False,
        'warnings': [
            'Do not use as a production/playable translation patch.',
            'Only CHR glyph tiles and one diagnostic byte in OPEN_02 were changed; no translation was applied.',
            'The OPEN_02 probe intentionally displays À instead of A; revert to the clean ROM for normal play.',
            'In-game tile reuse must be checked in Mesen/FCEUX; otherwise unrelated graphics may change.',
            'The extended text-byte encoding and all dialogue formats remain runtime-unverified.'
        ],
        'modified_tiles': [
            {'glyph': e['glyph'], 'text_byte': f"0x{e['text_byte']:02X}",
             'global_chr_tile': f"0x{e['tile_id']:04X}", 'rom_offset': f"0x{e['rom_offset']:06X}"}
            for e in entries
        ],
    }
    report_path = analysis / 'font_test_rom_report_step6.json'
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    log_lines = [
        'STEP 6 FONT-ONLY DIAGNOSTIC BUILD',
        f'Source SHA-256: {sha256(original)}',
        f'In-memory patched image SHA-256: {sha256(modified)}',
        f'In-memory patched image bytes: {len(modified)} (not saved/distributed)',
        f'Glyphs injected: {len(entries)}',
        f'CHR bytes changed: {len(changed)}',
        f'IPS size: {len(patch)} bytes; records: {len(entries) + 1}',
        'PASS: same-length text probe changes OPEN_02 first glyph byte 0x10 (A) -> 0x30 (À)',
        'PASS: all 67 target tiles were blank in source ROM',
        'PASS: iNES header unchanged; PRG unchanged except the single text probe byte',
        'PASS: all file-byte changes are restricted to candidate CHR tiles plus the one-byte OPEN_02 probe',
        'PASS: IPS application reproduces output ROM byte-for-byte',
        'NOT TESTED: Mesen/FCEUX execution; in-game tile reuse; translation text injection',
        'STATUS: experimental font-render smoke-test IPS only; not a playable Vietnamese translation',
    ]
    (analysis / 'step6_font_test_build_validation.txt').write_text('\n'.join(log_lines) + '\n', encoding='utf-8')
    print('\n'.join(log_lines))

if __name__ == '__main__':
    main()
