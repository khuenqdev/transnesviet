---
name: nes-vietnamese-translation
description: Translate a NES (Famicom) game into Vietnamese with full tone marks, Sino-Vietnamese vocabulary and no dialog overflow. Use for NES/UNROM/CHR-RAM ROM text hacking, bitmap-font injection, bank expansion and IPS patching.
---

# NES → Vietnamese ROM translation

Distilled from a finished project (Saiyuuki World, UNROM, hiragana-only, CHR-RAM). Reference implementation: `build_rom.py`, `src/tramp.asm`, `src/window.asm`, docs 01/02.

## 0. Ground rules
- Work on a COPY of the user's ROM; record md5; ship an IPS patch, never the ROM alone.
- Build everything by script (original → patched ROM). Never hand-edit the only copy.
- Change one thing, test, keep notes of every address in hex.
- Plan with a task list; verify by running the ROM in a headless emulator (jsnes: `git clone https://github.com/bfirsh/jsnes`) and viewing screenshots, not by assuming.
- Do not claim hardware/other-emulator compatibility unless tested. Report untested scenes honestly.

## 1. Recon (30 min)
1. Header: bytes 4/5/6/7 → PRG banks, CHR banks (0 = CHR-RAM), mapper, NES2.0. Mapper 2 (UNROM) = 16 KB switchable at $8000, last bank fixed at $C000, bus conflicts.
2. Per bank: first bytes, count of $FF/$00 padding (free space), reset/NMI vectors in last bank.
3. Run the game headless, dump PPU pattern tables ($0000-$1FFF) and nametables at text scenes; render tiles as PNG (2bpp: plane0 bytes 0-7, plane1 bytes 8-15). Identify the font range and which tiles are free (pictures vs. text).
4. Build a table file: tile number → kana/char, using the PNG plus known sentences. Dakuten/handakuten may be separate tiles.

## 2. Find the text
- Convert a known on-screen sentence with the table; search every bank for the bytes (also relative search: constant differences between consecutive bytes).
- Search for the little-endian address of the found record → pointer table. Confirm ascending, plausible targets, count N.
- Decode all records. Typical record: `[flags][len]([addr])[codes]`; flags encode wait-for-button, typewriter speed, chain-to-next, explicit VRAM address. Terminators/waits are often a special tile (▼).
- Dump the whole script to a bilingual file (JP | romaji/EN gloss | VI). Separate dialog, menu, shop, status labels, banners, title.

## 3. Understand the engine (emulator-assisted RE)
- Trace which PC writes PPU $2007/$2006, or log writes to the game's PPU buffer (here: queue at $0700, routine `JSR $FF76`; NMI drains ≤128 bytes/frame). Check the carry/full return convention.
- Disassemble the routine (dis6502). Map state: row index, column counter, timers, flags. Find 3-5 hook points: init row, per-step, blink-arrow, clear box, plus title/menu.
- Use RAM watchers to list free RAM; use savestates to jump to rare scenes. Input replays diverge when timing changes: load an ORIGINAL-ROM savestate into the NEW ROM instead (reload PRG banks after fromJSON).

## 4. Design for Vietnamese (the core decision)
Vietnamese needs ~134 glyph shapes with stacked marks; an 8×8 tile font cannot do it, and a game has few free tiles. Use **pre-rendered proportional bitmaps**:
1. Cell height 12 px (cap top 3, x-height top 5, baseline 9; marks above, dot-below/descenders below). Compose diacritics programmatically from base glyphs (never draw 134 glyphs by hand). 8-px all-caps variant for tight labels.
2. Render each translated row to a bitmap, line width ≤ box (e.g., 17 tile columns = 136 px; keep 8 px for a ▼ arrow). Each text column = two tiles (top 8 rows; bottom 4 rows + border/padding). Bake the box border into the bottom tile.
3. Cut into 8×8 chunks, dedupe, assign to a **tile pool** of free tiles (keep tiles still used: digits, symbols). Upload chunks into CHR-RAM through the game's own PPU queue a few per frame as the "typewriter" advances.
4. Hook the engine so kana drawing is replaced; rows that must stay original (numeric prices, etc.) pass through to the original routine.
5. Builder reports "row N too wide" → shorten the translation (never shrink below legibility); use `--strict` in CI.

## 5. Room for code and data: ROM expansion
- Header byte 4 → new PRG count (power of 2 for UNROM). Copy the fixed bank into the new last slot (and the old slot). Every bank may need its own number as a first byte (game's check) — preserve it.
- Bus conflicts: write bank number to an address holding the same value. Enlarge the table (16 entries) and repoint every `STA table,X` site.
- Fixed bank free bytes are scarce: put only small trampolines there (save zero-page scratch, select bank, `JSR` into bank, restore, restore bank). Real logic lives in switchable banks at the same address ($8000) so one routine layout serves all data banks (bank = base + row//32).
- Compact the original text bank: records that do not wait can be header-only; keep wait rows full with the ▼ terminator.

## 6. Writing the translation (quality)
- Context first: identify the source work (e.g., Journey to the West) and use established Vietnamese names/terms: Tôn Ngộ Không, Đường Tăng/Tam Tạng, Trư Bát Giới, Sa Tăng, Như Lai, Tây Thiên, Linh Sơn, Hán-Việt for places, titles, items, spells (e.g., 金→kim, 元→nguyên, 妖怪→yêu quái).
- Use full diacritics everywhere; consistent glossary file; one term = one translation.
- Respect budgets: ≈ 17-column × 2-line boxes; Vietnamese words are short per glyph but long per sentence; condense, drop particles, prefer Hán-Việt compounds for density.
- Status/menu labels: use uppercase 8-px font with simple accents (MẠNG/BẠC/CÔNG); avoid unreadable stacked marks at 8 px.
- Keep numerals, button names and escape codes unchanged.

## 7. Title screen
If title art is tiles in CHR-RAM: replace free tiles with outlined Vietnamese text (e.g., 13 columns × 2 rows), upload 3 tiles/frame, write nametable cells; if art is sprites/unavailable, add a plain Vietnamese caption below. Avoid sprite collisions (move to rows 25-26).

## 8. Testing checklist
- [ ] ROM boots; title shows translation; intro dialog plays and advances; boxes erase fully
- [ ] Every row rendered at least once (bulk-hook all rows through the engine and screenshot sheets)
- [ ] No row too wide; no tile collisions with pool/kept tiles
- [ ] Shop prices/status/menus; banners
- [ ] IPS regenerated and reproduces the ROM byte-for-byte
- [ ] README lists untested areas and md5 of the required base ROM

## 9. Known pitfalls (all hit in the original project)
- Assembler "branch out of range" → invert the branch over a JMP.
- A routine falling through into the next (missing `BNE common`).
- Carry not handled when computing 16-bit pattern address; compute high byte first.
- jsnes savestate: cpu.mem keeps the old ROM → reload banks.
- Matplotlib mathtext eats `$…$` in docs (set `text.parse_math=False`).
- Queue stalls ≈20 frames after big uploads: wait before screenshotting.
- Calling engine routines outside their normal context crashes; call the hook instead.

## 10. Deliverables
Patched ROM + IPS + README + translation table (JP | VI | width) + technical walkthrough with figures + tutorial + scripts. Provide md5s, state limitations, remind the user to own the original.
