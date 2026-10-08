# Doraemon: Giga Zombie no Gyakushuu — Vietnamese translation

This repository turns the Japanese Famicom ROM *Doraemon - Giga Zombie no Gyakushuu (Japan).nes* into a fully Vietnamese version, with all tones and diacritics. The existing English fan patch was used as a starting point and as a reference.

| File | Purpose |
|---|---|
| `Doraemon - Giga Zombie no Gyakushuu (Japan).nes` | original ROM (input) |
| `Doraemon - Giga Zombie no Gyakushuu (J) [!].ips` | English fan patch (reference / base) |
| `Doraemon - Giga Zombie no Gyakushuu (VN).nes` | **final Vietnamese ROM** |
| `Doraemon - Giga Zombie no Gyakushuu (VN).ips` | **Vietnamese patch**, apply to the original Japanese ROM |
| `script/A_*.txt`, `script/E_*.txt` | Vietnamese dialogue source |
| `tools/` | all tools (Node.js + one C# test host) |
| `work/` | build inputs: `jp.nes`, `en.nes`, and the test savestate/scripts |
| `emu.exe`, `fceumm_libretro.dll` | headless emulator used for automated screenshots |

## Quick start

Requirements: Node.js (v18+). Windows is needed only for the emulator.

```powershell
# 1. build inputs (only needed once)
Copy-Item "Doraemon - Giga Zombie no Gyakushuu (Japan).nes" work/jp.nes
node tools/ips.js apply work/jp.nes "Doraemon - Giga Zombie no Gyakushuu (J) [!].ips" work/en.nes

# 2. build the Vietnamese ROM
node tools/build.js work/t.nes

# 3. make the distributable patch
node tools/ips.js make work/jp.nes work/t.nes "Doraemon - Giga Zombie no Gyakushuu (VN).ips"
```

`build.js` prints a short report:

```
font: dropped ẺỂỬỶẴẪỠỮỸẶ free codes 0 free tiles 5   <- unused capitals left out of the code table
names: bank B space left 0+2+0+2                      <- bytes left in the name regions
file prompts: lines 21 slots left 2
script A used 3e47 1053 0 0  E used 3ffd 4da 0 0      <- bytes used per script bank
```

If any text contains a character the build cannot encode, or anything does not fit, the build stops with an error that names the string.

---

## How the translation was done, step by step

### Step 1 — Study the original and the English patch

* `tools/ipsmap.js` compared `jp.nes` with `en.nes` bank by bank. This showed which areas the English patch touched: the script banks, the font, the menu tables in bank B, the name entry and the file screens in bank C, and the title in bank 9.
* `tools/disasm.js`, `tools/hexdump.js`, `tools/find.js` and `tools/freespace.js` were used to read code, find byte patterns and find free space in each bank.
* `tools/tables.js` holds the Japanese and English character tables. `tools/script.js` walks the script pointer tables and decodes every message, following jumps and branches:

  ```
  node tools/script.js work/jp.nes jp work/script_jp.txt
  node tools/script.js work/en.nes en work/script_en.txt
  ```

**Key findings:**

* The ROM is MMC1 with 16 × 16 KB PRG banks. Bank 15 (`$C000-$FFFF`) is fixed. Graphics live in CHR-RAM, and the font is uploaded from bank 5 `$9280`.
* The dialogue script is split into two groups. Group **A** (bank 2) is system and battle messages. Group **E** (bank 3) is story and NPC text. Both are reached through pointer tables. The dialogue window is 15 characters wide.
* The Japanese text engine draws every text line as **two tile rows**. The upper row holds the dakuten/handakuten marks (゛ ゜) of the kana below. The English patch leaves that upper row empty.
* **This upper row is what makes full Vietnamese possible.** A vowel can be drawn as a base letter in the text row with its hat, breve or tone mark in the row above.

### Step 2 — Expand the ROM (256 KB → 512 KB)

The Vietnamese script is much longer than the Japanese one and did not fit. `build.js → expand()/patchMapper()` does the following:

* Doubles the ROM to 32 banks and sets iNES header byte 4 to `0x20`.
* Switches to the SUROM variant of MMC1, where CHR register bit 4 selects the upper 256 KB. The bank-switch routine at `$C0B2` is redirected to a small stub in free space at `$FF73`. The stub writes that bit before the normal PRG write.
* Copies banks 14/15 into 30/31, so the fixed bank is present in both halves.

New banks are used as follows:

* `$10`: character-code tables.
* `$11-$14`: script group A.
* `$15-$18`: script group E.

### Step 3 — Vietnamese font and character encoding (`tools/vn.js`)

* The English font layout is kept for digits, `A-Z`, `a-z` and punctuation, so plain letters have **code = tile**.
* The unused tiles `0E`, `10-15` and `55-8F` are replaced with hand-drawn 8×8 glyphs, stored in `vn.js` as ASCII art:
  * `đ Đ ơ Ơ ư Ư` and a dotless `ı`.
  * Dot-below vowels (`ạ ẹ ọ ụ ợ ự …`), generated from the base glyphs.
  * Mark tiles: every combination of hat/breve and tone, each drawn in the lower part of the tile so it sits just above the letter.
  * Single-tile accented letters (`ó1 ô1 á1 ù1 ê1 ớ1 é1 ấ1 ế1`). These are for screens that have no free row above the text, such as window borders, the name entry grid and the file menu.
* Every Vietnamese character in the text gets a **code** in `00-DE`. Two 256-byte tables in bank `$10` map each code to a pair:
  * `$8000`: the base tile, drawn in the text row.
  * `$8100`: the top tile, drawn in the mark row.
* There are more possible accented characters than free codes. `vn.init()` scans all texts that go into the ROM and gives codes to used characters first. Unused, rare capitals are dropped. If a used character cannot get a code, the build fails.
* `vn.encodeText`, `vn.encodeB` and `vn.rawTiles` turn strings into code bytes or tile rows. `encodeB` also accepts `<token>` for special art and `{hh}` for raw bytes.

**Tools used:** `tileart.js` (tiles as ASCII art), `sheet.js` and `png.js` (tile sheets as PNG).

### Step 4 — Patch the text engine (`build.js → patchTextEngine`)

* **New character output.** The Japanese dakuten routine at `$DC5F` is replaced by `NEWPUT`. It:
  1. switches to bank `$10`;
  2. looks up the base and top tiles of the code;
  3. writes the base tile to the text row and the top tile one row above;
  4. switches back.

  All call sites (`$DACC`, `$DADE`, `$DCCD`, `$DD1E`, `$DE6A`) now route codes below `$DF` to it. The player-name control code moved from `$D3` to `$DF`, which frees `$D3-$DE` as character codes.
* **Menu renderer** at `$ED38`. It does the same lookup for text in menus and windows. A blank top tile is not written, so window borders stay intact.
* **Absolute pointers in scripts.** `F2` (jump), `F3` (yes/no branch) and `F4` (flag test) originally used offsets relative to the bank. They now take absolute 16-bit addresses.
* **Script pointers across banks.** A new pointer-copy routine reads the bank offset from bits 7-6 of the pointer's high byte, so one pointer table can reach four consecutive banks.
* **Script bank bases.** Code that loads the script bank now uses the new banks:
  * group A at `$D87E`;
  * group E at `$D8D8`;
  * the gold-gain routine at `$D984`. It also resets the script bank. Missing this one made the Dorami save scene hang.
* **Yes/No choice** in dialogue is rewritten as `▶Có  Không` (`patchYesNo`).

### Step 5 — Translate and compile the script (`script/`, `tools/compile.js`)

* The decoded Japanese script was translated into Vietnamese, using the English version as a cross-check. The text is in `script/A_0x.txt` and `script/E_0x.txt`. The format looks like this:

  ```
  #L8172 A1          <- label + pointer table entries that point here
  {fa}{e9}           <- control codes ({e9} = target name, {fa} = clear window, ...)
  đã hồi sức!
  {p}{end}           <- {p} = wait for button / next page, {end} = end of message
  ```

  * A new line in a block becomes a text line. `{yesno L1 L2}`, `{jmp L}` and `{flag hh L1 L2}` refer to labels.
  * Any other `{hh ...}` is emitted as raw bytes. The Japanese macro codes are kept, for example `{d3}` for the hero name and `{ec}` for a number.
* `tools/check.js` checks that no line is wider than 15 characters, counting each name or number macro at its maximum width. `tools/reflow.js` re-wraps pages that are too wide.
* `compile.js` does the following:
  1. encodes the text with `vn.js`;
  2. packs the blocks into the 4 banks of each group;
  3. resolves labels into absolute addresses;
  4. rebuilds the pointer tables. For group E, the original bank-3 count header is kept.

### Step 6 — Menus, status and battle UI (`tools/menus.js`)

Bank B contains small layout scripts with opcodes that insert words (`E0`), labels (`E2`) and window titles (`E4`). Each is referenced through a table of pointers to fixed-length slots. `menus.js` does the following:

* Rewrites every slot in place, padded to its original length:
  * commands: *Nói, Tìm, Doraemon, Đồ, Tr.bị, Hội ý, Túi, Dorami, Dùng, Đưa, Vứt, Đánh, Chạy, Phép, Thủ …*
  * status labels: *TT, Cấp, HP, Công, Thủ, Exp*
  * status values: *Tốt, Đau, Nguy, Độc, Tê, Ngủ, Ngất*
  * warp destinations and window titles.
* Replaces the letters that the English patch had inserted before opcodes with spaces.
* Keeps the "Doraemon" logo tiles from the English font as special art. Short names such as *Nobita*, *Shizuka* and *Miyoko* are packed proportionally into fewer tiles.
* Repacks the party names, so the unused speed label slot can hold *Tera*.

Window titles are drawn on the border, so they use the single-tile accented letters.

### Step 7 — Item and enemy names (`tools/names.js`)

* The item table (`$8EB9`, 128 pointers) and the enemy tables in bank B are rebuilt.
* The Vietnamese names are longer than the English ones, so the strings are spread over several free regions:
  * three regions in bank B;
  * the old kana table in fixed bank F (`$ED70-$EDCB`), which is unused after the `$ED38` rewrite. Pointers `≥ $C000` read the fixed bank.
* Some names were shortened to fit, for example *Mũ cướp*, *Dao ngọc*, *Chuột núi* and *Dơi cốt*.
* The item icons (`{90}` weapon, `{91}` armor, `{92}` accessory) and the equipped mark are kept.

### Step 8 — Name entry screen (`tools/nameentry.js`)

* Bank C stores this screen as raw 32-byte nametable rows, with no mark rows, so only single-tile glyphs are used.
* The prompts become *Tên bạn?*, *Trai hay gái?*, *Có / Không* and *Được chưa?*. The words keep their original start columns, because the cursor positions are hard-coded.
* The character grid is Latin letters plus `Đ Ơ Ư đ ơ ư`, with *Xong* ("done"). The second grid page, which held kana, is replaced by a copy of the first page.

### Step 9 — Title screen and file select (`tools/filescreen.js`)

* **Title** (bank 9, a 20-column text area at `$A14F`):
  * *Cuộc phản công của / Giga Zombie*;
  * *— Nhấn Start —*;
  * the marks go into the empty row above each line.
* **File menu** (bank C `$A272`, rows of 11 bytes): *Tiếp tục, Chơi mới, Xóa, Chép*. Row 1 is shown above either row 2 or row 3 depending on whether saves exist, so it cannot hold marks. Single-tile glyphs are used instead.
* **Save box** (bank C `$A56C`…):
  * *Lưu 1-3*;
  * *Cấp*;
  * *Tốc độ*, with its marks in the blank row above;
  * *Có / Không*.
* **Prompts:**
  * *Chọn lệnh! · Bản nào? · Tốc độ chữ? · Hãy xóa bớt! · Xóa bản nào? · Xóa thật à? · Chép từ đâu? · Dán vào đâu? · Bản số N bị / hỏng rồi!!*
  * Each prompt needs a mark line and a text line, which is more lines than the original 17-entry table holds. The line pointer table was moved to free space at `$BF6D`, and the operands at `$A7D0`/`$A7D5` were patched. Identical lines are shared.
  * The corrupted-save message is built in RAM at `$02C0` from a template, and the game writes the slot digit into it.

### Step 10 — Testing with a scripted emulator

`tools/emu.cs` is a small libretro host around FCEUmm. It runs command scripts without showing a window, so every screen could be checked from PNG screenshots. To compile it:

```powershell
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /platform:x64 /out:emu.exe tools\emu.cs
```

Script commands:

* `load`/`save` savestates;
* `press BTN frames wait`, `tap BTN count interval` and `run n`;
* `shot file.png scale`;
* `ram`, `sram` and `vram` dumps;
* `poke`/`peek` (2 KB RAM) and `spoke` (battery RAM);
* `reset` and `quit`.

Example:

```powershell
"run 400`nshot work/title.png 2`npress START 5 60`nrun 120`nshot work/files.png 2`nquit" | Set-Content work/s.txt
./emu.exe work/t.nes work/s.txt
```

Savestates keep their own copy of CHR-RAM. After a font change, refresh them before testing, otherwise the text shows old tiles:

```powershell
node tools/statefont.js work/t.nes work/g8.st work/g8v.st   # g8.st = name entry screen
./emu.exe work/t.nes work/t3.txt    # enter a name, play the intro      -> work/t_d.st
./emu.exe work/t.nes work/t4.txt    # finish the intro, stand in the house -> work/t_play.st
```

`tools/state.js` parses FCEUmm savestates, and `tools/ntdump.js` prints a state's nametable as hex. These were used to find the layout of raw screens.

**Checked in the emulator:**

* dialogue pages and yes/no choices;
* command menus and submenus, items (icons and equipped mark), the status screen and warp list;
* battles: menu, enemy names in the list and in messages, damage and status texts;
* name entry;
* Dorami's save scene;
* title screen, file select with a real save, and the Continue, Delete, Copy and message-speed prompts.

### Step 11 — Release

```powershell
Copy-Item work/t.nes "Doraemon - Giga Zombie no Gyakushuu (VN).nes"
node tools/ips.js make work/jp.nes work/t.nes "Doraemon - Giga Zombie no Gyakushuu (VN).ips"
node tools/ips.js apply work/jp.nes "Doraemon - Giga Zombie no Gyakushuu (VN).ips" work/check.nes   # must be identical
```

The IPS file includes the ROM expansion, so it must be applied to the **original Japanese ROM**, not to the English one.

---

## Tool reference

| Tool | Use |
|---|---|
| `build.js` | full build: `node tools/build.js out.nes [--src dir]` |
| `vn.js` | Vietnamese glyphs, tile allocation, code tables, encoders |
| `compile.js` / `check.js` / `reflow.js` | script compiler, line-width checker, re-wrapper |
| `menus.js`, `names.js`, `nameentry.js`, `filescreen.js` | per-screen text patchers |
| `asm6502.js` | tiny assembler used for the code patches in `build.js` |
| `script.js`, `tables.js`, `bankb.js` | text extraction / decoding (JP & EN) |
| `disasm.js`, `hexdump.js`, `find.js`, `freespace.js`, `ipsmap.js` | ROM analysis |
| `tileart.js`, `sheet.js`, `png.js` | font inspection |
| `state.js`, `statefont.js`, `ntdump.js`, `emu.cs` | savestates and automated testing |
| `ips.js` | `list`, `apply`, `make` IPS patches |
