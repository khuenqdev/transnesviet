// Lab 2 - run a ROM headless with jsnes and dump video memory + a screenshot.
// usage: node lab2_vram_dump.mjs game.nes frames out_prefix [startAtFrame]
// needs jsnes:  git clone https://github.com/bfirsh/jsnes && set JSNES below (or env JSNES)
import fs from 'fs';
const JSNES = process.env.JSNES || '/home/claude/vendor/jsnes/src/index.js';
const {NES, Controller} = await import(JSNES);
const [,, rom, frames = '200', out = 'out', startAt = '150'] = process.argv;
let fb = new Array(61440).fill(0);
const nes = new NES({onFrame: f => { fb = f.slice(); }, onAudioSample: () => {}, emulateSound: false});
nes.loadROM(fs.readFileSync(rom).toString('binary'));
for (let f = 0; f < +frames; f++) {
  if (f === +startAt) nes.buttonDown(1, Controller.BUTTON_START);   // press START on the title screen
  if (f === +startAt + 4) nes.buttonUp(1, Controller.BUTTON_START);
  nes.frame();
}
fs.writeFileSync(out + '.vram', Buffer.from(nes.ppu.vramMem));            // 0x0000-0x1FFF patterns, 0x2000.. nametables, 0x3F00 palette
fs.writeFileSync(out + '.ram', Buffer.from(nes.cpu.mem.slice(0, 0x800)));
const b = Buffer.alloc(61440 * 3);
for (let i = 0; i < 61440; i++) { const c = fb[i]; b[i*3] = c & 255; b[i*3+1] = (c >> 8) & 255; b[i*3+2] = (c >> 16) & 255; }
fs.writeFileSync(out + '.ppm', Buffer.concat([Buffer.from('P6 256 240 255\n'), b]));
console.log('wrote', out + '.vram', out + '.ram', out + '.ppm');
