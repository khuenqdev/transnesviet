#!/usr/bin/env python3
"""Stage 1 – Build the translation master sheet (script_master.csv, UTF-8 BOM, Excel-ready)
from scenes.json + menu.json. Columns: id, block, scene, addr, ref_locations, jp_bytes,
jp_text (\\r shown as <br>), en_ref (from translation guide where available), vi_text (to fill)."""
import json, csv
S=json.load(open('scenes.json',encoding='utf-8')); M=json.load(open('menu.json',encoding='utf-8'))
EN_MENU=["Which data do you want to DELETE?","Where do you want to COPY to?","Which data do you want to COPY?","Which game do you want to START?",
"OVERWRITE this data?","DELETE this data?","Back to the map.","Retry this stage.","Configure keys.","Configure Gun Arts and Sheriff Badges.",
"Is this okay?","Powerful attack Arts bearing the name of a phantom beast.","Low-ground movement Arts imitating creatures crawling swiftly.",
"Aerial attack Arts imitating creatures dancing in the sky.","Body-blow Arts imitating powerful movements.","Dodge-focused Arts imitating agile movements.",
"Gun Force depletes more slowly.","The Metalgun is enhanced, increasing damage dealt to enemies.","Aerial shots become 3-WAY, but you take more damage.",
"You take less damage.","A memento of Billy's father."]
BOUNTY=[("0205","Pawn","Counterfeiting / Fraud"),("6972","Poison Herald","Trespassing / Food robbery"),("1543","Nicole","Donkey theft / Poaching"),
("1943","Tomahawk","Weapons smuggling"),("0258","Jill Morgan","Train robbery"),("2005","Rigg Morgan","Train robbery"),("1586","Arclight","House destruction / Property damage"),
("3647","Butch","Cop killing / Jailbreak"),("1300","Apple","Dine-and-dash / Vegetable theft"),("5236","Boubou","Cattle / Sheep / Horse theft"),
("0021","Hanging Man","Trespassing / Murder"),("4893","Flash William","Pickpocketing"),("1234","Lightning","Serial murder"),("0293","Mister Tanaka","Marriage fraud"),
("7803","Harvey the Strongarm","Kidnap-murder / Extortion"),("0981","Garcia","Luggage theft / Purse snatching"),("0036","Winston","Obstruction of official duty"),
("3000","Rocky","Brawling"),("9642","Hawkeye Lycos","Serial robbery / Murder"),("3875","Eastwood","Cop killing"),("7345","Colonel Mortimer","Highway robbery / Snatching"),("1956","Josey","Cattle theft")]
EN_MENU+= [f"Wanted No.{n} {nm}<br>Charges: {c}" for n,nm,c in BOUNTY]+[f"Wanted No.{n} {nm}" for n,nm,c in BOUNTY]
EN_MENU+=["Return to the title.","Start the tutorial.","View bounty data.","View stage data.","Is this okay?"]
assert len(EN_MENU)==len(M),(len(EN_MENU),len(M))
rows=[]; n=0
for i,m in enumerate(M):
    rows.append(['M%03d'%i,'menu','-','0x%06X'%m['addr'],' '.join('ptr@0x%06X'%r for r in m['refs']),m['len'],m['text'].replace('\r','<br>'),EN_MENU[i],''])
for s in S:
    for x in s['strings']:
        rows.append(['S%04d'%n,'story',s['id'],'0x%06X'%x['addr'],' '.join('op29@0x%06X'%r for r in x['refs']),x['len'],x['text'].replace('\r','<br>'),'',''])
        n+=1
with open('script_master.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['id','block','scene','addr','ref_locations','jp_bytes','jp_text','en_ref','vi_text']); w.writerows(rows)
print(len(rows),'rows')
