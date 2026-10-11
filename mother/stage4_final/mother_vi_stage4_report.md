# MOTHER (NES) → Vietnamese — Stage 4 (final): Translation and ROM Build

**Input:** `mother.nes`, CRC32 `ABBE02FA`
**Output:** `mother_vi.ips` applied to the original ROM gives `mother_vi.nes`: **CRC32 `814F319F`**, 786,448 bytes, NES 2.0 / MMC3, PRG 512 KB + CHR 256 KB.
The patch was verified by applying it to the original ROM; the result is byte-identical to the built ROM.

## 1. What is translated

| Part | Count | Notes |
|---|---|---|
| Script (dialogue, item descriptions, enemy CHECK, battle, Giegue, field messages, ending, anti-piracy) | **1,263 / 1,264** segments | Only S1203 (a battle layout with no text) is unchanged |
| Item / place / PSI / enemy names | 253 | ≤ 11 columns, repacked in bank `$00`, all pointer tables rewritten |
| Status names, guest names (Pippi, EVE, Người Bay) | 8 + 3 | Fixed slots |
| Field Command window, Cash title, battle command window, "can't" messages, Who? | 13 | Edited in place (see §4) |
| Naming prompts | 6 | Full tone marks (the window is double-spaced) |
| Opening story | 2 blocks | **Unaccented** Vietnamese (single-spaced renderer, see §4) |
| Staff credits | 36 | Kept as is (personal names) |

`build_report.json` lists **0 errors, 0 width/mark warnings**. Every line was checked:

- dialogue ≤ 22 columns, battle ≤ 21, enemy CHECK ≤ 22, ending ≤ 28
- ≤ 10 mark bytes per line
- names ≤ 11 columns
- window strings have the same bytes and columns as the English

## 2. Engine change in this stage: script moved from CHR to an expanded PRG

The CHR text area had only 7 KB free, and CHR is at MMC3's 256 KB limit.

- **PRG expanded 256 → 512 KB.** Banks `$00–$1D` are unchanged. Fixed banks `$1E/$1F` are copied to `$3E/$3F`. Banks `$20–$3D` are new text space.
- **Pointer table** (bank `$18`, 2,000 × 3 bytes) now holds `[lo][hi][PRG bank]`. Strings never cross an 8 KB bank boundary.
- **`$CAE9` (request) and `$F99F` (NMI command `$0A`) rewritten.** The NMI maps the text bank at `$8000`, copies 64 bytes to `$0110`, and restores the bank and the `$8000` shadow, as the original code did. The interpreter, typewriter and mark-row renderer are unchanged.
- **Verified with English text** moved to PRG: 4/4 checkpoint screens are pixel-identical to the original ROM.
- **Space used:** the Vietnamese script takes **75.8 KB in banks `$20–$29`**. Banks `$2A–$3D` (160 KB) are still free.

## 3. Emulator check of the final ROM (`screenshots/`)

| Screen | Result |
|---|---|
| Naming prompt "Cậu bé này / tên gì?" | Tone marks drawn in the gap row |
| Opening story | Unaccented text, layout identical to the English |
| Field menu "Menu / Gọi Xem / Kho Trạng / PSI Chọn", "Xu" | Correct |
| Talk → "Cậu đang nói chuyện với ai vậy?" | Typewriter, marks and window are correct; text is read from PRG bank `$20+` |
| Goods window "Thẻ Tiền" | Item name with marks is correct |

## 4. Limits and choices (honest list)

- **Window strings are edited in place.** Their pointers are loaded from code immediates or layout streams, so each string keeps the English byte length and column count. Top marks cost a byte without a column, so they only fit where a padding run can absorb them; the battle menu ("Đánh / Thủ / Hát") is an example.
  - The field Command menu has no padding, so it uses mark-free words: *Gọi, Xem, Kho, Trạng, PSI, Chọn*. Letters with a dot below, plus ơ, ư and đ, are their own glyphs and cost nothing extra.
