---
name: nes-vietnamese-translation
description: Translate a NES/Famicom game into Vietnamese (full tone marks, Hán-Việt, no overflow); covers ROM recon, text/engine RE, bitmap-font injection, UNROM/MMC1-SUROM expansion, IPS, QA bug-hunting and separate gameplay patches (e.g. walk speed).
---

# NES → Vietnamese ROM translation

Distilled from two finished projects: Saiyuuki World (UNROM, hiragana-only, CHR-RAM) and Doraemon: Giga Zombie no Gyakushuu (MMC1/SUROM 512 KB, script/event tables, field engine). Reference implementation: `build_rom.py`, `src/tramp.asm`, `src/window.asm`, docs 01/02 (parts 15 and 18, chapters 20-25).

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
- [ ] QA section (10) done: table counts asserted, all string copies patched, force-message sweep, gameplay flow replay

## 9. Known pitfalls (all hit in the original project)
- Assembler "branch out of range" → invert the branch over a JMP.
- A routine falling through into the next (missing `BNE common`).
- Carry not handled when computing 16-bit pattern address; compute high byte first.
- jsnes savestate: cpu.mem keeps the old ROM → reload banks.
- Matplotlib mathtext eats `$…$` in docs (set `text.parse_math=False`).
- Queue stalls ≈20 frames after big uploads: wait before screenshotting.
- Calling engine routines outside their normal context crashes; call the hook instead.
- Fixed-bank hook applied to only one of two SUROM copies → works in one half, crashes in the other.
- Gameplay patch changed one variable but a private timer kept the old rate (NPCs stop between tiles).
- Table header/count bytes not carried along when rewriting a table → wrong entry selected.
- Patch validated only on the player/scroll, not on NPCs/sprites → regression found by users.

## 10. QA: the game is more than its text (do this BEFORE delivering)
Text rewrites break things that do not look like text. Budget as much time for QA as for translation.
1. **Diff audit**: `cmp -l original new` grouped by bank. Every changed region must be explained.
2. **Lookup tables with counts/headers.** If a table is preceded by small numbers that sum to its size, they are counts or group sizes (Doraemon event table: `03 02 04 08 04` at bank 2 `$813E`). When the build rewrites or moves a table, copy the header and `assert` it equals the original. A lost header produces *wrong-entry* bugs (the wrong character joins the party, repeatedly).
3. **Strings that exist in several copies** (Yes/No drawn from three places, menu labels re-drawn by other screens). Search every bank of the original for each fixed string; patch all copies with the **same length** (pad with the blank tile).
4. **Force-message sweep**: write each message id into the engine's message RAM variable, screenshot the box, review a contact sheet. Also sweep menus, shops, status, title (`©`, alignment of left-aligned labels).
5. **Play the real flow** (title → intro → first town → first event → shop/save) with a recorded input script; compare screenshots with the original ROM at the same points. Replay by frame counts diverges when timings change, so use RAM/state conditions where possible.
6. **Keep a `docs/BUGFIXES.md`**: symptom, mechanism, fix, how verified, version.
7. When a tester reports a bug: reproduce → compare with original → find who writes the deciding RAM variable → fix at the lowest level (table byte) → test neighbours → audit the same bug class everywhere.

## 11. Bigger ROMs: MMC1/SUROM (512 KB) and fixed-bank copies
* SUROM: PRG select (reg 3) switches 16 KB within a 256 KB half; the half is chosen by a CHR-register bit. Bank-switch routines must set both. Header byte 4 = `0x20` for 512 KB.
* The fixed bank must exist **identically in both halves** (Doraemon: banks 15 and 31; banks 14/15 copied to 30/31). Redirect the game's bank-switch entry (`$C0B2`) to a stub that handles the half bit.
* Every later patch to the fixed bank must be applied to **all copies** (`forEachFixed`). Original ROM (header byte 4 = 16) has one copy. Detect the variant from the header.
* Free space: check `0xFF` runs in **both** ROMs and use the intersection. Prefer free space in the same bank as the caller (`JSR` within the bank) when the fixed bank is tight. Also verify free RAM with a never-referenced-address scan (search all banks for the address bytes) *and* a runtime check.
* Emulator: headless jsnes needs custom SUROM handling (see `scripts/jsnes_lib.mjs`); don't trust savestates (garbled tiles after `fromJSON`) - replay from boot and consume the pending reset with `cpu.emulate()`.

## 12. Gameplay patches (speed, etc.) as separate patches
Rules learned the hard way (walk speed took three versions):
1. **Inventory every reader/writer of the variable you change in ALL banks** (search each addressing mode: zero page `A5/85 xx`, absolute `AD/8D/CE/EE lo hi`). Read the consumers (NPC, camera, animation, collision) before designing.
2. **Never add an exception only part of the engine sees.** An extra scroll/movement call on some frames (v1) desynchronised NPC sprites that compensate for `$34` px/frame. Change the *step value* for the whole frame (before the consumers run) and restore it after (v2).
3. **Look for private timers** that tick once per frame regardless of speed (Doraemon NPC step clock `$0450`, `DEC` at bank D `$8BB3`). They must scale with the speed (v3: `$0450 -= $34`) or entities stop between tiles, overlap walls and start moving together.
4. Keep steps landing exactly on 0 (collision/events at step boundaries); gate a boost on counters (`$32 >= 2`, NPC clock != 1).
5. Reuse values the game already supports (e.g. `$34 = 2` with doubled sprite deltas) instead of inventing semantics.
6. A tiny flag in verified-free RAM remembers "I boosted, restore after"; never infer it from the value (modes that legitimately use 2 are ambiguous).
7. Deliver **separately** from the translation: one IPS per ROM (`*_JP.ips` must not write beyond the original size; `*_VN.ips` patches all fixed-bank copies) + `apply_*.js` that detects ROM type, verifies expected bytes, refuses double patching, supports variants, and produces output byte-identical to the IPS result. Order: translation first, gameplay patch second.
8. Version the patch; README lists hooks, free space, RAM byte, tests, open issues.

## 13. Measure glitches, don't eyeball them
* OAM buffer: find the `STA $4014` page (Doraemon `$0500`). Sprite = `y, tile, attr, x`.
* World position = sprite + scroll (+256 per X nametable bit, +240 per Y bit, mod 480 vertically).
* Static NPCs must keep a constant world position; walkers move in whole tile steps; **at rest, sprite left edge − (logical tile x × 16) must be 0** (NPC table in RAM, Doraemon `$420…`). Print a histogram for original, broken and fixed ROM. The original also shows noise (neighbouring NPC mis-matched, NPC mid-step) - compare against it, not against perfection.
* Add a seeded random-walk test with periodic screenshots (`scripts/wander.mjs`). Hero steering by frame counts means original and patched runs cannot be compared step by step - say so.
* State untested areas (other towns, vehicles, hardware) in the README and the final answer.

## 14. Deliverables
Patched ROM + IPS (+ separate gameplay IPS per ROM and an apply script) + README + translation table (JP | VI | width) + BUGFIXES.md + technical walkthrough with figures + tutorial + scripts and tests. Provide md5s, state limitations and untested areas, remind the user to own the original.
