#!/usr/bin/env python3
from pathlib import Path
import re, hashlib, json, shutil, subprocess, tempfile, zipfile, os, unicodedata

ROOT = Path('/mnt/data/ng2_project_ref')
BASE = ROOT / 'Ninja Gaiden II - The Dark Sword of Chaos (USA).nes'
OUTROOT = Path('/mnt/data/ng2_vietnamese_project')
OUTROOT.mkdir(parents=True, exist_ok=True)

# Clean base identity from the Spanish reference README.
EXPECTED_SHA1 = '269478947a5bc518551ab5d7b4687653006e243c'

# 26 precomposed Vietnamese glyphs. 0x66-0x7F are unused/extended glyph slots
# in the English/Spanish Alt2 text encoding and correspond to CHR tiles A6-BF.
VI_MAP = {
    'á':0x66,'à':0x67,'é':0x68,'è':0x69,'í':0x6A,'ì':0x6B,
    'ó':0x6C,'ò':0x6D,'ú':0x6E,'ù':0x6F,
    'ă':0x70,'â':0x71,'ê':0x72,'ô':0x73,'ơ':0x74,'ư':0x75,'đ':0x76,
    'ấ':0x77,'ầ':0x78,'ế':0x79,'ề':0x7A,'ố':0x7B,'ồ':0x7C,
    'ớ':0x7D,'ờ':0x7E,'ứ':0x7F,
}

# The game supports only the lowercase accented glyph set we supply. For words
# whose rare tone would need another glyph, the translation intentionally uses
# a no-tone spelling rather than a combining accent. This guarantees one 8x8
# cell per visible character and therefore fixed horizontal alignment.

