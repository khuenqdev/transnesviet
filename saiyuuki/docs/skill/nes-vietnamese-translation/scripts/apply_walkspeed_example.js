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
// Hook 3 (both variants): the NPC step clock $0450 (bank D $8BB3 "DEC $0450") must count down by the hero's pixels per frame ($34)
const H3_OLD = [0xCE, 0x50, 0x04], H3_NEW = [0x20, 0x3E, 0x9E];
const R3 = [0xAD, 0x50, 0x04, 0x38, 0xE5, 0x34, 0xB0, 0x02, 0xA9, 0x00, 0x8D, 0x50, 0x04, 0x60];
if (eq(13, 0x8BB3, H3_NEW)) { console.error('Already patched.'); process.exit(3); }
if (!eq(13, 0x8BB3, H3_OLD) || !eq(13, 0x9E3E, Array(R3.length).fill(0xFF))) { console.error('Bank 13: unexpected bytes - wrong ROM version?'); process.exit(2); }
if (!x2) {
  const H1 = [0xA9, 0x0D, 0x20, 0x5C, 0xCD], H2 = [0xA6, 0x32, 0x20, 0x22, 0xAE];
  const R1 = [0xA9, 0x0D, 0x20, 0x5C, 0xCD, 0xA9, 0x00, 0x8D, 0xEA, 0x07, 0xA5, 0x34, 0xC9, 0x01, 0xD0, 0x14,
    0xA5, 0x32, 0x29, 0x02, 0xF0, 0x0E, 0xAD, 0x50, 0x04, 0xC9, 0x01, 0xF0, 0x07, 0xA9, 0x02, 0x85, 0x34, 0x8D, 0xEA, 0x07, 0x60];
  const R2 = [0xA6, 0x32, 0x20, 0x22, 0xAE, 0x48, 0xAD, 0xEA, 0x07, 0xF0, 0x02, 0xC6, 0x34, 0x68, 0x60];
  for (const b of fixed) {
    if (!eq(b, 0xC613, H1) || !eq(b, 0xC62E, H2) || !eq(b, 0xFFA0, Array(R1.length).fill(0xFF)) || !eq(b, 0xFFC5, Array(R2.length).fill(0xFF))) { console.error(`Bank ${b}: unexpected bytes - wrong ROM version?`); process.exit(2); }
  }
  for (const b of fixed) { put(b, 0xC613, [0x20, 0xA0, 0xFF, 0xEA, 0xEA]); put(b, 0xC62E, [0x4C, 0xC5, 0xFF, 0xEA, 0xEA]); put(b, 0xFFA0, R1); put(b, 0xFFC5, R2); }
} else {
  const sites = [[fixed, 0xC064], [fixed, 0xD19B], [[13], 0x93FB], [[13], 0x941D]];
  for (const [bs, a] of sites) for (const b of bs) if (!eq(b, a, [0xA9, 0x01, 0x85, 0x34])) { console.error(`Bank ${b} $${a.toString(16)}: unexpected bytes (already patched / wrong ROM?)`); process.exit(2); }
  for (const [bs, a] of sites) for (const b of bs) put(b, a + 1, [0x02]);
}
put(13, 0x8BB3, H3_NEW); put(13, 0x9E3E, R3);
fs.writeFileSync(outp, rom);
console.log(`Patched ${prgBanks === 16 ? 'Japanese' : 'Vietnamese'} ROM (${x2 ? 'x2 speed' : 'x1.33 speed'}) -> ${outp}`);
