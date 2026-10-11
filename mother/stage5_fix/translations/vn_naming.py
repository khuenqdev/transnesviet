# Name-entry screens - stage 5.
#
# Screen streams (CHR $17866-$178FF, copied to RAM $6C66-$6CFF when the naming screen opens).
# Column positions of the ◆ markers and of "Có"/"Không" must stay where the English had them,
# because the cursor sprite positions are fixed by code.  Each value is checked by
# mother_vi_stage5.py (column count per line, total size <= 154 bytes).
NAMING = {
    # "  ◆Back  ◆End  " / "   ◆Previous   "   (◆ at columns 2, 9 and 3)
    'back_end':  "  ◆Xóa   ◆Xong ",
    'previous':  "   ◆Quay lại   ",
    # "Favorite food: " (followed by the favourite-food name, starts at column 3)
    'fav_food':  "Món ưa thích: ",
    # confirmation box, 16 columns inside the border
    'is_ok':     "  Được chưa?    ",
    'yes_no':    "     Có  Không  ",          # "Yes" at col 5, "No" at col 9
    # Reserved-name error (6 lines x 15 columns, printed over the keyboard).
    # Line 5 is printed on the "Back/End" row, whose mark row is not redrawn afterwards,
    # so line 5 must contain no top marks (letters ạ ẹ ị ọ ụ ỵ ợ ự ơ ư đ are fine).
    'error': [
        "Tên này đã có  ",
        "nhân vật trong ",
        "game dùng rồi. ",
        "Hãy thử lại và ",
        "ghi IN HOA nha.",
        "               ",
    ],
}

# Keyboard grid (RAM $6470, 16-byte rows, 15 visible cells). Letters are entered exactly as
# written here. Only single-tile letters can be offered (Đ đ Ơ ơ Ư ư); letters that need a
# mark byte (á, ê ...) cannot be stored by the 1-byte-per-cell entry routine.
KEYBOARD = [
    "ABCDEFG HIJKLMN",
    "OPQRSTUĐVWXYZƠƯ",
    "abcdefg hijklmn",
    "opqrstuđvwxyzơư",
]
