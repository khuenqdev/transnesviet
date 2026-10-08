# Step 2 — Verified pointer and renderer analysis

## ROM baseline

The supplied ROM is NES 2.0 with mapper 4/MMC3, 8 × 16 KiB PRG banks and 16 × 8 KiB CHR banks.
The PRG+CHR body CRC32 is `3F78037C`.

## 1. Opening/cutscene renderer

The renderer begins at PRG offset `0x01A00` (CPU `$9A00` when PRG bank 0 is mapped at `$8000`).

It loads the message index from RAM `$B8` and forms a 16-bit pointer:

- low-byte table: `$9B2C`
- high-byte table: `$9B33`
- entries: 7

The resulting pointers are:

`$9B3A, $9C34, $9C8C, $9CA3, $9D2E, $9D5C, $9E07`

Those map to PRG offsets beginning at `0x01B3A`.

The loop dereferences `(zp $0C),Y`, checks `$FF` for end-of-message, and handles `$FE` as a
layout/line-control byte. A decoded character is placed in the render command area around
`$0780-$0784`, followed by calls including `JSR $F406`.

## 2. Boss dialogue pointer loader

The boss dialogue pointer loader is in PRG around `0x0991F`.

It constructs the 16-bit text pointer from:

- high-byte table: `$A4FD`
- low-byte table: `$A54C`

There are 78 verified entries (indices 0–77). The next array byte does not produce a pointer inside the
dialogue region, so it is excluded from the table.

The pointers resolve into PRG offsets `0x09D71` through `0x0A4CA`, covering the complete boss/encounter
dialogue block.

This is the first solid indication that the boss dialogue can be safely relocated by changing only
these two pointer arrays, provided the runtime bank mapping remains valid.

## 3. Credits renderer

A second text renderer exists around PRG `0x12708`.

Its pointer arrays are:

- low: `$A7D6`
- high: `$A7DB`
- count: 5

When PRG bank 9 is mapped into `$A000-$BFFF`, these resolve to:

`$A7E0, $A7F1, $A87D, $A8CB, $A95C`

which map to the credits data at PRG `0x127E0-0x1299B`.

## 4. Text encoding

Verified ordinary text bytes:

- `00` space
- `10-29` A-Z
- `2A` apostrophe
- `2B` period
- `2C` comma

Verified control/effect bytes appearing in text:

- `75`, `76`, `78`
- `F9`, `FA`, `FB`, `FC`
- `FE`
- `FF`

Bytes such as `35` and `01-4E` occur as presentation/header/speaker metadata inside boss records and
must be preserved, not translated as ordinary characters.

## 5. What is now safe to implement

A future builder can relocate:

- opening message bodies, updating `$9B2C/$9B33`;
- boss dialogue message bodies, updating `$A4FD/$A54C`;
- credits bodies, updating `$A7D6/$A7DB`;

while keeping the original record/control bytes that are not text.

## 6. Still pending

The exact glyph-tile lookup inside the `JSR $F406` rendering path has not yet been isolated.
That is the next font-specific reverse-engineering task. Once isolated, the Vietnamese glyph bank can
be added without changing the dialogue pointer system.
