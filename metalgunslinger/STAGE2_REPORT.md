# Metal Gunslinger (GBA) – Việt hóa
## Giai đoạn 2: Font tiếng Việt, bộ mã hóa cặp ký tự, bộ chèn & dịch menu

### 1. Kết quả
| Mục | Kết quả |
|---|---|
| Font tiếng Việt 6×12 | 229 ký tự: đủ 134 nguyên âm có dấu (thường + hoa), đ/Đ, A–Z, 0–9, dấu câu, mũi tên, 『』「」… |
| Bản dịch | **70/70 chuỗi menu/hệ thống** (lưu/xóa/chép, tùy chọn, Gun Arts, Huy hiệu, 22 lệnh truy nã ×2, menu tiêu đề) |
| Kiểm tra độ rộng | 0 cảnh báo – mọi dòng ≤ độ rộng dòng tiếng Nhật gốc |
| Cặp ký tự đã dùng | 318 (còn 5.412 slot trống cho GĐ3) |
| Patch | `MetalGunslinger_VI_stage2.ips` (11 KB) – đã kiểm tra apply → khớp từng byte |
| ROM sau patch (MD5) | `19d9a3ae8f9fdf249a5c9f6b16149a76` |

### 2. Kỹ thuật
**Font:** mỗi ký tự rộng 6 px (5 px nét + 1 px giãn). Bố cục 12 hàng: hàng 0–2 dấu chữ hoa, 3–9 chữ hoa/số, 5–9 thân chữ thường, 10–11 phần đuôi (g, p, y) và dấu nặng. Khi có mũ (â, ê, ô) + thanh, dấu thanh đặt bên phải mũ để không dính nhau (kiểu chữ Việt truyền thống).

**Ghép cặp (DTE trong font):** mỗi dòng được cắt thành cặp 2 ký tự; mỗi cặp khác nhau được gán một mã kanji không dùng (ưu tiên JIS cấp 2, từ cao xuống), ảnh 12×12 của mã đó bị ghi đè bằng 2 ký tự 6 px. Văn bản lưu mã SJIS của cặp → **game không cần sửa code**, tra font như cũ. Bảng cặp lưu trong `pair_table.json` và được dùng tiếp ở GĐ3.

**Chèn văn bản:** chuỗi mới ghi vào vùng trống `0x6BDBB0`, mọi con trỏ tuyệt đối được cập nhật; chuỗi gốc giữ nguyên (không còn được tham chiếu). Xuống dòng vẫn dùng `0x0D`.

**Kiểm chứng:** `preview.py` đọc lại ROM đã patch qua chính con trỏ + bảng font của game và vẽ ra `preview_menu.png` → hiển thị đúng 100%.

> ⚠️ Chưa chạy được trên emulator trong môi trường này. Hãy thử trên mGBA/VBA-M: màn hình tiêu đề (menu), Lưu/Xóa/Chép, menu Start (Tùy chọn → Gun Arts/Huy hiệu), màn hình Truy nã. Lời thoại cốt truyện **vẫn là tiếng Nhật** (GĐ3).

### 3. Quy ước dịch
- Giữ tên riêng: Billy, Metalgun, Gun Arts, Gun Force, Perla Negra…
- 賞金首/手配書 → *Truy nã*; 罪状 → *Tội*; シェリフバッジ → *Huy hiệu Cảnh sát trưởng*.
- Biệt danh tội phạm dịch nghĩa: *William Tia Chớp, Harvey Tay Sắt, Lycos Mắt Ưng, Đại tá Mortimer*.
- 警官殺し → *Giết cớm* (ngắn gọn, đúng chất miền Tây, vừa khung 26 ký tự).

### 4. Cách dùng
```bash
# Áp patch
python tools/ips.py apply metal_gunslinger.gba MetalGunslinger_VI_stage2.ips metal_gunslinger_vi.gba
# Hoặc build lại từ bản dịch (sửa output/menu_vi.tsv rồi chạy, trong thư mục output/)
rm pair_table.json
python ../tools/insert_stage2.py ../metal_gunslinger.gba menu_vi.tsv mgs_vi_stage2.gba
python ../tools/preview.py mgs_vi_stage2.gba preview_menu.png
python ../tools/ips.py create ../metal_gunslinger.gba mgs_vi_stage2.gba MetalGunslinger_VI_stage2.ips
```

### 5. File mới / cập nhật
**tools/** `vi_font.py` (font Việt + xuất bảng chữ), `vi_codec.py` (bộ mã hóa cặp), `insert_stage2.py` (bộ chèn + kiểm tra độ rộng), `preview.py` (mô phỏng hiển thị), `ips.py` (tạo/áp patch) + toàn bộ công cụ GĐ1.
**output/** `MetalGunslinger_VI_stage2.ips`, `menu_vi.tsv`, `pair_table.json`, `preview_menu.png`, `vi_font_chart.png`, `script_master.csv` (đã điền 70 dòng `vi_text`), `menu.json`, `scenes.json`.

### 6. Tiếp theo – Giai đoạn 3
Dịch 1.222 dòng kịch bản/hướng dẫn/credits (148 cảnh), mở rộng bộ chèn cho opcode `0x29` (ghi vào `0x79AA00+`), giới hạn 38 ký tự/dòng.
