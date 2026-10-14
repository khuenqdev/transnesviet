# Metal Gunslinger (GBA) – Dự án Việt hóa
## Giai đoạn 1: Phân tích ROM & Trích xuất kịch bản

### 1. Thông tin ROM
| Mục | Giá trị |
|---|---|
| File | `metal_gunslinger.gba` (đổi tên từ `.gba.txt`) |
| Kích thước | 8 MB (8,388,608 byte) |
| Tiêu đề / Mã game | `METALGUN` / `AAPJ` (Nhật) |
| MD5 | `8b7a8c1e315ccf6132afb5bcd7aa4136` |
| Mã hóa văn bản | **Shift-JIS thuần** (không nén, không bảng ký tự riêng) |

### 2. Cấu trúc văn bản
**Khối A – Menu / Hệ thống (0x052E88–0x053A1x): 70 chuỗi**
- Thông báo lưu/xóa/sao chép, tùy chọn, mô tả Gun Arts & Huy hiệu, 22 lệnh truy nã (×2 dạng), menu tiêu đề.
- Mỗi chuỗi được tham chiếu bằng **con trỏ tuyệt đối 0x08xxxxxx** (bảng tại 0x261DC0–0x261EC4 và literal pool trong code: 0x0180C8, 0x018260, 0x018884, 0x01993C).
- Ký tự xuống dòng: `0x0D` (`\r`). Kết thúc: `0x00`.

**Khối B – Kịch bản cốt truyện / Hướng dẫn / Credits: 148 cảnh, 1.222 dòng (29.052 byte)**
- Bảng con trỏ cảnh: `0x780000` (148 × u32 con trỏ GBA → 0x780250 … 0x79317C).
- Mỗi cảnh = header (code bắt đầu tại +0x4C) + bytecode dạng từ 32-bit + vùng chuỗi ở cuối.
- **Opcode `0x29 <u32 offset>`** = đưa một dòng văn bản lên khung thoại; địa chỉ = `base_cảnh + offset`.
- Mỗi lệnh 0x29 hiển thị **một dòng**; mỗi dòng tối đa **19 ký tự full-width (228 px / màn hình 240 px)**.
- Tên người nói (Billy, Fay, Mapiya…) **không có trong văn bản** → có khả năng là nhãn đồ họa (xử lý ở giai đoạn sau).

### 3. Font
| Mục | Giá trị |
|---|---|
| Header font | `0x433ADC` (con trỏ từ code tại `0x002C9C`) |
| Kích thước glyph | 12×12, 1bpp, 2 byte/hàng (MSB bên trái), 24 byte/glyph |
| Số glyph | 6.951 (toàn bộ JIS X 0208) |
| Bảng mã (u16 LE, đã sắp xếp) | `0x433AE4` |
| Dữ liệu glyph | `0x437132` – `0x45FCD9` |
| Glyph game thực sự dùng | 835 |
| **Slot trống có thể tái sử dụng** | **≈ 6.112** |

### 4. Vùng trống trong ROM
| Địa chỉ | Kích thước | Ghi chú |
|---|---|---|
| `0x79A9C4`–`0x7FFFFF` | ~415 KB | **Dùng cho kịch bản tiếng Việt** (sau tất cả cảnh → offset op29 luôn dương) |
| `0x6BDBB0`–`0x77FFFF` | ~777 KB | Dự phòng (menu dùng con trỏ tuyệt đối nên đặt ở đâu cũng được) |
| `0x2878C0`–`0x3FFFFF` | ~1,5 MB | Dự phòng (font/đồ họa mới) |

### 5. Kiểm chứng bản đồ con trỏ
`relocate_test.py` chuyển **toàn bộ 1.292 chuỗi** sang vùng trống, xóa chuỗi gốc, cập nhật **1.340 tham chiếu**, rồi đọc lại qua con trỏ mới → **100% khớp**. ROM `test_relocated.gba` vẫn là tiếng Nhật, dùng để thử trên emulator (mGBA/VBA-M): nếu game hiển thị bình thường thì bản đồ con trỏ đã đúng hoàn toàn.
> Lưu ý: kiểm chứng ở mức dữ liệu; tôi chưa chạy được ROM trên emulator trong môi trường này.

