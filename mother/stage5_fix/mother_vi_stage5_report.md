# MOTHER (NES) → Vietnamese — Stage 5: Name-Entry Screens and Opening Story with Full Tones

**Input:** `mother.nes`, CRC32 `ABBE02FA`
**Output:** `mother_vi.ips` applied to the original ROM gives `mother_vi.nes`, **CRC32 `EFEC2D6B`** (786,448 bytes).
This patch replaces the stage-4 patch (`814F319F`) and includes everything from stages 2–4.
It was checked by applying it to the original ROM: the result is byte-identical to the built ROM.

## 1. Result

| Screen | Before (stage 4) | Now (stage 5) |
|---|---|---|
| Naming prompts | Vietnamese | Unchanged ("Cậu bé này tên gì?" …) |
| Keyboard commands | ◆Back ◆End ◆Previous | **◆Xóa ◆Xong ◆Quay lại** |
| Keyboard letters | A–Z, a–z, `. ' - :` | A–Z, a–z, **Đ Ơ Ư / đ ơ ư** |
| Reserved-name error | English (6 lines) | **"Tên này đã có nhân vật trong game dùng rồi. Hãy thử lại và ghi IN HOA nha."** |
| Confirm screen | "Favorite food:", "Is this OK? Yes No" | **"Món ưa thích:", "Được chưa? Có Không"** |
| Opening story | Unaccented, single-spaced | **Full tones and diacritics, double-spaced** |
| "80 years have passed since then." | Unaccented | **"80 năm đã trôi qua / kể từ đó."** |

`build_report.json`: **0 errors, 0 warnings**. All script, names and UI checks from stage 4 still pass.

## 2. Emulator verification (`screenshots/`, played from power-on)

| Shot | What was checked | Result |
|---|---|---|
| 01 | Naming screen: prompt, keyboard, ◆Xóa / ◆Xong / ◆Quay lại | Marks correct, layout unchanged |
| 02 | Typed **Đ → ư → n** with the new keys | Name buffer `93 8F EE` = "Đưn", shown in the name field |
| 03–05 | Typed the reserved name "Mary" → error → back to the keyboard | Error shown with marks; keyboard redrawn cleanly, no stray marks |
| 06 | Confirm screen | "Đưn" and other names, "Món ưa thích:", "Được chưa? Có Không" |
| 07–11 | Opening story, page 1 (13 lines) and page 2 | Full tones, double-spaced, nothing cut off |
| 13–15 | Opening → bedroom → menu → Talk | Game continues normally; "Đưn" appears in the Name window |
| — | NMI time while the 28-column story lines are typed | Worst frame 1,124 cycles (vblank ≈ 2,273) |

## 3. How it works

### 3.1 Opening story

- **Where the text lives.** When the naming screen opens, PRG bank `$19` `$B800–$BFFF` is copied to PRG-RAM `$6000–$67FF`. The story is read from that RAM copy. The CHR copy at `$1ECD0` that stage 4 also edited is never read, so stage 5 restores it to the original bytes.
- **How it is drawn.** The text goes through the normal typewriter (`$C707`), which stage 3 already taught to draw marks. The caller in bank `$14` (`$9B13`) ran **`DEC $77` after every line** (`$9B1E`), which cancels one of the two row steps a newline makes. That is the only reason the story was single-spaced.
- **Fix.** `$9B1E` `C6 77` → `EA EA`. The story is now double-spaced, each line gets a free row above it for marks, and the stage-3 renderer handles the rest.
- **Space.** An emulator trace showed that nothing but the initial copy writes to `$6000–$67FF` during naming and the opening. The full range `$64D0–$67FF` (816 bytes, up from 463) is therefore available:

  | Block | RAM address | Size |
  |---|---|---|
  | Page 1 | `$64D0` | 408 bytes |
  | Page 2 | `$6668` | 35 bytes |
  | Relocated error message | `$668B` | 107 bytes |
  | Free | — | 266 bytes |

  Pointers changed: `$9ACC/$9ACE` (page 2) and `$9CE7/$9CE9` (error message).
- **Limits.** Page 1 is at most **13 lines** (screen rows 4–28) of at most 28 columns. To fit, the story was **slightly condensed**: "all by himself" is folded into "lặng lẽ", and "his wife" is dropped from the last line. Every event and name is kept.

### 3.2 Name-entry screens

- **Keyboard.** The entry routine (bank `$14` `$9C4E`) stores `$6470[cursor]` directly, so the grid strings decide what is typed. `$A1/$A2/$A3` in rows 4–5 are the Back/End/Previous commands and are left alone. The grid has one byte per letter, so only letters with their own tile can be offered: **Đ Ơ Ư đ ơ ư** replace `. ' - :` and two of the four space cells.
- **Screen text.** The screen text is stored in CHR `$17800–$17FFF` and copied to RAM `$6C00` when the screen opens (32 × 64-byte NMI reads). Each block is printed from a start pointer, so I rebuilt `$6C66–$6CFF` (153 of 154 bytes used) and moved two pointers: `$9AD6` (names/favourite food) and `$9ADD` (confirm box). The ◆ markers and "Có"/"Không" stay on the English columns, because the cursor sprite positions are fixed in code.
- **Error message.** It is printed over the keyboard (column 8, rows 15–25), and the keyboard is redrawn afterwards. The redraw does not clear the mark row of the "◆Xóa ◆Xong" line, so **line 5 of the message must contain no top marks**. The builder checks this. ("ghi IN HOA nha." has none.)

## 4. Limits (honest list)

- **No tone marks when typing names.** The entry routine stores one byte per letter, and a toned letter needs two (mark + letter). Supporting it would mean rewriting the entry routine with dead keys for the tones. Names can use Latin letters plus Đ Ơ Ư đ ơ ư. Toned names still display correctly anywhere (stage 3 renderer), as shown with "Hùng" in stage 3.
- **Punctuation removed from the keyboard:** `. ' - :` (two of the four space cells remain).
- **Opening story slightly condensed**, as described in §3.1.
- **Still English:** the file-select screen (Continue/Copy/Erase, "will vanish. OK?") is outside this stage, along with the other stage-4 English UI.

## 5. Rebuild and edit

```
python mother_vi_build.py --rom mother.nes --script mother_script.json --tr translations --out out
python mother_vi_stage5_test.py out/mother_vi.nes shots        # emulator check of the stage-5 screens
python mother_vi_export_sheet.py mother_script.json translations out/sheet.csv
```

- `translations/vn_intro.py`: the opening story. Write one string per screen line; the builder checks line count, width and bytes.
- `translations/vn_naming.py`: keyboard commands, confirm screen, error message and keyboard rows, with column checks.

## 6. Files

| File | Purpose |
|---|---|
| `mother_vi.ips` | **Final patch** for `mother.nes` (ABBE02FA → EFEC2D6B) |
| `build_report.json` | Build statistics and checks, including the `stage5` section (addresses, free space) |
| `mother_vi_translation_sheet.csv` | All strings, plus the new `STAGE5_*` rows |
| `translations/` | `vn_01–08`, `vn_names`, `vn_ui`, **`vn_intro` (new, with tones)**, **`vn_naming` (new)** |
| `mother_vi_stage5.py` | Stage-5 patcher, called from `mother_vi_build.py` |
| `mother_vi_stage5_test.py` | Emulator test that produced the screenshots |
| `mother_vi_export_sheet.py` | CSV export |
| Other tools | Stage 1–4 tools, unchanged except `mother_vi_build.py` (calls stage 5) and `final_play.py` (relative path) |
| `screenshots/` | Emulator captures 01–15 |
