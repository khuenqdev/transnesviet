# Galaxian (NES) – Vietnamese Translation: Full Process Log

This document records every step taken to translate *Galaxian* (Namco, NES/Famicom) into Vietnamese with full tone marks and diacritics, including the analysis, the problems found along the way, and how the result was verified.

---

## 1. Inputs

| Input | Content |
|---|---|
| `galaxian_hexdump.txt` | Full hex dump of the ROM (16,400 bytes) |
| `galaxian_romfacts.txt` | ROM fact sheet: NROM (mapper 0), 8 KB PRG at file `$0010`, 8 KB CHR at file `$2010`, vectors NMI `$E20C` / RESET `$E020`, no free space found |
| `galaxian.tbl` | Character table: `00–09` digits, `0A–0F` alternate digits, `10` space, `11–2A` A–Z, `2B` `-`, `2C` `.`, `2D` `©`, `A3` `:` |

---

## 2. Rebuilding and validating the ROM

1. Parsed each `OFFSET: XX XX …` line of the dump, checking that offsets were contiguous.
2. Result: 16,400 bytes, CRC32 **`8451DC60`**, SHA-1 `a5f7a67a…dcaa`, headerless CRC32 `084F61CD`, all matching the fact sheet.

**Note on the dump header.** The dump's metadata says "52 banks × 16 KB PRG", which is wrong. The header is NES 2.0 (byte 7 = `$08`). Byte 9's upper nibble is `$F`, so byte 4 (`$34`) uses the exponent-multiplier form: 2^(`$34`>>2) × (2×(`$34`&3)+1) = 2^13 × 1 = **8,192 bytes**. This agrees with the fact sheet.

Memory map used from then on:

- PRG: 8 KB, mirrored at `$C000–$FFFF`; code runs at `$E000–$FFFF`. File offset = `$10 + (cpu − $E000)`.
- CHR: 8 KB at file `$2010`. Pattern table 0 (PT0) = CHR `$0000–$0FFF`, PT1 = CHR `$1000–$1FFF`.

---

## 3. Building an analysis emulator

The text and graphics depend on runtime behaviour: which pattern table is active, what the scroll is, and what the code writes. To see that, I wrote a small Python NES emulator (`nes.py`):

- Full official 6502 instruction set (no decimal mode, as on the 2A03).
- PPU at register level: `$2000/$2001/$2002/$2005/$2006/$2007`, OAM DMA (`$4014`), horizontal mirroring, palette RAM, read buffer.
- Controller strobe and shift on `$4016`.
- Frame timing: vblank and NMI at the start of each frame, about 29,781 CPU cycles per frame.
- Renderers that draw a nametable and the sprites to PNG.

It is not a cycle-accurate emulator. It is good enough to run the game's logic and capture screens.

---

## 4. Mapping the game's screens and text

### 4.1 Attract-mode run (no input)

About 1,800 frames recorded the title screen, the vertical scroll-in, and the attract page. I found these English strings:

