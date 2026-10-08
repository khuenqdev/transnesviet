// Search ROM for byte pattern (hex, '??' wildcard). usage: node find.js rom "58 6d ?? 62"
const fs = require('fs');
const rom = fs.readFileSync(process.argv[2]);
const pat = process.argv[3].trim().split(/\s+/).map(x => x === '??' ? -1 : parseInt(x, 16));
for (let i = 0; i + pat.length <= rom.length; i++) {
  let ok = true;
  for (let j = 0; j < pat.length; j++) if (pat[j] >= 0 && rom[i + j] !== pat[j]) { ok = false; break; }
  if (ok) {
    const o = i - 16; const bank = o >> 14; const addr = (o & 0x3FFF) + (bank === 15 ? 0xC000 : 0x8000);
    console.log(`file ${i.toString(16)} bank ${bank.toString(16)} addr ${addr.toString(16)} : ${rom.slice(i, i + 32).toString('hex')}`);
  }
}
