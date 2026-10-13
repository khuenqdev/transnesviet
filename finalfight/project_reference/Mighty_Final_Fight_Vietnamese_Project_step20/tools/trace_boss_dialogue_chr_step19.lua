-- Step 19 optional FCEUX trace: sample active CHR banks while boss text renders.
-- Compatible with older FCEUX builds: deliberately does NOT use memory.registerread.
-- Run this on the STEP 19 ROM. Play until Thrasher's translated dialogue appears.
-- CSV and info are written beside this script; it does not modify game memory.

local MAX_ROWS = 40000
local FLUSH_EVERY = 128
local src = debug.getinfo(1, "S").source or ""
if src:sub(1,1) == "@" then src = src:sub(2) end
local dir = src:match("^(.*[/\\])") or ""
local csvPath = dir .. "step19_boss_chr_trace.csv"
local infoPath = dir .. "step19_boss_chr_trace_info.txt"
local f, err = io.open(csvPath, "w")
if not f then error("Cannot write trace CSV: " .. tostring(err)) end
local info = io.open(infoPath, "w")

local function safe(fn, ...)
  local ok, value = pcall(fn, ...)
  if ok then return value end
  return nil
end
local function hx(v, n)
  if v == nil then return "" end
  return string.format("0x%0" .. tostring(n or 2) .. "X", v)
end
local function csv(v)
  if v == nil then return "" end
  local s = tostring(v)
  if s:find('[,\"\r\n]') then s = '"' .. s:gsub('"','""') .. '"' end
  return s
end

local selectReg, regs = nil, {[0]=nil,[1]=nil,[2]=nil,[3]=nil,[4]=nil,[5]=nil,[6]=nil,[7]=nil}
local ppuCtrl = 0
local rows = 0
local stopped = false
local lastQueue = nil
local fields = {'row','frame','pc','pc_bank8000','pc_banka000','event','queue_char','char_class','a','x','y','p','r0','r1','r2','r3','r4','r5','r6','r7','bank_select','prg_mode','selected_reg','ppu_ctrl','value_source','code_bytes'}
f:write(table.concat(fields, ','), '\n'); f:flush()
local function prgMode()
  if selectReg == nil then return nil end
  return math.floor(selectReg/64)%2
end
local function selected()
  if selectReg == nil then return nil end
  return selectReg%8
end
local function mapBank(v)
  if v == nil then return nil end
  return v%16
end
local function mappedBanks()
  local mode=prgMode()
  if mode == nil then return nil,nil end
  if mode == 0 then return mapBank(regs[6]),mapBank(regs[7]) end
  return 14,mapBank(regs[7])
end
local function decodeAbsoluteStoreValue(address)
  local pc=safe(memory.getregister,'pc')
  if pc==nil then return nil end
  local a=safe(memory.getregister,'a'); local x=safe(memory.getregister,'x'); local y=safe(memory.getregister,'y')
  for back=0,4 do
    local base=(pc-back)%0x10000
    local op=safe(memory.readbyte,base)
    if op==0x8D or op==0x8E or op==0x8C then
      local lo=safe(memory.readbyte,(base+1)%0x10000); local hi=safe(memory.readbyte,(base+2)%0x10000)
      if lo~=nil and hi~=nil and lo+hi*256==address then
        if op==0x8D and a~=nil then return a,'decoded_STA_abs' end
        if op==0x8E and x~=nil then return x,'decoded_STX_abs' end
        if op==0x8C and y~=nil then return y,'decoded_STY_abs' end
      end
    end
  end
  return nil
end
local function valueFor(address,size,value,isMapper)
  if type(value)=='number' then return value,'callback_value' end
  if isMapper then
    local v,src=decodeAbsoluteStoreValue(address)
    if v~=nil then return v,src end
    return nil,'unavailable_legacy_callback'
  end
  return safe(memory.readbyte,address),'memory_read_fallback'
