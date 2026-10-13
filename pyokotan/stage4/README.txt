PYOKOTAN NO DAI MEIRO — LOCALIZATION REVERSE-ENGINEERING TOOLKIT, STAGE 4

Start here:
  outputs/pyokotan_rom_analysis_v4.txt
  outputs/pyokotan_stage4_summary.json
  outputs/pyokotan_fixed_table_row_audit_v4.csv

New v4 work:
  tools/static_code_xref.py
    Best-effort reachable-code disassembly from reset, NMI and IRQ entry points.
  tools/scan_row_pointer_values.py
    Raw PRG scan for the little-endian CPU addresses of the 12 ASCII row starts.

Main new outputs:
  outputs/pyokotan_reachable_disassembly_v4.json and .csv
  outputs/pyokotan_code_xrefs_v4.json
  outputs/pyokotan_row_pointer_value_scan_v4.json and .csv
  outputs/pyokotan_fixed_table_row_audit_v4.json and .csv
  outputs/pyokotan_reset_path_disassembly_v4.txt
  outputs/pyokotan_rom_analysis_v4.txt

Core text tools and prior-stage files are included under stage3/ in the ZIP.
The original pyokotan.nes ROM is intentionally not included. Place your own ROM at
that path, or pass its path as the first argument to either Python script.

Example:
  python stage4/tools/static_code_xref.py pyokotan.nes --outdir stage4/outputs
  python stage4/tools/scan_row_pointer_values.py pyokotan.nes --outdir stage4/outputs

Important limitations:
- This is static analysis only; the emulator trace has not been run here.
- Disassembly is best effort, based on the reset bank map and reachable control flow.
- A raw two-byte address match is not proof of a pointer.
- The current .tbl and text JSON remain conservative starter outputs, not a complete
  Japanese dialogue dump or a patched Vietnamese ROM.
- Unknown row trailer bytes must not be edited as text without runtime confirmation.

Mapper technical reference:
  https://www.nesdev.org/wiki/INES_Mapper_069
  https://github.com/RigleGit/nes-specs/blob/main/cartridgesandmappers.md
