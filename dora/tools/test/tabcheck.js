const fs=require('fs');const comp=require('/home/claude/dora/in/dora/tools/compile.js');const RES={};const orig=comp.compileGroup;comp.compileGroup=(s,b,k)=>{const r=orig(s,b,k);RES[k]=r;return r;};
const B=require('/home/claude/dora/in/dora/tools/build.js');B.build({});
const jp=fs.readFileSync('work/jp.nes'), vn=fs.readFileSync(process.argv[2]);
const dir='script/';const rd=g=>fs.readdirSync(dir).filter(f=>f[0]==g).sort().map(f=>fs.readFileSync(dir+f,'utf8')).join('\n');
const GA=[0x11,0x12,0x13,0x14],GE=[0x15,0x16,0x17,0x18];
const A=RES.A,E=RES.E;
const inv=(res,banks)=>{const m={};for(const b of res.blocks)m[banks[b.bank]+':'+b.addr]=b.label;return m;};
const iA=inv(A,GA),iE=inv(E,GE);
const bk=(rom,b)=>rom.slice(16+b*0x4000,16+(b+1)*0x4000);
function chk(name,jb,jat,vb,vat,n,inv){let bad=0;
 for(let i=0;i<n;i++){const jt=bk(jp,jb).readUInt16LE(jat-0x8000+2*i);
  const v=bk(vn,vb).readUInt16LE(vat-0x8000+2*i);const bank=vb+(v>>14),addr=0x8000+(v&0x3FFF);
  const jl='L'+jt.toString(16), vl=inv[bank+':'+addr];
  if(jl!==vl){bad++;console.log(name,i,'jp',jl,'vn',vl,bank.toString(16),addr.toString(16));}}
 console.log(name,'entries',n,'bad',bad);}
chk('A',2,0x8000,0x11,0x8000,81,iA);chk('B',2,0x80A2,0x11,0x80A2,78,iA);chk('C',2,0x8143,0x11,0x8143,21,iA);chk('D',2,0x816D,0x11,0x816D,1,iA);
const n3=jp.slice(16+3*0x4000,16+3*0x4000+5).reduce((a,b)=>a+b,0);chk('E',3,0x8005,0x15,0x8005,n3,iE);
