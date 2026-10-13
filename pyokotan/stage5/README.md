# Pyokotan localization toolkit — Stage 5

The stage 5 package expands the static CHR audit and provides an improved FCEUX trace workflow. The attached ROM was inspected statically; no emulator is installed in this workspace, so no live trace was captured.

## Start here

1. `outputs/pyokotan_rom_analysis_v5.txt`
2. `outputs/pyokotan_chr_inventory_summary_v5.json`
3. `outputs/pyokotan_font_candidate_catalog_v5.csv`
4. `outputs/runtime_trace_instructions_v2.md`

## Rebuild CHR inventory

```sh
python tools/chr_inventory.py pyokotan.nes --outdir outputs --refdir reference --all-bank-atlases
```

Pillow is required for image generation. JSON/CSV output includes physical offsets, tile hashes, pixel statistics, exact-duplicate groups, and bank context.

## Capture runtime evidence in FCEUX

1. Open the original ROM in FCEUX and run `tools/pyokotan_fceux_text_trace_v2.lua` from power-on.
2. Reach the title/menu and any Japanese text-bearing screens.
3. Stop the Lua script. It creates `pyokotan_runtime_trace_v2.csv`.
4. Run:

```sh
python tools/trace_log_analyzer_v2.py pyokotan_runtime_trace_v2.csv --outdir outputs/runtime_analysis
```

The analyzer's bank-to-physical-offset calculations are labeled estimates, not final proof.

## Important limitation

This is not a complete dialogue dump and no Vietnamese-patched ROM is included. The `.tbl` and Japanese kana candidates remain conservative/provisional until runtime reads, PPU tile writes, and actual mapper state confirm the text byte-to-glyph path.
