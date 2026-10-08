// Refresh font in a savestate's CHR-RAM from a ROM: node tools/statefont.js rom in.st out.st
const fs = require('fs');
const { parseState } = require('./state');
const rom = fs.readFileSync(process.argv[2]); const st = fs.readFileSync(process.argv[3]);
const c = parseState(st);
const font = rom.slice(0x15290, 0x15290 + 0x1000);
for (let t = 0; t < 256; t++) { if (t >= 0x1B && t <= 0x1F) continue; font.copy(c.CHRR, 0x1000 + t * 16, t * 16, t * 16 + 16); }
fs.writeFileSync(process.argv[4], st);
