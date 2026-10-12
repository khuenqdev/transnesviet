// Call the patched row-draw hook (T_INIT) directly for chosen rows/addresses and screenshot.
// usage: node calltest.mjs rom seq.json stop "F60,Ps,F80" calls.json outprefix
//  calls.json: [{"row":8,"addr":"21b5","count":5}, ...]  (applied in order, buffer drained between)
import {NES, Controller} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, seqf, stopS, script, callsf, outp]=process.argv; const C=Controller;
const S=JSON.parse(fs.readFileSync(seqf));
let fb=new Array(61440).fill(0);
const nes=new NES({onFrame:f=>{fb=f.slice()},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
const cpu=nes.cpu;
const btns=[C.BUTTON_A,C.BUTTON_B,C.BUTTON_UP,C.BUTTON_DOWN,C.BUTTON_LEFT,C.BUTTON_RIGHT];
function shot(n){const b=Buffer.alloc(61440*3);for(let i=0;i<61440;i++){const c=fb[i];b[i*3]=c&255;b[i*3+1]=(c>>8)&255;b[i*3+2]=(c>>16)&255;}
 fs.writeFileSync(`${outp}_${n}.ppm`,Buffer.concat([Buffer.from('P6 256 240 255\n'),b]));}
let f=0; for(f=0;f<150;f++)nes.frame();
nes.buttonDown(1,C.BUTTON_START);for(let i=0;i<4;i++){nes.frame();f++}nes.buttonUp(1,C.BUTTON_START);
let si=1;
while(f<+stopS){ if(si<S.seq.length&&S.seq[si].f===f){const cur=new Set(S.seq[si].hold);for(const b of btns)cur.has(b)?nes.buttonDown(1,b):nes.buttonUp(1,b);si++;}
  if(f>600)nes.cpu.mem[0x34c]=12; nes.frame(); f++; }
for(const b of btns)nes.buttonUp(1,b);
const map={A:C.BUTTON_A,B:C.BUTTON_B,s:C.BUTTON_SELECT,t:C.BUTTON_START,u:C.BUTTON_UP,d:C.BUTTON_DOWN,l:C.BUTTON_LEFT,r:C.BUTTON_RIGHT};
const fr=n=>{for(let i=0;i<n;i++){nes.cpu.mem[0x34c]=12;nes.frame();}};
for(const cmd of script.split(',')){const k=cmd[0],a=cmd.slice(1);
 if(k==='F')fr(+a); else if(k==='P'){nes.buttonDown(1,map[a]);for(let i=0;i<4;i++)nes.frame();nes.buttonUp(1,map[a]);fr(10);}}
const T_INIT=0xC03A, TRAP=0xE000;
function call(row,addr,count,steps=1){
  const save={a:cpu.REG_ACC,x:cpu.REG_X,y:cpu.REG_Y,sp:cpu.REG_SP,pc:cpu.REG_PC,st:cpu.REG_STATUS,
    fc:cpu.F_CARRY,fz:cpu.F_ZERO,fn:cpu.F_SIGN,fv:cpu.F_OVERFLOW,fi:cpu.F_INTERRUPT,fd:cpu.F_DECIMAL,fb:cpu.F_BRK,fnu:cpu.F_NOTUSED};
  const m=cpu.mem; m[0x51]=row; m[0x52]=0; m[4]=addr&255; m[5]=addr>>8; m[0x53]=count; m[0x59]=0; 
  // push return
  cpu.mem[0x100+cpu.REG_SP]=((TRAP-1)>>8)&255; cpu.REG_SP--; cpu.mem[0x100+cpu.REG_SP]=(TRAP-1)&255; cpu.REG_SP--;
  cpu.REG_PC=T_INIT-1; cpu.REG_Y=count;
  let n=0; while(cpu.REG_PC+1!==TRAP&&n++<400000)cpu.emulate();
  const carry=cpu.F_CARRY;
  Object.assign(cpu,{REG_ACC:save.a,REG_X:save.x,REG_Y:save.y,REG_SP:save.sp,REG_PC:save.pc,F_CARRY:save.fc,F_ZERO:save.fz,F_SIGN:save.fn,F_OVERFLOW:save.fv,F_INTERRUPT:save.fi,F_DECIMAL:save.fd,F_BRK:save.fb,F_NOTUSED:save.fnu});
  return carry;
}
for(const c of JSON.parse(fs.readFileSync(callsf))){
  let tries=0; while(call(c.row,parseInt(c.addr,16),c.count)&&tries++<200){ nes.frame(); }
  fr(6);
}
fr(20); shot('end');
