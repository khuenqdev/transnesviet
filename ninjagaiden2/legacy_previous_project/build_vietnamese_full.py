#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, zlib, re, shutil, struct, json, zipfile, os
import importlib.util

ROOT = Path('/mnt/data/ng2_project_ref')
WORK = Path('/mnt/data/ng2_work')
OUT = Path('/mnt/data/ng2_vietnamese_project')
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'Ninja Gaiden II - The Dark Sword of Chaos (USA).nes'
EXPECTED_SHA1 = '269478947a5bc518551ab5d7b4687653006e243c'

# Import the prepared Vietnamese translation table.
spec = importlib.util.spec_from_file_location('prepared', WORK / 'build_vn_translation.py')
prepared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepared)
T = prepared.T
VI_MAP = prepared.VI_MAP

# Alt2 text encoding.
UP = {chr(ord('A') + i): 0x01 + i for i in range(26)}
LO = {chr(ord('a') + i): 0x21 + i for i in range(26)}
PUNC = {
    ' ':0x3F, '!':0x41, '"':0x42, "'":0x45, ',':0x4C, '-':0x4D,
    '.':0x4E, '/':0x4F, ':':0x5A, '?':0x5F, '&':0x46, '%':0x47,
    '(':0x48, ')':0x49, '*':0x4A, '+':0x4B, '$':0x44,
    '<':0x5C, '>':0x5E, '[':0x1B, ']':0x1D, '_':0x63,
    '=':0xA0, '^':0xA1, '¨':0x65,
}

# Playlist state in NES RAM. $EB/$EC are within the documented reserved area
# around $D8-$EF and are not used by the normal cutscene/title paths.
PLAYLIST_ACTIVE = 0x74
PLAYLIST_INDEX = 0x75

# Fixed PRG bank helper locations (file offsets / CPU addresses).
INPUT_HOOK_OFF = 0x1D748       # CPU $D738, replaces LDA $13
INPUT_HELPER_OFF = 0x1FA30     # CPU $FA20
CUTSCENE_AFTER_JSR_OFF = 0x1C845 # CPU $C835, immediately after JSR $A000
DISPATCHER_OFF = 0x1FA55       # CPU $FA45

# 15 high-level cutscene seeds are IDs 1..15 (0x01..0x0F). This follows the
# game's $CB cutscene seed and the fixed-bank cs_list/stage mappings.
FIRST_SCENE = 0x01
LAST_SCENE = 0x0F


def load_base():
    data = bytearray(BASE.read_bytes())
    got = hashlib.sha1(data).hexdigest()
    if got != EXPECTED_SHA1:
        raise SystemExit(f'Base SHA-1 mismatch: {got}')
    return data


def parse_alt2_entries():
    path = ROOT / 'ninjagaideniithedarkswordofchaosnesAlt2.ext'
    entries=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        m=re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
        if m:
            entries.append((int(m.group(1),16), int(m.group(3)), int(m.group(4)), m.group(2)))
    return entries


def raw_token_bytes(s: str) -> bytes:
    out=bytearray(); i=0
    while i < len(s):
        if s[i]=='~':
            j=s.find('~',i+1)
            if j<0: raise ValueError(f'unterminated ~ token in {s!r}')
            tok=s[i+1:j]
            out.append(int(tok,16))
            i=j+1
            continue
        ch=s[i]
        if ch in UP: out.append(UP[ch])
        elif ch in LO: out.append(LO[ch])
        elif ch in VI_MAP: out.append(VI_MAP[ch])
        elif ch=='Đ': out.append(UP['D'])
        elif ch=='đ': out.append(VI_MAP['đ'])
        elif ch in PUNC: out.append(PUNC[ch])
        else:
            # Unsupported tone combinations intentionally lose the tone rather
            # than becoming a second text cell. This preserves fixed-width alignment.
            import unicodedata
            base=''.join(c for c in unicodedata.normalize('NFD',ch) if unicodedata.category(c)!='Mn')
            if len(base)==1 and base in UP: out.append(UP[base])
            elif len(base)==1 and base in LO: out.append(LO[base])
            else: raise ValueError(f'No mapping for {ch!r}')
        i += 1
    return bytes(out)


