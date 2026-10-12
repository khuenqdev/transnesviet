# Saiyuuki World (西遊記ワールド, NES) – Việt hóa

ROM gốc: `Saiyuuki_World_Japan.nes` (md5 `01e8594637accca56e7d1a2e63906db5`).
Sản phẩm: `build/saiyuuki_vi.nes` (256 KB, mapper 2/UNROM) và `build/saiyuuki_vi.ips` (áp lên ROM gốc).

## Kết quả
- Toàn bộ 213 dòng thoại/tên/nhãn được dịch, có đủ dấu thanh, dùng từ Hán–Việt (Ngộ Không, Tam Tạng, Ngưu Ma Vương, Như Ý Bổng, Long Tháp, Ba Tiêu Động, 12 cung hoàng đạo…).
- Chữ không tràn khung: mỗi dòng ≤ 136 px (≤ 128 px nếu có mũi tên ▼); `build_rom.py` báo lỗi nếu vượt (`--strict` để dừng build).
- Tiêu đề: đồ họa logo là tile BG nén nên giữ nguyên; thêm dòng "Tây Du Ký Thế Giới" (viền đen, chữ trắng) dưới các dòng bản quyền.
- Đã kiểm thử bằng emulator jsnes: hộp thoại (gõ từng cột, ▼ nhấp nháy, xóa trang), cửa hàng (lời chào, tên món, "không đủ tiền"), màn trạng thái (Select), tiêu đề, và gameplay không bị hỏng sau đó (so sánh khung hình với ROM gốc).
- Chưa quan sát được trong game thật: 10 dòng "banner" (203–212, địa chỉ $2101); chỉ kiểm bằng cách gọi trực tiếp hook (vẽ đúng, nhưng màu/nền của màn hình thật chưa xem).

## Phát hiện về ROM
- UNROM 128 KB (8 bank × 16 KB), CHR-RAM; đồ họa nằm trong PRG dạng RLE (escape $FA). Header NES 2.0.
- Font kana là tile BG $B0–$FF (chữ = màu 1, nền = màu 3, viền hộp = màu 2); chữ số $B4–$BD, × $BE, 元 $CB.
- Engine thoại ở bank 3 ($AB0B–$ACF7). Bảng con trỏ 213 dòng tại $9E77, bản ghi tại $A021–$AB0A: `[cờ][độ dài][addr?][byte]`.
  Cờ: $80 chờ nút rồi xóa hộp, $40 gõ từng ký tự (8 khung/ký tự), $20 nối dòng kế, $10 địa chỉ tường minh, $08 vị trí theo bảng $AD0C. Byte cuối $B3 (▼) = chờ nút.
- Mọi chữ đi qua `JSR $FF76` (xếp hàng ghi PPU, bộ đệm $0700, NMI xả tối đa 128 byte/khung; carry = đầy, engine tự thử lại khung sau). Có 5 điểm gọi trong bank 3: $AB96, $AC1B, $ACA3, $ACD9, $ACE7.
- Đổi bank qua `$FCAA` + bảng chống bus-conflict $FF5F (8 mục); mỗi bank bắt đầu bằng byte = số bank (kiểm tra `CMP $8000`).
- RAM trống dùng được: $0491–$04FF. Vùng trống bank cố định: $C02A–$C0FF, $FF32–$FF5E.

## Thiết kế bản Việt hóa
Font kana 8×8 không chứa được dấu, nên chữ Việt là **bitmap vẽ sẵn, ghép dấu lúc build** (`tools/viet_font.py`, ô 12 hàng, độ rộng tỉ lệ) rồi nạp vào 68 tile "pool" của font kana:
1. ROM mở rộng lên 256 KB (16 bank). Bank 7 gốc → bank 15 (cố định), bảng bus-conflict mới 16 mục ở $C02A.
2. 5 điểm `JSR $FF76` của engine được trỏ tới các trampoline ở bank cố định (`src/tramp.asm`), chúng chọn bank dữ liệu `8 + dòng/32` và gọi mã "window" (`src/window.asm`, giống hệt nhau ở bank 8–14).
3. Mỗi cột 8 px của dòng chữ = 2 tile (12 px cao); mã 6502 ghép mẫu tile (nền màu 3, chữ màu 1, viền hộp ở dòng 2), đẩy vào PPU cùng bảng tên → hiệu ứng gõ chữ, ▼, xóa dòng giữ nguyên.
4. Bản ghi bank 3 được viết lại gọn (chỉ phần đầu, byte đệm chồng lên bản ghi sau; chỉ dòng có ▼ cần byte $B3 đúng chỗ) nên vừa chỗ cũ.
5. Màn trạng thái chỉ có 1 hàng tile/dòng → dùng font phụ 8 px toàn chữ hoa (`tools/viet_font8.py`), nhãn ngắn gọn dấu: MẠNG / BẠC / CÔNG / VŨ KHÍ / BẢO VẬT.
6. Giá tiền (dòng 154–178) và chữ 元 giữ nguyên cách vẽ gốc.
7. Tiêu đề: hook vòng lặp chính bank 6 ($81C6) khi `$FD==3` (tiêu đề đang chờ) nạp 26 tile + 2 hàng bảng tên.

## Công cụ / script (thư mục `tools/`, `src/`)
| File | Việc |
|---|---|
| `dis6502.py` | Disassembler 6502 (`dis6502.py rom bank start end`) |
| `asm6502.py` | Assembler 2 lượt tự viết |
| `extract_script.py`, `jtable.py` | Giải mã bảng thoại, bảng kana |
| `viet_font.py` / `viet_font8.py` | Font Việt 12 px / 8 px |
| `vi_script.py` | Toàn bộ bản dịch (`TEXT`, `SMALL`, `TITLE`) |
| `build_rom.py` | Dựng ROM (`python3 tools/build_rom.py`) |
| `make_ips.py` | Tạo IPS |
| `src/window.asm`, `src/tramp.asm` | Mã 6502 chèn thêm |
| `emu.mjs`, `ui_test.mjs`, `state_test.mjs`, `poke_hook.mjs`, `trace.mjs`, `pputrace.mjs`, `callsites.mjs`, `pcsample.mjs`… | Công cụ headless dựa trên jsnes (ảnh chụp, trace, nạp savestate từ ROM gốc sang ROM mới) |

Dựng lại: `python3 tools/build_rom.py && python3 tools/make_ips.py rom/original.nes build/saiyuuki_vi.nes build/saiyuuki_vi.ips`.

## Quy trình đã làm
1. Đọc header, tách bank, tìm font (dump CHR), giải mã kana → bảng 213 dòng.
2. Dịch ngược engine thoại, bộ đệm PPU, đổi bank; xác định 5 điểm hook.
3. Dò RAM trống, vùng trống ROM; lập bản đồ màn hình (thoại, cửa hàng, trạng thái, banner).
4. Thiết kế font bitmap, assembler, mã hook, builder.
5. Dịch (Hán–Việt), kiểm độ rộng từng dòng, chụp màn hình emulator từng loại màn hình.
6. Màn tiêu đề; kiểm hồi quy gameplay; đóng gói IPS.

## Hạn chế đã biết
- Tên vật phẩm ở màn trạng thái là chữ hoa 8 px (kém đẹp hơn hộp thoại).
- Màn trạng thái có ngân sách 68 tile: nếu sở hữu nhiều vật phẩm dài cùng lúc có thể tranh tile (đã chia ô cố định để tránh).
- Chưa thử trên máy thật; emulator khuyến nghị: Mesen/FCEUX (mapper 2, 256 KB).
