// Character tables for decoding JP / EN text
const JP = {};
const put = (start, s) => { [...s].forEach((c, i) => { JP[start + i] = c; }); };
put(0x00, '0123456789だー!ど・?太夫ドびジず');
put(0x20, ' あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんア');
put(0x50, 'イウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンゃゅょ');
put(0x80, 'ぁぃぅぇぉっ◆ャュョァィゥェォッ');
put(0x93, '…、「」');
put(0xA0, 'がぎぐげござじずぜぞだぢづでどばびぶべぼガギグゲゴザジズゼゾダヂヅデドバビブベボヴぱぴぷぺぽパピプペポ');
put(0xE0, '©ABCDEFGHIJKLMNOPQRSTUVWXYZ,');

const EN = {};
for (let i = 0; i < 10; i++) EN[i] = String(i);
EN[0x0B] = '-'; EN[0x0C] = '!'; EN[0x0F] = '?'; EN[0x20] = ' ';
for (let i = 0; i < 26; i++) { EN[0x21 + i] = String.fromCharCode(65 + i); EN[0x3B + i] = String.fromCharCode(97 + i); }
Object.assign(EN, { 0x0E: 'il', 0x10: 'le', 0x12: 'li', 0x13: 'll', 0x57: 'i', 0x58: 'ng', 0x68: '.', 0x69: '!', 0x70: "'", 0x7D: "'", 0x93: '.', 0x94: ',', 0x96: '!' });

function decode(bytes, table, ctl = true) {
  let s = '';
  for (const b of bytes) {
    if (ctl && b === 0xF0) s += '\n';
    else if (table[b] !== undefined) s += table[b];
    else s += `[${b.toString(16).padStart(2, '0')}]`;
  }
  return s;
}
module.exports = { JP, EN, decode };
