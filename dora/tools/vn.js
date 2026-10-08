// Vietnamese font + encoding
// Tile layout keeps EN font: digits 00-09, '-' 0B, '!' 0C, '?' 0F, space 20, A-Z 21-3A, a-z 3B-54, '.' 93, ',' 94
const fs = require('fs');

const FONT_OFF = 0x15290; // bank5 $9280, 256 tiles -> PPU $1000
const SPACE = 0x20;

function tileFromArt(rows) {
  const t = Buffer.alloc(16);
  for (let y = 0; y < 8; y++) {
    const r = (rows[y] || '').padEnd(8, '.');
    for (let x = 0; x < 8; x++) {
      const v = r[x] === '3' ? 3 : r[x] === '1' ? 1 : r[x] === '2' ? 2 : 0;
      if (v & 1) t[y] |= 0x80 >> x;
      if (v & 2) t[8 + y] |= 0x80 >> x;
    }
  }
  return t;
}
function artFromTile(t) {
  const rows = [];
  for (let y = 0; y < 8; y++) { let s = ''; for (let x = 0; x < 8; x++) { const v = ((t[y] >> (7 - x)) & 1) | (((t[8 + y] >> (7 - x)) & 1) << 1); s += '.123'[v]; } rows.push(s); }
  return rows;
}
const A = s => s.trim().split(/\s+/);

// New plain glyphs (hand drawn)
const GLYPHS = {
  'ı': A('........ ..3..... ..3..... ..3..... ..3..... ..3..... ..3..... ........'),
  'đ': A('....3... ...333.. .3333... 3...3... 3...3... 3...3... .3333... ........'),
  'Đ': A('.33333.. .3....3. .3....3. 3333..3. .3....3. .3....3. .33333.. ........'),
  'ơ': A('.....3.. .3333... 3...3... 3...3... 3...3... 3...3... .333.... ........'),
  'ư': A('.....3.. 3...3... 3...3... 3...3... 3...3... 3...3... .333.3.. ........'),
  'Ơ': A('.3333.3. 3....33. 3....3.. 3....3.. 3....3.. 3....3.. .3333... ........'),
  'Ư': A('3....33. 3....3.. 3....3.. 3....3.. 3....3.. 3....3.. .3333... ........'),
  'ị': A('........ ..3..... ........ ..3..... ..3..... ..3..... ........ ..3.....'),
  'ỵ': A('........ 3...3... 3...3... .3333... ....3... .333.... ........ ..3.....'),
  'Ị': A('..333... ...3.... ...3.... ...3.... ..333... ........ ........ ...3....'),
  'Ỵ': A('3...3... 3...3... .333.... ..3..... ..3..... ..3..... ........ ..3.....'),
  "'": A('...3.... ...3.... ..3..... ........ ........ ........ ........ ........'),
  '"': A('.3.3.... .3.3.... ........ ........ ........ ........ ........ ........'),
  ':': A('........ ........ ..33.... ........ ........ ..33.... ........ ........'),
  '…': A('........ ........ ........ ........ ........ ........ 3.3.3... ........'),
  '(': A('...3.... ..3..... .3...... .3...... .3...... ..3..... ...3.... ........'),
  ')': A('.3...... ..3..... ...3.... ...3.... ...3.... ..3..... .3...... ........'),
  '/': A('.....3.. ....3... ....3... ...3.... ..3..... ..3..... .3...... ........'),
  '~': A('........ ........ ........ .33..3.. 3..33... ........ ........ ........'),
  '♥': A('........ .33.33.. 3333333. 3333333. .33333.. ..333... ...3.... ........'),
  '♪': A('...33... ...3.3.. ...3.... ...3.... .333.... 3333.... .33..... ........'),
  '*': A('........ ..3..... 3.3.3... .333.... 3.3.3... ..3..... ........ ........'),
  '+': A('........ ..3..... ..3..... 33333... ..3..... ..3..... ........ ........'),
  '%': A('33...3.. 33..3... ...3.... ..3..... .3..33.. 3...33.. ........ ........'),
  // precomposed single-tile glyphs for raw layouts (yes/no etc.)
  'ó1': A('...3.... ..3..... ........ .333.... 3...3... 3...3... .333.... ........'),
  'ô1': A('..3..... .3.3.... ........ .333.... 3...3... 3...3... .333.... ........'),
  'á1': A('...3.... ..3..... ........ .333.... ....3... .3333... 3...3... .3333...'),
  'ù1': A('.3...... ..3..... ........ 3...3... 3...3... 3...3... .3333... ........'),
  'ê1': A('..3..... .3.3.... ........ .333.... 3...3... 33333... 3....... .3333...'),
  'ớ1': A('...3.... ..3..... .....3.. .3333... 3...3... 3...3... .333.... ........'),
  'é1': A('...3.... ..3..... ........ .333.... 3...3... 33333... 3....... .3333...'),
  'ấ1': A('..3...3. .3.3.3.. ........ .333.... ....3... .3333... 3...3... .3333...'),
  'ế1': A('..3...3. .3.3.3.. ........ .333.... 3...3... 33333... 3....... .3333...'),
};
// glyphs always allocated; the rest only when some used char needs them
const ALWAYS = new Set(['ı', 'đ', 'Đ', 'ơ', 'ư', 'Ơ', 'Ư', 'ó1', 'ô1', 'á1', 'ù1', 'ê1', 'ớ1', 'é1', 'ấ1', 'ế1']);

