// Print tiles as ASCII art: node tools/tileart.js rom fileOffHex tileHex...
const fs = require('fs');
const rom = fs.readFileSync(process.argv[2]); const base = parseInt(process.argv[3], 16);
const tiles = process.argv.slice(4).map(t => parseInt(t, 16));
const rows = Array(8).fill('');
for (const t of tiles) {
  const o = base + t * 16;
  for (let y = 0; y < 8; y++) {
    let s = '';
    for (let x = 0; x < 8; x++) { const b = 7 - x; const v = ((rom[o + y] >> b) & 1) | (((rom[o + 8 + y] >> b) & 1) << 1); s += '.123'[v]; }
    rows[y] += s + ' ';
  }
}
console.log(tiles.map(t => t.toString(16).padStart(2, '0').padEnd(9)).join(''));
console.log(rows.join('\n'));
