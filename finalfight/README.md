# Mighty Final Fight Vietnamese Translation - Documentation and AI Skill

This documentation bundle accompanies the Step 20 project and records the complete workflow demonstrated during the project. It also includes a reusable AI skill for other NES/Famicom translation tasks.

## Main documents

- `docs/STEP_BY_STEP_ROM_TRANSLATION_GUIDE.md` - full case-study walkthrough from source intake through patch release.
- `docs/STEP_BY_STEP_ROM_TRANSLATION_GUIDE.docx` - editable Word edition.
- `docs/STEP_BY_STEP_ROM_TRANSLATION_GUIDE.pdf` - PDF edition for reading/printing.
- `skill/nes-rom-translation/SKILL.md` - the main AI-agent skill entry point.
- `skill/nes-rom-translation/references/` - detailed workflow, case study, typography notes, validation checklist.
- `skill/nes-rom-translation/templates/` - manifest, catalog, emulator log, checklists and reusable prompts.
- `skill/nes-rom-translation/tools/` - generic, read-only/preflight validation helpers.
- `project_reference/Mighty_Final_Fight_Vietnamese_Project_step20/` - a Step 20 reference snapshot with build inputs, prior cumulative IPS baselines, catalog and scripts; the `.nes` binary is intentionally omitted.
- Loose copies at `project_reference/` provide quick access to the core catalog, pointer map, `.tbl`, scope report, checksums and scripts.

## What Step 20 means

Step 20 contains all currently verified indexed text entries (90 logical rows: 7 opening, 78 boss indexes, 5 credits; 86 physical slots because four boss indexes share pointers). The build passed static validation and exact IPS round-trip validation. The project record states that a full playthrough of every boss scene and credits in FCEUX was still pending, and menu/HUD graphical text outside the pointer inventory is not claimed translated. The documentation preserves that distinction.

## Quick start

1. Read the PDF or DOCX guide.
2. For future projects, install/copy `skill/nes-rom-translation/` into the agent's skill directory.
3. Start with the read-only tool `tools/nes_rom_preflight.py` and fill in `templates/rom_manifest.json`.
4. Follow the skill workflow to discover the mapper, text pointers, control codes, renderer, active CHR banks, font map, and tests.
5. Do not reuse Mighty Final Fight offsets or byte tables for a different ROM.

## External reference

STONE BOAT, “Contra và Kontora,” is referenced for the conceptual technique of storing base letters and diacritic marks separately and routing through a helper routine placed in verified free ROM space. The article is for a different game/mapper, so its addresses and mapper register values are not transferable as-is:
https://sites.google.com/view/sfc65816/famicom-nes/contra-v%C3%A0-kontora?authuser=0

## Licensing/source note

The documentation and helper scripts are newly authored for this workflow. The package does not include the clean source ROM or a patched `.nes` binary. The Step 20 IPS and prior baseline IPS files are included as reference artifacts. The user must provide the exact clean ROM for rebuilding and comply with applicable rights for any ROM they modify or distribute.
