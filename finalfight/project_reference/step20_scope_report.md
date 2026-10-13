# Step 20 scope and guarantees

## Included

- All seven opening narration records, retained from the user-confirmed Step 18 build.
- Boss dialogue pointer indexes 0–8, retained from the user-confirmed Step 19 pilot.
- All remaining unique boss text slots for indexes 11–77, including shared-pointer aliases where applicable.
- All five credits slots.
- Existing expanded CHR/font bank fix and original pointers.

## Special handling

- BOSS_09 and BOSS_10 are nonverbal grunt sequences. Their seven visible letter glyphs are localized as `ÁÁÁÁÁÁÁ`; the `0x76` punctuation and all `FB/FA/F9` animation bytes remain unchanged.
- Menu/HUD strings not present in the current verified pointer/text inventory are not claimed translated by this package.

## Encoding constraints

This step uses only known mapped glyph codes below $80 for the additional boss and credit text. The opening sequence retains the Step 17 high-glyph routing that the user has already tested. The boss context has not yet been traced with extended characters, so the build avoids those values rather than making an unverified claim.

## Validation

The builder verifies the clean ROM SHA, verifies the Step 19 cumulative IPS against the known-good base ROM, checks all fixed lengths and FF terminators, preserves the five-byte boss prefixes and BOSS_54 FC, does not modify pointer tables, creates a cumulative clean-source IPS, and verifies exact round-trip reproduction. The full game must still be played through in FCEUX before this can be called emulator-verified.
