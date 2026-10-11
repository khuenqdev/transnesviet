# MOTHER (NES) → Vietnamese — Stage 1: Text Extraction Report

**ROM:** `mother.nes` — CRC32 `ABBE02FA`, SHA-1 `f338af0af0058dc692d6003e04b4094bb324d2c5`, 524,304 bytes  
**Build:** English prototype, internal header `EARTH BOUND 1.00` (PRG bank $1F, `$FFE0`)  
**Hardware:** NES 2.0 header, mapper 4 (MMC3), PRG 256 KB @ file `$10`, CHR 256 KB @ file `$40010`

## 1. Results at a glance

| Item | Count |
|---|---|
| Message IDs in the script pointer table | 2,000 (IDs 0–1999) |
| Unique script segments | 1,372 (1,300 with text, 71 empty, 1 placeholder) |
| IDs unused (point at offset 0 = "System Error!!!") | 625 |
| Mid-string entry points (segments that fall through) | 22 (battle + final-boss speech) |
| PRG-ROM strings (names, menus, intro, naming) | 321 |
| Round-trip check (decode → encode = original bytes) | **100% pass** (all 1,372 + 321) |
| Free space inside CHR text area | 7,109 bytes (largest: 4,010 @ CHR `$2F056`; 2,509 @ `$33653`) |

## 2. Key finding: the dialogue lives in CHR-ROM, not PRG

The original text scan (`mother.nes.text.txt`) only searched PRG, which is why it reported "no pointer tables". The script is stored in **CHR-ROM `$20000–$3401F`** (file `$60010–$7402F`) and read through the PPU:

1. Text ID → `$73:$74` (bank `$1E`, routine `$CAA9`).
2. ID × 3 indexes the **pointer table in PRG bank `$18`, CPU `$8000`** (file `$30010`, 2,000 × 3 bytes, ends at `$31780`).
3. Each 3-byte little-endian value is a 17-bit offset: **CHR offset = `$20000` + value**.
4. Bank math: 1 KB CHR bank = `$80 | (value >> 10)` written to MMC3 R4/R5; PPU address = `$0800 | (value & $3FF)`.
5. NMI command `$0A` (`$F99F`, bank `$1F`) reads 64 bytes per frame via `$2007` into `$0110`; `$CB1A` advances the pointer.

The pointer table covers **100%** of the CHR text area — no orphan text. Text is packed per 8 KB CHR bank, with `$FF` padding at each bank end.

## 3. Encoding

### 3.1 Characters (verified against the font page at CHR `$1F800`, tiles `$80–$FF`; see `mother_font_map.png`)

