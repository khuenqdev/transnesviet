import {mk} from './lib.mjs';
const rom=process.argv[2]; const e=mk(rom); const cpu=e.nes.cpu, m=e.nes.mmap;
const jp=process.argv[3]==='jp';
const hdr=[0x11,0x46,0x24,0x41,0x28];
m.loadRomBank(31,0xC000);
cpu.emulate(); // consume reset
function call(addr){let sp=0xFD;cpu.mem[0x100+sp]=0xBE;cpu.mem[0x100+sp-1]=0xEF;cpu.REG_SP=sp-2;cpu.REG_PC=addr-1;let n=0;while(cpu.REG_PC+1!==0xBEF0&&n++<20000)cpu.emulate();return n<20000;}
let bad=0,tot=0;
// E table (group E): bank 3 (jp) or 0x15 (vn)
const eb=jp?3:0x15; const ab=jp?2:0x11;
for(let sub=0;sub<5;sub++)for(let k=0;k<hdr[sub];k++){
  m.loadRomBank(eb,0x8000);
  cpu.mem[0xEF]=0;cpu.mem[0xED]=sub;cpu.mem[0x2E]=k;cpu.mem[0xE0]=0;cpu.mem[0xE1]=0;
  call(0xD8D8);
  const idx=hdr.slice(0,sub).reduce((a,b)=>a+b,0)+k; const want=0x8005+2*idx; const got=cpu.mem[0xE0]|cpu.mem[0xE1]<<8;
  tot++; if(got!==want){bad++;if(bad<6)console.log('E sub',sub,'k',k,want.toString(16),got.toString(16));}
}
for(let i=0;i<81;i++){ if(i===0x18)continue;
  m.loadRomBank(ab,0x8000); cpu.mem[0x2F]=i; cpu.mem[0x2E]=0xFF; cpu.mem[0xE0]=0;cpu.mem[0xE1]=0;cpu.mem[0x37]=0;
  call(0xD952); const want=0x8000+2*i, got=cpu.mem[0xE0]|cpu.mem[0xE1]<<8; tot++; if(got!==want){bad++;console.log('A',i,want.toString(16),got.toString(16));}}
console.log(rom,'checked',tot,'bad',bad);
