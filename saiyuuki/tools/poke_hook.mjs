// usage: node poke_hook.mjs rom row out [frames]  -- calls the init hook directly for a banner row ($2101)
import {NES,Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romP, row, outp, frames='60', addrlo='01', addrhi='21']=process.argv;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romP).toString('binary'));
for(let f=0;f<150;f++)nes.frame();
nes.buttonDown(1,Controller.BUTTON_START);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,Controller.BUTTON_START);
for(let f=0;f<420;f++){nes.cpu.mem[0x34c]=12;nes.frame();}
const m=nes.cpu.mem;
const T_INIT=0xC03A;
const code=[0xA9,28,0x85,0x53,0xA9,parseInt(addrlo,16),0x85,0x04,0xA9,parseInt(addrhi,16),0x85,0x05,0xA9,+row,0x85,0x51,
 0x20,T_INIT&255,T_INIT>>8,0x90,0x03,0x4C,0x10,0x06, 0x4C,0x18,0x06];
// 0610: JSR; BCC +2 -> done ; JMP 0610 (retry) ; 0618: JMP 0618
const base=0x600; for(let i=0;i<code.length;i++)m[base+i]=code[i];
// fix layout: retry loop re-run from 0x600 (sets regs again) ; done loop at end
m[base+0x15]=0x4C; m[base+0x16]=0x00; m[base+0x17]=0x06; // JMP $0600 (retry)
m[base+0x18]=0x4C; m[base+0x19]=0x18; m[base+0x1A]=0x06;
m[0x10]=m[0x10];
nes.cpu.REG_PC=base-1;
for(let f=0;f<+frames;f++){ nes.frame(); }
const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
fs.writeFileSync(outp+'.ppm',Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));
console.log('pc',nes.cpu.REG_PC.toString(16));
