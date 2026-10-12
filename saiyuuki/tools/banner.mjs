import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, outp, total='4000']=process.argv; const C=Controller;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; let f=0,hits=[]; const ow=cpu.write.bind(cpu);
cpu.write=function(a,v){ if(a===0x2007&&f>400){const va=nes.ppu.vramAddress; if(va>=0x2101&&va<=0x211e&&v>=0xd1&&v<=0xfd)hits.push([f,va]);} return ow(a,v);};
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let shotsAfter=-1;
for(;f<+total;f++){
  nes.buttonDown(1,C.BUTTON_RIGHT);
  if(f%20<10)nes.buttonDown(1,C.BUTTON_A);else nes.buttonUp(1,C.BUTTON_A);
  if(f%14<4)nes.buttonDown(1,C.BUTTON_B);else nes.buttonUp(1,C.BUTTON_B);
  nes.frame();
  if(hits.length&&shotsAfter<0){shotsAfter=f;console.log('first banner write frame',hits[0]);}
  if(shotsAfter>=0&&[10,40,90,150].includes(f-shotsAfter))shot(f);
  if(shotsAfter>=0&&f-shotsAfter>160)break;
}
console.log('hits',hits.length,hits.slice(0,3));
