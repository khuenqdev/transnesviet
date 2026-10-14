// usage: node npcdrift.mjs <rom> <route> <dirseq e.g. u:96,l:96> [shotprefix]
// Counts frames where a non-player sprite changes WORLD position (screen pos + scroll) although it was on screen in the previous frame.
import {mk,BTN} from './jsnes_lib.mjs';
import fs from 'fs';
const [rom,route,dirs,pre]=process.argv.slice(2);
const e=mk(rom); const m=e.nes.cpu.mem;
const seq=fs.readFileSync(route,'utf8').trim().split(/\s+/);
for(const c of seq){ if(/^F\d+$/.test(c)) e.frames(+c.slice(1)); else if(c[0]==='H'){const [b,n]=c.slice(1).split(':'); e.nes.buttonDown(1,BTN[b]); e.frames(+n); e.nes.buttonUp(1,BTN[b]); e.frames(4);} else {const [b,n='1']=c.split(':'); for(let i=0;i<+n;i++) e.press(b,5,25);} }
e.frames(40);
const sprites=()=>{const o=[]; for(let i=0;i<64;i++){const y=m[0x500+i*4]; if(y<0xEF) o.push({y:y,t:m[0x501+i*4],a:m[0x502+i*4],x:m[0x503+i*4]});} return o;};
const sx=()=>m[0x02]+((m[0x00]&1)?256:0), sy=()=>m[0x03];
let rest=0,restOff=0;let tracks=[], frameNo=0, done=[];
const flush=()=>{for(const t of tracks) done.push(t); tracks=[];};
for(const d of dirs.split(',')){
  const [k,n]=d.split(':'); e.nes.buttonDown(1,BTN[k]);
  for(let f=0;f<+n;f++){ e.frames(1); frameNo++;
    const S=sprites().map(s=>({wx:(s.x+m[0x02]+(m[0x00]&1?256:0))&0x1FF, wy:(s.y+m[0x03]+(m[0x00]&2?240:0))%480, sx:s.x, sy:s.y, a:s.a&3}))
      .filter(s=>!(s.sx<16||s.sx>240||s.sy<16||s.sy>215) && !(s.sx>110&&s.sx<180&&s.sy>96&&s.sy<150));
    const used=new Set(); const next=[];
    for(const t of tracks){ let best=-1,bd=99; S.forEach((s,i)=>{ if(used.has(i)||s.a!==t.a) return; const dd=Math.abs(s.wx-t.wx)+Math.abs(s.wy-t.wy); if(dd<bd){bd=dd;best=i;} });
      if(best>=0&&bd<=5){used.add(best); const s=S[best]; t.wx=s.wx;t.wy=s.wy;t.life++;(t.h=t.h||[]).push(s.wx+','+s.wy+'@'+s.sx+','+s.sy+'/'+m[0x32]);t.maxd=Math.max(t.maxd,Math.abs(s.wx-t.x0)+Math.abs(s.wy-t.y0)); next.push(t);} else done.push(t); }
    S.forEach((s,i)=>{ if(!used.has(i)) next.push({wx:s.wx,wy:s.wy,x0:s.wx,y0:s.wy,a:s.a,life:1,maxd:0}); });
    tracks=next; }
  e.nes.buttonUp(1,BTN[k]); e.frames(30); flush();
  for(const s of sprites()){ const sx_=s.x,sy_=s.y; if(sx_<16||sx_>240||sy_<16||sy_>215||(sx_>110&&sx_<180&&sy_>96&&sy_<150)) continue; const wx=(s.x+m[0x02]+(m[0x00]&1?256:0))&0x1FF, wy=(s.y+m[0x03]+(m[0x00]&2?240:0))%480; rest++; if(wx%8||wy%8){ restOff++; if(process.env.OFF) console.log('   OFF seg',k+n,'wx,wy',wx,wy,'screen',s.x,s.y,'$450',m[0x450],'$32',m[0x32]); } }
  if(pre) e.shot(`${pre}_${k}${n}.png`);
}
const long=done.filter(t=>t.life>=15);
const drift=long.filter(t=>t.maxd>=4);
const fr=v=>{v=Math.abs(v)%16;return Math.min(v,16-v);};
const g8=v=>{v=((v%8)+8)%8;return Math.min(v,8-v);};
const odd=long.filter(t=>g8(t.wx)>0||g8(t.wy)>0);
if(process.env.DETAIL) for(const t of long.filter(t=>{const r=t.maxd%16;return r>3&&r<13;}).slice(0,3)) console.log('   TRACK',t.x0,t.y0,'a',t.a,(t.h||[]).join(' '));
const bad16=long.filter(t=>{const r=t.maxd%16; return r>3&&r<13;});
console.log('  tracks whose max displacement is NOT a whole number of tiles (+-3px lag):',bad16.length,'of',long.length,' values',bad16.map(t=>t.maxd).slice(0,10).join(','));
console.log('  at-rest sprites',rest,'off 8-px grid:',restOff);
console.log(rom.split('/').pop(),'tracks>=15f',long.length,'drifting(>=4px)',drift.length,'max drift',Math.max(0,...long.map(t=>t.maxd)),'| final position off the 8-px sprite grid:',odd.length);
