#!/usr/bin/env node
// Apply the walking-speed patch to a Doraemon - Giga Zombie no Gyakushuu ROM (Japanese original OR Vietnamese 512 KB ROM)
// usage: node apply_walkspeed.js <in.nes> <out.nes> [--x2]
// Apply it AFTER the translation patch (the Vietnamese ROM contains a second copy of the fixed bank that must be patched too).
const fs = require('fs');
const [inp, outp, ...flags] = process.argv.slice(2);
if (!inp || !outp) { console.log('usage: node apply_walkspeed.js <in.nes> <out.nes> [--x2]'); process.exit(1); }
const rom = Buffer.from(fs.readFileSync(inp));
const x2 = flags.includes('--x2');
const BANK = 0x4000, off = (b, a) => 16 + b * BANK + (a & 0x3FFF);
const prgBanks = rom[4];
if (rom.toString('latin1', 0, 4) !== 'NES\x1a' || (prgBanks !== 16 && prgBanks !== 32)) { console.error('Not a supported ROM (expected 256 KB Japanese or 512 KB Vietnamese)'); process.exit(2); }
const fixed = prgBanks === 16 ? [15] : [15, 31];
const eq = (b, a, bytes) => bytes.every((v, i) => rom[off(b, a + i)] === v);
const put = (b, a, bytes) => bytes.forEach((v, i) => { rom[off(b, a + i)] = v; });
if (!x2) {
  const HOOK = [0xA6, 0x32, 0x20, 0x22, 0xAE];
  const CODE = [0xA5, 0x34, 0xC9, 0x01, 0xD0, 0x09, 0xA5, 0x32, 0x29, 0x02, 0xF0, 0x03, 0x20, 0x22, 0xAE, 0xA6, 0x32, 0x20, 0x22, 0xAE, 0x60];
  for (const b of fixed) {
    if (eq(b, 0xC62E, [0x20, 0xA0, 0xFF, 0xEA, 0xEA])) { console.error('Already patched.'); process.exit(3); }
    if (!eq(b, 0xC62E, HOOK) || !eq(b, 0xFFA0, Array(CODE.length).fill(0xFF))) { console.error(`Bank ${b}: unexpected bytes - wrong ROM version?`); process.exit(2); }
  }
  for (const b of fixed) { put(b, 0xC62E, [0x20, 0xA0, 0xFF, 0xEA, 0xEA]); put(b, 0xFFA0, CODE); }
} else {
  const sites = [[fixed, 0xC064], [fixed, 0xD19B], [[13], 0x93FB], [[13], 0x941D]];
  for (const [bs, a] of sites) for (const b of bs) if (!eq(b, a, [0xA9, 0x01, 0x85, 0x34])) { console.error(`Bank ${b} $${a.toString(16)}: unexpected bytes (already patched / wrong ROM?)`); process.exit(2); }
  for (const [bs, a] of sites) for (const b of bs) put(b, a + 1, [0x02]);
}
fs.writeFileSync(outp, rom);
console.log(`Patched ${prgBanks === 16 ? 'Japanese' : 'Vietnamese'} ROM (${x2 ? 'x2 speed' : 'x1.33 speed'}) -> ${outp}`);
