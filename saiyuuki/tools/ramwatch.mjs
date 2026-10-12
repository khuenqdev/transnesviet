import {NES} from '/home/claude/vendor/jsnes/src/index.js';
import fs from 'fs';
const [,, romPath, f1, ...addrs]=process.argv;
const nes=new NES({onFrame:()=>{},onAudioSample:()=>{},emulateSound:false});
nes.loadROM(fs.readFileSync(romPath).toString('binary'));
let last='';
for(let f=0;f<+f1;f++){ nes.frame(); const s=addrs.map(a=>nes.cpu.mem[parseInt(a,16)].toString(16)).join(' '); if(s!==last){console.log(f,s);last=s;} }
