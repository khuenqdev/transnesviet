# Step 3 — CHR graphics inventory and font tile sheets

- Source ROM: `Mighty Final Fight (USA).nes`
- ROM SHA-256: `5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`
- CHR payload: 131,072 bytes, offsets `0x020010–0x04000F`
- Decoded tiles: 8,192 8×8 2bpp tiles (16 banks × 512 tiles)
- Globally unique tile patterns (SHA-256 prefix signatures): 6,262
- Duplicate excess tile instances: 1,930

## Bank summary

| CHR bank | Global tile IDs | Unique patterns | Blank tiles | Sparse tiles (≤12 nonzero pixels) | CRC32 |
|---:|---|---:|---:|---:|---|
| 00 | 0000–01FF | 439 | 22 | 72 | `E9A13166` |
| 01 | 0200–03FF | 415 | 42 | 96 | `18BF94EA` |
| 02 | 0400–05FF | 392 | 74 | 128 | `5208B538` |
| 03 | 0600–07FF | 406 | 49 | 98 | `12663AD9` |
| 04 | 0800–09FF | 410 | 67 | 116 | `A18138EA` |
| 05 | 0A00–0BFF | 419 | 67 | 137 | `60F68517` |
| 06 | 0C00–0DFF | 412 | 100 | 165 | `229F3199` |
| 07 | 0E00–0FFF | 447 | 34 | 113 | `DE314E89` |
| 08 | 1000–11FF | 434 | 2 | 36 | `BC397475` |
| 09 | 1200–13FF | 488 | 3 | 15 | `537ADB3C` |
| 10 | 1400–15FF | 485 | 5 | 40 | `6510C918` |
| 11 | 1600–17FF | 428 | 3 | 60 | `71123007` |
| 12 | 1800–19FF | 471 | 7 | 57 | `DA47D255` |
| 13 | 1A00–1BFF | 467 | 4 | 43 | `1DCB63DB` |
| 14 | 1C00–1DFF | 482 | 5 | 54 | `5B9347FB` |
| 15 | 1E00–1FFF | 334 | 109 | 145 | `7E7AF912` |

## Generated assets

- `chr_banks_montage.png`: 4×4 overview of density metrics per bank.
- `chr_bank15_first256_zoom.png`: larger view of global tile IDs `1E00–1EFF` for manual glyph-pattern inspection; not certified font-only space.
- `chr_bank15_first256_zoom.png`: larger view of global tile IDs `1E00–1EFF` for manual glyph-pattern inspection; not certified font-only space.
- `chr_bank_00_tiles.png` through `chr_bank_15_tiles.png`: labeled contact sheets. Tile labels are **global CHR tile IDs in hexadecimal**.
- `chr_inventory.json`: full tile/bank inventory, blank IDs, sparse IDs and duplicate groups.
- `font_glyph_plan.csv`: intended uppercase Vietnamese glyph set; text bytes and tile IDs intentionally remain `TBD`.
- `font_candidate_observations_step3.md`: visual candidate mapping and runtime verification requirements.

## Interpretation and safety boundary

This is a static inventory, not a safe-tile certification. Blank or repeated tiles may still be used by gameplay, animation, effects, sprites, or a different MMC3 CHR mapping. Do not overwrite them based only on their visual appearance. Before assigning full-tone Vietnamese glyphs, capture the MMC3 CHR-bank register writes during a real dialogue, trace the `$F406` text-character path to its final tile index, and confirm which CHR bank is mapped to the background pattern table at that moment.

## Result of this step

The CHR payload has been decoded and visualized for manual inspection. No ROM bytes have been changed, and no translated ROM or patch is produced in this step.
