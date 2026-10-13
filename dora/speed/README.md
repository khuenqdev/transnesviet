# Walking-speed patch – Doraemon: Giga Zombie no Gyakushuu

A tiny, separate patch that makes the player walk faster. It is independent of the Vietnamese translation and works on **both** the Japanese original and the Vietnamese ROM.

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
* **Slight version:** the call at `$C62E` (`LDX $32 / JSR $AE22`) is redirected to a 21-byte routine at `$FFA0` (free in both ROMs):
  ```
  FFA0  LDA $34 ; CMP #1 ; BNE normal      ; only for the normal 1 px/frame speed
        LDA $32 ; AND #2 ; BEQ normal      ; every step where bit 1 of the counter is set…
        JSR $AE22                          ; …gets one bonus pixel (counter is ≥ 2, so it never ends the step)
  FFAF  normal: LDX $32 ; JSR $AE22 ; RTS
  ```
  A tile now takes 12 frames (16 → 15 → 13 → 12 → 11 → 9 → 8 → 7 → 5 → 4 → 3 → 1 → 0) = 1.33× speed. Scrolling, the player, Doraemon following and NPCs use the same routine, so everything stays aligned.
* **×2 version:** the four `LDA #$01 / STA $34` defaults become `#$02` (8 frames per tile).

## Tests (jsnes, headless)
* Japanese and Vietnamese ROM, single tap: scroll `$02` moves exactly 16 px (e.g. 224 → 208) in 12 frames (patched) vs 16 frames (original); ×2: 8 frames.
* Held walking in all four directions, entering a house: no tearing, Doraemon stays adjacent, no stuck steps (screenshots compared with the unpatched ROM).
* `apply_walkspeed.js` output is byte-identical to the IPS result; JP→translation IPS→speed IPS chain verified; applying twice is refused.
* Not tested: real hardware / other emulators, vehicle/other `$34 = 2` modes (left untouched by the slight patch), long play sessions.
