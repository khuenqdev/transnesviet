// log PPU $2007 writes within a nametable address window with PC (CPU in NMI). usage: node pputrace.mjs rom "script" lo hi
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, script, lo, hi]=process.argv; const C=Controller;
const LO=parseInt(lo,16),HI=parseInt(hi,16);
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; let on=false,frame=0; const log=[];
const ow=cpu.write.bind(cpu);
cpu.write=function(a,v){ if(on&&a===0x2007){const va=nes.ppu.vramAddress; if(va>=LO&&va<=HI) log.push([frame,va.toString(16),v.toString(16),(cpu.REG_PC-1).toString(16)]);} return ow(a,v);};
const map={A:C.BUTTON_A,t:C.BUTTON_START};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F')for(let i=0;i<+a;i++){nes.frame();frame++;} else if(k==='P'){nes.buttonDown(1,map[a]);for(let i=0;i<4;i++){nes.frame();frame++}nes.buttonUp(1,map[a]);for(let i=0;i<10;i++){nes.frame();frame++}} else if(k==='T')on=true;}
const pcs=new Map();for(const l of log){pcs.set(l[3],(pcs.get(l[3])||0)+1);}
console.log('writes',log.length,'PCs',[...pcs.entries()].map(e=>e.join(' x')).join(', '));
const byF=new Map();for(const l of log){const k=l[0];if(!byF.has(k))byF.set(k,[]);byF.get(k).push(l);}for(const [k,v] of byF){console.log("frame",k,"first",v[0][1],"last",v[v.length-1][1],"n",v.length,"pcs",[...new Set(v.map(x=>x[3]))].join(","),"first bytes",v.slice(0,4).map(x=>x[2]).join(" "));}
