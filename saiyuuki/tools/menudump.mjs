import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seqf, outp, stopS, doClobber]=process.argv; const C=Controller;
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
while(f<+stopS){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
for(const b of btns)nes.buttonUp(1,b);
const fr=n=>{for(let i=0;i<n;i++){nes.cpu.mem[0x34c]=12;nes.frame();}};
const press=b=>{nes.buttonDown(1,b);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,b);fr(10);};
fr(30); shot('before');
press(C.BUTTON_SELECT); fr(40); shot('menu'); fs.writeFileSync(`${outp}.vram`,Buffer.from(nes.ppu.vramMem)); fs.writeFileSync(`${outp}.ram`,Buffer.from(nes.cpu.mem.slice(0,0x800)));
if(doClobber==='1'){ for(let a=0;a<0x800;a++) nes.ppu.writeMem(a,0xAA); shot('menu_clobbered'); }
press(C.BUTTON_SELECT); fr(60); shot('after');
