# Step 19 output index

## Top-level outputs (delivered separately)
- `Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.nes` — diagnostic ROM based on the clean USA ROM plus all Step 18 changes and the Step 19 boss-text pilot.
- `Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.ips` — cumulative patch for the clean USA ROM; do not apply it on top of an already-patched ROM.
- `Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.sha256.txt` — SHA-256 hashes.

## Project internals
- `analysis/step18_base_combined.ips` — bundled base patch for reproducible rebuilds.
- `analysis/font_prototype_tiles_step17.csv` — code map used by the builder.
- `analysis/source_dialogue_records.tsv` — source record and pointer reference.
- `analysis/step19_translated_boss_records.tsv` / `.json` — translated payloads and capacities.
- `analysis/step19_boss_dialogue_pilot.md` — readable translations and scope.
- `analysis/step19_boss_dialogue_preview_contact_sheet.png` — generated glyph preview, not an emulator capture.
- `analysis/step19_build_validation.txt` / `.json` — validation outcome.
- `tools/build_boss_dialogue_pilot_step19.py` — rebuilds the pilot ROM and cumulative IPS.
- `tools/trace_boss_dialogue_chr_step19.lua` — optional FCEUX trace for confirming CHR R0/R1 mappings while dialogue glyphs are rendered; it avoids `memory.registerread` for older FCEUX builds.
- `analysis/step19_test_instructions.md` — emulator checklist.

The original game ROM is not included in this project archive. Emulator test status is pending user verification.
