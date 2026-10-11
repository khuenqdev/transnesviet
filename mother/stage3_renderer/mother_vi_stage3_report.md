# MOTHER (NES) → Vietnamese — Stage 3: Mark-Row Text Renderer

**Input:** `mother.nes` (CRC32 `ABBE02FA`)
**Output:** `mother_vi_stage3.ips`, which applies to the original ROM. The result has CRC32 `71B930DC`: the stage-2 font plus the renderer patch. The text is still English.
**Demo patch:** `mother_vi_stage3_test.ips` gives CRC32 `CBF3A597`. It is the stage-3 ROM plus one Vietnamese test message (ID 901). It is for testing only and must not be released.

## 1. Result

The game's text engine now draws stage-2 Vietnamese. A mark byte (`$80–$8D`) placed before a glyph is drawn one tile row above that glyph and takes no column.

| Check (emulator, scripted play from power-on) | Result |
|---|---|
| English regression: naming, intro, field menu, dialogue | **4/4 pixel-identical** to the original ROM (`regression.txt`) |
| Dialogue typewriter with marks | Marks appear above their letters as they are typed; no sound blip for marks |
| `{Ninten}` name insert with marks ("Hùng") | Works in dialogue |
| Name / State window field printer ("Hùng") | Works; the field width still counts columns |
| Scrolling: 7-line message, 4-line window | Marks move with their lines; the window border stays intact; no stale marks are left behind |
| Every mark combination (ắ ằ ẳ ẵ ặ ấ ầ ẩ ẫ ậ, Ở Ữ Ỷ Ễ Ộ …) | Correct (`mother_vi_stage3_demo_sheet.png`) |
| NMI time (worst frame that includes new entry types) | **2,036 cycles**, against NTSC vblank ≈ 2,273. The game's own worst frame in the same run is 2,082. |

## 2. How the original engine works (traced in the emulator)

- **Text rows.** `$C83D` builds one text row as PPU-buffer entries `[05][len][hi][lo][tiles]` in page `$0400`, split at the nametable edge.
- **Gap rows.** `$C86D` builds the row above a window line: side borders plus spaces.
- **Field printer.** `$C9A5` is a fixed-width field printer, used for names and numbers.
- **Typewriter.** Dialogue and battle text (`$C707`) is built into 41-byte records at `$0433 / $045C / $0485 / $04AE / $04D7`. Each record holds two text entries (21 + 1 columns), plus two "clear row below" fill entries and a terminator, which uses **exactly 41 bytes**. The text is then typed one character per frame.
- **Scrolling.** `$C7C1/$C7D4` moves every record up one row twice, re-sending one record per frame.
- **NMI.** The NMI (`$F79F`) walks the buffer from `$E6` and dispatches on the entry type through the table at `$F8C1`. Buffer work starts about 574 cycles after the NMI because of OAM DMA.

## 3. What the patch changes

| # | Where | Change |
|---|---|---|
| 1 | `$C855` text builder | Mark bytes are appended inline to the current entry, which becomes type **`$0C`**. They use no column. |
| 2 | `$C887` gap-row builder | Mark bytes are skipped. |
| 3 | `$C72C` typewriter | Records no longer get fill entries. Their entries become type **`$0B`**. The 10 freed bytes hold the marks. |
| 4 | `$C762/$C7A4` typewriter | A mark is sent as a 1-byte `$0C` entry and the cursor does not advance. |
| 5 | `$C9AB/$C9B4` field printer | Marks inline, or skipped in gap rows. |
| 6 | `$C7C9/$C7DE` scroll | The line leaving the window becomes type **`$0D`** ("clear text row") instead of moving. Moving it would put its marks onto the border. |
| 7 | `$F7D1` NMI walker | Types `$0B` and above go through a trampoline into **PRG bank `$1B`** (`$9500`, 489 bytes). The trampoline saves and restores the MMC3 shadows `$EE/$F6` the same way the game's own NMI command `$0A` does. |

