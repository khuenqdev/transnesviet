// usage: node stack.mjs rom "script" addr(hex) -> at first read of addr print stack return addrs, regs, zp
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, script, ad, nth='1'] = process.argv; const A=parseInt(ad,16);
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu; let on=false,cnt=0; const ol=cpu.load.bind(cpu);
cpu.load=function(a){ if(on&&a===A&&++cnt==+nth){ const sp=cpu.REG_SP; const st=[];
 for(let s=sp+1;s<0x100;s+=1) st.push(cpu.mem[0x100+s]);
 const rets=[];for(let i=0;i+1<st.length;i+=2) rets.push(((st[i+1]<<8|st[i])+1).toString(16));
 console.log('SP',sp.toString(16),'stack raw',st.map(x=>x.toString(16)).join(' '));
 console.log('zp',Array.from(cpu.mem.slice(0,0x40)).map(x=>x.toString(16).padStart(2,'0')).join(' '));
 console.log('A X Y',cpu.REG_ACC,cpu.REG_X,cpu.REG_Y,'bank8000 byte',cpu.mem[0x8000]);}
 return ol(a);};
const map={A:Controller.BUTTON_A,B:Controller.BUTTON_B,s:Controller.BUTTON_SELECT,t:Controller.BUTTON_START,u:Controller.BUTTON_UP,d:Controller.BUTTON_DOWN,l:Controller.BUTTON_LEFT,r:Controller.BUTTON_RIGHT};
const frames=n=>{for(let i=0;i<n;i++)nes.frame();};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F')frames(+a); else if(k==='P'){nes.buttonDown(1,map[a]);frames(4);nes.buttonUp(1,map[a]);frames(10);} else if(k==='T')on=true;}
