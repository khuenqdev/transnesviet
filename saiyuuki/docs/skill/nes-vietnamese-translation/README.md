Skill folder. scripts/: viet_font.py (12-row Vietnamese bitmap font composer), viet_font8.py (8-px caps), asm6502.py / dis6502.py (tiny 6502 tools), make_ips.py. Reference implementation: ../../tools/build_rom.py, ../../src/*.asm.

Added in v2 (Doraemon project): `scripts/jsnes_lib.mjs` (headless jsnes with MMC1/SUROM handling), `npcalign.mjs`, `npcdrift.mjs`, `wander.mjs` (sprite/NPC glitch measurements), `ips.js` (IPS make/apply), `apply_walkspeed_example.js` (apply script template: ROM-type detection, byte verification, refuse double patch). Adjust the jsnes path in `jsnes_lib.mjs`.
