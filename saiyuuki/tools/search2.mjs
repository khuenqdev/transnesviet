// random-input search until CPU reads ROM address of target text row. usage: node search.mjs rom seed maxFrames targetAddr(hex) outfile
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seedS, maxF='4000', tgt='a037', outf='seq.json']=process.argv; const C=Controller;
let seed=+seedS; const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
const [TL,TH]=tgt.split('-').map(x=>parseInt(x,16));
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
let hit=-1,hitA=0; const ol=nes.cpu.load.bind(nes.cpu);
nes.cpu.load=function(a){ if(a>=TL&&a<=TH&&hit<0&&f>900){hit=f;hitA=a;} return ol(a);};
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT,C.BUTTON_START,C.BUTTON_SELECT];
let f=0; const seq=[]; let cur=new Set();
for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
seq.push({f:f,hold:[]});
for(;f<+maxF&&hit<0;f++){
  if(f%12===0){
    cur=new Set(); 
    if(rnd()<0.85)cur.add(C.BUTTON_RIGHT); else if(rnd()<0.3)cur.add(C.BUTTON_LEFT);
    if(rnd()<0.5)cur.add(C.BUTTON_A); if(rnd()<0.15)cur.add(C.BUTTON_B); if(rnd()<0.4)cur.add(C.BUTTON_UP); if(rnd()<0.05)cur.add(C.BUTTON_DOWN); if(rnd()<0.04)cur.add(C.BUTTON_START); if(rnd()<0.04)cur.add(C.BUTTON_SELECT);
    seq.push({f,hold:[...cur]});
    for(const b of btns){cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);}
  }
  if(f>600){nes.cpu.mem[0x34c]=12;}
  nes.frame();
}
if(hit>=0){fs.writeFileSync(outf,JSON.stringify({seed:+seedS,hit,seq}));console.log('HIT seed',seedS,'frame',hit,'addr',hitA.toString(16));}
else console.log('miss seed',seedS);
