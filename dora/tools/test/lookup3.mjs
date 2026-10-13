import {mk} from './lib.mjs';
const e=mk(process.argv[2]); const cpu=e.nes.cpu,m=e.nes.mmap; m.loadRomBank(31,0xC000); cpu.emulate();
const counts=[3,2,4,8,4];m.loadRomBank(0x11,0x8000);
const bank=e.nes.cpu.mem; const rd=a=>bank[a]|bank[a+1]<<8;
const ptr=i=>rd(0x8143+2*i);
const c1=ptr(1);
for(let sub=0;sub<5;sub++)for(let k=0;k<counts[sub];k++){
 cpu.mem[0xEF]=0;cpu.mem[0xED]=sub;cpu.mem[0x2E]=0xC0+k;cpu.mem[0xE0]=0;cpu.mem[0xE1]=0;
 let sp=0xFD;cpu.mem[0x100+sp]=0xBE;cpu.mem[0x100+sp-1]=0xEF;cpu.REG_SP=sp-2;cpu.REG_PC=0xD915-1;let n=0;while(cpu.REG_PC+1!==0xBEF0&&n++<9999)cpu.emulate();
 const ea=cpu.mem[0xE0]|cpu.mem[0xE1]<<8; const idx=counts.slice(0,sub).reduce((a,b)=>a+b,0)+k;
 const got=rd(ea), want=ptr(idx);
 console.log('sub',sub,'k',k,'want C'+idx,want.toString(16),'got',got.toString(16), got===want?'ok':(got===c1?'<<< = C1 (Shizuka)':''));
}
