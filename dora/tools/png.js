// Tiny PNG writer (RGBA) and NES tile helpers
const zlib = require('zlib');
const fs = require('fs');

function crc32(buf) {
  let c, crc = 0xFFFFFFFF;
  for (let n = 0; n < buf.length; n++) {
    c = (crc ^ buf[n]) & 0xFF;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    crc = (crc >>> 8) ^ c;
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function writePng(path, w, h, rgba) {
  const raw = Buffer.alloc((w * 4 + 1) * h);
  for (let y = 0; y < h; y++) { raw[y * (w * 4 + 1)] = 0; rgba.copy(raw, y * (w * 4 + 1) + 1, y * w * 4, (y + 1) * w * 4); }
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 6;
  fs.writeFileSync(path, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]));
}
function readPng(path) {
  const b = fs.readFileSync(path); let p = 8; let w, h, ct, idat = [], plte = null, bd;
  while (p < b.length) {
    const len = b.readUInt32BE(p); const t = b.toString('ascii', p + 4, p + 8); const d = b.slice(p + 8, p + 8 + len);
    if (t === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); bd = d[8]; ct = d[9]; }
    else if (t === 'PLTE') plte = d; else if (t === 'IDAT') idat.push(d);
    p += 12 + len;
  }
  if (bd !== 8) throw new Error('only 8-bit png');
  const bpp = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[ct];
  const raw = zlib.inflateSync(Buffer.concat(idat)); const out = Buffer.alloc(w * h * 4); const stride = w * bpp;
  let prev = Buffer.alloc(stride);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)]; const line = Buffer.from(raw.slice(y * (stride + 1) + 1, (y + 1) * (stride + 1)));
    for (let i = 0; i < stride; i++) {
      const a = i >= bpp ? line[i - bpp] : 0, u = prev[i], c = i >= bpp ? prev[i - bpp] : 0;
      let v = line[i];
      if (f === 1) v += a; else if (f === 2) v += u; else if (f === 3) v += (a + u) >> 1;
      else if (f === 4) { const pp = a + u - c, pa = Math.abs(pp - a), pb = Math.abs(pp - u), pc = Math.abs(pp - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? u : c; }
      line[i] = v & 255;
    }
    for (let x = 0; x < w; x++) {
      const o = (y * w + x) * 4; const s = x * bpp;
      if (ct === 6) line.copy(out, o, s, s + 4);
      else if (ct === 2) { out[o] = line[s]; out[o + 1] = line[s + 1]; out[o + 2] = line[s + 2]; out[o + 3] = 255; }
      else if (ct === 3) { const i = line[s]; out[o] = plte[i * 3]; out[o + 1] = plte[i * 3 + 1]; out[o + 2] = plte[i * 3 + 2]; out[o + 3] = 255; }
      else if (ct === 0) { out[o] = out[o + 1] = out[o + 2] = line[s]; out[o + 3] = 255; }
      else if (ct === 4) { out[o] = out[o + 1] = out[o + 2] = line[s]; out[o + 3] = line[s + 1]; }
    }
    prev = line;
  }
  return { w, h, data: out };
}

const GRAY = [[0, 0, 0], [85, 85, 85], [170, 170, 170], [255, 255, 255]];
// Render tiles (2bpp NES format) to a PNG sheet, 16 tiles per row, scale s
function tilesToPng(path, data, s = 2, cols = 16) {
  const n = data.length >> 4; const rows = Math.ceil(n / cols);
  const W = cols * 8 * s, H = rows * 8 * s; const img = Buffer.alloc(W * H * 4);
  for (let t = 0; t < n; t++) for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) {
    const v = ((data[t * 16 + y] >> (7 - x)) & 1) | (((data[t * 16 + 8 + y] >> (7 - x)) & 1) << 1);
    const c = GRAY[v];
    for (let dy = 0; dy < s; dy++) for (let dx = 0; dx < s; dx++) {
      const px = ((t % cols) * 8 + x) * s + dx, py = (Math.floor(t / cols) * 8 + y) * s + dy;
      const o = (py * W + px) * 4; img[o] = c[0]; img[o + 1] = c[1]; img[o + 2] = c[2]; img[o + 3] = 255;
    }
  }
  writePng(path, W, H, img);
}

module.exports = { writePng, readPng, tilesToPng };
