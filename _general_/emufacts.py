#!/usr/bin/env python3
"""emufacts.py - Emulator-assisted text facts (usage: see TEXTFACTS.md).

Boots the ROM in a libretro core, captures VRAM / work RAM / savestates while the
game is drawing text, then correlates the captured bytes with the ROM image.

A match proves that a run of ROM bytes really is text that the game puts on
screen, and gives the offset between a stored character code and the tile index
it draws. That turns the guesses of the static tools (where the text is, how wide
a line is, which byte ends a line, fixed width or VWF) into measurements.

The search works without knowing the character encoding: it compares the
*differences* between neighbouring bytes, so any encoding of the form
`tile = code + delta` is found.
"""
import argparse
import collections
import json
import os
import subprocess
import sys
import tempfile

import romfacts as R

try:
    import numpy as np
except ImportError:  # the fallback is ~10x slower but needs no packages
    np = None

HERE = os.path.dirname(os.path.abspath(__file__))
EMU = os.path.join(HERE, "emulator", "emu.exe")

# Cores that expose the memory this tool needs; see TEXTFACTS.md for what each one gives.
CORES = {"nes": "fceumm", "gb": "sameboy", "gba": "mgba", "snes": "snes9x", "md": "genesis_plus_gx"}

# Capture plan: a name plus the emulator commands to run before the capture.
# The button mashing is a blunt way to walk through title screens and menus into
# the first dialogue; pass --script for a game-specific route.
DEFAULT_PLAN = [
    ("boot", ["run 420"]),
    ("title", ["press START 6 60", "run 150"]),
    ("menu", ["press START 6 60", "tap A 6 30", "run 150"]),
    ("game1", ["tap A 12 24", "run 180"]),
    ("game2", ["tap A 12 24", "run 240"]),
    ("game3", ["tap START 2 30", "tap A 14 20", "run 240"]),
]

KINDS = ("vram", "ram", "state")


def hx(v, w=2):
    return f"${v:0{w}X}"


def diffs(b):
    """Byte-wise difference of neighbours, mod 256."""
    if len(b) < 2:
        return b""
    if np is not None:
        a = np.frombuffer(b, dtype=np.uint8)
        return (a[1:] - a[:-1]).tobytes()
    return bytes((y - x) & 0xFF for x, y in zip(b, b[1:]))


# ---------------------------------------------------------------------------------------------
# Capture

def emu_missing():
    return (f"{EMU} not found - build it with:\n"
            r"  C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /platform:x64 "
            r"/out:tools\emulator\emu.exe tools\emu.cs")


def parse_plan(path):
    """A custom script: '## name' starts a capture step, other lines are emulator commands."""
    plan, name, cmds = [], None, []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("##"):
                if name:
                    plan.append((name, cmds))
                name, cmds = line[2:].strip() or f"step{len(plan)}", []
            elif line and not line.startswith("#"):
                cmds.append(line)
    if name:
        plan.append((name, cmds))
    return plan or DEFAULT_PLAN


def run_emu(rom, core, outdir, plan, shots=False, log=False, timeout=300):
    script, caps = [], []
    for name, cmds in plan:
        script += cmds
        for kind in KINDS:
            script.append(f"{'save' if kind == 'state' else kind} {os.path.join(outdir, name + '.' + kind)}")
        if shots:
            script.append(f"shot {os.path.join(outdir, name + '.png')} 1")
        caps.append(name)
    script.append("quit")
    sp = os.path.join(outdir, "script.txt")
    with open(sp, "w", newline="\n") as fh:
        fh.write("\n".join(script) + "\n")
    cmd = [EMU, "--core", core] + (["--log"] if log else []) + [os.path.abspath(rom), sp]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return caps, r


def load_caps(outdir, caps):
    out = []
    for name in caps:
        for kind in KINDS:
            p = os.path.join(outdir, f"{name}.{kind}")
            if os.path.exists(p) and os.path.getsize(p) > 64:
                with open(p, "rb") as fh:
                    out.append((f"{name}.{kind}", fh.read()))
    return out


# ---------------------------------------------------------------------------------------------
# Correlation

