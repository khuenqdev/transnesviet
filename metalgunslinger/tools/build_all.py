#!/usr/bin/env python3
"""Full Vietnamese build (Stages 2-6): text + layout fixes -> name labels -> sprite text (plates/menus/title)
-> pause-screen BG text -> title subtitle (Stage 6) -> ROM (+ IPS)
usage (in work dir): build_all.py ../metal_gunslinger.gba menu_vi.tsv story_vi.txt out.gba [out.ips]"""
import sys, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_vi, stage4_gfx, ips
rom_p,menu,story,out=sys.argv[1:5]; orig=open(rom_p,'rb').read()
d=build_vi.build(orig,menu,story,os.path.dirname(os.path.abspath(out)))
if d is None: sys.exit(1)
for l in stage4_gfx.apply(d,orig): print('  gfx:',l)
for l in stage4_gfx.apply_stage5(d,orig)+stage4_gfx.apply_stage5_bg(d,orig): print('  gfx5:',l)
for l in stage4_gfx.apply_stage6(d,orig): print('  gfx6:',l)
open(out,'wb').write(d)
if len(sys.argv)>5: open(sys.argv[5],'wb').write(ips.create(orig,bytes(d))); print('IPS written',sys.argv[5])
