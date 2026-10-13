# Mighty Final Fight (USA) — Vietnamese indexed-text release (Step 20)

This folder is the reproducible project for the **full indexed dialogue and credits translation build**. It includes the cumulative ROM and IPS under `release/`, translation catalogs, original text extracts, pointer tables, glyph mapping, build code, and validation reports.

## Download/release files

- `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes` — cumulative diagnostic/final indexed-text ROM (278,544 bytes).
- `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips` — cumulative patch to apply to the clean `Mighty Final Fight (USA).nes` (do not apply to a previously patched ROM).
- `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes.sha256.txt` — checksums.

## Coverage

The verified pointer/text inventory contains 90 index-level rows: 7 opening records, 78 boss-dialogue indexes, and 5 credits records. Because four boss indexes are shared-pointer aliases, these map to 86 physical text slots. All indexed slots in that inventory now have Vietnamese text, including localized grunt text at BOSS_09 and BOSS_10 while preserving their animation commands.

This does **not** claim every visible pixel/text element in the game is translated. Menu/HUD labels and other graphical text not present in the verified pointer inventory have not been separately extracted and verified in this package. The full game has also not yet been played through in FCEUX after this build.

## Rebuild from your clean ROM

Requirements: Python 3, Pillow, and the clean original ROM matching the SHA-256 below.

```bash
python3 tools/build_full_translation_step20.py \
  --source-rom "/path/to/Mighty Final Fight (USA).nes" \
  --project "/path/to/Mighty_Final_Fight_Vietnamese_Project_step20" \
  --base-ips "/path/to/Mighty_Final_Fight_Vietnamese_Project_step20/analysis/step19_boss_dialogue_pilot_combined.ips" \
  --output-rom "/path/to/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes" \
  --output-ips "/path/to/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips"
```

The builder checks the clean ROM SHA-256, reconstructs and validates the Step 19 known-good base from the included cumulative IPS, enforces slot limits, preserves pointers/control bytes, and checks the output IPS by applying it back to the clean source. Do not include or distribute the clean source ROM in this project.

## Test status

- Automated static slot/encoding checks: passed.
- IPS round-trip from clean source: passed.
- ROM header/size and protected pointer/control checks: passed.
- User-confirmed rendering: opening sequence through Step 18, initial boss dialogue through Step 19, bank fix through Step 17.
- Step 20 full playthrough including all later boss dialogue and credits: pending user test.

See `analysis/step20_scope_report.md`, `analysis/step20_validation.txt`, and `analysis/step20_full_translation_catalog.tsv` for details.

## Final hashes (Step 20)

- ROM SHA-256: `03d2d05e2303e2b41a5213b248bdd3d20cfa478a8e473dd00734d42882e6bcbc`
- IPS SHA-256: `2778df5a7eabad3ca66d32b2a9fc6e41f1b0b7a825daa8c174e43dbdc6b135b5`

The independent validation script is `tools/validate_final_build_step20.py`. It verifies the exact IPS round-trip against the clean ROM, artifact hashes, all 90 catalog rows, and the preserved animation tails.


## Documentation snapshot note

The documentation bundle intentionally omits the `.nes` release binary and the clean source ROM. The IPS patch, project scripts, catalog, fonts, and baseline patches are retained as reference/build inputs. To rebuild, supply the clean ROM whose SHA-256 matches the manifest and use the explicit `--source-rom`, `--project`, `--base-ips`, `--output-rom`, and `--output-ips` arguments.
