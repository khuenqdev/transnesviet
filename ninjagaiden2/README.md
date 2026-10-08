# Ninja Gaiden II — Vietnamese Translation (fixed revision 3)

Built from the supplied USA ROM; the Spanish project is used only as a structural reference.

## What was wrong, and what changed

**1. Garbled cutscene dialog (text ROM).** Two independent faults:
- The dialog engine only prints byte values `$00-$7F` as glyphs; every byte `>= $80` is a control code
  (newline `$A0`, page `$A1`, end `$A6`, ...). The previous build stored accented letters at `$80-$BF`, so
  the engine executed them as commands.
- Glyphs were also written to the wrong CHR tile for codes `>= $80` (the dialog banks are mapped `[1,2,0,3]`),
  which overwrote tile `$FF`, the *blank fill tile* of the dialog screen. That produced the page of repeated
  garbage glyphs behind the text.

Now every glyph lives in a printable cell `$00-$7F` and is drawn at CHR tile `$40 + code`. The cells were chosen
by emulation: codes whose glyph is still needed by the English credits (letters used in credits, `$60-$62` which
draw the "II" of "NINJA-II", `$63/$64`, ...) are protected, and the remaining cells were verified with a
frame-by-frame visual diff (see *Verification*).

Only 63 free cells exist, so nine rare characters have no glyph and print as their base letter:
`Í Ý Ơ Ư ỹ ẹ ễ ụ õ` -> `I Y O U y e e u o` (11 words affected; all other tone-marked letters are kept).

**2. SELECT playlist ROM: flashing title / black screen.** The previous hooks overwrote *part* of an instruction:
- title: `LDA $13 / AND #$10 / BNE` became `JSR $FFD1` followed by a stray `10 D0` (= `BPL`) -> title flashed and stuck;
- cutscene return: `LDA #4 / JSR $C000` became `JSR $FFE3` followed by `00 C0` (= `BRK`) -> black screen
  when START skipped the opening cutscene.
It also wrote code over `$FFD1-$FFE0`, which holds game data, and kept its flag in `$EF`, which the game
zeroes at every cutscene start (`$D8-$EF` clear loop at `$D0BC`).

New design (no original instruction is split, no game data touched, no RAM flag):
- `$D73B` `AND #$10` -> `AND #$30`: START *or* SELECT leaves the title loop (1 byte).
- `$D751` `LDA #0 / STA $48` -> `JSR $FFE3 / NOP`. The 21-byte hook in the fixed bank's free area
  (`$FFE3-$FFF7`): START does the original two instructions and returns; SELECT drops its return address,
  maps PRG bank 5 at `$A000` and jumps to the driver.
- Driver at `$BBAE` (free space of PRG bank 5, 62 bytes) plays seeds `01..0E` in order, keeping the seed on the
  stack, using the same prelude as the normal title exit; then it starts seed `0F` through the normal path
  (`JMP $C820`). START still skips a cutscene as in the original game. Seed `0F` is the ending/credits
  sequence, so the playlist ends on "THE END" exactly like the real game.

## Verification (emulator, FCEUmm core with debug hooks)
- Intro, 15 cutscenes, endings (`$10/$11`) and gameplay were run frame-for-frame against the English ROM with
  all translated text blanked: identical pixels except one overscan-edge frame in the ending-credit transition
  (cells `$50 $54 $56 $58 $59 $5A $70` are used last for that reason).
- Every code `$00-$7F` was confirmed to print verbatim in the dialog engine.
- START at title -> cutscene 1 -> game; START in the opening cutscene -> title; SELECT -> seeds 1..15.
- `python3 tests/validate_fixed_project.py` (static) and `python3 tests/test_playlist_flow.py` (emulator).

## Files
- `release/Ninja_Gaiden_II_Vietnamese_Text_FIXED.nes` / `.ips` — text/font only
- `release/Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.nes` / `.ips` — text/font + SELECT playlist
  (`Cumulative` = same patch, `Playlist_ONLY` = text ROM -> playlist ROM)
- `release/*.tbl`, `*.ext`, `translation_vietnamese_FIXED.txt`, `vietnamese_glyphs_8x8_fixed.chr`, `build_manifest_fixed.json`
- `source/build_vietnamese_fixed.py` — reproducible builder (`python3 source/build_vietnamese_fixed.py`)
- `tests/` — validation scripts; `base/` — clean USA ROM; `reference/` — Spanish project

## Build IDs
Base SHA-1 `269478947a5bc518551ab5d7b4687653006e243c`  CRC32 `0C39B026`
Text ROM SHA-1 `52d614525dfe5295cbe8b4f6ac9a61a005eb79c9`  CRC32 `2A41DC8F`
Playlist ROM SHA-1 `fda25d5c0220b951bb871fa023348c3bd1868497`  CRC32 `C9D7E093`
ROM size 262160 bytes, 152 story blocks, 63 custom glyphs.

Use `release/` from this revision only; older playlist ROMs are superseded.
