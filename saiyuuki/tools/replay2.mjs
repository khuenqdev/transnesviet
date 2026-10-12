// replay seq to frame N then optionally call subroutine (spawn type) then run & shoot. usage: node replay2.mjs rom seq.json out stopFrame spawnType|- afterFrames
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seqf, outp, stopS, typeS='-', afterS='100']=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
let f=0; for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1;
function step(){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
while(f<+stopS)step();
shot('pre');
if(typeS!=='-'){
 const cpu=nes.cpu; const SENT=0x0100;
 const sv={pc:cpu.REG_PC,a:cpu.REG_ACC,x:cpu.REG_X,y:cpu.REG_Y,sp:cpu.REG_SP};
 cpu.mem[0x100+cpu.REG_SP]=((SENT-1)>>8)&255;cpu.REG_SP--;cpu.mem[0x100+cpu.REG_SP]=(SENT-1)&255;cpu.REG_SP--;
 cpu.REG_PC=0xCEC5-1;cpu.REG_ACC=parseInt(typeS,16);cpu.REG_X=0;cpu.REG_Y=0;
 let n=0;while(cpu.REG_PC+1!==SENT&&n++<200000)cpu.emulate();
 cpu.REG_PC=sv.pc;cpu.REG_ACC=sv.a;cpu.REG_X=sv.x;cpu.REG_Y=sv.y;cpu.REG_SP=sv.sp; console.log('spawned after',n,'instr');
}
for(let i=0;i<+afterS;i++){step(); if(i===20||i===+afterS-1)shot('s'+i);}
fs.writeFileSync(`${outp}.vram`,Buffer.from(nes.ppu.vramMem));