end
local function writeRow(eventName, queueChar, valueSource)
  if stopped then return end
  rows=rows+1
  if rows>MAX_ROWS then
    stopped=true
    if info then info:write('\nStopped: MAX_ROWS reached.\n'); info:flush() end
    emu.message('Step 19 boss trace reached row limit')
    return
  end
  local pc=safe(memory.getregister,'pc')
  local a=safe(memory.getregister,'a'); local x=safe(memory.getregister,'x'); local y=safe(memory.getregister,'y'); local p=safe(memory.getregister,'p')
  local b8,ba=mappedBanks()
  local q=queueChar
  local cls=''
  if q~=nil then
    if q>=0x30 and q<=0x7F then cls='low_custom_or_punctuation'
    elseif q>=0x80 and q<=0x8F then cls='extended_custom'
    elseif q==0xFF then cls='terminator'
    else cls='ordinary_or_control' end
  end
  local bc=''
  if pc~=nil then
    local t={}
    for i=0,3 do local v=safe(memory.readbyte,(pc+i)%0x10000); t[#t+1]=v and string.format('%02X',v) or '??' end
    bc=table.concat(t,' ')
  end
  local row={rows,safe(emu.framecount),hx(pc,4),b8,ba,eventName,hx(q,2),cls,hx(a,2),hx(x,2),hx(y,2),hx(p,2),hx(regs[0],2),hx(regs[1],2),hx(regs[2],2),hx(regs[3],2),hx(regs[4],2),hx(regs[5],2),hx(regs[6],2),hx(regs[7],2),hx(selectReg,2),prgMode(),selected(),hx(ppuCtrl,2),valueSource,bc}
  for i=1,#row do row[i]=csv(row[i]) end
  f:write(table.concat(row,','),'\n')
  if rows%FLUSH_EVERY==0 then f:flush() end
end
local function onMapperWrite(address,size,value)
  local v,src=valueFor(address,size,value,true)
  if address==0x8000 then if v~=nil then selectReg=v end
  elseif address==0x8001 then local r=selected(); if r~=nil and v~=nil then regs[r]=v end
  end
  writeRow('MMC3_WRITE_'..string.format('%04X',address),safe(memory.readbyte,0x0783),src)
end
for _,addr in ipairs({0x8000,0x8001}) do memory.registerwrite(addr,1,onMapperWrite) end
memory.registerwrite(0x2000,1,function(address,size,value)
  local v=valueFor(address,size,value,false); if v~=nil then ppuCtrl=v end
end)
memory.registerwrite(0x0783,1,function(address,size,value)
  local v=valueFor(address,size,value,false); if v~=nil then lastQueue=v end
end)
memory.registerexecute(0xF406,function()
  local q=safe(memory.readbyte,0x0783)
  -- Log custom/accent byte range and punctuation to keep the trace manageable.
  if q~=nil and ((q>=0x30 and q<=0x8F) or q==0x75 or q==0x76) then
    writeRow('EXEC_CHAR_LOOKUP_F406',q,'ram_0783_at_exec')
  end
end)
if info then
  info:write('Step 19 boss dialogue CHR-bank trace\n')
  info:write('ROM: '..tostring(safe(rom.getfilename) or 'unknown')..'\n')
  info:write('FCEUX MD5: '..tostring(safe(rom.gethash,'md5') or 'unknown')..'\n')
  info:write('Watches MMC3 $8000/$8001 writes, PPUCTRL writes, RAM $0783, and char lookup $F406.\n')
  info:write('No memory.registerread call; compatible with FCEUX builds lacking that callback.\n')
  info:write('Only logs $30-$8F text bytes plus punctuation at $F406. Bank values depend on observing mapper writes after startup.\n')
  info:write('Start from reset, run the translated boss dialogue, and stop normally.\n')
  info:flush()
end
emu.registerexit(function()
  if f then f:flush(); f:close(); f=nil end
  if info then info:write('\nLogged rows: '..tostring(rows)..'\n'); info:flush(); info:close(); info=nil end
end)
emu.message('Step 19 trace installed; power-cycle, then play to Thrasher dialogue')
safe(emu.poweron)
