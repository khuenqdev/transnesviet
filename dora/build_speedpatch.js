// Doraemon - Giga Zombie no Gyakushuu : walking-speed patch builder
// usage: node build_speedpatch.js <japanese.nes> <vietnamese.nes> [outdir]
// Writes: walkspeed_JP.ips (original ROM), walkspeed_VN.ips (Vietnamese 512 KB ROM) and walkspeed_x2_*.ips (twice as fast)
const fs = require('fs'), path = require('path');
const { makeIps } = require('./ips');

const BANK = 0x4000;
const off = (bank, addr) => 16 + bank * BANK + (addr & 0x3FFF);

// The field handler in the fixed bank ($C5D4) runs once per frame while the hero is mid-step:
//   C613  LDA #$0D ; JSR $CD5C            select bank D
//   C618  JSR $CF4C / $81A0 / $87E2 / $8B6F / $CF55    NPC + sprite logic  (all of them read $34 = pixels/frame)
//   C627  LDA #$0C ; JSR $CD5C            select bank C
//   C62C  LDA $45
//   C62E  LDX $32 ; JSR $AE22             scroll + hero movement by $34 pixels, $32 -= $34
// Version 1 gave an extra JSR $AE22 on some frames: the scroll moved 2 px while the NPC code still assumed 1 px,
// so NPCs drifted over houses/trees.  This version changes the step ($34) itself for the WHOLE frame, so the NPC
// logic and the scroll always agree (the game already supports $34 = 2: NPCs use "ASL" doubled deltas).
const HOOK1 = { addr: 0xC613, old: [0xA9, 0x0D, 0x20, 0x5C, 0xCD] };
const HOOK2 = { addr: 0xC62E, old: [0xA6, 0x32, 0x20, 0x22, 0xAE] };
const CODE1 = 0xFFA0, CODE2 = 0xFFC5, FLAG = 0x07EA; // $07EA-$07ED are never referenced by the game
//  FFA0  LDA #$0D / JSR $CD5C      (the two instructions replaced by the hook)
//  FFA5  LDA #$00 / STA $07EA      flag = "step not boosted"
//  FFAA  LDA $34 / CMP #$01 / BNE end   only boost normal walking (vehicles etc. already use 2)
//  FFB0  LDA $32 / AND #$02 / BEQ end   $32 = pixels left of the 16-px step; bit 1 set -> this frame moves 2 px
//  FFB6  LDA #$02 / STA $34 / STA $07EA
//  FFBD  RTS
//  FFBE  LDX $32 / JSR $AE22       (the instructions replaced by hook 2; A = $45 as before)
//  FFC3  PHA / LDA $07EA / BEQ +2 / DEC $34 / PLA / RTS     put the step back to 1
// 16 px take 12 frames instead of 16 (x1.33); $32 is >= 2 whenever a 2 px frame is chosen, so it can never overshoot 0.
// extra gate: no boost while the NPC clock $0450 is 1 (a 2-pixel frame would overshoot the NPC's step by 1 px)
const ROUTINE1 = [0xA9, 0x0D, 0x20, 0x5C, 0xCD, 0xA9, 0x00, 0x8D, 0xEA, 0x07, 0xA5, 0x34, 0xC9, 0x01, 0xD0, 0x14,
  0xA5, 0x32, 0x29, 0x02, 0xF0, 0x0E, 0xAD, 0x50, 0x04, 0xC9, 0x01, 0xF0, 0x07, 0xA9, 0x02, 0x85, 0x34, 0x8D, 0xEA, 0x07, 0x60];
const ROUTINE2 = [0xA6, 0x32, 0x20, 0x22, 0xAE, 0x48, 0xAD, 0xEA, 0x07, 0xF0, 0x02, 0xC6, 0x34, 0x68, 0x60];
// ROOT CAUSE of the NPC glitches (v1 and v2): the NPCs have their own 16-tick step clock $0450 that is decremented
// by exactly 1 per frame (bank D $8BB3: DEC $0450) no matter how many pixels the hero moves. With a faster hero the
// walking phase lasts 12 frames, the NPC routines only run during it, so NPCs never finished their 16-tick step:
// they stopped half way, left their grid and walked into houses/trees and started their next move together.
// Fix (hook 3): the clock is decremented by $34 (pixels per frame) so an NPC step ends together with the hero's step.
const HOOK3 = { bank: 13, addr: 0x8BB3, old: [0xCE, 0x50, 0x04], neu: [0x20, 0x3E, 0x9E] };   // DEC $0450 -> JSR $FFCD (BNE follows)
const CODE3 = 0x9E3E; // free space in bank D itself (55 bytes free in both ROMs)
//  9E3E  LDA $0450 ; SEC ; SBC $34 ; BCS store ; LDA #0 ; store: STA $0450 ; RTS     (Z flag = new value == 0, as DEC left it)
const ROUTINE3 = [0xAD, 0x50, 0x04, 0x38, 0xE5, 0x34, 0xB0, 0x02, 0xA9, 0x00, 0x8D, 0x50, 0x04, 0x60];
const CODE = CODE1;
// x2 variant: walking speed 2 px/frame (8 frames per tile) by changing the four "LDA #$01 / STA $34" defaults
const X2_SITES = [
  { bank: 15, addr: 0xC064 }, { bank: 15, addr: 0xD19B }, { bank: 13, addr: 0x93FB }, { bank: 13, addr: 0x941D },
]; // each: A9 01 85 34

function check(rom, bank, addr, bytes, what) {
  for (let i = 0; i < bytes.length; i++) if (rom[off(bank, addr + i)] !== bytes[i]) throw new Error(`${what}: unexpected byte at bank ${bank} $${(addr + i).toString(16)}`);
}
function patch(rom, fixedBanks, variant) {
  const out = Buffer.from(rom);
  check(out, HOOK3.bank, HOOK3.addr, HOOK3.old, 'hook 3');
  for (let i = 0; i < ROUTINE3.length; i++) if (out[off(13, CODE3 + i)] !== 0xFF) throw new Error('free space 3 not free');
  Buffer.from(HOOK3.neu).copy(out, off(HOOK3.bank, HOOK3.addr));
  Buffer.from(ROUTINE3).copy(out, off(13, CODE3));
  if (variant === 'slight') {
    for (const b of fixedBanks) {
      check(out, b, HOOK1.addr, HOOK1.old, 'hook 1');
      check(out, b, HOOK2.addr, HOOK2.old, 'hook 2');
      for (const [a, r] of [[CODE1, ROUTINE1], [CODE2, ROUTINE2]])
        for (let i = 0; i < r.length; i++) if (out[off(b, a + i)] !== 0xFF) throw new Error('free space not free');
      Buffer.from([0x20, CODE1 & 0xFF, CODE1 >> 8, 0xEA, 0xEA]).copy(out, off(b, HOOK1.addr));
      Buffer.from([0x4C, CODE2 & 0xFF, CODE2 >> 8, 0xEA, 0xEA]).copy(out, off(b, HOOK2.addr));
      Buffer.from(ROUTINE1).copy(out, off(b, CODE1));
      Buffer.from(ROUTINE2).copy(out, off(b, CODE2));
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