def apply_text(data: bytearray):
    entries=parse_alt2_entries()
    story=[e for e in entries if e[0] < 0x15BD1]
    assert len(story)==152 and len(T)==152
    report=[]
    for addr, src_len, cap, src_text in story:
        key=f'{addr:08X}'
        txt=T[key]
        enc=raw_token_bytes(txt)
        if not enc or enc[-1] != 0xA6:
            raise ValueError(f'{key}: translated text must end in A6')
        if len(enc)>cap:
            raise ValueError(f'{key}: {len(enc)} > capacity {cap}')
        body=enc[:-1]
        patched=body + bytes([0x3F])*(cap-1-len(body)) + bytes([0xA6])
        data[addr:addr+cap]=patched
        report.append({'addr':key,'capacity':cap,'used':len(enc),'text':txt})
    # Preserve English credits and UI. Fix the Spanish reference's non-English
    # PRESENTS block by restoring the English label.
    presents=bytes(UP[c] for c in 'PRESENTS')
    for a in (0x85A6,0x85B7):
        data[a:a+8]=presents
    return report


def base_tile(data: bytes, code: int) -> bytearray:
    # Text code maps to CHR tile code + 0x40.
    tile = 0x40 + code
    start = 0x20010 + tile*16
    return bytearray(data[start:start+16])


def clear_mask(row: int, bits: list[int], glyph: bytearray):
    v=glyph[row]
    for b in bits:
        v &= ~(1 << b)
    glyph[row]=v


def make_accented(base_glyph: bytearray, kind: str) -> bytearray:
    g=bytearray(base_glyph)
    # Overlay a compact 1-cell accent on rows 0-2. Pixel convention matches
    # the game's existing Spanish accent glyphs: 0 bits are foreground.
    patterns={
        'acute': [[6],[5],[4]],
        'grave': [[1],[2],[3]],
        'circumflex': [[3,4],[2,5],[1,6]],
        'breve': [[3,4],[2,5],[1,6]],
        'horn': [[1],[1],[2]],
    }
    for row,bits in enumerate(patterns[kind]): clear_mask(row,bits,g)
    return g


def build_custom_font(data: bytearray):
    # Source code -> base letter for precomposed glyph.
    glyph_defs={
      0x66:('a','acute'),0x67:('a','grave'),
      0x68:('e','acute'),0x69:('e','grave'),
      0x6A:('i','acute'),0x6B:('i','grave'),
      0x6C:('o','acute'),0x6D:('o','grave'),
      0x6E:('u','acute'),0x6F:('u','grave'),
      0x70:('a','breve'),0x71:('a','circumflex'),
      0x72:('e','circumflex'),0x73:('o','circumflex'),
      0x74:('o','horn'),0x75:('u','horn'),
      0x76:('d','acute'), # replaced below with d-bar
      0x77:('a','circumflex_acute'),0x78:('a','circumflex_grave'),
      0x79:('e','circumflex_acute'),0x7A:('e','circumflex_grave'),
      0x7B:('o','circumflex_acute'),0x7C:('o','circumflex_grave'),
      0x7D:('o','horn_acute'),0x7E:('o','horn_grave'),0x7F:('u','horn_acute'),
    }
    generated={}
    for code,(letter,kind) in glyph_defs.items():
        base_code=LO[letter]
        g=base_tile(data,base_code)
        if kind=='d-bar':
            # no dedicated key in defs; not used here
            pass
        if kind in ('acute','grave','circumflex','breve','horn'):
            g=make_accented(g,kind)
        elif kind=='d-acute':
            g=bytearray(base_tile(data,LO['d']))
            # horizontal bar through the stem
            for row in (3,4):
                g[row] &= ~((1<<2)|(1<<3)|(1<<4)|(1<<5))
        else:
            if 'circumflex' in kind:
                if 'acute' in kind:
                    g=make_accented(make_accented(g,'circumflex'),'acute')
                elif 'grave' in kind:
                    g=make_accented(make_accented(g,'circumflex'),'grave')
            elif 'horn' in kind:
                g=make_accented(make_accented(g,'horn'),'acute' if 'acute' in kind else 'grave')
        tile=0x40+code
        start=0x20010+tile*16
        data[start:start+16]=g
        generated[code]=bytes(g).hex()
    # Fix d-bar definition 0x76 independently.
    g=bytearray(base_tile(data,LO['d']))
    for row in (3,4): g[row] &= ~((1<<2)|(1<<3)|(1<<4)|(1<<5))
    data[0x20010+(0x40+0x76)*16:0x20010+(0x40+0x77)*16]=g
    generated[0x76]=bytes(g).hex()
    return generated


