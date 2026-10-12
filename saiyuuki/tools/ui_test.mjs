// usage: node ui_test.mjs orig.nes new.nes seq.json outprefix beforeHit "script"   script: F<n> | P<btn> | S<name>
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, origP, newP, seqf, outp, before, script]=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
const map={A:C.BUTTON_A,B:C.BUTTON_B,s:C.BUTTON_SELECT,t:C.BUTTON_START,u:C.BUTTON_UP,d:C.BUTTON_DOWN,l:C.BUTTON_LEFT,r:C.BUTTON_RIGHT};
let fb=new Array(61440).fill(0);
function mk(p){const n=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});n.loadROM(fs.readFileSync(p).toString('binary'));return n;}
function shot(tag){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${tag}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
let nes=mk(origP);
let f=0; for(;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1; const stop=S.hit-(+before);
for(;f<stop;f++){
  if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12;
  nes.frame();
}
if(newP!=='same'){const st=nes.toJSON(); nes=mk(newP); nes.fromJSON(st); nes.mmap.loadRomBank(nes.cpu.mem[0x10],0x8000); nes.mmap.loadRomBank(nes.rom.romCount-1,0xc000);}
for(const b of btns)nes.buttonUp(1,b);
let logOn=false, fno=0; const ow=nes.cpu.write.bind(nes.cpu);
nes.cpu.write=function(a,v){ if(logOn&&a===0x491) console.log('f',fno,'RET',v,'row',nes.cpu.mem[0x51],'mode',nes.cpu.mem[0x493],'sav',nes.cpu.mem[0x499].toString(16),nes.cpu.mem[0x498].toString(16),'prog',nes.cpu.mem[0x492]); return ow(a,v);};
let inv=true; const fr=n=>{for(let i=0;i<n;i++){fno++;if(inv)nes.cpu.mem[0x34c]=12;nes.frame();}};
const fr_old=n=>{for(let i=0;i<n;i++){nes.cpu.mem[0x34c]=12;nes.frame();}};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F')fr(+a); else if(k==='P'){nes.buttonDown(1,map[a]);fr(4);nes.buttonUp(1,map[a]);fr(10);} else if(k==='S')shot(a); else if(k==='L')logOn=true; else if(k==='N')inv=false; else if(k==='M'){const [ad,vl]=a.split('=');nes.cpu.mem[parseInt(ad,16)]=parseInt(vl);} else if(k==='J'){ const [lo,hi]=a.split('-').map(x=>parseInt(x,16)); for(let t=lo;t<=hi;t++)for(let y=0;y<16;y++)nes.ppu.writeMem(t*16+y,0xAA);}
 else if(k==='D')fs.writeFileSync(`${outp}_${a}.vram`,Buffer.from(nes.ppu.vramMem));}
console.log('done');
