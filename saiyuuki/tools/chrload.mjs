// log calls to decompressor entry $E724 : src ptr, dest PPU addr, bank at the time, from boot through N frames
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, framesS='700']=process.argv; const C=Controller;
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
let bank=0; const ow=nes.mmap.write.bind(nes.mmap); nes.mmap.write=function(a,v){ if(a>=0x8000)bank=v; return ow(a,v);};
const cpu=nes.cpu; const oe=cpu.emulate.bind(cpu); let f=0; const out=[];
cpu.emulate=function(){ const pc=cpu.REG_PC+1; if(pc===0xE724){ out.push({f,bank,src:((cpu.mem[3]<<8)|cpu.mem[2]).toString(16),dst:((cpu.mem[5]<<8)|cpu.mem[4]).toString(16),a:cpu.REG_ACC,x:cpu.REG_X,y:cpu.REG_Y,pc:(cpu.mem[0x100+cpu.REG_SP+1]|cpu.mem[0x100+cpu.REG_SP+2]<<8).toString(16)}); } return oe();};
for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
for(;f<+framesS;f++)nes.frame();
for(const o of out)console.log(JSON.stringify(o));
