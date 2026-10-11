# Mighty Final Fight (USA) — Vietnamese full-tone translation plan

## 1. ROM identity and baseline

Input: `Mighty Final Fight (USA).nes`

The supplied image is a 128 KiB PRG + 128 KiB CHR iNES ROM using mapper 4 / MMC3.
Its PRG CRC32 is `2EE3EF15`, CHR CRC32 is `BCFEB409`, and PRG+CHR body CRC32 is
`3F78037C`. The body MD5 is `be4670792b17c74eecf3a0e7f37ecfe2`.

This is a good baseline for patching because the PRG and CHR checksums line up with the known
USA dump identity.

## 2. Map the ROM before editing

- Treat the ROM as MMC3-banked rather than as a flat address space.
- Record CPU-bank -> file-offset relationships for every text and font access.
- Keep file offsets, CPU addresses, and CHR bank IDs in separate columns.
- Never patch a pointer using a raw file offset.

## 3. Locate every text class

The first pass already found confirmed text blocks using the custom alphabet:

- Opening/ending narrative: file offsets around `0x1B4A`.
- Boss/encounter dialogue: file offsets around `0x9E71` and the following block.
- Credits: file offsets around `0x127F0`.

Next locate, with the same encoding:
- title/menu labels,
- character selection descriptions,
- stage/round text,
- continue/game-over text,
- item/HUD labels,
- all remaining dialogue records,
- staff/credits and presentation screens.

## 4. Formalize the text encoding

Verified:
- `0x00` = space
- `0x10..0x29` = A..Z
- `0x2A` = ?
- `0x2B` = .
- `0x2C` = ,
- `0x2D` = apostrophe
- `0x2E` = !
- `0x2F` = hyphen
- `0xFE` = line break/control
- `0xFF` = end of text/control

Observed `0x70..0x79` values are presentation/control bytes and must be preserved until their runtime
meaning is verified. Bytes such as `0x35` also occur around dialogue records and appear to be
record/layout metadata rather than ordinary text.

## 5. Build a complete dump

Use `tools/extract_mff_text.py` to produce a controlled dump with:
- file offset,
- raw bytes,
- decoded English,
- control markers,
- record boundaries.

Then verify the dump against gameplay screen-by-screen.

## 6. Translate into Vietnamese

Translation rules:
- Use natural Vietnamese rather than literal word-for-word substitution.
- Keep names such as CODY, GUY, HAGGAR, JESSICA, MAD GEAR and METRO CITY consistent.
- Prefer concise wording when the original dialog box is tight.
- Retain the game's energetic arcade tone.
- Use full Vietnamese diacritics.
- Keep English technical/proper-name text only where it is deliberate or visually important.

The confirmed opening/ending and boss dialogue blocks have a first Vietnamese draft in
`analysis/vietnamese_draft_confirmed_blocks.md`.

## 7. Solve the font problem first

Because the original text renderer is one-byte-per-glyph, do not rely on UTF-8 in the ROM.
Create 8x8 Vietnamese uppercase glyphs and assign them to free font tile IDs.

Preferred order:
1. Reuse unused tiles in the already-active font bank.
2. If insufficient, add/expand a font bank in CHR and patch the text-time CHR bank selection.
3. Only change the renderer to support combining marks if neither of the above is practical.

## 8. Solve text length and relocation

Vietnamese strings will often be longer than the English source.

For every string record:
- calculate encoded byte length including controls,
- compare it with original capacity,
- flag overflows,
- relocate longer strings to an expanded PRG area instead of overwriting neighboring code/data,
- patch the relevant pointer table to the new location.

MMC3 is suitable for a larger emulator ROM, but expansion must be handled consistently in the header,
bank mapping, and pointer logic. Do not assume an expanded ROM will remain compatible with every
original-hardware board.

## 9. Verify pointer tables and the writer routine

Before the final builder is allowed to write:
- identify the text pointer table(s),
- identify the routine that reads the custom character codes,
- identify line-wrap behavior,
- identify how `0xFE`, `0xFF`, and `0x70..0x79` are interpreted,
- identify the active font CHR bank during dialog,
- confirm which address bytes are little-endian.

This is the one remaining reverse-engineering stage before a fully automated relocation builder can be trusted.

## 10. Build and test

Run the translation through these test cases:
- boot/title,
- character selection,
- opening story,
- every boss/encounter dialog,
- stage transition,
- continue/game-over,
- ending,
- credits.

For each screen:
- no missing glyphs,
- no pink/blank tiles,
- no clipped diacritics,
- no bad line wrapping,
- no overwritten graphics,
- no crash/hang after leaving the text screen.

## 11. Release artifacts

Final project should contain:
- clean ROM hash record,
- `.tbl`,
- complete English dump,
- complete Vietnamese script,
- font tile sheet and source,
- pointer/layout map,
- deterministic build script,
- IPS/BPS patch against the verified clean ROM,
- final translated ROM,
- test checklist and emulator test notes.

