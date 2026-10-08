// Vietnamese item / enemy names (bank B) and repacking
const vn = require('./vn');
const B = 11;

// items $8EB9 (128 ptrs). '' = empty. Icons: {90} weapon, {91} armor, {92} accessory
const ITEMS = [
  'Găng đấm', 'Súng Ataru', 'Súng cười', 'Súng xung', 'Ống lốc', 'Súng hơi', 'Đại pháo', 'Hút Ruột',
  'Đèn nhỏ', 'Búp bê', 'Dừng giờ', 'Dây cót', 'Pin mạnh', 'Tia chớp', 'Áo né', 'Ô an toàn',
  'Kem ngược', 'Tàng hình', 'Hút ngủ', 'Phân thân', 'Máy chắn', 'Túi y tế', 'Cơm hộp', 'Búa chiến',
  'Bom hồi', 'Bùa trừ tà', 'Cửa thần kỳ', 'Thạch dịch', 'Đèn Tekio', 'Tàu ngầm', 'Khăn trùm', 'Hố thần',
  'Máy TG', 'Rêu sáng', 'Chong chóng', 'Xe Buggy', 'Găng khéo', 'Dẫn lối', 'Tên bạc', 'Bạc',
  'Xương', 'Chìa hầm', 'Vé lên tàu', 'Cờ trắng', 'Thư tiến cử', 'Mắt Pha Lê', 'Pha lê dẫn', 'Lính nhựa',
  '', '', 'Lá thư', 'Chìa đền', 'Cỏ thuốc đỏ', 'Quạt thần', 'Ngọc bạc', 'Dao{90}',
  'Búa Piko{90}', 'Kiếm phép{90}', 'Súng nước{90}', 'Kiếm Long{90}', 'Dao ngọc{90}', 'Gươm gỉ{90}', 'Tay móc{90}', 'Kiếm kỵ sĩ{90}',
  'Gậy siêu{90}', 'Gậy quỷ{90}', 'Kiếm báu{90}', 'Diệt Long{90}', 'Giáo điện{90}', 'Súng sét{90}', 'Kiếm băng{90}', 'Kiếm lửa{90}',
  'Kiếm vàng{90}', 'Mũ vải{91}', 'Mũ sắt{91}', 'Mũ phép{91}', 'Mão Nabara{91}', 'Áo Nabara{91}', 'Mão san hô{91}', 'Mũ cướp{91}',
  'Mũ trứng{91}', 'Khiên rồng{91}', 'Giáp kỵ sĩ{91}', 'Mũ rồng{91}', 'Áo phượng{91}', 'Áo choàng{91}', 'Khiên tộc{91}', 'Áo mát{91}',
  'Áo chắn{91}', 'Da gấu{91}', 'Siêu nhân{91}', 'Chuông{92}', 'Huy hiệu{92}', 'Trâm bạc{92}', 'Răng cá{92}', 'Đồng xu{92}',
  'Huy chương{92}', 'Vòng tay{92}', 'Vỏ ốc sên{92}', 'Lông thần{92}', 'Lục lạc{92}', 'Nhẫn phép{92}', 'Vòng cổ{92}', 'Xu rồng{92}',
  'Ngọc bùa{92}', 'Cánh ngựa{92}', 'Sừng rồng{92}', 'Vuốt ưng{92}', 'Nhẫn đá{92}', 'Tên lửa', 'Dây thừng', 'Bom',
  '', 'Mic quỷ', 'Bánh rán', 'Bánh siêu', 'Bánh mega', 'Giải độc', 'Tỉnh ngủ', 'Giải tê',
  '', '', '', '', '', '', 'Trống', '',
];
// enemies $93DB (0x6F ptrs -> 12 stat bytes + name + FF)
const ENEMIES = [
  'Tsuchidama', 'Sâu gai', 'Giun', 'Dơi', 'Cây quỷ', 'Ong bọ', 'Chuột', 'Ốc sấu',
  'Khỉ quỷ', 'Nhím', 'Mắt lồi', 'Dơi sát', 'Bò điên', 'Ong độc', 'Chuột cốt', 'Sâu bụi',
  'Bóng ma', 'Nhện', 'Sên sấu', 'Khỉ ác', 'Tay mắt', 'Ác quỷ', 'Chuột cống', 'Đầu dê',
  'Quỷ 1 sao', 'Quỷ 2 sao', 'Quỷ 3 sao', 'Medusa', 'Demaon', 'Cá xác', 'Hải quỳ', 'Mực',
  'Sao biển', 'Sứa điện', 'Mực quái', 'Cá mập', 'Cá đèn', 'Cá ma', 'Quỳ nhỏ', 'Neo quỷ',
  'Lươn', 'Tàu ma', 'Cá chiến', 'Cá búa', 'Dama võ', 'Kẻ chặn', 'Lính sắt', 'Poseidon',
  'Bí ngô', 'Chuột núi', 'Chuồn cổ', 'Tí hon', 'Rồng đất', 'Nhầy', 'Dama trùm', 'Cúc đá',
  'Trứng rồng', 'Rồng con', 'Rồng non', 'Tộc Nanja', 'Tù trưởng', 'Đà điểu', 'Dơi cốt', 'Xin xỏ',
  'Chuột ma', 'Chuột dữ', 'Ruồi quỷ', 'Allosaur', 'Rồng 3 đầu', 'Bạo long', 'Nấm mốc', 'Lè lưỡi',
  'Dơi X', 'Người đá', 'Gorgosaur', 'Rồng lửa', 'Kẻ độc', 'Dama phép', 'Dama chúa', 'Dama chúa',
  'Cầu lửa', 'Tengu', 'Rắn xanh', 'Dama vua', 'Người rừng', 'Quỷ con', 'Quỷ đất', 'Tộc Bóng',
  'Cho đi!', 'Tô tem', 'Mắt đôi', 'Dơi ma', 'Đá sát', 'Ma mút', 'Chimera', 'Dama kỵ',
  'Robot', 'Chúa vàng', 'Chuột quỷ', 'Vua ma mút', 'Chimera to', 'Boro', 'Tường đá', 'Cột mắt',
  'Chúa bóng', 'GigaZombie', 'Ngân Giác', 'Kim Giác', 'Jud', 'Ngưu Ma', 'Ngưu Ma',
];
const ITEM_MAX = 11, ENEMY_MAX = 10;
const TEXTS = ITEMS.concat(ENEMIES).join('\n').replace(/\{..\}/g, '');

