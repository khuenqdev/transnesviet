"""textfacts_core.py - shared engine of the per-platform text fact tools
(nes_text.py, gb_text.py, gba_text.py, snes_text.py, md_text.py).

It fills the "== Text ==" part of the fact sheet with candidates found by static analysis:
table (relative search / ASCII / Shift-JIS / .tbl), text regions, terminator and control codes,
pointer tables, hard-coded pointers, line width / lines per page, DTE hints and non-script text.
"""
import argparse
import array
import bisect
import collections
import math
import os
import re
import sys

TODO = "(fill in)"
HIRA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
UP = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LO = UP.lower()
DIG = "0123456789"
# (name, characters in code order). Smallest layouts first: a word uses the first layout that has matches.
LAYOUTS = [
    ("0-9", DIG), ("A-Z", UP), ("a-z", LO), ("kana gojuon (hiragana)", HIRA), ("kana gojuon (katakana)", KATA),
    ("0-9A-Z", DIG + UP), ("A-Za-z", UP + LO), ("a-zA-Z", LO + UP), ("0-9A-Za-z", DIG + UP + LO),
    ("ASCII order", "".join(map(chr, range(0x20, 0x7F)))),
    ("JIS/Unicode hiragana order", "".join(map(chr, range(0x3041, 0x3097)))),
    ("JIS/Unicode katakana order", "".join(map(chr, range(0x30A1, 0x30FB)))),
]


def hx(v, w=2):
    return f"${v:0{w}X}"


def hexb(b):
    return "".join(f"{x:02X}" for x in b)


def words(img, phase, size, big):
    """Values of consecutive size-byte entries starting at phase."""
    n = (len(img) - phase) // size
    if n <= 0:
        return []
    b = img[phase:phase + n * size]
    code = {2: "H", 4: "I" if array.array("I").itemsize == 4 else "L"}.get(size)
    if code:
        a = array.array(code)
        a.frombytes(b)
        if big != (sys.byteorder == "big"):
            a.byteswap()
        return a
    order = "big" if big else "little"
    return [int.from_bytes(b[i:i + size], order) for i in range(0, len(b), size)]


# ---------------------------------------------------------------------------------------------
# Character tables

class Table:
    kind = "table"

    def __init__(self, name):
        self.name = name
        self.chars = {}   # bytes -> text
        self.ctrl = {}    # bytes -> label (from .tbl '/' and '*' lines)
        self.width = 1

    def finalize(self):
        self.by_first = collections.defaultdict(list)
        for k, v in self.chars.items():
            self.by_first[k[0]].append((k, v))
        for lst in self.by_first.values():
            lst.sort(key=lambda kv: -len(kv[0]))
        self.first = bytes(1 if i in self.by_first else 0 for i in range(256))
        self.density = sum(self.first) / 256
        self.width = max((len(k) for k in self.chars), default=1)
        return self

    def mask(self, img):
        return img.translate(self.first)

    def accept(self, seq):
        return True

    def char_at(self, img, p):
        for k, v in self.by_first.get(img[p], ()):
            if img[p:p + len(k)] == k:
                return len(k), v
        return None


class AsciiTable(Table):
    kind = "ascii"

    def __init__(self):
        super().__init__("ASCII")
        for i in range(0x20, 0x7F):
            self.chars[bytes([i])] = chr(i)
        self.finalize()

    def accept(self, seq):
        return ascii_like(seq)


def ascii_like(seq):
    # real text is mostly letters, digits and spaces; random bytes are ~1/3 punctuation
    return sum(c.isalnum() or c == " " for c in seq) >= len(seq) * 0.8


class SjisTable(Table):
    kind = "sjis"

    def __init__(self):
        super().__init__("Shift-JIS")
        self.first = bytes(1 if (0x20 <= i < 0x7F or 0x81 <= i <= 0x84 or 0x88 <= i <= 0x9F or 0xE0 <= i <= 0xEA) else 0
                           for i in range(256))
        self.density = sum(self.first) / 256
        self.width = 2
        self.chars = {}

    def finalize(self):
        return self

    def accept(self, seq):
        cjk = [c for c in seq if c >= "\u3000"]
        if len(cjk) < len(seq) * 0.05:
            return ascii_like(seq)
        # Japanese prose is full of hiragana; random data hits kanji far more often than kana
        hira = sum("\u3040" <= c < "\u30a0" for c in cjk)
        kata = sum("\u30a0" <= c < "\u3100" for c in cjk)
        return hira >= len(cjk) * 0.25 or kata >= len(cjk) * 0.4

    def char_at(self, img, p):
        b = img[p]
        if 0x20 <= b < 0x7F:
            return 1, chr(b)
        if self.first[b] and p + 1 < len(img):
            t = img[p + 1]
            if 0x40 <= t <= 0xFC and t != 0x7F:
                try:
                    return 2, img[p:p + 2].decode("cp932")
                except UnicodeDecodeError:
                    return None
        return None


def load_tbl(path):
    t = Table(os.path.basename(path))
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            kind = ""
            if line[0] in "/*$!@":
                kind, line = line[0], line[1:]
            key, _, val = line.partition("=")
            try:
                kb = bytes.fromhex(key.strip())
            except ValueError:
                continue
            if not kb:
                continue
            if kind or val == "":
                t.ctrl[kb] = {"/": "end", "*": "newline"}.get(kind, val or "ctrl")
            else:
                t.chars[kb] = val
    return t.finalize()