// Top-row mark tiles: key = hat + tone ; hat in '', '^', '(' ; tone in '', '/', '\\', '?', '~'
const TONE_ART = {
  '/': ['...3....', '..3.....'],
  '\\': ['.3......', '..3.....'],
  '?': ['.33.....', '...3....', '..3.....'],
  '~': ['.33.3...', '3..3....'],
};
const HAT_ART = { '^': ['..3.....', '.3.3....'], '(': ['3...3...', '.333....'] };
function markArt(hat, tone) {
  const rows = Array(8).fill('........');
  if (!hat) { const t = TONE_ART[tone]; t.forEach((r, i) => rows[7 - t.length + i] = r); return rows; }
  HAT_ART[hat].forEach((r, i) => rows[5 + i] = r);
  if (tone) { const t = TONE_ART[tone]; t.forEach((r, i) => rows[4 - t.length + i] = r); }
  return rows;
}

// Tile assignment
const T = {}; // name -> tile
'0123456789'.split('').forEach((c, i) => T[c] = i);
Object.assign(T, { '-': 0x0B, '!': 0x0C, '?': 0x0F, ' ': SPACE, '.': 0x93, ',': 0x94 });
for (let i = 0; i < 26; i++) { T[String.fromCharCode(65 + i)] = 0x21 + i; T[String.fromCharCode(97 + i)] = 0x3B + i; }
// LOW tiles: code == tile (plain glyphs usable anywhere). HIGH tiles: marks only (never used as codes).
// Tiles A0-EF get overwritten in-game, so VN glyphs replace EN extra tiles 0E,10-15,55-8F.
const LOW = [0x0E, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15]; for (let t = 0x55; t <= 0x8F; t++) LOW.push(t);
const HIGH = LOW;
const tileArt = {}; // tile -> art rows
const alloc = (name, art, pool = LOW) => { if (!pool.length) throw new Error('out of tiles'); const t = pool.shift(); T[name] = t; tileArt[t] = art; return t; };

// base glyph names needed by a set of chars
function neededBases(usedCh) {
  const need = new Set();
  for (const ch of usedCh) {
    need.add(ch);
    const d = ch.normalize('NFD'); let b = d[0]; let dot = false, horn = false;
    for (const m of d.slice(1)) { if (m === '\u031B') horn = true; else if (m === '\u0323') dot = true; }
    if (horn) b = (b + '\u031B').normalize('NFC');
    if (dot) b = dotted(b);
    need.add(b);
  }
  return need;
}

