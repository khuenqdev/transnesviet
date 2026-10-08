// Minimal 6502 assembler. asm(src, org, syms) -> { bytes: Buffer, labels }
// Syntax: "label:" ; "OP operand" ; ".db a,b" ; ".dw w" ; comments with ';'
// Operand forms: #v, v, v,X, v,Y, (v),Y, (v,X), (v). Values: $hex, decimal, label, label+n, <v, >v
const OPS = {
  ADC: { imm: 0x69, zp: 0x65, zpx: 0x75, abs: 0x6D, absx: 0x7D, absy: 0x79, indx: 0x61, indy: 0x71 },
  AND: { imm: 0x29, zp: 0x25, zpx: 0x35, abs: 0x2D, absx: 0x3D, absy: 0x39, indx: 0x21, indy: 0x31 },
  ASL: { acc: 0x0A, zp: 0x06, zpx: 0x16, abs: 0x0E, absx: 0x1E },
  BIT: { zp: 0x24, abs: 0x2C },
  BPL: { rel: 0x10 }, BMI: { rel: 0x30 }, BVC: { rel: 0x50 }, BVS: { rel: 0x70 }, BCC: { rel: 0x90 }, BCS: { rel: 0xB0 }, BNE: { rel: 0xD0 }, BEQ: { rel: 0xF0 },
  BRK: { imp: 0x00 },
  CMP: { imm: 0xC9, zp: 0xC5, zpx: 0xD5, abs: 0xCD, absx: 0xDD, absy: 0xD9, indx: 0xC1, indy: 0xD1 },
  CPX: { imm: 0xE0, zp: 0xE4, abs: 0xEC }, CPY: { imm: 0xC0, zp: 0xC4, abs: 0xCC },
  DEC: { zp: 0xC6, zpx: 0xD6, abs: 0xCE, absx: 0xDE },
  EOR: { imm: 0x49, zp: 0x45, zpx: 0x55, abs: 0x4D, absx: 0x5D, absy: 0x59, indx: 0x41, indy: 0x51 },
  CLC: { imp: 0x18 }, SEC: { imp: 0x38 }, CLI: { imp: 0x58 }, SEI: { imp: 0x78 }, CLV: { imp: 0xB8 }, CLD: { imp: 0xD8 }, SED: { imp: 0xF8 },
  INC: { zp: 0xE6, zpx: 0xF6, abs: 0xEE, absx: 0xFE },
  JMP: { abs: 0x4C, ind: 0x6C }, JSR: { abs: 0x20 },
  LDA: { imm: 0xA9, zp: 0xA5, zpx: 0xB5, abs: 0xAD, absx: 0xBD, absy: 0xB9, indx: 0xA1, indy: 0xB1 },
  LDX: { imm: 0xA2, zp: 0xA6, zpy: 0xB6, abs: 0xAE, absy: 0xBE },
  LDY: { imm: 0xA0, zp: 0xA4, zpx: 0xB4, abs: 0xAC, absx: 0xBC },
  LSR: { acc: 0x4A, zp: 0x46, zpx: 0x56, abs: 0x4E, absx: 0x5E },
  NOP: { imp: 0xEA },
  ORA: { imm: 0x09, zp: 0x05, zpx: 0x15, abs: 0x0D, absx: 0x1D, absy: 0x19, indx: 0x01, indy: 0x11 },
  TAX: { imp: 0xAA }, TXA: { imp: 0x8A }, DEX: { imp: 0xCA }, INX: { imp: 0xE8 }, TAY: { imp: 0xA8 }, TYA: { imp: 0x98 }, DEY: { imp: 0x88 }, INY: { imp: 0xC8 },
  ROL: { acc: 0x2A, zp: 0x26, zpx: 0x36, abs: 0x2E, absx: 0x3E },
  ROR: { acc: 0x6A, zp: 0x66, zpx: 0x76, abs: 0x6E, absx: 0x7E },
  RTI: { imp: 0x40 }, RTS: { imp: 0x60 },
  SBC: { imm: 0xE9, zp: 0xE5, zpx: 0xF5, abs: 0xED, absx: 0xFD, absy: 0xF9, indx: 0xE1, indy: 0xF1 },
  STA: { zp: 0x85, zpx: 0x95, abs: 0x8D, absx: 0x9D, absy: 0x99, indx: 0x81, indy: 0x91 },
  STX: { zp: 0x86, zpy: 0x96, abs: 0x8E }, STY: { zp: 0x84, zpx: 0x94, abs: 0x8C },
  TXS: { imp: 0x9A }, TSX: { imp: 0xBA }, PHA: { imp: 0x48 }, PLA: { imp: 0x68 }, PHP: { imp: 0x08 }, PLP: { imp: 0x28 },
};

