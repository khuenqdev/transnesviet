#!/usr/bin/env python3
"""Stage 5 – sprite text replacements: (resource gfx offset, [anims sharing tiles], text, options)"""
JOBS=[]
# area name plates (proper nouns kept in Latin, as in the script)
for g,first,opt in ((0x5BB354,5,{'xr':(-52,46),'E':2}),(0x5C315C,1,{'E':2}),(0x5C48C0,2,{'E':2}),(0x5C6E90,2,{'E':2})):
    for k,name in enumerate(['HEAVEN','NAVANHO','GOLD MOUNTAIN','IRON TRAIN','COSMOPOLITAN','LAND']):
        JOBS.append((g,[first+k],name,dict(opt)))
for k,name in enumerate(['NAVANHO','GOLD MOUNTAIN','IRON TRAIN','COSMOPOLITAN']):
    JOBS.append((0x5CC2B4,[1+k],name,{'pieces':5,'xr':(-100,-2),'E':2}))
# game-over menu (blue glow, 2 palette states share tiles)
for a,t in ((1,'CHƠI LẠI MÀN'),(2,'TẢI DỮ LIỆU'),(3,'TIÊU ĐỀ')):
    JOBS.append((0x5BEBB4,[a,a+3],t,{'R':3,'LUM':215,'sy':2,'captop':-6,'E':5,'clear_all':True}))
# data select buttons コピー / 削除
JOBS.append((0x5C6E90,[8],'CHÉP',{'xr':(-48,-8),'LUM':215,'E':2,'noise':0}))
JOBS.append((0x5C6E90,[8],'XÓA',{'xr':(0,40),'LUM':215,'E':2,'noise':0}))
# title copyright: keep "© 2002", replace アットマーク
JOBS.append((0x5BD7DC,[0],'ATMARK',{'xr':(-4,88),'LUM':215,'R':1,'E':3}))
