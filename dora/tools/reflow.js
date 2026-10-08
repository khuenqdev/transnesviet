// Re-wrap pages that contain lines wider than W: node tools/reflow.js file [width]
const fs = require('fs');
const f = process.argv[2], W = +(process.argv[3] || 15);
const MACW = { d3: 5, e8: 7, e9: 7, ea: 10, eb: 10, ec: 5, ed: 5 };
const vis = s => [...s.replace(/\{(\w+)[^}]*\}/g, (m, k) => '#'.repeat(MACW[k] || 0)).normalize('NFC')].length;
const lines = fs.readFileSync(f, 'utf8').split(/\r?\n/);
const out = [];
let inB = false, i = 0;
const isStart = l => l.startsWith('#') || l.startsWith('{') || l.trim() === '';
while (i < lines.length) {
  let l = lines[i];
  // page: this line + following non-start lines
  let j = i + 1;
  if (!l.startsWith('#')) while (j < lines.length && !isStart(lines[j])) j++;
  const page = lines.slice(i, j);
  i = j;
  if (page.length === 1 && page[0].startsWith('#')) {
    const r = page[0].split(/\s+/)[1];
    if (r) inB = r[0] === 'B';
    out.push(page[0]); continue;
  }
  if (inB) { out.push(...page); continue; }
  const m = page[0].match(/^((?:\{[^}]*\})*)(.*)$/);
  const prefix = m[1];
  const body = [m[2], ...page.slice(1)];
  const last = body[body.length - 1].match(/^(.*?)((?:\{[^}]*\})*)$/);
  const suffix = last[2];
  body[body.length - 1] = last[1];
  // skip B-table (battle) sections: width detection by marker comments not available; only fix if long
  if (!body.some(b => vis(b) > W) || /\{(p|fa|w0|w1|jmp|yesno|flag|end)/.test(body.join(''))) { out.push(...page); continue; }
  const words = body.join(' ').split(/ +/).filter(Boolean);
  const res = [];
  let cur = '';
  for (const w of words) {
    if (!cur) cur = w;
    else if (vis(cur) + 1 + vis(w) <= W) cur += ' ' + w;
    else { res.push(cur); cur = w; }
  }
  if (cur) res.push(cur);
  if (res.length > 3 || res.some(r => vis(r) > W)) console.log(`MANUAL ${f}: ${body.join(' / ')}`);
  res[0] = prefix + res[0];
  res[res.length - 1] += suffix;
  out.push(...res);
}
fs.writeFileSync(f, out.join('\n'), 'utf8');
