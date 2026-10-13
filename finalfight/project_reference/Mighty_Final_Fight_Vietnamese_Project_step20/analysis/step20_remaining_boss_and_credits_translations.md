# Step 20 — Remaining boss dialogue and credits

This cumulative build preserves the user-confirmed Step 17 font/bank fix, Step 18 opening sequence, and Step 19 initial Thrasher dialogue. It translates the remaining indexed boss lines and all five credits records. BOSS_09 and BOSS_10 have their visible grunt letters localized, while their punctuation and FB/FA/F9 animation commands remain byte-identical.

## Localized nonverbal lines

- **BOSS_09:** ÁÁÁÁÁÁÁ! (the original 0x76 punctuation and FB/FA/F9 animation bytes are preserved)
- **BOSS_10:** ÁÁÁÁÁÁÁ! (the original 0x76 punctuation and FB/FA/F9 animation bytes are preserved)

## Remaining boss translations

- **BOSS_11:** TA CAO TAY!
- **BOSS_12:** NGƯƠI MẠNH HƠN
- **BOSS_13:** TA NGHĨ.
- **BOSS_14:** SAO KHÔNG VÀO BĂNG TA?
- **BOSS_15:** NGƯƠI DÁM BÁC BỎ MAD GEAR
- **BOSS_16:** BĂNG!
- **BOSS_17:** HA HA! TA KHÔNG TIN
- **BOSS_18:** NGƯƠI. ĐÚNG LÀ THẰNG
- **BOSS_19:** CẬU ẤM!
- **BOSS_20:** NGƯƠI QUÁ MẬP, CHẬM CHẠP
- **BOSS_21:** KHÓ ĐẤU TA
- **BOSS_22:** NHÓC, NGƯƠI ĐÂU PHẢI
- **BOSS_23:** SAMURAI!
- **BOSS_24:** JESSICA ĐÂU RỒI
- **BOSS_25:** MỒM TO, KIẾM NGẮN.
- **BOSS_26:** KHAI MAU, BIẾT GÌ?
- **BOSS_27:** TA SẼ ĐẬP NGƯƠI!
- **BOSS_28:** NGƯƠI CHẲNG ĐỊCH NỔI TA
- **BOSS_30:** TA LÀ VUA ĐẤU VẬT.
- **BOSS_31:** TRÁNH LỐI TA TRƯỚC KHI TA
- **BOSS_32:** DẬP BẸP NGƯƠI!
- **BOSS_33:** CÒN LẢM NHẢM À?
- **BOSS_34:** CÁI MỒM KIA!
- **BOSS_35:** TỐT, TA SẼ XẺ
- **BOSS_36:** RA THÀNH MẢNH!
- **BOSS_37:** TA LÀ ABIGAIL, MẠNH NHẤT
- **BOSS_39:** ĐẤU SĨ BĂNG MAD GEAR.
- **BOSS_40:** NGƯƠI MAY MẮN LẮM...
- **BOSS_41:** VẬN MAY NGƯƠI SẮP HẾT
- **BOSS_42:** RỒI!
- **BOSS_43:** BỌN KIA MẠNH HƠN
- **BOSS_44:** NGƯƠI, ĐỒ NGỐC!
- **BOSS_45:** TA SẼ NHỒI MẤY CÂU NÓI
- **BOSS_46:** XUỐNG HỌNG NGƯƠI!
- **BOSS_47:** JESSICA ĐÃ BỊ ĐƯA
- **BOSS_48:** TỚI SÀO HUYỆT BÍ MẬT BỌN TA
- **BOSS_49:** TA SẼ TRẢ MỐI HẬN CHO
- **BOSS_50:** ANH TA!
- **BOSS_51:** TRÔNG NGƯƠI CÓ VẺ MỆT.
- **BOSS_52:** NÀY, UỐNG NƯỚC ĐI.
- **BOSS_53:** TA THẤY KHỎE RA
- **BOSS_54:** VÀ RẤT MẠNH.
- **BOSS_55:** NGƯƠI DÁM CHÊ QUÀ TA!
- **BOSS_56:** NGƯƠI ĐÃ XÚC PHẠM TA
- **BOSS_57:** VÌ THẾ NGƯƠI PHẢI
- **BOSS_58:** TIÊU DIỆT!
- **BOSS_59:** SẴN RỒI
- **BOSS_60:** TRẬN CUỐI TA SẼ THẮNG!
- **BOSS_61:** TA YÊU JESSICA. GIAO NÀNG
- **BOSS_62:** TA!
- **BOSS_63:** NGƯƠI LÀ TRÙM À?
- **BOSS_64:** HA! TA TÌM THẤY NGƯƠI RỒI!
- **BOSS_65:** THẢ CON GÁI TA RA
- **BOSS_66:** ĐỒ HẠ TIỆN!
- **BOSS_67:** BÌNH TĨNH. JESSICA LÀ KHÁCH
- **BOSS_68:** QUÝ.
- **BOSS_69:** NÀNG TRONG PHÒNG KẾ BÊN.
- **BOSS_70:** TA VÀ JESSICA SẼ
- **BOSS_71:** CƯỚI NHAU NGÀY MAI
- **BOSS_72:** HA HA HA!
- **BOSS_73:** HÃY BẮT ĐẦU
- **BOSS_74:** TRẬN CUỐI!
- **BOSS_75:** NGƯƠI CHẲNG ĐỊCH NỔI TA
- **BOSS_76:** SẴN RỒI
- **BOSS_77:** TỚI ĐÂY LÀ HẾT, NGƯƠI!

## Credits

- **CREDIT_00:**     NHÂN VIÊN
- **CREDIT_01:** LẬP KẾ HOẠCH / K.O / LẬP TRÌNH / CHIPS, EACUM, NIWANO / THIẾT KẾ VẬT THỂ / ARASHI.KAI / TSUBO PI / ZENDEN
- **CREDIT_02:** THIẾT KẾ CUỘN / YUKI, LINDA / RYUGO, ARNIE / MAMIMU
- **CREDIT_03:** NHẠC / SETSUO, YUKO / CẢM ƠN ĐẶC BIỆT / MANASHI, USHI / BLACK.I / PROFESSOR.K / VÀ TOÀN THỂ NHÂN VIÊN / CAPCOM
- **CREDIT_04:** CẢM ƠN / BẠN ĐÃ CHƠI / TRÌNH BÀY / CAPCOM

All text is constrained to original slots; no pointers are relocated. Extended codes $80-$8F are not emitted by the new boss/credit batch because their runtime routing was only confirmed in the opening path.
