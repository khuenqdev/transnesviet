# Walking-speed patch – Doraemon: Giga Zombie no Gyakushuu

A tiny, separate patch (**v3** – fixes the NPC glitches of the earlier releases) that makes the player walk faster. It is independent of the Vietnamese translation and works on **both** the Japanese original and the Vietnamese ROM.

| File | Use on | Effect |
|---|---|---|
| `walkspeed_JP.ips` | original Japanese ROM (256 KB, 262 160 bytes) | **≈ 1.33× faster** (recommended, "slightly faster") |
| `walkspeed_VN.ips` | Vietnamese ROM (512 KB, 524 304 bytes) – apply **after** the translation patch | same, ≈ 1.33× |
| `walkspeed_x2_JP.ips` / `walkspeed_x2_VN.ips` | same as above | optional: **2× faster** (4 bytes changed, no new code) |
| `apply_walkspeed.js` | either ROM | patches the ROM directly, auto-detects JP / VN, refuses wrong or already-patched ROMs. `node apply_walkspeed.js in.nes out.nes [--x2]` |
| `build_speedpatch.js`, `ips.js` | – | rebuilds the IPS files from the two ROMs |

Why two IPS files? The Vietnamese ROM (512 KB, SUROM) keeps a second copy of the fixed program bank (banks 15 and 31); both copies must be patched, and an IPS record beyond the end of the 256 KB original would enlarge it. The script `apply_walkspeed.js` handles both cases with one command. Order: *translation first, speed patch second* (the translation IPS would overwrite the second bank copy otherwise).

## How it works
* The field engine moves the character in 16-pixel steps (one tile). Each frame the routine at `$AE22` (bank `$0C`) scrolls 1 pixel (`$34` = pixels per frame, normally 1) and subtracts it from the step counter `$32` (16 → 0), so a tile takes **16 frames**. Some game states set `$34 = 2` (faster mode); the walking defaults are written at `$C064`, `$D19B` and in bank `$0D` at `$93FB`, `$941D`.
* The step length must stay a multiple that ends exactly on 0 (collision checks and events happen at the step boundaries), so a fractional speed cannot simply be stored in `$34`.
* **Slight version (v3, NPC-safe):** the earlier releases made NPCs glitch (they moved with the hero, ended over houses/trees, sprites broke up, all NPCs restarted together). Root cause: every NPC step is driven by its own 16-tick clock `$0450` (bank D `$8BB3`: `DEC $0450`) that always counts down by **1 per frame**, while the NPC/sprite routines only get called as long as the hero's step lasts. A hero step of 12 frames therefore cut every NPC step short, leaving NPCs half-way between tiles (and v1 additionally shifted them against the scroll). v3 changes three things, all in space that is free in both ROMs:
  1. *Step size per frame:* the step `$34` is set for the **whole frame** (not an extra scroll call), so NPC logic and scroll agree.
     ```
     C613  JSR $FFA0   (replaces LDA #$0D / JSR $CD5C, before the NPC/sprite routines)
     FFA0  LDA #$0D ; JSR $CD5C                 ; the replaced code
           LDA #0 ; STA $07EA                   ; flag = not boosted ($07EA is never used by the game)
           LDA $34 ; CMP #1 ; BNE end           ; only normal walking (modes that already use 2 are untouched)
           LDA $32 ; AND #2 ; BEQ end           ; counter bit 1 set (counter >= 2) -> this frame moves 2 px
           LDA $0450 ; CMP #1 ; BEQ end         ; ...unless the NPC clock has 1 tick left (would overshoot)
           LDA #2 ; STA $34 ; STA $07EA
     end:  RTS
     C62E  JMP $FFC5   (replaces LDX $32 / JSR $AE22)
     FFC5  LDX $32 ; JSR $AE22                  ; scroll + hero by $34 pixels
           PHA ; LDA $07EA ; BEQ + ; DEC $34 ; + PLA ; RTS    ; give the step back to 1
     ```
  2. *NPC clock:* `DEC $0450` at bank D `$8BB3` becomes `JSR $9E3E` (routine in free bank-D space): `$0450 -= $34` (clamped at 0, Z flag as DEC left it). An NPC step now ends exactly when the hero's step ends, and NPC pixels per frame (the game doubles them when `$34 != 1`) match the clock.
  A tile takes 12 frames (16 → 15 → 13 → 12 → 11 → 9 → 8 → 7 → 5 → 4 → 3 → 1 → 0) = 1.33× speed. The ×2 patch uses the same NPC-clock fix.
* **×2 version:** the four `LDA #$01 / STA $34` defaults become `#$02` (8 frames per tile).

## Tests (jsnes, headless)
* Single tap on Japanese and Vietnamese ROMs: scroll moves exactly 16 px in 12 frames (patched) vs 16 (original); ×2: 8 frames.
* **NPC alignment test** (`tests/npcalign.mjs`): the hero walks 10–12 long segments through the first town and stops; after 70 frames at rest the sprite position of every NPC is compared with its logical tile in the game's NPC table (RAM `$420…`). Offset 0 = sprite is exactly on its tile. Vietnamese ROM, route 1: v1 patch 7 of 18 on the tile (offsets 4, 12, -4, -8, -12 … scattered), **v3 patch 15 of 19**, the rest being ±8/16 mismatches that the unpatched ROM also shows (neighbouring NPC picked by the test). Route 2: v1 7 of 18, **v3 16 of 18 (VN), 22 of 24 (JP)**; ×2 24 of 33 (JP). A few odd offsets (9, 1 px) remain in the JP/×2 runs and were not explained – they may be test noise or a small residual glitch.
* `tests/npcdrift.mjs` (sprites tracked in world coordinates) and `tests/wander.mjs` (random walk + screenshots): NPCs stay on roads in the screenshots.
* `apply_walkspeed.js` output is byte-identical to the IPS result; JP→translation IPS→speed IPS chain verified; applying twice is refused.
* Not tested: real hardware / other emulators, vehicles and other `$34 = 2` modes, towns other than the first one, dungeons, very long play sessions. The test hero is steered by frame counts, so original and patched ROMs cannot be compared step by step.
