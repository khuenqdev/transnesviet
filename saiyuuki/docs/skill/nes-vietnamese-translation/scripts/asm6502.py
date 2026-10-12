#!/usr/bin/env python3
"""Tiny two-pass 6502 assembler (official opcodes) used by the Saiyuuki World patch builder.

Supported syntax (one statement per line, ';' comments):
    label:                 define label (may share a line with an instruction)
    NAME = expr            constant
    .org  expr             set location counter (CPU address)
    .db   e1, e2, "str"    bytes
    .dw   e1, e2           little-endian words
    .ds   n [, fill]       reserve n bytes
    .align n               pad with 0xFF until (pc % n)==0
    LDA #expr / LDA expr / LDA expr,X / LDA (expr),Y / LDA (expr,X) / JMP (expr) / ASL A
Expressions: numbers ($hex, %bin, decimal, 'c'), labels, + - * and unary < (low byte) / > (high byte).
Zero-page vs absolute is chosen automatically (labels known only later default to absolute).
"""
import re
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from dis6502 import OPS  # opcode -> (mnemonic, mode)

# reverse table: (mnemonic, mode) -> opcode
REV = {}
for op, (mn, mode) in OPS.items():
    REV[(mn, mode)] = op

BRANCHES = {'BPL', 'BMI', 'BVC', 'BVS', 'BCC', 'BCS', 'BNE', 'BEQ'}
LEN = {'imp': 1, 'acc': 1, 'imm': 2, 'zp': 2, 'zpx': 2, 'zpy': 2, 'izx': 2, 'izy': 2, 'rel': 2,
       'abs': 3, 'abx': 3, 'aby': 3, 'ind': 3}


class AsmError(Exception):
    pass


def _num(tok, labels, pc, final):
    tok = tok.strip()
    if tok == '*':
        return pc
    if tok.startswith('$'):
        return int(tok[1:], 16)
    if tok.startswith('%'):
        return int(tok[1:], 2)
    if re.fullmatch(r'\d+', tok):
        return int(tok)
    if re.fullmatch(r"'.'", tok):
        return ord(tok[1])
    if tok in labels:
        return labels[tok]
    if final:
        raise AsmError('undefined symbol %r' % tok)
    return 0x8000  # unknown yet: pretend absolute


def evaluate(expr, labels, pc, final):
    expr = expr.strip()
    if expr.startswith('<'):
        return evaluate(expr[1:], labels, pc, final) & 0xFF
    if expr.startswith('>'):
        return (evaluate(expr[1:], labels, pc, final) >> 8) & 0xFF
    # split on + - * at top level (no parentheses supported inside expr)
    toks = re.findall(r"[+\-*]|[^+\-*]+", expr)
    # handle a leading '*' meaning current pc
    val = 0
    sign = 1
    i = 0
    first = True
    while i < len(toks):
        t = toks[i].strip()
        if t in '+-' and t:
            sign = 1 if t == '+' else -1
            i += 1
            continue
        if t == '*' and first:
            val += sign * pc
        else:
            val += sign * _num(t, labels, pc, final)
        sign = 1
        first = False
        i += 1
    return val


def _split_args(s):
    out, cur, q = [], '', False
    for ch in s:
        if ch == '"':
            q = not q
            cur += ch
        elif ch == ',' and not q:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_operand(mn, op):
    """Return (mode, expr)."""
    op = op.strip()
    if not op:
        return 'imp', None
    if op.upper() == 'A':
        return 'acc', None
    if op.startswith('#'):
        return 'imm', op[1:]
    m = re.fullmatch(r'\((.+),\s*[xX]\)', op)
    if m:
        return 'izx', m.group(1)
    m = re.fullmatch(r'\((.+)\)\s*,\s*[yY]', op)
    if m:
        return 'izy', m.group(1)
    m = re.fullmatch(r'\((.+)\)', op)
    if m:
        return 'ind', m.group(1)
    m = re.fullmatch(r'(.+),\s*[xX]', op)
    if m:
        return 'abx', m.group(1)   # resolved to zpx later
    m = re.fullmatch(r'(.+),\s*[yY]', op)
    if m:
        return 'aby', m.group(1)
    return 'abs', op


