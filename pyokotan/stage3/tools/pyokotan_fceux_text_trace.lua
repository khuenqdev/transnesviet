-- Pyokotan no Dai Meiro — FCEUX Lua candidate text/bank trace
-- Tested against the documented FCEUX Lua API shape; adapt TRACE_PATH if needed.
-- Logs data reads in the candidate $DE86-$E01D region, writes to the FME-7
-- command/data address windows ($8000-$BFFF), and writes to PPU CPU registers.
-- It does not modify game memory or ROM.

local TRACE_PATH = "pyokotan_runtime_trace.csv"
local MAX_ROWS = 100000
local FLUSH_EVERY = 200
local out = io.open(TRACE_PATH, "w")
if not out then
  emu.message("Trace logger could not open " .. TRACE_PATH .. "; change TRACE_PATH to an absolute writable path.")
  return
end
out:write("frame,event,address,value,pc,size\n")
out:flush()

local rows = 0
local closed = false
local function close_log()
  if not closed then
    out:flush()
    out:close()
    closed = true
  end
end

local function emit(event, address, size, value)
  if closed or rows >= MAX_ROWS then return end
  local pc = 0
  local ok, result = pcall(function() return memory.getregister("pc") end)
  if ok and result then pc = result end
  local frame = 0
  local ok2, result2 = pcall(function() return emu.framecount() end)
  if ok2 and result2 then frame = result2 end
  out:write(string.format("%d,%s,0x%04X,0x%02X,0x%04X,%d\n", frame, event, address, value % 256, pc, size or 1))
  rows = rows + 1
  if rows % FLUSH_EVERY == 0 then out:flush() end
  if rows >= MAX_ROWS then
    out:write(string.format("%d,limit_reached,0x0000,0x00,0x0000,1\n", frame))
    close_log()
    emu.message("Pyokotan trace row limit reached; log flushed.")
  end
end

-- Physical PRG table candidate mapped to CPU $DE86-$E01D only under the
-- bank-14-at-$C000 / fixed-bank-15-at-$E000 hypothesis.
memory.registerread(0xDE86, 0x198, function(address, size, value)
  emit("text_region_read", address, size, value)
end)

-- Mapper 69/FME-7 command/data writes: broad windows needed because the chip
-- decodes writes across $8000-$9FFF and $A000-$BFFF, not only one exact address.
memory.registerwrite(0x8000, 0x4000, function(address, size, value)
  emit("mapper_write", address, size, value)
end)

-- CPU-visible PPU registers ($2000-$2007). Use $2006/$2007 sequences to help
-- determine which tiles/addresses the renderer updates.
memory.registerwrite(0x2000, 0x0008, function(address, size, value)
  emit("ppu_register_write", address, size, value)
end)

-- A small stop marker when the script is manually stopped/reloaded may not
-- run on all FCEUX versions, so flush frequently while logging.
emu.message("Pyokotan trace active. Output: " .. TRACE_PATH)
