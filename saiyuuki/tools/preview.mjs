// Preview any two table rows in the intro dialog box by overriding the pointer-table reads for rows 193/194.
// usage: node preview.mjs rom rowA rowB outprefix [waitFrames=420] [intro-start-script]
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, aS, bS, outp, waitS='500']=process.argv; const C=Controller;
const A=+aS,B=+bS; const rom=fs.readFileSync(romPath);
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(rom.toString('binary'));
const cpu=nes.cpu;
// find pointer table in whichever PRG bank is mapped: base offset of table = 0x9E77 in bank 3 (and later builds keep it)
const prg=rom.subarray(16); const TBL=3*0x4000+(0x9E77-0x8000);
function rowPtr(i){return prg[TBL+2*i]|prg[TBL+2*i+1]<<8;}
const ol=cpu.load.bind(cpu);
const T193=0x9E77+2*193,T194=0x9E77+2*194;
cpu.load=function(a){ let v=ol(a);
  if(a===T193)return rowPtr(A)&255; if(a===T193+1)return rowPtr(A)>>8;
  if(a===T194)return rowPtr(B)&255; if(a===T194+1)return rowPtr(B)>>8; return v;};
const log=[]; let f=0; const oe=cpu.emulate.bind(cpu);
cpu.emulate=function(){ const pc=cpu.REG_PC+1; if(pc===0xFF76||pc===0xFD1E){log.push([f,pc.toString(16),cpu.mem[0x51],((cpu.mem[5]<<8)|cpu.mem[4]).toString(16),cpu.REG_Y,((cpu.mem[3]<<8)|cpu.mem[2]).toString(16)]);} return oe();};
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
for(f=0;f<120;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
for(;f<+waitS;f++){nes.frame(); if(f%60===0&&f>=300)shot(f);}
shot('end');
const seen=new Map(); for(const l of log){const k=l.slice(1).join(' '); }
const calls=log.filter(l=>l[1]==='ff76'); 
const sum=new Map(); for(const l of calls){const k=`row=${l[2]} addr=${l[3]} Y=${l[4]} ptr=${l[5]}`; if(!sum.has(k))sum.set(k,l[0]);}
console.log([...sum.entries()].slice(0,40).map(([k,v])=>`f${v} ${k}`).join('\n'));
