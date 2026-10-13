# Font and Vietnamese Diacritic Design Notes

## Separate visual-design bugs from encoding/bank bugs

An accented glyph can fail for several different reasons:

1. **Artwork defect:** the correct tile is fetched but the bitmap is visually ambiguous (for example `Ồ` looks like `Ố`).
2. **Text-code collision:** a new character byte is already a control, metadata, or animation code.
3. **Wrong tile ID:** the decoder maps a text byte to the wrong tile.
4. **Wrong active CHR bank:** the PPU tile ID is correct but MMC3 supplies different graphics.
5. **Wrong renderer assumptions:** opening, dialogue, credits, or HUD do not use the same path.
6. **Bad hook state:** injected code corrupts A/X/Y, flags, stack, RAM temporaries, or PPU latch/address.

Diagnose in that order before redrawing artwork blindly. Capture the input byte, resulting tile ID, PPU address, active CHR register/bank, and screen context.

## Composite glyph strategy

One tile represents a complete accented letter. It is easier to integrate into renderers that write one tile per character, but an 8x8 cell has little room for the base, horn/circumflex/breve, tone mark, and under-dot simultaneously. Inspect bitmaps at native 8x8 scale and through emulator screenshots, not only enlarged mockups.

Quality rules:
- Preserve the recognizable base letter silhouette first.
- Keep tone mark position consistent across vowels.
- Ensure `acute` and `grave` have visibly different slopes.
- Avoid letting `hook` merge into `horn`.
- Do not let a dot-under letter become shorter/squashed than its unaccented base.
- Make `Đ` distinguishable from `B` and `D` at 8x8.
- Distinguish `Ồ` from `Ố` by accent slope, not just one ambiguous pixel.

## Split-mark strategy (article-derived concept)

The Contra/Kontora article by STONE BOAT describes storing base glyphs and tone marks separately. A logical accented character maps to a base tile plus an upper mark; dot-below forms may require a lower-mark row. When a circumflex/breve/horn modifies the base, use a suitable base variant in addition to tone mark logic. Some characters require both upper and lower marks, so the renderer needs a three-row arrangement or a custom combined-mark tile.

Transferable implementation outline:

1. Assign each supported logical character an encoded byte/code point that is not in conflict with controls.
2. Map it to `(base_tile, upper_mark, lower_mark)` where each mark can be none.
3. Determine the PPU tile row/column for the base character.
4. Place upper and lower marks in safe adjacent rows/columns.
5. Verify top/bottom rows are not shared with another line or UI element.
6. Ensure page clearing erases all rows used by marks.
7. Ensure text speed, line breaks, punctuation, and right-edge handling still work.
8. Test line overlap, consecutive accented characters, spaces, punctuation, and the first/last character on every row.

Do not apply the article's exact CPU addresses or mapper writes. Its Contra/Kontora example uses a different game and mapper. Mighty Final Fight is MMC3, and its custom bank selection must be handled with its own runtime trace.

## Why the case-study project used composite tiles first

The user prioritized making the opening translation render correctly with minimal text-engine changes. Composite glyphs made it possible to validate a small pilot faster. The high-byte glyph failure turned out to be a CHR-bank mismatch, not simply artwork quality. Step 17 expanded CHR and copied glyphs into the active contexts. That was user-confirmed for the tested opening/bank-fix context. The remaining boss/credits high-byte routing was not assumed, so Step 20 used a safer mapped character subset there.

## Font QA grid

Build a test string or scene that includes all of:

- `A Á À Ả Ã Ạ Ă Ắ Ằ Ẳ Ẵ Ặ Â Ấ Ầ Ẩ Ẫ Ậ`
- `E É È Ẻ Ẽ Ẹ Ê Ế Ề Ể Ễ Ệ`
- `I Í Ì Ỉ Ĩ Ị`
- `O Ó Ò Ỏ Õ Ọ Ô Ố Ồ Ổ Ỗ Ộ Ơ Ớ Ờ Ở Ỡ Ợ`
- `U Ú Ù Ủ Ũ Ụ Ư Ứ Ừ Ử Ữ Ự`
- `Y Ý Ỳ Ỷ Ỹ Ỵ`
- `Đ` plus punctuation, spaces, and the game's line-break/end markers.

Review the actual text-renderer output, not only a font sheet. For a glyph used in multiple bank contexts, test each context explicitly.
