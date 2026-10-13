import {mk} from './lib.mjs';
const e=mk(process.argv[2]); const cpu=e.nes.cpu,m=e.nes.mmap; m.loadRomBank(31,0xC000); cpu.emulate(); m.loadRomBank(process.argv[3]==='jp'?2:0x11,0x8000);
let bad=0;for(let i=0;i<78;i++){cpu.mem[0x2F]=i;cpu.mem[0xE0]=0;cpu.mem[0xE1]=0;cpu.mem[0x37]=0;
 let sp=0xFD;cpu.mem[0x100+sp]=0xBE;cpu.mem[0x100+sp-1]=0xEF;cpu.REG_SP=sp-2;cpu.REG_PC=0xD9ED-1;let n=0;while(cpu.REG_PC+1!==0xBEF0&&n++<9999)cpu.emulate();
 const got=cpu.mem[0xE0]|cpu.mem[0xE1]<<8; if(got!==0x80A2+2*i){bad++;if(bad<4)console.log(i,got.toString(16));}}
console.log('B bad',bad);