T = {
'00012010': '"Jaquio đã bại trận."~86~="Đúng như ta nghĩ.~84~= Còn tên Ninja?"~84~="Hắn vẫn chưa biết gì."~86~^~A6~',
'00012075': '"Tốt.~83~Cứ theo kế hoạch."~89~^~A6~',
'00012092': '"Chuyện gì với= Ninja Rồng, thưa bệ hạ?"~84~="Không cần."~83~^"Hắn không còn ích lợi.~84~= Ít nhất là lúc này.~84~= Cứ làm đúng kế hoạch.~83~= Giờ đi đi."^"Vâng, thưa bệ hạ."~A6~',
'00012134': '"¨¨¨= Thời khắc ấy sẽ đến¨¨¨"~A6~',
'00012152': '"Khi Cổng Bóng Tối= được mở ra¨¨¨"~A6~',
'0001217F': '"Tất cả sẽ quỳ gối= trước ta¨¨¨"~A6~',
'000121A3': '"Tất cả sẽ tôn ta, Ashtar,= làm chủ nhân mới!~84~= HA,HA,HA,HA¨¨¨¨"~A6~',
'000121E7': '~A3~Na)Một năm sau~A3~Ra~87~trận chiến định mệnh~A3~Na~CB~với JAQUIO¨¨¨~A6~',
'00012222': "~A3~Va'Cuộc phiêu lưu mới bắt đầu~A3~Qa~88~của RYU HAYABUSA,~A3~La~CA~Ninja cầm~A3~QbHLong Kiếm.~A6~",
'00012277': '"Bọn chúng là ai?"~82~="Họ bảo cậu rất= giỏi."~87~~A3~NcC"Ai đấy?"~A6~',
'000122C1': '"Đến Tháp Lahja,= nếu muốn cứu cô gái."~A6~',
'000122FD': '"Ý ông là¨¨¨?"~A6~',
'0001230C': '"Phải¨¨¨ Irene.~82~= Hết thời gian, Hayabusa= ¨¨¨¨ Đi thôi."~A6~',
'0001234A': '"Nhưng ông là ai?~A6~',
'0001235C': '~A3~Mb~84~"Cái gì¨¨¨?"~A6~',
'0001236E': '~84~"Aaargh¨¨¨¨"~A6~',
'0001237C': '"Ngươi là ai?~83~= Cái gì¨¨¨~87~= Hắn đâu rồi?"~A6~',
'000123AA': '"Nhanh lên, Hayabusa. Cậu có thể= là người duy nhất hạ được chúng.~82~Nhưng không kịp nếu chậm."~A6~',
'00012411': '"¨¨¨¨= Tháp Lahja¨¨¨¨"~A6~',
'00012430': '"Ngươi phục kích ta.= Ngươi là ai?"~A6~',
'00012458': '"Ta là tộc nhân của= thế giới Hỗn Mang, dưới quyền= Hoàng đế Bóng Tối, Ashtar¨¨¨¨"~87~^"Ashtar."~82~="Cái chết của ngươi= đã cận kề,= Ninja Rồng."~A6~',
'000124F0': '"¨¨¨¨= Ashtar¨¨¨ Hoàng đế= Bóng Tối."~A6~',
'0001251C': '"Ta phải tìm Irene trước= khi quá muộn."~A6~',
'00012547': '~A4~"Ryu¨¨¨¨"~A5~~A6~',
'00012553': '"Irene, cô ổn chứ?"~A6~',
'0001256E': '"Ta thấy ngươi vẫn còn= sống, Ninja."~82~~A4~="Cái gì¨¨¨?!"~A5~~A6~',
'000125A5': '"¨¨¨¨!?"~A6~',
'000125AE': '~91~"Đỡ này!"~A6~',
'000125BC': '"Aaargh!"~A6~',
'000125C6': '"Ha, ha, thật khó mà= tin¨¨¨ rằng một kẻ yếu như ngươi= lại hạ được Jaquio."~A6~',
'00012622': '"Ngươi¨¨¨ Ashtar!~83~= Kiếm đó¨¨¨¨"~A6~',
'00012644': '"Ngươi là chiến binh= thế này sao."^~A6~',
'0001266B': '"Chết đi, Ninja."~A6~',
'0001267F': '"Noooooooo¨¨¨!"~A6~',
'0001268F': '"Cái gì¨¨¨?~82~= Ngươi là ai?"~82~^"Sao ngươi vào được đây,= đồ chuột cống?"~A6~',
'000126D9': '~A4~"Giao Kiếm và= đầu hàng. Tháp này= đã bị bao vây."~A5~~A6~',
'00012726': '"Ha,ha,ha. Muốn có= Kiếm thì phải theo ta¨¨¨= vào Mê Cung Bóng Tối."~87~^"RYU¨¨¨!"~A6~',
'0001278C': '"Irene!"~A6~',
'00012795': '"Thanh kiếm¨¨¨¨= Nó là gì?"~A6~',
'000127B2': '"Nó gọi là Kiếm Hỗn Mang,= sinh ra từ xương của Quỷ."~87~^"Giống như Long Kiếm của ngươi= được cho là từ nanh Rồng."~A6~',
'0001284B': '"Sao có thể?= Sao ông biết¨¨¨?"~A6~',
'00012873': '"Ta là Robert.= Ta thuộc Tình báo= Đặc biệt, Quân đội Mỹ."~87~^"Phải ngăn Ashtar= trước khi Kiếm đạt= toàn lực¨¨¨ bằng mọi giá."~A6~',
'00012906': '~A4~"Nhanh lên, Ryu.= Hạ Ashtar trong= mê cung ngầm."~A5~~A6~',
'0001293B': '"Hắn muốn gì?~87~= Hắn cần gì ở ta?"~A6~',
'0001296D': '"Nghe đây."="¨¨¨ Ashtar!"~88~^~A6~',
'0001298E': '"Ra đây mà đấu.~83~= Không thì cô gái sẽ chết."~A6~',
'000129BB': '~A4~"Đừng làm thế, Ryu.= Họ sẽ giết cậu!"~A5~~A6~',
'000129E3': '"Ra đây. Hay ngươi quá= hèn nhát sao!~83~= Ha,ha,ha,ha¨¨¨¨"~A6~',
'00012A27': '"Đồ quỷ.~82~= Irene, ta sẽ cứu cô."~A6~',
'00012A4B': '"Kẻ giải phóng Bóng Tối bằng= máu bất tử,~83~^"sẽ nhận được= Quyền Năng= của Tà Ác Tối Thượng."~83~^"Truyền thuyết sẽ= thành sự thật."~A6~',
'00012ADE': '"Mặt đất này sẽ chìm= trong bóng tối, và quỷ dữ= sẽ thống trị mãi mãi."~83~^"Hm,hm,hm,hm¨¨¨~83~= Ha,ha,ha,ha!"~A6~',
'00012B51': '"Ta sẽ bắt ngươi!"~A6~',
'00012B68': '"Ra đây, Ashtar!"~A6~',
'00012B80': '"Cuối cùng, tên Ninja ngu ngốc= cũng chịu đánh."~A6~',
'00012BB8': '"Bắt cô gái."~A6~',
'00012BC9': '~A4~"Ryu!"~A5~~A6~',
'00012BD2': '"Irene!"~A6~',
'00012BDB': '"Đỡ này!"~A6~',
'00012BEC': '"Ah¨¨¨ Ryu¨¨¨¨"~A6~',
'00012BFC': '"Irene¨¨¨!!"~A6~',
'00012C09': '"Ryu¨¨¨"~A6~',
'00012C12': '"Irene¨¨¨ Đừng chết."~A6~',
'00012C28': '"Ha,ha,ha,ha.~81~= Xem Kiếm Hỗn Mang= đang run lên vì khoái chí!"~A6~',
'00012C6D': '~A4~"Ôi không. Bắt Irene¨¨¨¨"~A5~~A6~',
'00012C8A': '"Aaargh¨¨¨¨"~A6~',
'00012C97': '"Lùi lại,~81~= đồ lợn đáng ghét.~83~= Ta sẽ xử ngươi= sau."~A6~',
'00012CD8': '"Robert, lo cho= Irene."~A6~',
'00012CF6': '"Ashtar!"~A6~',
'00012D00': '"Vậy tà lực trong ngươi= bắt đầu thức tỉnh rồi sao?"~83~^"Nhưng ngươi không thể= chạm vào ta với= thanh kiếm đầy thù hận.~87~Đồ ngốc!"~A6~',
'00012D8D': '"Đủ trò rồi, Ashtar.~87~= Đây là chuyện giữa= ngươi và ta."~A6~',
'00012DCD': '"Ngươi dám giao chiến= với Ashtar sao?= Ninja ngu muội."~81~^"Ta sẽ cho ngươi thấy= mình bất lực thế nào."~A6~',
'00012E39': '"¨¨¨ Aaargh¨¨¨~83~= Tà lực sắp thức tỉnh.~82~Không ai= cản nổi nữa."~A6~',
'00012E96': '"Hỡi Bóng Tối Hỗn Mang.~87~Hãy nuốt chửng thế giới= vào Đêm Tối Vĩnh Hằng¨¨¨"~A6~',
'00012EE4': '"¨¨¨¨"~A6~',
'00012EEB': '"Irene, cô ổn chứ?"~88~^~A6~',
'00012F08': '~A4~"Ryu,~84~có một bàn thờ¨¨¨~84~= phía trước¨¨¨ đâu đó¨¨¨¨~87~= Cậu phải¨¨¨ ~84~phá nó."~A5~~8A~^~A6~',
'00012F5E': '"Không thể bỏ cô= ở đây¨¨¨¨"~A6~',
'00012F7C': '~A4~"Tôi ổn.~82~= Chỉ cậu mới= làm được¨¨¨ ~82~chỉ cậu= mới ngăn được chúng."~A5~^~A4~"Đi¨¨¨¨ ~87~Nhanh."~A5~~A6~',
'00012FF1': '"Được rồi¨¨¨ tôi đi đây, Irene.~89~= Nhưng tôi sẽ trở lại= ngay khi có thể.~87~= Cố lên."~A6~',
'00013048': '"Robert, đưa Irene và= rời khỏi đây ngay."~89~~A4~="Cẩn thận."~A5~~A6~',
'00013087': '"Cậu cũng vậy.= Chăm sóc cô ấy."~A6~',
'000130AC': '"¨¨¨¨~84~= Kia."~A6~',
'000130BC': '~A4~"Hộc,hộc."~A5~~A6~',
'000130CB': '~A4~="Cô ổn chứ?= Muốn nghỉ một lúc không?"~A5~^~A6~',
'000130F9': '~A4~="Không¨¨¨¨ Tôi ổn¨¨¨¨= Cái gì¨¨¨?"~A5~~A6~',
'0001311F': '~A4~="Á! Không.= Ai đó~83~Ngươi là"=~A5~~A6~',
'00013142': '=="Tên nào¨¨¨!"~A6~',
'00013157': '"Hm,hm,hm,hm."~A6~',
'00013166': '"Ta từng đánh nhau với= thứ này rồi.~82~= Sao có thể là¨¨¨?"~A6~',
'000131A3': '"¨¨¨ Ooooh¨¨¨¨~83~= ¨¨¨ Ryu¨¨¨¨"~A6~',
'000131C1': '"Robert?!= Chuyện gì vậy?~82~ Cậu= ổn chứ?"~A6~',
'000131F1': '~A4~"Ryu¨¨¨¨~82~= Họ bắt Irene."~A5~~A6~',
'0001320F': '"¨¨¨¨!?"=~A6~',
'00013219': '~A4~"Ryu. Nếu Cổng= Bóng Tối được mở,~82~= tộc nhân từ thế giới tối= sẽ gieo hỗn loạn."~A5~^~A4~"Nhân loại sẽ diệt vong.~86~= Hm?¨¨¨ ~83~Nghe này!"~A5~~A6~',
'000132B2': '"Chúng lại đến.~82~= Và đông lắm."~A6~',
'000132F0': '~A4~"Ta sẽ ở lại cản chúng.= Ryu, cậu đi đi."~82~~A5~^"Cậu bị thương. Ta không= thể bỏ cậu một mình¨¨¨¨"~82~=~A4~"Đừng lo cho ta.= Đi đi!"~A5~~A6~',
'0001337A': '~A4~"Giờ chỉ cậu mới= phá được kế hoạch tà ác.~87~= Đi ngay!"~A5~~A6~',
'000133C2': '"¨¨¨ Ta đi.~87~= Robert¨¨¨¨"~A6~',
'000133DE': '~A4~"Đừng quên cứu cô gái.~87~= Đi¨¨¨¨ Đi mau!"~A5~~A6~',
'00013429': '"May mắn!"~A6~',
'00013436': '"Được, lũ quái vật. Đến đây= mà nhận đòn!"~82~^"Các ngươi sẽ gặp= ác mộng tồi tệ.~87~= Chẳng ai qua được= Rob Chuột Rừng!"~A6~',
'000134B4': '~A4~"Vậy¨¨¨¨ đây là cuối đường= rồi sao? ~87~Tối quá= ¨¨¨ ~87~mọi thứ đang= mờ dần."~A5~^~A4~"Ryu.~82~Hạ chúng¨¨¨ ~83~thay ta."~A5~~A6~',
'0001352B': '"Đây là đâu?~83~= ¨¨¨ Irene!"~A6~',
'0001354D': '~A4~"Ryu¨¨¨ Cẩn thận!~82~= Là hắn¨¨¨¨"~A5~~8A~^~A6~',
'00013574': '"Ai?"~82~="Lâu rồi không gặp,= Ryu Hayabusa."~A6~',
'000135A4': '"Ai đó?!!"~A6~',
'000135B5': '"Hm,hm,hm,hm¨¨¨¨"~A6~',
'000135C7': '"¨¨¨?!= Ngươi"~A6~',
'000135D7': '"JAQUIO!!"~A6~',
'000135E2': '"Ngươi sống?!"~A6~',
'000135F4': '"Không ai tiêu diệt được= Tà Lực."~88~^"Sau trận chiến của ta và ngươi,= linh hồn ấy nhập vào= thân thể ta."~A6~',
'0001365F': '~A4~"Ta đã tái sinh.= Và giờ ta có= Tà Lực Bóng Tối."~A5~~A6~',
'00013697': '"¨¨¨¨"~A6~',
'0001369E': '~A4~"Linh hồn ngươi từng diệt= chỉ là tốt thí."~A5~~88~^~A4~"Trận chiến ấy chỉ= đánh thức những= Linh Hồn Tà Ác cổ xưa."~A5~~A6~',
'0001372D': '"Kiếm Hỗn Mang hút cạn= sinh lực của ngươi.~82~Và khi= nó thức tỉnh,~88~^"Cổng Bóng Tối sẽ mở tung¨¨¨= Quỷ dữ sẽ sống lại."~A6~',
'000137DC': '"Ngươi định làm gì với= Irene?"~A6~',
'00013804': '~A4~"Sinh lực của cô ấy sẽ= dùng để gọi quỷ."~A5~~88~^~A4~"Ngươi sẽ đánh thức chúng,= còn cô ấy kéo chúng về= cõi đời."~A5~~A6~',
'0001387F': '"Ngươi nên tự hào.~82~= Hai người sẽ mở đầu= Kỷ Nguyên mới."~88~^"Kỷ Nguyên Bóng Tối= Vĩnh Hằng!"=~88~^"Hm,hm,hm,hm.= Ha,ha,ha,ha."~A6~',
'00013908': '"Nói xong chưa?~82~= Ta chán mấy bài diễn văn."^"Và ta chán NGƯƠI!"~A6~',
'00013960': '~A4~"Đấu đi, Ninja Rồng= __ kẻ cuối cùng của tộc."~A5~~87~^~A4~"Giờ hãy quyết định= Ánh Sáng hay¨¨¨= Bóng Tối sẽ là= chủ nhân thật sự!!"~A5~~A6~',
'000139EA': '"¨¨¨¨= Irene¨¨¨¨"~A6~',
'000139FC': '~A4~"¨¨¨¨= Ryu¨¨¨¨"~A5~~A6~',
'00013A0E': '"Cô ổn chứ, Irene?"~A6~',
'00013A29': '~A4~"¨¨¨ Ta phải¨¨¨~83~= phá bàn thờ này¨¨¨¨"~A5~~A6~',
'00013A5A': '"Ryu!"~82~="Thanh Kiếm! ~82~Nó đã= thức tỉnh nhờ= máu Jaquio."~A6~',
'00013AA6': '~A4~"¨¨¨¨= Ryu!!"~A5~~A6~',
'00013AB6': '"¨¨¨¨= Irene."~A6~',
'00013AC5': '"Ryu¨¨¨¨"~A6~',
'00013ACF': '"Ireeeeene!!"~A6~',
'00013ADD': '"¨¨¨ Hm¨¨¨¨"~A6~',
'00013AEA': '"NGUOI"~A6~',
'00013AF2': '"Mmmm¨¨¨¨ Urrrrgh¨¨¨¨"~A6~',
'00013B09': '"Cái gì¨¨¨¨"~A6~',
'00013B18': '"Hộc¨¨¨ hộc.~87~= Đây cuối cùng là= kết thúc sao?"~A6~',
'00013B4E': '"Đấu thế nào với= kẻ địch này?"~A6~',
'00013B6F': '"Cha.~83~= Long Kiếm của tộc Rồng.~83~= Xin cho con sức mạnh."~A6~',
'00013BA9': '"Quỷ! Ngươi là của ta.= Nếm sức mạnh thật sự= của Long Kiếm!"~A6~',
'00015910': '"Irene¨¨¨¨~85~= Ireeeeene!!"~A6~',
'0001592A': '"Uhhhhh.~85~= Uuuuuuooohhh!"~A6~',
'00015944': '"Irene¨¨¨ Ta xin lỗi."~A6~',
'0001595D': '~A4~"Tộc ta¨¨¨ đánh bại= quỷ dữ¨¨¨ ~87~nhưng chẳng= còn nghĩa lý gì¨¨¨ ~8B~giờ cô đã ra đi¨¨¨¨"~A5~~A6~',
'000159B8': '~A4~"Gì¨¨¨¨?~A5~~82~~A4~= Kiếm!"~A5~~A6~',
'000159D3': '"Long Kiếm¨¨¨¨"~A6~',
'000159EA': '"¨¨¨¨"~A6~',
'000159F1': '"¨¨¨?"~A6~',
'000159F8': '"Cái gì¨¨¨¨"~A6~',
'00015A07': '"Mmm¨¨¨ ~83~ờ¨¨¨¨"~87~="¨¨¨¨?!!!~83~= Irene!"~A6~',
'00015A2D': '~A4~"Ryu?~87~= Ôi, Ryu!"~A5~~A6~',
'00015A44': '~A4~"Kỳ diệu quá!~8A~= ¨¨¨ Irene."~A5~~A6~',
'00015A65': '~A4~"Ryu. Chuyện gì= xảy ra với tôi? ~87~Tôi thấy= như mơ rất lâu= ¨¨¨ trong giấc mơ."~A5~~A6~',
'00015AC1': '~A4~"Không sao¨¨¨ ~83~Hết rồi.~83~Mọi thứ xong rồi, Irene.~83~= Bóng Tối đã biến mất."~A5~~A6~',
'00015B11': '"Ôi, Ryu. Vậy¨¨¨ ~83~là thật.~87~= Chuyện về¨¨¨~83~= anh và em¨¨¨ ~83~đúng không?"~83~="Đúng, Irene."~8F~^"Nhìn này.~83~Thấy thế giới của chúng ta= đẹp biết bao không, Irene? ~83~Nó sẽ= mãi như thế này¨¨¨ ~83~mãi mãi."~A6~',
}

