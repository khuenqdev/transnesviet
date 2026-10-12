import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const romPath=process.argv[2]; const C=Controller;
function run(addr,val,frames=2200){
  let fb=new Array(61440).fill(0);
  const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
  nes.loadROM(fs.readFileSync(romPath).toString('binary'));
  for(let f=0;f<150;f++)nes.frame();
  nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,C.BUTTON_START);
  const hearts=()=>{let n=0;for(let y=0;y<24;y++)for(let x=0;x<64;x++){const c=fb[y*256+x];const r=c&255,g=(c>>8)&255,b=(c>>16)&255;if(r>180&&g<100&&b<100)n++;}return n;};
  let minH=999,maxH=0,title=0;
  for(let f=0;f<frames;f++){
    nes.buttonDown(1,C.BUTTON_RIGHT);
    if(f%20<10)nes.buttonDown(1,C.BUTTON_A);else nes.buttonUp(1,C.BUTTON_A);
    if(f%14<4)nes.buttonDown(1,C.BUTTON_B);else nes.buttonUp(1,C.BUTTON_B);
    if(addr>=0&&f>600)nes.cpu.mem[addr]=val;
    nes.frame();
    if(f>800){const h=hearts();if(h>0){minH=Math.min(minH,h);maxH=Math.max(maxH,h);}}
  }
  return [minH,maxH];
}
for(const a of [-1,0x16b,0x17c,0x18d,0x61b,0x348,0x34c,0xf8,0x115,0x19e,0x44,0x47]){
  console.log(a<0?'none':a.toString(16),JSON.stringify(run(a,a==0x61b?0x0e:12)));
}
