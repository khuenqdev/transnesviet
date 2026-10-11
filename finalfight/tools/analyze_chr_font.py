#!/usr/bin/env python3
"""Inventory and render the CHR graphics in Mighty Final Fight (NES).

This script is an analysis aid only. It never modifies the ROM or assigns live
font tile IDs; those require runtime bank-selection and tile-lookup tracing.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, zlib
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TILE_BYTES = 16
TILE_PIXELS = 8
TILES_PER_BANK = 512
BANK_BYTES = TILE_BYTES * TILES_PER_BANK
PALETTE = [(18, 20, 24), (105, 111, 119), (184, 190, 197), (250, 250, 246)]


def decode_tile(data: bytes) -> list[list[int]]:
    if len(data) != 16:
        raise ValueError('Expected exactly 16 bytes per 8x8 NES 2bpp tile')
    rows = []
    for y in range(8):
        p0, p1 = data[y], data[y + 8]
        row = []
        for x in range(8):
            bit = 7 - x
            row.append(((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1))
        rows.append(row)
    return rows


def tile_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:16]


def render_bank(bank_tiles: list[bytes], bank_index: int, output: Path) -> None:
    # 32 columns x 16 rows, with the global tile number printed below every tile.
    cols, rows = 32, 16
    scale, label_h, gap, margin = 3, 10, 2, 6
    cell_w = 8 * scale + 2 * gap
    cell_h = 8 * scale + label_h + 2 * gap
    width = margin * 2 + cols * cell_w
    height = margin * 2 + rows * cell_h + 24
    img = Image.new('RGB', (width, height), (238, 239, 241))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((margin, margin), f'CHR bank {bank_index:02d}  |  global tile IDs {bank_index*512:04X}-{bank_index*512+511:04X}', fill=(10, 10, 10), font=font)
    y0 = margin + 20
    for local_id, raw in enumerate(bank_tiles):
        r, c = divmod(local_id, cols)
        x = margin + c * cell_w + gap
        y = y0 + r * cell_h + gap
        pix = decode_tile(raw)
        for py, prow in enumerate(pix):
            for px, value in enumerate(prow):
                col = PALETTE[value]
                x1 = x + px * scale
                y1 = y + py * scale
                draw.rectangle((x1, y1, x1 + scale - 1, y1 + scale - 1), fill=col)
        gid = bank_index * TILES_PER_BANK + local_id
        label = f'{gid:04X}'
        draw.text((x, y + 8 * scale + 1), label, fill=(28, 28, 28), font=font)
    img.save(output, optimize=True)


def render_zoom(tiles: list[bytes], first_global_id: int, output: Path) -> None:
    """Render 256 sequential tile IDs as a larger 16x16 contact sheet."""
    cols, rows, scale, label_h, gap, margin = 16, 16, 6, 13, 5, 10
    cell_w = 8 * scale + 2 * gap
    cell_h = 8 * scale + label_h + 2 * gap
    width = margin * 2 + cols * cell_w
    height = margin * 2 + rows * cell_h + 24
    img = Image.new('RGB', (width, height), (238, 239, 241))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((margin, margin), f'Zoomed tiles {first_global_id:04X}-{first_global_id + len(tiles) - 1:04X} (global IDs)', fill=(10, 10, 10), font=font)
    y0 = margin + 20
    for index, raw in enumerate(tiles):
        r, c = divmod(index, cols)
        x = margin + c * cell_w + gap
        y = y0 + r * cell_h + gap
        for py, row in enumerate(decode_tile(raw)):
            for px, value in enumerate(row):
                x1, y1 = x + px * scale, y + py * scale
                draw.rectangle((x1, y1, x1 + scale - 1, y1 + scale - 1), fill=PALETTE[value])
        draw.text((x, y + 8 * scale + 1), f'{first_global_id + index:04X}', fill=(28, 28, 28), font=font)
    img.save(output, optimize=True)


def render_montage(bank_stats: list[dict], out: Path) -> None:
    # Use the 8x8 tile signatures in a small sample grid to summarize visual density.
    # The individual bank contact sheets remain the authoritative labeled sheets.
    thumb_w, thumb_h = 360, 206
    canvas = Image.new('RGB', (thumb_w * 4, thumb_h * 4), (233, 235, 238))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.load_default()
    for item in bank_stats:
        i = item['bank']
        x, y = (i % 4) * thumb_w, (i // 4) * thumb_h
        d.rectangle((x + 2, y + 2, x + thumb_w - 3, y + thumb_h - 3), outline=(110, 114, 120), width=1)
        d.text((x + 10, y + 8), f"BANK {i:02d}  unique={item['unique_tiles']}  blank={item['blank_tiles']}", font=f, fill=(15, 15, 15))
        # Density histogram, normalized to 320x120.
        hist = item['nonzero_pixel_histogram']
        maxv = max(hist) if hist else 1
        left, top, bw, bh = x + 16, y + 34, 320, 112
        d.rectangle((left, top, left + bw, top + bh), outline=(150, 153, 158))
        for idx, count in enumerate(hist):
            barw = max(1, bw // 65)
            bx = left + int(idx * (bw / max(1, len(hist))))
            barh = max(1, int((count / maxv) * (bh - 6)))
            d.rectangle((bx, top + bh - barh, bx + barw, top + bh - 1), fill=(61, 89, 122))
        d.text((x + 10, y + 153), 'Pixels used per tile (0..64); histogram scaled per bank', font=f, fill=(35, 35, 35))
        d.text((x + 10, y + 172), f"CRC32={item['crc32']}  repeated signatures={item['duplicate_excess']}", font=f, fill=(35, 35, 35))
    canvas.save(out, optimize=True)


def build_glyph_rows() -> list[dict]:
    # Full intended Vietnamese uppercase glyph inventory. Tile/code assignment is deliberately TBD.
    glyphs = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    groups = [
        'A Á À Ả Ã Ạ Ă Ắ Ằ Ẳ Ẵ Ặ Â Ấ Ầ Ẩ Ẫ Ậ',
        'E É È Ẻ Ẽ Ẹ Ê Ế Ề Ể Ễ Ệ',
        'I Í Ì Ỉ Ĩ Ị',
        'O Ó Ò Ỏ Õ Ọ Ô Ố Ồ Ổ Ỗ Ộ Ơ Ớ Ờ Ở Ỡ Ợ',
        'U Ú Ù Ủ Ũ Ụ Ư Ứ Ừ Ử Ữ Ự',
        'Y Ý Ỳ Ỷ Ỹ Ỵ',
        'Đ',
    ]
    for group in groups:
        glyphs.update(group.split())
    rows = []
    for ch in sorted(glyphs, key=lambda s: (ord(s), s)):
        decomp = ch
        import unicodedata
        nfd = unicodedata.normalize('NFD', ch)
        marks = ''.join(c for c in nfd if unicodedata.combining(c))
        base = ''.join(c for c in nfd if not unicodedata.combining(c))
        rows.append({
            'glyph': ch,
            'codepoint': f'U+{ord(ch):04X}',
            'nfc': ch,
            'nfd_decomposition': ' + '.join(f'U+{ord(c):04X} {unicodedata.name(c, "UNKNOWN")}' for c in nfd),
            'base_letter': base,
            'combining_marks': marks or '(none)',
            'text_byte': 'TBD',
            'chr_bank': 'TBD',
            'global_tile_id': 'TBD',
            'status': 'PLANNED_NOT_MAPPED',
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', default='/mnt/data/Mighty Final Fight (USA).nes')
    ap.add_argument('--project', default='/mnt/data/Mighty_Final_Fight_Vietnamese_Project')
    args = ap.parse_args()
    rom_path = Path(args.rom)
    project = Path(args.project)
    analysis = project / 'analysis'
    analysis.mkdir(parents=True, exist_ok=True)
    raw = rom_path.read_bytes()
    if raw[:4] != b'NES\x1a':
        raise SystemExit('Input does not have an iNES signature')
    prg_size = raw[4] * 16384
    chr_size = raw[5] * 8192
    trainer_size = 512 if raw[6] & 0x04 else 0
    chr_start = 16 + trainer_size + prg_size
    chr_end = chr_start + chr_size
    if len(raw) < chr_end:
        raise SystemExit(f'ROM shorter than declared CHR payload: need {chr_end}, got {len(raw)}')
    chr_data = raw[chr_start:chr_end]
    if len(chr_data) != 131072 or len(chr_data) % BANK_BYTES:
        raise SystemExit(f'Unexpected CHR size {len(chr_data)}; expected 131072 bytes (16 x 8 KiB)')

    all_tiles = [chr_data[i:i+TILE_BYTES] for i in range(0, len(chr_data), TILE_BYTES)]
    global_counts = Counter(tile_hash(t) for t in all_tiles)
    bank_stats = []
    sheets = []
    for bank in range(chr_size // BANK_BYTES):
        bank_tiles = all_tiles[bank*TILES_PER_BANK:(bank+1)*TILES_PER_BANK]
        hashes = [tile_hash(t) for t in bank_tiles]
        nonzero_hist = [0] * 65
        blank_ids = []
        one_color_or_sparse_ids = []
        for local_id, tile in enumerate(bank_tiles):
            pix = decode_tile(tile)
            nonzero = sum(px != 0 for row in pix for px in row)
            nonzero_hist[nonzero] += 1
            if nonzero == 0:
                blank_ids.append(bank*TILES_PER_BANK + local_id)
            if nonzero <= 12:
                one_color_or_sparse_ids.append(bank*TILES_PER_BANK + local_id)
        unique = len(set(hashes))
        item = {
            'bank': bank,
            'file_offset_start': chr_start + bank * BANK_BYTES,
            'file_offset_end_exclusive': chr_start + (bank + 1) * BANK_BYTES,
            'global_tile_id_start': bank*TILES_PER_BANK,
            'global_tile_id_end_inclusive': bank*TILES_PER_BANK + TILES_PER_BANK - 1,
            'tile_count': len(bank_tiles),
            'unique_tiles': unique,
            'duplicate_excess': len(bank_tiles) - unique,
            'blank_tiles': len(blank_ids),
            'blank_global_tile_ids': blank_ids,
            'sparse_tiles_nonzero_pixels_le_12': len(one_color_or_sparse_ids),
            'sparse_global_tile_ids_nonzero_pixels_le_12': one_color_or_sparse_ids,
            'nonzero_pixel_histogram': nonzero_hist,
            'crc32': f'{zlib.crc32(b"".join(bank_tiles)) & 0xffffffff:08X}',
            'sha256': hashlib.sha256(b''.join(bank_tiles)).hexdigest(),
        }
        bank_stats.append(item)
        out = analysis / f'chr_bank_{bank:02d}_tiles.png'
        render_bank(bank_tiles, bank, out)
        sheets.append(out.name)

    duplicate_groups = defaultdict(list)
    for idx, tile in enumerate(all_tiles):
        duplicate_groups[tile_hash(tile)].append(idx)
    duplicate_groups_list = [ids for ids in duplicate_groups.values() if len(ids) > 1]
    inventory = {
        'source_rom': rom_path.name,
        'source_rom_sha256': hashlib.sha256(raw).hexdigest(),
        'source_rom_crc32': f'{zlib.crc32(raw) & 0xffffffff:08X}',
        'header_declared_prg_bytes': prg_size,
        'header_declared_chr_bytes': chr_size,
        'chr_file_offset_start': chr_start,
        'chr_file_offset_end_exclusive': chr_end,
        'tile_format': 'NES 2bpp planar 8x8, 16 bytes/tile, plane 0 then plane 1',
        'total_tiles': len(all_tiles),
        'banks': bank_stats,
        'global_unique_tiles': len(global_counts),
        'global_duplicate_excess': len(all_tiles) - len(global_counts),
        'global_duplicate_groups_count': len(duplicate_groups_list),
        'global_duplicate_groups': duplicate_groups_list,
        'contact_sheets': sheets,
        'montage': 'chr_banks_montage.png',
        'limitations': [
            'A static CHR inventory does not establish that any particular tile is unused at runtime.',
            'MMC3 bank mappings and write order must be traced during text rendering before a glyph tile can be overwritten or used.',
            'Text byte-to-tile conversion through the $F406 path is not yet proven from this inventory alone.',
        ],
    }
    (analysis / 'chr_inventory.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    render_montage(bank_stats, analysis / 'chr_banks_montage.png')
    # This is a zoomed contact sheet for inspection, not a declaration that the range is font-only.
    zoom_start = 15 * TILES_PER_BANK
    render_zoom(all_tiles[zoom_start:zoom_start + 256], zoom_start, analysis / 'chr_bank15_first256_zoom.png')

    glyph_rows = build_glyph_rows()
    import csv
    with (analysis / 'font_glyph_plan.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(glyph_rows[0].keys()))
        writer.writeheader()
        writer.writerows(glyph_rows)

    lines = [
        '# Step 3 — CHR graphics inventory and font tile sheets', '',
        f'- Source ROM: `{rom_path.name}`',
        f'- ROM SHA-256: `{hashlib.sha256(raw).hexdigest()}`',
        f'- CHR payload: {chr_size:,} bytes, offsets `0x{chr_start:06X}–0x{chr_end-1:06X}`',
        f'- Decoded tiles: {len(all_tiles):,} 8×8 2bpp tiles ({len(bank_stats)} banks × {TILES_PER_BANK} tiles)',
        f'- Globally unique tile patterns (SHA-256 prefix signatures): {len(global_counts):,}',
        f'- Duplicate excess tile instances: {len(all_tiles)-len(global_counts):,}', '',
        '## Bank summary', '',
        '| CHR bank | Global tile IDs | Unique patterns | Blank tiles | Sparse tiles (≤12 nonzero pixels) | CRC32 |',
        '|---:|---|---:|---:|---:|---|',
    ]
    for b in bank_stats:
        lines.append(f"| {b['bank']:02d} | {b['global_tile_id_start']:04X}–{b['global_tile_id_end_inclusive']:04X} | {b['unique_tiles']} | {b['blank_tiles']} | {b['sparse_tiles_nonzero_pixels_le_12']} | `{b['crc32']}` |")
    lines += ['', '## Generated assets', '',
              '- `chr_banks_montage.png`: 4×4 overview of density metrics per bank.',
              '- `chr_bank15_first256_zoom.png`: larger view of global tile IDs `1E00–1EFF` for manual glyph-pattern inspection; not certified font-only space.',
              '- `chr_bank_00_tiles.png` through `chr_bank_15_tiles.png`: labeled contact sheets. Tile labels are **global CHR tile IDs in hexadecimal**.',
              '- `chr_inventory.json`: full tile/bank inventory, blank IDs, sparse IDs and duplicate groups.',
              '- `font_glyph_plan.csv`: intended uppercase Vietnamese glyph set; text bytes and tile IDs intentionally remain `TBD`.', '',
              '## Interpretation and safety boundary', '',
              'This is a static inventory, not a safe-tile certification. Blank or repeated tiles may still be used by gameplay, animation, effects, sprites, or a different MMC3 CHR mapping. Do not overwrite them based only on their visual appearance. Before assigning full-tone Vietnamese glyphs, capture the MMC3 CHR-bank register writes during a real dialogue, trace the `$F406` text-character path to its final tile index, and confirm which CHR bank is mapped to the background pattern table at that moment.', '',
              '## Result of this step', '',
              'The CHR payload has been decoded and visualized for manual inspection. No ROM bytes have been changed, and no translated ROM or patch is produced in this step.']
    (analysis / 'chr_font_analysis_step3.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    strategy = '''# Font strategy — Step 3 results and next runtime task

## What Step 3 provides

- All 8 KiB CHR banks have been decoded as 512 8×8 2bpp tiles each.
- Every sheet labels tiles with the global hexadecimal tile ID, not just a bank-local index.
- The JSON inventory records blank-tile IDs, sparse-tile IDs, per-bank duplicate counts and checksums.
- `font_glyph_plan.csv` inventories the uppercase Vietnamese glyphs needed for a full-tone pass, including NFC glyphs and their Unicode decompositions.

## What it does not prove

A blank-looking or repeated CHR tile is not necessarily safe to replace. It may be selected by a different MMC3 bank register, loaded for animation, or used by sprites/effects. Likewise, the global tile ID is a file-layout identifier; it does not automatically equal the tile index used by the text renderer at runtime.

## Next step: trace runtime text rendering

1. Run the game to a scene with dialogue and set a breakpoint on the CPU call site that invokes `$F406`.
2. Record the code byte at `$0783` and the value(s) it is converted into before pattern-table access.
3. Break on writes to MMC3 CHR bank registers ($8000/$8001 when configured for bank select/data, or the game's register-write wrapper). Record CHR mappings during dialogue and during gameplay.
4. Identify whether the dialog uses background tiles or sprite tiles, which pattern table is selected, and how the text renderer resolves a character byte to a tile number.
5. Compare the runtime mapping with the contact sheets; only then mark candidate tiles as `RUNTIME_VERIFIED_AVAILABLE`.
6. Implement glyphs at 8×8 fixed width, reserving top pixels for acute, grave, hook, tilde and dot-below; reserve clear top-space for breve/circumflex/horn. Test the rendered lines in the actual box width and verify baseline alignment.

## Encoding policy

Keep the game’s existing one-byte text model for the first pass. Use precomposed uppercase Unicode input normalized to NFC in the translation source, then assign each supported glyph a distinct available in-game byte after the renderer mapping is understood. Do not inject raw UTF-8 bytes into the ROM text stream.
'''
    (analysis / 'font_strategy_step3.md').write_text(strategy, encoding='utf-8')

    # Write a compact manifest for the whole pack and update readme with truthful state.
    (project / 'project_manifest.json').write_text(json.dumps({
        'project': 'Mighty Final Fight Vietnamese translation groundwork',
        'step': 3,
        'source_rom': rom_path.name,
        'source_rom_sha256': hashlib.sha256(raw).hexdigest(),
        'source_rom_crc32': f'{zlib.crc32(raw) & 0xffffffff:08X}',
        'files_added_step3': [
            'analysis/chr_inventory.json', 'analysis/chr_font_analysis_step3.md',
            'analysis/chr_banks_montage.png', 'analysis/chr_bank15_first256_zoom.png', 'analysis/chr_bank_00_tiles.png through analysis/chr_bank_15_tiles.png',
            'analysis/font_glyph_plan.csv', 'analysis/font_strategy_step3.md', 'tools/analyze_chr_font.py'
        ],
        'rom_modified': False,
        'translated_rom_included': False,
        'blocking_unknowns': [
            'runtime MMC3 CHR bank mapping during dialogue',
            'exact character-byte to tile-index transformation in the $F406 render path',
            'safe font tile region or need for CHR expansion'
        ]
    }, indent=2) + '\n', encoding='utf-8')

    readme = project / 'README.md'
    old = readme.read_text(encoding='utf-8')
    if '## Step 3 completed' not in old:
        old += '''\n\n## Step 3 completed — static CHR inventory\n\nAdded a decoded inventory and labeled contact sheets for all 16 CHR banks (8,192 tiles), plus a full-tone uppercase Vietnamese glyph plan. This is static graphics analysis only: it does not certify tiles as unused and does not modify the ROM. The next blocker is dynamic verification of MMC3 CHR bank mappings and the character-byte lookup reached through `$F406`. See `analysis/chr_font_analysis_step3.md` and `analysis/font_strategy_step3.md`.\n'''
        readme.write_text(old, encoding='utf-8')

    print(json.dumps({
        'status': 'OK',
        'source_rom': str(rom_path),
        'project': str(project),
        'tiles': len(all_tiles),
        'banks': len(bank_stats),
        'global_unique_tiles': len(global_counts),
        'glyph_rows': len(glyph_rows),
        'files_generated': len(sheets) + 6,
        'rom_modified': False,
    }, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
