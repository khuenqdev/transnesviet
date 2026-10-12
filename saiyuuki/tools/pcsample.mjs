import {NES} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, f0, f1]=process.argv;
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; const oe=cpu.emulate.bind(cpu); let on=false; const cnt=new Map();
cpu.emulate=function(){ if(on){const pc=cpu.REG_PC+1; const k=pc.toString(16)+'/b'+cpu.mem[0x10]; cnt.set(k,(cnt.get(k)||0)+1);} return oe(); };
for(let f=0;f<+f1;f++){ on=f>=+f0; nes.frame(); }
console.log([...cnt.entries()].sort((a,b)=>b[1]-a[1]).slice(0,40).map(e=>e.join(':')).join('\n'));