# Additional non-story blocks: keep English labels/titles per the standing rules.
T_ALT = {
'000085A6': 'PRESENTS',
'000085B7': 'PRESENTS',
}


def check_base():
    data = BASE.read_bytes()
    got = hashlib.sha1(data).hexdigest()
    if got != EXPECTED_SHA1:
        raise SystemExit(f'Base ROM SHA1 mismatch: {got}')


def parse_ext(path):
    entries=[]; current=None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('@'):
            current=line.strip()
        elif line.startswith(';') and '{' in line:
            m=re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
            if m:
                entries.append({'addr':m.group(1),'src':m.group(2),'src_bytes':int(m.group(3)),'cap':int(m.group(4)),'range':current})
    return entries


def encode_text(s):
    # Controls are encoded with ~HH~, while '=' and '^' are control punctuation
    # represented by the original TBL mapping. ¨ is a literal accent/delay glyph
    # in the original ext representation and maps to the game's filler byte.
    out=bytearray()
    i=0
    special={'=':0x5C,'^':0x5D,'¨':0x65}
    # The punctuation/letters are based on the Alt2 TBL.  We only need text bytes
    # that actually occur in our translation.
    up={chr(ord('A')+i):0x01+i for i in range(26)}
    lo={chr(ord('a')+i):0x21+i for i in range(26)}
    punc={' ':0x3F,'!':0x41,'"':0x42,"'":0x45,',':0x4C,'-':0x4D,'.':0x4E,'/':0x4F,':':0x5A,'?':0x5F,'&':0x46,'%':0x47,'(':0x48,')':0x49,'*':0x4A,'+':0x4B,'$':0x44,'[':0x1B,']':0x1D,'<':0x5C,'>':0x5E,'=':0x5C}
    while i<len(s):
        if s[i]=='~':
            j=s.find('~',i+1)
            if j<0: raise ValueError(f'bad token at {s[i:]}')
            tok=s[i+1:j]
            if tok.startswith('0x'): tok=tok[2:]
            b=int(tok,16)
            out.append(b); i=j+1; continue
        ch=s[i]
        if ch in special:
            out.append(special[ch])
        elif ch in up:
            out.append(up[ch])
        elif ch in lo:
            out.append(lo[ch])
        elif ch in punc:
            out.append(punc[ch])
        elif ch in VI_MAP:
            out.append(VI_MAP[ch])
        elif ch=='Đ':
            out.append(up['D'])
        elif ch=='đ':
            out.append(VI_MAP['đ'])
        elif ch=='_':
            out.append(0x63)
        else:
            # Rare Vietnamese tone combinations not allocated a dedicated tile are
            # rendered without the tone rather than using a combining mark. This is
            # deliberate: a combining accent would consume an extra fixed-width cell
            # and cause the misalignment problem the project is designed to avoid.
            base = unicodedata.normalize('NFD', ch)
            base = ''.join(c for c in base if unicodedata.category(c) != 'Mn')
            if len(base)==1 and base in up:
                out.append(up[base])
            elif len(base)==1 and base in lo:
                out.append(lo[base])
            else:
                raise ValueError(f'No mapping for {ch!r}')
        i+=1
    return bytes(out)


