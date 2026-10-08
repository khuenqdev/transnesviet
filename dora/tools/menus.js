// Vietnamese menu texts in bank B (layout scripts, menu words, labels, titles, party names)
const vn = require('./vn');
const B = 11;

// E0 menu words (ptr table $8CB7): fixed slot length, text padded with spaces
const WORDS = {
  0: 'Nói', 1: 'Tìm', 2: '<dora>', 3: 'Đồ', 4: 'Tr.bị', 5: 'Hội ý', 6: 'Túi', 7: 'orami',
  8: 'Dùng', 9: 'Đưa', 0xA: 'Vứt', 0xB: 'Miy<oko>', 0xC: 'Đánh', 0xD: 'Chạy', 0xE: 'Phép', 0xF: 'Đồ', 0x10: 'Thủ',
};
// E2 status labels (ptr table $8D7E); 6 (speed) is unused -> holds party name Tera
const LABELS = { 0: 'TT', 1: 'Cấp', 2: 'HP', 3: 'MHP', 4: 'Công', 5: 'Thủ', 6: 'Tera', 7: 'Exp' };
// status values (ptr table $8E2E, 4 cells): good, hurt, badly hurt, poison, paralysed, asleep, fainted
const STATUS = { 0: 'Tốt', 1: 'Đau', 2: 'Nguy', 3: 'Độc', 4: 'Tê', 5: 'Ngủ', 6: 'Ngất' };
// warp destinations (ptr table $8E5F, 7 cells)
const PLACES = { 0: 'Enlil', 1: 'Nodon', 2: 'Urus', 3: 'Nanja', 4: 'Toro', 5: 'Nanbo', 6: 'ÁnhSáng', 7: 'Bóng' };
// E4 window titles (ptr table $8DB9); drawn on the top border: no top marks
const TITLES = { 0: ' Menu ', 1: '<dora>', 3: ' Chọn ', 4: ' Ai?  ', 5: ' Ai?  ', 11: ' B<á1>nh ', 12: ' Đi?  ' };
// single layout bytes: prefix letters inserted by EN before word/label opcodes
const PREFIX_SPACE = [0x8014, 0x801F, 0x8035, 0x8040, 0x80E9, 0x80F4,
  0x842B, 0x843A, 0x84B8, 0x84C7, 0x8545, 0x8554,
  0x8663, 0x8675, 0x8687, 0x86A0, 0x86B2, 0x86C4, 0x86D6,
  0x8704, 0x8716, 0x8728, 0x8741, 0x8753, 0x8765, 0x8777, 0x8A56, 0x8A61];
// inline layout texts: [addr, EN length, text]
const INLINE = [
  [0x800C, 1, '{9e}'],
  [0x87AA, 4, 'B<á1>nh'],
  [0x87E0, 5, ' Thôi'],
  [0x899A, 4, 'D<ù1>ng'],
  [0x89A2, 4, 'B<á1>nh'],
  [0x89EA, 4, 'D<ù1>ng'],
  [0x89F2, 4, 'B<á1>nh'],
  [0x8A31, 6, ' B<á1>nh '],
  [0x8B07, 11, ' Bánh rán: '],
  [0x8B24, 6, ' Ai?  '],
];
// party names (ptr table $8D3F); 5 cells max
const PARTY = { 2: 'Nob<ita>', 3: 'Jaian', 4: 'Suneo', 5: 'S<hizuka>', 8: 'Túi' };

const TEXTS = [WORDS, LABELS, TITLES, PARTY, STATUS, PLACES].flatMap(o => Object.values(o)).concat(INLINE.map(x => x[2])).join('\n').replace(/<[^>]*>|\{..\}/g, '');

function patchMenus(rom) {
  const rd = a => rom.rd(B, a), rd16 = a => rom.rd16(B, a);
  const slotLen = p => { let n = 0; while (rd(p + n) !== 0xFF) n++; return n; };
  const pad = (bytes, n, where) => {
    if (bytes.length > n) throw new Error(`${where}: ${bytes.length} > ${n}`);
    return bytes.concat(Array(n - bytes.length).fill(vn.SPACE));
  };
  const fill = (tab, map, what) => {
    for (const [i, s] of Object.entries(map)) {
      const p = rd16(tab + 2 * i), n = slotLen(p);
      rom.wr(B, p, pad(vn.encodeB(s, what + i), n, what + i));
    }
  };
  const words = Object.assign({}, WORDS); delete words[2];
  fill(0x8CB7, words, 'word');
  // Doraemon art: first tile in the layout prefix byte (needs a code < $E0), rest in the slot
  const dora = vn.encodeB('<dora>');
  if (dora[0] >= 0xE0) throw new Error('dora0 code must be < E0');
  rom.wr(B, 0x802A, [dora[0]]); rom.wr(B, rd16(0x8CB7 + 4), dora.slice(1));
  fill(0x8DB9, TITLES, 'title');
  fill(0x8E2E, STATUS, 'status');
  fill(0x8E5F, PLACES, 'place');
  // label 6 slot: 5 bytes + FF; Tera is written without padding
  const l6 = rd16(0x8D7E + 12);
  const labels = Object.assign({}, LABELS); delete labels[6];
  fill(0x8D7E, labels, 'label');
  const tera = vn.encodeB(LABELS[6]);
  rom.wr(B, l6, [...tera, 0xFF]);
  for (const a of PREFIX_SPACE) rom.wr(B, a, [vn.SPACE]);
  for (const [a, n, s] of INLINE) {
    const b = vn.encodeB(s, 'inline ' + a.toString(16));
    if (b.length !== n) throw new Error(`inline ${a.toString(16)} length ${b.length} != ${n}`);
    if (b.some(x => x >= 0xE0)) throw new Error(`inline ${a.toString(16)} uses code >= E0`);
    rom.wr(B, a, b);
  }
  // party names: repack idx 2-5,8 into $8D5D-$8D7C; idx 7 (Tera) -> label 6 slot
  let p = 0x8D5D;
  for (const i of [2, 3, 4, 5, 8]) {
    const b = vn.encodeB(PARTY[i], 'party' + i);
    if (b.length > 5) throw new Error('party name too long ' + PARTY[i]);
    rom.wr(B, p, [...b, 0xFF]); rom.wr(B, 0x8D3F + 2 * i, [p & 0xFF, p >> 8]); p += b.length + 1;
  }
  if (p > 0x8D7D) throw new Error('party names overflow');
  rom.wr(B, 0x8D3F + 14, [l6 & 0xFF, l6 >> 8]);
}

module.exports = { patchMenus, TEXTS };
