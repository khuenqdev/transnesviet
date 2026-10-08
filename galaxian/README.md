# Galaxian (NES) – Vietnamese translation patch

**Base ROM:** `galaxian.nes`, 16,400 bytes, CRC32 `8451DC60`, SHA-1 `a5f7a67a40b7a0a47a48f2280938129a1335dcaa` (NES 2.0 header, NROM, 8 KB PRG + 8 KB CHR)
**Patched ROM:** CRC32 `94875BBD` (same size; header untouched)
**Patch:** `galaxian_vi.ips` (954 bytes, 763 bytes changed). Apply it with Lunar IPS, Floating IPS, or RomPatcher.js.

## Translated text

| ID | Original | Vietnamese | Where | CHR addr |
|---|---|---|---|---|
| 0 | 1UP | NGƯỜI 1 | title + HUD | $17A6 |
| 31 | 2UP (in game) | NGƯỜI 2 | HUD | $17BA |
| 2 | 2UP (title) | NGƯỜI 2 | title | $17B0 |
| 1 | HI-SCORE | ĐIỂM CAO | title + HUD | $1785 |
| 3 | MISSION: DESTROY ALIENS | NHIỆM VỤ: DIỆT SINH VẬT LẠ | attract | $14C7 |
| 4 | WE ARE THE GALAXIANS | CHÚNG TA LÀ GALAXIAN | attract | $159C |
| 5 | - SCORE ADVANCE TABLE - | - BẢNG ĐIỂM - | attract | $173C |
| 6 | CONVOY  CHARGER | ĐỘI HÌNH  LAO XUỐNG | attract | $15B3 |
| 27 | 60 … PTS (×4 rows) | 60 … ĐIỂM | attract | $15C9 |
| 7 | 1 PLAYER | 1 NGƯỜI CHƠI | title | $15F1 |
| 8 | 2 PLAYERS | 2 NGƯỜI CHƠI | title | $174C |
| 9 | ©1979 1984 NAMCO LTD. | (unchanged) | title | $14E4 |
| 10 | ALL RIGHTS RESERVED | BẢO LƯU MỌI QUYỀN | title | $1728 |
| 17 | PLAYER 1 | NGƯỜI CHƠI 1 | game | $175B |
| 18 | PLAYER 2 | NGƯỜI CHƠI 2 | game | $176A |
| 20 | READY | SẴN SÀNG | game | $179B |
| 21 | PAUSE | TẠM NGƯNG | game | $1779 |
| 19 | GAME  OVER | KẾT THÚC | game (2P) | $1790 |
| — | GAME OVER (sprite fly-in, PRG $FBDB) | KẾT THÚC | game | PRG |

The score-table digits (150/200/300/800, 100, 80, 60) are unchanged. The copyright line stays in English because it's a legal notice with a company name.

## What was changed

1. **Font (CHR-ROM).** I drew 19 accented capitals in the game's 2-pixel-stroke style, in bitplane 0 so they match the letters' colour. The title screen draws its background from pattern table 0, while gameplay and attract mode use pattern table 1, so each glyph went into whichever table(s) display it:
   - Both tables: `15`=Ể `16`=Đ `1A`=Ư `20`=Ờ `22`=Ơ `27`=Ả `2A`=Ế `40`=Ú. These replace the now-unused E, F, J, P, R, W, Z and a blank `$FF` tile.
   - PT1 only: `21`=Ẵ (Q is only shown on the title, which uses PT0), `42`=Ạ, `99`–`9F`=À Ệ Ụ Ậ Ộ Ì Ố (blank `$FF` tiles after the namcot logo).
   - PT0 only: `41`=Ọ, `43`=Ề (blank `$FF` tiles).
2. **Strings.** The text lives in CHR $1480–$17FF and is copied to RAM $0300–$067F at boot. Each string is `row, col, (tile+$30)…, $2A`. I repacked all strings into the free space there (379 of 413 bytes used) and updated the pointer table. The logo strings were left in place.
3. **PAUSE → TẠM NGƯNG.** The game writes the PAUSE column at run time ($E398 `STA $0603`). I pointed that write at the new string's column byte and changed the centring and clamp constants at $E385/$E38D/$E391 so the 9-letter word stays centred and never runs past the 26-tile line buffer.
4. **GAME OVER sprite animation.** This is not in the string table: 8 sprites fly in using a tile table at $FBDB and target-X table at $FBE3. I changed both so the sprites spell `KẾT THÚC`, centred, with one blank sprite for the space.

Not touched: the music data pages the hidden sound-test easter egg reads straight from CHR ($0600, $1600, $1800, $1A00, $1B00), the stage-path data at CHR $098E, the "PTS" tiles, and the `COPR.1984 NAMCO` boot signature at $E000.

## Files
- `galaxian_vi.tbl` – table for PT1 text (HUD, gameplay, attract)
- `galaxian_vi_title.tbl` – table for PT0 (title screen, GAME OVER sprites). In the string data each byte = tile + $30.
- `galaxian_vi_toolkit.zip` – Python sources to rebuild or adjust the patch (`build.py`, `glyphs.py`, `slots.json`, `options.json`) plus the small NES emulator (`nes.py`) I used for testing.

## Testing
I checked everything in the bundled emulator: title, attract, 1P and 2P start, PAUSE with the ship at both edges, the GAME OVER animation, and the 2P game-over text. A real emulator (Mesen/FCEUX) or hardware hasn't been tested yet. The small digit at the top-left of the screenshots is overscan row 0 and appears in the original game too.
