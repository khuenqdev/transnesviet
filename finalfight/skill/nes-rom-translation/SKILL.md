---
name: nes-rom-translation
version: 1.0.0
description: Reverse-engineer, extract, translate, render, patch, validate, and document text in NES/Famicom ROMs. Use when asked to localize a NES ROM, build a translation patch, analyze pointers/CHR fonts/mapper banks, debug text glitches, or produce a reproducible ROM-translation project.
---

# NES/Famicom ROM Translation Skill

## Mission

Produce a reproducible, technically defensible ROM-translation project. Optimize for correctness and reversibility, not speed. A patch is not finished when encoded text looks plausible in a dump: it must preserve code/data boundaries, render in the actual game, and be accompanied by source identity, catalogs, scripts, tests, checksums, and an honest scope statement.

## When to activate

Use this skill when the user wants to:
- translate or localize NES/Famicom text;
- dump text, create or fix a `.tbl`, discover pointers, or reconstruct control codes;
- build custom fonts including non-Latin characters and diacritics;
- debug garbled text, wrong CHR tiles, crashes after injection, or screen-transition bugs;
- generate IPS/BPS patches, a reproducible build script, documentation, or a reusable ROM-translation workflow.

## Required outputs

For a completed scoped task, produce as many of the following as relevant:
1. Clean-source ROM manifest and hash.
2. ROM/header/mapper/PRG/CHR preflight report.
3. Text extraction, pointer catalog, `.tbl`, control-code notes, and source dumps.
4. Translation catalog with one row per logical index and physical-slot/alias information.
5. Font atlas, glyph-to-byte map, bank mapping, and native-size previews.
6. Reproducible injector/build script and IPS/BPS patch.
7. Independent validation script plus machine-readable and human-readable reports.
8. Emulator test checklist and record of user-confirmed versus not-tested scenarios.
9. Step-by-step documentation and release ZIP.

Do not produce every file mechanically when it is not needed; explain omissions. Never distribute the clean user-supplied commercial ROM in a public archive. It is usually sufficient to distribute the translation patch, builder, documentation, catalogs, and checksums.

## Hard rules

- **Never guess a ROM layout.** Inspect the actual header and hash. Mapper, pointer widths, PRG mapping, CHR mapping, and control bytes are game-specific.
- **Preserve the clean source.** Work from a copy and verify its SHA-256 before each release build.
- **Keep CPU address, bank-relative offset, PRG-relative offset, and file offset separate.** Include the 16-byte iNES header in file offsets only when converting explicitly.
- **Do not treat `00`/`FF` fill as proof of unused space.** Check references and runtime bank state.
- **Do not treat a byte as text merely because it resembles a glyph index.** Establish whether it is a character, metadata, pointer byte, control code, animation command, or terminator.
- **Never overwrite control bytes accidentally.** Preserve terminators, timing, line breaks, animation markers, metadata prefixes, and special commands unless a specific, validated transformation requires editing them.
- **Never move a pointer target or grow a fixed slot silently.** Either fit the translation into the original slot or document and test a relocation/expansion plan that updates every consumer.
- **Map high-byte glyphs only after tracing active CHR banks in the relevant runtime context.** A tile can exist in CHR ROM and still display as unrelated graphics if a different bank is active.
- **Preserve machine state in injected code.** Track the accumulator, index registers, processor flags, stack, PPU latch/address, RAM temporaries, bank mapping, and interrupt behavior expected by the caller.
- **Use feature detection for emulator scripting APIs.** A Lua callback missing in a user's FCEUX build must not make the entire script fail. Record missing observations as unavailable, never fabricate them.
- **Require exact IPS/BPS round-trip validation.** Applying the patch to the expected clean ROM must reproduce the expected output bytes exactly.
- **Distinguish evidence levels.** Use `STATIC_PASS`, `PREVIEW_ONLY`, `USER_EMULATOR_PASS`, `FULL_PLAYTHROUGH_PASS`, or `NOT_TESTED`. Never say emulator-verified just because a validator or preview passes.
- **Report coverage boundaries.** If menu/HUD/image text or unindexed scenes were not found and tested, say they are not covered rather than calling the whole game 100% translated.

## Workflow

Follow `references/workflow.md` in order. At a high level:

1. Intake and protect source files.
2. Identify header, mapper, PRG/CHR dimensions, source hash, and any trainer.
3. Extract candidate text and inspect it in-game before trusting the decoder.
4. Find every renderer separately: opening, in-game dialogue, credits, menus, HUD, cutscenes.
5. Build a control-code-aware pointer catalog with aliases and exact capacities.
6. Inspect CHR graphics, map base characters, and locate the actual text-to-PPU path.
7. Trace runtime PRG/CHR bank mappings with a debugger/emulator.
8. Choose font architecture: composite glyphs or split diacritics. Test the architecture with tiny probes.
9. Translate within byte/screen limits; encode using a strict table; reject unknown/reserved bytes.
10. Build to a separate output from the clean source; generate a cumulative patch.
11. Run independent static, binary-diff, and patch round-trip checks.
12. Test in an emulator: opening, text pages, dialogue, credits, transitions, and gameplay regressions.
13. Package outputs, hashes, scope notes, build scripts, and evidence.

## Vietnamese and other diacritic-heavy scripts

Use the typography notes in `references/vietnamese-font-design.md`. The general strategy demonstrated in the Contra/Kontora article is to separate a base glyph from upper/lower diacritic marks and map logical accented characters to a base glyph plus mark placement. This can save tile slots and improve typography, but it requires a renderer change and a safe row/PPU placement model. It is not a drop-in technique: the reference article targets a different ROM and mapper.

For a quick pilot, a bank-safe composite glyph set may be lower risk. For a scalable font, split marks may be superior. Decide based on the game's tile layout, line spacing, character width, active CHR bank, and available code/data space—not ideology.

## Required test gates

See `references/validation-checklist.md`. Minimum gates before release:

- exact source SHA-256 accepted;
- all encoded characters mapped;
- no reserved/control byte emitted as plain text unless intended;
- every fixed slot fits and its terminator remains at the expected location;
- original pointer tables unchanged unless relocation is explicitly planned;
- CHR bank mapping proven for every path using custom glyphs;
- IPS/BPS round trip exact;
- ROM header and size are expected;
- emulator result recorded with the tested output hash;
- release states untested areas plainly.

## Project-specific case study

The companion reference in `references/mighty-final-fight-case-study.md` records the verified Step 20 facts for Mighty Final Fight (USA). The included `templates/` are blank reusable templates, not authoritative values for new ROMs. The supplied helper scripts are generic preflight/check tools; they do not reverse-engineer all ROM-specific pointers automatically.

## User handoff

When reporting progress, make each message useful and bounded. State:
- what changed;
- what was checked automatically;
- what was tested in the emulator and by whom;
- what remains unverified;
- exact files and how to apply/rebuild them.

If the user reports a glitch, stop expanding the translation. Reproduce the exact byte, glyph ID, physical offset, PPU address, active CHR bank, and code path first. Correct the smallest isolated cause; then rerun regression checks. Do not just redraw an icon when the underlying problem may be a bank mapping or encoding collision.
