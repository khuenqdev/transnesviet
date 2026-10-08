// Summarize differing regions between two ROMs, merged per bank: node tools/ipsmap.js a.nes b.nes [gapHex]
const fs = require('fs');
const a = fs.readFileSync(process.argv[2]), b = fs.readFileSync(process.argv[3]);
const gap = parseInt(process.argv[4] || '40', 16);
const m = []; const bank = o => Math.floor((o - 16) / 0x4000);
for (let i = 16; i < Math.min(a.length, b.length); i++) {
  if (a[i] === b[i]) continue;
  const l = m[m.length - 1];
  if (l && i - l.e <= gap && bank(i) === bank(l.s)) { l.e = i + 1; l.n++; } else m.push({ s: i, e: i + 1, n: 1 });
}
for (const r of m) { const o = r.s - 16; console.log(`bank ${bank(r.s).toString(16)} ${(0x8000 + o % 0x4000).toString(16)}-${(0x8000 + (r.e - 17) % 0x4000).toString(16)} diff ${r.n}`); }
