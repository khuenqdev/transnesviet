import {mk} from './lib.mjs';
import fs from 'fs';
// usage: node force_msg.mjs rom out sub k   (triggers C-event message sub/k when the Tim command is used)
const [,,rom,out,subS,kS,tag]=process.argv; fs.mkdirSync(out,{recursive:true});
const e=mk(rom); const cpu=e.nes.cpu; let armed=false, fired=0;
const orig=cpu.emulate.bind(cpu);
cpu.emulate=function(){ if(armed&&cpu.REG_PC+1===0xD8A5){ cpu.mem[0x2E]=0xC0+(+kS); cpu.mem[0xED]=+subS; cpu.mem[0xEF]=0; fired++; armed=false; } return orig(); };
const seq=fs.readFileSync('full_to_booth.txt','utf8').trim().split(/\s+/);
const {BTN}=await import('./lib.mjs');
for(const c of seq){ if(/^F\d+$/.test(c)) e.frames(+c.slice(1)); else if(c[0]==='H'){const [b,n]=c.slice(1).split(':'); e.nes.buttonDown(1,BTN[b]); e.frames(+n); e.nes.buttonUp(1,BTN[b]); e.frames(4);} else {const [b,n='1']=c.split(':'); for(let i=0;i<+n;i++) e.press(b,5,25);} }
armed=true; e.press('A'); e.frames(40); e.press('d'); e.frames(10); e.press('A');
for(let i=0;i<4;i++){ e.frames(70); e.shot(`${out}/${tag||'m'}${i}.png`); e.press('A'); }
console.log('fired',fired);