function patchNames(rom) {
  if (ITEMS.length !== 128 || ENEMIES.length !== 0x6F) throw new Error('name table sizes');
  const rd = a => rom.rd(B, a), rd16 = a => rom.rd16(B, a);
  // $ED70-$EDCB: old kana table in fixed bank F, unused after the $ED38 menu renderer patch
  const regions = [[0x94B9, 0x9CFB], [0x8FB9, 0x93DB], [0xBF77, 0xBFD8], [0xED70, 0xEDCC]];
  const wr = (a, bytes) => rom.wr(a >= 0xC000 ? 15 : B, a, bytes);
  const free = regions.map(r => [...r]);
  const alloc = n => {
    const r = free.find(f => f[0] + n <= f[1]);
    if (!r) throw new Error('bank B name space full, need ' + n + ' left ' + free.map(f => f[1] - f[0]).join('+'));
    const a = r[0]; r[0] += n; return a;
  };
  // read stats before overwriting
  const stats = [];
  for (let i = 0; i < 0x6F; i++) { const s = rd16(0x93DB + 2 * i); stats.push([...Array(12)].map((_, k) => rd(s + k))); }
  for (let i = 0; i < 0x6F; i++) {
    const b = vn.encodeB(ENEMIES[i], 'enemy ' + i);
    if (b.length > ENEMY_MAX) throw new Error(`enemy ${i.toString(16)} too long: ${ENEMIES[i]}`);
    const a = alloc(12 + b.length + 1);
    wr(a, [...stats[i], ...b, 0xFF]); rom.wr(B, 0x93DB + 2 * i, [a & 0xFF, a >> 8]);
  }
  const seen = new Map();
  for (let i = 0; i < 128; i++) {
    const b = vn.encodeB(ITEMS[i], 'item ' + i);
    if (b.length > ITEM_MAX) throw new Error(`item ${i.toString(16)} too long: ${ITEMS[i]}`);
    const key = b.join(',');
    let a = seen.get(key);
    if (a === undefined) { a = alloc(b.length + 1); wr(a, [...b, 0xFF]); seen.set(key, a); }
    rom.wr(B, 0x8EB9 + 2 * i, [a & 0xFF, a >> 8]);
  }
  console.log('names: bank B space left', free.map(f => f[1] - f[0]).join('+'));
}

module.exports = { patchNames, TEXTS };
