// at rest after random-ish walking segments: compare logical NPC tile (RAM $420.. table x,y) with sprite world position
import {mk,BTN} from './jsnes_lib.mjs';
import fs from 'fs';
const [rom,route,segs]=process.argv.slice(2);
const e=mk(rom); const m=e.nes.cpu.mem;
const seq=fs.readFileSync(route,'utf8').trim().split(/\s+/);
for(const c of seq){ if(/^F\d+$/.test(c)) e.frames(+c.slice(1)); else if(c[0]==='H'){const [b,nn]=c.slice(1).split(':'); e.nes.buttonDown(1,BTN[b]); e.frames(+nn); e.nes.buttonUp(1,BTN[b]); e.frames(4);} else {const [b,nn='1']=c.split(':'); for(let i=0;i<+nn;i++) e.press(b,5,25);} }
e.frames(40);
let tot=0,bad=0; const hist={};
for(const p of segs.split(',')){const [d,c]=p.split(':'); e.nes.buttonDown(1,BTN[d]); e.frames(+c); e.nes.buttonUp(1,BTN[d]); e.frames(70);
  const S=[];for(let i=0;i<64;i++){const y=m[0x500+i*4];if(y<0xEF)S.push({wx:(m[0x503+i*4]+m[2]+(m[0]&1?256:0))&0x1ff,wy:(m[0x500+i*4]+m[3]+(m[0]&2?240:0))%480,sx:m[0x503+i*4],sy:y});}
  for(let a=0x420;a<0x450;a+=4){ const tx=m[a],ty=m[a+1]; if(tx===0xff) break;
    // sprites of this NPC: those whose world pos is within (tx*16-8..+24, ty*16-24..+8)
    const near=S.filter(s=>s.sx>8&&s.sx<248&&s.sy>8&&s.sy<225&&Math.abs(s.wx-tx*16)<20&&Math.abs((s.wy+0)-ty*16)<24);
    if(!near.length) continue; const minx=Math.min(...near.map(s=>s.wx)); tot++; const dx=(minx-tx*16); hist[dx]=(hist[dx]||0)+1; if(dx!==0) bad++; } }
console.log(rom.split('/').pop(),'NPC samples',tot,'x-offset histogram (sprite left edge - tile*16):',JSON.stringify(hist));