def pick_probes(seq, sdiff, win, cap):
    """Windows that are varied enough to identify a place in the ROM on their own."""
    out, i, n = [], 0, len(seq)
    need = max(4, win // 2)
    for _ in range(n):
        if i + win > n:
            break
        w = seq[i:i + win]
        d = sdiff[i:i + win - 1]
        if len(set(w)) >= need and sum(1 for x in d if x) >= (win - 1) * 0.6:
            out.append(i)
            i += max(1, win // 2)
        else:
            i += 1
    if len(out) > cap:
        step = len(out) / cap
        out = [out[int(k * step)] for k in range(cap)]
    return out


def extend(rom, p, seq, i, win):
    """Grow a window match as far as the constant code->tile offset keeps holding."""
    delta = (rom[p] - seq[i]) & 0xFF
    a, b, si, sj = p, p + win, i, i + win
    while a > 0 and si > 0 and (rom[a - 1] - seq[si - 1]) & 0xFF == delta:
        a -= 1
        si -= 1
    while b < len(rom) and sj < len(seq) and (rom[b] - seq[sj]) & 0xFF == delta:
        b += 1
        sj += 1
    return {"rom": a, "end": b, "len": b - a, "src": si, "delta": delta}


def local_fill(seq, src, span=512):
    """Share of the commonest value around src.

    A tilemap is mostly blank tiles, so it scores high; tile pixels, code and
    work RAM score low. This is what separates a line of text from graphics
    that happen to be copied out of the ROM.
    """
    a = max(0, src - span // 2)
    w = seq[a:a + span]
    if not w:
        return 0.0
    return collections.Counter(w).most_common(1)[0][1] / len(w)


def classify(m, min_fill):
    # A long run copied byte for byte is a graphics/data DMA, not a line of text.
    if m["delta"] == 0 and m["len"] >= 64:
        return "asset"
    if m["fill"] < min_fill:
        return "data"
    return "tilemap" if m["stride"] == 2 else "line"


def find_matches(rom, romdiff, buf, label, win, cap, min_run, min_fill, per_probe=6):
    out = []
    for stride in (1, 2):
        for phase in range(stride):
            seq = buf if stride == 1 else buf[phase::stride]
            if len(seq) < win + 1:
                continue
            sdiff = diffs(seq)
            wd_seen = set()
            for i in pick_probes(seq, sdiff, win, cap):
                wd = sdiff[i:i + win - 1]
                if wd in wd_seen:
                    continue
                wd_seen.add(wd)
                p, n = romdiff.find(wd), 0
                while p != -1 and n < per_probe:
                    m = extend(rom, p, seq, i, win)
                    if m["len"] >= min_run:
                        m.update(buf=label, stride=stride, phase=phase)
                        m["fill"] = round(local_fill(seq, m["src"]), 3)
                        m["kind"] = classify(m, min_fill)
                        out.append(m)
                    n += 1
                    p = romdiff.find(wd, p + 1)
    return out


def dedupe(ms):
    ms.sort(key=lambda m: (m["buf"], m["stride"], m["phase"], m["rom"], -m["len"]))
    out = []
    for m in ms:
        if out:
            q = out[-1]
            same = (q["buf"], q["stride"], q["phase"]) == (m["buf"], m["stride"], m["phase"])
            if same and m["rom"] < q["end"] and m["src"] < q["src"] + q["len"]:
                continue
        out.append(m)
    return out


def mode(values, lo, hi):
    c = collections.Counter(v for v in values if lo <= v <= hi)
    return c.most_common(1)[0] if c else (None, 0)


def summarize(rom, matches, top=12):
    """Turn raw matches into the facts the text fact sheet wants."""
    text = [m for m in matches if m["kind"] in ("line", "tilemap")]
    assets = [m for m in matches if m["kind"] == "asset"]
    data = [m for m in matches if m["kind"] == "data"]
    f = {"matches": len(matches), "text_matches": len(text), "assets": len(assets), "data": len(data)}
    if not text:
        return f, text, assets

    f["delta"], f["delta_n"] = collections.Counter(m["delta"] for m in text).most_common(1)[0]
    widths = sorted(m["len"] for m in text)
    f["width_max"] = widths[-1]
    f["width_med"] = widths[len(widths) // 2]

    # Lines of the same screen sit a fixed number of entries apart: that is the tilemap row pitch.
    bufs = {m["buf"] for m in text}
    starts = {b: sorted({m["src"] for m in text if m["buf"] == b}) for b in bufs}
    pitches = [y - x for s in starts.values() for x, y in zip(s, s[1:])]
    f["pitch"], f["pitch_n"] = mode(pitches, 8, 256)
    # the longest chain of lines exactly one row apart is what fits on screen at once
    rows = []
    if f["pitch"]:
        for s in starts.values():
            best = run = 1
            for x, y in zip(s, s[1:]):
                run = run + 1 if y - x == f["pitch"] else 1
                best = max(best, run)
            rows.append(best)
    f["rows_max"] = max(rows) if rows else 0

    # What follows a line in the ROM is a newline / terminator / control code.
    after = collections.Counter(rom[m["end"]] for m in text if m["end"] < len(rom))
    before = collections.Counter(rom[m["rom"] - 1] for m in text if m["rom"] > 0)
    f["after"] = after.most_common(top)
    f["before"] = before.most_common(top)
    f["buffers"] = sorted({m["buf"] for m in text})
    f["fixed"] = any(m["kind"] in ("line", "tilemap") for m in text)
    return f, text, assets


# ---------------------------------------------------------------------------------------------
# Entry points

def collect(rom_path, core=None, plan=None, win=8, probes=400, min_run=6, min_fill=0.4,
            keep=None, shots=False, log=False, timeout=300):
    """Run the emulator and correlate; returns (facts, matches, info)."""
    if not os.path.exists(EMU):
        raise RuntimeError(emu_missing())
    with open(rom_path, "rb") as fh:
        data = fh.read()
    sysname = R.detect(data, os.path.splitext(rom_path)[1].lower())
    if sysname is None:
        raise RuntimeError("unknown system: cannot pick a core")
    core = core or CORES.get(sysname)
    if core is None:
        raise RuntimeError(f"no core configured for {sysname}")
    img = R.ANALYZERS[sysname](data).image

    tmp = keep or tempfile.mkdtemp(prefix="emufacts")
    os.makedirs(tmp, exist_ok=True)
    if " " in tmp:
        raise RuntimeError(f"capture directory must not contain spaces: {tmp}")
    caps, proc = run_emu(rom_path, core, tmp, plan or DEFAULT_PLAN, shots, log, timeout)
    bufs = load_caps(tmp, caps)
    info = {"system": sysname, "core": core, "dir": tmp,
            "captures": [(n, len(b)) for n, b in bufs],
            "stderr": (proc.stderr or "").strip()}
    if not bufs:
        return {"matches": 0, "text_matches": 0, "assets": 0, "data": 0}, [], info

    romdiff = diffs(img)
    matches = []
    for label, buf in bufs:
        matches += find_matches(img, romdiff, buf, label, win, probes, min_run, min_fill)
    matches = dedupe(matches)
    facts, text, assets = summarize(img, matches)
    info["image_size"] = len(img)
    return facts, matches, info


def report(rom_path, facts, matches, info, top=20):
    A = f"{os.path.basename(rom_path)}"
    out = [f"Emulator text evidence - {A}",
           f"System: {info['system']}   core: {info['core']}"]
    caps = ", ".join(f"{n} ({l:,}B)" for n, l in info.get("captures", [])) or "none"
    out += ["", "== Captures ==", f"  {caps}"]
    if info.get("stderr"):
        out += ["  core messages: " + info["stderr"].splitlines()[-1][:120]]

    out += ["", "== Measured facts =="]
    if not facts.get("text_matches"):
        out += ["  no screen text could be matched to the ROM.",
                "  The game may not have reached a text screen, or it decodes/decompresses text",
                "  before drawing (DTE, compression, VWF). Try --script with a route into dialogue."]
    else:
        d = facts["delta"]
        rows = [("Text on screen", f"{facts['text_matches']} run(s) of ROM bytes found in {len(facts['buffers'])} capture(s)"),
                ("Code -> tile", f"tile = code + {hx(d)} ({facts['delta_n']} run(s) agree)"
                                 + ("  [codes are tile indices]" if d == 0 else "")),
                ("Line width", f"longest matched run {facts['width_max']} chars, median {facts['width_med']}"),
                ("Row pitch", f"{facts['pitch']} entries between lines ({facts['pitch_n']} gap(s) agree)"
                              if facts.get("pitch") else "not resolved"),
                ("Lines on one screen", str(facts["rows_max"])),
                ("Fixed width or VWF", "fixed-width tiles: the text is on screen as tile indices"
                                       if facts["fixed"] else "no tilemap match - glyphs may be drawn (VWF)"),
                ("Ignored as not text", f"{facts['assets']} asset copy/copies, {facts['data']} run(s) in non-tilemap memory")]
        w = max(len(k) for k, _ in rows)
        out += [f"  {k.ljust(w)} : {v}" for k, v in rows]

        out += ["", "== Byte after each matched line ==",
                "  a line normally ends at a newline, a terminator or the edge of the window",
                "  " + ", ".join(f"{hx(b)} x{n}" for b, n in facts["after"])]
        out += ["", "== Byte before each matched line ==",
                "  " + ", ".join(f"{hx(b)} x{n}" for b, n in facts["before"])]

    shown = [m for m in matches if m["kind"] in ("line", "tilemap")]
    shown.sort(key=lambda m: -m["len"])
    out += ["", "== Matched runs ==",
            "  rom offset     len  delta  stride  fill  capture           at",
            *[f"  {m['rom']:06X}-{m['end']:06X} {m['len']:5}  {hx(m['delta'])}   {m['stride']}      "
              f"{m['fill']:.2f}  {m['buf']:16}  {m['src']:#07x}" for m in shown[:top]]]
    if len(shown) > top:
        out.append(f"  ... {len(shown) - top} more")

    out += ["", "== Notes ==",
            "- A match means the ROM bytes and the captured screen differ by one constant offset,",
            "  so the text is stored as plain character codes (no DTE/compression) for that run.",
            "- Text that is decompressed or built in RAM shows up in the .ram/.state captures instead",
            "  of the tilemap; the ROM offset is still the real storage location.",
            "- Runs marked as assets are graphics copied from the ROM, not text.",
            "- A run is only counted as text if the memory around it looks like a tilemap",
            "  (mostly one blank tile); raise or lower that bar with --min-fill.",
            "- The default route only mashes START/A: use --script for a game-specific path into dialogue."]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emulator-assisted Text facts: correlate what is on screen with the ROM.")
    ap.add_argument("rom")
    ap.add_argument("-o", "--out", help="report file (default: <rom>.emu.txt)")
    ap.add_argument("--core", help=f"libretro core name or path (default: {', '.join(f'{k}={v}' for k, v in CORES.items())})")
    ap.add_argument("--script", help="capture plan ('## name' starts a step, other lines are emulator commands)")
    ap.add_argument("--keep", help="directory to keep the captures in (must not contain spaces)")
    ap.add_argument("--shots", action="store_true", help="also save a PNG of every capture")
    ap.add_argument("--window", type=int, default=8, help="probe length in characters (default 8)")
    ap.add_argument("--probes", type=int, default=400, help="probe windows per capture (default 400)")
    ap.add_argument("--min-run", type=int, default=6, help="shortest accepted run (default 6)")
    ap.add_argument("--min-fill", type=float, default=0.4,
                    help="how blank the memory around a match must be to count as a tilemap (default 0.4)")
    ap.add_argument("--top", type=int, default=20, help="rows per list (default 20)")
    ap.add_argument("--log", action="store_true", help="show core log messages")
    ap.add_argument("--json", action="store_true", help="write the facts as JSON instead")
    args = ap.parse_args(argv)

    plan = parse_plan(args.script) if args.script else None
    try:
        facts, matches, info = collect(args.rom, args.core, plan, args.window, args.probes,
                                       args.min_run, args.min_fill, args.keep, args.shots, args.log)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    path = args.out or args.rom + (".emu.json" if args.json else ".emu.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        if args.json:
            json.dump({"facts": facts, "info": info, "matches": matches}, fh, indent=1)
        else:
            fh.write("\n".join(report(args.rom, facts, matches, info, args.top)) + "\n")
    print(f"{info['system']}/{info['core']}: {facts.get('text_matches', 0)} text run(s), wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
