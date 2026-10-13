# Reusable prompts for AI-assisted ROM translation

## Intake
"Inspect the attached clean NES ROM without modifying it. Produce a source manifest with SHA-256, iNES/NES 2.0 header interpretation, mapper/submapper, PRG/CHR sizes, trainer/mirroring, total size, and any header-length mismatch. Stop on uncertainty and label assumptions."

## Text extraction
"Using the clean ROM and current table/project files, locate and verify the text records for [specific scene]. Trace the code path from index to pointer to payload. Return a catalog with logical ID, shared-pointer identity, CPU address, bank context, PRG offset, absolute file offset, slot capacity, terminator, and control-code notes. Do not edit the ROM."

## Font/renderer audit
"Investigate the reported glyph failure [describe]. Determine whether it is artwork, text-code collision, wrong tile ID, wrong active CHR bank, renderer-specific mapping, or CPU-state corruption. Gather the smallest concrete evidence set: input byte, resulting tile ID, PPU address, active mapper registers, physical CHR offset, and scene. Do not redraw artwork until mapping is verified."

## Translation
"Translate the following catalog records to Vietnamese with full diacritics. Preserve character voice, proper nouns, game terminology, line/page limits, and each control/terminator byte. Provide draft text, encoded byte sequence, byte count, and any glyph/encoding gaps. Do not invent mappings for unknown bytes."

## Patch/release
"Build a cumulative patch from the exact clean source hash. Preserve pointers and reserved/control bytes unless explicitly authorized. Run an independent IPS/BPS round-trip, source/output hash checks, slot-capacity and terminator checks, binary-diff review, and an emulator test plan. Return the ROM/patch plus reproducible build script, catalog, scope report and validation logs. State all untested paths."