- HUD: `1UP`, `HI-SCORE`, `2UP`
- Title: `1 PLAYER`, `2 PLAYERS`, `©1979 1984 NAMCO LTD.`, `ALL RIGHTS RESERVED`
- Attract: `MISSION: DESTROY ALIENS`, `WE ARE THE GALAXIANS`, `- SCORE ADVANCE TABLE -`, `CONVOY  CHARGER`, the score rows with `PTS`
- Gameplay (from the dump's ASCII column): `PLAYER 1`, `PLAYER 2`, `GAME  OVER`, `READY`, `PAUSE`

### 4.2 Gameplay runs (scripted input)

I scripted games that press Start, move and fire at random, pause and unpause, and lose all lives. These captured `READY`, `PAUSE`, and the sprite-based **GAME OVER fly-in**: eight letters fly in from different directions. That turned out to be a second, separate text system (section 6.4).

### 4.3 Where the text lives

The text is not in PRG. At boot, the code at `$E0B8` sets the PPU address to `$1480` and copies CHR `$1480–$17FF` into RAM `$0300–$067F` through `$2007` reads. A second copy moves CHR `$098E` (`$B2` bytes) into `$014E–$01FF`. That block is not text and was left alone.

**String format**, decoded from the print routine at `$F937`:

```
row, column, (tile + $30) …, $2A
```

- Pointer table: RAM `$0301 + 2n` (CHR `$1481 + 2n`). Each pointer holds a CHR address; the routine subtracts `$1180` to get the RAM address.
- The routine clears a 26-byte line buffer at `$06BC` to spaces (`$10`), then copies characters, subtracting `$06D6` (= `$30`) from each byte.
- **Limits:** at most 26 characters per line, and no encoded byte can equal `$2A` (the terminator). So tile `$FA` can never appear in a string.
- 35 pointers exist. IDs 11–16, 22 and 34 draw the Galaxian/namcot logos from tiles; I left those untouched.

### 4.4 Code that touches the string data

I scanned PRG for absolute-mode instructions addressing `$0300–$067F`. The only one that modifies string data is at `$E398`: `STA $0603`. It writes the column of the `PAUSE` string at runtime so the word follows the ship. Everything else reads strings through the pointer table, so the strings can be safely repacked.

---

## 5. Pattern-table analysis (finding room for new glyphs)

The ROM has no free PRG space, and the alphabet holds only A–Z. Vietnamese accented capitals had to go into CHR tiles the game never shows.

### 5.1 Which table draws what

Logging `$2000` writes showed:

- **Title screen**: background uses **PT0** (`PPUCTRL = $88`).
- **Attract page and gameplay**: background uses **PT1** (`$90`).
- **Sprites** (including the GAME OVER letters): always **PT0**.

So each accented letter must be in the table(s) that display it.

### 5.2 Visible-tile tracking

A tracker recorded every background tile that actually appears on screen, per table, using the real vertical scroll, and every sprite tile, over about 11,000 frames of attract mode and gameplay.

**Two bugs in my tracker, both found and fixed:**

1. The game reads `$2002` during NMI, which cleared the emulator's vblank flag before the per-frame pattern-table snapshot ran. The snapshot never updated, and every frame was attributed to the wrong table. Fixed by snapshotting at a fixed cycle point instead of on the flag.
2. The title uses a vertical scroll value of 255, i.e. ≥ 240. The NES treats that as a negative offset into the same nametable, not a wrap into the next one. Fixed by handling Y ≥ 240 separately.

With both fixed, the results were consistent with the screenshots.

### 5.3 Transition check

I checked every frame of the title scroll-in to confirm that no title text row is ever shown while PT1 is active. That makes PT1 tiles used only for title letters (e.g. `Q` at `$21`) free for reuse in PT1.

### 5.4 Free / reusable slots chosen

- Letters the Vietnamese text never uses: **E, F, J, P, R, W, Z** (tiles `$15 $16 $1A $20 $22 $27 $2A`), plus Q (`$21`) in PT1 only.
- Blank `$FF`-filled tiles that are never shown: `$40–$43`, `$99–$9F`.

---

## 6. Translation

### 6.1 Vietnamese text

| ID | Original | Vietnamese | Shown in |
|---|---|---|---|
| 0 | 1UP | NGƯỜI 1 | title + HUD |
| 1 | HI-SCORE | ĐIỂM CAO | title + HUD |
| 2 / 31 | 2UP | NGƯỜI 2 | title / HUD |
| 3 | MISSION: DESTROY ALIENS | NHIỆM VỤ: DIỆT SINH VẬT LẠ | attract |
| 4 | WE ARE THE GALAXIANS | CHÚNG TA LÀ GALAXIAN | attract |
| 5 | - SCORE ADVANCE TABLE - | - BẢNG ĐIỂM - | attract |
| 6 | CONVOY  CHARGER | ĐỘI HÌNH  LAO XUỐNG | attract |
| 27–30 | 60 … PTS (4 rows) | 60 … ĐIỂM | attract |
| 7 / 8 | 1 PLAYER / 2 PLAYERS | 1 NGƯỜI CHƠI / 2 NGƯỜI CHƠI | title |
| 9 | ©1979 1984 NAMCO LTD. | unchanged (legal notice) | title |
| 10 | ALL RIGHTS RESERVED | BẢO LƯU MỌI QUYỀN | title |
| 17 / 18 | PLAYER 1 / PLAYER 2 | NGƯỜI CHƠI 1 / NGƯỜI CHƠI 2 | gameplay |
| 19 | GAME  OVER | KẾT THÚC | gameplay (2P) |
| 20 | READY | SẴN SÀNG | gameplay |
| 21 | PAUSE | TẠM NGƯNG | gameplay |
| — | GAME OVER sprite fly-in | KẾT THÚC | gameplay |

**Wording choices made to fit the limits:**

- "BẢNG ĐIỂM" instead of "BẢNG TÍNH ĐIỂM", and "TẠM NGƯNG" instead of "TẠM DỪNG". Each avoids an extra accented glyph that would not fit in the free tiles.
- "SINH VẬT LẠ" for *aliens* keeps the line at exactly 26 characters, the line-buffer maximum.
- "ĐỘI HÌNH" (formation) for *convoy* and "LAO XUỐNG" (dive down) for *charger* describe the arcade's two enemy states.

### 6.2 Glyph design

The 19 accented capitals needed: **Đ À Ả Ạ Ẵ Ậ Ú Ụ Ư Ì Ọ Ố Ộ Ơ Ờ Ệ Ế Ề Ể**.

Design rules, matching the game's font:

- 8×8, 2-pixel strokes, column 0 blank, baseline on row 7.
- Drawn in **bitplane 0 only**, which is how the game's letters are stored, so they take the same palette colour as the surrounding text.
- Glyphs with a top mark (À Ú Ì Ả Ố Ế Ề Ể Ờ Ẵ) use a shortened 5-row letter body with the mark above. Glyphs with a dot below (Ạ Ụ Ọ Ậ Ệ Ộ) raise the body and put the dot on row 7.
- Double-mark letters (Ế Ề Ể Ố Ẵ) place the circumflex/breve on the left and the tone on the right.

Iterations:

1. First draft, previewed at 10× scale.
2. A preview-renderer bug: it read only bitplane 1 of the original font, so the stock letters showed blank. Fixed by OR-ing both planes.
3. Refined Đ (shorter crossbar), the horns on Ư/Ơ (moved to the top-right corner), Ờ (grave mark repositioned), and Ẵ (tilde over the breve), each checked in full Vietnamese lines.

### 6.3 Glyph slot assignment

| Tables | Tile → glyph |
|---|---|
| PT0 + PT1 (same index in both) | `15`=Ể `16`=Đ `1A`=Ư `20`=Ờ `22`=Ơ `27`=Ả `2A`=Ế `40`=Ú |
| PT1 only | `21`=Ẵ `42`=Ạ `99`=À `9A`=Ệ `9B`=Ụ `9C`=Ậ `9D`=Ộ `9E`=Ì `9F`=Ố |
| PT0 only | `41`=Ọ `43`=Ề |

Glyphs used by strings that appear under both tables (HUD: NGƯỜI, ĐIỂM) and by the PT0 GAME OVER sprites (Ế, Ú) share the same index in both tables, so one encoded string works everywhere. The build script asserts this.

### 6.4 Encoding and repacking strings

- Each character is mapped to its tile, then `+$30`. The builder asserts that no byte equals `$2A`, that no line exceeds 26 columns, and that every glyph exists in the table(s) where the string is displayed.
- Digits in the HUD/player strings use the alternate digit tiles `0A–0F`, as the original does, so they take the letter colour.
- The old text areas were cleared to `$FF`, and all strings were repacked longest-first into three free regions:
  - CHR `$14C7–$14FF`, `$159C–$15FF`, `$1700–$17FF`
  - Total used: **379 of 413 bytes**.
  - The logo strings at `$1500–$159B` stayed where they were.
- The pointer table was updated for every moved string.

### 6.5 Code patches (PRG)

**a) PAUSE → TẠM NGƯNG** (9 characters instead of 5)

