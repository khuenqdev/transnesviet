// Parse FCEUmm savestates: extract chunks (RAM, NTAR, PRAM, CHRR, WRAM, CPU regs...)
const fs = require('fs');

function parseState(buf) {
  const chunks = {};
  let p = 16;
  while (p + 5 <= buf.length) {
    const type = buf[p]; const size = buf.readUInt32LE(p + 1); p += 5;
    const end = p + size;
    while (p + 8 <= end) {
      let name = buf.toString('latin1', p, p + 4).replace(/\0+$/, '');
      const sz = buf.readUInt32LE(p + 4); p += 8;
      const key = chunks[name] ? name + '_' + type : name;
      chunks[key] = buf.slice(p, p + sz); p += sz;
    }
    p = end;
  }
  return chunks;
}

module.exports = { parseState };

if (require.main === module) {
  const c = parseState(fs.readFileSync(process.argv[2]));
  for (const k in c) console.log(k, c[k].length, c[k].length <= 8 ? c[k].toString('hex') : '');
}
