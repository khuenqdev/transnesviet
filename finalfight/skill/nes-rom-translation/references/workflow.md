# Detailed Agent Workflow

## Stage 0 - Intake

1. Ask for or locate the clean ROM and any existing scripts, patches, table files, screenshots, CDL/debugger logs, or prior translation project.
2. Record which files are authoritative; do not replace a supplied source with a web download.
3. Hash the source and store the filename, size, hash, and acquisition notes.
4. Copy it read-only to an immutable `source/` or reference location. Put outputs in a different directory.
5. Determine any legal/redistribution constraints. Avoid bundling the clean ROM in the release ZIP.

## Stage 1 - Format preflight

1. Inspect the 16-byte header and file length.
2. Determine iNES 1.0 versus NES 2.0; handle trainer bit and mapper/submapper correctly.
3. Calculate PRG/CHR sizes from the header and compare with actual byte length.
4. Report trailing/truncated data rather than silently trimming it.
5. Save `rom_manifest.json` and hash report.

Use `tools/nes_rom_preflight.py` to create a first-pass report. Confirm any unusual format manually.

## Stage 2 - Text discovery

1. Search for likely strings using a provisional byte table; never inject at this stage.
2. Use emulator screenshots and breakpoints to identify at least one known on-screen string.
3. Inspect both the bytes before and after it. Determine terminator, control bytes, and how record length is represented.
4. Decode multiple examples, including punctuation, short strings, and strings with non-text payload.
5. Record uncertainty; do not convert every unexplained value to a character.

## Stage 3 - Pointer/record model

1. Find code that loads the relevant record index and reads pointer bytes.
2. Determine pointer width, endianness, CPU base/window, bank selection, and whether pointers are relative or absolute.
3. Convert each pointer to a physical file offset with a documented formula.
4. Record the start of payload separately from metadata prefixes.
5. Mark aliases: different indexes pointing to the same physical record.
6. Identify exact maximum payload length, terminator, and any per-record metadata.
7. Compare at least 3 records against emulator output before calling the map verified.

## Stage 4 - Control codes and encoding table

1. Build a `.tbl` for verified printable bytes only.
2. Put controls and reserved bytes in comments/explicit metadata rather than pretending they are letters.
3. Create a separate control-code grammar for each renderer where needed.
4. Build an encoder that fails closed on unmapped characters and reserved bytes.
5. Unit test encoding/decoding round trips on clean text strings and control-bearing samples.

## Stage 5 - Font/CHR investigation

1. Decode CHR data into 8x8 2bpp tiles (16 bytes per tile), unless this game's PPU format proves otherwise.
2. Produce labeled tile sheets organized by physical CHR bank.
3. Identify existing glyphs and blank-looking candidates.
4. Inspect the font at native scale; distinguish an art-quality defect from a mapping/bank defect.
5. Trace the path from a text byte to the PPU tile, including mapping registers active during use.
6. Never overwrite a blank-looking tile without testing whether it is referenced by other screens or bank configurations.

## Stage 6 - Architecture choice

### Composite glyphs

Use a dedicated tile for each accented character. Pros: small renderer change. Cons: more tiles and 8x8 space may make marks cramped.

### Split marks

Map an input code to a base letter plus one or two mark tiles positioned above and/or below. Pros: shared marks and less glyph duplication. Cons: requires renderer and layout changes, adjacent-row writes, clearing logic, and collision checks.

If adding code, don't grow existing routines in place in a way that shifts other addresses. Consider a jump to a validated code cave or a safely expanded bank, but first check references and runtime mapping. Save/restore state according to the calling convention.

## Stage 7 - Runtime trace

1. Use FCEUX/Mesen breakpoints, trace logger, memory tools, code/data logger, or emulator Lua callbacks.
2. Capture mapper register writes and active bank mappings at each relevant hook.
3. Trace every text path, not only the opening.
4. Feature-detect optional APIs. If `memory.registerread` is unavailable, continue with explicitly reduced observability; do not infer the PPU address as though observed.
5. Log event caps and dropped events; a capped log cannot prove behavior beyond the cap.
6. Reproduce glyph defects with an exact character, byte code, PPU tile address, and bank register values.

## Stage 8 - Translation

1. Translate with game context and speaker voice.
2. Fit the text box/slot; preserve essential meaning and proper names.
3. Maintain a style glossary and consistent term choices.
4. Test encoded byte count, not Unicode character count.
5. Keep one row per logical game entry and explicit physical slot / aliases.
6. Never silently remove diacritics if full-tone script is a requirement; rephrase or alter font capacity instead.

## Stage 9 - Build

1. Rebuild all outputs from the clean source every time.
2. Apply any known-good base patch internally only after verifying its exact hash and output hash.
3. Edit only approved payload and graphics ranges.
4. Preserve pointer tables and all control/metadata bytes that are not explicitly targeted.
5. Expand PRG/CHR only after updating the proper header fields and confirming the mapper supports the layout.
6. Generate a cumulative IPS/BPS against the clean source.
7. Apply the patch with an independent parser and compare to the expected output exactly.

## Stage 10 - Validation

Run static checks and produce JSON plus readable logs. Minimum binary checks:

- source and output hashes;
- output header, PRG/CHR dimensions, total length;
- patch parsing and round trip;
- only expected file ranges changed;
- pointer tables unchanged (or diff approved);
- every slot within capacity;
- terminators/control bytes preserved;
- catalog rows complete;
- no unmapped glyphs or accidental high-byte output;
- any animation/sequence payload byte-for-byte preserved.

## Stage 11 - Emulator QA

Test the actual output hash—not a preview and not a different build. Work through:

1. cold boot/title/menu;
2. every page of each translated scene;
3. all supported Vietnamese glyph families;
4. opening-to-game transitions;
5. dialogue alias indexes;
6. credits and credits exit;
7. normal gameplay regressions including sprites, scrolling, animation, audio, pause/reset and scene transitions.

Record ROM hash, emulator name/version, tested scenes, outcomes, screenshots, and bugs. Fix issues one at a time, rebuild from clean source, and rerun regression.

## Stage 12 - Package and handoff

Include README, scope report, full catalog, table/control-code notes, pointer map, scripts, tests, outputs, checksums, source provenance, and status. Exclude original source ROM unless explicitly and legally appropriate. State what was not extracted or not tested. Make the release reproducible by someone who only has the clean source ROM plus the project package.
