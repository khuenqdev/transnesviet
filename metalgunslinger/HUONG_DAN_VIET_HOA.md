# Metal Gunslinger (GBA) – Tài liệu quy trình Việt hóa đầy đủ (Giai đoạn 1 → 6)

Tài liệu này mô tả **toàn bộ** quy trình đã dùng để Việt hóa *メタルガン・スリンガー / Metalgun Slinger* (GBA, Nhật, 2002),
từ phân tích ROM tới bản patch cuối cùng, kèm cách build lại từ mã nguồn.

---

## 0. Tổng quan

| Hạng mục | Giá trị |
|---|---|
| ROM gốc | Metalgun Slinger (Japan), mã game `AAPJ`, 8 MB |
| CRC32 / MD5 ROM gốc | `8DFB7A2F` / `8b7a8c1e315ccf6132afb5bcd7aa4136` |
| Mã hóa văn bản gốc | Shift-JIS thuần (không nén) |
| Font gốc | 12×12, 1bpp, 6.951 glyph JIS X 0208 @ `0x433ADC` |
| Văn bản đã dịch | 70 chuỗi menu + 630 khung thoại (1.270 dòng màn hình) |
| Đồ họa chữ đã vẽ lại | 14 nhãn tên, 28 bảng tên khu vực, menu Game Over, nút Data Select, bản quyền, màn tạm dừng, phụ đề logo |
| Sửa code ASM | **Không** – mọi thay đổi chỉ là dữ liệu (văn bản, font, con trỏ, đồ họa) |

Cấu trúc thư mục:

```
tools/    mã nguồn Python của mọi giai đoạn (parser, font, encoder, builder, đồ họa, patch)
emu/      emulator GBA headless tự viết (C) + script kiểm thử
output/   bản dịch (menu_vi.tsv, story_vi.txt), dữ liệu trung gian, patch cuối
qa/       ảnh kiểm thử
```

---

## 1. Giai đoạn 1 – Phân tích ROM & trích xuất

1. **Dò văn bản** (`sjis_dump.py`): quét toàn ROM tìm chuỗi Shift-JIS kết thúc bằng `0x00`.
2. **Menu/hệ thống** (`menu_parser.py`): 70 chuỗi tại `0x052E88–0x053A1x`, mỗi chuỗi được tham chiếu bằng con trỏ tuyệt đối `0x08xxxxxx` → tìm mọi con trỏ (căn 4 byte).
3. **Kịch bản** (`scene_parser.py`): bảng 148 con trỏ cảnh tại `0x780000`. Mỗi cảnh là bytecode các từ 32-bit;
   **opcode `0x29 <u32 offset>`** đẩy một dòng chữ (địa chỉ = base cảnh + offset).
4. **Font** (`font_finder.py`, `font_dump.py`): header `0x433ADC`, bảng mã u16 đã sắp xếp `0x433AE4`, bitmap `0x437132` (24 byte/glyph).
   Game chỉ dùng 835 glyph → ~6.100 slot trống.
5. **Kiểm chứng bản đồ con trỏ** (`relocate_test.py`): dời toàn bộ 1.292 chuỗi sang vùng trống, xóa bản gốc, đọc lại qua con trỏ mới → khớp 100%.
6. Xuất bảng dịch `script_master.csv` (`export_script.py`).

## 2. Giai đoạn 2 – Font tiếng Việt & bộ mã hóa

* **Font 6×12** (`vi_font.py`): vẽ tay đủ 134 nguyên âm có dấu (thường + hoa), đ/Đ, A–Z, số, dấu câu. Khi có mũ + thanh, thanh đặt bên phải mũ.
* **Ghép cặp ký tự / DTE trong font** (`vi_codec.py`): mỗi dòng cắt thành cặp 2 ký tự; mỗi cặp khác nhau chiếm một mã kanji không dùng,
  ảnh 12×12 của mã đó bị ghi đè bằng 2 ký tự 6 px → mỗi dòng chứa được gấp đôi ký tự, **game không cần sửa code**.
* Menu được chèn vào vùng trống `0x6BDBB0`, mọi con trỏ tuyệt đối được cập nhật (`insert_stage2.py`).

## 3. Giai đoạn 3 – Dịch kịch bản

* `group_messages.py`: các lệnh `0x29` liên tiếp kết thúc bằng `0x2A` (hiện khung & chờ) hoặc `0x69` (dòng intro/credits) = 1 khung thoại → `messages.json` (630 khung).
* `build_vi.py`: tự ngắt dòng cân đối trong ≤ số dòng gốc, thụt 1 khoảng ở dòng tiếp như bản Nhật, dòng thừa để trống;
  văn bản ghi vào `0x79AA00+`, chỉ đổi toán hạng của `0x29` (không đụng bytecode khác).
* `preview_story.py`: đọc lại 1.270 dòng qua chính opcode `0x29` + font trong ROM → 0 thiếu glyph, 0 sai lệch.
* Quy ước xưng hô: Billy ↔ Mabel/Doc *tớ–cậu*; Fay ↔ nhóm *chị–em*; Mapiya (giọng máy) **IN HOA**; Sun Dance nói ngắt quãng;
  Myna Myna *tao–mày*; phản diện *ta–ngươi*.

## 4. Giai đoạn 4 – Emulator headless, sửa bố cục, nhãn tên