function buildFontArt(enFont, usedCh) {
  const art = t => artFromTile(enFont.slice(t * 16, t * 16 + 16));
  const need = neededBases(usedCh);
  for (const k of Object.keys(GLYPHS)) if (ALWAYS.has(k) || need.has(k)) alloc(k, GLYPHS[k]);
  // dot-below variants
  const mk = (rows, del) => { const r = rows.slice(0, 7); r.splice(del, 1); r.push('........'); r[6] = '........'; r[7] = '..3.....'; return r.slice(0, 8); };
  for (const c of 'aeouơư') { if (!need.has(dotted(c))) continue; const src = GLYPHS[c] || art(T[c]); alloc(dotted(c), mk(src, 4)); }
  for (const c of 'AEOUƠƯ') { if (!need.has(dotted(c))) continue; const src = GLYPHS[c] || art(T[c]); alloc(dotted(c), mk(src, 2)); }
  // marks
  for (const hat of ['', '^', '(']) for (const tone of ['', '/', '\\', '?', '~']) { if (!hat && !tone) continue; alloc('M' + hat + tone, markArt(hat, tone), HIGH); }
  // EN "Doraemon" art (6 tiles)
  X.dora = [0x5C, 0x5D, 0x5E, 0x5F, 0x60, 0x61].map((t, i) => alloc('<dora' + i + '>', art(t)));
  for (const p of PACKS) X[p] = packText(p).map((a, i) => alloc('<' + p + i + '>', a));
}
// proportional packing of short strings into tiles (for 5-cell names)
const PACKS = ['ita', 'oko', 'hizuka'];
const X = {}; // name -> tiles (later -> codes)
function glyphArt(ch) { return GLYPHS[ch] || artFromTile(ENFONT.slice(T[ch] * 16, T[ch] * 16 + 16)); }
function packText(s) {
  const cols = [];
  for (const ch of s) {
    const a = glyphArt(ch); let lo = 8, hi = -1;
    for (const r of a) for (let x = 0; x < 8; x++) if (r[x] !== '.') { lo = Math.min(lo, x); hi = Math.max(hi, x); }
    if (cols.length) cols.push('........');
    for (let x = lo; x <= hi; x++) cols.push(a.map(r => r[x]).join(''));
  }
  const n = Math.ceil(cols.length / 8);
  if (n > 4) throw new Error('pack too wide ' + s + ' ' + cols.length);
  const tiles = [];
  for (let t = 0; t < n; t++) {
    const rows = [];
    for (let y = 0; y < 8; y++) { let r = ''; for (let x = 0; x < 8; x++) { const c = cols[t * 8 + x]; r += c ? c[y] : '.'; } rows.push(r); }
    tiles.push(rows);
  }
  return tiles;
}
let ENFONT = null;
function dotted(c) { return (c.normalize('NFD') + '\u0323').normalize('NFC'); }

// Decompose a Vietnamese character -> {base tile name, mark name or null}
const TONES = { '\u0301': '/', '\u0300': '\\', '\u0309': '?', '\u0303': '~' };
function analyzeChar(ch) {
  if (T[ch] !== undefined) return { base: ch, mark: null };
  const d = ch.normalize('NFD');
  let base = d[0], hat = '', tone = '', dot = false, horn = false;
  for (const m of d.slice(1)) {
    if (m === '\u0302') hat = '^'; else if (m === '\u0306') hat = '(';
    else if (m === '\u031B') horn = true; else if (m === '\u0323') dot = true;
    else if (TONES[m]) tone = TONES[m]; else return null;
  }
  let b = base;
  if (horn) b = (base + '\u031B').normalize('NFC');
  if (dot) b = dotted(b);
  if (!dot && (hat || tone) && base === 'i') b = 'ı';
  if (dot && base === 'i' || dot && base === 'I' || dot && /[yY]/.test(base)) { if (tone || hat) return null; }
  if (T[b] === undefined) return null;
  return { base: b, mark: hat || tone ? 'M' + hat + tone : null };
}

// Code table: plain chars use code = tile. Composites get free codes.
const LOWER_V = ['a', 'ă', 'â', 'e', 'ê', 'i', 'o', 'ô', 'ơ', 'u', 'ư', 'y'];
function allComposites() {
  const list = [];
  const tones = ['\u0301', '\u0300', '\u0309', '\u0303', '\u0323', ''];
  for (const upper of [false, true]) for (const tn of tones) for (const v of LOWER_V) {
    let c = (v.normalize('NFD') + tn).normalize('NFC'); if (upper) c = c.toUpperCase();
    list.push(c);
  }
  return list;
}
// rare uppercase dropped first if code space runs out
const RARE = 'ẲẴẶẨẪỶỸỲỴẺẼẸỂỄỈĨỊỖỠỮỪỬỰẰẦỀỒỜ';

