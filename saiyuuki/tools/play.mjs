// autoplay explorer: node play.mjs rom outprefix totalFrames shotEvery [seedPattern]
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, outp, total='3000', every='120', startScript=''] = process.argv;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const C=Controller;
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${String(n).padStart(5,'0')}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
let f=0;
for(;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
for(;f<+total;f++){
  // mash A to skip dialog, hold right, jump & attack periodically
  nes.buttonDown(1,C.BUTTON_RIGHT);
  if(f%20<10)nes.buttonDown(1,C.BUTTON_A);else nes.buttonUp(1,C.BUTTON_A);
  if(f%14<4)nes.buttonDown(1,C.BUTTON_B);else nes.buttonUp(1,C.BUTTON_B);
  for(const a of [0x16b,0x17c,0x18d])nes.cpu.mem[a]=9;
  nes.frame();
  if(f%(+every)===0)shot(f);
}
