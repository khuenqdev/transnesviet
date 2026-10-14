#!/usr/bin/env python3
"""Stage 5 – BG text jobs: (BG (tiles,(maps),palette), map index, rect x0,y0,x1,y1, text, options)"""
PAUSE=(0x6BC63C,(0x6BD698,0x6BD8A8),0x6BD628)
BGJOBS=[(PAUSE,0,(8,32,33,39),'TIME',{'bgc':0}),(PAUSE,0,(8,40,33,47),'ENEMY',{'bgc':0}),(PAUSE,0,(8,48,33,55),'SCORE',{'bgc':0}),
        (PAUSE,0,(133,96,181,103),'BILLY',{'left':137}),(PAUSE,0,(133,104,181,111),'MACDOLEANE',{'left':137})]
