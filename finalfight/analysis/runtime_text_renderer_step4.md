# Step 4 — Static text-to-PPU and CHR mapping trace

## Result

This step resolves the main static font-lookup question more precisely than Step 3. The game does not appear to run a character-to-tile lookup routine at `JSR $F406`. Instead, its text renderers populate a VRAM command record, and a fixed-bank queue writer sends that record's character/data byte directly to the PPU. Separately, the NMI setup maps the final 4 KiB of CHR into the background pattern-table window.

**Status: statically confirmed from the supplied ROM bytes; not yet captured in an emulator debugger.** The original ROM is unchanged.

## 1. Text renderers queue the character byte

The opening/cutscene loop at PRG offset `0x01A00` (CPU `$9A00` when the relevant 8 KiB PRG bank is mapped at `$8000`) writes a VRAM command record around `$0780-$0784`. For each ordinary text character, the code computes a PPU address in `$0780/$0781`, sets `$0782` to zero for a one-byte payload, writes the current encoded text byte to `$0783`, and writes `$FF` at `$0784` as the end marker. The credits renderer at PRG `0x12700` uses the same queue fields. Boss dialogue has separate record/header handling and still needs an in-emulator context check before reusing candidate extended codes.

## 2. The actual queue writer

The fixed-bank routine at CPU `$C1FD-$C221` (PRG offset `0x1C1FD`) consumes the queued VRAM commands. Its relevant operations are:

| CPU address | Operation | Meaning |
|---|---|---|
| `$C201` | `LDA $0780,X` | Read command PPU-address high byte; a negative value ends the command list |
| `$C206` | `STA $2006` | Write PPU-address high byte |
| `$C209` | `LDA $0781,X` | Read PPU-address low byte |
| `$C20C` | `STA $2006` | Write PPU-address low byte |
| `$C20F` | `LDY $0782,X` | Read payload length/control |
| `$C212` | `LDA $0783,X` | Read the character/tile byte |
| `$C215` | `STA $2007` | Write that byte directly to PPU VRAM |

There is no glyph arithmetic between the load from `$0783,X` and the store to `$2007` in this routine. So for this writer the text byte is the PPU tile index, not a code that is converted through a second font table.

## 3. CHR bank mapping aligns with the candidate font

The NMI handler in the fixed bank (CPU `$C1BC-$C1CF`, PRG `0x1C1BC`) writes MMC3 CHR register 0 to `0x78` and register 1 to `0x7A`. MMC3 registers 0 and 1 each select an aligned 2 KiB CHR bank, so this maps 1 KiB banks `0x78-0x7B` into PPU pattern-table addresses `$0000-$0FFF`. CHR 1 KiB bank `0x78` starts at CHR offset `0x1E000`, global tile `0x1E00`.

The PPUCTRL shadow is initialized to `0x88` at CPU `$FEB6`; its background pattern-table select bit (bit 4) is zero. The interrupt/setup code preserves this bit while changing other PPUCTRL flags. Thus the mapped background glyph path is consistent with the direct relationship:

`text/tile byte N -> PPU tile N -> global CHR tile 0x1E00 + N`

This exactly fits the visible sequence at `0x1E10-0x1E29` for A-Z and `0x1E01-0x1E0A` for digits. The mapping is supported by static bank-write and PPU-writer code, but must still be checked against live PPU state in Mesen/FCEUX during each text renderer.

## 4. Supplemental Vietnamese glyph capacity (candidate only)

The source CHR bytes in the following ranges contain zero nonzero pixels in every tile:

- `0x1E30-0x1E5F`: 48 slots
- `0x1E7C-0x1E8E`: 19 slots
- Total: 67 candidate slots, matching the 67 supplemental uppercase Vietnamese glyphs in the current 93-entry glyph plan (26 basic Latin letters + 67 Vietnamese-specific glyphs). `0x8F` is left as one additional spare tile code.

The allocation file assigns the supplemental glyphs to those codes for planning. **These are not yet approved for overwriting.** A blank CHR tile may still be referenced by an existing nametable/background layout; changing its pixels could make an unrelated screen show a new glyph. The mapping also must be applied only to text-body bytes, never to boss dialogue header/metadata bytes or control tokens.

## 5. What Step 4 files contain

- `font_glyph_allocation_candidate_step4.csv` — proposed Unicode glyph -> text byte -> CHR tile allocation.
- `candidate_vietnamese_tile_slots_step4.csv` — measured blankness of every candidate source tile.
- `runtime_code_evidence_step4.json` — machine-readable code signatures and derived mapping.
- `runtime_validation_checklist_step4.csv` — static passes and emulator checks still pending.
- `tools/trace_text_renderer_step4.py` — reproducible validator for the findings.

## 6. Pending emulator checks before writing any patch

1. Set debugger breakpoints at CPU `$C212` (load of `$0783,X`) and `$C215` (store to `$2007`); verify one visible opening character goes through unchanged.
2. Inspect PPUCTRL bit 4 and MMC3 CHR registers 0/1 during opening, boss dialogue, and credits.
3. Confirm that 0x30-0x5F and 0x7C-0x8E are accepted as literal body bytes in every renderer, and that boss header bytes are skipped/handled before the body.
4. Confirm candidate blank tile IDs are not relied on by title, gameplay, HUD, or backgrounds while CHR bank `0x78-0x7B` is mapped.
5. Only then draw the 67 glyphs, insert translated body bytes, build a test ROM, and run emulator regression tests.

No ROM bytes were modified in this step. No translated `.nes` or `.ips` is claimed complete.
