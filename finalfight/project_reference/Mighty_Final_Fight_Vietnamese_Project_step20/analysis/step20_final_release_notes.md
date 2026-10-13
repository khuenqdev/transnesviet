# Step 20 — Final indexed-text release notes

## Delivered files

- Final ROM: `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes`
- Cumulative IPS for the clean USA ROM: `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips`
- Full level-by-level catalog: `analysis/step20_full_translation_catalog.tsv`
- Translation entries added in this step: `analysis/step20_remaining_boss_and_credits_translations.md`
- Original extracted source text: `analysis/english_text_dump.md` and `analysis/confirmed_text_extract.txt`
- Pointer inventory: `analysis/pointer_tables.csv`
- Character table: `mighty_final_fight.tbl`
- Build scripts: `tools/build_full_translation_step20.py` and `tools/validate_final_build_step20.py`

## Coverage summary

| Group | Index rows | Status |
|---|---:|---|
| Opening narration | 7 | Retained from the user-tested Step 17/18 build |
| Boss dialogue | 78 | All index rows have a Vietnamese entry; four indexes are shared-pointer aliases |
| Credits | 5 | Translated in Step 20 |
| **Total** | **90** | All known pointer-indexed rows cataloged |

There are 86 unique physical slots after accounting for four shared-pointer aliases. Step 20 writes 67 unique boss slots (65 normal dialogue slots and 2 grunt lines) and 5 credits slots on top of the previously tested opening and initial boss dialogue.

## Static checks

- Clean source SHA-256: `5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`
- Final ROM SHA-256: `03d2d05e2303e2b41a5213b248bdd3d20cfa478a8e473dd00734d42882e6bcbc`
- IPS SHA-256: `2778df5a7eabad3ca66d32b2a9fc6e41f1b0b7a825daa8c174e43dbdc6b135b5`
- IPS records: 137
- Output size: 278,544 bytes
- Exact IPS round-trip from clean source: PASS
- Translation catalog: 90 rows, none empty
- Boss metadata prefixes and all indexed pointers: preserved
- BOSS_09/10 visible vocalizations localized; `0x76` punctuation and `FB/FA/F9` animation tail: preserved
- BOSS_54 trailing `FC`: preserved

See `step20_validation.json`, `step20_validation.txt`, and `step20_independent_validation.json` for machine-readable and plain-text results.

## Known boundary

The work covers the currently verified pointer-indexed opening, boss-dialogue and credits inventory. Menu/HUD labels or text drawn directly as graphics that were not in that inventory are not claimed translated by this release. The full Step 20 build has not been independently played through in FCEUX; it needs a complete pass through later bosses and credits before it can be called emulator-verified.
