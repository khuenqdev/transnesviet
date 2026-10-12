// Headless jsnes runner: node emu.mjs rom.nes script out_prefix
// script: comma list of  "F<n>" run n frames | "P<btn>" press for 4 frames | "S<name>" screenshot | "D<name>" dump VRAM/nametable
// buttons: A B s(elect) t(start) u d l r
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, script, outp='out'] = process.argv;
const rom = fs.readFileSync(romPath).toString('binary');
let fb = new Array(256*240).fill(0);
const nes = new NES({onFrame: f=>{fb=f.slice()}, onAudioSample:()=>{}, emulateSound:false});
nes.loadROM(rom);
const map={A:Controller.BUTTON_A,B:Controller.BUTTON_B,s:Controller.BUTTON_SELECT,t:Controller.BUTTON_START,u:Controller.BUTTON_UP,d:Controller.BUTTON_DOWN,l:Controller.BUTTON_LEFT,r:Controller.BUTTON_RIGHT};
function shot(name){
  const b=Buffer.alloc(256*240*3);
  for(let i=0;i<fb.length;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
  fs.writeFileSync(`${outp}_${name}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));
}
const frames=n=>{for(let i=0;i<n;i++)nes.frame();};
for(const cmd of script.split(',')){
  const k=cmd[0],a=cmd.slice(1);
  if(k==='F')frames(+a);
  else if(k==='P'){nes.buttonDown(1,map[a]);frames(4);nes.buttonUp(1,map[a]);frames(10);}
  else if(k==='S')shot(a);
  else if(k==='D'){fs.writeFileSync(`${outp}_${a}.vram`,Buffer.from(nes.ppu.vramMem));fs.writeFileSync(`${outp}_${a}.cpuram`,Buffer.from(nes.cpu.mem.slice(0,0x800)));}
}
