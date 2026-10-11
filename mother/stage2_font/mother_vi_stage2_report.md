# MOTHER (NES) → Vietnamese — Stage 2: Font and Text Encoding

**Input ROM:** `mother.nes` (CRC32 `ABBE02FA`). **Patched ROM:** CRC32 `547D1633` = input + 32 new glyph tiles. To produce it, apply `mother_vi_font.ips`, or run `python mother_vi_font.py --rom mother.nes --out out`, which also writes `mother_vi_font_test.nes`. The ROM itself is not in the package.

## 1. Result

- Every Vietnamese letter (146 = 12 vowels × 6 tones × 2 cases + đ/Đ) can now be encoded and drawn with the game's own font.
- 32 font tiles that no text uses were redrawn as Vietnamese glyphs. All other tiles are untouched.
- Diacritics use a **mark row**: tone, breve and circumflex marks are drawn in the blank tile row above each text line.
- The encoder round-trips all 146 letters and re-encodes all 1,693 stage-1 strings to their original bytes.
- The patched ROM was played in the emulator from power-on to an in-game dialogue. Every checkpoint screen is pixel-identical to the original ROM (`regression.txt`).

## 2. Why a mark row (and not one tile per accented letter)

Verified in the emulator (MMC3 with CHR A12 inversion, `$8000` bit 7 = 1):

| Screen | R2/R3 (BG tiles `$00–$7F`) | R4/R5 (BG tiles `$80–$FF`) |
|---|---|---|
| Title / file select / naming | `$7C/$7D` (blank + grey alphabet) | `$7E/$7F` = font |
| Field, menus, dialogue | `$19/$1A` = **map tiles** | `$7E/$7F` = font |

- **Only 128 font tiles exist** in the field (`$80–$FF`), and about 96 are needed for Latin letters, digits, punctuation and window borders. Precomposed Vietnamese would need about 134 extra tiles, which is impossible.
- **The game's windows are double-spaced.** In the dialogue window the text rows are 20/22/24/26, and rows 19/21/23/25 are blank (row 19 is directly under the window border). The command menu, Cash window and Name window follow the same pattern. Those blank rows hold the marks.

The supplied `glyphs.py` sample uses 2-px strokes and a row-7 baseline. MOTHER's real font (CHR `$1F800`) uses **1-px strokes, colour index 2, capitals on rows 0–6, x-height rows 2–6, and column 7 blank**. The new glyphs follow the real font so they match the existing letters.

## 3. Tile allocation (font page CHR `$1F800`, tile = code)

| Code | Glyph | Was |
|---|---|---|
| `$80–$83` | mark: sắc ´, huyền `, hỏi ̉, ngã ˜ | unused ligatures |
| `$84–$85` | mark: breve ˘, circumflex ˆ | unused ligatures |
| `$86–$89` | mark: ˘+´ ˘+` ˘+̉ ˘+˜ (ắ ằ ẳ ẵ) | unused ligatures |
| `$8A–$8D` | mark: ˆ+´ ˆ+` ˆ+̉ ˆ+˜ (ấ ầ ẩ ẫ) | unused ligatures |
| `$8E $8F $90` | ơ ư đ | ligature, ligature, blank |
| `$91 $92 $93` | Ơ Ư Đ | blank |
| `$97` | ı (dotless i, used under a tone mark) | "SMAAAASH!!" logo |
| `$98–$9F` | ạ ẹ ị ọ ụ ỵ ợ ự | "SMAAAASH!!" logo |
| `$A3 $A5 $AB` | Ạ Ọ Ụ | `‥` `•` `;` (no text uses them) |

**Kept:** `$94–$96` (○ ◉ ♪), Greek α–Ω (PSI levels), `$BA` (the small "00" after cash amounts, seen on the field Cash window).

**Side effect:** message 1511 (the "SMAAAASH!!" logo, segment S1289) must be translated as normal text, for example `CHÍ MẠNG!!`.

## 4. Encoding rules

1. A Vietnamese letter becomes `[mark] glyph`. The **mark byte (`$80–$8D`) comes first** and takes no column.
2. Dot below (nặng) is built into the main glyph (`ạ ặ ậ` → `ạ` plus ˘ or ˆ as the mark).
3. Horn letters use their own glyphs (`ớ` = `$80 $8E`).
4. `i` with a tone mark uses the dotless `ı` (`í` = `$80 $97`). `ị` keeps its dot.
5. **Capital dot-below fallback:** there are no tiles for Ẹ Ị Ỵ Ợ Ự (including Ệ). The encoder writes the lowercase form and logs a warning. Ạ Ặ Ậ Ọ Ộ Ụ are fully supported.
6. Everything else is unchanged from stage 1: tags (`{wait}`, `{Ninten}`, `{num:…}`, `\n`), Latin letters, digits and punctuation. `‥ • ;` are no longer available.

Example: `◆{Ninten} ơi, đừng sợ!` → `C0 217874 A0 8E E9 AC A0 90 81 8F EE E7 A0 F3 9E A1`

## 5. Rules for translators (the CSV `vietnamese` column)

- **Line width:** at most 22 visible characters per dialogue line, or 28 for the ending and anti-piracy text. **Marks do not count:** "Cái đèn" counts as 7.
- **Avoid capital Ẹ Ị Ỵ Ợ Ự** at the start of a sentence; they render lowercase.
- **Keep every tag exactly as written.** Names inserted by `{Ninten}` and the like stay Latin, because they come from the name keyboard.

## 6. What stage 3 (renderer) must do

- **Character printer:** the loop around bank `$1E` `$C7D4` treats bytes ≥ `$40` as tiles. Add `CMP #$80 / BCC / CMP #$8E / BCS`. On a mark, store it and do not advance. When printing the next glyph, also write the stored tile to the PPU address minus 32 (the row above). `mother_vi_preview.layout()` is the reference behaviour.
- **Text without a blank row above** needs reflow or its own handling:
  - the opening story (bank `$19`, own renderer, single-spaced; confirmed in the emulator)
  - the ending, credits and anti-piracy text (not yet checked)
  - the name-entry keyboard
- **Window layouts in PRG** (`battle_ui`, `field_menu`) print through the same tile path. Check each one in the emulator once Vietnamese strings are inserted.

## 7. Files

| File | Purpose |
|---|---|
| `mother_vi_font.py` | Glyph pixel art, Unicode → glyph and mark mapping, CHR injection, IPS, table and sheet output |
| `mother_vi_codec.py` | `encode()` / `decode()` / `check_lines()` built on the stage-1 codec; run it to execute the self-tests |
| `mother_vi_preview.py` | Alphabet chart, plus a full emulator run of the original and patched ROMs with screen regression and an in-game Vietnamese preview |
| `mmc3.py` | MMC3 mapper add-on for the supplied `emu.py`/`nes.py` (PRG/CHR banking, PRG-RAM, scanline IRQ, sprite-0) |
| `mother_vi_font.ips` | IPS patch with the new glyphs (680 bytes; verified to produce CRC32 `547D1633`) |
| `mother_vi.tbl` | Updated table (marks shown as `<MARK_…>`) |
| `mother_vi_charmap.json` | Every Vietnamese letter → bytes, glyph list, replaced tiles |
| `mother_vi_font_sheet.png` | Font page `$80–$FF`; new tiles highlighted |
| `mother_vi_alphabet_preview.png` | All 146 letters laid out with the mark row |
| `mother_vi_ingame_preview.png` | Vietnamese message in the real dialogue window, using the patched CHR |
| `regress_*.png`, `regression.txt` | Checkpoint screens from the patched ROM; identical to the original |
