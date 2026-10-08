// Dump bank B name tables: node tools/bankb.js rom [jp|en]
const fs = require('fs');
const { JP, EN, decode } = require('./tables');
const rom = fs.readFileSync(process.argv[2]);
const tab = process.argv[3] === 'jp' ? JP : EN;
const off = a => 16 + 11 * 0x4000 + (a - 0x8000);
const rd16 = a => rom[off(a)] | (rom[off(a) + 1] << 8);
const str = a => { const b = []; for (let i = 0; rom[off(a) + i] !== 0xFF && i < 40; i++) b.push(rom[off(a) + i]); return b; };
const show = (name, a, n, skip = 0) => {
  console.log(`== ${name} $${a.toString(16)}`);
  for (let i = 0; i < n; i++) {
    const p = rd16(a + 2 * i) + skip;
    const b = str(p);
    console.log(i.toString(16).padStart(2, '0'), p.toString(16), b.length, decode(b, tab, false), '|', b.map(x => x.toString(16)).join(' '));
  }
};
const cnt = a => (rd16(a) - a) / 2;
show('party', 0x8D3F, cnt(0x8D3F));
show('items', 0x8EB9, cnt(0x8EB9));
show('enemies', 0x93DB, cnt(0x93DB), 12);
