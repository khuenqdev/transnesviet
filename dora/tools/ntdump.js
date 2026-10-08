// Dump nametable(s) from a savestate as hex grid
const fs = require('fs');
const { parseState } = require('./state');
const c = parseState(fs.readFileSync(process.argv[2]));
const nt = c.NTAR; const which = +(process.argv[3] || 0);
for (let y = 0; y < 30; y++) {
  let s = y.toString().padStart(2) + ': ';
  for (let x = 0; x < 32; x++) s += nt[which * 0x400 + y * 32 + x].toString(16).padStart(2, '0') + ' ';
  console.log(s);
}
