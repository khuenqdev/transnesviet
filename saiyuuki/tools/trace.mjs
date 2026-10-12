// Memory-access tracer. usage: node trace.mjs rom "script" lo hi [r|w] 
// logs PC for reads/writes in CPU range [lo,hi] (hex) during the script (same script syntax as emu.mjs)
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, script, lo, hi, mode='r'] = process.argv;
const LO=parseInt(lo,16),HI=parseInt(hi,16);
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; let log=[]; let on=false;
const ol=cpu.load.bind(cpu), ow=cpu.write.bind(cpu);
let lastPC=0;
if(mode.includes('r')) cpu.load=function(a){ if(on&&a>=LO&&a<=HI) log.push(['R',a.toString(16),(cpu.REG_PC-1).toString(16),cpu.mem[a].toString(16)]); return ol(a);};
if(mode.includes('w')) cpu.write=function(a,v){ if(on&&a>=LO&&a<=HI) log.push(['W',a.toString(16),(cpu.REG_PC-1).toString(16),v.toString(16)]); return ow(a,v);};
const map={A:Controller.BUTTON_A,B:Controller.BUTTON_B,s:Controller.BUTTON_SELECT,t:Controller.BUTTON_START,u:Controller.BUTTON_UP,d:Controller.BUTTON_DOWN,l:Controller.BUTTON_LEFT,r:Controller.BUTTON_RIGHT};
const frames=n=>{for(let i=0;i<n;i++)nes.frame();};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F')frames(+a); else if(k==='P'){nes.buttonDown(1,map[a]);frames(4);nes.buttonUp(1,map[a]);frames(10);} else if(k==='T')on=true; else if(k==='X')on=false;}
const seen=new Map();
for(const l of log){const key=l[0]+l[2];seen.set(key,(seen.get(key)||0)+1);}
console.log([...seen.entries()].map(([k,v])=>k+' x'+v).join('\n'));
console.log('first:',JSON.stringify(log.slice(0,12)));
console.log('bank-state: PRG@8000 first byte',cpu.mem[0x8000]);
