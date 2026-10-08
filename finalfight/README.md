# Mighty Final Fight — Vietnamese Translation Project

This pack is the reverse-engineering and translation groundwork for the supplied USA ROM.

## What is complete

- ROM identity/hash verification
- MMC3/mapper-4 structure identification
- verified custom text alphabet
- confirmed opening/ending text location
- confirmed boss/encounter text location
- confirmed credits location
- `.tbl` mapping
- extraction script
- Vietnamese draft for the confirmed dialogue blocks
- full-tone font requirements and implementation strategy
- safe build scaffold that refuses to patch until pointer/font layout is verified

## What is deliberately not claimed complete

A final translated ROM is not included yet. The remaining work is runtime verification of
pointer tables, dialog writer behavior, CHR font-bank selection, and relocation mechanics.
That verification is necessary to prevent a seemingly successful build from corrupting the game.

## Files

- `02_TRANSLATION_PLAN.md` — step-by-step plan
- `mighty_final_fight.tbl` — verified custom alphabet/control mapping
- `analysis/rom_analysis.json` — machine-readable ROM facts
- `analysis/confirmed_text_extract.txt` — confirmed extracted blocks
- `analysis/vietnamese_draft_confirmed_blocks.md` — first Vietnamese draft
- `analysis/font_strategy.md` — full-tone font plan
- `tools/analyze_mff.py` — ROM validator
- `tools/extract_mff_text.py` — text extractor
- `tools/build_vn_scaffold.py` — guarded build scaffold

## Baseline checksum

PRG+CHR body CRC32: `3F78037C`


## Step 2 completed

The pointer tables and message-reader paths have now been verified statically.

Verified:
- 7 opening/cutscene message pointers
- 78 boss/encounter dialogue pointers
- 5 credits pointers
- opening renderer and its RAM pointer construction
- boss pointer loader and its two pointer arrays
- credits pointer arrays
- ordinary text character codes and key controls
- render-command area `$0780-$0784`
- character pipeline call `JSR $F406`

The exact font-tile lookup inside the `$F406` path remains the next task.