### 6. Chiến lược hiển thị tiếng Việt (đề xuất cho Giai đoạn 2)
Vấn đề: 19 ô × 12 px/dòng là quá ngắn cho tiếng Việt (thường dài gấp ~2 lần tiếng Nhật).

**Giải pháp: "ghép cặp ký tự" (glyph-pair / DTE trong font)**
- Thiết kế bộ chữ Việt **6×12 px (half-width)** đầy đủ dấu: a ă â e ê o ô ơ u ư i y × 5 thanh + đ, chữ hoa, số, dấu câu.
- Mỗi glyph 12×12 chứa **2 ký tự** 6 px → mỗi dòng đạt **38 ký tự Latin**.
- Ghi đè các cặp ký tự thực tế xuất hiện trong bản dịch vào các slot kanji không dùng (~6.112 slot trống – đủ cho vài nghìn cặp).
- Bộ mã hóa sẽ chuyển văn bản Việt → chuỗi mã SJIS của các slot đó.
- **Ưu điểm:** không cần sửa code ASM, game vẫn tra font bằng tìm kiếm nhị phân như cũ.
- 12 px chiều cao đủ chỗ cho dấu kép (ví dụ: ổ, ữ, ậ).

### 7. Lộ trình đề xuất
| GĐ | Nội dung |
|---|---|
| **1 ✅** | Phân tích ROM, trích xuất toàn bộ văn bản, bản đồ con trỏ, font, kiểm chứng relocation |
| 2 | Font tiếng Việt 6×12 + bộ mã hóa cặp ký tự + bộ chèn văn bản; dịch thử Khối A (70 chuỗi menu) → patch thử nghiệm |
| 3 | Dịch toàn bộ kịch bản (1.222 dòng) – tách dòng theo giới hạn 38 ký tự |
| 4 | Đồ họa chữ (tiêu đề, tên nhân vật, tên màn, nút…) |
| 5 | Kiểm tra, sửa lỗi, tạo patch IPS/BPS + tài liệu cuối |

### 8. Danh mục file
**tools/**
- `sjis_dump.py` – quét toàn ROM tìm chuỗi Shift-JIS (khảo sát ban đầu)
- `scene_parser.py` – phân tích 148 cảnh, chuỗi + tham chiếu op29 → `scenes.json`
- `menu_parser.py` – chuỗi menu + con trỏ tuyệt đối → `menu.json`
- `font_finder.py` – dò tìm font theo heuristic
- `font_dump.py` – xuất font 12×12 → `font_sheet.png`, `font_map.tsv`
- `tileview.py` – xem dữ liệu ROM dạng tile GBA 1/2/4/8bpp
- `export_script.py` – tạo bảng dịch `script_master.csv`
- `relocate_test.py` – kiểm chứng bản đồ con trỏ → `test_relocated.gba`

**output/**
- `script_master.csv` – **bảng dịch chính** (1.292 dòng; UTF-8 BOM, mở được bằng Excel). Cột `vi_text` để điền bản dịch; `en_ref` có sẵn tiếng Anh tham chiếu cho menu.
- `scenes.json`, `menu.json` – dữ liệu máy đọc cho bộ chèn
- `script_raw.tsv` – kết quả quét thô (có nhiều nhiễu từ đồ họa – chỉ để tham khảo)
- `font_sheet.png` – toàn bộ font (glyph sáng = đang dùng; mờ = slot trống)
- `font_map.tsv` – index ↔ mã SJIS ↔ ký tự ↔ offset ↔ đang dùng
- `glossary_vi.tsv` – thuật ngữ / tên riêng & đề xuất tiếng Việt
- `test_relocated.gba` – ROM kiểm thử relocation

### 9. Cách chạy lại
```bash
python tools/scene_parser.py metal_gunslinger.gba
python tools/menu_parser.py metal_gunslinger.gba
python tools/font_dump.py metal_gunslinger.gba
python tools/export_script.py
python tools/relocate_test.py
```
Cần: Python 3.8+, Pillow (cho `font_dump.py`, `tileview.py`).