def relative_search(img, word, layout, width, big):
    idx = [layout.index(c) for c in word]
    d = [i - idx[0] for i in idx]
    hits = []
    if width == 1:
        for b0 in range(-min(d), 256 - max(d)):
            pat = bytes(b0 + x for x in d)
            p = img.find(pat)
            while p != -1:
                hits.append((p, b0 - idx[0]))
                if len(hits) > 5000:
                    return hits
                p = img.find(pat, p + 1)
    else:
        n = len(d)
        for phase in (0, 1):
            vals = words(img, phase, 2, big)
            d1 = d[1]
            for i in range(len(vals) - n + 1):
                v = vals[i]
                if vals[i + 1] - v == d1 and all(vals[i + k] - v == d[k] for k in range(2, n)):
                    hits.append((phase + 2 * i, v - idx[0]))
                    if len(hits) > 5000:
                        return hits
    return hits


def build_known_table(img, known, width, big, log):
    t = Table("relative search")
    picks = []
    for word in known:
        if len(word) < 3 or len(set(word)) < 2:
            log.append(f"'{word}': too short (need 3+ characters, 2+ different)")
            continue
        found = False
        for name, layout in LAYOUTS:
            if not all(c in layout for c in word):
                continue
            hits = relative_search(img, word, layout, width, big)
            if not hits:
                continue
            bases = collections.Counter(b for _, b in hits)
            base, n = bases.most_common(1)[0]
            where = [f"{p:06X}" for p, b in hits if b == base]
            where = ", ".join(where[:8]) + (", ..." if len(where) > 8 else "")
            other = f"; {len(bases) - 1} other base(s) - ambiguous, try a longer word" if len(bases) > 1 else ""
            code0 = base + layout.index(word[0])
            log.append(f"'{word}': layout {name}, '{word[0]}' = {hx(code0, 2 * width)}, "
                       f"'{layout[0]}' = {hx(base, 2 * width) if base >= 0 else str(base)}; {n} hit(s) at {where}{other}")
            picks.append((n, len(bases) == 1, word, layout, base))
            found = True
            break
        if not found:
            log.append(f"'{word}': no match in any layout (custom order, DTE, or the word is not stored as plain text)")
    # most reliable word first; later words do not overwrite its codes
    for n, unique, word, layout, base in sorted(picks, key=lambda p: (not p[1], -p[0])):
        clash = 0
        for i, c in enumerate(layout):
            code = base + i
            if 0 <= code < (1 << (8 * width)):
                k = code.to_bytes(width, "big" if big else "little")
                if k in t.chars and t.chars[k] != c:
                    clash += 1
                else:
                    t.chars[k] = c
        if clash:
            log.append(f"'{word}': {clash} code(s) already taken by a more reliable word - this match is probably wrong")
    return t


# ---------------------------------------------------------------------------------------------
# Pointer formats and code patterns (filled in by the platform front-ends)

class PtrFormat:
    def __init__(self, name, size, keys=None, align=1, big=False, allowed=None, read=None, relative=False,
                 isolated_is_code=False, resolve=None):
        self.name, self.size, self.keys, self.align, self.big = name, size, keys, align, big
        self.allowed, self.read, self.relative, self.isolated_is_code = allowed, read, relative, isolated_is_code
        self.resolve = resolve  # (value, ctx) -> file offset or None; lets tables include short/unmatched strings

    def values(self, img, phase):
        return self.read(img, phase) if self.read else words(img, phase, self.size, self.big)


class CodePattern:
    def __init__(self, name, regex, fmt=None, value=None, target=None, align=1):
        self.name, self.fmt, self.value, self.target, self.align = name, fmt, value, target, align
        self.regex = re.compile(b"(?=" + regex + b")", re.DOTALL)


class Platform:
    name = "?"
    big = False
    vwf_hint = ""
    notes = []

    def setup_args(self, ap):
        pass

    def load(self, data, args):
        raise NotImplementedError

    def addr(self, f):
        return f"{f:06X}"

    def formats(self, args):
        return []

    def code_patterns(self, args):
        return []

    def extra(self, ctx):
        return []


# ---------------------------------------------------------------------------------------------
# Analysis

class Ctx:
    pass


def find_regions(img, tbl, min_chars, max_gap, min_ratio):
    pat = re.compile(rb"\x01(?:\x00{0,%d}\x01)*" % max_gap)
    mask = tbl.mask(img)
    regions = []

    def flush(cur, unk):
        if cur is None:
            return
        s, e, covered, seq = cur
        n = len(seq)
        if n < min_chars or covered < (e - s) * min_ratio:
            return
        cnt = collections.Counter(seq)
        if len(cnt) < 5 or cnt.most_common(1)[0][1] > n * 0.4:
            return
        if len(set(zip(seq, seq[1:]))) < min((n - 1) * 0.5, 40):  # repeated patterns are tables/graphics, not text
            return
        if not tbl.accept(seq):
            return
        regions.append({"start": s, "end": e, "chars": n, "unk": [u for u in unk if u < e]})

    for m in pat.finditer(mask):
        s, e = m.span()
        if e - s < min_chars:
            continue
        p, cur, unk = s, None, []
        while p < e:
            r = tbl.char_at(img, p)
            if r:
                if cur is None:
                    cur = [p, p, 0, []]
                    unk = []
                n, t = r
                cur[2] += n
                cur[3].append(t)
                p += n
                cur[1] = p
            else:
                if cur is not None:
                    if p + 1 - cur[1] > max_gap:
                        flush(cur, unk)
                        cur = None
                    else:
                        unk.append(p)
                p += 1
        flush(cur, unk)
    return regions


class RegionIndex:
    def __init__(self, regions):
        self.r = regions
        self.starts = [x["start"] for x in regions]

    def find(self, off):
        i = bisect.bisect_right(self.starts, off) - 1
        if i >= 0 and off < self.r[i]["end"]:
            return i
        return -1

    def covered(self, a, b):
        n = 0
        i = max(0, bisect.bisect_right(self.starts, a) - 1)
        while i < len(self.r) and self.r[i]["start"] < b:
            n += max(0, min(b, self.r[i]["end"]) - max(a, self.r[i]["start"]))
            i += 1
        return n


