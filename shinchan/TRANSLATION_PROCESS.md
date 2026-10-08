# Crayon Shin-chan: Ora to Poi Poi (NES): Vietnamese Translation

This document covers how the Japanese Famicom game was translated into Vietnamese with full tones and diacritics: the analysis, the engine changes, the ROM expansion, and how to rebuild the patch.

---

## 1. Deliverables

| File | Purpose |
|---|---|
| `shinchan_vi.ips` | Patch to apply to the original ROM |
| `tools/` | Every script used. `python3 tools/make.py` rebuilds the ROM from scratch |
| `script_ja_vi.tsv` | The full Japanese script next to the Vietnamese translation |
| `screenshot_*.png` | Captures from the headless emulator |

**Base ROM (required):** `shinchan.nes`, 262,160 bytes, CRC32 `F3259AB4`, SHA-1 `a194b3ac9ca499cb4c56ebbb351772a6b310689e`
**Patched ROM:** 393,232 bytes (256 KB PRG + 128 KB CHR), CRC32 `66192626`

The patch also changes the iNES/NES 2.0 header (PRG size 8 to 16 banks). Apply it with any IPS tool (Lunar IPS, Floating IPS, or `tools/mkips.py`, which includes `apply_ips`). Use a mapper-16 emulator such as Mesen, FCEUX or puNES.

---

## 2. Step 1: Rebuild the ROM from the hex dump

`tools/rebuild_rom.py` parses `shinchan_hexdump.txt`, checks that offsets are contiguous, and writes `orig.nes`. The result matches the fact sheet: 262,160 bytes, CRC32 F3259AB4.

---

## 3. Step 2: Hardware analysis

* Mapper 16 (Bandai FCG): `$8008` selects the 16 KB PRG bank at `$8000`, `$8000-$8007` select eight 1 KB CHR banks, and `$8009` sets mirroring. The last bank is fixed at `$C000`.
* The supplied `nes.py` only handles NROM, so `tools/emu16.py` subclasses it with mapper-16 banking, switchable mirroring and a screen renderer. Background rendering only (no sprites); it was used for headless testing.
* `tools/dis.py` is a bank-aware disassembler built on the `OPS` table in `nes.py`.

---

## 4. Step 3: Locating the text

### 4.1 Character encoding (table file)
I rendered every CHR bank to images. Text uses BG tiles from CHR 1 KB bank 2 (`$C0-$FF` = hiragana and punctuation) and bank 1 (`$80-$BF` = katakana). Voiced marks are prefix bytes: `$EF` = dakuten (゛) and `$EE` = handakuten (゜), drawn on the row above the kana. Text lines are therefore 2 tiles tall. The full decoding table is in `tools/jtab.py`.

### 4.2 Control codes (dialogue VM in bank 3, `$84B1-$8A42`)
| Code | Meaning |
|---|---|
| `$2F` | end of string |
| `$3F` | new line |
| `$20` / `$21` | wait for button / timed wait |
| `$30 nn` | insert name *nn* |
| `$31-$33` | speaker-name variables |
| `$34-$38` | number/variable inserts |

### 4.3 Pointer structure
* Group table at bank 3 `$8C1A`: 7 groups → sub-tables → strings (`tools/extract.py`).
* Speaker-name table at `$8B69` (21 names, `$00`-terminated).
* Story scenes select a string with `$048A` (group) and `$0489` (index).

**Result:** 1,045 pointer entries resolving to **441 unique strings**, plus 21 names.

### 4.4 Text outside the dialogue engine
* **Stage title cards:** raw nametable packets in bank 3 (`$B7B3…`, position tables at `$B8C1…`).
* **Title menu, GAME OVER, continue prompt, opponent names, stage ordinals:** packets in the fixed bank (`$F3A7`, `$F3E9`, `$F404`, `$F464`, `$F667`, `$F686`). The call sites in bank 4 set their screen positions.
* **Screen layouts** (pause screen, 1P/2P labels, VS/Endless settings, continue screen, VS result): RLE-compressed nametables stored *in CHR ROM* banks `$78-$7F` and decompressed by `$D905`. The first byte of each stream is the escape marker, followed by `marker, value, count` runs.

---

## 5. Step 4: Font design (`tools/vfont.py`)

The game's 2-row text layout is useful for Vietnamese: the upper tile, which held dakuten, now holds tone marks and hats.

* **Lower tile:** 26 Latin letters, Đ, Ơ, Ư, eight letters with a dot below (Ạ Ẹ Ị Ọ Ụ Ỵ Ợ Ự), punctuation, and digits. Style follows the supplied `glyphs.py`: 2-px vertical strokes and column 0 left blank.
* **Upper tile (14 mark tiles `$F0-$FD`):** acute, grave, hook, tilde, circumflex, breve, and every circumflex/breve + tone combination (e.g. Ấ Ầ Ẩ Ẫ, Ắ Ằ Ẳ Ẵ).
* **Encoding:** a mark byte is a *prefix*, the same mechanism as the original `$EF`/`$EE`. For example, `Ằ` = `$FB $C0`. Unicode NFD decomposition maps every precomposed Vietnamese capital automatically.
* The horn on Ơ/Ư was redrawn as a distinct top-right hook after a legibility comparison.
* All text is **uppercase**. Two-row uppercase is the only layout that fits the 8×8 grid and stays readable with stacked marks.

---

## 6. Step 5: ROM expansion and engine changes (`tools/build.py`)

