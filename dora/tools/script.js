// Script extraction: pointer tables, flow-following decoder for banks 2/3
const fs = require('fs');
const { JP, EN } = require('./tables');

const ARGLEN = { 0xF0: 0, 0xF1: 0, 0xF2: 1, 0xF3: 2, 0xF4: 3, 0xF5: 1, 0xF6: 1, 0xF7: 0, 0xF8: 0, 0xF9: 1, 0xFA: 0, 0xFB: 1, 0xFC: 0, 0xFD: 0, 0xFE: 0, 0xFF: 0 };
const END = new Set([0xFD, 0xFE, 0xFF]);

function bankMem(rom, bank) { return rom.slice(16 + bank * 0x4000, 16 + bank * 0x4000 + 0x4000); }
const rd16 = (m, a) => m[a - 0x8000] | (m[a - 0x8000 + 1] << 8);

// Returns list of {name, bank, addrOfPtr, target}
function pointerTables(rom) {
  const out = [];
  const m2 = bankMem(rom, 2), m3 = bankMem(rom, 3);
  for (let i = 0; i < 81; i++) out.push({ tab: 'A', i, bank: 2, at: 0x8000 + i * 2, target: rd16(m2, 0x8000 + i * 2) });
  for (let i = 0; i < 78; i++) out.push({ tab: 'B', i, bank: 2, at: 0x80A2 + i * 2, target: rd16(m2, 0x80A2 + i * 2) });
  for (let i = 0; i < 21; i++) out.push({ tab: 'C', i, bank: 2, at: 0x8143 + i * 2, target: rd16(m2, 0x8143 + i * 2) });
  out.push({ tab: 'D', i: 0, bank: 2, at: 0x816D, target: rd16(m2, 0x816D) });
  let n3 = 0; for (let i = 0; i < 5; i++) n3 += m3[i];
  for (let i = 0; i < n3; i++) out.push({ tab: 'E', i, bank: 3, at: 0x8005 + i * 2, target: rd16(m3, 0x8005 + i * 2) });
  return out;
}

// Parse instruction at addr
function parseOp(m, a) {
  const b = m[a - 0x8000];
  if (b >= 0xF0) {
    const n = ARGLEN[b]; const args = [...m.slice(a - 0x8000 + 1, a - 0x8000 + 1 + n)];
    const op = { a, b, len: 1 + n, args, targets: [] };
    const s8 = v => v < 128 ? v : v - 256;
    if (b === 0xF2) op.targets = [a + s8(args[0])];
    if (b === 0xF3) op.targets = [a + s8(args[0]), a + s8(args[1])];
    if (b === 0xF4) op.targets = [a + s8(args[1]), a + s8(args[2])];
    return op;
  }
  return { a, b, len: 1, args: [], targets: [] };
}

// Flow analysis: returns map addr->op for all reachable ops, and label set
function analyze(rom, bank, entries) {
  const m = bankMem(rom, bank); const ops = new Map(); const labels = new Set(); const work = [...entries];
  entries.forEach(e => labels.add(e));
  while (work.length) {
    let a = work.pop();
    while (a >= 0x8000 && a < 0xC000 && !ops.has(a)) {
      const op = parseOp(m, a); ops.set(a, op);
      for (const t of op.targets) { labels.add(t); work.push(t); }
      if (END.has(op.b) || op.b === 0xF2 || op.b === 0xF3 || op.b === 0xF4) break;
      a += op.len;
    }
  }
  return { ops, labels, m };
}

const CTL = { 0xF0: 'n', 0xF1: 'p', 0xF7: 'w0', 0xF8: 'w1', 0xFA: 'fa', 0xFC: 'fc', 0xFD: 'halt', 0xFE: 'end2', 0xFF: 'end' };
function opText(op, table, lab) {
  const b = op.b;
  if (b < 0xD3) return table[b] !== undefined ? table[b] : `{${b.toString(16).padStart(2, '0')}}`;
  if (b < 0xF0) return `{${b.toString(16)}}`;
  if (CTL[b]) return b === 0xF0 ? '\n' : `{${CTL[b]}}`;
  const h = v => v.toString(16).padStart(2, '0');
  if (b === 0xF2) return `{jmp ${lab(op.targets[0])}}`;
  if (b === 0xF3) return `{yesno ${lab(op.targets[0])} ${lab(op.targets[1])}}`;
  if (b === 0xF4) return `{flag ${h(op.args[0])} ${lab(op.targets[0])} ${lab(op.targets[1])}}`;
  return `{${h(b)} ${op.args.map(h).join(' ')}}`;
}

function dump(rom, table, perBank) {
  const ptrs = pointerTables(rom); let out = '';
  for (const bank of [2, 3]) {
    if (perBank) out = '';
    const ents = ptrs.filter(p => p.bank === bank);
    const { ops, labels } = analyze(rom, bank, ents.map(p => p.target));
    const lab = a => 'L' + a.toString(16);
    const names = {}; ents.forEach(p => { (names[p.target] = names[p.target] || []).push(p.tab + p.i); });
    const addrs = [...ops.keys()].sort((x, y) => x - y);
    let cur = '';
    for (const a of addrs) {
      if (labels.has(a)) { out += cur; cur = `\n#${lab(a)}${names[a] ? ' ' + names[a].join(',') : ''}\n`; }
      else if (a > 0 && !ops.has(a - 1) && ![...ops.values()].some(o => o.a < a && o.a + o.len > a)) { }
      const op = ops.get(a);
      cur += (op.b === 0xF0 && labels.has(a + 1)) ? '{n}' : opText(op, table, lab);
    }
    out += cur;
    const first = addrs[0], last = addrs[addrs.length - 1];
    out += `\n;; bank ${bank} text span ${first.toString(16)}-${last.toString(16)} ops ${addrs.length}\n`;
    const covered = new Set(); for (const o of ops.values()) for (let i = 0; i < o.len; i++) covered.add(o.a + i);
    let gs = null;
    for (let a = first; a <= last + 1; a++) {
      if (!covered.has(a) && a <= last) { if (gs === null) gs = a; }
      else if (gs !== null) {
        const m = bankMem(rom, bank); const bytes = [...m.slice(gs - 0x8000, a - 0x8000)];
        out += `;; gap ${gs.toString(16)}-${(a - 1).toString(16)}: ${bytes.map(b => b < 0xD3 ? (table[b] !== undefined ? table[b] : '{' + b.toString(16) + '}') : '{' + b.toString(16) + '}').join('')}\n`;
        gs = null;
      }
    }
    if (perBank) perBank[bank] = out;
  }
  return out;
}

module.exports = { pointerTables, analyze, parseOp, ARGLEN, bankMem };

if (require.main === module) {
  const rom = fs.readFileSync(process.argv[2]); const table = process.argv[3] === 'en' ? EN : JP;
  const pb = {};
  fs.writeFileSync(process.argv[4], dump(rom, table));
  dump(rom, table, pb);
  fs.writeFileSync(process.argv[4].replace(/\.txt$/, '_A.txt'), pb[2]);
  fs.writeFileSync(process.argv[4].replace(/\.txt$/, '_E.txt'), pb[3]);
}
