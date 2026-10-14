#!/usr/bin/env python3
"""Stage 4/5 – apply all graphic translations to a ROM image."""
import sys
sys.path.insert(0,__file__.rsplit('/',1)[0])
import labels, label_maker, gfx_insert, anim, sprite_text
def apply(d, orig):
    """Stage 4: speaker name labels."""
    gfx_insert.log.clear(); pool=label_maker.plate_rows(orig)
    for g,t in label_maker.NAMES.items():
        lab,img,o=label_maker.make(orig,g,t,pool,seed=g)
        gfx_insert.put_lz(d,g,lab['gfx_len'],labels.from_index_image(lab,img,o),'label '+t)
    return list(gfx_insert.log)
def apply_stage5(d, orig):
    """Stage 5: repaint Japanese text in sprite resources (area plates, menus, title)."""
    from stage5_jobs import JOBS
    R={r['gfx']:r for r in anim.find_resources(orig)}
    for r in R.values(): r['tiles']=bytearray(r['tiles'])
    done=[]
    for g,an,txt,opt in JOBS:
        r=R[g]; ps,img,new,lost=sprite_text.repaint(orig,r,an,txt,**opt)
        sprite_text.write_back(r,ps,img,new); done.append(g)
    log=[]
    for g in dict.fromkeys(done):
        r=R[g]; gfx_insert.log.clear(); gfx_insert.put_lz(d,g,r['gfx_len'],bytes(r['tiles']),'sprites %06X'%g); log+=gfx_insert.log
    return log
def apply_stage5_bg(d, orig):
    """Stage 5: repaint small Japanese text on BG tile graphics (pause screen)."""
    import bg_text
    from stage5_bgjobs import BGJOBS
    groups={}
    for spec,m,rect,txt,opt in BGJOBS:
        bg=groups.get(spec) or groups.setdefault(spec,bg_text.BG(orig,*spec))
        bg.repaint(m,rect,txt,top=rect[1]+1,**opt)
    log=[]
    for spec,bg in groups.items():
        gfx_insert.log.clear(); gfx_insert.put_lz(d,spec[0],bg.tlen,bytes(bg.tiles),'bg tiles %06X'%spec[0]); log+=gfx_insert.log
    return log
def apply_stage6(d, orig):
    """Stage 6: title-logo subtitle katakana -> 'TIẾNG VIỆT'."""
    import title_sub
    return title_sub.apply(d, orig)
