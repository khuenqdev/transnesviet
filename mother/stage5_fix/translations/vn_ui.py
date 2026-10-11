
# In-place UI strings (bank $00 window layouts, bank $13/$19 screens).
# Rule: same byte length AND same column count as the English string (window geometry is
# fixed).  Top marks cost a byte without a column, so they are only possible where a {rep:..}
# padding run can absorb the difference.  Window TITLES (in the border row) must be mark-free:
# a mark would be drawn over the map row above the window.
# Text that cannot be expressed under these rules keeps a mark-free Vietnamese word
# (ạ ẹ ị ọ ụ ỵ ợ ự ơ ư đ have their own glyphs and are free) or stays English.
T = {'__UI__': {
# ---- battle command window
'P00D93': '{24} Đánh{rep:A0,05}Tự  {rep:A0,04}{25}',
'P00DA6': '{24} PSI{rep:A0,06}Thủ {rep:A0,04}{25}',
'P00DB8': '{24} Đồ  {rep:A0,05}Lui{rep:A0,05}{25}',
'P00DCA': '{24} Xem  {rep:A0,0C}{25}',
'P00DDC': '{24} Xem  {rep:A0,04}Hát{rep:A0,05}{25}',
'P00E48': '{pos:0D,19}Chưa được.    ',
'P00E5A': '{pos:0D,19}Chưa được.    ',
'P00E6C': '{pos:0D,19}{Actor} chịu. ',
# ---- field Command window (no padding runs -> mark-free words)
'P011EC': '{24} Gọi   Xem  {25}\n{25}{clear}{24} Kho   Trạng{25}\n{25}{goto:A024}PSI   Chọn {25}',
'P01300': '┏{rep:DC,04}┓\n{25}{0E}{24}Ai? {25}',
# ---- window titles (border row: mark-free only)
'X011D9': ('{pos:01,01}┏▬Command{rep:DC,04}┓', '{pos:01,01}┏▬Menu▔▔▔{rep:DC,04}┓'),
'P0121D': '{25}{06}┗{rep:FC,0C}┛\n{pos:15,01}┏▔▔▬Xu▔▔▔┓\n{25}',
# ---- naming screen prompts (bank $19, same length, trailing spaces)
'P33B03': 'Cậu bé này\ntên gì?',
'P33B1C': 'Cô bé này\ntên gì?',
'P33B36': 'Cậu bé kia\ntên gì?',
'P33B4D': 'Bé cuối\ntên gì?',
'P33B63': 'Món ăn bạn\nthích nhất?',
'P33B7F': 'Hãy đổi\ntên này.',
}}
