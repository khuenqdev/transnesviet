# Step 5 — Vietnamese glyph artwork prototype

## Outputs

- `font_prototype_step5.png`: contact sheet of all 67 proposed uppercase Vietnamese glyphs, enlarged from 8x8 pixels.
- `font_prototype_tiles_step5.bin`: packed 16-byte-per-tile CHR data, ordered by ascending candidate text byte.
- `font_prototype_tiles_step5.csv`: glyph, Unicode code point, candidate byte/tile, component marks, and tile bytes.
- `byte_code_collision_audit_step5.csv`: separates candidate-byte matches in boss record headers from body-stream matches under the current dump layout.
- `font_prototype_validation_step5.json`: ROM identity, reproducibility metadata, and limitations.

## Method

The generator starts from this ROM's existing A-Z tiles, shrinks the uppercase body into rows 2-6, then draws compact Vietnamese marks within the remaining pixels. It creates precomposed single-tile glyphs so a text string remains one byte per displayed character. The proposed code and tile slots are taken from the Step 4 allocation CSV.

## Status and limitations

This is a **visual prototype only**. The raw dump shows `0x35` as a recurring boss render-segment marker (and `0x2B` as an initial boss layout-header variant), so the prototype deliberately avoids assigning that byte to a glyph and places `É` at spare byte/tile `0x8F` instead. The generator does not modify the ROM and does not assert that any candidate byte is safe in all dialogue paths. The raw-byte audit is only a clue: a matching byte may be a header, a layout parameter, a control code, or body text. Before injection, the glyph shapes need a visual legibility review, and Mesen/FCEUX runtime checks must verify both glyph display and absence of unintended tile usage in other screens.

ROM body CRC32: `3F78037C`  
ROM SHA-256: `5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`  
Glyph tiles generated: **67** (1072 bytes).  
Candidate raw-record byte occurrences for allocated glyph codes: **78** total; **78** occur in boss segment headers and **0** in body streams under the current dump layout. Reserved boss segment marker `0x35` occurs **61** times in the dump and is not assigned to a glyph; `É` is remapped to spare byte/tile `0x8F`.