- **Window titles in the border row must be mark-free.** A mark would be drawn on the map above the window. For this reason the HUD header *Name / Lvl / HP / PP / Exp* stays English.
- **Not translated (shown in English):**
  - Goods action menu (Use/Eat/Give/Drop/Look), State and Setup windows, file-select screen, "Favorite food / Is this OK? Yes No", battle HUD header.
  - These strings either have no padding to absorb marks or were not located by stage 1. They are rarely-read UI. The next step is to relocate their layout streams, starting from the immediate loader found at `$C26C`.
- **Name keyboard** stays A–Z. Player names are Latin, which matches the "names stay Latin" rule from stage 2.
- **Opening story is unaccented** because its renderer is single-spaced (stage-3 finding).
- **Not played in the emulator:** battles, the ending and the anti-piracy screen. They use the same text path; the layout checks above passed.
- **Capital Ẹ Ị Ỵ Ợ Ự Ệ** are not used anywhere (stage-2 font limit): stat names are title case, and EVE speaks in sentence case.

## 5. Glossary (main terms)

| English | Vietnamese |
|---|---|
| Magic Herb | Thảo Dược (Phép) |
| Big Bag | Túi Lớn |
| Bread / Crumbs | Bánh Mì / Vụn Bánh |
| Cash Card | Thẻ Tiền |
| Phone Card | Thẻ Điện Thoại |
| Franklin Badge | Huy Hiệu (Franklin) |
| Onyx Hook | Móc Mã Não |
| Healer | Thầy Chữa |
| Mayor | Thị Trưởng |
| Zoo | Sở Thú |
| Canary Village | Làng Hoàng Yến |
| Queen Mary's Fountain | Suối Nữ Hoàng Mary |
| Mother Ship | Tàu Mẹ |
| Flying Man | Người Bay |
| Bottle Rocket | Tên Lửa Chai |
| Strawberry Tofu | Đậu Phụ Dâu |
| Noodlenoggin | Đầu Bún |
| SAVE / USE / CHECK / EAT | LƯU / DÙNG / XEM / ĂN |
| OFFENSE / DEFENSE / FIGHT / SPEED / WISDOM / STRENGTH / FORCE | Tấn Công / Phòng Thủ / Chiến Đấu / Tốc Độ / Trí Tuệ / Sức Mạnh / Lực (title case, because capital Ệ/Ự have no glyph) |
| PK Fire / Freeze / Thunder / Beam | PK Lửa / Băng / Sấm / Tia |
| LifeUp / Healing | Hồi Sức / Chữa Trị |

Forms of address follow the speaker:

| Speaker | Speaking to | Form |
|---|---|---|
| Sisters | Ninten | anh / em |
| Mom / Dad | Ninten | mẹ, bố / con |
| Adults | the children | cháu / cậu |
| B.B. Gang | the children | tao / mày |
| Giegue | — | ta / ngươi |

Town names stay as in the original.

## 6. Rebuilding and editing

```
python mother_vi_build.py --rom mother.nes --script mother_script.json --tr translations --out out
```

To edit the text, change `translations/vn_*.py`. Write each page as one plain sentence (`{wait}` separates pages); the wrapper line-breaks it to the game's rules. `RAW:` turns wrapping off for signs, menus and the Giegue speech. Rebuild, then check `build_report.json`.

`python final_play.py out/mother_vi.nes shots` plays the ROM in the emulator and saves the screenshots.

## 7. Files

| File | Purpose |
|---|---|
| `mother_vi.ips` | **Final patch** for `mother.nes` (ABBE02FA → 814F319F) |
| `build_report.json` | Build statistics, errors, warnings, untranslated keys |
| `mother_vi_translation_sheet.csv` | Every string: English, Vietnamese source, final in-game layout |
| `translations/` | Translation sources (`vn_01–08` script, `vn_names`, `vn_ui`, `vn_intro`) |
| `mother_vi_build.py`, `mother_vi_expand.py`, `mother_vi_wrap.py` | Stage-4 tools: builder, PRG expansion and text reader, word-wrapper |
| `mother_vi_renderer.py`, `mother_vi_font.py`, `mother_vi_codec.py`, `mother_text_extract.py` | Stage 1–3 tools used by the build |
| `mmc3.py`, `asm6502.py`, `nes.py`, `mother_vi_preview.py`, `final_play.py` | Emulator and assembler support (`nes.py` imports your `emu.py`) |
| `screenshots/` | Final-ROM emulator captures |