### 6.1 Expansion
Vietnamese text encodes to about 12.7 KB, larger than the original Japanese. PRG was doubled from 128 KB to 256 KB:
* Banks 0–6 are unchanged. The original fixed bank 7 moves to bank 15, the new last bank.
* **Bank 8** is the new text bank. It holds all strings, pointer tables, names, and a copy of the text-fetch routines (`$87E9-$8A42`) at their original addresses.
* Trampolines in the fixed bank (`$FB90`) switch to bank 8, call the fetch/lookup routine, and switch back to bank 3.

### 6.2 Bank 3 patches
| Address | Change |
|---|---|
| `$85B6`, `$8521` | Ring-buffer fill and pointer lookup go through the text-bank trampolines |
| `$85EF` | `$F0-$FF` are treated as mark prefixes (was `$EE/$EF` only); new code `$22` = **page break** |
| `$850D`, `$8ACD` | Page-break state: show a blinking prompt, wait for A, clear the box, continue |
| `$81C9`, `$82A2`, `$816A`, `$81A1` | Box clear/reset also resets the page-break flag (`$0670`, a previously unused RAM byte) |
| `$8147`, `$815B`, `$81DD`, `$80F8` | Wider dialogue box (24 tiles), text from row 20, prompt moved to the corner |
| `$8151`, `$811A` | Typing speed raised from `$28` to `$50` (names `$C0`); holding A still fast-forwards |

### 6.3 Text encoder (`tools/encoder.py`)
Text is word-wrapped automatically: 23 columns × 3 lines for story boxes, 14 × 1 for the in-match speech bubble, and 22 × 3 for the course-clear message. Longer story lines split into pages with `$22`. Identical strings are deduplicated.

### 6.4 Other screens (`tools/misc.py`)
* Stage titles are rebuilt as two-row packets (top = marks, bottom = letters) and centred.
* Title menu: CHẾ ĐỘ TRUYỆN / VÔ TẬN / ĐỐI KHÁNG.
* GAME OVER → "THUA RỒI! / KHÔNG BỎ CUỘC!". The continue prompt → "TIẾP / THÔI".
* Opponent names and the "MÀN 1/2/3" ordinal now get a mark row; a small new routine in bank 4 (`$BEB8`) draws both rows.
* RLE screen layouts are decompressed, edited, recompressed with `tools/rle.py` (round-trip verified), repacked into the CHR area, and the loader source pointers are patched. The budget was tight: data ends at `$1FEF` of `$2000`, so some labels were shortened.

---

## 7. Step 6: Translation

* All 441 strings were translated by hand: natural, colloquial Vietnamese that keeps Shin-chan's cheeky tone. Shin uses "tớ"; adults use "cô/mẹ/thầy".
* Names stay in Japanese romanisation (SHINNOSUKE, MASAO, KAZAMA…). Action Kamen keeps its name; "ông trùm" is the nickname for the principal.
* Speech bubbles were rewritten to fit 14 characters.
* The complete script is in `script_ja_vi.tsv` and `tools/tr.py`. To change a line, edit it in `tr.py` and run `make.py`.

---

## 8. Step 7: Testing

* Every original patch site is checked with `expect()` before writing, so the build aborts on a wrong base ROM.
* Built-in checks: text-bank capacity, RLE round trip, screen-data size, and branch ranges in the assembler.
* The IPS patch is verified by applying it back to the original ROM.
* In the headless emulator I boot-tested the title menu, the first story scene (speaker names, wrapping, tones, prompt, paging) and the rebuilt settings screens.

---

## 9. Known limitations

1. **The course name on the stage title card** (large kanji graphics such as 「らくらくコース」) is still Japanese. The subtitle line underneath is translated. I traced the routine but didn't finish the patch.
2. **Graphic logos** (the title logo and the large "VS"/"WIN" art) are untouched images.
3. **Testing coverage:** my emulator has no sprite rendering or mid-frame effects, and I did not play through every scene or every game mode. Some lines may still overflow or look cramped on screens I haven't seen. Please do a full playthrough in Mesen or FCEUX before release.
4. Text is uppercase only.

---

## 10. Rebuilding

```bash
cd tools
python3 rebuild_rom.py        # needs ../shinchan_hexdump.txt path inside the script, or place orig.nes here
python3 make.py               # -> shinchan_vi.nes
python3 mkips.py orig.nes shinchan_vi.nes shinchan_vi.ips
python3 dump_script.py        # -> script_ja_vi.tsv
```
Paths inside the scripts point to `/home/claude/w/`; adjust them to your folder.

### Tool index
| Script | Role |
|---|---|
| `rebuild_rom.py` | Hex dump → ROM |
| `dis.py` | 6502 disassembler (bank aware) |
| `jtab.py` | Japanese table + control-code decoder |
| `extract.py` | Pointer-table walker / script dumper |
| `screens.py`, `rle.py` | CHR-stored screen layouts: decompress, compress |
| `vfont.py` | Vietnamese font + Unicode → tile encoder |
| `encoder.py` | Word wrap, paging, string encoding |
| `asm6502.py` | Two-pass assembler for the patches |
| `tr.py` | **The Vietnamese script** |
| `build.py`, `misc.py`, `make.py` | ROM builder |
| `emu16.py`, `drive.py`, `nes.py` | Headless mapper-16 emulator + input driver |
| `mkips.py`, `dump_script.py` | Patch creation and script export |
