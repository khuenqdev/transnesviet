# Translation plan and current release scope — Step 20

## Goal

Translate the presently verified pointer-indexed story text in Mighty Final Fight (USA) to Vietnamese with full tone marks while respecting the NES's fixed-width byte encoding and MMC3 CHR banking.

## Confirmed and retained from earlier tests

- Step 17: expanded CHR banks fixed high-byte font lookup for the opening path; user confirmed glyph rendering and screen transition.
- Step 18: seven opening narration records; user confirmed clean text rendering.
- Step 19: initial Thrasher dialogue pilot; user confirmed boss dialogue looked fine.
- Step 20: remaining indexed boss lines and all five credits records; visible grunt lettering is localized while `0x76` punctuation and `FB/FA/F9` animations remain intact.

## Encoding safeguards

- Original pointer tables are not relocated or rewritten.
- Boss records retain their five-byte metadata prefix; the `BOSS_54` trailing `FC` command is preserved.
- No extra high-byte glyph codes `0x80–0x8F` are emitted in Step 20 boss/credits payloads, because that bank-routing behavior has only been confirmed in the opening path.
- BOSS_09 and BOSS_10 replacement is exactly seven visible glyph bytes per record; the following punctuation and animation commands remain byte-identical.
- Credits use `FE` for line breaks and `FF` for end-of-string; replacement lengths remain fixed.

## Coverage boundary

The current verified catalog is 90 index-level rows: 7 opening, 78 boss-dialogue indexes, 5 credits. Four boss indexes alias other indexes by pointer, leaving 86 physical slots. Text in menu/HUD graphics or any unidentified text path outside these pointer tables is not claimed translated. The final ROM also needs a complete FCEUX playthrough to be called emulator-verified.

## Build artifacts

- `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.nes`
- `release/Mighty_Final_Fight_Vietnamese_FULL_TRANSLATION_STEP20.ips`
- `analysis/step20_full_translation_catalog.tsv`
- `analysis/step20_remaining_boss_and_credits_translations.md`
- `analysis/step20_validation.json`, `step20_validation.txt`, `step20_checksums.txt`
- `tools/build_full_translation_step20.py`

## Clean source identity

Expected source SHA-256: `5e70be9de1c0d272c456873216a568eb2377f5c211456c8f8330c601f3920b26`

Do not run the builder against a previously patched ROM. Pass the clean USA ROM via `--source-rom`.
