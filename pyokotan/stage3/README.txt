PYOKOTAN LOCALIZATION TOOLKIT — STAGE 3
======================================

This stage adds a physical-PRG-to-CPU-window audit and an emulator runtime trace workflow.
It does not claim complete Japanese dialogue extraction, and it does not patch the ROM.

New tools
---------
tools/bank_mapping_audit.py
  Records the strong static hypothesis that PRG bank 14 maps at $C000 and the fixed
  final bank maps at $E000, based on interrupt/reset vectors and the candidate text block.

tools/scan_ascii_candidates.py
  Enumerates printable PRG runs and creates a conservative readable-candidate shortlist.
  Most printable runs in a graphics-heavy ROM are not text; every candidate is marked
  heuristic and requires context validation.

tools/pyokotan_fceux_text_trace.lua
  Observes candidate text-region reads, mapper writes, and PPU-register writes in FCEUX.
  It does not modify ROM or emulated memory.

tools/trace_log_analyzer.py
  Summarizes the trace CSV and exports focused JSON/CSV results.

tools/rom_audit.py, tools/extract_text.py (fixed to preserve space mappings), tools/build_text_dump_v3.py,
tools/scan_pointer_candidates.py, tools/scan_ascii_candidates.py, tools/trace_log_analyzer.py,
tools/build_chr_atlas.py
  Earlier repeatable static analysis utilities retained from stage 2.

Outputs
-------
outputs/pyokotan_rom_analysis_v3.txt       Main report
outputs/pyokotan_text_dump_v3.json         Structured known-text/template records + audit notes
outputs/bank_mapping_audit.json            CPU/PRG mapping hypothesis with vectors
outputs/ascii_run_census.json/.csv         Full printable-byte run census + heuristic candidates
outputs/runtime_trace_instructions.md      How to capture runtime evidence in FCEUX
outputs/runtime_trace_capture_template.csv Empty CSV header for integrations
outputs/charset_sequence_candidates.json Character-sweep candidates, not dialogue
outputs/runtime_trace_summary_template.json Empty-trace analyzer smoke-test result
outputs/pyokotan_v3.tbl                    Conservative TBL, no blanket JIS X 0201 assumption

Run static tools (Python 3 standard library, except the CHR atlas builder needs Pillow)
--------------------------------------------------------------------------------------
  python tools/rom_audit.py /path/to/pyokotan.nes --out outputs/rom_fingerprint.json
  python tools/extract_text.py /path/to/pyokotan.nes --tbl pyokotan_v3.tbl --out outputs/text_dump.json
  python tools/scan_pointer_candidates.py /path/to/pyokotan.nes --out outputs/pointer_candidate_audit.json
  python tools/bank_mapping_audit.py /path/to/pyokotan.nes --out outputs/bank_mapping_audit.json
  python tools/scan_ascii_candidates.py /path/to/pyokotan.nes --out-json outputs/ascii_run_census.json --out-csv outputs/ascii_run_census.csv

Runtime trace (requires FCEUX)
------------------------------
See outputs/runtime_trace_instructions.md. The Lua logger has not been run in this
headless workspace; check the FCEUX Lua console for API/version-specific issues.

The user's original ROM is intentionally not duplicated in the ZIP. Supply pyokotan.nes
as an argument to tools; the extractor validates PRG+CHR CRC32 against this analyzed dump.
