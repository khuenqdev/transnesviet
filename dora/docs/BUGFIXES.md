# Bug-fix report (v2)

Reported: (1) choices flip between English YES/NO and Có/Không; (2) the cat in the Startown mansion shows Shizuka's scene and adds another Shizuka to the party each time. This round also audited the ROM for further defects.

## Fix 1 – third "blink" variant of the Yes/No box was still English
* The dialogue Yes/No choice (`F3` opcode, routine at `$E186`) copies a 10-byte string from the fixed bank to the window: `$E1FE` (cursor on *Yes*), `$E208` (cursor on *No*) and **`$E212` (cursor hidden, used for the blink)**.
* `patchYesNo()` translated only the first two, so every blink showed the English-patch text `Yes   No`.
* Fix (`tools/build.js → patchYesNo`): the third string is now `␠Có␠␠Không`. The build verifies the old bytes first (`expect`).

## Fix 2 – story-event messages (C-table) resolved to the wrong text
* Message ids `$C0–$FE` are story events (table **C**, 21 entries, pointers at `$8143`). The lookup at `$D915` computes the entry as `sum(counts[0..sub)) + (id-$C0)`, where `counts` are the five bytes **`03 02 04 08 04` stored at `$813E–$8142` of the script bank**.
* The Vietnamese build moves the script to new banks `$11–$14`, but `compile.js` writes only the pointer tables and leaves the header gap as `$FF`. With `$FF` counts, every event with sub-table ≥ 1 (C3…C20: the cat "Meo… Meo…", Dekisugi, the Miyoko/Shizuka scenes, shopkeepers…) read a pointer from random text bytes.
* Fix (`tools/build.js → patchScript`): copy the five count bytes from the original bank 2 into the new bank header (checked to equal `03 02 04 08 04`).
* Verified by running the real ROM routine (`tools/test/lookup3.mjs`): old ROM – C3…C20 all wrong; new ROM – C0…C20 all correct. `lookup2.mjs` (E table 228 entries + A table) and `lookup4.mjs` (B table) pass on both. `tabcheck.js` confirms every pointer of tables A, B, C, D, E in the new ROM points to the block with the same label as in the Japanese ROM. Forcing event C4 in the emulator: old ROM shows unrelated text, new ROM shows "Meo… Meo…".

## Fix 3 (found in audit) – broken © on the title screen
* The English patch drew © with tiles `$56`+`$EF`. `$56` is now a Vietnamese glyph, so the title showed `ỵ)1990`. A new tile `©1` is allocated (`tools/vn.js`) and written at `$A2F6` and `$A31B` of bank 9 → `(C)1990 Epoch Co.` / `(C)1999 WakdHacks Co.`.

## Audit results (no defect)
* Script control codes and pointer references are identical to the Japanese script for all 334 + 356 blocks (only layout codes `{p}{w0}{w1}{fa}` differ because of re-wrapping); `check.js` reports no overlong lines.
* No remaining English `Yes`/`No` strings in the active banks; E/A/B/D lookups correct.
* Regression: file select, speed, name entry, intro, first Yes/No, menu and "Tìm" screens are pixel-identical before/after Fix 3.

## Not verified
* I could not walk all the way to the Startown mansion in the headless emulator (jsnes), so the cat scene was verified through the real lookup routine and a forced-event test, not by playing through it. Please re-test it in your emulator.
* Only jsnes was used (on Linux); the original author used FCEUmm.

## Re-running the checks
`node tools/test/lookup3.mjs "<rom>"`, `lookup2.mjs "<rom>" vn`, `lookup4.mjs "<rom>" vn` (needs jsnes cloned next to the repo: `git clone https://github.com/bfirsh/jsnes ../vendor/jsnes`; SUROM support is added inside `tools/test/lib.mjs`).