def string_starts(img, tbl, regions):
    starts = set()
    for r in regions:
        starts.add(r["start"])
        # strings often begin with a few control bytes (name, colour, portrait...)
        for k in range(1, 5):
            p = r["start"] - k
            if p < 0 or tbl.char_at(img, p) is not None:
                break
            starts.add(p)
        for u in r["unk"]:
            if u + 1 < r["end"]:
                starts.add(u + 1)
    return starts


def key_dict(fmt, starts):
    d = {}
    for f in starts:
        for key, ctx in fmt.keys(f):
            d.setdefault(key, {})[ctx] = f
    return d


def scan_tables(img, fmt, starts, kd, ridx, min_entries):
    found, isolated = [], []
    size, n_img = fmt.size, len(img)
    resolve = fmt.resolve

    def res(v, ctx):
        r = resolve(v, ctx) if resolve else None
        return r if r is not None and 0 <= r < n_img else None

    def close(phase, i0, i1, ctxs, vals):
        n = i1 - i0
        off = phase + i0 * size
        ctx = sorted(ctxs, key=lambda c: (not isinstance(c, int), str(c)))[0]
        hit = [kd.get(vals[i], {}).get(ctx) for i in range(i0, i1)]
        strong = sum(h is not None for h in hit)
        if strong < min_entries or strong < n * 0.4:
            if fmt.isolated_is_code:
                for i, h in zip(range(i0, i1), hit):
                    o = phase + i * size
                    if h is not None and ridx.find(o) < 0:
                        isolated.append((o, h))
            return
        if ridx.covered(off, off + n * size) > n * size * 0.5:
            return
        targets = [h if h is not None else res(vals[i], ctx) for i, h in zip(range(i0, i1), hit)]
        found.append({"off": off, "fmt": fmt.name, "size": size, "n": n, "strong": strong, "ctx": ctx, "targets": targets})

    if fmt.relative:
        sset = starts
        vals = fmt.values(img, 0)
        i = 0
        while i < len(vals):
            base = i * size
            k = i
            while k < len(vals) and vals[k] and (base + vals[k]) in sset:
                k += 1
            if k - i >= min_entries and ridx.covered(base, k * size) <= (k - i) * size * 0.5:
                found.append({"off": base, "fmt": fmt.name, "size": size, "n": k - i, "strong": k - i, "ctx": "table start",
                              "targets": [base + vals[j] for j in range(i, k)]})
                i = k
            else:
                i += 1
        return found, isolated

    phases = range(0, size, fmt.align) if fmt.align < size else [0]
    for phase in phases:
        vals = fmt.values(img, phase)
        get = kd.get
        allowed = fmt.allowed
        i0, ctxs, last = None, None, 0
        for i, v in enumerate(vals):
            c = get(v)
            cs = None
            if c is not None:
                if allowed:
                    o = phase + i * size
                    cs = {x for x in c if allowed(o, x)}
                else:
                    cs = set(c)
            if cs:
                if i0 is not None:
                    inter = ctxs & cs
                    if inter:
                        ctxs, last = inter, i
                        continue
                    close(phase, i0, last + 1, ctxs, vals)
                i0, ctxs, last = i, cs, i
            elif i0 is not None:
                if resolve and any(res(v, x) is not None for x in ctxs):
                    continue
                close(phase, i0, last + 1, ctxs, vals)
                i0 = None
        if i0 is not None:
            close(phase, i0, last + 1, ctxs, vals)
    return found, isolated


def dedupe_tables(tables):
    tables.sort(key=lambda t: (-t["n"], t["off"]))
    keep = []
    for t in tables:
        a, b = t["off"], t["off"] + t["n"] * t["size"]
        if any(a < k["off"] + k["n"] * k["size"] and k["off"] < b for k in keep):
            continue
        keep.append(t)
    keep.sort(key=lambda t: t["off"])
    return keep


def decode_string(img, p, tbl, term, limit):
    toks, start = [], p
    tl = len(term) if term else 0
    while p < len(img) and p - start < limit:
        if tl and img[p:p + tl] == term:
            return toks, p + tl, True
        r = tbl.char_at(img, p)
        if r:
            toks.append(("c", r[1]))
            p += r[0]
        else:
            toks.append(("x", img[p]))
            p += 1
    return toks, p, False


def show(toks, nl=None, maxlen=None):
    s = []
    for k, v in toks:
        s.append(v if k == "c" else ("/" if v == nl else f"[{v:02X}]"))
    out = "".join(s)
    if maxlen and len(out) > maxlen:
        out = out[:maxlen] + "..."
    return out


