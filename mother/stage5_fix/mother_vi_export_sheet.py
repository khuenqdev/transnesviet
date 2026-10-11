#!/usr/bin/env python3
"""Export every string (English, Vietnamese source, in-game layout) to a CSV for review.
usage: python mother_vi_export_sheet.py mother_script.json translations out.csv"""
import csv, importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mother_vi_build import load_translations, lay
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def main(script, tr, out):
    import json
    J = json.load(open(script, encoding='utf-8')); T = load_translations(tr)
    ui = T.get('__UI__', {})
    rows = []
    for s in J['script_segments']:
        if s['category'] in ('empty', 'placeholder'): continue
        vn = T.get(s['seg'], '')
        rows.append([s['seg'], 'script', s['category'], ' '.join(map(str, s['ids'][:10])), s['text'], vn,
                     lay(vn, s) if vn else ''])
    for p in J['prg_strings']:
        vn = T.get(p['key']) or ui.get(p['key'], '')
        rows.append([p['key'], 'PRG', p['category'], '', p['text'], vn, vn])
    intro = load(os.path.join(tr, 'vn_intro.py'), 'vn_intro')
    naming = load(os.path.join(tr, 'vn_naming.py'), 'vn_naming')
    en = {x['key']: x['text'] for x in J['prg_strings']}
    rows.append(['STAGE5_INTRO1', 'stage5', 'intro', '', en.get('P33CD0', ''), '\n'.join(intro.INTRO1), '\n'.join(intro.INTRO1)])
    rows.append(['STAGE5_INTRO2', 'stage5', 'intro', '', en.get('P33E7D', ''), '\n'.join(intro.INTRO2), '\n'.join(intro.INTRO2)])
    N = naming.NAMING
    for key, eng in (('back_end', '  ◆Back  ◆End  '), ('previous', '   ◆Previous   '), ('fav_food', 'Favorite food: '),
                     ('is_ok', '  Is this OK?   '), ('yes_no', '     Yes No     ')):
        rows.append(['STAGE5_' + key.upper(), 'stage5', 'naming_screen', '', eng, N[key], N[key]])
    rows.append(['STAGE5_ERROR', 'stage5', 'naming_screen', '', en.get('P33B98', ''), '\n'.join(N['error']), '\n'.join(N['error'])])
    rows.append(['STAGE5_KEYBOARD', 'stage5', 'name_entry', '', '\n'.join(en.get(k, '') for k in ('P33C70', 'P33C80', 'P33C90', 'P33CA0')),
                 '\n'.join(naming.KEYBOARD), '\n'.join(naming.KEYBOARD)])
    with open(out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['key', 'source', 'category', 'ids', 'english', 'vietnamese', 'in_game_layout']); w.writerows(rows)
    print(len(rows), 'rows,', sum(1 for r in rows if r[5]), 'translated')
if __name__ == '__main__':
    main(*sys.argv[1:4])
