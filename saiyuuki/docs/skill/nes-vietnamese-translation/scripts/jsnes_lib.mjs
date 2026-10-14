import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
export const BTN={A:Controller.BUTTON_A,B:Controller.BUTTON_B,s:Controller.BUTTON_SELECT,t:Controller.BUTTON_START,u:Controller.BUTTON_UP,d:Controller.BUTTON_DOWN,l:Controller.BUTTON_LEFT,r:Controller.BUTTON_RIGHT};
export function mk(romPath){
  const rom=fs.readFileSync(romPath).toString('binary');
  const o={fb:new Array(256*240).fill(0)};
  const nes=new NES({onFrame:f=>{o.fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
  nes.loadROM(rom);
  const m=nes.mmap, orig=m.setReg.bind(m);
  m.hi=0; m.prgReg=0;
  const apply=()=>{const n=nes.rom.romCount,hi=n>=32?m.hi*16:0;
    if(m.prgSwitchingSize===0){const b=hi+(m.prgReg&0xE);m.loadRomBank(b%n,0x8000);m.loadRomBank((b+1)%n,0xC000);return;}
    if(m.prgSwitchingArea===1){m.loadRomBank((hi+(m.prgReg&15))%n,0x8000);m.loadRomBank((hi+15)%n,0xC000);}
    else{m.loadRomBank(hi%n,0x8000);m.loadRomBank((hi+(m.prgReg&15))%n,0xC000);}};
  m.setReg=(reg,v)=>{ if(reg===3){m.prgReg=v;} else {orig(reg,v); if(reg===1)m.hi=(v>>4)&1;} apply(); };
  const n32=()=>nes.rom.romCount>=32;
  m.loadRomBank(0,0x8000);m.loadRomBank(nes.rom.romCount-1,0xC000);
  o.nes=nes; o.frames=n=>{for(let i=0;i<n;i++)nes.frame();};
  o.press=(b,n=4,w=12)=>{nes.buttonDown(1,BTN[b]);o.frames(n);nes.buttonUp(1,BTN[b]);o.frames(w);};
  o.ram=a=>nes.cpu.mem[a];
  o.shot=(file,scale=2)=>{ // write PPM->PNG via python later
    const b=Buffer.alloc(256*240*3);for(let i=0;i<o.fb.length;i++){const c=o.fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
    fs.writeFileSync(file.replace(/\.png$/,'.ppm'),Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));};
  return o;}
