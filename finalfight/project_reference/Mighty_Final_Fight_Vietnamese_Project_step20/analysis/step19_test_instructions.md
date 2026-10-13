# Step 19 FCEUX test — Thrasher dialogue pilot

## Files

- Standalone diagnostic ROM: `Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.nes`
- Combined IPS: `Mighty_Final_Fight_Vietnamese_BOSS_DIALOGUE_PILOT_STEP19.ips`

The patch is based on the clean USA ROM and already includes Step 17's expanded CHR/font bank fix plus Step 18's translated opening sequence. Do not apply it over a Step 17/18/19 ROM.

## In-game test

1. Open the Step 19 ROM directly in FCEUX and start from a fresh reset.
2. Confirm the opening sequence still renders cleanly and transitions to gameplay.
3. Progress until Thrasher's first dialogue; the target text sequence is the opening boast/threat block (`HA HA! TA LÀ THRASHER,` → `CHÚA TỂ THÀNH PHỐ.` → `CÚI ĐẦU MAU LÊN!` → `BIẾT CHƯA? TA CAI TRỊ` / `PHỐ NÀY!` → `KẺ NÀO XÚC PHẠM TA` → `ĐỀU CHẾT!`). The existing game may split these records into separate dialogue boxes.
4. Verify that accented low-byte glyphs such as `Ú`, `Ể`, `À`, `Ố`, `Đ`, `Ầ`, `Ê`, `Ị`, `Ẻ`, and `Ạ` are clean; no unrelated graphics should change; confirm the boss dialogue and later transition continue normally.

The seven modified payloads are fixed-size and retain the five-byte metadata prefix and original FF terminator position. BOSS_00/BOSS_01 share one pointer, as do BOSS_04/BOSS_05, so each pair will display the same translated record.

## Optional CHR-bank trace

If letters render incorrectly during this dialogue, run `tools/trace_boss_dialogue_chr_step19.lua` in the Lua scripting window while the Step 19 ROM is loaded. It does not call `memory.registerread`, so it works with older FCEUX builds that lack that callback. Power-cycle after installing it, then play to the boss text. The script writes `step19_boss_chr_trace.csv` and `step19_boss_chr_trace_info.txt` beside itself. Return those files if further bank analysis is needed.

## Status

Build-time checks passed, including exact IPS round-trip and confined-diff checks. The boss-dialogue renderer/font bank is not yet user-verified in FCEUX; this test is required before extending the patch to more boss records.
