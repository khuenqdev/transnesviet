# Case Study: Mighty Final Fight (USA), Step 20

This reference captures observations from the actual Step 20 project. Use these as regression examples only; they are not generic offsets for other ROMs.

## Input and output identity

- Source: `Mighty Final Fight (USA).nes`
- Source SHA-256: `5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`
- Original size: 262,160 bytes
- Header: NES 2.0, mapper 4/MMC3; initial report recorded horizontal mirroring
- Original PRG: 128 KiB; original CHR: 128 KiB
- Step 20 output size: 278,544 bytes
- Step 20 output SHA-256: `03d2d05e2303e2b41a5213b248bdd3d20cfa478a8e473dd00734d42882e6bcbc`
- Step 20 IPS SHA-256: `2778df5a7eabad3ca66d32b2a9fc6e41f1b0b7a825daa8c174e43dbdc6b135b5`
- Step 20 IPS size: 20,208 bytes; 137 records

The Step 17 font/bank fix grew the output by 16 KiB of CHR data. The final output size and header were checked by the builder; for another ROM, do not copy the same sizes/mapper assumptions.

## Verified text coverage

- 7 opening text records.
- 78 boss dialogue index rows.
- 5 credits records.
- 90 index rows; four boss entries share physical pointers, so 86 unique physical text slots.
- Opening and first boss-dialogue rendering were confirmed by the user in earlier iterations.
- Full Step 20 playthrough remained pending in the validation report.
- Menu/HUD graphic text and unidentified text paths are outside the claim of coverage.

## Pointer/renderer observations

- Opening pointer tables at PRG offsets `0x1B2C/0x1B33`; targets include CPU `$9B3A`, `$9C34`, `$9C8C`, `$9CA3`, `$9D2E`, `$9D5C`, `$9E07`.
- Boss pointer table: high `$A4FD`, low `$A54C`; pointers map into PRG around `0x09D71-0x0A4CA`.
- Credits low table `$A7D6`, high table `$A7DB`; targets `$A7E0`, `$A7F1`, `$A87D`, `$A8CB`, `$A95C`.
- Text queue RAM `$0780-$0784`.
- Opening hook candidate CPU `$9A47`; fixed bank consumer `$C1FD`; fixed-bank character lookup `$F406` in observed trace contexts.
- Boss records retain five-byte metadata prefixes. The special `BOSS_54` trailing `FC` command remains intact.

Consult `project_reference/pointer_tables.csv` for exact offsets and bank annotations.

## Verified base table

- `00` space.
- `10-29` A-Z.
- `2A` apostrophe; `2B` period; `2C` comma.
- `0x35` is reserved as a boss-record metadata/header value in this extraction context; do not assign it as a normal character.
- Control bytes include `75`, `76`, `78`, `F9`, `FA`, `FB`, `FC`, `FE`, `FF` with usage depending on renderer/record.

The table is incomplete for all possible game graphics; it documents the current verified indexed text context.

## Major debugging events

1. Static CHR sheets found candidate glyph ranges but did not prove they were active at runtime.
2. The first composite font drew marks too tightly; user testing flagged `Ị`, `Đ`, `Ẹ`, and confusion between `Ồ` and `Ố`.
3. High custom-byte glyphs appeared as glitches because the active CHR bank differed from the bank where glyphs had been written.
4. The runtime trace revealed different observed MMC3 R1 values during opening text. Step 17 copied the required CHR contexts and placed custom glyphs in the corresponding bank copies; the user confirmed the glyphs and transition looked correct.
5. A Step 12 code-cave helper corrupted other glyphs because it overwrote A during the PPU-address check and wrote the address byte as text on its non-target path. Step 13 repaired register/flag preservation; user reported only the intended T->E change.
6. Step 18 translated all opening records and the user confirmed clean rendering.
7. Step 19 translated the initial Thrasher dialogue and the user reported it looked fine.
8. Step 20 completed the indexed boss/credits catalog and passed static/IPS round-trip checks. Complete FCEUX playthrough was not recorded.

## Step 20 exact build commands

```bash
python3 tools/build_full_translation_step20.py \
  --source-rom "/path/to/Mighty Final Fight (USA).nes" \
  --project "/path/to/Mighty_Final_Fight_Vietnamese_Project_step20" \
  --base-ips "/path/to/Mighty_Final_Fight_Vietnamese_Project_step20/analysis/step19_boss_dialogue_pilot_combined.ips" \
  --output-rom "/path/to/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes" \
  --output-ips "/path/to/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips"

python3 tools/validate_final_build_step20.py \
  --source-rom "/path/to/Mighty Final Fight (USA).nes"
```

The builder and validator should be run with the exact project tree and expected base IPS. The source ROM must match the source SHA shown above.
