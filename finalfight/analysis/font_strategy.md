# Full-tone Vietnamese font strategy

1. Preserve the existing text engine's one-byte character model during the first pass.
2. Prefer precomposed 8x8 Vietnamese uppercase glyphs over runtime compositing. This avoids
   changing the dialog writer to draw two tiles for one letter.
3. Reclaim unused tiles in a verified font CHR bank first. Do not overwrite gameplay tiles until
   runtime tracing identifies the bank used while text is rendered.
4. If the available font bank cannot hold the full Vietnamese set, expand CHR and add a dedicated
   font bank, then patch the text-time CHR bank selection.
5. Keep glyph widths visually uniform. The source game is all-caps and uses a fixed-width font.
6. Build a preview sheet and inspect every line at the game's real dialog width, not in a desktop font.
7. All Vietnamese text must be normalized to NFC before encoding.

Required uppercase glyph families:
A Á À Ả Ã Ạ Ă Ắ Ằ Ẳ Ẵ Ặ Â Ấ Ầ Ẩ Ẫ Ậ
E É È Ẻ Ẽ Ẹ Ê Ế Ề Ể Ễ Ệ
I Í Ì Ỉ Ĩ Ị
O Ó Ò Ỏ Õ Ọ Ô Ố Ồ Ổ Ỗ Ộ Ơ Ớ Ờ Ở Ỡ Ợ
U Ú Ù Ủ Ũ Ụ Ư Ứ Ừ Ử Ữ Ự
Y Ý Ỳ Ỷ Ỹ Ỵ
D Đ


## Step 4: Static text-to-PPU mapping

The direct PPU writer is at CPU `$C1FD-$C221`; it sends `$0783,X` directly to `$2007`. The NMI setup writes MMC3 CHR registers 0/1 as `0x78/0x7A`, with background pattern-table select bit 4 cleared by the `0x88` PPUCTRL shadow initialization. This supports a direct text-byte to global tile relationship of `0x1E00 + byte`.

The 67 supplemental Vietnamese uppercase glyphs are assigned candidate byte values in the blank-looking ranges `0x30-0x5F` and `0x7C-0x8E`; `0x8F` remains spare. The allocation is a planning aid only until emulator tracing confirms renderer semantics and no unrelated screen uses those tile IDs.
