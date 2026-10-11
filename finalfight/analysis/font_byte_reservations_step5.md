# Step 5 — byte reservation discovered in the dialogue dump

The extracted boss-dialogue records contain repeated five-byte layout/render headers. Byte `0x35` recurs as a segment marker, including inside longer boss dialogue streams, and must not be allocated as an ordinary glyph byte in those streams. Step 4 had assigned `É` to `0x35`; Step 5 corrects that candidate mapping to the spare byte `0x8F` / global CHR tile `0x1E8F` / CHR file offset `0x03E900`. The original tile at `0x1E8F` is blank in the supplied ROM.

The updated full 93-row allocation is `font_glyph_allocation_step5.csv`; the compact 67-entry generated glyph list is `font_prototype_tiles_step5.csv`. The reserved `0x35` entry is explicit in `byte_code_collision_audit_step5.csv`.

This is a static interpretation of the extracted stream layout, not proof from an emulator trace. Before translating/injecting boss text, validate the command/header parser in Mesen or FCEUX. The source ROM is unchanged.
