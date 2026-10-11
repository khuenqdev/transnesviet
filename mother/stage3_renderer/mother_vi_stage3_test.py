#!/usr/bin/env python3
"""
mother_vi_stage3_test.py - emulator verification for the stage-3 renderer.

  python mother_vi_stage3_test.py regress ORIGINAL.nes STAGE3.nes OUTDIR
      Plays both ROMs from power-on with the same scripted input (title -> file select ->
      naming -> intro -> bedroom -> Command menu -> Talk) and compares the screens at 4
      checkpoints. English text must render pixel-identically through the new code paths
      (dialogue now uses the type-$0B record + new NMI handler).

  python mother_vi_stage3_test.py demo TEST.nes OUTDIR
      Plays the TEST ROM (mother_vi_testrom.py) to the bedroom, sets Ninten's name to "Hùng",
      re-opens the menu (Name window = fixed-width field printer) and uses Talk, which shows the
      7-line Vietnamese test message: typewriter, {Ninten} insert, scrolling, all mark combos.
Each run takes a few minutes in pure Python.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from mmc3 import MMC3
from mother_vi_preview import press, idle, screen
from mother_vi_codec import encode

def to_field(n, cps=None):
    def cp(name):
        if cps is not None: cps.append((name, screen(n)))
    idle(n, 400); press(n, 'START', 4, 120); press(n, 'START', 4, 120); press(n, 'A', 4, 120)
    idle(n, 200); press(n, 'START', 4, 150); press(n, 'A', 4, 150); cp('file_select_naming')
    for _ in range(5):
        for b in ['A', 'A', 'D', 'D', 'D', 'D', 'R', 'A']: press(n, b, 3, 12)
        idle(n, 60)
    press(n, 'A', 3, 30)
    for i in range(8):
        idle(n, 150)
        if i == 3: press(n, 'A', 3, 10)
    cp('intro_text')
    for i in range(30): press(n, 'A', 2, 90)
    cp('field_menu')

def regress(orig, new, outdir):
    os.makedirs(outdir, exist_ok=True)
    res = []
    ca, cb = [], []
    for rom, cps in ((orig, ca), (new, cb)):
        n = MMC3(open(rom, 'rb').read())
        to_field(n, cps)
        press(n, 'A', 2, 200); cps.append(('dialogue', screen(n)))
    for (name, a), (_, b) in zip(ca, cb):
        same = bool((a == b).all())
        res.append('%-20s %s' % (name, 'identical' if same else 'DIFFERENT'))
        Image.fromarray(b).resize((512, 480), Image.NEAREST).save(os.path.join(outdir, 'regress_%s.png' % name))
    open(os.path.join(outdir, 'regression.txt'), 'w').write('\n'.join(res) + '\n')
    print('\n'.join(res))

def demo(test_rom, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = MMC3(open(test_rom, 'rb').read())
    to_field(n)
    for i, b in enumerate(encode('Hùng')):          # Ninten's name in save RAM ($7478)
        n.prgram[0x7478 - 0x6000 + i] = b
    shots = []
    press(n, 'B', 2, 60); press(n, 'A', 2, 60); shots.append(('menu_name_window', screen(n)))
    press(n, 'A', 2, 0)                              # Talk -> message 901 (test message)
    for k in range(14):
        idle(n, 25); shots.append(('typing_%02d' % k, screen(n)))
    for k in range(4):
        press(n, 'A', 2, 0)
        for j in range(3):
            idle(n, 25); shots.append(('page%d_%d' % (k, j), screen(n)))
    for name, img in shots:
        Image.fromarray(img).resize((512, 480), Image.NEAREST).save(os.path.join(outdir, 'demo_%s.png' % name))
    # contact sheet of the dialogue window
    sel = [s for s in shots if s[0] in ('menu_name_window', 'typing_02', 'typing_05', 'typing_13',
                                        'page0_2', 'page1_2', 'page2_2')]
    W = Image.new('RGB', (512 * 2, 200 * ((len(sel) + 1) // 2)))
    for i, (name, img) in enumerate(sel):
        im = Image.fromarray(img).crop((0, 140, 256, 240)).resize((512, 200), Image.NEAREST)
        W.paste(im, ((i % 2) * 512, (i // 2) * 200))
    W.save(os.path.join(outdir, 'mother_vi_stage3_demo_sheet.png'))
    print('demo frames:', len(shots))

if __name__ == '__main__':
    if sys.argv[1] == 'regress':
        regress(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        demo(sys.argv[2], sys.argv[3])