| Bytes | Glyphs |
|---|---|
| `A0–AF` | space `! ? ‥ $ • " ' ( ) : ; , - . /` |
| `B0–B9` | `0–9` |
| `BB–BF` | `α β γ π Ω` (PSI levels); `BA` = unidentified glyph, written `{BA}` |
| `C0` | `◆` speech bullet |
| `C1–DA` / `E1–FA` | `A–Z` / `a–z` |
| `DB DC DD DE DF E0` | window borders `┏ ▔ ┓ ⎸ ⎹` and cursor `➡` |
| `FB FC FD FE FF` | `┗ ▁ ┛ ▬ ▶` |
| `94 95 96` | `○ ◉ ♪` |
| `80–8F` | narrow "ligature" tiles (in, il, ll, 's, of, is, the…), **unused by any text** |
| `97–9F` | "SMAAAASH!!" graphic, used once |

The raw dump's `"` is really **`?`** (`A2`), and `&` is really **`"`** (`A6`). Without the table, the old ASCII view showed these wrong.

### 3.2 Control codes

These are classified by the ROM's own table at `$C22C`. Bytes below `$40` with a class value below `$0A` are controls.

| Byte | Args | Tag in dump | Meaning |
|---|---|---|---|
| `00` | 0 | (segment end) / `{end}` | End of message |
| `01` | 0 | newline | New line (dialogue lines are double-spaced) |
| `02` | 0 | `{clear}` | Message break/clear (battle text, after `{wait}`); inferred |
| `03` | 0 | `{wait}` | Wait for button, then continue |
| `04` | 2 | `{goto:XXXX}` | Continue reading at CPU address |
| `05` | 0 | `{05}` | No-op (handler `$C9D2`) |
| `20` | 2 | `{pos:XX,YY}` | Set print position (window layouts) |
| `21` | 2 | `{Ninten}`… / `{str:XXXX}` | Insert string from address |
| `22` | 2 | `{rep:CC,NN}` | Repeat tile CC, NN times |
| `23` | 4 | `{num:XXXX,NN,FF}` | Print NN-byte number at address |

**Name aliases for `21` (inferred from context):** `$7478` Ninten, `$74B8` Ana, `$74F8` Lloyd, `$7538` Teddy, `$7689` FavFood, `$0580` Actor, `$0588` Target, `$0590` BattleItem, `$670A` Leader, `$6D00` Patient, `$6D04` ShopItem, `$6D20` User, `$6D24` UsedItem, `$7420` Str7420.

## 4. Script segments and categories

A **segment** starts at each unique pointer. If another ID's pointer lands inside a string, the earlier segment stops there and is flagged `falls_through_to_next`. Re-insertion must keep fall-through pairs adjacent; all other segments are freely relocatable through the pointer table.

| Category (by ID range) | IDs | Segments | Bytes | Max line* |
|---|---|---|---|---|
| dialogue | 1–999 | 860 | 57,909 | 22 |
| item_description | 1000–1299 | 82 | 4,866 | 22 |
| enemy_check | 1300–1499 | 103 | 3,777 | 22 |
| battle_message | 1500–1649 | 146 | 3,964 | 22 |
| final_boss_speech | 1650–1699 | 22 | 1,005 | 21 |
| field_system | 1700–1779 | 41 | 1,595 | 21 |
| anti_piracy | 1780 | 1 | 305 | 28 |
| ending | 1781–1799 | 9 | 815 | 28 |
| staff_credits | 1800–1835 | 36 | 511 | 17 |

\*Visible characters per line, including the `◆` bullet or the leading indent space. Most dialogue lines are 18–20 characters; 22 is the observed maximum.

## 5. PRG-ROM strings

| Category | Count | Location / reference | Edit policy |
|---|---|---|---|
| item_name / place_name / psi_name | 95 / 9 / 46 | Bank `$00` strings; master table bank `$00` `$9800`, 256 × 8 bytes, name pointer at +0 | Relocatable (pointers known) |
| enemy_name | 104 | Bank `$00` strings; table bank `$16` `$8000`, 32-byte records, pointer at +`$18` (122 enemies) | Relocatable |
| status_name | 8 | Bank `$00` +`$05F8`, fixed 7-byte slots | **Exactly 6 chars** |
| character_name | 3 | Pippi / EVE / FlynMan, bank `$18` records, 8-byte field | ≤ 7 chars |
| battle_ui, field_menu | 16 / 17 | Window layouts in bank `$00` (`00` separates window rows) | In place |
| system_ui, file_select, naming, reserved_names, name_entry, intro | 4 / 4 / 7 / 1 / 5 / 2 | Banks `$13` and `$19`; no direct pointers found yet | In place (pointers to be traced with the emulator) |

## 6. Excluded from the dump (on purpose)

- **Title-screen credits** ("SHIGESATO ITOI", logo): graphic tiles plus a nametable at CHR `$132C8`, not script text.
- **Debug character-set screen** in bank `$14` (`$29EC7`).
- **Stale text fragment** at CHR `$1E000–$1F7FF`. It partly mirrors bank `$19` and is never read.
- **Internal header** `EARTH BOUND 1.00`.

## 7. Notes for the next stages

- **Font space.** `80–8F` (16 tiles) are unused and can be freed right away for Vietnamese glyphs. `97–9F` ("SMAAAASH") is a candidate too, after checking the battle graphic. Vietnamese needs roughly 67 accented lowercase letters plus capitals, so the glyph strategy (precomposed tiles vs. diacritic-overlay rows) is the main design decision.
- **Size.** The CHR text area has only 7,109 bytes free, and CHR is already at MMC3's 256 KB limit. If Vietnamese text grows, the plan should expand PRG to 512 KB and move or extend text there, or add DTE/compression to the reader at `$CAA9`/`$F99F`.
- **Line width.** Translate to ≤ 22 visible characters per dialogue line (28 for ending/anti-piracy), keep the `◆` / leading-space convention, and keep tags exactly as written.

## 8. Deliverables

| File | Purpose |
|---|---|
| `mother_text_extract.py` | Reproducible extractor plus `Codec.encode/decode` (round-trip safe) for the re-inserter. Run: `python mother_text_extract.py --hexdump mother_hexdump.txt --out out` (or `--rom mother.nes`) |
| `mother_script.json` | Master data: meta, control codes, charset, free space, 1,372 segments (IDs, offsets, raw hex, text), 321 PRG strings (offsets, pointer refs, limits) |
| `mother_translation_sheet.csv` | Translation worksheet (UTF-8 BOM, Excel-ready): fill the `vietnamese` column |
| `mother_script_en.txt` | Human-readable full script |
| `mother.tbl` | Table file for hex editors / other tools |
| `mother_font_map.png` | Labelled font tiles `$80–$FF` |
