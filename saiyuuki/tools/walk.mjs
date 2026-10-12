import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, outp, from, to, every, pat] = process.argv;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const C=Controller;
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${String(n).padStart(5,'0')}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
for(let f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,C.BUTTON_START);
for(let f=0;f<+to;f++){
  nes.buttonDown(1,C.BUTTON_RIGHT);
  const upOn=(f%40<6); if(upOn)nes.buttonDown(1,C.BUTTON_UP);else nes.buttonUp(1,C.BUTTON_UP);
  if(f%60<14)nes.buttonDown(1,C.BUTTON_A);else nes.buttonUp(1,C.BUTTON_A);
  if(f>600){nes.cpu.mem[0x34c]=12;}
  nes.frame();
  if(f>=+from&&f%(+every)===0)shot(f);
}
