// Check VN script line widths: node tools/check.js script/A_01.txt [more files]
const fs = require('fs');
const { parseSource, MACROS } = require('./compile');
const W = { A: 15, B: 23, C: 15, D: 15, E: 15 };
const MACW = { d3: 5, e8: 7, e9: 7, ea: 10, eb: 10, ec: 5, ed: 5 };
let bad = 0;
for (const f of process.argv.slice(2)) {
  const blocks = parseSource(fs.readFileSync(f, 'utf8'));
  let width = 15;
  for (const b of blocks) {
    if (b.refs.length) width = W[b.refs[0][0]];
    const text = b.text.replace(/\{(\w+)[^}]*\}/g, (m, k) => {
      if (MACROS[k] !== undefined) return MACROS[k];
      if (MACW[k]) return '#'.repeat(MACW[k]);
      if (['fa', 'w0', 'w1'].includes(k)) return '\n';
      return '';
    });
    for (const line of text.split('\n')) {
      const n = [...line.normalize('NFC')].length;
      if (n > width) { console.log(`${f} #${b.label} (${n}>${width}): ${line}`); bad++; }
    }
    const pages = b.text.replace(/\{(p|fa|w0|w1|end|end2|halt|jmp[^}]*|yesno[^}]*|flag[^}]*)\}/g, '\u0001').split('\u0001');
    for (const pg of pages) {
      const ls = pg.split('\n').filter(l => l.replace(/\{[^}]*\}/g, '').trim());
      if (ls.length > 3) { console.log(`${f} #${b.label} ${ls.length} lines: ${ls[0]}`); bad++; }
    }
  }
}
console.log(bad ? `${bad} long lines` : 'ok');
