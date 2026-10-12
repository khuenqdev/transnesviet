import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const romPath=process.argv[2];
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const C=Controller;
for(let f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,C.BUTTON_START);
// heart pixel count: red pixels (r>200,g<80) in region x 0..60,y 0..24
function hearts(){let n=0;for(let y=0;y<24;y++)for(let x=0;x<64;x++){const c=fb[y*256+x];const r=c&255,g=(c>>8)&255,b=(c>>16)&255;if(r>180&&g<100&&b<100)n++;}return n;}
let prevH=-1,prevRam=null;
for(let f=0;f<5000;f++){
  nes.buttonDown(1,C.BUTTON_RIGHT);
  if(f%20<10)nes.buttonDown(1,C.BUTTON_A);else nes.buttonUp(1,C.BUTTON_A);
  if(f%14<4)nes.buttonDown(1,C.BUTTON_B);else nes.buttonUp(1,C.BUTTON_B);
  nes.frame();
  const h=hearts(); const ram=Array.from(nes.cpu.mem.slice(0,0x800));
  if(prevH>=0&&h!==prevH&&f>300){
    const ch=[];for(let i=0;i<0x800;i++)if(ram[i]===prevRam[i]-1&&ram[i]<=12)ch.push(i.toString(16)+':'+prevRam[i]+'->'+ram[i]);
    console.log('frame',f,'hearts px',prevH,'->',h,'candidates',ch.join(' '));
  }
  prevH=h;prevRam=ram;
}
