// replay seq to hit, then continue with extra input script, logging every call into FD1E (row draw) and screenshots
// usage: node drawlog.mjs rom seq.json out stopFrame "script"   script tokens: F<n> P<btn> S<name>
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seqf, outp, stopS, script='']=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; const log=[]; let f=0;
const oe=cpu.emulate.bind(cpu);
cpu.emulate=function(){ const pc=cpu.REG_PC+1; if(pc===0xFD1E){log.push({f,row:cpu.mem[0x51],f52:cpu.mem[0x52],addr:((cpu.mem[5]<<8)|cpu.mem[4]).toString(16),Y:cpu.REG_Y,ptr:((cpu.mem[3]<<8)|cpu.mem[2]).toString(16)});} return oe();};
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
const map={A:C.BUTTON_A,B:C.BUTTON_B,s:C.BUTTON_SELECT,t:C.BUTTON_START,u:C.BUTTON_UP,d:C.BUTTON_DOWN,l:C.BUTTON_LEFT,r:C.BUTTON_RIGHT};
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1;
function step(){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
while(f<+stopS)step();
for(const b of btns)nes.buttonUp(1,b);
for(const cmd of script.split(',')){if(!cmd)continue;const k=cmd[0],a=cmd.slice(1);
 if(k==='F')for(let i=0;i<+a;i++){nes.frame();f++;} else if(k==='P'){nes.buttonDown(1,map[a]);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,map[a]);for(let i=0;i<12;i++){nes.frame();f++}} else if(k==='S')shot(a);}
fs.writeFileSync(`${outp}_log.json`,JSON.stringify(log));
const seen=new Map();for(const l of log){const k=`row ${l.row} f52=${l.f52.toString(16)} addr ${l.addr} Y=${l.Y}`;seen.set(k,(seen.get(k)||0)+1);}
console.log([...seen.entries()].map(([k,v])=>k+' x'+v).join('\n'));
