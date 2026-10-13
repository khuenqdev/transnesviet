-- Pyokotan no Dai Meiro — FCEUX text/mapper/PPU trace, v2
-- Read-only diagnostic: it never writes to emulator memory or the ROM.
-- Based on FCEUX memory.registerread/registerwrite APIs. See README for usage.

local TRACE_PATH = "pyokotan_runtime_trace_v2.csv"
local MAX_ROWS = 200000
local FLUSH_EVERY = 250
local PRG_8K_BANKS = 16       -- from this ROM's NES 2.0 header
local CHR_1K_BANKS = 128      -- from this ROM's 128 KiB CHR ROM

local out = io.open(TRACE_PATH, "w")
if not out then
  emu.message("Cannot open " .. TRACE_PATH .. "; edit TRACE_PATH to an absolute writable path.")
  return
end

local header = {
  "frame","event","address","value","pc","size","mapper_command","mapper_register",
  "prg_8000_raw","prg_a000_raw","prg_c000_raw",
  "chr0_raw","chr1_raw","chr2_raw","chr3_raw","chr4_raw","chr5_raw","chr6_raw","chr7_raw",
  "ppu_ctrl","ppu_addr_current","ppu_addr_write_target","ppu_latch_high_next"
}
out:write(table.concat(header, ",") .. "\n")
out:flush()

local rows = 0
local closed = false
local mapper_command = nil
local prg_banks = {[9]=nil,[10]=nil,[11]=nil}
local chr_banks = {[0]=nil,[1]=nil,[2]=nil,[3]=nil,[4]=nil,[5]=nil,[6]=nil,[7]=nil}
local ppu_ctrl = 0
local ppu_addr = 0
local ppu_addr_high = 0
local ppu_latch_high_next = true

local function hx(v, width)
  if v == nil then return "" end
  return string.format("0x%0" .. tostring(width or 2) .. "X", v)
end

local function safe_register(name)
  local ok, v = pcall(function() return memory.getregister(name) end)
  if ok and type(v) == "number" then return v end
  return 0
end

local function safe_frame()
  local ok, v = pcall(function() return emu.framecount() end)
  if ok and type(v) == "number" then return v end
  return 0
end

local function csv_cell(v)
  if v == nil then return "" end
  local s = tostring(v)
  if string.find(s, '[",\r\n]') then
    return '"' .. string.gsub(s, '"', '""') .. '"'
  end
  return s
end

local function emit(event, address, size, value, selected_register, ppu_target)
  if closed or rows >= MAX_ROWS then return end
  local vals = {
    safe_frame(), event, hx(address,4), hx(value,2), hx(safe_register("pc"),4), size or 1,
    mapper_command and hx(mapper_command,1) or "",
    selected_register ~= nil and hx(selected_register,1) or "",
    prg_banks[9] ~= nil and hx(prg_banks[9],2) or "",
    prg_banks[10] ~= nil and hx(prg_banks[10],2) or "",
    prg_banks[11] ~= nil and hx(prg_banks[11],2) or "",
    chr_banks[0] ~= nil and hx(chr_banks[0],2) or "",
    chr_banks[1] ~= nil and hx(chr_banks[1],2) or "",
    chr_banks[2] ~= nil and hx(chr_banks[2],2) or "",
    chr_banks[3] ~= nil and hx(chr_banks[3],2) or "",
    chr_banks[4] ~= nil and hx(chr_banks[4],2) or "",
    chr_banks[5] ~= nil and hx(chr_banks[5],2) or "",
    chr_banks[6] ~= nil and hx(chr_banks[6],2) or "",
    chr_banks[7] ~= nil and hx(chr_banks[7],2) or "",
    hx(ppu_ctrl,2), hx(ppu_addr,4), ppu_target ~= nil and hx(ppu_target,4) or "",
    ppu_latch_high_next and "1" or "0"
  }
  for i=1,#vals do vals[i] = csv_cell(vals[i]) end
  out:write(table.concat(vals, ",") .. "\n")
  rows = rows + 1
  if rows % FLUSH_EVERY == 0 then out:flush() end
  if rows >= MAX_ROWS then
    out:flush(); out:close(); closed = true
    emu.message("Trace row limit reached; output flushed and closed.")
  end
end

-- CPU reads from the observed 12-row literal table and its two-byte trailers.
-- The range is $DE86-$E01D inclusive (0x198 bytes). CPU $C000-$DFFF depends on
-- current FME-7 bank command $0B; $E000-$FFFF is fixed to the last bank.
memory.registerread(0xDE86, 0x198, function(address, size, value)
  emit("text_region_read", address, size, value, nil, nil)
end)

-- Mapper 69: $8000-$9FFF selects command; $A000-$BFFF supplies its parameter.
-- Record command/parameter writes and track CHR commands 0-7 and PRG commands 9-B.
memory.registerwrite(0x8000, 0x2000, function(address, size, value)
  if value == nil then value = memory.readbyteunsigned(address) end
  mapper_command = value % 16
  emit("mapper_command_write", address, size, value, mapper_command, nil)
end)

memory.registerwrite(0xA000, 0x2000, function(address, size, value)
  if value == nil then value = memory.readbyteunsigned(address) end
  local reg = mapper_command
  if reg ~= nil and reg >= 0 and reg <= 7 then
    chr_banks[reg] = value
  elseif reg == 9 or reg == 10 or reg == 11 then
    prg_banks[reg] = value
  end
  emit("mapper_parameter_write", address, size, value, reg, nil)
end)

-- Track CPU writes to PPU registers. A $2007 row includes the estimated PPU
-- address targeted before the write; CHR bank state is included in the CSV row.
memory.registerwrite(0x2000, 0x0008, function(address, size, value)
  if value == nil then value = memory.readbyteunsigned(address) end
  local ppu_target = nil
  local reg = address % 8
  if reg == 0 then
    ppu_ctrl = value
  elseif reg == 5 then
    -- $2005 and $2006 share the PPU write toggle.
    ppu_latch_high_next = not ppu_latch_high_next
  elseif reg == 6 then
    if ppu_latch_high_next then
      ppu_addr_high = value % 64
      ppu_addr = ((ppu_addr_high * 256) + (ppu_addr % 256)) % 0x4000
      ppu_latch_high_next = false
    else
      ppu_addr = ((ppu_addr_high * 256) + value) % 0x4000
      ppu_latch_high_next = true
    end
  elseif reg == 7 then
    ppu_target = ppu_addr
  end
  emit("ppu_register_write", address, size, value, nil, ppu_target)
  if reg == 7 then
    local increment = (ppu_ctrl % 8 >= 4) and 32 or 1
    ppu_addr = (ppu_addr + increment) % 0x4000
  end
end)

emu.message("Pyokotan trace v2 active. CSV: " .. TRACE_PATH)
