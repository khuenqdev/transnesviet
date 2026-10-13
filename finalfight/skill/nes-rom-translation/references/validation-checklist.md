# ROM Translation Acceptance Checklist

Record each item as PASS, FAIL, or NOT TESTED and include evidence paths.

## Source identity
- [ ] Source ROM SHA-256 recorded and exact.
- [ ] Source file is clean/unpatched and stored separately.
- [ ] Header format, mapper/submapper, PRG/CHR sizes, trainer, mirroring documented.
- [ ] Source ROM not embedded in public project archive unless explicitly authorized and appropriate.

## Text map and catalog
- [ ] Each renderer/path has been identified separately.
- [ ] Each logical text index has a catalog row.
- [ ] Pointer location, CPU address, physical file offset, and bank mapping are distinguished.
- [ ] Aliases/shared pointers documented.
- [ ] Terminator/control-code grammar is verified on in-game samples.
- [ ] Unknown byte values remain unknown until proven.
- [ ] No blank/untranslated row is represented as complete.

## Translation/encoding
- [ ] Names, terms, and tone are consistent.
- [ ] All Unicode characters have explicit verified encoded values.
- [ ] Encoding rejects unmapped characters and reserved bytes.
- [ ] Encoded bytes—not code points—fit each record's capacity.
- [ ] Line lengths and visual box constraints pass.
- [ ] Control bytes, pointer bytes, metadata, line breaks, animation bytes, and end markers preserved.
- [ ] Shared-pointer aliases display the same intended translation.

## Font and mapper
- [ ] CHR tiles have a labeled atlas and glyph-to-code map.
- [ ] Every custom glyph's physical tile location is known.
- [ ] Active CHR bank is traced in every context that emits the custom character.
- [ ] Blank candidate tiles checked for other references/contexts.
- [ ] New code cave checked for code/data references and mapped-window accessibility.
- [ ] Injected code preserves caller-required registers, flags, stack, and PPU state.
- [ ] Expanded PRG/CHR sizes and NES header fields are valid.
- [ ] Generated previews and in-emulator screenshots are kept distinct.

## Build integrity
- [ ] Build starts from exact clean source.
- [ ] Base patch/artifact hash verified before build.
- [ ] Output is written to a separate file.
- [ ] ROM header/size/mapper fields match design.
- [ ] Approved byte ranges only are modified; binary diff reviewed.
- [ ] Pointer tables unchanged unless relocation is approved and tested.
- [ ] IPS/BPS parses.
- [ ] Applying patch to clean source reproduces exact output hash.
- [ ] ROM, patch, catalog, source and script hashes are recorded.
- [ ] Build script and independent validator are included.

## Emulator tests
- [ ] Correct output hash tested in stated emulator/version.
- [ ] Cold boot/title/menu.
- [ ] Every page of each supported opening/cutscene record.
- [ ] Each relevant dialogue variant/alias.
- [ ] All translated credits pages and end behavior.
- [ ] Vietnamese mark families, special letters, punctuation, spaces, line breaks.
- [ ] No malformed characters, overflow, leftover glyphs, or timing changes.
- [ ] Scene transitions and normal gameplay work.
- [ ] Graphics/animation/audio/pause/reset/death/retry unaffected.
- [ ] Full playthrough completed, or remaining sections explicitly listed as untested.
- [ ] User screenshots/logs linked to output hash.

## Release notes
- [ ] Coverage count and exclusions stated.
- [ ] `STATIC_PASS` is not mislabeled `EMULATOR_PASS`.
- [ ] Clean source is not accidentally included.
- [ ] README gives exact patch base and reproducible build commands.
