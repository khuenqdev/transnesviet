// Hexdump by bank:addr. usage: node hexdump.js rom bank addrHex len
const fs = require('fs');
const rom = fs.readFileSync(process.argv[2]);
const bank = parseInt(process.argv[3], 16); let addr = parseInt(process.argv[4], 16); const len = parseInt(process.argv[5] || '100', 16);
const base = 16 + bank * 0x4000 - (addr >= 0xC000 ? 0xC000 : 0x8000);
for (let a = addr; a < addr + len; a += 16) {
  const row = []; for (let i = 0; i < 16; i++) row.push(rom[base + a + i].toString(16).padStart(2, '0'));
  console.log(a.toString(16) + ': ' + row.join(' '));
}