function asm(src, org, syms = {}) {
  const lines = src.split('\n').map(l => l.replace(/;.*/, '').trim()).filter(Boolean);
  let labels = {};
  const evalv = (s, pass) => {
    s = s.trim();
    if (s[0] === '<') { const v = evalv(s.slice(1), pass); return v & 0xFF; }
    if (s[0] === '>') { const v = evalv(s.slice(1), pass); return (v >> 8) & 0xFF; }
    const m = s.match(/^(.+?)([+-])([^+-]+)$/);
    if (m && !/^\$?[0-9A-Fa-f]+$/.test(s)) { const a = evalv(m[1], pass), b = evalv(m[3], pass); return m[2] === '+' ? a + b : a - b; }
    if (s[0] === '$') return parseInt(s.slice(1), 16);
    if (/^\d+$/.test(s)) return parseInt(s, 10);
    if (s in labels) return labels[s];
    if (s in syms) return syms[s];
    if (pass === 1) return 0xFFFF;
    throw new Error('undefined symbol ' + s);
  };
  const isZpVal = (s) => { s = s.trim(); if (s[0] === '<' || s[0] === '>') return true; if (s[0] === '$') return s.length <= 3; if (/^\d+$/.test(s)) return +s < 256; const v = s in syms ? syms[s] : null; return v !== null && v < 256; };
  let out;
  for (const pass of [1, 2]) {
    let pc = org; out = [];
    for (const line of lines) {
      let l = line;
      const lm = l.match(/^([A-Za-z_][\w]*):\s*(.*)$/);
      if (lm) { if (pass === 1) { if (lm[1] in labels) throw new Error('dup label ' + lm[1]); labels[lm[1]] = pc; } l = lm[2]; if (!l) continue; }
      const [op, ...rest] = l.split(/\s+/); const arg = rest.join(' ').trim(); const OP = op.toUpperCase();
      if (OP === '.DB') { for (const v of arg.split(',')) { out.push(evalv(v, pass) & 0xFF); pc++; } continue; }
      if (OP === '.DW') { for (const v of arg.split(',')) { const w = evalv(v, pass); out.push(w & 0xFF, (w >> 8) & 0xFF); pc += 2; } continue; }
      const t = OPS[OP]; if (!t) throw new Error('bad op ' + op + ' in: ' + line);
      let mode, v = 0, m;
      if (!arg) mode = t.imp !== undefined ? 'imp' : 'acc';
      else if (/^A$/i.test(arg)) mode = 'acc';
      else if (arg[0] === '#') { mode = 'imm'; v = evalv(arg.slice(1), pass); }
      else if ((m = arg.match(/^\((.+)\),\s*Y$/i))) { mode = 'indy'; v = evalv(m[1], pass); }
      else if ((m = arg.match(/^\((.+),\s*X\)$/i))) { mode = 'indx'; v = evalv(m[1], pass); }
      else if ((m = arg.match(/^\((.+)\)$/))) { mode = 'ind'; v = evalv(m[1], pass); }
      else if ((m = arg.match(/^(.+),\s*([XY])$/i))) { const zp = isZpVal(m[1]); v = evalv(m[1], pass); const r = m[2].toLowerCase(); mode = (zp && t['zp' + r] !== undefined ? 'zp' : 'abs') + r; }
      else { v = evalv(arg, pass); if (t.rel !== undefined) mode = 'rel'; else mode = isZpVal(arg) && t.zp !== undefined ? 'zp' : 'abs'; }
      const code = t[mode]; if (code === undefined) throw new Error(`bad mode ${mode} for ${op} in: ${line}`);
      out.push(code); pc++;
      if (mode === 'rel') { const d = v - (pc + 1); if (pass === 2 && (d < -128 || d > 127)) throw new Error('branch out of range: ' + line); out.push(d & 0xFF); pc++; }
      else if (['imm', 'zp', 'zpx', 'zpy', 'indx', 'indy'].includes(mode)) { out.push(v & 0xFF); pc++; }
      else if (['abs', 'absx', 'absy', 'ind'].includes(mode)) { out.push(v & 0xFF, (v >> 8) & 0xFF); pc += 2; }
    }
  }
  return { bytes: Buffer.from(out), labels };
}
module.exports = { asm };
