// spawn an object type via JSR $CEC5 then run frames, screenshot. usage: node spawn.mjs rom startScript type(hex) framesAfter out [pressScript]
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, pre, typeS, after='200', outp='spawn', post='']=process.argv; const C=Controller;
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const map={A:C.BUTTON_A,B:C.BUTTON_B,s:C.BUTTON_SELECT,t:C.BUTTON_START,u:C.BUTTON_UP,d:C.BUTTON_DOWN,l:C.BUTTON_LEFT,r:C.BUTTON_RIGHT};
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
function run(script){for(const cmd of script.split(',')){if(!cmd)continue;const k=cmd[0],a=cmd.slice(1);
 if(k==='F')for(let i=0;i<+a;i++)nes.frame(); else if(k==='P'){nes.buttonDown(1,map[a]);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,map[a]);for(let i=0;i<10;i++)nes.frame();} else if(k==='S')shot(a);}}
run(pre);
// call subroutine
function call(addr,A,X,Y){const cpu=nes.cpu; const sv={pc:cpu.REG_PC,a:cpu.REG_ACC,x:cpu.REG_X,y:cpu.REG_Y,sp:cpu.REG_SP,st:cpu.REG_STATUS};
 const SENT=0x0100; // fake return to unreachable sentinel
 // push return (sentinel-1)
 cpu.mem[0x100+cpu.REG_SP]=((SENT-1)>>8)&255; cpu.REG_SP--; cpu.mem[0x100+cpu.REG_SP]=(SENT-1)&255; cpu.REG_SP--;
 cpu.REG_PC=addr-1; cpu.REG_ACC=A;cpu.REG_X=X;cpu.REG_Y=Y;
 let n=0; while(cpu.REG_PC+1!==SENT&&n++<200000)cpu.emulate();
 console.log('call done instr',n,'carry',cpu.F_CARRY);
 cpu.REG_PC=sv.pc;cpu.REG_ACC=sv.a;cpu.REG_X=sv.x;cpu.REG_Y=sv.y;cpu.REG_SP=sv.sp;}
call(0xCEC5,parseInt(typeS,16),0,0);
run('F'+after+',Sa'+(post?','+post:''));
fs.writeFileSync(`${outp}.vram`,Buffer.from(nes.ppu.vramMem));
