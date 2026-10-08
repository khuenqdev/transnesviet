// Vietnamese title screen (bank 9) and file select screen (bank C): raw nametable rows
const vn = require('./vn');
const C = 12, TB = 9;

// ---- title: text area rows of 20 cells (screen cols 6-25) at $A14F + row*20
const TITLE_D = 0xA14F;
const TITLE = [[14, 'Cuộc phản công của'], [18, '{1a} Nhấn Start {1a}']];

// ---- file menu window: 7 rows of 11 bytes (9f + 9 + 9f) at $A272; text at pos 2
const MENU_D = 0xA272, MENU_W = 11;
const MENU = { 2: 'Ti<ế1>p tục', 3: 'Chơi m<ớ1>i', 5: 'X<ó1>a', 6: 'Ch<é1>p' }; // row 1 is shown above row 2 or row 3: no marks

// ---- data box rows (16 bytes)
const BOX_TITLE = 0xA56C, BOX_LEVEL = 0xA57C, BOX_SPEEDM = 0xA58C, BOX_SPEED = 0xA59C, BOX_YESNO = 0xA5BC;

// ---- prompts: 10 defs x 4 line indices at $A793; lines 12 bytes, ptr table $A7DC (moved to free space)
const PROMPTS = ['Chọn lệnh!', 'Bản nào?', 'Tốc độ chữ?', 'Hãy xóa bớt!', 'Xóa bản nào?', 'Xóa thật à?', 'Chép từ đâu?', 'Dán vào đâu?', null];
const TEMPLATE = 'Bản số 1 bị'; // digit written at index 7 ($02C7)
const P9_LINE2 = 'hỏng rồi!!';

function patchTitle(rom) {
  const cell = (r, c) => TITLE_D + r * 20 + (c - 6);
  for (const [row, s] of TITLE) {
    const [b, t] = vn.rawTiles(s, 'title');
    if (b.length > 20) throw new Error('title too long ' + s);
    for (let c = 6; c < 26; c++) if (rom.rd(TB, cell(row - 1, c)) !== vn.SPACE) throw new Error('title mark row busy');
    const c0 = 6 + ((20 - b.length) >> 1);
    rom.wr(TB, cell(row, 6), Array(20).fill(vn.SPACE)); rom.wr(TB, cell(row, c0), b); rom.wr(TB, cell(row - 1, c0), t);
  }
}

function put(rom, bank, addr, s, maxLen, marksAddr) {
  const [b, t] = vn.rawTiles(s, s);
  if (b.length > maxLen) throw new Error(`too long (${maxLen}): ${s}`);
  if (!marksAddr && t.some(x => x !== vn.SPACE)) throw new Error('marks without mark row: ' + s);
  rom.wr(bank, addr, b); if (marksAddr) rom.wr(bank, marksAddr, t);
}

function patchFileScreen(rom) {
  const rd = a => rom.rd(C, a), sp = n => Array(n).fill(vn.SPACE);
  // menu
  for (let r = 0; r < 7; r++) if (rd(MENU_D + r * MENU_W) !== 0x9F || rd(MENU_D + r * MENU_W + 10) !== 0x9F) throw new Error('file menu layout');
  for (const r of [1, 2, 3, 4, 5, 6]) rom.wr(C, MENU_D + r * MENU_W + 1, sp(9));
  for (const [r, s] of Object.entries(MENU)) put(rom, C, MENU_D + r * MENU_W + 2, s, 8, 0);
  // data box
  rom.expect(C, BOX_TITLE, '9A 9E 9E 9E 20 20 24 3B 4E 3B 20 20');
  put(rom, C, BOX_TITLE + 6, 'Lưu ', 4);
  rom.wr(C, BOX_LEVEL + 2, sp(6)); put(rom, C, BOX_LEVEL + 2, 'C<ấ1>p', 6);
  rom.wr(C, BOX_SPEED + 2, sp(7)); rom.wr(C, BOX_SPEEDM + 2, sp(7)); put(rom, C, BOX_SPEED + 2, 'Tốc độ', 7, BOX_SPEEDM + 2);
  rom.wr(C, BOX_YESNO + 2, sp(12)); put(rom, C, BOX_YESNO + 3, 'C<ó1>', 2); put(rom, C, BOX_YESNO + 9, 'Kh<ô1>ng', 5);
  patchPrompts(rom);
}

function patchPrompts(rom) {
  rom.expect(C, 0xA7CF, 'BD DC A7 85 52 BD DD A7');
  const blank = Array(12).fill(vn.SPACE);
  const lines = [blank]; // index 0
  const idx = bytes => { const k = bytes.join(','); let i = lines.findIndex(l => l && l.join(',') === k); if (i < 0) { if (lines.length === 14) lines.push(null); i = lines.length; lines.push(bytes); } return i; };
  const line = (s, centre = true) => {
    const [b, t] = vn.rawTiles(s, s); if (b.length > 12) throw new Error('prompt too long: ' + s);
    const pad = centre ? (12 - b.length) >> 1 : 0;
    const L = [...blank], M = [...blank];
    b.forEach((x, i) => { L[pad + i] = x; }); t.forEach((x, i) => { M[pad + i] = x; });
    return [M, L];
  };
  const defs = [];
  for (const s of PROMPTS) {
    if (!s) { defs.push([0, 0, 0, 0]); continue; }
    const [m, l] = line(s); defs.push([idx(m), idx(l), 0, 0]);
  }
  // prompt 9: template line (RAM $02C0, index 14) + second line
  const [tm, tl] = line(TEMPLATE, false);
  const [m2, l2] = line(P9_LINE2);
  const d9 = [idx(tm), 14, idx(m2), idx(l2)];
  while (lines.length < 15) lines.push(blank.slice()); // make sure index 14 exists
  lines[14] = null;
  defs.push(d9);
  if (defs.length !== 10) throw new Error('prompt defs');
  // template: 12 bytes at $A8C4 (copied with index 7 = digit)
  rom.wr(C, 0xA8C4, tl);
  // storage
  const n = lines.length, tab = 0xBF6D;
  const slots = [];
  for (let a = 0xA828; a < 0xA8C4; a += 12) slots.push(a);
  slots.push(0xA8D1, 0xA7DC, 0xA7E8); // $A8D0 is read as the 13th template byte
  for (let a = tab + 2 * n; a + 12 <= 0xBFD8; a += 12) slots.push(a);
  const ptr = [];
  lines.forEach((l, i) => {
    if (i === 0) { ptr.push(0xA81C); rom.wr(C, 0xA81C, blank); return; }
    if (l === null) { ptr.push(0x02C0); return; }
    const a = slots.shift(); if (a === undefined) throw new Error('prompt line space full');
    rom.wr(C, a, l); ptr.push(a);
  });
  if (tab + 2 * n > 0xBFD8) throw new Error('prompt table overflow');
  ptr.forEach((a, i) => rom.wr(C, tab + 2 * i, [a & 0xFF, a >> 8]));
  rom.wr(C, 0xA7D0, [tab & 0xFF, tab >> 8]); rom.wr(C, 0xA7D5, [(tab + 1) & 0xFF, (tab + 1) >> 8]);
  defs.forEach((d, i) => rom.wr(C, 0xA793 + 4 * i, d));
  console.log('file prompts: lines', n, 'slots left', slots.length);
}

module.exports = {
  patchTitle, patchFileScreen,
  TEXTS: [...TITLE.map(t => t[1]), ...Object.values(MENU), 'Lưu Tốc độ', ...PROMPTS.filter(Boolean), TEMPLATE, P9_LINE2].join('\n').replace(/<[^>]*>|\{..\}/g, ''),
};
