#!/usr/bin/env python3
"""Stage 4 QA – play dialogue scenes through scene-jump ROMs and screenshot each page (press A between pages).
Needs t/vi_game0.st (state saved just before scene 2, see intro.txt).
usage: run_scenes.py rom.gba outdir [scene,scene,...]"""
import json,subprocess,sys,os
rom,out=sys.argv[1],sys.argv[2]; only=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
MSG=json.load(open('../messages.json',encoding='utf-8')); cnt={}
for m in MSG: cnt[m['scene']]=cnt.get(m['scene'],0)+len(m['refs'])//2+1
os.makedirs(out,exist_ok=True)
for s in sorted(cnt):
    if (only and s not in only) or s in (1,40,45): continue
    subprocess.run(['python3','../tools/scene_jump.py',rom,out+'/sj%d.gba'%s,str(s)],check=True)
    L=['load t/vi_game0.st','run 2100']
    for k in range(cnt[s]+2): L+=['run 130','shot %s/s%02d_%03d.ppm'%(out,s,k),'press A 3']
    open(out+'/sj%d.txt'%s,'w').write('\n'.join(L)+'\n')
    subprocess.run(['./gbaemu',out+'/sj%d.gba'%s,out+'/sj%d.txt'%s],check=True); print('scene',s,flush=True)
