# Release checklist template

Mark each row `PASS`, `FAIL`, or `NOT TESTED`. Add evidence filenames.

- [ ] Clean source hash matches manifest.
- [ ] Header/mapper/PRG/CHR sizes understood and recorded.
- [ ] Every text rendering path of scope identified.
- [ ] Text table based on verified byte-to-glyph mappings.
- [ ] Control codes, terminators, metadata and animation codes documented.
- [ ] Every logical index has a catalog row; aliases are explicit.
- [ ] Translation bytes fit fixed capacities or documented relocation plan.
- [ ] No reserved bytes are emitted as ordinary text.
- [ ] Custom glyphs are in the CHR bank active in every claimed context.
- [ ] Hook/cave mapping and reference safety checked; CPU state preserved.
- [ ] Only approved source ranges changed.
- [ ] IPS/BPS parses and round-trips exactly from clean source.
- [ ] Independent validator passes.
- [ ] Opening, dialogue, credits, transitions and gameplay checks recorded.
- [ ] Build and tested ROM hashes match.
- [ ] Coverage limitations clearly stated.
- [ ] Source ROM excluded from distributable archive unless allowed.
