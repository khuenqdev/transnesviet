PYOKOTAN NO DAI MEIRO — STAGE 5 OUTPUTS
======================================

Start with:
  outputs/pyokotan_rom_analysis_v5.txt
  outputs/pyokotan_chr_inventory_summary_v5.json
  outputs/pyokotan_font_candidate_catalog_v5.csv
  outputs/runtime_trace_instructions_v2.md

New scripts:
  tools/chr_inventory.py
    Reads NES 2bpp CHR ROM and writes an inventory of each physical 8x8 tile,
    duplicate groups, page summaries, a candidate font catalog, and atlases.
  tools/pyokotan_fceux_text_trace_v2.lua
    Runtime observer for candidate text reads, Mapper 69 banks, and PPU writes.
  tools/trace_log_analyzer_v2.py
    Converts the runtime CSV to a summary, PRG bank-context JSON, and detailed
    PPU $2007 writes with heuristic tile/CHR-offset estimates.

Outputs:
  pyokotan_chr_tile_inventory_v5.csv / .json
  pyokotan_chr_page_summary_v5.csv
  pyokotan_chr_exact_duplicates_v5.json
  pyokotan_font_candidate_catalog_v5.csv / .json
  pyokotan_chr_inventory_summary_v5.json

References:
  reference/chr_tiles_0000_00ff_upscaled.png
  reference/chr_tiles_0100_01ff_upscaled.png
  reference/chr_physical_page_00_full.png
  reference/chr_physical_page_00.png through chr_physical_page_15.png

Re-run CHR inventory:
  python tools/chr_inventory.py pyokotan.nes --outdir outputs --refdir reference --all-bank-atlases

Run trace analyzer after capturing in FCEUX:
  python tools/trace_log_analyzer_v2.py pyokotan_runtime_trace_v2.csv --outdir outputs/runtime_analysis

Important: no runtime trace was captured in this environment. This is not a
complete dialogue extraction or a Vietnamese-patched ROM. CHR tile indices do
not establish a text encoding without observed bank state and render behavior.
