// Vietnamese name entry screen (bank C raw nametable rows, tile = code)
const vn = require('./vn');
const C = 12;

// prompt rows (32 bytes, col 2 / 29 = border); text only on the base row -> single-tile glyphs
const PROMPTS = [
  [0x986E, 'T<ê1>n bạn?'],
  [0x98AE, 'Trai hay g<á1>i?'],
];
// option rows: words keep the EN start columns (cursor positions)
const OPTIONS = [
  [0x98CE, ['Trai', 'G<á1>i']],
  [0x992E, ['C<ó1>', 'Kh<ô1>ng']],
];
// confirm rows (boy / girl): name is drawn at cols 11-15
const CONFIRM = [[0x990E, 17, 'Được chưa?'], [0x996E, 17, 'Được chưa?']];
// character grid: 2 pages x 6 rows x 25 cols (screen cols 4-28); positions below are [grid row, screen col]
const GRID1 = 0x9A06, GRID2 = 0x9A9C, GW = 25;
const GRID_EXTRA = [[0, 18, 'ĐƠƯ'], [1, 18, 'đơư']];
const END = [1, 25, 'Xong'], PAGE = [4, 25, '   '];

function tiles(s) {
  const out = [];
  for (const part of s.split(/(<[^>]+>)/)) {
    if (!part) continue;
    if (part[0] === '<') { const t = vn.T[part.slice(1, -1)]; if (t === undefined) throw new Error('no tile ' + part); out.push(t); continue; }
    for (const ch of part.normalize('NFC')) {
      if (ch === ' ') { out.push(vn.SPACE); continue; }
      const t = vn.T[ch];
      if (t === undefined) throw new Error(`name entry: no single tile for '${ch}' in ${s}`);
      out.push(t);
    }
  }
  return out;
}

function patchNameEntry(rom) {
  const rd = a => rom.rd(C, a);
  const clear = (row, c0, c1) => rom.wr(C, row + c0, Array(c1 - c0).fill(vn.SPACE));
  for (const row of [...PROMPTS.map(p => p[0]), ...OPTIONS.map(o => o[0]), ...CONFIRM.map(c => c[0])])
    if (rd(row + 2) !== 0x9F || rd(row + 29) !== 0x9F) throw new Error('name entry row ' + row.toString(16));
  for (const [row, s] of PROMPTS) {
    const t = tiles(s); if (t.length > 19) throw new Error('prompt too long ' + s);
    clear(row, 9, 29); rom.wr(C, row + 10 + ((19 - t.length) >> 1), t);
  }
  for (const [row, words] of OPTIONS) {
    const starts = [];
    for (let c = 3; c < 29; c++) if (rd(row + c) !== vn.SPACE && rd(row + c - 1) === vn.SPACE) starts.push(c);
    if (starts.length !== words.length) throw new Error('option row ' + row.toString(16));
    clear(row, 3, 29);
    words.forEach((w, i) => rom.wr(C, row + starts[i], tiles(w)));
  }
  for (const [row, col, s] of CONFIRM) { clear(row, 16, 29); const t = tiles(s); if (col + t.length > 29) throw new Error('confirm too long'); rom.wr(C, row + col, t); }
  // grid: VN extra letters in the empty block, "End" -> Xong, kana page switch removed (page 2 = page 1)
  const cell = (r, c) => GRID1 + r * GW + (c - 4);
  for (const [r, c, s] of GRID_EXTRA) {
    for (let k = 0; k < s.length; k++) if (rd(cell(r, c) + k) !== vn.SPACE) throw new Error('grid cell busy');
    rom.wr(C, cell(r, c), tiles(s));
  }
  for (const [r, c, s] of [END, PAGE]) rom.wr(C, cell(r, c), tiles(s));
  const page = []; for (let i = 0; i < 6 * GW; i++) page.push(rd(GRID1 + i));
  rom.wr(C, GRID2, page);
}

module.exports = { patchNameEntry, TEXTS: [...PROMPTS.map(p => p[1]), ...OPTIONS.flatMap(o => o[1]), ...CONFIRM.map(c => c[2]), 'ĐƠƯđơư', 'Xong'].join('\n').replace(/<[^>]*>/g, '') };
