# Step 19 scope and encoding notes

This is the first boss-dialogue pilot, not a full game translation. Only the seven listed record payloads change compared with the Step 18 output; the patch is cumulative when applied to the clean original ROM.

## Record structure

Each selected record has a five-byte metadata/control prefix beginning with `35`. It is preserved exactly. The text payload starts five bytes after each record's file offset. The body is padded with space byte `00` as needed so its terminal `FF` remains at the original address. Existing record lengths and pointer-table entries do not change.

## Extended codes

All seven translations use mapped text bytes strictly below `80`. This avoids introducing `80–8F` codes, whose R1 bank-switch helper is only confirmed on the opening text path. The custom glyphs in the `$30–$7F` range depend on the active R0 font bank; this pilot’s FCEUX test must confirm the active bank in boss dialogue.

## Translations

- BOSS_00/BOSS_01: `HA HA! TA LÀ THRASHER,`
- BOSS_02: `CHÚA TỂ THÀNH PHỐ.`
- BOSS_03: `CÚI ĐẦU MAU LÊN!`
- BOSS_04/BOSS_05: `BIẾT CHƯA? TA CAI TRỊ`
- BOSS_06: `PHỐ NÀY!`
- BOSS_07: `KẺ NÀO XÚC PHẠM TA`
- BOSS_08: `ĐỀU CHẾT!`

The translation is condensed to fit each fixed slot. The last two records form the sentence “Kẻ nào xúc phạm ta đều chết!” The records BOSS_00/BOSS_01 and BOSS_04/BOSS_05 share pointers, so the translation applies to both index aliases.
