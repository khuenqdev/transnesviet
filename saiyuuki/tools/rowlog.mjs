// log engine row draws (PC $AB96 in bank 3) while replaying seq then pressing keys.
// usage: node rowlog.mjs rom seq.json stopFrame "script" out.png-prefix
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seqf, stopS, script, outp]=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; const oe=cpu.emulate.bind(cpu); const log=[];
cpu.emulate=function(){ const pc=cpu.REG_PC+1; if(pc===0xAB96||pc===0xAB97){ if(cpu.mem[0x8000]===3) log.push({row:cpu.mem[0x51],pos:cpu.mem[0x52],a:(cpu.mem[5]<<8|cpu.mem[4]).toString(16),fl:cpu.mem[0x59].toString(16)}); } return oe(); };
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
let f=0; for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1;
while(f<+stopS){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
for(const b of btns)nes.buttonUp(1,b);
const map={A:C.BUTTON_A,B:C.BUTTON_B,s:C.BUTTON_SELECT,t:C.BUTTON_START,u:C.BUTTON_UP,d:C.BUTTON_DOWN,l:C.BUTTON_LEFT,r:C.BUTTON_RIGHT};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F'){for(let i=0;i<+a;i++){nes.cpu.mem[0x34c]=12;nes.frame();}}
 else if(k==='P'){nes.buttonDown(1,map[a]);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,map[a]);for(let i=0;i<10;i++)nes.frame();}
 else if(k==='S')shot(a);}
fs.writeFileSync(`${outp}.vram`,Buffer.from(nes.ppu.vramMem));fs.writeFileSync(`${outp}.ram`,Buffer.from(nes.cpu.mem.slice(0,0x800)));
const seen=new Map(); for(const l of log){const k=JSON.stringify(l);seen.set(k,(seen.get(k)||0)+1);}
console.log([...seen.entries()].map(([k,v])=>k+' x'+v).join('\n'));
