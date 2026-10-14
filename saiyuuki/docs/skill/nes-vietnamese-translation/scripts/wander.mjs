// usage: node wander.mjs <rom> <route> <outdir> [seed] [segments]
import {mk,BTN} from './jsnes_lib.mjs';
import fs from 'fs';
const [rom,route,out,seedS='1',segS='60']=process.argv.slice(2);
let seed=+seedS; const rnd=()=>{seed=(seed*1664525+1013904223)>>>0; return seed/4294967296;};
const e=mk(rom); const m=e.nes.cpu.mem;
const seq=fs.readFileSync(route,'utf8').trim().split(/\s+/);
for(const c of seq){ if(/^F\d+$/.test(c)) e.frames(+c.slice(1)); else if(c[0]==='H'){const [b,n]=c.slice(1).split(':'); e.nes.buttonDown(1,BTN[b]); e.frames(+n); e.nes.buttonUp(1,BTN[b]); e.frames(4);} else {const [b,n='1']=c.split(':'); for(let i=0;i<+n;i++) e.press(b,5,25);} }
e.frames(40);
fs.mkdirSync(out,{recursive:true});
const dirs=['u','d','l','r']; let k=0;
for(let s=0;s<+segS;s++){ const d=dirs[Math.floor(rnd()*4)], n=20+Math.floor(rnd()*100);
  e.nes.buttonDown(1,BTN[d]); e.frames(n); e.nes.buttonUp(1,BTN[d]); e.frames(20);
  if(s%6===5){ e.shot(`${out}/w${String(k++).padStart(2,'0')}.png`); } }
console.log('done',k,'shots');
