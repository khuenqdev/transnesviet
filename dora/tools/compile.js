// Script compiler: source text -> banks of bytes with pointer tables
// Source format:
//   #Label [A0,B3,...]    starts a block; refs = pointer table entries (tab letter + index)
//   text lines; a newline inside a block = F0 (newline code). Lines starting with ';' are comments.
//   {p} F1, {jmp L} F2 abs, {yesno L1 L2} F3 abs, {flag hh L1 L2} F4 abs, {f5 hh} etc raw with args,
//   {fa} {w0} {w1} {fc} {halt} {end} {end2}, {hh} raw byte, {Name} macros from MACROS
const vn = require('./vn');

const SIMPLE = { p: [0xF1], n: [0xF0], w0: [0xF7], w1: [0xF8], fa: [0xFA], fc: [0xFC], halt: [0xFD], end2: [0xFE], end: [0xFF] };
const MACROS = {};

function parseSource(src) {
  const blocks = []; let cur = null;
  const lines = src.replace(/\r/g, '').split('\n');
  for (const line of lines) {
    if (line.startsWith('#')) {
      const [label, refs] = line.slice(1).trim().split(/\s+/);
      cur = { label, refs: refs ? refs.split(',') : [], lines: [] }; blocks.push(cur); continue;
    }
    if (line.startsWith(';') || !cur) continue;
    cur.lines.push(line);
  }
  for (const b of blocks) { while (b.lines.length && b.lines[b.lines.length - 1] === '') b.lines.pop(); b.text = b.lines.join('\n'); }
  return blocks;
}

// tokenise block text into ops: {bytes, fix:[{pos,label}], term, targets}
function compileBlock(b) {
  const out = []; const fix = []; let last = null;
  const s = b.text; let i = 0; let textRun = '';
  const flush = () => { if (textRun) { out.push(...vn.encodeText(textRun, `#${b.label}: ${textRun}`)); textRun = ''; } };
  while (i < s.length) {
    const c = s[i];
    if (c === '\n') { flush(); out.push(0xF0); last = 0xF0; i++; continue; }
    if (c === '{') {
      const j = s.indexOf('}', i); if (j < 0) throw new Error('unclosed { in ' + b.label);
      flush();
      const parts = s.slice(i + 1, j).trim().split(/\s+/); const k = parts[0];
      if (SIMPLE[k]) { out.push(...SIMPLE[k]); last = SIMPLE[k][0]; }
      else if (k === 'jmp') { out.push(0xF2, 0, 0); fix.push({ pos: out.length - 2, label: parts[1] }); last = 0xF2; }
      else if (k === 'yesno') { out.push(0xF3, 0, 0, 0, 0); fix.push({ pos: out.length - 4, label: parts[1] }, { pos: out.length - 2, label: parts[2] }); last = 0xF3; }
      else if (k === 'flag') { out.push(0xF4, parseInt(parts[1], 16), 0, 0, 0, 0); fix.push({ pos: out.length - 4, label: parts[2] }, { pos: out.length - 2, label: parts[3] }); last = 0xF4; }
      else if (/^[0-9a-f]{2}$/i.test(k)) { const bytes = parts.map(h => parseInt(h, 16)).map(b => b === 0xD3 ? 0xDF : b); out.push(...bytes); last = bytes[0]; }
      else if (MACROS[k] !== undefined) { out.push(...vn.encodeText(MACROS[k])); last = null; }
      else throw new Error(`unknown code {${k}} in ${b.label}`);
      i = j + 1; continue;
    }
    textRun += c; last = null; i++;
  }
  flush();
  b.bytes = out; b.fix = fix;
  b.fallsThrough = !(last !== null && [0xF2, 0xF3, 0xF4, 0xFD, 0xFE, 0xFF].includes(last));
  b.targets = fix.map(f => f.label);
}

