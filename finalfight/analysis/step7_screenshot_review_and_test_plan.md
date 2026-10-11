# Step 7 — screenshot review and refined accent-strip test

## User screenshot review

The supplied Step 6 screenshot shows that the first character was changed from `A` to the `À` candidate at the expected position. The accent is visible, but it looks like a short horizontal dash at display size. This is useful evidence that the candidate tile byte reached the renderer, while also revealing that the grave accent artwork should be redesigned. The screenshot does not prove every byte code is safe or that unused tiles are never referenced elsewhere.

## What changed

- Redesigned tone marks to use diagonal pixel strokes where space permits; composite glyphs with circumflex/breve/horn plus tone move the tone mark toward a free edge.
- Rebuilt all 67 candidate glyph tiles and generated `font_prototype_step7.png`, CSV, and packed binary.
- Created `Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips`, an experimental diagnostic patch. It writes the font tiles and replaces the first 13 characters of the opening line `A COUPLE DAYS` with `ÀÁÂÃÈÊÌÍÒÓÔÕÙ`. The next line `LATER...` is left unchanged. The edit remains 13 bytes long and does not move pointers.

## Validation

- Source ROM identity verified by size and body CRC32 `3F78037C`.
- All 67 candidate target tiles are blank in the source ROM.
- IPS application round-trips exactly to the expected diagnostic image.
- iNES header is unchanged; PRG changes are limited to the 13-byte opening-line probe, and CHR changes are limited to candidate glyph tiles.

## Limitations

The user screenshot is evidence for the Step 6 `À` test only. Step 7's 13-glyph strip has not yet been tested in an emulator. This remains a diagnostic patch, not a full translation release. Extended codes, other screens, credits, dialogue metadata, and glyph legibility still need validation.