def validate_translations(src_entries, trans):
    max_seen=0
    bad=[]
    used=set()
    for e in src_entries:
        if e['addr'] not in trans:
            if int(e['addr'],16) >= 0x15BD1:
                continue
            bad.append(('missing',e['addr'],e['src']))
            continue
        try:
            enc=encode_text(trans[e['addr']])
        except Exception as ex:
            bad.append(('encode',e['addr'],str(ex))); continue
        used.update(set(ch for ch in trans[e['addr']] if ch in VI_MAP))
        if len(enc)>e['cap']:
            bad.append(('overflow',e['addr'],len(enc),e['cap'],trans[e['addr']]))
        max_seen=max(max_seen,len(enc)/max(1,e['cap']))
    print('entries',len(src_entries),'translated',sum(1 for e in src_entries if e['addr'] in trans),'max use ratio',round(max_seen,3))
    print('unique Vietnamese glyphs:', ''.join(sorted(used)), len(used))
    if bad:
        for x in bad[:20]: print(x)
        raise SystemExit(f'Validation failed: {len(bad)} issues')


def write_vn_ext(src_path, out_path, trans):
    out=[]
    for line in src_path.read_text(encoding='utf-8').splitlines():
        if line.startswith(';') and '{' in line:
            m=re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
            if m:
                addr=m.group(1); cap=int(m.group(4))
                if addr in trans:
                    out.append(f';{addr}{{{m.group(2)}}}# {m.group(3)}#{cap}'.replace('# ','#'))
                    out.append(trans[addr]+f'#{cap}')
                    continue
        if line.startswith('"') or line.startswith('~') or line.startswith('=='):
            # active line: detect first address by previous comment isn't handy;
            # rebuild later from comment lines; skip existing active lines here.
            if out and out[-1].startswith(';') and re.match(r';[0-9A-F]+\{',out[-1]):
                continue
        # Keep range and separators, but not the old active lines.
        if line.startswith('|') or line.startswith('@') or line.startswith(';'):
            out.append(line)
        elif line.strip()=='' and (not out or out[-1] != ''):
            out.append('')
    # Remove duplicate original active lines left by generic branch and ensure only one per comment.
    cleaned=[]
    skip_next_active=False
    last_comment_addr=None
    for line in out:
        if line.startswith(';') and '{' in line:
            m=re.match(r';([0-9A-F]+)\{',line); last_comment_addr=m.group(1) if m else None
            cleaned.append(line); skip_next_active=False
        elif last_comment_addr and (line.startswith('"') or line.startswith('~') or line.startswith('==')):
            # Replace/ignore if not our translated active line. We already inserted ours immediately
            # after the comment, so any later source active line is discarded.
            if skip_next_active:
                continue
            # Find whether previous line after comment is the translated one; source active is next.
            if len(cleaned)>=1 and cleaned[-1].startswith(';'):
                if last_comment_addr in trans:
                    skip_next_active=True
                    continue
                cleaned.append(line)
            else:
                cleaned.append(line)
        else:
            cleaned.append(line); last_comment_addr=None
    # The above gets cumbersome; instead rebuild deterministically from original source.
    src=src_path.read_text(encoding='utf-8').splitlines(); out=[]; current_addr=None; source_active=False
    for line in src:
        if line.startswith(';') and '{' in line:
            m=re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)',line)
            if m:
                current_addr=m.group(1); cap=int(m.group(4)); out.append(line); source_active=True; continue
        if source_active and (line.startswith('"') or line.startswith('~') or line.startswith('==')):
            if current_addr in trans:
                out.append(trans[current_addr]+f'#{cap}')
            else:
                out.append(line)
            source_active=False; continue
        if line.startswith('@') or line.startswith('|') or line.startswith('#') or line.startswith(';'):
            out.append(line)
        elif not line.strip():
            out.append(line)
        else:
            out.append(line)
    out_path.write_text('\n'.join(out)+'\n',encoding='utf-8')


def main():
    check_base()
    src=ROOT/'ninjagaideniithedarkswordofchaosnesAlt2.ext'
    entries=parse_ext(src)
    validate_translations(entries,T)
    outroot=OUTROOT/'text'; outroot.mkdir(exist_ok=True)
    write_vn_ext(src,outroot/'vi_ninjagaideniithedarkswordofchaosnesAlt2.ext',T)
    # Keep Alt and Alt3 unchanged, as English UI/title labels are deliberately retained.
    for name in ['ninjagaideniithedarkswordofchaosnes.ext','ninjagaideniithedarkswordofchaosnesAlt.ext','ninjagaideniithedarkswordofchaosnesAlt3.ext']:
        shutil.copy2(ROOT/name,outroot/name.replace('.ext','_VI_BASE.ext'))
    print('Wrote',outroot)

if __name__=='__main__': main()
