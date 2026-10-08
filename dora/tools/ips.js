// IPS utilities: list records, apply patch, create patch
const fs = require('fs');

function parseIps(buf) {
  if (buf.toString('ascii', 0, 5) !== 'PATCH') throw new Error('not IPS');
  const recs = [];
  let p = 5;
  while (p < buf.length) {
    if (buf.toString('ascii', p, p + 3) === 'EOF' && p + 3 >= buf.length - 3) { p += 3; break; }
    const off = (buf[p] << 16) | (buf[p + 1] << 8) | buf[p + 2]; p += 3;
    const size = (buf[p] << 8) | buf[p + 1]; p += 2;
    if (size === 0) {
      const rle = (buf[p] << 8) | buf[p + 1]; p += 2;
      recs.push({ off, size: rle, data: Buffer.alloc(rle, buf[p]), rle: true }); p += 1;
    } else {
      recs.push({ off, size, data: buf.slice(p, p + size) }); p += size;
    }
  }
  let truncate = null;
  if (p + 3 <= buf.length) truncate = (buf[p] << 16) | (buf[p + 1] << 8) | buf[p + 2];
  return { recs, truncate };
}

function applyIps(rom, ips) {
  const { recs, truncate } = parseIps(ips);
  let end = rom.length;
  for (const r of recs) end = Math.max(end, r.off + r.size);
  const out = Buffer.alloc(end); rom.copy(out);
  for (const r of recs) r.data.copy(out, r.off);
  return truncate != null ? out.slice(0, truncate) : out;
}

function makeIps(orig, mod) {
  const parts = [Buffer.from('PATCH')];
  let i = 0;
  while (i < mod.length) {
    if (i < orig.length && orig[i] === mod[i]) { i++; continue; }
    let j = i;
    while (j < mod.length && j - i < 0xFFFF && !(j < orig.length && orig[j] === mod[j] && (j + 1 >= mod.length || orig[j + 1] === mod[j + 1]))) j++;
    let off = i;
    if (off === 0x454F46) off--; // avoid "EOF" offset
    const data = mod.slice(off, j);
    const h = Buffer.from([off >> 16, (off >> 8) & 255, off & 255, data.length >> 8, data.length & 255]);
    parts.push(h, data);
    i = j;
  }
  parts.push(Buffer.from('EOF'));
  return Buffer.concat(parts);
}

module.exports = { parseIps, applyIps, makeIps };

if (require.main === module) {
  const [cmd, a, b, c] = process.argv.slice(2);
  if (cmd === 'list') {
    const { recs, truncate } = parseIps(fs.readFileSync(a));
    for (const r of recs) console.log(`${r.off.toString(16).padStart(6, '0')} len=${r.size.toString(16)}${r.rle ? ' RLE' : ''}`);
    if (truncate != null) console.log('truncate', truncate.toString(16));
  } else if (cmd === 'apply') {
    fs.writeFileSync(c, applyIps(fs.readFileSync(a), fs.readFileSync(b)));
  } else if (cmd === 'make') {
    fs.writeFileSync(c, makeIps(fs.readFileSync(a), fs.readFileSync(b)));
  } else {
    console.log('usage: ips.js list <ips> | apply <rom> <ips> <out> | make <orig> <mod> <out>');
  }
}
