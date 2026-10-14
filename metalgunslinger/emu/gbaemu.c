/* gbaemu.c - minimal headless Game Boy Advance emulator (Metal Gunslinger VI translation QA).
 * ARM7TDMI interpreter (ARM+Thumb), HLE BIOS (SWI) + IRQ-dispatch stub, PPU (modes 0-5,
 * affine BGs, sprites, windows, blending), DMA, timers, keypad, EEPROM, save states.
 * build: gcc -O2 -o gbaemu gbaemu.c -lm
 * usage: gbaemu rom.gba script.txt   (script: run N | press KEYS N | hold KEYS|NONE | shot f.ppm |
 *   save f | load f | poke8/16/32 a v | dump a len f | trace on|off | regs | eesave f | eeload f) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef int32_t s32; typedef int16_t s16; typedef int8_t s8; typedef uint64_t u64; typedef int64_t s64;
static u8 *rom; static u32 romsize; static u8 bios[0x4000];
typedef struct {
  u32 r[16]; u32 cpsr; u32 spsr; u32 bank_usr[7], bank_fiq[7], bank_irq[2], bank_svc[2], bank_abt[2], bank_und[2];
  u32 spsr_fiq, spsr_irq, spsr_svc, spsr_abt, spsr_und; int halted, intrwait;
  u8 ewram[0x40000], iwram[0x8000], io[0x400], pal[0x400], vram[0x18000], oam[0x400];
  u32 frame; int line; u16 tm_reload[4]; u32 tm_counter[4], tm_sub[4];
  u32 dma_src[4], dma_dst[4], dma_cnt[4]; s32 bgx[2], bgy[2]; u16 keys;
  u8 eeprom[0x2000]; int ee_state; u32 ee_addr; int ee_bits; u64 ee_buf; int ee_readpos; u8 ee_rbits[68]; int ee_size_bits;
} GBA;
static GBA g; static u16 fb[240*160]; static int trace=0; static u32 cur_pc;
#define CPSR_T (1u<<5)
#define CPSR_I (1u<<7)
#define FLAG_N (1u<<31)
#define FLAG_Z (1u<<30)
#define FLAG_C (1u<<29)
#define FLAG_V (1u<<28)
#define IO16(a) (*(u16*)&g.io[(a)])
#define IO32(a) (*(u32*)&g.io[(a)])
static void bank_save(int m){ switch(m){case 0x10:case 0x1F: memcpy(g.bank_usr,&g.r[8],28); break; case 0x11: memcpy(g.bank_fiq,&g.r[8],28); g.spsr_fiq=g.spsr; break;
  default: memcpy(g.bank_usr,&g.r[8],20);
   if(m==0x12){g.bank_irq[0]=g.r[13];g.bank_irq[1]=g.r[14];g.spsr_irq=g.spsr;} if(m==0x13){g.bank_svc[0]=g.r[13];g.bank_svc[1]=g.r[14];g.spsr_svc=g.spsr;}
   if(m==0x17){g.bank_abt[0]=g.r[13];g.bank_abt[1]=g.r[14];g.spsr_abt=g.spsr;} if(m==0x1B){g.bank_und[0]=g.r[13];g.bank_und[1]=g.r[14];g.spsr_und=g.spsr;} } }
static void bank_load(int m){ switch(m){case 0x10:case 0x1F: memcpy(&g.r[8],g.bank_usr,28); break; case 0x11: memcpy(&g.r[8],g.bank_fiq,28); g.spsr=g.spsr_fiq; break;
  default: memcpy(&g.r[8],g.bank_usr,20);
   if(m==0x12){g.r[13]=g.bank_irq[0];g.r[14]=g.bank_irq[1];g.spsr=g.spsr_irq;} if(m==0x13){g.r[13]=g.bank_svc[0];g.r[14]=g.bank_svc[1];g.spsr=g.spsr_svc;}
   if(m==0x17){g.r[13]=g.bank_abt[0];g.r[14]=g.bank_abt[1];g.spsr=g.spsr_abt;} if(m==0x1B){g.r[13]=g.bank_und[0];g.r[14]=g.bank_und[1];g.spsr=g.spsr_und;} } }
static void set_cpsr(u32 v){ int om=g.cpsr&0x1F,nm=v&0x1F; if(om!=nm){bank_save(om); g.cpsr=v; bank_load(nm);} else g.cpsr=v; }
static void io_write8(u32 a,u8 v); static void io_write16(u32 a,u16 v); static u16 io_read16(u32 a); static u32 ee_read(void); static void ee_write(u32 v);
static u8 rd8(u32 a){ switch(a>>24){ case 0: return a<0x4000?bios[a]:0; case 2: return g.ewram[a&0x3FFFF]; case 3: return g.iwram[a&0x7FFF];
  case 4: { if(a-0x04000000>=0x400) return 0; u16 v=io_read16((a&0x3FF)&~1); return (a&1)?v>>8:v&0xFF; }
  case 5: return g.pal[a&0x3FF]; case 6: { u32 o=a&0x1FFFF; if(o>=0x18000) o-=0x8000; return g.vram[o]; } case 7: return g.oam[a&0x3FF];
  case 8: case 9: case 0xA: case 0xB: case 0xC: { u32 o=a&0x1FFFFFF; return o<romsize?rom[o]:0; }
  case 0xD: return ee_read()&1; case 0xE: case 0xF: return 0xFF; } return 0; }
static u16 rd16(u32 a){ a&=~1; switch(a>>24){ case 2: return *(u16*)&g.ewram[a&0x3FFFF]; case 3: return *(u16*)&g.iwram[a&0x7FFF];
  case 4: if(a-0x04000000>=0x400) return 0; return io_read16(a&0x3FF); case 5: return *(u16*)&g.pal[a&0x3FF];
  case 6: { u32 o=a&0x1FFFF; if(o>=0x18000) o-=0x8000; return *(u16*)&g.vram[o]; } case 7: return *(u16*)&g.oam[a&0x3FF];
  case 8: case 9: case 0xA: case 0xB: case 0xC: { u32 o=a&0x1FFFFFF; return o+1<romsize?*(u16*)&rom[o]:0; }
  case 0xD: return ee_read(); default: return rd8(a)|(rd8(a+1)<<8); } }
static u32 rd32(u32 a){ a&=~3; switch(a>>24){ case 2: return *(u32*)&g.ewram[a&0x3FFFF]; case 3: return *(u32*)&g.iwram[a&0x7FFF];
  case 8: case 9: case 0xA: case 0xB: case 0xC: { u32 o=a&0x1FFFFFF; return o+3<romsize?*(u32*)&rom[o]:0; } default: return rd16(a)|((u32)rd16(a+2)<<16); } }
static void wr8(u32 a,u8 v){ switch(a>>24){ case 2: g.ewram[a&0x3FFFF]=v; break; case 3: g.iwram[a&0x7FFF]=v; break;
  case 4: if(a-0x04000000<0x400) io_write8(a&0x3FF,v); break; case 5: { u32 o=a&0x3FE; g.pal[o]=v; g.pal[o+1]=v; } break;
  case 6: { u32 o=a&0x1FFFF; if(o>=0x18000) o-=0x8000; if(o<0x10000){ o&=~1; g.vram[o]=v; g.vram[o+1]=v; } } break; } }
static void wr16(u32 a,u16 v){ a&=~1; switch(a>>24){ case 2: *(u16*)&g.ewram[a&0x3FFFF]=v; break; case 3: *(u16*)&g.iwram[a&0x7FFF]=v; break;
  case 4: if(a-0x04000000<0x400) io_write16(a&0x3FF,v); break; case 5: *(u16*)&g.pal[a&0x3FF]=v; break;
  case 6: { u32 o=a&0x1FFFF; if(o>=0x18000) o-=0x8000; *(u16*)&g.vram[o]=v; } break; case 7: *(u16*)&g.oam[a&0x3FF]=v; break; case 0xD: ee_write(v); break; } }
static void wr32(u32 a,u32 v){ a&=~3; switch(a>>24){ case 2: *(u32*)&g.ewram[a&0x3FFFF]=v; break; case 3: *(u32*)&g.iwram[a&0x7FFF]=v; break; default: wr16(a,v); wr16(a+2,v>>16); } }
static void ee_write(u32 v){ int bit=v&1;
  if(g.ee_state==0){ g.ee_buf=0; g.ee_bits=0; g.ee_state=1; }
  if(g.ee_state==1){ g.ee_buf=(g.ee_buf<<1)|bit; g.ee_bits++; int ab=g.ee_size_bits?g.ee_size_bits:14;
    if(g.ee_bits==2+ab){ int cmd=(g.ee_buf>>ab)&3; u32 ad=g.ee_buf&((1u<<ab)-1);
      if(cmd==3){ g.ee_addr=(ad&0x3FF)*8; g.ee_state=2; } else if(cmd==2){ g.ee_addr=(ad&0x3FF)*8; g.ee_state=3; g.ee_bits=0; g.ee_buf=0; } } return; }
  if(g.ee_state==2){ g.ee_state=4; g.ee_readpos=0; for(int i=0;i<4;i++) g.ee_rbits[i]=0;
    for(int i=0;i<64;i++){ u8 b=g.eeprom[(g.ee_addr+i/8)&0x1FFF]; g.ee_rbits[4+i]=(b>>(7-(i&7)))&1; } return; }
  if(g.ee_state==3){ g.ee_buf=(g.ee_buf<<1)|bit; g.ee_bits++; if(g.ee_bits==64){ for(int i=0;i<8;i++) g.eeprom[(g.ee_addr+i)&0x1FFF]=(g.ee_buf>>(56-8*i))&0xFF; g.ee_state=5; } return; }
  if(g.ee_state==5){ g.ee_state=0; return; } }
static u32 ee_read(void){ if(g.ee_state==4){ u32 b=g.ee_rbits[g.ee_readpos++]; if(g.ee_readpos>=68) g.ee_state=0; return b; } return 1; }
static void dma_run(int ch){ u32 base=0xB0+ch*12; u16 ctl=IO16(base+10); u32 cnt=g.dma_cnt[ch]; if(!cnt) cnt=(ch==3)?0x10000:0x4000;
  int w32=ctl&(1<<10), dc=(ctl>>5)&3, sc=(ctl>>7)&3, st=w32?4:2; u32 s=g.dma_src[ch], d=g.dma_dst[ch];
  if((d>>24)==0xD && ch==3 && !g.ee_size_bits){ if(cnt==9||cnt==73) g.ee_size_bits=6; else if(cnt==17||cnt==81) g.ee_size_bits=14; }
  if((s>>24)==0xD && ch==3 && !g.ee_size_bits) g.ee_size_bits=14;
  if(trace && (d>>24)>=5 && (d>>24)<=7) fprintf(stderr,"[f%u] DMA%d %08X -> %08X n=%u %s pc=%08X\n",g.frame,ch,s,d,cnt,w32?"w32":"w16",cur_pc);
  for(u32 i=0;i<cnt;i++){ if(w32) wr32(d,rd32(s)); else wr16(d,rd16(s)); if(dc==0||dc==3) d+=st; else if(dc==1) d-=st; if(sc==0) s+=st; else if(sc==1) s-=st; }
  g.dma_src[ch]=s; g.dma_dst[ch]=(dc!=3)?d:IO32(base+4);
  if(ctl&(1<<14)) IO16(0x202)|=(1<<(8+ch));
  if(!(ctl&(1<<9)) || ((ctl>>12)&3)==0) IO16(base+10)&=~0x8000; else g.dma_cnt[ch]=IO16(base+8); }
static void dma_trigger(int t){ for(int ch=0;ch<4;ch++){ u16 c=IO16(0xB0+ch*12+10); if((c&0x8000)&&((c>>12)&3)==t) dma_run(ch); } }
static u16 io_read16(u32 a){ switch(a){ case 0x130: return (~g.keys)&0x3FF; case 0x100: case 0x104: case 0x108: case 0x10C: return g.tm_counter[(a-0x100)/4]; case 0x006: return g.line; } return IO16(a); }
static void io_write16(u32 a,u16 v){ switch(a){
  case 0x004: IO16(a)=(IO16(a)&7)|(v&~7); return; case 0x006: return; case 0x202: IO16(a)&=~v; return;
  case 0x028: case 0x02A: case 0x02C: case 0x02E: case 0x038: case 0x03A: case 0x03C: case 0x03E:
    IO16(a)=v; { int i=(a>=0x38); int isy=((a&4)!=0); s32 val=(s32)(IO32(a&~2)<<4)>>4; if(isy) g.bgy[i]=val; else g.bgx[i]=val; } return;
  case 0x100: case 0x104: case 0x108: case 0x10C: g.tm_reload[(a-0x100)/4]=v; return;
  case 0x102: case 0x106: case 0x10A: case 0x10E: { int t=(a-0x102)/4; u16 o=IO16(a); IO16(a)=v; if(!(o&0x80)&&(v&0x80)){ g.tm_counter[t]=g.tm_reload[t]; g.tm_sub[t]=0; } return; }
  case 0x0BA: case 0x0C6: case 0x0D2: case 0x0DE: { int ch=(a-0xBA)/12; u16 o=IO16(a); IO16(a)=v;
    if(!(o&0x8000)&&(v&0x8000)){ u32 b=0xB0+ch*12; g.dma_src[ch]=IO32(b); g.dma_dst[ch]=IO32(b+4); g.dma_cnt[ch]=IO16(b+8); if(((v>>12)&3)==0) dma_run(ch); } return; }
  case 0x300: IO16(a)=v; if(v&0x8000) g.halted=1; return; }
  IO16(a)=v; }
static void io_write8(u32 a,u8 v){ if(a==0x301){ g.halted=1; return; } if(a==0x202||a==0x203){ g.io[a]&=~v; return; }
  u16 c=IO16(a&~1); io_write16(a&~1,(a&1)?((c&0xFF)|(v<<8)):((c&0xFF00)|v)); }
static void swi(int n); static int branched;
static inline void setpc(u32 v){ g.r[15]=v; branched=1; }
static inline int cond_ok(u32 c){ u32 f=g.cpsr; int N=!!(f&FLAG_N),Z=!!(f&FLAG_Z),C=!!(f&FLAG_C),V=!!(f&FLAG_V);
  switch(c){case 0:return Z;case 1:return !Z;case 2:return C;case 3:return !C;case 4:return N;case 5:return !N;case 6:return V;case 7:return !V;
  case 8:return C&&!Z;case 9:return !C||Z;case 10:return N==V;case 11:return N!=V;case 12:return !Z&&N==V;case 13:return Z||N!=V;case 14:return 1;} return 0; }
static inline void setNZ(u32 r){ g.cpsr=(g.cpsr&~(FLAG_N|FLAG_Z))|(r&FLAG_N)|(r?0:FLAG_Z); }
static inline void setC(int c){ if(c) g.cpsr|=FLAG_C; else g.cpsr&=~FLAG_C; }
static inline void setV(int v){ if(v) g.cpsr|=FLAG_V; else g.cpsr&=~FLAG_V; }
static inline u32 add_f(u32 a,u32 b,u32 c,int s){ u64 r=(u64)a+b+c; u32 res=(u32)r; if(s){setNZ(res);setC(r>>32);setV(((a^res)&(b^res))>>31);} return res; }
static inline u32 sub_f(u32 a,u32 b,u32 c,int s){ u64 r=(u64)a+(u64)(~b)+c; u32 res=(u32)r; if(s){setNZ(res);setC(r>>32);setV(((a^b)&(a^res))>>31);} return res; }
static u32 shift(u32 v,int type,u32 amt,int *carry,int imm){ int c=*carry;
  switch(type){
  case 0: if(amt==0){} else if(amt<32){c=(v>>(32-amt))&1; v<<=amt;} else if(amt==32){c=v&1; v=0;} else {c=0;v=0;} break;
  case 1: if(imm&&amt==0) amt=32; if(amt==0){} else if(amt<32){c=(v>>(amt-1))&1; v>>=amt;} else if(amt==32){c=v>>31; v=0;} else {c=0;v=0;} break;
  case 2: if(imm&&amt==0) amt=32; if(amt==0){} else if(amt<32){c=((s32)v>>(amt-1))&1; v=(s32)v>>amt;} else {c=v>>31; v=(s32)v>>31;} break;
  case 3: if(imm&&amt==0){ c=v&1; v=(v>>1)|((g.cpsr&FLAG_C)?0x80000000:0);} else if(amt==0){} else { amt&=31; if(amt==0){c=v>>31;} else {c=(v>>(amt-1))&1; v=(v>>amt)|(v<<(32-amt));} } break; }
  *carry=c; return v; }
static u32 ldr_rot(u32 a){ u32 v=rd32(a); int r=(a&3)*8; return r?(v>>r)|(v<<(32-r)):v; }
static void arm_exec(u32 op){
  if(!cond_ok(op>>28)) return;
  if((op&0x0FFFFFF0)==0x012FFF10){ u32 v=g.r[op&15]; if(v&1){ g.cpsr|=CPSR_T; setpc(v&~1);} else { g.cpsr&=~CPSR_T; setpc(v&~3);} return; }
  if((op&0x0FC000F0)==0x00000090){ int rd=(op>>16)&15,rn=(op>>12)&15,rs=(op>>8)&15,rm=op&15; u32 r=g.r[rm]*g.r[rs]; if(op&(1<<21)) r+=g.r[rn]; g.r[rd]=r; if(op&(1<<20)) setNZ(r); return; }
  if((op&0x0F8000F0)==0x00800090){ int hi=(op>>16)&15,lo=(op>>12)&15,rs=(op>>8)&15,rm=op&15; u64 r;
    if(op&(1<<22)) r=(u64)((s64)(s32)g.r[rm]*(s64)(s32)g.r[rs]); else r=(u64)g.r[rm]*(u64)g.r[rs];
    if(op&(1<<21)) r+=((u64)g.r[hi]<<32)|g.r[lo]; g.r[lo]=(u32)r; g.r[hi]=r>>32;
    if(op&(1<<20)){ g.cpsr=(g.cpsr&~(FLAG_N|FLAG_Z))|((r>>32)&FLAG_N)|(r?0:FLAG_Z);} return; }
  if((op&0x0FB00FF0)==0x01000090){ int rn=(op>>16)&15,rd=(op>>12)&15,rm=op&15; u32 a=g.r[rn];
    if(op&(1<<22)){ u8 t=rd8(a); wr8(a,g.r[rm]); g.r[rd]=t; } else { u32 t=ldr_rot(a); wr32(a,g.r[rm]); g.r[rd]=t; } return; }
  if((op&0x0E000090)==0x00000090 && (op&0x60)){
    int P=op>>24&1,U=op>>23&1,I=op>>22&1,W=op>>21&1,L=op>>20&1,rn=op>>16&15,rd=op>>12&15,sh=(op>>5)&3;
    u32 off=I?(((op>>4)&0xF0)|(op&15)):g.r[op&15]; u32 base=g.r[rn]; u32 addr=P?(U?base+off:base-off):base;
    if(L){ u32 v; if(sh==1){ v=rd16(addr); if(addr&1) v=(v>>8)|(v<<24); } else if(sh==2) v=(s32)(s8)rd8(addr); else { if(addr&1) v=(s32)(s8)rd8(addr); else v=(s32)(s16)rd16(addr); }
      if(!P) g.r[rn]=U?base+off:base-off; else if(W) g.r[rn]=addr; if(rd==15) setpc(v&~3); else g.r[rd]=v; }
    else { u32 v=g.r[rd]; if(rd==15) v+=4; wr16(addr,v); if(!P) g.r[rn]=U?base+off:base-off; else if(W) g.r[rn]=addr; }
    return; }
  if((op&0x0FBF0FFF)==0x010F0000){ g.r[(op>>12)&15]=(op&(1<<22))?g.spsr:g.cpsr; return; }
  if((op&0x0DB0F000)==0x0120F000){ u32 v; if(op&(1<<25)){ u32 imm=op&0xFF; int rot=((op>>8)&15)*2; v=rot?(imm>>rot)|(imm<<(32-rot)):imm; } else v=g.r[op&15];
    u32 mask=0; if(op&(1<<19)) mask|=0xFF000000; if(op&(1<<16)) mask|=0xFF; if(op&(1<<17)) mask|=0xFF00; if(op&(1<<18)) mask|=0xFF0000;
    if(op&(1<<22)) g.spsr=(g.spsr&~mask)|(v&mask); else { if((g.cpsr&0x1F)==0x10) mask&=0xFF000000; set_cpsr((g.cpsr&~mask)|(v&mask)); } return; }
  switch((op>>25)&7){
  case 0: case 1: { int opc=(op>>21)&15,S=(op>>20)&1,rn=(op>>16)&15,rd=(op>>12)&15; int carry=!!(g.cpsr&FLAG_C); u32 op2;
    if(op&(1<<25)){ u32 imm=op&0xFF; int rot=((op>>8)&15)*2; if(rot){ op2=(imm>>rot)|(imm<<(32-rot)); carry=op2>>31; } else op2=imm; }
    else { int type=(op>>5)&3; u32 rmv=g.r[op&15]; if(op&0x10){ if((op&15)==15) rmv+=4; op2=shift(rmv,type,g.r[(op>>8)&15]&0xFF,&carry,0); } else op2=shift(rmv,type,(op>>7)&31,&carry,1); }
    u32 a=g.r[rn]; if(rn==15 && !(op&(1<<25)) && (op&0x10)) a+=4; u32 res=0; int logic=0, wr=1;
    switch(opc){ case 0: res=a&op2; logic=1; break; case 1: res=a^op2; logic=1; break; case 2: res=sub_f(a,op2,1,S); break; case 3: res=sub_f(op2,a,1,S); break;
    case 4: res=add_f(a,op2,0,S); break; case 5: res=add_f(a,op2,!!(g.cpsr&FLAG_C),S); break; case 6: res=sub_f(a,op2,!!(g.cpsr&FLAG_C),S); break; case 7: res=sub_f(op2,a,!!(g.cpsr&FLAG_C),S); break;
    case 8: res=a&op2; logic=1; wr=0; break; case 9: res=a^op2; logic=1; wr=0; break; case 10: sub_f(a,op2,1,1); wr=0; break; case 11: add_f(a,op2,0,1); wr=0; break;
    case 12: res=a|op2; logic=1; break; case 13: res=op2; logic=1; break; case 14: res=a&~op2; logic=1; break; case 15: res=~op2; logic=1; break; }
    if(S && logic){ setNZ(res); setC(carry); }
    if(wr){ if(rd==15){ if(S) set_cpsr(g.spsr); setpc(res&((g.cpsr&CPSR_T)?~1u:~3u)); } else g.r[rd]=res; }
    return; }
  case 2: case 3: { int I=op>>25&1,P=op>>24&1,U=op>>23&1,B=op>>22&1,W=op>>21&1,L=op>>20&1,rn=op>>16&15,rd=op>>12&15; u32 off;
    if(I){ int c=!!(g.cpsr&FLAG_C); off=shift(g.r[op&15],(op>>5)&3,(op>>7)&31,&c,1); } else off=op&0xFFF;
    u32 base=g.r[rn]; u32 addr=P?(U?base+off:base-off):base;
    if(L){ u32 v=B?rd8(addr):ldr_rot(addr); if(!P) g.r[rn]=U?base+off:base-off; else if(W) g.r[rn]=addr; if(rd==15) setpc(v&~3); else g.r[rd]=v; }
    else { u32 v=g.r[rd]; if(rd==15) v+=4; if(B) wr8(addr,v); else wr32(addr,v); if(!P) g.r[rn]=U?base+off:base-off; else if(W) g.r[rn]=addr; }
    return; }
  case 4: { int P=op>>24&1,U=op>>23&1,S=op>>22&1,W=op>>21&1,L=op>>20&1,rn=op>>16&15; u16 list=op&0xFFFF; int n=__builtin_popcount(list); u32 base=g.r[rn], addr;
    if(!list){ list=0x8000; n=16; } if(U) addr=base+(P?4:0); else addr=base-n*4+(P?0:4); u32 nb=U?base+n*4:base-n*4;
    int usr=S && !(L && (list&0x8000)); int om=g.cpsr&0x1F; if(usr && om!=0x10 && om!=0x1F){ bank_save(om); bank_load(0x10); }
    if(L){ if(W && !(list&(1<<rn))) g.r[rn]=nb;
      for(int i=0;i<16;i++) if(list&(1<<i)){ u32 v=rd32(addr); addr+=4; if(i==15){ if(S) set_cpsr(g.spsr); setpc(v&((g.cpsr&CPSR_T)?~1u:~3u)); } else g.r[i]=v; } }
    else { int first=1; for(int i=0;i<16;i++) if(list&(1<<i)){ u32 v=g.r[i]; if(i==15) v+=4; if(i==rn && !first) v=nb; wr32(addr,v); addr+=4; first=0; } if(W) g.r[rn]=nb; }
    if(usr && om!=0x10 && om!=0x1F){ bank_save(0x10); bank_load(om); } return; }
  case 5: { s32 off=(s32)(op<<8)>>6; if(op&(1<<24)) g.r[14]=g.r[15]-4; setpc(g.r[15]+off); return; }
  case 7: if((op&0x0F000000)==0x0F000000) swi((op>>16)&0xFF); return; } }
static void thumb_exec(u16 op){
  switch(op>>13){
  case 0: if(((op>>11)&3)!=3){ int c=!!(g.cpsr&FLAG_C); u32 r=shift(g.r[(op>>3)&7],(op>>11)&3,(op>>6)&31,&c,1); g.r[op&7]=r; setNZ(r); setC(c); }
    else { u32 a=g.r[(op>>3)&7]; u32 b=(op&(1<<10))?((op>>6)&7):g.r[(op>>6)&7]; g.r[op&7]=(op&(1<<9))?sub_f(a,b,1,1):add_f(a,b,0,1); } return;
  case 1: { int rd=(op>>8)&7; u32 imm=op&0xFF; switch((op>>11)&3){ case 0: g.r[rd]=imm; setNZ(imm); break; case 1: sub_f(g.r[rd],imm,1,1); break;
      case 2: g.r[rd]=add_f(g.r[rd],imm,0,1); break; case 3: g.r[rd]=sub_f(g.r[rd],imm,1,1); break; } return; }
  case 2:
    if((op&0xFC00)==0x4000){ int rd=op&7; u32 a=g.r[rd], b=g.r[(op>>3)&7]; int c=!!(g.cpsr&FLAG_C); u32 r;
      switch((op>>6)&15){ case 0: r=a&b; g.r[rd]=r; setNZ(r); break; case 1: r=a^b; g.r[rd]=r; setNZ(r); break;
      case 2: r=shift(a,0,b&0xFF,&c,0); g.r[rd]=r; setNZ(r); setC(c); break; case 3: r=shift(a,1,b&0xFF,&c,0); g.r[rd]=r; setNZ(r); setC(c); break;
      case 4: r=shift(a,2,b&0xFF,&c,0); g.r[rd]=r; setNZ(r); setC(c); break; case 5: g.r[rd]=add_f(a,b,!!(g.cpsr&FLAG_C),1); break;
      case 6: g.r[rd]=sub_f(a,b,!!(g.cpsr&FLAG_C),1); break; case 7: r=shift(a,3,b&0xFF,&c,0); g.r[rd]=r; setNZ(r); setC(c); break;
      case 8: setNZ(a&b); break; case 9: g.r[rd]=sub_f(0,b,1,1); break; case 10: sub_f(a,b,1,1); break; case 11: add_f(a,b,0,1); break;
      case 12: r=a|b; g.r[rd]=r; setNZ(r); break; case 13: r=a*b; g.r[rd]=r; setNZ(r); break; case 14: r=a&~b; g.r[rd]=r; setNZ(r); break; case 15: r=~b; g.r[rd]=r; setNZ(r); break; }
      return; }
    if((op&0xFC00)==0x4400){ int rd=(op&7)|((op>>4)&8), rs=(op>>3)&15; u32 b=g.r[rs];
      switch((op>>8)&3){ case 0: if(rd==15) setpc((g.r[15]+b)&~1); else g.r[rd]+=b; break; case 1: sub_f(g.r[rd],b,1,1); break;
      case 2: if(rd==15) setpc(b&~1); else g.r[rd]=b; break; case 3: if(b&1) setpc(b&~1); else { g.cpsr&=~CPSR_T; setpc(b&~3);} break; } return; }
    if((op&0xF800)==0x4800){ g.r[(op>>8)&7]=rd32((g.r[15]&~3)+((op&0xFF)<<2)); return; }
    { int ro=(op>>6)&7, rb=(op>>3)&7, rd=op&7; u32 a=g.r[rb]+g.r[ro];
      if(!(op&(1<<9))){ switch((op>>10)&3){ case 0: wr32(a,g.r[rd]); break; case 1: wr8(a,g.r[rd]); break; case 2: g.r[rd]=ldr_rot(a); break; case 3: g.r[rd]=rd8(a); break; } }
      else { switch((op>>10)&3){ case 0: wr16(a,g.r[rd]); break; case 1: g.r[rd]=(s32)(s8)rd8(a); break;
          case 2: { u32 v=rd16(a); if(a&1) v=(v>>8)|(v<<24); g.r[rd]=v; } break; case 3: g.r[rd]=(a&1)?(u32)(s32)(s8)rd8(a):(u32)(s32)(s16)rd16(a); break; } }
      return; }
  case 3: { int rb=(op>>3)&7, rd=op&7; u32 off=(op>>6)&31;
      switch((op>>11)&3){ case 0: wr32(g.r[rb]+off*4,g.r[rd]); break; case 1: g.r[rd]=ldr_rot(g.r[rb]+off*4); break; case 2: wr8(g.r[rb]+off,g.r[rd]); break; case 3: g.r[rd]=rd8(g.r[rb]+off); break; } return; }
  case 4: if(!(op&0x1000)){ int rb=(op>>3)&7, rd=op&7; u32 a=g.r[rb]+((op>>6)&31)*2; if(op&0x800){ u32 v=rd16(a); if(a&1) v=(v>>8)|(v<<24); g.r[rd]=v; } else wr16(a,g.r[rd]); }
    else { int rd=(op>>8)&7; u32 a=g.r[13]+(op&0xFF)*4; if(op&0x800) g.r[rd]=ldr_rot(a); else wr32(a,g.r[rd]); } return;
  case 5:
    if(!(op&0x1000)){ g.r[(op>>8)&7]=((op&0x800)?g.r[13]:(g.r[15]&~3))+(op&0xFF)*4; return; }
    if((op&0xFF00)==0xB000){ u32 v=(op&0x7F)*4; if(op&0x80) g.r[13]-=v; else g.r[13]+=v; return; }
    if((op&0xF600)==0xB400){ int L=op&0x800, R=op&0x100; u8 list=op&0xFF;
      if(L){ u32 a=g.r[13]; for(int i=0;i<8;i++) if(list&(1<<i)){ g.r[i]=rd32(a); a+=4; } if(R){ setpc(rd32(a)&~1); a+=4; } g.r[13]=a; }
      else { int n=__builtin_popcount(list)+(R?1:0); u32 a=g.r[13]-n*4; g.r[13]=a; for(int i=0;i<8;i++) if(list&(1<<i)){ wr32(a,g.r[i]); a+=4; } if(R) wr32(a,g.r[14]); }
      return; }
    return;
  case 6:
    if(!(op&0x1000)){ int rb=(op>>8)&7; u8 list=op&0xFF; u32 a=g.r[rb];
      if(op&0x800){ for(int i=0;i<8;i++) if(list&(1<<i)){ g.r[i]=rd32(a); a+=4; } if(!(list&(1<<rb))) g.r[rb]=a; }
      else { for(int i=0;i<8;i++) if(list&(1<<i)){ wr32(a,g.r[i]); a+=4; } g.r[rb]=a; } return; }
    { int c=(op>>8)&15; if(c==15){ swi(op&0xFF); return; } if(c==14) return; if(cond_ok(c)) setpc(g.r[15]+((s32)(s8)(op&0xFF))*2); return; }
  case 7:
    if(((op>>11)&3)==0){ setpc(g.r[15]+(((s32)(op<<21))>>20)); return; }
    if(((op>>11)&3)==2){ g.r[14]=g.r[15]+(((s32)(op<<21))>>9); return; }
    if(((op>>11)&3)==3){ u32 nxt=(g.r[15]-2)|1; u32 t=g.r[14]+((op&0x7FF)<<1); g.r[14]=nxt; setpc(t&~1); return; }
    return; } }
static void lz77(u32 src,u32 dst,int vram){ u32 size=rd32(src)>>8; src+=4;
  if(trace) fprintf(stderr,"[f%u] LZ77 %08X -> %08X size=%u pc=%08X\n",g.frame,src-4,dst,size,cur_pc);
  u8 *tmp=malloc(size+16); u32 n=0;
  while(n<size){ u8 fl=rd8(src++); for(int i=0;i<8&&n<size;i++){ if(fl&0x80){ u8 b1=rd8(src++),b2=rd8(src++); int len=(b1>>4)+3, disp=((b1&15)<<8|b2)+1;
        for(int j=0;j<len&&n<size;j++){ tmp[n]=tmp[n-disp]; n++; } } else tmp[n++]=rd8(src++); fl<<=1; } }
  if(vram){ for(u32 i=0;i<size;i+=2) wr16(dst+i,tmp[i]|((i+1<size?tmp[i+1]:0)<<8)); } else for(u32 i=0;i<size;i++) wr8(dst+i,tmp[i]);
  free(tmp); }
static void rlunc(u32 src,u32 dst,int vram){ u32 size=rd32(src)>>8; src+=4; u8 *tmp=malloc(size+256); u32 n=0;
  while(n<size){ u8 f=rd8(src++); if(f&0x80){ int len=(f&0x7F)+3; u8 b=rd8(src++); while(len--&&n<size) tmp[n++]=b; } else { int len=(f&0x7F)+1; while(len--&&n<size) tmp[n++]=rd8(src++); } }
  if(vram){ for(u32 i=0;i<size;i+=2) wr16(dst+i,tmp[i]|(tmp[i+1]<<8)); } else for(u32 i=0;i<size;i++) wr8(dst+i,tmp[i]); free(tmp); }
static void huff(u32 src,u32 dst){ u32 hdr=rd32(src); int bits=hdr&15; u32 size=hdr>>8; u32 tree=src+4; u32 data=tree+(rd8(tree)+1)*2; u32 out=0,ob=0,n=0;
  u32 node=tree+1; u8 nv=rd8(node);
  while(n<size){ u32 w=rd32(data); data+=4;
    for(int i=31;i>=0&&n<size;i--){ int bit=(w>>i)&1; u32 next=(node&~1)+((nv&0x3F)+1)*2+bit; int leaf=nv&(0x80>>bit); nv=rd8(next); node=next;
      if(leaf){ out|=(u32)nv<<ob; ob+=bits; node=tree+1; nv=rd8(node); if(ob==32){ wr32(dst+n,out); n+=4; out=0; ob=0; } } } } }
static void swi(int n){ u32 *r=g.r;
  switch(n){
  case 0x01: { u8 f=r[0]; if(f&1) memset(g.ewram,0,sizeof g.ewram); if(f&2) memset(g.iwram,0,0x7E00); if(f&4) memset(g.pal,0,sizeof g.pal); if(f&8) memset(g.vram,0,sizeof g.vram); if(f&16) memset(g.oam,0,sizeof g.oam); } break;
  case 0x02: case 0x03: g.halted=1; break;
  case 0x04: case 0x05: { if(n==5){ r[0]=1; r[1]=1; } IO16(0x208)=1;
    if(!g.intrwait){ g.intrwait=1; if(r[0]) wr16(0x03007FF8,rd16(0x03007FF8)&~r[1]); }
    u16 f=rd16(0x03007FF8); if(f&r[1]){ wr16(0x03007FF8,f&~r[1]); g.intrwait=0; } else { g.halted=1; setpc(cur_pc); } } break;
  case 0x06: if(r[1]){ s32 a=r[0],b=r[1],q=a/b,m=a%b; r[0]=q; r[1]=m; r[3]=q<0?-q:q; } break;
  case 0x07: if(r[0]){ s32 a=r[1],b=r[0],q=a/b,m=a%b; r[0]=q; r[1]=m; r[3]=q<0?-q:q; } break;
  case 0x08: { u32 v=r[0], res=0, bit=1u<<30; while(bit>v) bit>>=2; while(bit){ if(v>=res+bit){ v-=res+bit; res=(res>>1)+bit;} else res>>=1; bit>>=2; } r[0]=res; } break;
  case 0x09: { s32 a=r[0]; s32 b=-((a*a)>>14); s32 t=((0xA9*b)>>14)+0x390; t=((t*b)>>14)+0x91C; t=((t*b)>>14)+0xFB6; t=((t*b)>>14)+0x16AA; t=((t*b)>>14)+0x2081; t=((t*b)>>14)+0x3651; t=((t*b)>>14)+0xA2F9; r[0]=(a*t)>>16; } break;
  case 0x0A: { double x=(s16)r[0], y=(s16)r[1]; double ang=__builtin_atan2(y,x); if(ang<0) ang+=2*3.14159265358979; r[0]=((u32)(ang/(2*3.14159265358979)*65536.0))&0xFFFF; } break;
  case 0x0B: { u32 s=r[0],d=r[1],c=r[2]; u32 cnt=c&0x1FFFFF; int fill=c&(1<<24), w32=c&(1<<26);
      if(trace && ((d>>24)>=5&&(d>>24)<=7)) fprintf(stderr,"[f%u] CpuSet %08X -> %08X n=%u pc=%08X\n",g.frame,s,d,cnt,cur_pc);
      if(w32){ u32 v=rd32(s); for(u32 i=0;i<cnt;i++){ wr32(d,fill?v:rd32(s)); d+=4; if(!fill) s+=4; } } else { u16 v=rd16(s); for(u32 i=0;i<cnt;i++){ wr16(d,fill?v:rd16(s)); d+=2; if(!fill) s+=2; } } } break;
  case 0x0C: { u32 s=r[0],d=r[1],c=r[2]; u32 cnt=((c&0x1FFFFF)+7)&~7; int fill=c&(1<<24); u32 v=rd32(s);
      if(trace && ((d>>24)>=5&&(d>>24)<=7)) fprintf(stderr,"[f%u] CpuFastSet %08X -> %08X n=%u pc=%08X\n",g.frame,s,d,cnt,cur_pc);
      for(u32 i=0;i<cnt;i++){ wr32(d,fill?v:rd32(s)); d+=4; if(!fill) s+=4; } } break;
  case 0x0D: r[0]=0xBAAE187F; break;
  case 0x0E: { u32 s=r[0],d=r[1]; for(u32 i=0;i<r[2];i++){ s32 ox=rd32(s),oy=rd32(s+4); s16 cx=rd16(s+8),cy=rd16(s+10),sx=rd16(s+12),sy=rd16(s+14); u16 th=rd16(s+16); s+=20;
        double a=th/65536.0*2*3.14159265358979; s32 c=(s32)(__builtin_cos(a)*256), sn=(s32)(__builtin_sin(a)*256);
        s16 pa=(sx*c)>>8, pb=-(sx*sn)>>8, pc=(sy*sn)>>8, pd=(sy*c)>>8;
        wr16(d,pa);wr16(d+2,pb);wr16(d+4,pc);wr16(d+6,pd); wr32(d+8,ox-(pa*cx+pb*cy)); wr32(d+12,oy-(pc*cx+pd*cy)); d+=16; } } break;
  case 0x0F: { u32 s=r[0],d=r[1],st=r[3]; for(u32 i=0;i<r[2];i++){ s16 sx=rd16(s),sy=rd16(s+2); u16 th=rd16(s+4); s+=8;
        double a=th/65536.0*2*3.14159265358979; s32 c=(s32)(__builtin_cos(a)*256), sn=(s32)(__builtin_sin(a)*256);
        wr16(d,(sx*c)>>8); wr16(d+st,-(sx*sn)>>8); wr16(d+2*st,(sy*sn)>>8); wr16(d+3*st,(sy*c)>>8); d+=4*st; } } break;
  case 0x10: { u32 s=r[0],d=r[1],p=r[2]; u16 len=rd16(p); int sw=rd8(p+2), dw=rd8(p+3); u32 off=rd32(p+4); int z=off>>31; off&=0x7FFFFFFF;
      u32 out=0; int ob=0; for(u32 i=0;i<len;i++){ u8 b=rd8(s+i); for(int k=0;k<8;k+=sw){ u32 v=(b>>k)&((1<<sw)-1); if(v||z) v+=off; out|=v<<ob; ob+=dw; if(ob>=32){ wr32(d,out); d+=4; out=0; ob=0; } } } } break;
  case 0x11: lz77(r[0],r[1],0); break; case 0x12: lz77(r[0],r[1],1); break; case 0x13: huff(r[0],r[1]); break;
  case 0x14: rlunc(r[0],r[1],0); break; case 0x15: rlunc(r[0],r[1],1); break;
  case 0x16: case 0x17: { u32 s=r[0],d=r[1]; u32 size=rd32(s)>>8; s+=4; u8 acc=0; for(u32 i=0;i<size;i++){ acc+=rd8(s+i); wr8(d+i,acc);} } break;
  case 0x18: { u32 s=r[0],d=r[1]; u32 size=rd32(s)>>8; s+=4; u16 acc=0; for(u32 i=0;i<size;i+=2){ acc+=rd16(s+i); wr16(d+i,acc);} } break;
  case 0x1F: { double m=r[1], f=r[2]/256.0; r[0]=(u32)((double)rd32(r[0]+4)/__builtin_pow(2.0,(180.0-m-f)/12.0)); } break;
  default: break; } }
static u16 linebuf[5][240]; static u8 objprio[240], objsemi[240], objwin[240];
static void render_text_bg(int bg,int y){ u16 cnt=IO16(0x08+bg*2); u32 cb=((cnt>>2)&3)*0x4000, sb=((cnt>>8)&31)*0x800; int c256=cnt&0x80, sz=cnt>>14;
  int hof=IO16(0x10+bg*4)&0x1FF, vof=IO16(0x12+bg*4)&0x1FF; int w=(sz&1)?512:256, h=(sz&2)?512:256; int yy=(y+vof)&(h-1);
  for(int x=0;x<240;x++){ int xx=(x+hof)&(w-1); int sbi=0; if(xx>=256) sbi+=1; if(yy>=256) sbi+=(w==512)?2:1;
    u16 e=*(u16*)&g.vram[sb+sbi*0x800+(((yy&255)>>3)*32+((xx&255)>>3))*2]; int tx=xx&7, ty=yy&7; if(e&0x400) tx=7-tx; if(e&0x800) ty=7-ty; int tile=e&0x3FF; u8 ci;
    if(c256){ u32 a=cb+tile*64+ty*8+tx; ci=a<0x10000?g.vram[a]:0; linebuf[bg][x]=ci?0x8000|*(u16*)&g.pal[ci*2]:0; }
    else { u32 a=cb+tile*32+ty*4+tx/2; ci=a<0x10000?g.vram[a]:0; ci=(tx&1)?ci>>4:ci&15; linebuf[bg][x]=ci?0x8000|*(u16*)&g.pal[((e>>12)*16+ci)*2]:0; } } }
static void render_affine_bg(int bg){ u16 cnt=IO16(0x08+bg*2); u32 cb=((cnt>>2)&3)*0x4000, sb=((cnt>>8)&31)*0x800; int size=128<<(cnt>>14), wrap=cnt&0x2000;
  int i=bg-2; s16 pa=IO16(0x20+i*16), pc=IO16(0x24+i*16); s32 x0=g.bgx[i], y0=g.bgy[i];
  for(int x=0;x<240;x++){ s32 tx=(x0+pa*x)>>8, ty=(y0+pc*x)>>8; if(wrap){ tx&=size-1; ty&=size-1; } else if(tx<0||ty<0||tx>=size||ty>=size){ linebuf[bg][x]=0; continue; }
    u8 tile=g.vram[sb+(ty>>3)*(size>>3)+(tx>>3)]; u8 ci=g.vram[cb+tile*64+(ty&7)*8+(tx&7)]; linebuf[bg][x]=ci?0x8000|*(u16*)&g.pal[ci*2]:0; } }
static void render_obj(int y){ u16 dc=IO16(0); int map1d=dc&0x40, bmp=(dc&7)>=3;
  memset(linebuf[4],0,480); memset(objprio,4,240); memset(objsemi,0,240); memset(objwin,0,240);
  static const int sizes[3][4][2]={{{8,8},{16,16},{32,32},{64,64}},{{16,8},{32,8},{32,16},{64,32}},{{8,16},{8,32},{16,32},{32,64}}};
  for(int i=0;i<128;i++){ u16 a0=*(u16*)&g.oam[i*8], a1=*(u16*)&g.oam[i*8+2], a2=*(u16*)&g.oam[i*8+4];
    int aff=a0&0x100; if(!aff && (a0&0x200)) continue; int shape=(a0>>14)&3; if(shape==3) continue; int sz=(a1>>14)&3;
    int w=sizes[shape][sz][0], h=sizes[shape][sz][1], bw=w, bh=h; if(aff && (a0&0x200)){ bw*=2; bh*=2; }
    int oy=a0&0xFF, ox=a1&0x1FF; if(ox>=240) ox-=512; int ly=(y-oy)&0xFF; if(ly>=bh) continue;
    int mode=(a0>>10)&3, c256=a0&0x2000, tile=a2&0x3FF, prio=(a2>>10)&3, palb=(a2>>12)*16; if(bmp && tile<512) continue;
    s16 pa=256,pb=0,pc=0,pd=256; if(aff){ int p=(a1>>9)&31; pa=*(s16*)&g.oam[p*32+6]; pb=*(s16*)&g.oam[p*32+14]; pc=*(s16*)&g.oam[p*32+22]; pd=*(s16*)&g.oam[p*32+30]; }
    for(int lx=0;lx<bw;lx++){ int sx=ox+lx; if(sx<0||sx>=240) continue; int tx,ty;
      if(aff){ int cx=lx-bw/2, cy=ly-bh/2; tx=((pa*cx+pb*cy)>>8)+w/2; ty=((pc*cx+pd*cy)>>8)+h/2; if(tx<0||ty<0||tx>=w||ty>=h) continue; }
      else { tx=lx; ty=ly; if(a1&0x1000) tx=w-1-tx; if(a1&0x2000) ty=h-1-ty; }
      int t; u8 ci;
      if(c256){ t=map1d? tile+((ty>>3)*(w>>3)+(tx>>3))*2 : (tile&~1)+(ty>>3)*32+(tx>>3)*2; ci=g.vram[0x10000+(t&0x3FF)*32+(ty&7)*8+(tx&7)]; }
      else { t=map1d? tile+(ty>>3)*(w>>3)+(tx>>3) : tile+(ty>>3)*32+(tx>>3); ci=g.vram[0x10000+(t&0x3FF)*32+(ty&7)*4+(tx&7)/2]; ci=(tx&1)?ci>>4:ci&15; }
      if(!ci) continue; if(mode==2){ objwin[sx]=1; continue; }
      if(prio<objprio[sx] || !(linebuf[4][sx]&0x8000)){ linebuf[4][sx]=0x8000|*(u16*)&g.pal[0x200+(c256?ci:palb+ci)*2]; objprio[sx]=prio; objsemi[sx]=(mode==1); } } } }
static int inwin(int w,int x,int y){ u16 h=IO16(0x40+w*2), v=IO16(0x44+w*2); int x1=h>>8,x2=h&0xFF,y1=v>>8,y2=v&0xFF;
  int ix=(x1<=x2)?(x>=x1&&x<x2):(x>=x1||x<x2); int iy=(y1<=y2)?(y>=y1&&y<y2):(y>=y1||y<y2); return ix&&iy; }
static void render_line(int y){ u16 dc=IO16(0); int mode=dc&7;
  if(dc&0x80){ for(int x=0;x<240;x++) fb[y*240+x]=0x7FFF; return; }
  for(int b=0;b<4;b++) memset(linebuf[b],0,480); int en=(dc>>8)&0x1F;
  if(mode==0){ for(int b=0;b<4;b++) if(en&(1<<b)) render_text_bg(b,y); }
  else if(mode==1){ for(int b=0;b<2;b++) if(en&(1<<b)) render_text_bg(b,y); if(en&4) render_affine_bg(2); }
  else if(mode==2){ if(en&4) render_affine_bg(2); if(en&8) render_affine_bg(3); }
  else if(mode==3){ if(en&4) for(int x=0;x<240;x++) linebuf[2][x]=0x8000|*(u16*)&g.vram[(y*240+x)*2]; }
  else if(mode==4){ u32 base=(dc&0x10)?0xA000:0; if(en&4) for(int x=0;x<240;x++){ u8 c=g.vram[base+y*240+x]; linebuf[2][x]=c?0x8000|*(u16*)&g.pal[c*2]:0; } }
  else if(mode==5){ u32 base=(dc&0x10)?0xA000:0; if(en&4) for(int x=0;x<240;x++) linebuf[2][x]=(x<160&&y<128)?0x8000|*(u16*)&g.vram[base+(y*160+x)*2]:0; }
  if(en&0x10) render_obj(y); else { memset(linebuf[4],0,480); memset(objwin,0,240); }
  int win0=dc&0x2000, win1=dc&0x4000, winobj=dc&0x8000, anywin=win0||win1||winobj;
  u16 bldcnt=IO16(0x50); int bmode=(bldcnt>>6)&3; u16 ba=IO16(0x52); int eva=ba&31, evb=(ba>>8)&31; if(eva>16)eva=16; if(evb>16)evb=16; int evy=IO16(0x54)&31; if(evy>16)evy=16;
  u16 backdrop=*(u16*)&g.pal[0];
  for(int x=0;x<240;x++){ int mask=0x3F;
    if(anywin){ mask=(winobj&&objwin[x])?(IO16(0x4A)>>8)&0x3F:IO16(0x4A)&0x3F;
      if(win1 && inwin(1,x,y)) mask=(IO16(0x48)>>8)&0x3F; if(win0 && inwin(0,x,y)) mask=IO16(0x48)&0x3F; }
    int top=5, sec=5; u16 tc=backdrop, sc=backdrop;
    for(int pr=0;pr<4;pr++){
      if((mask&0x10) && (linebuf[4][x]&0x8000) && objprio[x]==pr){ if(top==5){top=4;tc=linebuf[4][x];} else if(sec==5){sec=4;sc=linebuf[4][x];} }
      for(int b=0;b<4;b++){ if(!(en&(1<<b))||!(mask&(1<<b))||(IO16(0x08+b*2)&3)!=pr||!(linebuf[b][x]&0x8000)) continue;
        if(top==5){top=b;tc=linebuf[b][x];} else if(sec==5){sec=b;sc=linebuf[b][x];} } }
    u16 out=tc&0x7FFF; int seff=(mask&0x20)||!anywin; int topsel=(bldcnt>>top)&1, secsel=(bldcnt>>(8+sec))&1;
    int r1=out&31,g1=(out>>5)&31,b1=(out>>10)&31,r2=sc&31,g2=(sc>>5)&31,b2=(sc>>10)&31;
    if((top==4 && objsemi[x] && secsel) || (seff && topsel && bmode==1 && secsel)){ int r=(r1*eva+r2*evb)>>4, gg=(g1*eva+g2*evb)>>4, b=(b1*eva+b2*evb)>>4; if(r>31)r=31; if(gg>31)gg=31; if(b>31)b=31; out=r|(gg<<5)|(b<<10); }
    else if(seff && topsel && bmode==2){ r1+=((31-r1)*evy)>>4; g1+=((31-g1)*evy)>>4; b1+=((31-b1)*evy)>>4; out=r1|(g1<<5)|(b1<<10); }
    else if(seff && topsel && bmode==3){ r1-=(r1*evy)>>4; g1-=(g1*evy)>>4; b1-=(b1*evy)>>4; out=r1|(g1<<5)|(b1<<10); }
    fb[y*240+x]=out; } }
static void timers_step(u32 cyc){ static const int pres[4]={1,64,256,1024}; int prev=0;
  for(int t=0;t<4;t++){ u16 ctl=IO16(0x102+t*4); int ov=0; if(!(ctl&0x80)){ prev=0; continue; }
    if(t>0 && (ctl&4)){ if(prev){ g.tm_counter[t]++; if(g.tm_counter[t]>0xFFFF){ g.tm_counter[t]=g.tm_reload[t]; ov=1; } } }
    else { g.tm_sub[t]+=cyc; int p=pres[ctl&3]; while(g.tm_sub[t]>=(u32)p){ g.tm_sub[t]-=p; if(++g.tm_counter[t]>0xFFFF){ g.tm_counter[t]=g.tm_reload[t]; ov++; } } }
    if(ov && (ctl&0x40)) IO16(0x202)|=(8<<t); prev=ov; } }
static void check_irq(void){ if((IO16(0x208)&1) && (IO16(0x200)&IO16(0x202)) && !(g.cpsr&CPSR_I)){ u32 ret=g.r[15]+4, old=g.cpsr; set_cpsr((old&~0x3F)|0x12|CPSR_I); g.spsr=old; g.r[14]=ret; g.r[15]=0x18; } }
static void cpu_run(int cycles){ int done=0;
  while(done<cycles){ if(g.halted){ if(IO16(0x200)&IO16(0x202)) g.halted=0; else break; }
    check_irq(); cur_pc=g.r[15]; branched=0;
    if(g.cpsr&CPSR_T){ u16 op=rd16(cur_pc); g.r[15]=cur_pc+4; thumb_exec(op); if(!branched) g.r[15]=cur_pc+2; done+=((cur_pc>>24)>=8)?3:1; }
    else { u32 op=rd32(cur_pc); g.r[15]=cur_pc+8; arm_exec(op); if(!branched) g.r[15]=cur_pc+4; done+=((cur_pc>>24)>=8)?5:1; } }
  timers_step(cycles); }
static void run_frame(void){
  for(int ln=0;ln<228;ln++){ g.line=ln; u16 ds=IO16(4); ds&=~7; if(ln>=160&&ln<227) ds|=1; if(((ds>>8)&0xFF)==ln){ ds|=4; if(ds&0x20) IO16(0x202)|=4; } IO16(4)=ds;
    if(ln==160){ if(ds&8) IO16(0x202)|=1; dma_trigger(1); g.bgx[0]=(s32)(IO32(0x28)<<4)>>4; g.bgy[0]=(s32)(IO32(0x2C)<<4)>>4; g.bgx[1]=(s32)(IO32(0x38)<<4)>>4; g.bgy[1]=(s32)(IO32(0x3C)<<4)>>4; }
    cpu_run(960); if(ln<160) render_line(ln);
    IO16(4)|=2; if(IO16(4)&0x10) IO16(0x202)|=2; if(ln<160){ dma_trigger(2); g.bgx[0]+=(s16)IO16(0x22); g.bgy[0]+=(s16)IO16(0x26); g.bgx[1]+=(s16)IO16(0x32); g.bgy[1]+=(s16)IO16(0x36); }
    cpu_run(272); IO16(4)&=~2; }
  g.frame++; }
static void save_ppm(const char *fn){ FILE *f=fopen(fn,"wb"); fprintf(f,"P6\n240 160\n255\n");
  for(int i=0;i<240*160;i++){ u16 c=fb[i]; u8 px[3]={(c&31)<<3|(c&31)>>2,((c>>5)&31)<<3|((c>>5)&31)>>2,((c>>10)&31)<<3|((c>>10)&31)>>2}; fwrite(px,1,3,f); } fclose(f); }
static u16 parse_keys(const char *s){ u16 k=0; char buf[128]; strncpy(buf,s,127); buf[127]=0;
  for(char *t=strtok(buf,"+");t;t=strtok(NULL,"+")){ if(!strcmp(t,"A"))k|=1; else if(!strcmp(t,"B"))k|=2; else if(!strcmp(t,"SEL"))k|=4; else if(!strcmp(t,"START"))k|=8;
    else if(!strcmp(t,"RIGHT"))k|=16; else if(!strcmp(t,"LEFT"))k|=32; else if(!strcmp(t,"UP"))k|=64; else if(!strcmp(t,"DOWN"))k|=128; else if(!strcmp(t,"R"))k|=256; else if(!strcmp(t,"L"))k|=512; }
  return k; }
static void reset(void){ memset(&g,0,sizeof g);
  u32 stub[]={0xE92D500F,0xE3A00301,0xE28FE000,0xE510F004,0xE8BD500F,0xE25EF004}; /* IRQ: push; r0=0x04000000; lr=ret; ldr pc,[r0,#-4]; pop; subs pc,lr,#4 */
  *(u32*)&bios[0x18]=0xEA000016; memcpy(&bios[0x80],stub,sizeof stub);
  g.cpsr=0x1F; g.r[13]=0x03007F00; g.bank_usr[5]=0x03007F00; g.bank_irq[0]=0x03007FA0; g.bank_svc[0]=0x03007FE0;
  g.r[15]=0x08000000; IO16(0x88)=0x200; memset(g.eeprom,0xFF,sizeof g.eeprom); }
