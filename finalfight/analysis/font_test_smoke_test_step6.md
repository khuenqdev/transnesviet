# Step 6 — Font render smoke test (experimental)

## Purpose

This is the first patch artifact intended for a short emulator check. It installs the 67 supplemental uppercase Vietnamese glyph tiles into candidate CHR slots that were blank in the exact source ROM, and changes one existing opening-text byte without altering its length or pointers. In the opening string `A COUPLE DAYS LATER...`, the initial `A` byte (`0x10`) becomes `0x30` so the game should attempt to draw `À` from tile `0x1E30`.

This is **not** a translated ROM. It includes only the one-character diagnostic substitution plus font tile art. No full ROM is included in the project archive; the user can apply the IPS patch to their own matching clean dump.

## Source compatibility

The patch is bound to the clean USA ROM with SHA-256:

`5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`

The included application script refuses a different ROM hash and verifies the resulting image hash before writing a local test copy.

## Build-time checks

- 67 supplemental glyph tiles (1,072 bytes of tile payload) loaded from the Step 5 CSV.
- All 67 target CHR tile slots were zero-filled in the clean input.
- Exactly one text byte is changed: file offset `0x001C9C`, `0x10` → `0x30` (`A` → `À`) in `OPEN_02`.
- iNES header preserved byte-for-byte.
- PRG preserved except the one-byte smoke-test edit.
- All other differences are restricted to the 67 candidate CHR tiles.
- IPS apply/round-trip matches the generated test image byte-for-byte.
- IPS size: 1,421 bytes; 68 records (67 tile records + 1 text probe).

## Manual emulator test

1. Keep a separate untouched copy of the clean ROM.
2. Apply `Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.ips` to that exact ROM, or use `tools/apply_font_test_ips_step6.py` (it checks the base and result hashes).
3. Open the diagnostic output in Mesen or FCEUX and play through the opening narration until `A COUPLE DAYS LATER...` appears.
4. Expected probe: the initial `A` appears as `À` with a visible grave mark, with spacing/alignment unchanged.
5. Check title/menu, background/sprite graphics, opening dialogue before/after the probe, and normal game progression for unexpected changes.
6. Do not use this patch for normal play. Return to the clean ROM after testing.

Record the emulator/version and attach screenshots if the glyph is missing, clipped, malformed, or if unrelated graphics change. No emulator was available in the build environment, so this step is **not emulator-validated**.

## Limits

The direct text-byte-to-PPU-tile mapping and tile allocation are still hypotheses supported by static code/CHR inspection. A passing smoke test would validate this one byte and renderer path only; it would not prove all dialogue encodings are safe or that all 67 glyphs are legible in every scene. Full text translation, pointer relocation, and full-game regression tests remain outstanding.
