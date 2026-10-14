# Metal Gunslinger (GBA) – Việt hóa
## Giai đoạn 3: Dịch toàn bộ kịch bản cốt truyện, hướng dẫn & credits

### 1. Kết quả
| Mục | Kết quả |
|---|---|
| Thoại/văn bản đã dịch | **630/630 khung thoại = 1.270 dòng màn hình** (148 cảnh): mở đầu, toàn bộ cốt truyện, hướng dẫn (tutorial), staff credits, thông báo nhận chip/huy hiệu |
| Menu (GĐ2) | 70/70 – đã gộp vào cùng bản build |
| Kiểm chứng | Đọc lại 1.270 dòng qua chính opcode `0x29` của game → **0 thiếu glyph, 0 sai lệch** so với bản dịch |
| Cặp ký tự (font) | 1.405 cặp đã dùng · còn 4.325 slot trống |
| Dung lượng chèn | Kịch bản 32 KB tại `0x79AA00+` · menu 2,5 KB tại `0x6BDBB0+` |
| Patch | `MetalGunslinger_VI_stage3.ips` (83 KB) – **thay thế patch GĐ2** (đã bao gồm menu), apply → khớp từng byte |
| ROM sau patch (MD5) | `ba2fec865a77cdfa530487d81b0f2355` |

### 2. Kỹ thuật
- **Nhóm thoại:** các lệnh `0x29` liên tiếp kết thúc bằng `0x2A` (hiện khung & chờ) hoặc `0x69` (dòng mở đầu/credits) = 1 khung thoại → `tools/group_messages.py` → `messages.json`.
- **Ngắt dòng tự động:** mỗi đoạn thoại (bắt đầu bằng 「/『) được ngắt dòng cân đối trong **≤ số dòng gốc**, tối đa 38 ký tự/dòng (= 19 ô 12 px, đúng độ rộng tối đa bản Nhật), dòng tiếp theo thụt 1 khoảng như bản gốc. Dòng thừa → để trống (chuỗi " "). **Không sửa bytecode**, chỉ đổi toán hạng của `0x29`.
- **Hướng dẫn / credits / mở đầu:** dịch theo từng dòng, giữ đúng số dòng.
- **Sửa font:** dấu hỏi (ả) trên chữ HOA trước đây giống dấu sắc → đã vẽ lại (Ả, Ẻ, Ủ, Ể, Ẩ…).

### 3. Quy ước dịch
| Nhân vật | Xưng hô |
|---|---|
| Billy ↔ Mabel / Doc | tớ – cậu |
| Fay ↔ Billy/Mabel/Doc | chị – em |
| Hawk → Billy | tôi/ta – cậu; Billy → *anh Hawk* |
| Mapiya (giọng máy, katakana) | **CHỮ IN HOA** để giữ chất "máy móc" |
| Sun Dance (nói ngắt quãng) | giữ lối nói cụt, có dấu phẩy: *"Bên kia, nối với, Gold Mountain."* |
| Babag (katakana xen kẽ) | IN HOA một vài từ |
| Myna Myna | tao – mày, "đại gia đây", "nhóc" |
| Ác nhân (Sam, Dalton, Perla Negra) | ta – ngươi / các ngươi |

Thuật ngữ: Speeder Horse, Killer Edge, Shooter giữ nguyên; tên chip/huy hiệu giữ tiếng Anh (Jack, Bear, Zett, Eagle, Serpent, Dragon, Wyatt, Double); tên staff Latin hóa theo thứ tự Tên – Họ.
> Một vài cách đọc tên staff (桜井巌雪, 渡辺明寿, 沼田出穂, 高橋登也, 高橋易史) là phỏng đoán – nên đối chiếu nếu cần chính xác.

### 4. Cần kiểm tra trên emulator
1. Khung thoại: chữ có tràn mép phải không (đặc biệt dòng 36–38 ký tự).
2. Dòng trống ở cuối khung (khi bản Việt ngắn hơn) có gây khoảng chờ lạ không.
3. Màn mở đầu & credits: vị trí căn lề.
4. Tutorial (cảnh 45).

### 5. Build lại
```bash
cd output
python ../tools/build_vi.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt mgs_vi.gba --check   # chỉ kiểm tra
python ../tools/build_vi.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt mgs_vi.gba
python ../tools/preview_story.py mgs_vi.gba preview_story.png T0001 T0039 T0616
python ../tools/ips.py create ../metal_gunslinger.gba mgs_vi.gba MetalGunslinger_VI.ips
```
Sửa bản dịch: chỉnh `story_vi.txt` (hoặc 4 file `story_vi_part*.txt`), mỗi dòng `Txxxx | đoạn / đoạn…`.

### 6. File mới / cập nhật
**tools/** `group_messages.py`, `build_vi.py` (builder đầy đủ menu + kịch bản, kiểm tra tràn dòng/thiếu glyph), `preview_story.py` (kiểm chứng + mô phỏng khung thoại), `vi_font.py` (đã sửa dấu chữ hoa) + công cụ GĐ1–2.
**output/** `MetalGunslinger_VI_stage3.ips`, `story_vi.txt` + `story_vi_part1-4.txt`, `messages.json`, `messages_jp.txt` (kịch bản Nhật theo khung), `story_layout.json`, `pair_table.json`, `preview_story.png`, `preview_menu.png`, `vi_font_chart.png`, `script_master.csv` (cột `vi_text` đã điền; dòng trống = dòng đệm khi bản Việt ngắn hơn).

### 7. Tiếp theo – Giai đoạn 4
Đồ họa chữ: logo/màn hình tiêu đề, nhãn tên nhân vật trong khung thoại, tên màn, các mục menu dạng hình (START, OPTION, nút…).
