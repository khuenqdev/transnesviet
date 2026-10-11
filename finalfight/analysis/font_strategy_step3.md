# Font strategy — Step 3 results and next runtime task

## What Step 3 provides

- All 8 KiB CHR banks have been decoded as 512 8×8 2bpp tiles each.
- Every sheet labels tiles with the global hexadecimal tile ID, not just a bank-local index.
- The JSON inventory records blank-tile IDs, sparse-tile IDs, per-bank duplicate counts and checksums.
- `font_glyph_plan.csv` inventories the uppercase Vietnamese glyphs needed for a full-tone pass, including NFC glyphs and their Unicode decompositions.

A visual inspection also found a likely base font sequence at global tile IDs `0x1E10–0x1E29` (`A–Z`) and likely digit glyphs at `0x1E01–0x1E0A`. This fits the text encoding and suggests—but does not prove—the mapping `tile_id = 0x1E00 + text_byte`. See `font_candidate_observations_step3.md`.

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
