// Build Vietnamese ROM
const fs = require('fs');
const path = require('path');
const { asm } = require('./asm6502');

const ROOT = path.join(__dirname, '..');
const BANK = 0x4000;
const off = (bank, addr) => 16 + bank * BANK + (addr & 0x3FFF);

class Rom {
  constructor(buf) { this.b = buf; }
  rd(bank, addr) { return this.b[off(bank, addr)]; }
  rd16(bank, addr) { return this.rd(bank, addr) | (this.rd(bank, addr + 1) << 8); }
  wr(bank, addr, bytes) { Buffer.from(bytes).copy(this.b, off(bank, addr)); }
  // assemble and write; checks optional end limit
  patch(bank, addr, src, syms = {}, limit) {
    const { bytes, labels } = asm(src, addr, syms);
    if (limit !== undefined && addr + bytes.length > limit) throw new Error(`patch at ${addr.toString(16)} overflows ${limit.toString(16)} by ${addr + bytes.length - limit}`);
    this.wr(bank, addr, bytes); return { len: bytes.length, labels, end: addr + bytes.length };
  }
  expect(bank, addr, hex) {
    const bytes = hex.split(/\s+/).map(h => parseInt(h, 16));
    bytes.forEach((v, i) => { if (this.rd(bank, addr + i) !== v) throw new Error(`expect failed at ${bank}:${(addr + i).toString(16)}`); });
  }
}

function expand(src) {
  const out = Buffer.alloc(16 + 32 * BANK, 0xFF);
  src.copy(out, 0, 0, 16 + 16 * BANK);
  out[4] = 0x20;
  return new Rom(out);
}
const copyBank = (rom, from, to) => rom.b.copy(rom.b, 16 + to * BANK, 16 + from * BANK, 16 + (from + 1) * BANK);

// Fixed bank free area allocator
const FREE_F = { start: 0xFF73, end: 0xFFDF };

function patchMapper(rom) {
  rom.expect(15, 0xC0B2, '8D F8 FF 4A');
  const r = rom.patch(15, FREE_F.start, `
  SETPRG:
    PHA
    AND #$10
    JSR $C08A     ; CHR0 bit4 = PRG A18 (SUROM)
    PLA
    AND #$0F
    STA $FFF8
    JMP $C0B5
  `, {}, FREE_F.end);
  FREE_F.start = r.end;
  rom.patch(15, 0xC0B2, `JMP ${r.labels.SETPRG}`);
}

const vn = require('./vn');
const menus = require('./menus');
const names = require('./names');
const nameEntry = require('./nameentry');
const fileScreen = require('./filescreen');
const { compileGroup } = require('./compile');

const TBANK = 0x10;           // char code -> (base, top) tables
const GROUP_A = [0x11, 0x12, 0x13, 0x14];
const GROUP_E = [0x15, 0x16, 0x17, 0x18];

function patchFont(rom, usedText) {
  const fo = off(5, 0x9280);
  const en = rom.b.slice(fo, fo + 0x1000);
  const codes = vn.init(Buffer.from(en), usedText);
  console.log('font: dropped', codes.dropped.join('') || '-', 'free codes', codes.freeLeft, 'free tiles', vn.tilesLeft);
  vn.fontBytes(en).copy(rom.b, fo);
  const base = Buffer.alloc(256, vn.SPACE), top = Buffer.alloc(256, vn.SPACE);
  codes.pair.forEach((p, i) => { if (p) { base[i] = p[0]; top[i] = p[1]; } });
  rom.wr(TBANK, 0x8000, base); rom.wr(TBANK, 0x8100, top);
}

