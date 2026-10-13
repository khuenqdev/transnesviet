// Doraemon - Giga Zombie no Gyakushuu : walking-speed patch builder
// usage: node build_speedpatch.js <japanese.nes> <vietnamese.nes> [outdir]
// Writes: walkspeed_JP.ips (original ROM), walkspeed_VN.ips (Vietnamese 512 KB ROM) and walkspeed_x2_*.ips (twice as fast)
const fs = require('fs'), path = require('path');
const { makeIps } = require('./ips');

const BANK = 0x4000;
const off = (bank, addr) => 16 + bank * BANK + (addr & 0x3FFF);

// Original code at $C62E (fixed bank): LDX $32 ; JSR $AE22   (one pixel of walking per frame, 16 frames per tile)
const HOOK = { addr: 0xC62E, old: [0xA6, 0x32, 0x20, 0x22, 0xAE] };
// Free space in the fixed bank that is unused in BOTH the Japanese ROM and the Vietnamese ROM
const CODE = 0xFFA0;
//  FFA0  LDA $34        ; walking speed (1 px/frame)? vehicles use 2 and are left alone
//  FFA2  CMP #$01
//  FFA4  BNE FFAF
//  FFA6  LDA $32        ; pixels left of the 16-px step
//  FFA8  AND #$02       ; every step where bit 1 is set gets a bonus pixel -> 16 px in 12 frames (x1.33)
//  FFAA  BEQ FFAF
//  FFAC  JSR $AE22      ; bonus pixel (same routine the game uses; $32 >= 2 here so it never ends the step)
//  FFAF  LDX $32
//  FFB1  JSR $AE22      ; the normal pixel
//  FFB4  RTS
const SLIGHT = [0xA5, 0x34, 0xC9, 0x01, 0xD0, 0x09, 0xA5, 0x32, 0x29, 0x02, 0xF0, 0x03, 0x20, 0x22, 0xAE, 0xA6, 0x32, 0x20, 0x22, 0xAE, 0x60];
const JSR_HOOK = [0x20, CODE & 0xFF, CODE >> 8, 0xEA, 0xEA];
// x2 variant: walking speed 2 px/frame (8 frames per tile) by changing the four "LDA #$01 / STA $34" defaults
const X2_SITES = [
  { bank: 15, addr: 0xC064 }, { bank: 15, addr: 0xD19B }, { bank: 13, addr: 0x93FB }, { bank: 13, addr: 0x941D },
]; // each: A9 01 85 34

function check(rom, bank, addr, bytes, what) {
  for (let i = 0; i < bytes.length; i++) if (rom[off(bank, addr + i)] !== bytes[i]) throw new Error(`${what}: unexpected byte at bank ${bank} $${(addr + i).toString(16)}`);
}
function patch(rom, fixedBanks, variant) {
  const out = Buffer.from(rom);
  if (variant === 'slight') {
    for (const b of fixedBanks) {
      check(out, b, HOOK.addr, HOOK.old, 'hook');
      for (let i = 0; i < SLIGHT.length; i++) if (out[off(b, CODE + i)] !== 0xFF) throw new Error('free space not free');
      Buffer.from(JSR_HOOK).copy(out, off(b, HOOK.addr));
      Buffer.from(SLIGHT).copy(out, off(b, CODE));
    }
  } else {
    for (const s of X2_SITES) {
      const banks = s.bank === 15 ? fixedBanks : [s.bank];
      for (const b of banks) { check(out, b, s.addr, [0xA9, 0x01, 0x85, 0x34], 'x2 site'); out[off(b, s.addr + 1)] = 0x02; }
    }
  }
  return out;
}
module.exports = { patch };

if (require.main === module) {
  const [jpPath, vnPath, outDir = '.'] = process.argv.slice(2);
  const jp = fs.readFileSync(jpPath), vn = fs.readFileSync(vnPath);
  for (const v of ['slight', 'x2']) {
    const tag = v === 'slight' ? 'walkspeed' : 'walkspeed_x2';
    const jpOut = patch(jp, [15], v), vnOut = patch(vn, [15, 31], v);
    fs.writeFileSync(path.join(outDir, `${tag}_JP.ips`), makeIps(jp, jpOut));
    fs.writeFileSync(path.join(outDir, `${tag}_VN.ips`), makeIps(vn, vnOut));
    fs.writeFileSync(path.join(outDir, `${tag}_JP.nes`), jpOut);
    fs.writeFileSync(path.join(outDir, `${tag}_VN.nes`), vnOut);
    console.log(tag, 'JP records', jpOut.compare(jp) !== 0, 'ok');
  }
}
