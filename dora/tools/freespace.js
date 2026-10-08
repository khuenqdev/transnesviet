// Report free space (runs of same byte >= min) per bank
const fs = require('fs');
const rom = fs.readFileSync(process.argv[2]); const min = +(process.argv[3] || 64);
for (let b = 0; b < (rom.length - 16) / 0x4000; b++) {
  const base = 16 + b * 0x4000; let tot = 0; const runs = [];
  let i = 0;
  while (i < 0x4000) {
    let j = i; while (j < 0x4000 && rom[base + j] === rom[base + i]) j++;
    if (j - i >= min && (rom[base + i] === 0xFF || rom[base + i] === 0)) { runs.push(`${((b === 15 ? 0xC000 : 0x8000) + i).toString(16)}+${(j - i).toString(16)}(${rom[base + i].toString(16)})`); tot += j - i; }
    i = j;
  }
  console.log(`bank ${b.toString(16)}: free ${tot} ${runs.join(' ')}`);
}