function patchTextEngine(rom) {
  // NEWPUT replaces the dakuten routine at $DC5F-$DCCC
  rom.expect(15, 0xDC5F, '48 A5 E0 38 E5 4F');
  rom.patch(15, 0xDC5F, `
    PHA
    TXA
    PHA
    LDA $04
    PHA
    LDA #${TBANK}
    JSR $CD5C
    TSX
    LDA $0103,X
    TAX
    LDY $E7
    LDA $8000,X
    STA ($E0),Y
    LDA $8100,X
    PHA
    LDA $E0
    SEC
    SBC $4F
    STA $E0
    BCS n1
    DEC $E1
  n1:
    PLA
    STA ($E0),Y
    LDA $E0
    CLC
    ADC $4F
    STA $E0
    BCC n2
    INC $E1
  n2:
    PLA
    JSR $CD5C
    PLA
    TAX
    PLA
    RTS
  `, {}, 0xDCCD);
  // codes < $DF go through NEWPUT; $DF = player name (was $D3); $D3-$DE become char codes
  rom.expect(15, 0xDACC, 'C9 A0 B0 0E A4 E7 91 E0 20 98 E5'); rom.wr(15, 0xDACD, [0xDF]); rom.wr(15, 0xDAD0, [0x20, 0x5F, 0xDC, 0xEA, 0xEA, 0xEA, 0xEA]);
  rom.expect(15, 0xDADE, 'C9 D3'); rom.wr(15, 0xDADF, [0xDF]);
  rom.expect(15, 0xDCCD, '38 E9 D3 F0 29'); rom.wr(15, 0xDCCF, [0xDF]);
  rom.expect(15, 0xDD1E, 'C9 A0 B0 0D 84 EC A4 E7 91 E0'); rom.wr(15, 0xDD1F, [0xDF]); rom.wr(15, 0xDD24, [0x20, 0x5F, 0xDC, 0xEA]);
  rom.expect(15, 0xDE6A, 'C9 A0 B0 0D 84 EC A4 E7 91 E0'); rom.wr(15, 0xDE6B, [0xDF]); rom.wr(15, 0xDE70, [0x20, 0x5F, 0xDC, 0xEA]);

  // menu renderer at $ED38: codes < $D3 -> (base, top) via TBANK tables; blank tops are not written
  rom.expect(15, 0xED38, 'C9 A0 90 24');
  rom.patch(15, 0xED38, `
    PHA
    LDA $04
    PHA
    LDA #${TBANK}
    JSR $CD5C
    TSX
    LDA $0102,X
    TAX
    LDA $8100,X
    PHA
    LDA $8000,X
    LDX $02D3
    STA $0200,X
    TXA
    SEC
    SBC $02CE
    TAX
    PLA
    BCC nt
    CMP #$20
    BEQ nt
    STA $0200,X
  nt:
    PLA
    JSR $CD5C
    PLA
    LDX $02D3
    INX
    STX $02D3
    RTS
  `, {}, 0xEDCC);
  // F2 absolute jump
  rom.expect(15, 0xE0A7, 'A0 01 B1 70');
  rom.patch(15, 0xE0A7, `
    LDY #$01
    LDA ($70),Y
    TAX
    INY
    LDA ($70),Y
    STA $71
    STX $70
    LDA #$00
    STA $E3
    RTS
  `, {}, 0xE0C8);
  // F3 yes/no absolute: Y = 1 + 2*$E9
  rom.expect(15, 0xE186, 'A5 E9 A8 C8 B1 70');
  rom.patch(15, 0xE186, `
    LDA $E9
    ASL A
    TAY
    INY
    LDA ($70),Y
    TAX
    INY
    LDA ($70),Y
    STA $71
    STX $70
    JMP $E1A4
  `, {}, 0xE1A4);
  // F4 flag test absolute: F4 flag tlo thi flo fhi
  rom.expect(15, 0xE242, 'A0 02 B1 70');
  rom.patch(15, 0xE242, `
    LDY #$02
    BNE f4a
    NOP
    NOP
    NOP
    LDY #$04
  f4a:
    LDA ($70),Y
    TAX
    INY
    LDA ($70),Y
    STA $71
    STX $70
    LDA #$00
    STA $E3
    RTS
  `, {}, 0xE26A);
  // pointer copy with bank offset in bits 7-6 of high byte
  rom.expect(15, 0xD8CA, 'A0 00 B1 E0 99 70 00');
  const r = rom.patch(15, FREE_F.start, `
  PTRCOPY:
    LDY #$00
    LDA ($E0),Y
    STA $70
    INY
    LDA ($E0),Y
    PHA
    AND #$3F
    ORA #$80
    STA $71
    PLA
    ROL A
    ROL A
    ROL A
    AND #$03
    CLC
    ADC $05
    STA $05
    JMP $CD5C
  `, {}, FREE_F.end);
  FREE_F.start = r.end;
  rom.patch(15, 0xD8CA, `JMP ${r.labels.PTRCOPY}`);
  rom.expect(15, 0xD87E, 'A9 02'); rom.wr(15, 0xD87F, [GROUP_A[0]]);
  rom.expect(15, 0xD8D8, 'A9 03'); rom.wr(15, 0xD8D9, [GROUP_E[0]]);
  // gold-gain routine (D97C) also restores the script bank
  rom.expect(15, 0xD984, 'A9 02 85 05'); rom.wr(15, 0xD985, [GROUP_A[0]]);
}