Original code computes the column from the ship's X position:
`col = (clamp($84 − X, $30, $D0) − $30) >> 3`, then `STA $0603`.

| Address | Original | Patched | Purpose |
|---|---|---|---|
| `$E384` | `ADC #$84` | `ADC #$74` | Shift left by 2 tiles to stay centred on the ship |
| `$E38C` | `CMP #$D1` | `CMP #$B9` | New right clamp |
| `$E390` | `LDA #$D0` | `LDA #$B8` | Max column = 17 (17 + 9 = 26, the buffer limit) |
| `$E398` | `STA $0603` | `STA $05FA` | Column byte of the relocated string (CHR `$177A` − `$1180`) |

**b) GAME OVER sprite fly-in → KẾT THÚC**

The animation uses a tile table at `$FBDB` and a target-X table at `$FBE3` (8 entries each, sprites from PT0).

| Table | Original | Patched |
|---|---|---|
| Tiles `$FBDB` | `17 11 1D 15 1F 26 15 22` (GAME OVER) | `1B 2A 24 10 24 18 40 13` (K Ế T ␣ T H Ú C) |
| X `$FBE3` | `58 60 68 70 88 90 98 A0` | `60 68 70 78 80 88 90 98` (evenly spaced, centred) |

### 6.6 Areas deliberately left untouched

