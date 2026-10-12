// usage: node poke_row.mjs rom row out frames  -- runs the dialog engine directly on a given row from a gameplay state
import {NES,Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romP, row, outp, frames='300']=process.argv;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romP).toString('binary'));
for(let f=0;f<150;f++)nes.frame();
nes.buttonDown(1,Controller.BUTTON_START);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,Controller.BUTTON_START);
for(let f=0;f<420;f++){nes.cpu.mem[0x34c]=12;nes.frame();}
const m=nes.cpu.mem;
// stub
const code=[0xA5,0xA6,0xCD,0xFE,0x04,0xF0,0xF8,0x8D,0xFE,0x04,0x20,0x0B,0xAB,0x4C,0x00,0x06];
for(let i=0;i<code.length;i++)m[0x600+i]=code[i];
nes.mmap.loadRomBank(3,0x8000); m[0x10]=3;
m[0x50]=0;m[0x51]=+row;m[0x52]=0;m[0x59]=0;m[0x53]=0;m[0x54]=0;m[0x55]=0;
nes.cpu.REG_PC=0x600-1;
for(let f=0;f<+frames;f++){ nes.frame(); }
const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
fs.writeFileSync(outp+'.ppm',Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));
console.log('ok',m[0x50],m[0x51],m[0x59].toString(16));
