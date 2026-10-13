# Step 18 FCEUX test instructions

1. Open `Mighty_Final_Fight_Vietnamese_OPENING_SEQUENCE_STEP18.nes` directly in FCEUX from a fresh power-on/reset. Do not apply the IPS to Step 17 or any other modified ROM. Alternatively, apply the combined Step 18 IPS to the matching clean `Mighty Final Fight (USA).nes` ROM.
2. Let the opening story play through. Step 17's bank/font fix was already confirmed by the user, but the six newly translated records have not yet been observed in an emulator.
3. Check these new records in order:
   - `OPEN_01`: `TA KHÔNG NGỜ MÌNH` / `ĐÃ YÊU CÔ ẤY.` / `CÔ ẤY SẼ THUỘC` / `VỀ TA.....`
   - `OPEN_02`: `VÀI NGÀY SAU...`
   - `OPEN_03`: begins `CÁI GÌ?! JESSICA...` and ends `SAO, GUY?`
   - `OPEN_04`: `ĐÚNG. KHÔNG CÒN` / `THỜI GIAN ĐÂU.` / `ĐI THÔI!`
   - `OPEN_05`: begins `BỐ, CUỐI CÙNG` and ends `Ồ, HAY LẮM, BỐ!`
   - `OPEN_06`: begins `BUÔNG TÔI RA, GUY!` and ends `BUÔNG TÔI RA!`
4. Pay attention to high-byte glyphs such as `Ờ`, `Ở`, `Ừ`, `Ử`, `Ứ`, and transitions between records.
5. After the opening narration, continue into the next scene and check for crashes or unrelated tile changes.

The contact-sheet preview is generated from the dumped 8x8 tiles and is not a capture from FCEUX. If any issue appears, report the record ID, the visible line, and what the glyph looks like.