function buildCodes(usedText = '') {
  const usedCh = new Set(usedText.normalize('NFC'));
  const code = {}; const pair = []; // pair[code] = [base, top]
  const used = new Set();
  for (const [name, t] of Object.entries(T)) {
    if ([...name].length !== 1 || name === 'ı') continue;
    code[name] = t; pair[t] = [t, SPACE]; used.add(t);
  }
  // precomposed single-cell glyphs and EN tiles used raw in bank B strings keep code == tile
  for (const [name, t] of Object.entries(T)) if (/^.1$/u.test(name) && !used.has(t)) { pair[t] = [t, SPACE]; used.add(t); }
  // first Doraemon art tile is used raw in a layout script (must be < $E0)
  if (X.dora) { const t = X.dora[0]; pair[t] = [t, SPACE]; used.add(t); }
  for (let t = 0x16; t <= 0x1F; t++) { pair[t] = [t, SPACE]; used.add(t); }
  for (let t = 0x90; t <= 0x9F; t++) if (t < 0x96 || t > 0x99) { pair[t] = [t, SPACE]; used.add(t); }
  const free = []; for (let c = 0; c < 0xDF; c++) if (!used.has(c)) free.push(c);
  let comps = allComposites().filter(c => code[c] === undefined);
  const need = [];
  for (const c of comps) { const a = analyzeChar(c); if (a && a.mark) need.push([c, a]); }
  // prioritize: non-rare first
  const rank = c => (usedCh.has(c) ? 0 : 2) + (RARE.includes(c) ? 1 : 0);
  need.sort((x, y) => rank(x[0]) - rank(y[0]));
  const dropped = [];
  for (const [c, a] of need) {
    if (!free.length) { dropped.push(c); continue; }
    const k = free.shift(); code[c] = k; pair[k] = [T[a.base], T[a.mark]];
  }
  for (const k of free) pair[k] = [SPACE, SPACE];
  // codes >= $E0: identity by default; extra tiles for bank-B strings only
  for (let k = 0xDF; k < 0x100; k++) pair[k] = [k, SPACE];
  let xc = 0xE0; const xcode = {};
  for (const [name, tiles] of Object.entries(X)) xcode[name] = tiles.map((t, i) => { if (name === 'dora' && i === 0) return t; if (xc > 0xFE) throw new Error('out of extra codes'); pair[xc] = [t, SPACE]; return xc++; });
  return { code, pair, dropped, freeLeft: free.length, xcode };
}

let CODES = null;
function init(enFont, usedText = '') {
  ENFONT = enFont;
  const usedCh = new Set(usedText.normalize('NFC'));
  buildFontArt(enFont, usedCh); CODES = buildCodes(usedText); return CODES;
}

function fontBytes(enFont) {
  const out = Buffer.from(enFont);
  for (const [t, art] of Object.entries(tileArt)) tileFromArt(art).copy(out, +t * 16);
  return out;
}

// encode plain text (no control codes) -> bytes
function encodeText(s, where) {
  const out = [];
  for (const ch of s.normalize('NFC')) {
    const c = CODES.code[ch];
    if (c === undefined) throw new Error(`unencodable char '${ch}' (U+${ch.codePointAt(0).toString(16)}) in ${where || s}`);
    out.push(c);
  }
  return out;
}

// encode bank-B string: plain text plus <name> tokens (extra art) and {hex} raw bytes
function encodeB(s, where) {
  const out = [];
  for (const part of s.split(/(<[^>]+>|\{[0-9a-fA-F]{2}\})/)) {
    if (!part) continue;
    if (part[0] === '<') {
      const k = part.slice(1, -1);
      if (CODES.xcode[k]) out.push(...CODES.xcode[k]);
      else if (T[k] !== undefined && CODES.pair[T[k]] && CODES.pair[T[k]][0] === T[k]) out.push(T[k]);
      else throw new Error(`unknown token ${part} in ${where || s}`);
    } else if (part[0] === '{') out.push(parseInt(part.slice(1, -1), 16));
    else out.push(...encodeText(part, where));
  }
  return out;
}

// raw nametable text: returns [base row tiles, top (mark) row tiles]; <name> = single tile, {hh} = raw tile
function rawTiles(s, where) {
  const base = [], top = [];
  for (const part of s.split(/(<[^>]+>|\{[0-9a-fA-F]{2}\})/)) {
    if (!part) continue;
    if (part[0] === '<') { const t = T[part.slice(1, -1)]; if (t === undefined) throw new Error(`no tile ${part} in ${where || s}`); base.push(t); top.push(SPACE); continue; }
    if (part[0] === '{') { base.push(parseInt(part.slice(1, -1), 16)); top.push(SPACE); continue; }
    for (const c of encodeText(part, where)) { const p = CODES.pair[c]; base.push(p[0]); top.push(p[1]); }
  }
  return [base, top];
}

module.exports = { init, fontBytes, encodeText, encodeB, rawTiles, T, get CODES() { return CODES; }, get tilesLeft() { return LOW.length; }, FONT_OFF, SPACE, tileFromArt, artFromTile, tileArt };

if (require.main === module) {
  const rom = fs.readFileSync(process.argv[2] || 'work/en.nes');
  const c = init(rom.slice(FONT_OFF, FONT_OFF + 0x1000));
  console.log('low left', LOW.length, 'high left', HIGH.length, 'dropped', c.dropped.join(''), 'free codes', c.freeLeft);
}