function patchYesNo(rom) {
  const T = vn.T, S = vn.SPACE;
  const co = [T.C, T['ó1']], khong = [T.K, T.h, T['ô1'], T.n, T.g];
  rom.wr(15, 0xE1FE, [0x16, ...co, S, S, ...khong]);
  rom.wr(15, 0xE208, [S, ...co, S, 0x16, ...khong]);
}

function patchScript(rom, srcA, srcE) {
  const a = compileGroup(srcA, GROUP_A, 'A');
  a.mem.forEach((m, i) => rom.wr(GROUP_A[i], 0x8000, m));
  const e = compileGroup(srcE, GROUP_E, 'E');
  // counts header from original bank 3
  const counts = [0, 1, 2, 3, 4].map(i => rom.rd(3, 0x8000 + i));
  e.mem[0].set(counts, 0);
  e.mem.forEach((m, i) => rom.wr(GROUP_E[i], 0x8000, m));
  console.log('script A used', a.used.map(u => u.toString(16)).join(' '), ' E used', e.used.map(u => u.toString(16)).join(' '));
}

function build(opts = {}) {
  const base = fs.readFileSync(path.join(ROOT, 'work/en.nes'));
  const rom = expand(base);
  patchMapper(rom);
  const sd = opts.srcDir || path.join(ROOT, 'script');
  const readGroup = g => fs.readdirSync(sd).filter(f => f.startsWith(g + '_') && f.endsWith('.txt')).sort().map(f => fs.readFileSync(path.join(sd, f), 'utf8')).join('\n');
  const srcA = readGroup('A'), srcE = readGroup('E');
  patchFont(rom, srcA + srcE + menus.TEXTS + names.TEXTS + nameEntry.TEXTS + fileScreen.TEXTS);
  patchTextEngine(rom);
  patchYesNo(rom);
  menus.patchMenus(rom);
  names.patchNames(rom);
  nameEntry.patchNameEntry(rom);
  fileScreen.patchTitle(rom);
  fileScreen.patchFileScreen(rom);
  patchScript(rom, srcA, srcE);
  copyBank(rom, 14, 30); copyBank(rom, 15, 31);
  return rom;
}

module.exports = { build, Rom, off };
if (require.main === module) {
  const sdi = process.argv.indexOf('--src');
  const rom = build({ srcDir: sdi > 0 ? process.argv[sdi + 1] : undefined });
  const outp = process.argv[2] && !process.argv[2].startsWith('-') ? process.argv[2] : path.join(ROOT, 'work/vn.nes');
  fs.writeFileSync(outp, rom.b);
  console.log('wrote', outp, rom.b.length);
}
