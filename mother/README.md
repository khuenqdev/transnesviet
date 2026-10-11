# MOTHER (NES) → Vietnamese — outputs of stages 1–3

Base ROM: `mother.nes`, CRC32 `ABBE02FA` (not included; rebuild it from `mother_hexdump.txt` with
`python stage1_extraction/mother_text_extract.py --hexdump mother_hexdump.txt --out out`).

| Folder | Stage | Main deliverables |
|---|---|---|
| `stage1_extraction/` | Text extraction | `mother_script.json`, `mother_translation_sheet.csv`, `mother_script_en.txt`, `mother.tbl`, extractor + report |
| `stage2_font/` | Vietnamese font + encoding | `mother_vi_font.ips` (→ CRC32 `547D1633`), `mother_vi.tbl`, `mother_vi_charmap.json`, font/preview images, report |
| `stage3_renderer/` | Mark-row text renderer | `mother_vi_stage3.ips` (→ `71B930DC`), `mother_vi_stage3_test.ips` (→ `CBF3A597`, test only), demo/regression screens, report |

All IPS patches apply to the **original** ROM (they are not cumulative on top of each other):
stage 3 already contains the stage-2 font.

`stage3_renderer/` holds the current versions of the shared scripts (`mother_vi_codec.py` there adds
`check_marks()`); `stage3_renderer/nes.py` is a shim that imports the supplied `emu.py` — put
`emu.py` next to it to run the emulator tools.
