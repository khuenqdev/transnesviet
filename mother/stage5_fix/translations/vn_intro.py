# Opening story - stage 5: full tones and diacritics.
#
# The story is printed by the stage-3 text engine ($C707 typewriter, marks drawn one row above).
# Stage 5 removes the "DEC $77" in the bank-$14 caller ($9B1E), so lines are now DOUBLE-SPACED
# and every line has a free row above it for the tone marks.
#
# Layout limits (checked by mother_vi_stage5.py):
#   INTRO1: max 13 lines (text rows 4..28), max 28 columns (screen columns 2..29)
#   INTRO2: shown alone on the next screen at column 6, row 11 (max 3 lines, 24 columns)
#   Both blocks together must fit in RAM $64D0-$67FF (816 bytes, bank $19 $33CD0-$33FFF),
#   shared with the relocated naming-error message.
INTRO1 = [
    "Đầu những năm 1900, một bóng",
    "đen bao trùm một thị trấn",
    "nhỏ ở vùng quê nước Mỹ. Khi",
    "ấy, một đôi vợ chồng trẻ",
    "biến mất bí ẩn khỏi nhà.",
    "Người chồng tên là George,",
    "người vợ tên là Maria.",
    "Hai năm sau, George bỗng trở",
    "về đột ngột như lúc ra đi.",
    "Ông không kể với ai đã đi",
    "đâu, làm gì. Rồi ông lặng lẽ",
    "nghiên cứu một điều kỳ lạ.",
    "Còn Maria... không trở về.",
]
INTRO2 = [
    "80 năm đã trôi qua",
    "kể từ đó.",
]
