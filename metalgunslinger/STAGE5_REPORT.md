# Metal Gunslinger (GBA) – Việt hóa
## Giai đoạn 5: Việt hóa chữ đồ họa còn lại, kiểm thử, patch phát hành (IPS + BPS)

### 1. Kết quả chính
| Hạng mục | Kết quả |
|---|---|
| Quét toàn bộ tài nguyên sprite | Bộ phân tích `ANIM` tổng quát: **188 tài nguyên, 754 khung hình** → xác định mọi chữ Nhật dạng sprite |
| Bảng tên khu vực (4 bộ + bản đồ) | 28 bảng: HEAVEN · NAVANHO · GOLD MOUNTAIN · IRON TRAIN · COSMOPOLITAN · LAND |
| Menu Game Over (2 trạng thái màu) | ステージリトライ → **CHƠI LẠI MÀN** · データロード → **TẢI DỮ LIỆU** · タイトル → **TIÊU ĐỀ** |
| Màn Data Select | コピー → **CHÉP** · 削除 → **XÓA** |
| Màn tiêu đề | © 2002 アットマーク → **© 2002 ATMARK** |
| Màn tạm dừng (BG) | タイム/エネミー/スコア → **TIME / ENEMY / SCORE**; chú thích chân dung → **BILLY MACDOLEANE** |
| Ghi lại đồ họa | 8 khối LZ77 nén lại đều nhỏ hơn bản gốc → **ghi đè tại chỗ**, không đổi con trỏ |
| Patch phát hành | `MetalGunslinger_VI_v1.0.bps` (CRC32 nguồn/đích) + `MetalGunslinger_VI_stage5.ips` – cả hai cho ROM giống nhau từng byte |
| ROM gốc | CRC32 `8DFB7A2F`, MD5 `8b7a8c1e315ccf6132afb5bcd7aa4136` |
| ROM Việt hóa | CRC32 `10A3AEBF`, MD5 `bc843c440a37c68f591b2acae992ca9a` |

### 2. Kỹ thuật
- **`tools/anim.py`** – định dạng sprite: `[LZ77 tile][LZ77 palette]['ANIM'…]`; bảng animation tại `ANIM+0x4C`; khung 36 byte bắt đầu bằng con trỏ danh sách mảnh OAM.
- **`tools/sprite_text.py`** – xóa chữ cũ bằng màu nền của từng hàng (cùng palette), vẽ chữ in hoa đậm 5×7 có dấu tiếng Việt; màu viền/quầng sáng lấy theo khoảng cách tới lõi chữ gốc → giữ phong cách bảng vàng và quầng xanh.
- **`tools/bg_text.py`** – chữ trên nền BG: kiểm tra tile không dùng chung, font 3×5.
- **`tools/bps.py`** – tạo/áp patch BPS có kiểm tra CRC32.
- Danh sách chữ: `tools/stage5_jobs.py` (sprite), `tools/stage5_bgjobs.py` (BG); xem trước: `tools/preview_jobs.py`.

### 3. Kiểm thử
- Màn tiêu đề và Data Select chụp từ emulator (`qa/title_screen.png`, `qa/data_select.png`).
- Bảng tên khu vực, menu Game Over: so sánh trước–sau dựng từ dữ liệu ROM (`qa/sprite_text_before_after.png`).
- Màn tạm dừng: trước–sau dựng từ dữ liệu ROM (`qa/pause_before_after.png`); đã kiểm trong emulator ở phiên trước.

### 4. Build
```
cd output
python3 ../tools/build_all.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt mgs_vi.gba MetalGunslinger_VI.ips
python3 ../tools/bps.py create ../metal_gunslinger.gba mgs_vi.gba MetalGunslinger_VI_v1.0.bps
```

### 5. Giới hạn đã biết
- Chữ nhỏ dưới logo tiêu đề (メタルガン・スリンガー) giữ nguyên.
- Chưa chơi hết toàn bộ game; nên chơi thử trên mGBA. Emulator không mô phỏng âm thanh.
