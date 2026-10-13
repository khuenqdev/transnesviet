# NES ROM Translation Skill

This folder is a reusable AI-agent skill for NES/Famicom text translation and ROM patching.

## Contents

- `SKILL.md` - routing rules, safety invariants, required outputs and workflow summary.
- `references/workflow.md` - detailed intake through release workflow.
- `references/mighty-final-fight-case-study.md` - observed facts and lessons from Step 20.
- `references/vietnamese-font-design.md` - composite glyphs, split diacritics, bank-mapping diagnosis.
- `references/validation-checklist.md` - release acceptance criteria.
- `templates/` - blank manifest, catalog, emulator log, checklist, prompt templates.
- `tools/nes_rom_preflight.py` - read-only ROM header and hash preflight.
- `tools/ips_roundtrip_validator.py` - independent IPS application/round-trip checker.
- `tools/catalog_validator.py` - translation catalog completeness/capacity checker.

## Installation/use

Copy `nes-rom-translation/` into the AI agent's configured skills directory or project knowledge area. Keep the folder name and internal relative paths. Tell the model to load `SKILL.md` before starting a ROM-translation task. On systems without skill auto-loading, attach or paste the contents of `SKILL.md` and relevant reference documents explicitly.

The included generic scripts are helpers, not a universal text extractor or injector. Every new ROM still requires its own mapper, text pointers, control codes, renderer, font layout, and tests to be discovered.

## Fast smoke tests

```bash
python3 tools/nes_rom_preflight.py "/path/to/clean.nes" --json rom_manifest_report.json
python3 tools/catalog_validator.py translation_catalog.tsv --json catalog_report.json
python3 tools/ips_roundtrip_validator.py clean.nes translation.ips expected_output.nes
```

Run commands from this skill directory, or adjust paths after installation. Keep the clean ROM outside distributable archives.