**Two-frame NMI split.** This keeps vblank use within budget.

- **Frame A, types `$0B/$0C`:** writes the text row, then stops while keeping the buffer pending. It sets bit 7 on the first entry; the original walker strips that bit and stops without clearing `$E5`.
- **Frame B, type `$1B`:** writes the full mark row (marks and spaces) and clears the row below.
- **Frame B, type `$1C`:** writes only the marks.

The types are then restored, so later scroll passes can re-send the records.

**Space used:**

| Area | Usage |
|---|---|
| Fixed bank `$FEA2–$FF3F` | All 158 free bytes |
| Freed bytes | 46 of 51 at `$C72C`; 24 of 31 at `$C7DE` |
| Bank `$1B` | 489 of 2,936 free bytes |
| RAM `$0105–$010F` | Bottom of the stack page; never touched in a full emulator run |

**NMI timing (CPU cycles from NMI start to the last PPU write):**

| ROM / content | Worst frame |
|---|---|
| Original, long English dialogue | 1,937 |
| Stage 3, same English dialogue | 1,944 |
| Stage 3, Vietnamese line with 10 marks (frame B) | 2,036 |
| Game's own map redraw after closing a window (unchanged code) | 2,082 |

## 4. Rules for translators (added to the stage-2 rules)

1. **Dialogue and battle lines:** at most 22 columns (unchanged) and **at most 10 mark bytes per line**. A mark byte is any letter with a top mark: sắc, huyền, hỏi or ngã, ˘ or ˆ, and their combinations. Dot-below letters, ơ, ư and đ need no mark byte. Check with `mother_vi_codec.check_marks(text)`.
2. **Do not put marks in window titles inside a border**, such as `┏▬Name▔`. Their marks would be drawn on the map row above the window. Use mark-free titles; a dedicated fix is planned.
3. Names inserted with `{Ninten}` and similar tags may contain marks, but they still count toward the 22 columns and the 10 marks.

## 5. Not covered yet (next stage)

- **Opening story** (`intro`). It uses its own single-spaced renderer, which was not traced yet. A copy of the text also sits in CHR at `$1ECD0`, so the stage-1 note calling CHR `$1E000–$1F7FF` "never read" needs to be re-checked.
- **Ending, credits and anti-piracy screens.** Not traced.
- **Name-entry keyboard.** The Vietnamese letters will need a layout.
- **Battle window.** It uses the same typewriter and scroll code (`$C707/$C7C1` called from bank `$17`), but it was not played in the emulator.
- **Window titles with marks**, and any single-spaced window found during insertion.

## 6. Files

| File | Purpose |
|---|---|
| `mother_vi_renderer.py` | Patch builder: 6502 source, original-byte checks before patching, and IPS output. Run with `--rom mother.nes`. |
| `mother_vi_stage3.ips` | Font plus renderer, applied to the original ROM |
| `mother_vi_stage3_test.ips` / `mother_vi_testrom.py` | Demo ROM: message 901 (Talk to nobody) becomes a 7-line Vietnamese test |
| `mother_vi_stage3_test.py` | Emulator verification: `regress` (English, 4 checkpoints) and `demo` (Vietnamese screenshots) |
| `mother_vi_stage3_patch_listing.asm` | Disassembly of every patched region |
| `mother_vi_codec.py` | Stage-2 codec plus `marks_per_line()` / `check_marks()` |
| `regress_*.png`, `regression.txt` | English regression screens |
| `demo_*.png`, `mother_vi_stage3_demo_sheet.png` | Vietnamese typing, scrolling and Name-window frames |
| `nmi_timing.txt` | Vblank measurements |
| Support files | `mother_vi_font.py`, `mother_vi_preview.py`, `mother_text_extract.py`, `mmc3.py`, `asm6502.py`, `nes.py` (shim that imports your `emu.py`) |
