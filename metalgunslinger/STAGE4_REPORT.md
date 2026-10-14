# Metal Gunslinger (GBA) – Việt hóa
## Giai đoạn 4: Kiểm thử bằng emulator headless, sửa bố cục & Việt hóa nhãn tên nhân vật

### 1. Kết quả chính
| Hạng mục | Kết quả |
|---|---|
| Emulator headless tự viết (`emu/gbaemu.c`) | Chạy được ROM gốc lẫn ROM Việt hóa: intro, menu tiêu đề, hội thoại (scene 2–39, 41) |
| Giới hạn dòng thực tế | **36 ký tự** (18 ô) chứ không phải 38 – ô thứ 19 bị khung hộp thoại che |
| Dòng vượt giới hạn đã sửa | 26 câu thoại/hướng dẫn viết gọn lại; trình build kiểm tra MAXW=36 |
| Intro (scene 1) | 12 khung chữ viết lại ≤20 ký tự; cửa sổ chữ (opcode 0x67) tự căn giữa |
| Hộp chữ căn giữa (opcode 0x77) | Độ rộng tự cập nhật theo số ô tiếng Việt |
| Nhãn tên nhân vật | **14/14 nhãn** vẽ lại chữ Latin, giữ khung vàng/palette/bố cục sprite, nén lại và ghi đè tại chỗ |
| Kiểm thử emulator | 944 trang hội thoại đã chụp và duyệt – không còn dòng bị khung che |
| ROM sau patch GĐ4 (MD5) | `063ec378813c483a74b8b51831db2f18` |

### 2. Emulator headless
`emu/gbaemu.c`: ARM7TDMI (ARM + Thumb), BIOS HLE, IRQ, PPU mode 0–5, DMA, timer, phím, EEPROM, save state.
Script: `run N`, `press A 3`, `hold KEYS`, `shot f.ppm`, `save/load f.st`, `poke`, `dump`, `trace`.
Quy trình: `intro.txt` (lưu state trước hội thoại) → `run_scenes.py` (ROM nhảy scene, nhấn A, chụp) → `box_sheets.py` (bảng duyệt).

### 3. Nhãn tên (sprite)
`tools/labels.py`, `tools/label_maker.py`, `tools/gfx_insert.py` – xem chi tiết trong mã nguồn.
