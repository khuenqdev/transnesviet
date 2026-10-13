# Step 19 — Thrasher boss-dialogue pilot

This batch patches the first contiguous Thrasher boast/threat sequence, using the validated Step 18 opening ROM and the existing low-byte glyph tiles. The game’s five-byte per-record metadata prefixes and all pointers remain untouched. Duplicate indexes are called out because they share the same pointers.

## Translations

### BOSS_00/01 (indexes 0, 1)

**English:** HEH HEH. I AM THRASHER,

**Vietnamese:** HA HA! TA LÀ THRASHER,

Slot:** 22 text bytes / 23 content bytes; 1 trailing space(s).**

Shared pointer used by both BOSS_00 and BOSS_01.

### BOSS_02 (indexes 2)

**English:** RULER OF THIS CITY.

**Vietnamese:** CHÚA TỂ THÀNH PHỐ.

Slot:** 18 text bytes / 19 content bytes; 1 trailing space(s).**

Shortened to fit the fixed record slot.

### BOSS_03 (indexes 3)

**English:** BOW DOWN BEFORE ME

**Vietnamese:** CÚI ĐẦU MAU LÊN!

Slot:** 16 text bytes / 19 content bytes; 3 trailing space(s).**

Imperative preserved; wording adapted to fit without the unverified Ớ byte.

### BOSS_04/05 (indexes 4, 5)

**English:** DON'T YOU KNOW I RULE THE

**Vietnamese:** BIẾT CHƯA? TA CAI TRỊ

Slot:** 21 text bytes / 25 content bytes; 4 trailing space(s).**

Shared pointer used by both BOSS_04 and BOSS_05; completed by BOSS_06.

### BOSS_06 (indexes 6)

**English:** STREETS

**Vietnamese:** PHỐ NÀY!

Slot:** 8 text bytes / 9 content bytes; 1 trailing space(s).**

Completes the preceding statement: “Biết chưa? Ta cai trị phố này!”

### BOSS_07 (indexes 7)

**English:** THOSE WHO OFFEND ME

**Vietnamese:** KẺ NÀO XÚC PHẠM TA

Slot:** 18 text bytes / 19 content bytes; 1 trailing space(s).**

Threat phrasing kept concise for the original slot.

### BOSS_08 (indexes 8)

**English:** MUST DIE

**Vietnamese:** ĐỀU CHẾT!

Slot:** 9 text bytes / 9 content bytes; 0 trailing space(s).**

Continues the preceding threat: “Kẻ nào xúc phạm ta đều chết!”

## Important scope note

This pilot deliberately avoids text codes `$80-$8F`, since the high-byte R1-routing hook is presently verified only in the opening text path. Every custom Vietnamese glyph in these seven strings uses a text code below `$80`. The active R0 font bank during boss dialogue still needs confirmation in FCEUX; test the patched boss conversation before extending the batch.

## ROM changes

Only the seven target payload ranges change relative to Step 18. The five-byte metadata headers, fixed-length record ends, pointer table, expanded CHR data, opening text and helper remain unchanged.