def build_playlist_patch(data: bytearray):
    # Confirm hook bytes in the clean ROM.
    if data[INPUT_HOOK_OFF:INPUT_HOOK_OFF+3] != bytes.fromhex('a5 13 29 10')[:3]:
        # The original sequence is A5 13 29 10; replace only the LDA $13.
        pass
    if data[INPUT_HOOK_OFF:INPUT_HOOK_OFF+2] != bytes.fromhex('a5 13'):
        raise ValueError(f'Unexpected title hook bytes: {data[INPUT_HOOK_OFF:INPUT_HOOK_OFF+6].hex()}')
    # Replace LDA $13 with JSR $FA20; keep the following AND #$10 unchanged.
    data[INPUT_HOOK_OFF:INPUT_HOOK_OFF+3] = bytes.fromhex('20 20 fa')
    # Fill helper area with NOPs first.
    data[INPUT_HELPER_OFF:INPUT_HELPER_OFF+128] = b'\xEA'*128
    # Helper at FA20:
    #   LDA $13 / AND #$20 / BEQ normal / LDA #1 / STA $EB / LDA #1 / STA $EC / STA $CB / JMP C820
    helper=bytes.fromhex(
        'A5 13 29 20 F0 0D'
        'A9 01 85 74'
        'A9 01 85 75 85 CB'
        '4C 20 C8'
        'A5 13 60'
    )
    data[INPUT_HELPER_OFF:INPUT_HELPER_OFF+len(helper)] = helper
    # Cutscene return hook. Original at C835 is A9 04. Replace with JSR FA45.
    if data[CUTSCENE_AFTER_JSR_OFF:CUTSCENE_AFTER_JSR_OFF+2] != bytes.fromhex('a9 04'):
        raise ValueError(f'Unexpected C835 bytes: {data[CUTSCENE_AFTER_JSR_OFF:CUTSCENE_AFTER_JSR_OFF+8].hex()}')
    data[CUTSCENE_AFTER_JSR_OFF:CUTSCENE_AFTER_JSR_OFF+5] = bytes.fromhex('20 45 fa ea ea')
    # Dispatcher at FA45:
    # active? if no -> A=04 RTS
    # index++ ; if ==10 -> clear + A=04 RTS; else CB=index, JMP C820
    dispatcher=bytes.fromhex(
        'A5 74 F0 12'
        'E6 75 A5 75 C9 10 F0 05'
        '85 CB 4C 20 C8'
        'A9 00 85 74'
        'A9 04 60'
    )
    data[DISPATCHER_OFF:DISPATCHER_OFF+len(dispatcher)] = dispatcher
    return helper, dispatcher


def make_ips(old: bytes, new: bytes, max_chunk=0xFF00):
    out=bytearray(b'PATCH')
    i=0
    while i<len(old):
        if old[i]==new[i]: i+=1; continue
        s=i
        i+=1
        while i<len(old) and old[i]!=new[i] and i-s<max_chunk: i+=1
        payload=new[s:i]
        out += s.to_bytes(3,'big') + len(payload).to_bytes(2,'big') + payload
    out += b'EOF'
    return bytes(out)


def create_tbl():
    p=OUT/'ninjagaideniithedarkswordofchaosnesAlt2_VI.tbl'
    lines=(ROOT/'ninjagaideniithedarkswordofchaosnesAlt2.tbl').read_text(encoding='utf-8').splitlines()
    # Remove existing Spanish accent mappings 70-7D and add Vietnamese glyphs.
    vi_names={
      0x66:'á',0x67:'à',0x68:'é',0x69:'è',0x6A:'í',0x6B:'ì',0x6C:'ó',0x6D:'ò',0x6E:'ú',0x6F:'ù',
      0x70:'ă',0x71:'â',0x72:'ê',0x73:'ô',0x74:'ơ',0x75:'ư',0x76:'đ',0x77:'ấ',0x78:'ầ',0x79:'ế',0x7A:'ề',0x7B:'ố',0x7C:'ồ',0x7D:'ớ',0x7E:'ờ',0x7F:'ứ'}
    filtered=[]
    for line in lines:
        if re.match(r'^[0-9A-Fa-f]{2}=.',line):
            code=int(line[:2],16)
            if code in vi_names:
                continue
        filtered.append(line)
    filtered.append('; Vietnamese fixed-width precomposed glyphs')
    for code,ch in sorted(vi_names.items()): filtered.append(f'{code:02X}={ch}')
    p.write_text('\n'.join(filtered)+'\n',encoding='utf-8')
    return p



def create_vn_ext(entries):
    src=ROOT/'ninjagaideniithedarkswordofchaosnesAlt2.ext'
    out=OUT/'vi_ninjagaideniithedarkswordofchaosnesAlt2.ext'
    lines=src.read_text(encoding='utf-8').splitlines()
    result=[]; current=None; cap=None
    for line in lines:
        m=re.match(r';([0-9A-F]+)\{(.*)\}#(\d+)#(\d+)', line)
        if m:
            current=m.group(1); cap=int(m.group(4)); result.append(line); continue
        if current is not None and (line.startswith('"') or line.startswith('~') or line.startswith('==')):
            if current in T:
                result.append(T[current]+f'#{cap}')
            else:
                result.append(line)
            current=None; cap=None
            continue
        result.append(line)
    out.write_text('\n'.join(result)+'\n',encoding='utf-8')
    return out


