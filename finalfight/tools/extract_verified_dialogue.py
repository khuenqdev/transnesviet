#!/usr/bin/env python3
from pathlib import Path
import csv, json, sys

def decode(raw):
    o=[]
    for x in raw:
        if x==0:o.append(" ")
        elif 0x10<=x<=0x29:o.append(chr(65+x-0x10))
        elif x==0x2A:o.append("'")
        elif x==0x2B:o.append(".")
        elif x==0x2C:o.append(",")
        elif x==0xFE:o.append("<FE>")
        elif x==0xFF:o.append("<FF>")
        elif x in (0xF9,0xFA,0xFB,0xFC):o.append(f"<CTRL{x:02X}>")
        elif x in (0x75,0x76,0x78):o.append(f"<CTRL{x:02X}>")
        else:o.append(f"<{x:02X}>")
    return "".join(o)

def read_record(prg,cpu,bank,base):
    off=bank*0x2000+(cpu-base)
    out=bytearray()
    while off<len(prg) and len(out)<512:
        out.append(prg[off])
        if prg[off]==0xFF: break
        off+=1
    return bytes(out), off-len(out)+1

def main():
    if len(sys.argv)<2: raise SystemExit("Usage: extract_verified_dialogue.py ROM")
    p=Path(sys.argv[1]); data=p.read_bytes(); prg=data[16:16+0x20000]
    layout=Path(__file__).resolve().parents[1]/"analysis"/"layout_verified.json"
    cfg=json.loads(layout.read_text())
    rows=[]
    openings=[0x9B3A,0x9C34,0x9C8C,0x9CA3,0x9D2E,0x9D5C,0x9E07]
    for i,c in enumerate(openings):
        raw,off=read_record(prg,c,0,0x8000)
        rows.append(("opening",i,c,off,raw))
    low=0xA54C; high=0xA4FD
    for i in range(78):
        c=prg[low+i]|prg[high+i]<<8
        raw,off=read_record(prg,c,4,0x8000)
        rows.append(("boss",i,c,off,raw))
    credits=[0xA7E0,0xA7F1,0xA87D,0xA8CB,0xA95C]
    for i,c in enumerate(credits):
        raw,off=read_record(prg,c,9,0xA000)
        rows.append(("credits",i,c,off,raw))
    w=csv.writer(sys.stdout,delimiter="\t")
    w.writerow(["group","index","cpu","prg_offset","length","decoded","raw_hex"])
    for g,i,c,o,raw in rows:
        w.writerow([g,i,f"${c:04X}",f"0x{o:05X}",len(raw),decode(raw),raw.hex(" ")])
if __name__=="__main__": main()
