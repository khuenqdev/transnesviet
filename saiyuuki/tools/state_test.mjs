// usage: node state_test.mjs orig.nes new.nes seq.json outprefix framesAfter [offsetBeforeHit]
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, origP, newP, seqf, outp, after='200', before='3']=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
let fb=new Array(61440).fill(0);
function mk(p){const n=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});n.loadROM(fs.readFileSync(p).toString('binary'));return n;}
function shot(n,tag){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${tag}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
const nes=mk(origP);
let f=0; for(;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1; const stop=S.hit-(+before);
for(;f<stop;f++){
  if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12;
  nes.frame();
}
const st=nes.toJSON();
fs.writeFileSync(outp+'.state.json',JSON.stringify(st));
const n2=mk(newP); n2.fromJSON(st); n2.mmap.loadRomBank(n2.cpu.mem[0x10], 0x8000); n2.mmap.loadRomBank(n2.rom.romCount-1, 0xc000);
// keep held buttons as at that moment
const sh=(k)=>{ for(let i=0;i<k;i++){ n2.cpu.mem[0x34c]=12; n2.frame(); } };
const marks=(process.argv[8]||'60,120,200,300').split(',').map(Number);
let t=0; for(const m of marks){ sh(m-t); t=m; shot(0,'f'+m); }
fs.writeFileSync(outp+'.vram',Buffer.from(n2.ppu.vramMem));
console.log('ok');
