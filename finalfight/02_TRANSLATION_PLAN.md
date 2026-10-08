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
