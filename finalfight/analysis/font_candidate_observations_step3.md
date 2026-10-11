# Step 3 visual observation — candidate base font region

## What is visible in the contact sheet

The zoom sheet `chr_bank15_first256_zoom.png` shows a strong, structured glyph sequence in the final 8 KiB CHR chunk:

- Global tile `0x1E00` is blank-looking.
- Global tiles `0x1E01–0x1E0A` visually resemble the digits `0–9` in order.
- Global tiles `0x1E10–0x1E29` visibly form `A–Z` in order.
- Global tiles around `0x1E2A–0x1E2C` look like low-density punctuation or small marks; inspect at runtime before assigning semantics.
- Another partial glyph-looking sequence appears at `0x1E60–0x1E7B`, but the contact sheet alone does not establish its role.
- `0x1E30–0x1E5F` and `0x1E7C–0x1E8F` look blank in the static dump. They are **candidates for further verification**, not approved overwrite space.

## Mapping hypothesis

The established text encoding uses `00` for space and `10–29` for `A–Z`. The visual correspondence is consistent with the hypothesis:

`global_tile_id = 0x1E00 + text_byte`

That would place space at `0x1E00` and `A–Z` at `0x1E10–0x1E29`. It is a strong static clue because the byte ranges line up, but it is **not yet proven** that the game’s `$F406` path uses this direct arithmetic or that this CHR chunk is mapped into the active pattern table throughout each dialog renderer.

## Why no glyph allocation is committed yet

The message decoder, opening/cutscene renderer, boss dialogue loader and credits renderer are separate paths. The game uses MMC3, whose live CHR mapping can change. In addition, byte values in the `0x2D–0x4E` range may serve structural/presentation roles in some dialogue records. Adding glyphs there without distinguishing body text from metadata could corrupt records. The runtime trace must establish (1) the CHR bank and pattern table in use, (2) the character-byte-to-tile lookup, and (3) a safe encoding range understood as text by all relevant renderers.

## Next validation

Use Mesen or FCEUX to pause on a known `A` in dialogue; follow the call into `$F406`; record `$0783`, any conversion/index registers, and the MMC3 CHR register state. Repeat for a digit and punctuation. If the resolved PPU tile matches the candidate mapping, trace all renderers and identify which blank-looking slots remain unreferenced before drawing Vietnamese glyphs.
