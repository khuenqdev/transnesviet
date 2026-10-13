import {mk} from './lib.mjs';
import fs from 'fs';
// usage: node play.mjs rom outdir "cmds"   cmds space-separated: F<n> run, <btn>[:n] press (A,B,s,t,u,d,l,r) with n repeats, S<name> shot, W<file> save state, L<file> load state
const [,,rom,out,cmds]=process.argv; fs.mkdirSync(out,{recursive:true});
const e=mk(rom);
for(const c of cmds.trim().split(/\s+/)){
  if(c[0]==='F'&&/^F\d+$/.test(c)) e.frames(+c.slice(1));
  else if(c[0]==='S') e.shot(`${out}/${c.slice(1)}.png`);
  else if(c[0]==='W') fs.writeFileSync(c.slice(1),JSON.stringify(e.nes.toJSON()));
  else if(c[0]==='L'){e.nes.fromJSON(JSON.parse(fs.readFileSync(c.slice(1))));}
  else if(c[0]==='H'){const [b,n]=c.slice(1).split(':'); e.nes.buttonDown(1,(await import('./lib.mjs')).BTN[b]); e.frames(+n); e.nes.buttonUp(1,(await import('./lib.mjs')).BTN[b]); e.frames(4);}
  else {const [b,n='1']=c.split(':'); for(let i=0;i<+n;i++) e.press(b,5,25);}
}
