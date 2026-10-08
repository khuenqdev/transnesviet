// Render tiles with grid + hex row/col labels (labels drawn using the digit tiles 0-9 of the same font is unreliable, so use a built-in 3x5 font)
const { writePng } = require('./png');
const DIG = {
  0: '111101101101111', 1: '010110010010111', 2: '111001111100111', 3: '111001111001111', 4: '101101111001001', 5: '111100111001111',
  6: '111100111101111', 7: '111001001001001', 8: '111101111101111', 9: '111101111001111', a: '111101111101101', b: '110101110101110',
  c: '111100100100111', d: '110101101101110', e: '111100111100111', f: '111100111100100'
};
function renderSheet(path, data, s = 4, cols = 16, first = 0) {
  const n = data.length >> 4; const rows = Math.ceil(n / cols);
  const cell = 8 * s + 2; const L = 16;
  const W = L + cols * cell, H = L + rows * cell; const img = Buffer.alloc(W * H * 4);
  const px = (x, y, r, g, b) => { if (x < 0 || y < 0 || x >= W || y >= H) return; const o = (y * W + x) * 4; img[o] = r; img[o + 1] = g; img[o + 2] = b; img[o + 3] = 255; };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) px(x, y, 60, 0, 60);
  const txt = (str, x0, y0) => { let x = x0; for (const ch of str) { const d = DIG[ch]; for (let i = 0; i < 15; i++) if (d[i] === '1') { px(x + i % 3 * 1, y0 + Math.floor(i / 3), 255, 255, 0); } x += 4; } };
  for (let c = 0; c < cols; c++) txt(c.toString(16), L + c * cell + cell / 2 - 1, 4);
  for (let r = 0; r < rows; r++) txt(((first >> 4) + r).toString(16).padStart(2, '0'), 2, L + r * cell + cell / 2 - 2);
  const G = [[0, 0, 0], [85, 85, 85], [170, 170, 170], [255, 255, 255]];
  for (let t = 0; t < n; t++) for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) {
    const v = ((data[t * 16 + y] >> (7 - x)) & 1) | (((data[t * 16 + 8 + y] >> (7 - x)) & 1) << 1);
    for (let dy = 0; dy < s; dy++) for (let dx = 0; dx < s; dx++) px(L + (t % cols) * cell + 1 + x * s + dx, L + Math.floor(t / cols) * cell + 1 + y * s + dy, ...G[v]);
  }
  writePng(path, W, H, img);
}
module.exports = { renderSheet };
if (require.main === module) {
  const fs = require('fs');
  const [file, off, len, out, scale] = process.argv.slice(2);
  const d = fs.readFileSync(file).slice(parseInt(off, 16), parseInt(off, 16) + parseInt(len, 16));
  renderSheet(out, d, +(scale || 4), 16, 0);
}
