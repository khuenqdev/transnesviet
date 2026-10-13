# Installing and Using the AI ROM Translation Skill

## What the skill is

`skill/nes-rom-translation/SKILL.md` is a compact instruction entry point for an AI model or coding agent. The references provide details on workflow, mapper/text discovery, Vietnamese font design, validation, and the Step 20 case study. Templates standardize manifests, catalogs, and testing; small scripts make file checks repeatable.

## Installation

1. Unzip the documentation bundle.
2. Copy the entire `skill/nes-rom-translation/` directory into the skill directory supported by the AI model/agent, retaining its name and subdirectories.
3. If the host loads skills automatically, ask the model to use `nes-rom-translation` for the task. Otherwise, provide `SKILL.md` and the relevant references as context.
4. Run the helper scripts on the user's own clean ROM, not a patched intermediate.
5. Preserve the output manifest and validation records with every patch.

## First prompt for a new project

> Use the `nes-rom-translation` skill. Inspect the attached clean ROM and project files without modifying the ROM. Create a source manifest, identify the mapper and PRG/CHR layout, and report the first three steps needed to discover one verified text record. Do not infer pointers or code caves without evidence. Label everything as verified, inferred, or unknown.

## Debugging prompt

> Use the `nes-rom-translation` skill to diagnose the reported rendered-text problem. Do not redraw the glyph yet. Trace the source text byte, logical record and pointer, CPU address/bank, encoded byte, resulting PPU tile ID, active CHR bank, and code path. Propose the smallest reversible test and state what the test will and will not prove.

## Release prompt

> Build a reproducible patch from the exact clean source hash. Include the ROM only as requested and appropriate; otherwise provide the patch and toolchain. Verify an exact IPS/BPS round trip, protected pointer/control bytes, output hash, translation catalog completeness, and the actual emulator test status. Package the script, catalog, mapping, scope report, test log, and checksums. Do not call it a full-game verified release unless all required contexts were tested.
