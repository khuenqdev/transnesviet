# NES ROM Hacking for Absolute Beginners
### Learning by translating *Saiyuuki World* into Vietnamese

> **Who this is for:** you have never opened a hex editor, or you only know the basics. You do **not** need to know assembly or electronics. You need Python 3 and curiosity.
> **What you will be able to do at the end:** read a NES ROM header, find the graphics and the text, understand why Vietnamese is harder than English to insert, write a patch (IPS), and follow the real project described in `01_TECHNICAL_WALKTHROUGH.md`.
> **Legal note:** only hack ROMs of games you own. Distribute **patches** (IPS), never the ROM itself. Everything here ships as a patch.

---

## Table of contents
1. [What is a ROM, really?](#1-what-is-a-rom-really)
2. [Numbers: binary, hex, and why programmers love $](#2-numbers)
3. [Your toolbox](#3-your-toolbox)
4. [Lab 1 – The 16-byte header](#4-lab-1--the-header)
5. [How the NES shows pictures: tiles](#5-tiles)
6. [Lab 2 – Seeing the graphics](#6-lab-2--seeing-the-graphics)
7. [Text: the "table file" idea](#7-text-and-tables)
8. [Lab 3 – Finding and dumping the dialog](#8-lab-3--dumping-the-dialog)
9. [Why Vietnamese is hard on a NES](#9-why-vietnamese-is-hard)
10. [The big idea: draw the letters yourself](#10-the-big-idea)
11. [Banks and mappers: when 32 KB is not enough](#11-banks-and-mappers)
12. [A 10-minute crash course in 6502 assembly](#12-6502-crash-course)
13. [Lab 5 – Assemble and disassemble](#13-lab-5)
14. [Patching: IPS files (Lab 4)](#14-lab-4--ips)
15. [Mini project: translate one line yourself](#15-mini-project)
16. [Debugging and testing](#16-debugging)
17. [Where to go next / roadmap through the real project](#17-roadmap)
18. [Glossary](#18-glossary)
19. [Cheat sheet](#19-cheat-sheet)

All commands assume the project folder `saiyuuki/` and that the original ROM is saved as `rom/original.nes` (md5 `01e8594637accca56e7d1a2e63906db5`). Check yours with `md5sum rom/original.nes`.

---

## 1. What is a ROM, really?

A ROM file (`.nes`) is a **dump of a cartridge**: a long list of bytes. A byte is a number from 0 to 255. Nothing else. Every picture, sound, and sentence in the game is some of those bytes, and the game's *program* is also bytes (instructions for the CPU).

```
 file on disk:  4E 45 53 1A 08 00 21 08 ... (thousands more) ...
                └ "NES" + 1A: "I am a NES ROM"
```

The console has:

| Part | Job | Analogy |
|------|-----|---------|
| **CPU** (6502) | Runs the program, 1.79 million tiny steps per second | The brain |
| **PPU** | Draws the screen from tiles | The painter |
| **RAM** (2 KB) | Scratch memory for the game | Whiteboard |
| **Cartridge ROM** | Program + data, read-only | The book |

![The game, original vs Vietnamese](img/fig02_dialog.png)

*Figure 1 – A dialog box: original (left) vs. our translation (right).*

Hacking a ROM = changing some bytes so the game does something different, **without the source code**. For a translation we must change *text*, sometimes *graphics*, and sometimes *code*.

## 2. Numbers

Computers count in binary, humans prefer hexadecimal ("hex"), which is just a compact way to write bytes.

| Decimal | Binary | Hex |
|--------:|-------:|----:|
| 0 | 00000000 | $00 |
| 10 | 00001010 | $0A |
| 16 | 00010000 | $10 |
| 255 | 11111111 | $FF |

* One hex digit = 4 bits (0–F). A byte = 2 hex digits.
* We write hex with a `$` (assembly style) or `0x` (Python style): `$C000 = 0xC000 = 49152`.
* **Address** = a byte's position. The NES CPU sees 64 KB of addresses `$0000–$FFFF`.
* **Little-endian:** a 16-bit number is stored low byte first. Address `$9E77` appears in the file as `77 9E`. This trips up every beginner exactly once.

Try it:
```python
>>> hex(49152), 0x9E77 & 0xFF, 0x9E77 >> 8
('0xc000', 119, 158)
```

## 3. Your toolbox

| Tool | Why | How to get it |
|------|-----|---------------|
| **Python 3.9+** | Our scripts | `python3 --version` |
| **Pillow** | Draw PNGs | `pip install pillow` |
| **Node.js + jsnes** | Headless emulator we script | `git clone https://github.com/bfirsh/jsnes` then `npm i` |
| **A hex editor** (HxD, ImHex, `xxd`) | Look at bytes | any |
| **An emulator with a debugger** (Mesen is excellent; FCEUX too) | Watch the game run, view tiles, set breakpoints | download |
| **Our tools** in `tools/` | `asm6502.py` assembler, `dis6502.py` disassembler, `make_ips.py`, `build_rom.py` | already in the project |

You can follow all labs with only Python + Pillow (+ Node for Lab 2's VRAM dump). A real debugger (Mesen) makes everything ten times nicer; open *Debug → Event/PPU viewer/Tile viewer/Trace logger*.

## 4. Lab 1 – The header

The first 16 bytes of every `.nes` file are the **iNES header**:

```
offset  0-3   "NES" 1A           magic
        4     PRG-ROM size, in 16 KB units
        5     CHR-ROM size, in 8 KB units (0 = the game has CHR-RAM!)
        6     flags: low nibble bits: mirroring, battery, trainer; high nibble = mapper low 4 bits
        7     flags: high nibble = mapper high 4 bits; bits 2-3 = 0b10 means "NES 2.0 format"
        8-15  extras (NES 2.0: sizes, submapper)
```

Run:
```bash
python3 docs/examples/lab1_header.py rom/original.nes
```
Expected for *Saiyuuki World*:
```
PRG-ROM : 8 x 16 KB = 128 KB
CHR-ROM : 0 x 8 KB   (0 => the game uses CHR-RAM: graphics live inside PRG)
mapper  : 2 (UNROM ...)
```
What it tells us:
* **No CHR-ROM** → pictures are *not* in a separate chip; the game copies them into video RAM at startup. That is great news: we can copy **different** pictures (our Vietnamese letters) there at any time.
* **Mapper 2 (UNROM)** → the cartridge swaps 16 KB banks. See §11.

![ROM layout](img/fig05_rom_layout.png)

*Figure 2 – Where things live in the 128 KB original and in our 256 KB result.*

## 5. Tiles

The NES screen is 256×240 pixels but it never stores pixels directly. It stores **8×8-pixel tiles** and a **map** saying which tile goes in each cell (32×30 cells = the *nametable*).

Each tile = 16 bytes. Each pixel gets 2 bits = 4 colors. The 16 bytes are two 8-byte "bit planes": plane 0 holds the low bit of each pixel, plane 1 the high bit.

![Tile format](img/fig10_tile_2bpp.png)

*Figure 3 – Decoding a tile: byte N of plane 0 and byte N+8 of plane 1 combine into row N.*

Worked example. Row bytes `0x3C` (plane 0) and `0x00` (plane 1):
```
0x3C = 0011 1100  → pixels:  . . # # # # . .   (color 1 where bit=1)
```
If plane 1 were `0x3C` too, those pixels would be color 3.

**Consequence for translation:** a letter on the NES is just *one tile*. Japanese kana fit nicely: one kana = one 8×8 tile = one text byte. English needs ~60 tiles. Vietnamese, with its accents, needs far more than the game has room for → §9.

## 6. Lab 2 – Seeing the graphics

Because the game uses CHR-RAM, the graphics are not at a fixed place in the file (they are compressed or stored in PRG and uploaded). The easiest way to *see* them is to run the game and **dump video memory**.

```bash
node docs/examples/lab2_vram_dump.mjs rom/original.nes out.vram 600   # run 600 frames, save 8 KB of pattern memory
python3 docs/examples/lab2_tiles.py out.vram tiles.png 3
```

![VRAM dump of the original game](img/lab2_tiles.png)

*Figure 4 – The two 256-tile pattern tables. The right half contains the font: tiles `$B0–$FF` are hiragana.*

Open the picture and count: that block of kana is the entire alphabet of the original game. Tile `$B0` is the first kana; tile number = the **byte used in the text**. That is the key to everything in the next section.

![The same dump in the finished translation](img/fig20_chr_dump.png)

*Figure 5 – After translation, the same pattern memory holds Vietnamese letter fragments.*

## 7. Text and tables

If text is stored as bytes, which byte means which letter? Usually the game's author picked the order of tiles in the font, so byte = tile number. A **table file** records it:

```
B0=あ
B1=い
...
```
You find the table by (a) looking at the tile picture (Lab 2) and (b) checking against known sentences. A common trick: dump the VRAM while a known sentence is on screen, or search for **relative searching** — if "ABC" is stored as 41 42 43 then the *differences* between consecutive bytes are 1,1 whatever the real table. With kana in alphabetical order (あいうえお…) the same trick works.

In *Saiyuuki World*:
* One byte = one kana tile (`$B0–$FF`).
* Voiced marks (゛ ゜) are separate tiles `$FE/$FF` printed after the base letter.
* `$B3` = ▼ ("press a button") and also acts as the terminator in records that wait.

## 8. Lab 3 – Dumping the dialog

Now find the sentences. In this game they are in bank 3, behind a **pointer table**:

```
$9E77:  [lo hi] [lo hi] [lo hi] ...      213 little-endian addresses
           │
           └─►  record: [flags][length]([address])[tile bytes...]
```

![Record layout](img/fig07_row_record.png)

*Figure 6 – One text "row" (record).*

```bash
python3 docs/examples/lab3_text.py rom/original.nes 20
```
prints the first 20 rows decoded to kana. Compare with a screenshot of the game: the first intro line should match.

How was the pointer table found? (so you can repeat it on other games)
1. Pick a distinctive sentence on screen; convert it with your table → search the ROM for the bytes. Found at `$A021`.
2. Search the ROM for the **address** of that location in little-endian (`21 A0`). A run of such addresses = the pointer table.
3. Confirm: the table entries ascend and each one points to a plausible record.

## 9. Why Vietnamese is hard

Compare the problem sizes:

| | Japanese kana | English | **Vietnamese** |
|--|--:|--:|--:|
| Distinct glyphs needed | ~80 | ~60 | **~134** (a, ă, â, à, á, ả, ã, ạ, ằ, ắ, ẳ ...) |
| Typical width | 8 px, fixed | 8 px | proportional is needed to fit |
| Text per line | 17 kana | 17 chars | **same box, more letters** per sentence |

Three problems:
1. **Tone marks and vowel marks stack** (ệ = e + ^ + dot below). An 8×8 tile has no room above and below.
2. **Not enough tiles.** The pattern table holds 256 tiles and the game uses most for pictures.
3. **Vietnamese sentences are longer** than the Japanese ones. The box is 2 lines × 17 characters.

"Just replace kana with Latin letters" would give you text without tone marks. The user demanded full tones, so we needed a different approach.

![Vietnamese font cell](img/fig11_font_cell.png)

*Figure 7 – Our solution: a 12-pixel-tall glyph cell. Upper area for diacritics, x-height middle, lower area for dot-below and descenders.*

## 10. The big idea

> **Stop thinking of the text as bytes → tiles. Pre-render each sentence into pixels, then cut those pixels into tiles that are uploaded on demand.**

Steps (details: Walkthrough §§4–8):

1. For every translated sentence, render it with a **proportional bitmap font** (letters 3–7 px wide) so it fits 2 lines × 17 tile-columns = 136 px.
2. A line is 12 pixels tall; the screen's tile is 8 pixels tall, so each text column uses **two tiles** (top 8 rows, bottom 4 rows + the box border).
3. Cut the bitmap into 8×8 chunks, remove duplicates (many are empty), and give each chunk a tile number from a **pool of 68 free tiles**.
4. When the game wants to show the sentence, a patch of ours (running on the CPU) **uploads those chunks into VRAM** and writes the right tile numbers to the nametable.

![Pipeline](img/fig18_build_pipeline.png)

*Figure 8 – The build pipeline: translation script → bitmaps → tile chunks → patched ROM.*

![Dialog typing](img/fig22_typing_sequence.png)

*Figure 9 – Frames of the finished game typing out a Vietnamese line.*

Because the game's own routine only draws kana tiles, we **hook** it: the original code calls our code at four points (init, step, blink, clear) and we draw instead.

![Hook flow](img/fig13_hook_flow.png)

*Figure 10 – Where our code takes over from the original.*

## 11. Banks and mappers

The CPU only sees 64 KB, and half of that is RAM/hardware. The cartridge gives:
```
$8000-$BFFF  16 KB window  ← switchable bank (UNROM: choose any of N banks)
$C000-$FFFF  16 KB fixed   ← always the LAST bank
```
Switching = write the bank number to a ROM address. A quirk of UNROM ("bus conflict"): the ROM chip also drives the data bus, so you must write to an address that **already contains the same number**. Game authors store a table `00 01 02 03 ...` for that; we made a bigger one.

![CPU memory map](img/fig06_cpu_map.png)

*Figure 11 – CPU memory map.*

Why this matters for us: the original had 8 banks (128 KB), and the text-engine bank was full. Vietnamese text lives in **seven new banks** (we grew the ROM to 256 KB). The fixed bank had ~220 free bytes for our trampoline, so every new routine is placed in a swappable bank and a tiny stub in the fixed bank switches to it, runs it, and switches back.

## 12. 6502 crash course

You can read 6502 code after learning ~15 instructions. It has three registers: **A** (accumulator), **X**, **Y**; a stack; and flags (Z zero, C carry, N negative).

| Instruction | Meaning |
|---|---|
| `LDA #$05` | A = 5 (`#` = literal number) |
| `LDA $0300` | A = byte at address $0300 |
| `LDA $0300,X` | A = byte at $0300+X |
| `STA $0300` | store A to $0300 |
| `LDX/LDY`, `STX/STY` | same for X, Y |
| `INX DEX INY DEY` | +1 / −1 |
| `CLC` / `ADC #n` | clear carry; A = A + n + carry |
| `SEC` / `SBC #n` | A = A − n − (1−carry) |
| `CMP #n` `CPX` `CPY` | compare (sets flags, no change) |
| `BEQ / BNE label` | branch if equal (Z=1) / not equal (Z=0) |
| `BCC / BCS label` | branch if carry clear / set |
| `JMP addr` | go to |
| `JSR addr` / `RTS` | call subroutine / return |
| `PHA / PLA` | push/pull A on stack |
| `LSR A`, `ASL A` | shift right / left (÷2, ×2) |
| `AND #n`, `ORA #n` | bit mask / bit set |

Reading example:
```
        LDX #$10        ; X = 16
loop:   STA $0300,X     ; write A at $0300+X
        INX             ; X = X + 1
        CPX #$20        ; X == 32 ?
        BNE loop        ; no → repeat
        RTS
```
It fills 16 bytes. **Every loop in game code looks like this.**

How do you find the *text* routine in a program of 100 KB? **Work backwards from a result you can see.** The pointer table address `$9E77` (Lab 3) appears in code exactly once, in the routine that loads a row. Find the code that reads it: start at the reference, follow the logic. We used an emulator trace + the ability to ask "which instruction wrote to PPU `$2007`?". See Walkthrough §5.

![Engine states](img/fig16_engine_states.png)

*Figure 12 – The dialog engine as a state machine (what we found).*

## 13. Lab 5

```bash
python3 docs/examples/lab5_asm.py
```
It assembles the loop above with `tools/asm6502.py`, prints the bytes, and disassembles them back with `tools/dis6502.py`. Change `$0300` to `$0400`, rerun: only the operand bytes change. That is all a patch is.

## 14. Lab 4 – IPS

IPS is the simplest patch format:
```
"PATCH"  { offset(3 bytes) size(2 bytes) data }*  "EOF"
```
```bash
python3 docs/examples/lab4_ips.py
```
creates a fake ROM, patches it, and verifies. Real use: `python3 tools/make_ips.py rom/original.nes build/saiyuuki_vi.nes build/saiyuuki_vi.ips`. IPS records may extend the file, so our 256 KB result is still one small patch.

Apply with any patcher (Floating IPS, `flips`) onto an **unmodified** ROM (check md5!).

## 15. Mini project

Goal: change the first dialog to say something else, using only a hex editor and Lab 3's table.

1. Run Lab 3 and note the address (file offset) of row 0's text. File offset = 16 (header) + bank×$4000 + (address − $8000).
2. Pick a record with `flags` `$80` (waits for a button). Keep the **length byte** the same, or *shorter* text with `$B3`.
3. Overwrite the kana bytes with others from the table. For example turn "ありがとう" into another kana word of the same length.
4. Save as a **new file**, open in the emulator. The line changes.
5. Bonus: change only the length byte (+1) and see the text engine print one more tile — a garbage tile — proving the length byte matters.

*Why can't we simply type "Xin chào"?* Because there are no Latin tiles in the pattern table and no tile for "à". That is the whole reason this project needs §10.

Mini-project 2 (pixel art): in the VRAM dump, find the kana あ. Convert the 16 bytes by hand into pixels (Figure 3). Draw a "Đ" in a free tile and write its 16 bytes — you have created your first font glyph.

## 16. Debugging

| Symptom | Likely cause | Fix |
|---|---|---|
| Game freezes on boot after you edit code | Wrong bank-switch / forgot bus-conflict table | restore ROM, change one thing at a time |
| Garbled tiles in dialog | Tile numbers outside pool, or upload not finished before display | Check pool map (Fig. 14 in the walkthrough) |
| Text clipped / misaligned | Sentence wider than 136 px | `build_rom.py` prints "row N too wide" → shorten |
| Crash only in emulator X | Bus-conflict ignored in some emulators | use the bus-conflict-safe bank switch |
| Palette wrong | Attribute table not updated | check nametable attribute bytes |

Habits that save days:
* **Always keep the original** and build from it by script (never hand-edit the only copy).
* Change **one thing**, test, commit a copy.
* Make a **savestate** right before the scene you test (our `state_test.mjs`).
* Print numbers in hex, always.
* Write down every address you learn. Your notes *are* the project.

## 17. Roadmap

Read in this order:
1. This tutorial (labs 1–5).
2. `01_TECHNICAL_WALKTHROUGH.md` — the full real project, with every address.
3. `docs/translation_table.md` — the Japanese → Vietnamese sentences with the Sino-Vietnamese choices.
4. `docs/APPENDIX_source.md` — the source code.
5. Try the method on another small UNROM game: dump the header, dump the pattern tables, find a sentence, find its pointer, and write down the engine.

Suggested exercises of rising difficulty: (a) change a price in the shop; (b) swap two items' names (same length); (c) make a one-byte patch to change the text speed (the 8-frames-per-column constant); (d) add a second text line style; (e) port the font to another game.

## 18. Glossary

| Term | Meaning |
|---|---|
| **ROM** | read-only memory; the cartridge's contents |
| **iNES header** | the 16 bytes at the start of `.nes` |
| **PRG** | program ROM (code and data) |
| **CHR** | character (graphics) memory; CHR-RAM can be written at run time |
| **Mapper** | cartridge hardware that switches banks |
| **Bank** | one switchable chunk of ROM |
| **Bus conflict** | writing to ROM while the ROM outputs data; value must match |
| **Nametable** | 32×30 map of tile numbers = what is on screen |
| **Pattern table** | the tile pixel data |
| **2bpp** | two bits per pixel |
| **PPU** | picture processing unit |
| **NMI** | interrupt at each frame (60/s), when drawing is safe |
| **Pointer** | address stored as data |
| **Little-endian** | low byte first |
| **Hook** | replacing a call so your code runs instead |
| **Trampoline** | small routine that switches bank, runs code, switches back |
| **IPS** | simple patch format |
| **Savestate** | frozen snapshot of the emulator |
| **Dakuten** | the ゛ voiced mark |
| **Sino-Vietnamese (Hán-Việt)** | Vietnamese words derived from Chinese readings, e.g. *Tây Du Ký* |

## 19. Cheat sheet

* Header: `NES 1A, PRG×16K, CHR×8K, flags6, flags7`. Mapper = `(f7 & F0) | (f6 >> 4)`.
* File offset of bank *b* address *a* (window): `16 + b*0x4000 + (a-0x8000)`. Fixed last bank: same with `b = last`.
* Tile bytes: `plane0[0..7], plane1[0..7]`; pixel `= bit(p0)|bit(p1)<<1`.
* PPU registers: `$2006` (address ×2), `$2007` (data), `$2000/2001` control.
* To find text: relative search → pointer table → engine.
* Keep a build script. Always.

You are ready for the real thing: open `01_TECHNICAL_WALKTHROUGH.md`.
