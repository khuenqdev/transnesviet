import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, ...seqs]=process.argv; const C=Controller;
const written=new Uint8Array(0x800);
for(const seqf of seqs){
 const S=JSON.parse(fs.readFileSync(seqf));
 const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
 nes.loadROM(fs.readFileSync(romPath).toString('binary'));
 const cpu=nes.cpu; const ow=cpu.write.bind(cpu);
 let track=false; cpu.write=function(a,v){ if(track&&a<0x800)written[a]=1; return ow(a,v);};
 const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
 let f=0; for(f=0;f<150;f++)nes.frame();
 nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
 track=true; let si=1;
 while(f<S.hit+300){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
 for(const b of btns)nes.buttonUp(1,b);
 for(const s of ['select','select']){nes.buttonDown(1,C.BUTTON_SELECT);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,C.BUTTON_SELECT);for(let i=0;i<60;i++)nes.frame();}
}
// print free ranges >=8 in 0x300-0x7ff
let s=-1;const out=[];for(let a=0x2ff;a<=0x800;a++){const free=a<0x800&&!written[a];if(free&&s<0)s=a;if(!free&&s>=0){if(a-s>=3)out.push(s.toString(16)+'+'+(a-s));s=-1;}}
console.log(out.join(' '));
console.log('free bytes in 0x300-0x7ff:',Array.from(written.slice(0x300)).filter(x=>!x).length, 'free list', Array.from(written.keys()).filter(a=>a>=0x300&&!written[a]).map(a=>a.toString(16)).join(' '));