def assemble(src, origin=0x8000, symbols=None):
    """Assemble text. Returns (bytes_by_segment list[(addr, bytes)], labels dict)."""
    lines = []
    for raw in src.splitlines():
        line = raw.split(';')[0].rstrip()
        if line.strip():
            lines.append(line)
    labels = dict(symbols or {})
    segments = None
    for final in (False, True):
        pc = origin
        segs = []
        cur = bytearray()
        start = pc

        def flush():
            nonlocal cur, start
            if cur:
                segs.append((start, bytes(cur)))
            cur = bytearray()

        for line in lines:
            s = line.strip()
            # constants:  NAME = expr
            m = re.fullmatch(r'([A-Za-z_][\w.]*)\s*=\s*(.+)', s)
            if m:
                labels[m.group(1)] = evaluate(m.group(2), labels, pc, final)
                continue
            # labels
            while True:
                m = re.match(r'([A-Za-z_@][\w.@]*):\s*(.*)', s)
                if not m:
                    break
                labels[m.group(1)] = pc
                s = m.group(2)
            if not s:
                continue
            parts = s.split(None, 1)
            mn = parts[0]
            rest = parts[1] if len(parts) > 1 else ''
            if mn.startswith('.'):
                d = mn.lower()
                if d == '.org':
                    flush()
                    pc = evaluate(rest, labels, pc, final)
                    start = pc
                elif d == '.db':
                    for a in _split_args(rest):
                        if a.startswith('"'):
                            b = a.strip('"').encode('latin-1')
                            cur += b
                            pc += len(b)
                        else:
                            cur.append(evaluate(a, labels, pc, final) & 0xFF)
                            pc += 1
                elif d == '.dw':
                    for a in _split_args(rest):
                        v = evaluate(a, labels, pc, final) & 0xFFFF
                        cur += bytes([v & 0xFF, v >> 8])
                        pc += 2
                elif d == '.ds':
                    a = _split_args(rest)
                    n = evaluate(a[0], labels, pc, final)
                    fill = evaluate(a[1], labels, pc, final) if len(a) > 1 else 0xFF
                    cur += bytes([fill & 0xFF]) * n
                    pc += n
                elif d == '.align':
                    n = evaluate(rest, labels, pc, final)
                    while pc % n:
                        cur.append(0xFF)
                        pc += 1
                else:
                    raise AsmError('unknown directive ' + mn)
                continue
            mn = mn.upper()
            mode, expr = parse_operand(mn, rest)
            if mn in BRANCHES:
                tgt = evaluate(expr, labels, pc, final)
                off = tgt - (pc + 2)
                if final and not -128 <= off <= 127:
                    raise AsmError('branch out of range at $%04X -> %s (%d)' % (pc, expr, off))
                cur += bytes([REV[(mn, 'rel')], off & 0xFF])
                pc += 2
                continue
            if mode in ('abs', 'abx', 'aby') and expr is not None:
                v = evaluate(expr, labels, pc, final)
                known = (not final and not re.fullmatch(r"\$[0-9A-Fa-f]{1,2}|\d{1,3}", expr.strip())
                         and re.search(r'[A-Za-z_]', expr) and expr.strip() not in labels)
                zp_ok = 0 <= v < 0x100 and not known
                zmode = {'abs': 'zp', 'abx': 'zpx', 'aby': 'zpy'}[mode]
                if zp_ok and (mn, zmode) in REV:
                    mode = zmode
            if (mn, mode) not in REV:
                raise AsmError('bad addressing mode %s %s (%s)' % (mn, mode, rest))
            op = REV[(mn, mode)]
            ln = LEN[mode]
            if ln == 1:
                cur.append(op)
            else:
                v = evaluate(expr, labels, pc, final)
                if ln == 2:
                    if final and not -128 <= v <= 255:
                        raise AsmError('operand out of range: %s' % s)
                    cur += bytes([op, v & 0xFF])
                else:
                    cur += bytes([op, v & 0xFF, (v >> 8) & 0xFF])
            pc += ln
        flush()
        segments = segs
    return segments, labels


if __name__ == '__main__':
    segs, labels = assemble(open(sys.argv[1]).read(), int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x8000)
    for a, b in segs:
        print('$%04X: %s' % (a, b.hex(' ')))
    print(labels)