At this stage, the ROM analysis and encoding discovery are complete; pointer/font runtime verification is
the remaining prerequisite for a safe final patch.


# Step 2 execution result

Pointer/runtime static analysis has now been completed beyond the original plan:
- opening table verified: `$9B2C/$9B33`, 7 entries
- boss table verified: `$A4FD/$A54C`, 78 entries
- credits table verified: `$A7D6/$A7DB`, 5 entries
- opening text renderer verified at PRG `0x01A00`
- boss pointer loader verified near PRG `0x0991F`
- credits renderer verified near PRG `0x12708`
- render command area identified at `$0780-$0784`
- character dispatch call identified as `JSR $F406`

The next step is to isolate the actual CHR tile lookup used by `$F406` and then build a Vietnamese
font bank/expansion plan around the real renderer.


## Step 4: Static text-to-PPU mapping

1. Verify the fixed-bank `$C1FD-$C221` VRAM queue consumer.
2. Confirm that the data byte stored at `$0783,X` is written directly to `$2007`.
3. Trace NMI CHR setup (`$C1BC-$C1CF`) and PPUCTRL shadow initialization (`$FEB6`).
4. Create a candidate mapping for the 67 supplemental Vietnamese uppercase glyphs using currently blank source tiles, but do not overwrite until runtime screen references and dialogue-header semantics are checked.
5. Record emulator validation tasks explicitly; no ROM bytes are modified by this step.


## Step 5: Font artwork prototype and byte-collision audit

1. Generate 67 supplemental uppercase glyphs as 8x8 2bpp tile records using the original A-Z tile shapes as a starting point.
2. Inspect `analysis/font_prototype_step5.png` for pixel legibility; the prototype is compact and has not been emulator-tested.
3. Use `analysis/byte_code_collision_audit_step5.csv` to distinguish byte matches inside boss layout headers from bytes in body streams.
4. Reserve `0x35` because it appears as a boss segment/layout header marker; move the glyph `É` to spare byte/tile `0x8F`.
5. Keep the ROM unchanged until Mesen/FCEUX confirms how each renderer handles the extended bytes and verifies that the candidate blank tile IDs are not used by other screens.

Outputs: `analysis/font_prototype_tiles_step5.bin`, `analysis/font_prototype_tiles_step5.csv`, `analysis/font_glyph_allocation_step5.csv`, `analysis/font_prototype_step5.png`, `analysis/font_prototype_validation_step5.json`, `analysis/font_byte_reservations_step5.md`, and `tools/build_font_prototype_step5.py`. No playable ROM or patch is generated by Step 5.


## Step 6: Minimal font-render smoke test

1. Build a reversible IPS patch that writes the 67 supplemental glyphs into the candidate blank CHR slots.
2. Change only the first `A` in `OPEN_02` (`A COUPLE DAYS LATER...`, file offset `0x01C9C`) from byte `0x10` to `0x30` (`À`) as a same-length probe; do not move text or touch pointers.
3. Verify clean-ROM SHA-256, original blank tile slots, exact patch round-trip, and that no non-target ROM bytes change.
4. Provide an application script that refuses mismatched source ROMs and writes only a local user-side diagnostic copy.
5. Test the result in Mesen/FCEUX: verify the grave mark, spacing, unrelated graphics, and progression. The static build passes, but emulator validation remains open.

Outputs: `analysis/Mighty_Final_Fight_Vietnamese_FONT_TEST_ONLY_step6.ips`, `analysis/font_test_rom_report_step6.json`, `analysis/step6_font_test_build_validation.txt`, `analysis/font_test_smoke_test_step6.md`, `tools/build_font_test_rom_step6.py`, and `tools/apply_font_test_ips_step6.py`. This does not translate the game text and is not a release patch.


## Step 7 — screenshot-informed glyph refinement

The Step 6 screenshot is evidence that the `0x30` test byte selected the candidate À tile in the opening narration. Its tone mark looks horizontal at display scale. Step 7 redraws all 67 candidate uppercase glyphs with more diagonal tone marks where possible and builds a new same-length diagnostic string by replacing `A COUPLE DAYS` (13 bytes) with `ÀÁÂÃÈÊÌÍÒÓÔÕÙ`. The `LATER...` continuation remains intact.

The diagnostic patch is `analysis/Mighty_Final_Fight_Vietnamese_FONT_TEST_STEP7.ips`. Apply with `python3 tools/apply_font_test_ips_step7.py --rom "/path/to/Mighty Final Fight (USA).nes" --output "/path/to/Mighty_Final_Fight_FONT_TEST_STEP7.nes"`. Only test on a separate copy. Expected first line is the glyph sequence above; the current emulator status for this Step 7 patch is **not yet tested**. The build is statically verified but not a playable translation release.
