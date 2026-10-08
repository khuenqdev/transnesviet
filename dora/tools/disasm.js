// 6502 disassembler. usage: node disasm.js rom bank addrHex lenHex
const fs = require('fs');
const OPS = {};
const def = (s) => s.trim().split(/\s*;\s*/).forEach(e => { const [op, m, c] = e.split(/\s+/); OPS[parseInt(c, 16)] = [op, m]; });
def(`ADC imm 69;ADC zp 65;ADC zpx 75;ADC abs 6D;ADC abx 7D;ADC aby 79;ADC izx 61;ADC izy 71;
AND imm 29;AND zp 25;AND zpx 35;AND abs 2D;AND abx 3D;AND aby 39;AND izx 21;AND izy 31;
ASL acc 0A;ASL zp 06;ASL zpx 16;ASL abs 0E;ASL abx 1E;BCC rel 90;BCS rel B0;BEQ rel F0;BIT zp 24;BIT abs 2C;
BMI rel 30;BNE rel D0;BPL rel 10;BRK imp 00;BVC rel 50;BVS rel 70;CLC imp 18;CLD imp D8;CLI imp 58;CLV imp B8;
CMP imm C9;CMP zp C5;CMP zpx D5;CMP abs CD;CMP abx DD;CMP aby D9;CMP izx C1;CMP izy D1;
CPX imm E0;CPX zp E4;CPX abs EC;CPY imm C0;CPY zp C4;CPY abs CC;DEC zp C6;DEC zpx D6;DEC abs CE;DEC abx DE;
DEX imp CA;DEY imp 88;EOR imm 49;EOR zp 45;EOR zpx 55;EOR abs 4D;EOR abx 5D;EOR aby 59;EOR izx 41;EOR izy 51;
INC zp E6;INC zpx F6;INC abs EE;INC abx FE;INX imp E8;INY imp C8;JMP abs 4C;JMP ind 6C;JSR abs 20;
LDA imm A9;LDA zp A5;LDA zpx B5;LDA abs AD;LDA abx BD;LDA aby B9;LDA izx A1;LDA izy B1;
LDX imm A2;LDX zp A6;LDX zpy B6;LDX abs AE;LDX aby BE;LDY imm A0;LDY zp A4;LDY zpx B4;LDY abs AC;LDY abx BC;
LSR acc 4A;LSR zp 46;LSR zpx 56;LSR abs 4E;LSR abx 5E;NOP imp EA;ORA imm 09;ORA zp 05;ORA zpx 15;ORA abs 0D;ORA abx 1D;ORA aby 19;ORA izx 01;ORA izy 11;
PHA imp 48;PHP imp 08;PLA imp 68;PLP imp 28;ROL acc 2A;ROL zp 26;ROL zpx 36;ROL abs 2E;ROL abx 3E;ROR acc 6A;ROR zp 66;ROR zpx 76;ROR abs 6E;ROR abx 7E;
RTI imp 40;RTS imp 60;SBC imm E9;SBC zp E5;SBC zpx F5;SBC abs ED;SBC abx FD;SBC aby F9;SBC izx E1;SBC izy F1;
SEC imp 38;SED imp F8;SEI imp 78;STA zp 85;STA zpx 95;STA abs 8D;STA abx 9D;STA aby 99;STA izx 81;STA izy 91;
STX zp 86;STX zpy 96;STX abs 8E;STY zp 84;STY zpx 94;STY abs 8C;TAX imp AA;TAY imp A8;TSX imp BA;TXA imp 8A;TXS imp 9A;TYA imp 98`);
const LEN = { imp: 1, acc: 1, imm: 2, zp: 2, zpx: 2, zpy: 2, izx: 2, izy: 2, rel: 2, abs: 3, abx: 3, aby: 3, ind: 3 };
const h2 = v => v.toString(16).toUpperCase().padStart(2, '0'), h4 = v => v.toString(16).toUpperCase().padStart(4, '0');

function disasm(mem, org, start, len) {
  const out = []; let pc = start;
  while (pc < start + len) {
    const i = pc - org; const b = mem[i]; const o = OPS[b];
    if (!o) { out.push(`${h4(pc)}: ${h2(b)}        .db $${h2(b)}`); pc++; continue; }
    const [op, m] = o; const n = LEN[m]; const bytes = [...mem.slice(i, i + n)].map(h2).join(' ').padEnd(9);
    const v8 = mem[i + 1], v16 = mem[i + 1] | (mem[i + 2] << 8);
    let a = '';
    switch (m) {
      case 'imm': a = `#$${h2(v8)}`; break; case 'zp': a = `$${h2(v8)}`; break;
      case 'zpx': a = `$${h2(v8)},X`; break; case 'zpy': a = `$${h2(v8)},Y`; break;
      case 'izx': a = `($${h2(v8)},X)`; break; case 'izy': a = `($${h2(v8)}),Y`; break;
      case 'rel': a = `$${h4((pc + 2 + (v8 < 128 ? v8 : v8 - 256)) & 0xFFFF)}`; break;
      case 'abs': a = `$${h4(v16)}`; break; case 'abx': a = `$${h4(v16)},X`; break; case 'aby': a = `$${h4(v16)},Y`; break;
      case 'ind': a = `($${h4(v16)})`; break; case 'acc': a = 'A'; break;
    }
    out.push(`${h4(pc)}: ${bytes} ${op} ${a}`);
    pc += n;
  }
  return out.join('\n');
}
module.exports = { disasm };

if (require.main === module) {
  const rom = fs.readFileSync(process.argv[2]);
  const bank = parseInt(process.argv[3], 16); const addr = parseInt(process.argv[4], 16); const len = parseInt(process.argv[5] || '100', 16);
  const org = addr >= 0xC000 ? 0xC000 : 0x8000;
  const mem = rom.slice(16 + bank * 0x4000, 16 + bank * 0x4000 + 0x4000);
  console.log(disasm(mem, org, addr, len));
}