int main(int argc,char **argv){ if(argc<3){ fprintf(stderr,"usage: %s rom script\n",argv[0]); return 1; }
  FILE *f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); romsize=ftell(f); fseek(f,0,SEEK_SET); rom=malloc(romsize+4); if(fread(rom,1,romsize,f)!=romsize) return 1; fclose(f);
  reset(); FILE *sc=strcmp(argv[2],"-")?fopen(argv[2],"r"):stdin; char line[512]; u16 held=0;
  while(fgets(line,sizeof line,sc)){ char cmd[64]={0},a1[256]={0},a2[256]={0},a3[256]={0}; if(line[0]=='#') continue;
    int n=sscanf(line,"%63s %255s %255s %255s",cmd,a1,a2,a3); if(n<1) continue;
    if(!strcmp(cmd,"run")){ int k=atoi(a1); for(int i=0;i<k;i++){ g.keys=held; run_frame(); } }
    else if(!strcmp(cmd,"press")){ int k=n>2?atoi(a2):2; u16 pk=parse_keys(a1); for(int i=0;i<k;i++){ g.keys=held|pk; run_frame(); } g.keys=held; run_frame(); }
    else if(!strcmp(cmd,"hold")) held=strcmp(a1,"NONE")?parse_keys(a1):0;
    else if(!strcmp(cmd,"shot")) save_ppm(a1);
    else if(!strcmp(cmd,"save")){ FILE *o=fopen(a1,"wb"); fwrite(&g,sizeof g,1,o); fwrite(fb,sizeof fb,1,o); fclose(o); }
    else if(!strcmp(cmd,"load")){ FILE *o=fopen(a1,"rb"); if(o){ if(fread(&g,sizeof g,1,o)){} if(fread(fb,sizeof fb,1,o)){} fclose(o);} else fprintf(stderr,"no state %s\n",a1); }
    else if(!strncmp(cmd,"poke",4)){ u32 ad=strtoul(a1,0,0), v=strtoul(a2,0,0); if(cmd[4]=='8') wr8(ad,v); else if(!strcmp(cmd+4,"16")) wr16(ad,v); else wr32(ad,v); }
    else if(!strcmp(cmd,"dump")){ u32 ad=strtoul(a1,0,0), ln=strtoul(a2,0,0); FILE *o=fopen(a3,"wb"); for(u32 i=0;i<ln;i++) fputc(rd8(ad+i),o); fclose(o); }
    else if(!strcmp(cmd,"trace")) trace=!strcmp(a1,"on");
    else if(!strcmp(cmd,"regs")) fprintf(stderr,"f%u pc=%08X cpsr=%08X halted=%d IE=%04X IF=%04X DISPCNT=%04X\n",g.frame,g.r[15],g.cpsr,g.halted,IO16(0x200),IO16(0x202),IO16(0));
    else if(!strcmp(cmd,"eesave")){ FILE *o=fopen(a1,"wb"); fwrite(g.eeprom,1,sizeof g.eeprom,o); fclose(o); }
    else if(!strcmp(cmd,"eeload")){ FILE *o=fopen(a1,"rb"); if(o){ if(fread(g.eeprom,1,sizeof g.eeprom,o)){} fclose(o);} }
    else fprintf(stderr,"unknown cmd %s\n",cmd); }
  return 0; }