def median(a):
    if not a:
        return 0
    a = sorted(a)
    return a[len(a) // 2]


def pct(a, q):
    if not a:
        return 0
    a = sorted(a)
    return a[min(len(a) - 1, int(len(a) * q))]


def analyze_controls(strings, term_byte, nl_force, page_force):
    st = collections.defaultdict(lambda: {"n": 0, "strings": set(), "same": [], "next": collections.Counter(),
                                          "prev": collections.Counter(),
                                          "last": 0, "between_chars": 0, "between_strict": 0})
    for si, toks in enumerate(strings):
        pos, seen = 0, {}
        for j, (k, v) in enumerate(toks):
            if k == "c":
                pos += len(v)
                continue
            s = st[v]
            s["n"] += 1
            s["strings"].add(si)
            s["same"].append(pos - seen.get(v, 0))  # tokens since the same code (or the string start)
            pos += 1
            seen[v] = pos
            if j == len(toks) - 1:
                s["last"] += 1
            nxt = toks[j + 1] if j + 1 < len(toks) else None
            s["next"]["end" if nxt is None else ("char" if nxt[0] == "c" else f"{nxt[1]:02X}")] += 1
            prv = toks[j - 1] if j > 0 else None
            s["prev"]["start" if prv is None else ("char" if prv[0] == "c" else f"{prv[1]:02X}")] += 1
            if prv and nxt and (prv[0] == "c" or prv[1] == v) and (nxt[0] == "c" or nxt[1] == v):
                s["between_chars"] += 1
                if prv[0] == "c" and nxt[0] == "c":
                    s["between_strict"] += 1
    nstr = max(1, len(strings))
    common = [c for c, s in st.items() if c != term_byte and s["n"] >= 5 and len(s["strings"]) >= max(2, nstr * 0.05)]
    # a line break repeats at most every <window width> tokens, but not every few (a space does) and not twice in a row
    nl_c = sorted((c for c in common if pct(st[c]["same"], 0.98) <= 48 and median(st[c]["same"]) >= 6
                   and st[c]["next"][f"{c:02X}"] < st[c]["n"] * 0.1),
                  key=lambda c: -st[c]["n"])
    nl = nl_force if nl_force is not None else (nl_c[0] if nl_c else None)
    nl_med = median(st[nl]["same"]) if nl in st else 0
    nl_key = f"{nl:02X}" if nl is not None else None
    # a page break is rarer than a newline and is not itself followed by a newline (punctuation often is)
    page_c = sorted((c for c in common if c != nl and pct(st[c]["same"], 0.98) <= 200 and median(st[c]["same"]) > nl_med
                     and st[c]["next"][nl_key] < st[c]["n"] * 0.25 and st[c]["between_chars"] < st[c]["n"] * 0.3
                     and (st[c]["prev"][nl_key] >= st[c]["n"] * 0.2 or st[c]["next"]["char"] >= st[c]["n"] * 0.5)),
                    key=lambda c: -st[c]["n"])
    page = page_force if page_force is not None else (page_c[0] if page_c else None)
    charlike = sorted((c for c, s in st.items() if c not in (nl, page) and s["n"] >= 3 and s["between_chars"] >= s["n"] * 0.6
                       and s["between_strict"] >= s["n"] * 0.3),
                      key=lambda c: -st[c]["n"])
    for c, s in st.items():
        nxt_unk = sum(v for k, v in s["next"].items() if k not in ("char", "end"))
        if c == nl:
            s["guess"] = "newline?"
        elif c == page:
            s["guess"] = "new page / wait for button?"
        elif c in charlike:
            s["guess"] = "used like a character (missing table entry / DTE / dakuten kana?)"
            if c == charlike[0] and (len(charlike) == 1 or s["n"] >= 2 * st[charlike[1]]["n"]):
                s["guess"] = "used like a character - most frequent: space? (add --map XX=\" \")"
        elif s["n"] and s["last"] >= s["n"] * 0.6:
            s["guess"] = "end-type (before terminator)?"
        elif s["n"] and nxt_unk >= s["n"] * 0.6:
            s["guess"] = "control with argument byte(s)?"
        else:
            s["guess"] = "control?"
    return st, nl, page, set(charlike)


def line_stats(strings, nl, page, charlike):
    """Widths of lines ended by a newline/page code, counted two ways: (table chars + char-like codes, every token).
    The real width lies in between: unknown codes may be kana/DTE (count) or control codes (do not)."""
    widths, lines = [], []
    for toks in strings:
        w, wa, nlines = 0, 0, 1
        for k, v in toks:
            if k == "c":
                w += len(v)
                wa += len(v)
            elif v == nl:
                widths.append((w, wa))
                w = wa = 0
                nlines += 1
            elif v == page:
                widths.append((w, wa))
                lines.append(nlines)
                w = wa = 0
                nlines = 1
            else:
                wa += 1
                if v in charlike:
                    w += 1
        lines.append(nlines)
    return widths, lines


def entropy_blocks(img, block=4096, limit=7.5):
    n = 0
    for p in range(0, len(img) - block + 1, block):
        c = collections.Counter(img[p:p + block])
        h = -sum(v / block * math.log2(v / block) for v in c.values())
        if h > limit:
            n += 1
    return n


def fixed_fields(img, r, term):
    if not term:
        return None
    s, e = r["start"], r["end"] + len(term)
    pos = [m.start() for m in re.finditer(re.escape(term), img[s:e])]
    if len(pos) >= 4:
        gaps = {b - a for a, b in zip(pos, pos[1:])}
        if len(gaps) == 1:
            return f"fixed {gaps.pop()}-byte fields"
        return f"{len(pos)} terminated strings"
    return None


# ---------------------------------------------------------------------------------------------
# Main

def common_args(ap):
    ap.add_argument("rom")
    ap.add_argument("-o", "--out", help="report file (default: <rom>.text.txt)")
    ap.add_argument("--tbl", help="use this Thingy .tbl table ('/XX' = end, '*XX' = newline)")
    ap.add_argument("--known", action="append", default=[], metavar="WORD",
                    help="relative search: a word that appears in the game (repeat for upper case, lower case, kana)")
    ap.add_argument("--map", action="append", default=[], metavar="XX=c", help="add a table entry, e.g. --map 20=\" \"")
    ap.add_argument("--encoding", choices=["auto", "ascii", "sjis"], default="auto",
                    help="table to try when no --tbl/--known is given (default auto)")
    ap.add_argument("--char-width", type=int, choices=[1, 2], default=1, help="bytes per character for --known (default 1)")
    ap.add_argument("--end", help="terminator byte(s) in hex (default: detected)")
    ap.add_argument("--newline", help="newline code in hex (default: guessed)")
    ap.add_argument("--page", help="new page / wait code in hex (default: guessed)")
    ap.add_argument("--min-chars", type=int, default=8, help="shortest text run counted as a text region (default 8)")
    ap.add_argument("--max-gap", type=int, help="unknown bytes allowed inside a text run (default 3 for small tables, 1 otherwise)")
    ap.add_argument("--min-ratio", type=float, help="share of text bytes in a region (default 0.6 / 0.8)")
    ap.add_argument("--min-entries", type=int, default=4, help="shortest pointer table (default 4)")
    ap.add_argument("--any-bank", action="store_true", help="banked systems: allow 16-bit pointers into any bank")
    ap.add_argument("--max-len", type=int, default=1024, help="longest string decoded from a pointer (default 1024 bytes)")
    ap.add_argument("--top", type=int, default=20, help="rows per list in the report (default 20)")
    ap.add_argument("--dump", action="store_true", help="also write <rom>.strings.txt with every pointed string")
    ap.add_argument("--emu", action="store_true",
                    help="also run the ROM in a libretro core and use what is on screen as evidence")
    ap.add_argument("--emu-core", help="libretro core name or path for --emu (default: by system)")
    ap.add_argument("--emu-script", help="capture plan for --emu ('## name' starts a step; see TEXTFACTS.md)")
    ap.add_argument("--emu-keep", help="keep the --emu captures in this directory")


def run_emulator(args):
    """Boot the ROM in a libretro core and correlate the screen with the ROM image."""
    try:
        import emufacts
    except ImportError as e:
        return {"error": f"emufacts.py not importable: {e}"}
    try:
        plan = emufacts.parse_plan(args.emu_script) if args.emu_script else None
        facts, matches, info = emufacts.collect(args.rom, core=args.emu_core, plan=plan, keep=args.emu_keep)
        return {"facts": facts, "matches": matches, "info": info}
    except Exception as e:
        return {"error": str(e)}


def emu_runs(emu):
    """ROM spans that were seen on screen."""
    if not emu or "error" in emu:
        return []
    return [m for m in emu["matches"] if m["kind"] in ("line", "tilemap")]


def emu_geom(emu):
    """Window geometry and fixed-width verdict measured on screen, or (None, None)."""
    ef = emu["facts"] if emu and "error" not in emu else {}
    if not ef.get("text_matches"):
        return None, None
    win = (f"measured on screen: line ~{ef['width_med']} chars typical, up to {ef['width_max']}; "
           f"{ef['rows_max']} line(s) at once"
           + (f"; row pitch {ef['pitch']}" if ef.get("pitch") else ""))
    vwf = ("fixed width - the emulator drew this text as tile indices, one tile per character"
           if ef.get("fixed") else None)
    return win, vwf


def emu_lines(emu, A, top):
    out = ["", "== Emulator evidence =="]
    if "error" in emu:
        return out + [f"  not collected: {emu['error']}"]
    f, info = emu["facts"], emu["info"]
    runs = emu_runs(emu)
    out.append(f"  core {info['core']}, {len(info.get('captures', []))} capture(s); "
               f"{f.get('text_matches', 0)} run(s) of ROM text found on screen")
    if not runs:
        return out + ["  nothing matched: the capture never reached a text screen, or the text is",
                      "  decompressed / DTE-encoded before it is drawn. Try --emu-script with a route into dialogue."]
    out.append(f"  stored code -> drawn tile: +{hx(f['delta'])} ({f['delta_n']} run(s) agree); "
               f"row pitch {f['pitch'] if f.get('pitch') else '?'}; up to {f['rows_max']} line(s) at once")
    out += ["  These ROM offsets are text for certain - the emulator drew them.",
            "  rom offset      address        len  delta  capture           on-screen at"]
    out += [f"  {m['rom']:06X}-{m['end']:06X}  {A(m['rom']):13} {m['len']:4}  {hx(m['delta'])}   "
            f"{m['buf']:16}  {m['src']:#07x}" for m in sorted(runs, key=lambda m: -m["len"])[:top]]
    if len(runs) > top:
        out.append(f"  ... {len(runs) - top} more")
    return out


def pick_table(img, args, log):
    if args.tbl:
        t = load_tbl(args.tbl)
        src = f"{args.tbl} (given)"
    elif args.known:
        t = build_known_table(img, args.known, args.char_width, PLATFORM.big, log)
        src = "generated by relative search"
    else:
        t = None
        src = ""
    if t is not None:
        for m in args.map:
            k, _, v = m.partition("=")
            t.chars[bytes.fromhex(k)] = v
        t.finalize()
        if not t.chars:
            return None, "no table: relative search found nothing"
        return t, src
    cands = []
    if args.encoding in ("auto", "ascii"):
        cands.append(AsciiTable())
    if args.encoding in ("auto", "sjis"):
        cands.append(SjisTable())
    best, best_n = None, 0
    for c in cands:
        regs = find_regions(img, c, max(args.min_chars, 12), 1, 0.85)
        n = sum(r["end"] - r["start"] for r in regs)
        log.append(f"{c.name}: {len(regs)} region(s), {n:,} bytes of text-like data")
        # Shift-JIS also matches ASCII: it has to find clearly more text to win
        if n > best_n * (1.2 if c.kind == "sjis" else 1):
            best, best_n = c, n
    if best is None or best_n < 512:
        return None, "custom encoding (no ASCII / Shift-JIS text found): run again with --known WORD or --tbl FILE"
    for m in args.map:
        k, _, v = m.partition("=")
        best.chars[bytes.fromhex(k)] = v
    best.finalize()
    return best, f"{best.name} (auto-detected)"


def kv(rows):
    w = max((len(k) for k, _ in rows), default=0)
    return "\n".join(f"{k.ljust(w)} : {v}" for k, v in rows)


def run(platform, argv=None):
    global PLATFORM
    PLATFORM = platform
    ap = argparse.ArgumentParser(description=f"Collect the Text facts of a {platform.name} ROM (candidates from static analysis).")
    common_args(ap)
    platform.setup_args(ap)
    args = ap.parse_args(argv)
    with open(args.rom, "rb") as fh:
        data = fh.read()
    img = platform.load(data, args)
    A = platform.addr
    log = []
    emu = run_emulator(args) if getattr(args, "emu", False) else None
    tbl, tsrc = pick_table(img, args, log)

    out = [f"Text fact sheet - {os.path.basename(args.rom)}", f"Platform: {platform.name}"]
    sheet = []
    if tbl is None:
        runs = emu_runs(emu)
        seen = (f"{len(runs)} ROM run(s) confirmed on screen by the emulator - see Emulator evidence"
                if runs else TODO)
        mwin, mvwf = emu_geom(emu)
        sheet = [("Table file", tsrc), ("Text confirmed on screen", seen)] + \
                [(k, TODO) for k in ("Control codes", "Dictionary / DTE / compression",
                                     "Pointer tables", "Hard-coded pointers")] + \
                [("Window size / line width / lines per page", mwin or TODO),
                 ("Fixed width or VWF", mvwf or f"{TODO} {platform.vwf_hint}".rstrip()),
                 ("Non-script text", TODO)]
        out += ["", "== Text ==", kv(sheet), "", "== Encoding ==", *log]
        if emu:
            out += emu_lines(emu, A, args.top)
        return finish(args, out, platform)

    dense = tbl.density >= 0.3
    max_gap = args.max_gap if args.max_gap is not None else (1 if dense else 3)
    min_ratio = args.min_ratio if args.min_ratio is not None else (0.8 if dense else 0.6)
    regions = find_regions(img, tbl, args.min_chars, max_gap, min_ratio)
    ridx = RegionIndex(regions)
    starts = string_starts(img, tbl, regions)

    tbl_file = None
    if tbl.kind == "table" and not args.tbl:
        tbl_file = args.rom + ".tbl"

    # pointer tables
    fmts = platform.formats(args)
    tables, isolated = [], []
    kds = {}
    for fmt in fmts:
        kd = None if fmt.relative else key_dict(fmt, starts)
        kds[fmt.name] = kd
        f, iso = scan_tables(img, fmt, starts, kd, ridx, args.min_entries)
        for t in f:
            t["targets"] = [x for x in t["targets"] if x is not None]
        tables += f
        isolated += [(o, fmt.name, t) for o, t in iso]
    tables = dedupe_tables(tables)

    # terminator
    term = bytes.fromhex(args.end) if args.end else None
    if term is None:
        ends = [k for k, v in tbl.ctrl.items() if v == "end"]
        term = ends[0] if ends else None
    if term is None:
        w = tbl.width if tbl.kind == "table" else 1
        c = collections.Counter()
        for t in tables:
            for x in t["targets"]:
                if x >= w and all(tbl.char_at(img, x - w + i) is None for i in range(w)):
                    c[img[x - w:x]] += 1
        if not c:
            for r in regions:
                if r["end"] + w <= len(img):
                    c[img[r["end"]:r["end"] + w]] += 1
        term = c.most_common(1)[0][0] if c else None
    strong = {s for s in starts if term is None or img[max(0, s - len(term)):s] == term or ridx.find(s - 1) < 0}

    # hard-coded pointers
    in_tables = sorted((t["off"], t["off"] + t["n"] * t["size"]) for t in tables)

    def in_table(o):
        i = bisect.bisect_right(in_tables, (o, 1 << 62)) - 1
        return i >= 0 and o < in_tables[i][1]

    fmt_by = {f.name: f for f in fmts}
    code_hits = []
    for cp in platform.code_patterns(args):
        fmt = fmt_by.get(cp.fmt)
        kd = kds.get(cp.fmt)
        for m in cp.regex.finditer(img):
            o = m.start()
            if o % cp.align or ridx.find(o) >= 0 or in_table(o):
                continue
            if cp.target:
                f = cp.target(m, o)
                if f is not None and f in strong:
                    code_hits.append((o, cp.name, f))
            elif kd is not None:
                c = kd.get(cp.value(m))
                if not c:
                    continue
                for ctx, f in c.items():
                    if f in strong and (fmt.allowed is None or fmt.allowed(o, ctx)):
                        code_hits.append((o, cp.name, f))
                        break
    for o, name, f in isolated:
        if f in strong and not in_table(o):
            code_hits.append((o, f"{name} (lone pointer / literal pool)", f))
    code_hits.sort()

    # strings and controls
    targets = sorted({x for t in tables for x in t["targets"]} | {f for _, _, f in code_hits})
    strings, spans = [], []
    for x in targets:
        toks, end, ok = decode_string(img, x, tbl, term, args.max_len)
        strings.append(toks)
        spans.append((x, end if ok else x + 1))
    nl_force = int(args.newline, 16) if args.newline else next((k[0] for k, v in tbl.ctrl.items() if v == "newline"), None)
    page_force = int(args.page, 16) if args.page else None
    term_byte = term[0] if term and len(term) == 1 else None
    st, nl, page, charlike_set = analyze_controls(strings, term_byte, nl_force, page_force)
    widths, lines = line_stats(strings, nl, page, charlike_set)

    # referenced regions
    referenced = set()
    for a, b in spans:
        i = max(0, bisect.bisect_right(ridx.starts, a) - 1)
        while i < len(regions) and regions[i]["start"] < max(b, a + 2):
            if regions[i]["end"] > a:
                referenced.add(i)
            i += 1
    unref = [r for i, r in enumerate(regions) if i not in referenced]
    # score blocks by how close their characters are to the pointed script (graphics/data score low)
    prof = collections.Counter(v for toks in strings for k, v in toks if k == "c")
    ptotal = sum(prof.values())

    def pairs(toks):
        return [(a[1], b[1]) for a, b in zip(toks, toks[1:]) if a[0] == "c" and b[0] == "c"]
    if ptotal >= 200:
        V = len(tbl.chars) + 1
        big = collections.Counter(p for toks in strings for p in pairs(toks))

        def lp(p):
            a, b = p
            uni = (prof[b] + 0.5) / (ptotal + 0.5 * V)
            return math.log2(0.7 * big[p] / prof[a] + 0.3 * uni if prof[a] else uni)
        allp = [p for toks in strings for p in pairs(toks)]
        base = sum(map(lp, allp)) / max(1, len(allp))
        for r in unref:
            toks, _, _ = decode_string(img, r["start"], tbl, None, r["end"] - r["start"])
            ps = pairs(toks)
            r["score"] = sum(map(lp, ps)) / len(ps) - base if ps else -99
    likely = [r for r in unref if r.get("score", 0) >= -1.0]
    for r in unref:
        r["tend"] = bool(term) and term in img[r["end"]:r["end"] + 4 + len(term)]

    # DTE / compression
    charlike = sorted(charlike_set)
    total_bytes = sum(len(t) for t in strings) or 1
    charlike_n = sum(st[c]["n"] for c in charlike)
    dte = "none detected"
    if len(charlike) >= 8:
        dte = (f"{len(charlike)} codes used like characters ({hx(charlike[0])}-{hx(charlike[-1])}, "
               f"{100 * charlike_n / total_bytes:.0f}% of string bytes): DTE/dictionary or kana/kanji not in the table")
    elif charlike:
        dte = "a few character-like codes not in the table: " + " ".join(hx(c) for c in charlike)
    ent = entropy_blocks(img)
    comp = f"{ent * 4} KB in 4 KB blocks look compressed or random (entropy > 7.5 bits/byte)" if ent else "no high-entropy blocks"
    ctx = Ctx()
    ctx.img, ctx.tbl, ctx.regions, ctx.term, ctx.args, ctx.tables = img, tbl, regions, term, args, tables
    extra = platform.extra(ctx)

    # ---------------- report ----------------
    ctl_summary = [f"{hexb(term)} end (terminator)" if term else "terminator not found"]
    if nl is not None:
        ctl_summary.append(f"{hx(nl)} newline?")
    if page is not None:
        ctl_summary.append(f"{hx(page)} new page / wait?")
    others = [c for c in st if c not in (nl, page, term_byte) and not st[c]["guess"].startswith("used like")]
    if others:
        ctl_summary.append(f"{len(others)} other code(s) - see Control codes")
    tsum = "none found"
    if tables:
        big = sorted(tables, key=lambda t: -t["n"])[:3]
        tsum = f"{len(tables)} found ({sum(t['n'] for t in tables)} entries); largest: " + "; ".join(
            f"{A(t['off'])} {t['fmt']} x{t['n']}" for t in big)
    win = TODO
    if widths:
        lo = [a for a, _ in widths]
        hi = [b for _, b in widths]
        win = (f"line width ~{pct(lo, 0.99)}-{pct(hi, 0.99)} chars (99th percentile; table chars only - all bytes), "
               f"lines per page ~{pct(lines, 0.99)} (max {max(lines)}) - estimate, confirm in game")
    vwf = f"{TODO} {platform.vwf_hint}".rstrip()
    mwin, mvwf = emu_geom(emu)
    if mwin:
        win = mwin + (f"; static estimate: {win}" if widths else "")
        if mvwf:
            vwf = mvwf
    unref_big = sorted(likely, key=lambda r: (not r.get("tend"), -(r["end"] - r["start"])))
    unref_big += sorted((r for r in unref if r.get("score", 0) < -1.0), key=lambda r: -r["score"])
    runs = emu_runs(emu)
    spans = sorted((m["rom"], m["end"]) for m in runs)

    def on_screen(a, b):
        i = bisect.bisect_right(spans, (b, 1 << 62)) - 1
        return i >= 0 and spans[i][1] > a

    sheet = [
        ("Table file", f"{tbl_file or args.tbl} ({len(tbl.chars)} entries; {tsrc})" if tbl.kind == "table" else tsrc),
        ("Control codes", "; ".join(ctl_summary)),
        ("Dictionary / DTE / compression", f"{dte}; {comp}" + ("; " + "; ".join(v for _, v in extra) if extra else "")),
        ("Pointer tables", tsum),
        ("Hard-coded pointers", f"{len(code_hits)} found" + (" - see list" if code_hits else "")),
        ("Window size / line width / lines per page", win),
        ("Fixed width or VWF", vwf),
        ("Non-script text", f"{len(likely)} text block(s) not reached by any pointer and similar to the script "
                            f"({sum(r['tend'] for r in likely)} end with the terminator; menus, names, fixed fields, "
                            f"jump targets?) + {len(unref) - len(likely)} less likely - see list"
                            if unref else "none found outside pointed strings"),
    ]
    if emu:
        sheet.insert(1, ("Text confirmed on screen",
                         f"{len(runs)} ROM run(s) drawn by the emulator - see Emulator evidence"
                         if runs else "nothing matched - see Emulator evidence"))
    out += ["", "== Text ==", kv(sheet)]

    out += ["", "== Encoding ==", f"Table: {tsrc}"] + [f"  {x}" for x in log]
    if tbl_file:
        out.append(f"  written to {tbl_file} (check it with the font in a tile viewer; add missing codes with --map)")
    out += ["", "== Text regions ==",
            f"{len(regions)} region(s), {sum(r['end'] - r['start'] for r in regions):,} bytes "
            f"(min {args.min_chars} chars, gap <= {max_gap}, text share >= {min_ratio})"
            + ("; '*' = seen on screen in the emulator" if runs else "")]
    for r in sorted(regions, key=lambda r: -(r["end"] - r["start"]))[:args.top]:
        toks, _, _ = decode_string(img, r["start"], tbl, None, min(48, r["end"] - r["start"]))
        mark = "*" if on_screen(r["start"], r["end"]) else " "
        out.append(f"  {mark} {r['start']:06X}-{r['end']:06X}  {A(r['start'])}  {r['end'] - r['start']:7,} B  {show(toks, nl, 40)}")

    out += ["", "== Pointer tables ==", "  'entries' = total / pointing at a detected string start",
            "  file    address        format                         entries   target   first strings"]
    for t in sorted(tables, key=lambda t: -t["n"])[:args.top]:
        tgt = t["targets"]
        ctxs = t["ctx"] if isinstance(t["ctx"], str) else (f"bank {t['ctx']:02X}" if isinstance(t["ctx"], int) else "absolute")
        sample = " | ".join(show(decode_string(img, x, tbl, term, 64)[0], nl, 18) for x in tgt[:2])
        out.append(f"  {t['off']:06X}  {A(t['off']):13}  {t['fmt']:30} {t['n']:4}/{t['strong']:<4} {ctxs:8} "
                   f"-> {A(min(tgt))}..{A(max(tgt))}  {sample}")
    if len(tables) > args.top:
        out.append(f"  ... {len(tables) - args.top} more")

    out += ["", "== Hard-coded pointers ==", "  code at  address        pattern                        -> string"]
    for o, name, f in code_hits[:args.top * 2]:
        out.append(f"  {o:06X}   {A(o):13}  {name:30} -> {A(f)}  {show(decode_string(img, f, tbl, term, 64)[0], nl, 30)}")
    if len(code_hits) > args.top * 2:
        out.append(f"  ... {len(code_hits) - args.top * 2} more")

    out += ["", "== Control codes ==",
            f"  from {len(strings)} pointed string(s); 'repeat' = characters since the same code (or string start); 'next' = what follows",
            "  code   count strings  repeat(median/max)  next (top 3)                guess"]
    for c in sorted(st, key=lambda c: -st[c]["n"])[:args.top * 2]:
        s = st[c]
        nxt = ", ".join(f"{k}:{v}" for k, v in s["next"].most_common(3))
        out.append(f"  {hx(c)}  {s['n']:7} {len(s['strings']):7}  {median(s['same']):6}/{max(s['same']):<8}     {nxt:28} {s['guess']}")
    if term:
        out.append(f"  terminator {hexb(term)} (from the bytes before pointed strings)" if not args.end else f"  terminator {args.end} (given)")

    out += ["", "== Non-script text candidates ==",
            "  'score' = how close the characters are to the pointed script (0 = same, below -1.0 = probably data); "
            "'T' = followed by the terminator",
            "  file    address        bytes  score T  layout                  preview"]
    for r in unref_big[:args.top]:
        toks, _, _ = decode_string(img, r["start"], tbl, None, min(80, r["end"] - r["start"]))
        sc = f"{r['score']:5.1f}" if "score" in r else "    -"
        out.append(f"  {r['start']:06X}  {A(r['start']):13} {r['end'] - r['start']:6}  {sc} {'T' if r['tend'] else ' '}  "
                   f"{(fixed_fields(img, r, term) or ''):23} {show(toks, nl, 44)}")

    notes = list(platform.notes) + [
        "All values are candidates from static analysis: confirm control codes, window size and VWF in a debugger.",
        "Pointer tables are matched against string starts inside text regions; tables whose entries point to "
        "compressed/DTE text, split low/high-byte tables and pointers with a bank byte elsewhere are not found.",
    ]
    if runs:
        notes.append("Rows marked '*' and everything under Emulator evidence were seen on screen, so they are "
                     "measurements rather than guesses.")
    out += ["", "== Notes =="] + [f"- {n}" for n in notes]
    if emu:
        out += emu_lines(emu, A, args.top)

    if tbl_file:
        with open(tbl_file, "w", encoding="utf-8", newline="\n") as fh:
            for k in sorted(tbl.chars):
                fh.write(f"{hexb(k)}={tbl.chars[k]}\n")
            if term:
                fh.write(f"/{hexb(term)}\n")
            if nl is not None:
                fh.write(f"*{nl:02X}\n")
    if args.dump:
        dpath = args.rom + ".strings.txt"
        with open(dpath, "w", encoding="utf-8", newline="\n") as fh:
            for t in tables:
                fh.write(f"# table {A(t['off'])} ({t['fmt']}, {t['n']} entries)\n")
                for i, x in enumerate(t["targets"]):
                    fh.write(f"[{i:03}] {A(x)}  {show(decode_string(img, x, tbl, term, args.max_len)[0], nl)}\n")
            if code_hits:
                fh.write("# hard-coded pointers\n")
                for o, name, f in code_hits:
                    fh.write(f"{A(o)} -> {A(f)}  {show(decode_string(img, f, tbl, term, args.max_len)[0], nl)}\n")
        print(f"wrote {dpath}")
    return finish(args, out, platform)


def finish(args, out, platform):
    path = args.out or args.rom + ".text.txt"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"{platform.name}: wrote {path}")
    return 0


PLATFORM = None