def create_font_bin(data):
    out=OUT/'vietnamese_glyphs_8x8.chr'
    payload=bytearray()
    for code in sorted(VI_MAP.values()):
        tile=0x40+code
        start=0x20010+tile*16
        payload += data[start:start+16]
    out.write_bytes(payload)
    return out

def main():
    base=load_base()
    data=bytearray(base)
    text_report=apply_text(data)
    glyph_report=build_custom_font(data)
    helper,dispatcher=build_playlist_patch(data)
    # Exact output and metadata.
    out_rom=OUT/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.nes'
    out_rom.write_bytes(data)
    ips=make_ips(base,bytes(data))
    (OUT/'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.ips').write_bytes(ips)
    # Save a Vietnamese text script in plain text form.
    script=OUT/'translation_vietnamese.txt'
    with script.open('w',encoding='utf-8') as f:
        f.write('# Ninja Gaiden II — Vietnamese translation\n# One entry per original Alt2 text block.\n\n')
        for r in text_report:
            f.write(f"@0x{r['addr']}: {r['text']}\n")
    create_tbl()
    create_vn_ext(parse_alt2_entries())
    create_font_bin(data)
    # Save patch report.
    meta={
      'base_sha1':hashlib.sha1(base).hexdigest(),
      'base_crc32':f'{zlib.crc32(base)&0xffffffff:08X}',
      'rom_sha1':hashlib.sha1(data).hexdigest(),
      'rom_crc32':f'{zlib.crc32(data)&0xffffffff:08X}',
      'rom_size':len(data),
      'translated_story_blocks':len(text_report),
      'custom_glyphs':len(glyph_report),
      'playlist_scene_ids':[f'{i:02X}' for i in range(FIRST_SCENE,LAST_SCENE+1)],
      'input_hook_cpu':'$D738', 'input_hook_file':'$1D748',
      'input_helper_cpu':'$FA20', 'input_helper_file':'$1FA30',
      'dispatcher_cpu':'$FA45', 'dispatcher_file':'$1FA55',
      'cutscene_return_hook_cpu':'$C835', 'cutscene_return_hook_file':'$1C845',
      'ram_active':'$74','ram_index':'$75','cutscene_seed':'$CB',
    }
    (OUT/'build_manifest.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text(f'''# Ninja Gaiden II — Vietnamese Translation + SELECT Cutscene Playlist\n\n## Output\n\n`Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist.nes` is built directly from the clean USA ROM.\n\nAt the static title screen, press **SELECT once**. The patch consumes SELECT and starts cutscene seed **01** directly. After each cutscene returns from the game’s existing cutscene engine, the dispatcher increments the seed and starts the next one without requiring another button press. The playlist covers seeds **01 through 0F**.\n\n## Fixed-width Vietnamese glyphs\n\nVietnamese diacritics are stored as **precomposed 8x8 NES glyphs**, one byte of text per glyph and one tile per glyph. No combining accent occupies an additional text cell. Unsupported rare tone combinations deliberately fall back to their base vowel rather than introducing an extra-width combining character. This prevents the horizontal misalignment seen in the previous translation.\n\n## Build identity\n\nBase SHA-1: `{meta['base_sha1']}`\nBase CRC32: `{meta['base_crc32']}`\nFinal SHA-1: `{meta['rom_sha1']}`\nFinal CRC32: `{meta['rom_crc32']}`\n\n## Patch locations\n\n- Title input hook: file `$1D748` / CPU `$D738`\n- Fixed-bank SELECT helper: file `$1FA30` / CPU `$FA20`\n- Cutscene-return hook: file `$1C845` / CPU `$C835`\n- Playlist dispatcher: file `$1FA55` / CPU `$FA45`\n- Playlist active flag: RAM `$EB`\n- Playlist index: RAM `$EC`\n- Existing cutscene seed: RAM `$CB`\n\nThe text remains in place; no pointer table relocation is required. All translated blocks are padded with the game’s single-cell space byte and retain the original `$A6` terminator.\n\n## Files\n\n- Vietnamese ROM\n- cumulative IPS patch\n- Vietnamese `.tbl`\n- translation source\n- build manifest\n- source/reference files under `reference/`\n''',encoding='utf-8')
    print(json.dumps(meta,indent=2))
    print('IPS bytes:',len(ips))

if __name__=='__main__': main()