- The `COPR.1984 NAMCO` signature at `$E000`.
- The logo strings and logo tiles (Galaxian, namcot).
- The `PTS` tiles. They're no longer referenced, but untouched is safer.
- The data block copied from CHR `$098E` to `$014E`.
- The CHR pages read as music data by the hidden sound-test routine.

---

## 7. Building the patch

`build.py` does the following:

1. Verifies the source CRC32 is `8451DC60`.
2. Writes the glyphs into CHR per `slots.json`.
3. Encodes, packs and relocates the strings, then rewrites the pointers.
4. Applies the PRG patches. Each patch first asserts that the original bytes match.
5. Writes `galaxian_vi.nes` (CRC32 **`94875BBD`**, same size, header unchanged).
6. Produces an IPS patch (`galaxian_vi.ips`, 954 bytes, 763 changed bytes), re-applies it to the original, and checks that the result is byte-identical.

---

## 8. Verification

Each scenario below was run on the patched ROM in the analysis emulator and checked by screenshot:

| Scenario | Result |
|---|---|
| Title screen (PT0) | NGƯỜI 1 / ĐIỂM CAO / NGƯỜI 2, menu, BẢO LƯU MỌI QUYỀN correct; logo intact |
| Attract page (PT1) | All four lines and the score table correct |
| 1P start | NGƯỜI CHƠI 1 / SẴN SÀNG |
| 2P mode (Select + Start) | NGƯỜI CHƠI 2 on player switch; NGƯỜI 2 in the HUD |
| Pause, ship at far left and far right | TẠM NGƯNG stays fully on screen and inside the buffer |
| GAME OVER animation | Letters fly in and land as KẾT THÚC, centred |
| 2P game-over text | NGƯỜI CHƠI 1 / KẾT THÚC |

**Not yet done:** testing in a mainstream emulator (Mesen, FCEUX) and on real hardware. The analysis emulator is not cycle-accurate. The patch does not change timing-sensitive code, but a real-emulator check is still recommended.

---

## 9. Deliverables

| File | Description |
|---|---|
| `galaxian_vi.ips` | The translation patch |
| `galaxian_vi_preview.png` | Screenshots of the translated screens |
| `README.md` | Short summary, string table, change list |
| `galaxian_vi.tbl` | Table for PT1 (gameplay, HUD, attract) |
| `galaxian_vi_title.tbl` | Table for PT0 (title, GAME OVER sprites) |
| `galaxian_vi_toolkit.zip` | `build.py`, `glyphs.py`, `slots.json`, `options.json`, `nes.py`, `preview.py` |

**To change a translation:** edit the string list in `build.py` (or the READY text in `options.json`) and run `python build.py` next to an original `galaxian.nes`. The builder stops with an error if a line is too long, a glyph is missing from the needed table, or the string space runs out.
