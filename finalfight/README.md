# Mighty Final Fight — Vietnamese Translation Project

This pack is the reverse-engineering and translation groundwork for the supplied USA ROM.

## What is complete

- ROM identity/hash verification
- MMC3/mapper-4 structure identification
- verified custom text alphabet
- confirmed opening/ending text location
- confirmed boss/encounter text location
- confirmed credits location
- `.tbl` mapping
- extraction script
- Vietnamese draft for the confirmed dialogue blocks
- full-tone font requirements and implementation strategy
- safe build scaffold that refuses to patch until pointer/font layout is verified

## What is deliberately not claimed complete

A final translated ROM is not included yet. The remaining work is runtime verification of
pointer tables, dialog writer behavior, CHR font-bank selection, and relocation mechanics.
That verification is necessary to prevent a seemingly successful build from corrupting the game.

## Files

- `02_TRANSLATION_PLAN.md` — step-by-step plan
- `mighty_final_fight.tbl` — verified custom alphabet/control mapping
- `analysis/rom_analysis.json` — machine-readable ROM facts
- `analysis/confirmed_text_extract.txt` — confirmed extracted blocks
- `analysis/vietnamese_draft_confirmed_blocks.md` — first Vietnamese draft
- `analysis/font_strategy.md` — full-tone font plan
- `tools/analyze_mff.py` — ROM validator
- `tools/extract_mff_text.py` — text extractor
- `tools/build_vn_scaffold.py` — guarded build scaffold

## Baseline checksum

PRG+CHR body CRC32: `3F78037C`


## Step 2 completed

The pointer tables and message-reader paths have now been verified statically.

Verified:
- 7 opening/cutscene message pointers
- 78 boss/encounter dialogue pointers
- 5 credits pointers
- opening renderer and its RAM pointer construction
- boss pointer loader and its two pointer arrays
- credits pointer arrays
- ordinary text character codes and key controls
- render-command area `$0780-$0784`
- character pipeline call `JSR $F406`

The exact font-tile lookup inside the `$F406` path remains the next task.


## Step 3 completed — static CHR inventory

Added a decoded inventory and labeled contact sheets for all 16 CHR banks (8,192 tiles), plus a full-tone uppercase Vietnamese glyph plan. This is static graphics analysis only: it does not certify tiles as unused and does not modify the ROM. The next blocker is dynamic verification of MMC3 CHR bank mappings and the character-byte lookup reached through `$F406`. A visual candidate base font sequence is visible around global tile IDs `0x1E01–0x1E29`; the direct mapping hypothesis remains unverified at runtime. See `analysis/chr_font_analysis_step3.md`, `analysis/font_candidate_observations_step3.md` and `analysis/font_strategy_step3.md`.


## Step 4 completed — static text-to-PPU mapping

The fixed-bank VRAM-command consumer at `$C1FD-$C221` reads the queued glyph byte from `$0783,X` and writes it directly to `$2007`. The NMI setup maps MMC3 CHR registers 0/1 to `0x78/0x7A`, and the PPUCTRL shadow is initialized to `0x88`; this statically supports the candidate tile relationship `global CHR tile = 0x1E00 + text byte`.

A candidate map for all 67 Vietnamese-specific uppercase glyphs is supplied in `analysis/font_glyph_allocation_candidate_step4.csv`. It uses source tiles that are currently blank, leaving `0x8F` spare. **The assignments are planning-only**: dynamic checks must still establish that the candidate IDs are not referenced by existing screens and that each dialogue renderer accepts the proposed extended bytes. The ROM remains unchanged; no playable translated ROM or patch is claimed complete.

See `analysis/runtime_text_renderer_step4.md`, `analysis/runtime_code_evidence_step4.json`, `analysis/candidate_vietnamese_tile_slots_step4.csv`, `analysis/runtime_validation_checklist_step4.csv`, and `tools/trace_text_renderer_step4.py`.


## Step 5 completed — Vietnamese glyph artwork prototype

Generated a visual 8x8 prototype for all 67 supplemental uppercase Vietnamese glyphs, plus packed tile bytes, a glyph/code CSV, a raw-byte collision audit, and a reproducible validator. The prototype derives its letter bodies from the ROM's A-Z tiles and compresses them to rows 2–6, reserving pixels for marks. Inspect `analysis/font_prototype_step5.png` carefully; these are candidate pixel designs, not final approved artwork.

**Important correction:** the raw boss dialogue dump uses `0x35` as a recurring five-byte segment/layout header marker. Step 4 had tentatively assigned `É` to `0x35`; Step 5 moves `É` to the spare blank source tile/code `0x8F` (`global CHR tile 0x1E8F`, file offset `0x03E900`). The updated full allocation is `analysis/font_glyph_allocation_step5.csv`. The source tile for every proposed glyph code was checked and is blank in the input CHR data. The collision audit separates header matches from body-stream matches under the current dump parsing.

The ROM remains unchanged. No ROM patch or playable translated ROM is included: actual PPU/CHR state, rendering of extended bytes, non-text references to blank tiles, and glyph legibility still need Mesen/FCEUX validation. Run `python3 tools/build_font_prototype_step5.py` to reproduce the assets and `python3 tools/validate_font_prototype_step5.py` for static validation.


## Step 6 completed — experimental font-render smoke test

Created a small IPS diagnostic patch, not a full ROM. It injects the 67 supplemental Vietnamese uppercase glyph tiles into candidate CHR locations and changes exactly one text byte in `OPEN_02` from `A` (`0x10`) to `À` (`0x30`) so the opening narration can test whether a supplemental glyph renders. The edit is same-length and does not change any pointer. The IPS patch is `analysis/Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.ips`; see `analysis/font_test_smoke_test_step6.md` for application instructions and emulator checks.

Build-time checks passed: source tile slots were blank, the iNES header is unchanged, PRG data is unchanged except the single test byte, other changes are restricted to the 67 allocated CHR tiles, and an IPS round-trip reproduces the constructed test image exactly. No full ROM is included in the archive. `tools/apply_font_test_ips_step6.py` can apply the IPS to the user's own exact matching clean ROM after checking the base SHA-256 and output SHA-256. Mesen/FCEUX testing has not yet been performed; this is an experimental smoke test, not a translation release.


## Step 7 completed — screenshot-informed tone-mark revision

The user-supplied screenshot from the Step 6 test shows the opening-line `A` was replaced by the candidate `À` glyph at the expected position. The grave mark is visible but reads as a short horizontal dash at native display size, so the font artwork was revised to use diagonal tone strokes where the 8×8 cell allows. A new diagnostic IPS `analysis/Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips` installs the revised 67 glyphs and replaces the 13 bytes of `A COUPLE DAYS` with the sample `ÀÁÂÃÈÊÌÍÒÓÔÕÙ`; `LATER...` remains unchanged. The text edit is same-length.

Build checks pass: 67 targets were blank in the clean source, the IPS round-trip is exact, the iNES header is unchanged, PRG modifications are limited to the 13-byte diagnostic text, and CHR modifications are limited to candidate glyph tiles. Step 7 itself has not yet been tested in Mesen/FCEUX. It is an accent-strip diagnostic, not a translated ROM. See `analysis/step7_screenshot_review_and_test_plan.md`, `analysis/font_prototype_step7.png`, `analysis/step7_build_validation.txt`, and `tools/apply_font_test_ips_step7.py`.
