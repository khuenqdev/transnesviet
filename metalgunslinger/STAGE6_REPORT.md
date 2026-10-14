# Metal Gunslinger (GBA) – Việt hóa
## Giai đoạn 6 (cuối): Hoàn thiện, kiểm thử hồi quy, phát hành v1.1

### 1. Kết quả chính
| Hạng mục | Kết quả |
|---|---|
| Phụ đề logo tiêu đề | メタルガン・スリンガー → **TIẾNG VIỆT** (chữ trắng viền đen, có dấu Ế/Ệ) – `tools/title_sub.py` |
| Credits | Sửa tên staff theo MobyGames/VGMdb: Akira Takada, Mineyuki Sakurai, Noboru Takahashi, Makoto Morimoto, Mitsuru Kemmochi, Mediat |
| ROM gốc để build | Tái tạo từ `test_relocated.gba` (GĐ1) – khớp CRC32 `8DFB7A2F` / MD5 gốc |
| Build tái lập | Build lại bản v1.0 từ mã nguồn → trùng từng byte với patch GĐ5 |
| Kiểm chứng văn bản | 630/630 khung, 1.270 dòng: 0 lỗi, 0 thiếu glyph, 0 sai lệch |
| Quét hội thoại emulator | 38 cảnh, 1.031 ảnh chụp, 954 trang có hộp thoại → 24 bảng duyệt (`qa/dialogue_sweep/`) |
| Màn hình kiểm tra | Tiêu đề, Data Select, gameplay, tạm dừng, Key Config, Badge & Arts (`qa/final_screens_v1.1.png`) |
| Patch cuối | `MetalGunslinger_VI_v1.1.bps` + `MetalGunslinger_VI_v1.1.ips` – cả hai áp ra ROM giống hệt |
| ROM Việt hóa v1.1 | CRC32 `072D1316`, MD5 `81ebe904c21915c3e346c5ef12274882` |

### 2. Kỹ thuật – phụ đề logo
- Màn tiêu đề: BG1 mode 0, 256 màu, tile LZ77 `0x5F9DC4` (182 tile 8bpp), map LZ77 `0x5FC0F0`.
- Phụ đề nằm ở tile 175–181 (hàng 11) và dòng cuối của tile 161–168; tất cả chỉ dùng 1 lần trong map → sửa an toàn.
- Xóa katakana, vẽ chữ hoa 3×5 + dấu (mũ, sắc, nặng) với màu trắng/xám (palette 191/133) và viền đen (1); nén lại LZ77 → nhỏ hơn bản gốc (8.244 ≤ 8.562 byte), **ghi tại chỗ**, không đổi con trỏ.

### 3. Giới hạn đã biết
- Emulator tự viết không có âm thanh; nên chơi thử hết game trên mGBA.
- Kiểm thử credits/intro được làm bằng mô phỏng hiển thị từ dữ liệu ROM (`qa/preview_credits.png`), vì nhảy cảnh trực tiếp vào credits không nạp nền gốc.
- Cách viết tên riêng dùng phiên âm Latin phổ biến (Perla Negra, Myna Myna, Babag-Gun…).

### 4. Build
```bash
cd output
python3 ../tools/build_all.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt mgs_vi.gba MetalGunslinger_VI_v1.1.ips
python3 ../tools/bps.py create ../metal_gunslinger.gba mgs_vi.gba MetalGunslinger_VI_v1.1.bps
```
