# Metal Gunslinger – Bản Việt hóa v1.1 (bản cuối) – GBA

**Game:** メタルガン・スリンガー / Metalgun Slinger (Nhật, 2002 – Open Sesame / Atmark)

## Cài đặt
1. Chuẩn bị ROM gốc **Metalgun Slinger (Japan)** – CRC32 `8DFB7A2F`, MD5 `8b7a8c1e315ccf6132afb5bcd7aa4136`.
2. Áp **`output/MetalGunslinger_VI_v1.1.bps`** bằng Floating IPS (Flips), Rom Patcher JS, hoặc:
   `python3 tools/bps.py apply metal_gunslinger.gba output/MetalGunslinger_VI_v1.1.bps metal_gunslinger_vi.gba`
   (Bản IPS tương đương: `output/MetalGunslinger_VI_v1.1.ips` – cho ROM giống hệt từng byte.)
3. ROM kết quả: CRC32 `072D1316`, MD5 `81ebe904c21915c3e346c5ef12274882`. Khuyên dùng **mGBA**.

> Patch BPS tự kiểm tra CRC32 ROM nguồn: nếu báo lỗi, ROM của bạn không phải bản gốc chuẩn.

## Đã Việt hóa
- Toàn bộ menu/hệ thống (70 chuỗi), kịch bản, hướng dẫn, thông báo nhận chip/huy hiệu, staff credits (630 khung / 1.270 dòng) – đủ dấu tiếng Việt.
- 14 nhãn tên nhân vật, 28 bảng tên khu vực, menu Game Over, nút Data Select, dòng bản quyền, màn tạm dừng.
- Phụ đề dưới logo tiêu đề: メタルガン・スリンガー → **TIẾNG VIỆT** (mới trong v1.1).

## Lịch sử phiên bản
- **v1.1 (Giai đoạn 6 – bản cuối):** phụ đề logo tiêu đề; sửa cách đọc tên staff trong credits theo MobyGames/VGMdb; kiểm thử hồi quy toàn bộ.
- v1.0 (Giai đoạn 5): bản phát hành đầu tiên.

Chi tiết quy trình: `HUONG_DAN_VIET_HOA.md`; báo cáo từng giai đoạn: `STAGE1…6_REPORT.md`.