// Pack blocks into banks. groupBanks: list of bank numbers; header: {size, build(ptrOf) -> Buffer}
function pack(blocks, banks, headerSize) {
  const byLabel = {}; blocks.forEach((b, i) => { b.idx = i; if (byLabel[b.label]) throw new Error('dup label ' + b.label); byLabel[b.label] = b; });
  // union-find components
  const par = blocks.map((_, i) => i); const find = x => par[x] === x ? x : (par[x] = find(par[x]));
  const uni = (a, b) => { par[find(a)] = find(b); };
  blocks.forEach((b, i) => {
    if (b.fallsThrough && i + 1 < blocks.length) uni(i, i + 1);
    for (const t of b.targets) { if (!byLabel[t]) throw new Error(`undefined label ${t} in ${b.label}`); uni(i, byLabel[t].idx); }
  });
  // components in order of first block; blocks inside component keep file order
  const comps = new Map();
  blocks.forEach((b, i) => { const r = find(i); if (!comps.has(r)) comps.set(r, []); comps.get(r).push(b); });
  // fallthrough requires adjacency: component blocks placed in file order; a falling-through block's successor is in same component and next in order
  let bi = 0; let addr = 0x8000 + headerSize; const mem = banks.map(() => Buffer.alloc(0x4000, 0xFF));
  for (const comp of comps.values()) {
    const size = comp.reduce((s, b) => s + b.bytes.length, 0);
    if (size > 0x4000 - headerSize) throw new Error('component too large at ' + comp[0].label);
    if (addr + size > 0xC000) { bi++; addr = 0x8000; if (bi >= banks.length) throw new Error('out of script banks'); }
    for (const b of comp) { b.bank = bi; b.addr = addr; addr += b.bytes.length; }
  }
  for (const b of blocks) {
    for (const f of b.fix) { const t = byLabel[f.label]; if (t.bank !== b.bank) throw new Error('cross-bank jump'); b.bytes[f.pos] = t.addr & 0xFF; b.bytes[f.pos + 1] = t.addr >> 8; }
    Buffer.from(b.bytes).copy(mem[b.bank], b.addr - 0x8000);
  }
  const used = banks.map((_, i) => { const bl = blocks.filter(b => b.bank === i); return bl.length ? Math.max(...bl.map(b => b.addr + b.bytes.length)) - 0x8000 : 0; });
  return { mem, byLabel, used };
}

const encPtr = b => ((b.bank << 14) | (b.addr & 0x3FFF));

function compileGroup(src, banks, kind) {
  const blocks = parseSource(src); blocks.forEach(compileBlock);
  const refs = {}; for (const b of blocks) for (const r of b.refs) { if (refs[r]) throw new Error('dup ref ' + r); refs[r] = b; }
  const headerSize = kind === 'A' ? 0x16F : null;
  let hs = headerSize;
  if (kind === 'E') { let n = 0; while (refs['E' + n]) n++; hs = 5 + n * 2; }
  const res = pack(blocks, banks, hs);
  const h = res.mem[0];
  const put = (a, b) => { const v = encPtr(b); h[a - 0x8000] = v & 0xFF; h[a - 0x8000 + 1] = v >> 8; };
  if (kind === 'A') {
    for (let i = 0; i < 81; i++) put(0x8000 + i * 2, need(refs, 'A' + i));
    for (let i = 0; i < 78; i++) put(0x80A2 + i * 2, need(refs, 'B' + i));
    for (let i = 0; i < 21; i++) put(0x8143 + i * 2, need(refs, 'C' + i));
    put(0x816D, need(refs, 'D0'));
  } else {
    let n = 0; while (refs['E' + n]) { put(0x8005 + n * 2, refs['E' + n]); n++; }
  }
  return { ...res, blocks, headerSize: hs };
}
function need(refs, r) { if (!refs[r]) throw new Error('missing pointer ' + r); return refs[r]; }

module.exports = { parseSource, compileGroup, MACROS };