* `emu/gbaemu.c`: ARM7TDMI (ARM+Thumb), BIOS HLE, PPU mode 0–5, DMA, timer, EEPROM, save state, script điều khiển.
* Phát hiện giới hạn thực tế **36 ký tự/dòng** (ô thứ 19 bị khung che) → 26 câu viết gọn lại; builder kiểm tra `MAXW=36`.
* Intro (cảnh 1): khung ≤20 ký tự, tự căn giữa cửa sổ chữ (opcode `0x67`); hộp căn giữa (opcode `0x77`) cập nhật độ rộng.
* 14 nhãn tên nhân vật (sprite) vẽ lại chữ Latin trên nền khung vàng gốc (`labels.py`, `label_maker.py`, `gfx_insert.py`).
* 944 trang hội thoại được chụp & duyệt.

## 5. Giai đoạn 5 – Chữ đồ họa còn lại & patch phát hành

* `anim.py`: bộ phân tích tổng quát tài nguyên sprite `[LZ77 tile][LZ77 palette]['ANIM'…]` – 188 tài nguyên, 754 khung.
* `sprite_text.py`: xóa chữ Nhật bằng màu nền từng hàng, vẽ chữ in hoa đậm có dấu tiếng Việt, giữ màu viền/quầng sáng gốc.
  Áp cho 28 bảng tên khu vực, menu Game Over (CHƠI LẠI MÀN / TẢI DỮ LIỆU / TIÊU ĐỀ), nút CHÉP/XÓA, © 2002 ATMARK.
* `bg_text.py`: chữ trên BG màn tạm dừng (TIME/ENEMY/SCORE, BILLY MACDOLEANE).
* Patch BPS (`bps.py`, có kiểm tra CRC32) + IPS.

## 6. Giai đoạn 6 – Hoàn thiện & phát hành bản cuối (v1.1)

* **Phụ đề logo tiêu đề**: dòng katakana nhỏ メタルガン・スリンガー dưới logo được thay bằng **TIẾNG VIỆT**
  (BG1 màn tiêu đề, tile 8bpp LZ77 `0x5F9DC4`, map `0x5FC0F0`; tile của phụ đề là duy nhất trong map – đã kiểm tra) – `tools/title_sub.py`.
* **Credits**: đối chiếu với danh sách staff công khai (MobyGames, VGMdb), sửa cách đọc tên:
  Akira Takada, Mineyuki Sakurai, Noboru Takahashi, Makoto Morimoto, Mitsuru Kemmochi, Mediat.
* **Tái tạo ROM gốc** từ `test_relocated.gba` (GĐ1) để build lại – khớp MD5/CRC32 gốc.
* **Kiểm thử hồi quy**: build lại từ mã nguồn, kiểm chứng 1.270 dòng; quét lại toàn bộ cảnh hội thoại trên emulator; chụp màn tiêu đề,
  Data Select, gameplay, màn tạm dừng, Key Config, Badge & Arts, credits.
* Đóng gói bản cuối: BPS + IPS, README, tài liệu này, công cụ, emulator, ảnh QA.

---

## 7. Build lại từ mã nguồn

Yêu cầu: Python 3.8+, Pillow; gcc (cho emulator, không bắt buộc).

```bash
cp /đường/dẫn/metal_gunslinger.gba .          # ROM gốc (CRC32 8DFB7A2F)
cd output
python ../tools/build_all.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt mgs_vi.gba MetalGunslinger_VI_v1.1.ips
python ../tools/bps.py create ../metal_gunslinger.gba mgs_vi.gba MetalGunslinger_VI_v1.1.bps
python ../tools/preview_story.py mgs_vi.gba preview.png T0001 T0039     # kiểm chứng + ảnh mô phỏng
```

Sửa bản dịch:
* Menu: `output/menu_vi.tsv` (`\n` = xuống dòng).
* Kịch bản: `output/story_vi.txt`, mỗi dòng `Txxxx | đoạn / đoạn …` (thoại: mỗi đoạn = 1 câu trong 「」; intro/hướng dẫn/credits: mỗi phần = 1 dòng màn hình).
* Chạy `build_vi.py … --check` để kiểm tra tràn dòng/thiếu glyph trước khi build.

Kiểm thử bằng emulator:

```bash
cd emu && gcc -O2 -o gbaemu gbaemu.c -lm
./gbaemu ../output/mgs_vi.gba menus.txt         # script: run N | press KEYS N | shot f.ppm | save/load f …
```

## 8. Bản đồ dữ liệu ROM (tóm tắt)

| Địa chỉ | Nội dung |
|---|---|
| `0x052E88–0x053A1x` | Chuỗi menu gốc (Shift-JIS) |
| `0x261DC0–0x261EC4` | Bảng con trỏ menu |
| `0x433ADC` | Header font 12×12; bảng mã `0x433AE4`; bitmap `0x437132` |
| `0x5D6E78…0x5F4A1C` | 14 sprite nhãn tên nhân vật |
| `0x5BB354…0x5CC2B4` | Sprite bảng tên khu vực / menu |
| `0x5F9DC4` / `0x5FC0F0` | Tile 8bpp / map logo tiêu đề (BG1) |
| `0x6BC63C` | Tile BG màn tạm dừng |
| `0x6BDBB0+` | Menu tiếng Việt (mới) |
| `0x780000` | Bảng 148 con trỏ cảnh |
| `0x79AA00+` | Kịch bản tiếng Việt (mới) |
