-- Mesen Capture Script (V8 - Universal Case-Insensitive PPU Resolver)
local capture_count = 0
local key_was_pressed = false

-- Log all available memory types in MesenCE for transparency
local function logAvailableMemoryTypes()
    if not emu.memType then
        emu.log("[Warning] emu.memType table is nil!")
        return
    end
    emu.log("=== Registered emu.memType in this Mesen build ===")
    for k, v in pairs(emu.memType) do
        emu.log(string.format("  emu.memType.%s = %s", tostring(k), tostring(v)))
    end
    emu.log("==================================================")
end

-- Case-insensitive search across all emu.memType keys
local function findMemoryType(patterns)
    if not emu.memType then return nil, "none" end
    for k, v in pairs(emu.memType) do
        local lower_k = string.lower(tostring(k))
        for _, pat in ipairs(patterns) do
            if string.find(lower_k, pat, 1, true) then
                return v, tostring(k)
            end
        end
    end
    return nil, "not_found"
end

-- Resolve the true PPU memory type by verifying it reads non-zero bytes from active VRAM
local function resolvePpuMemType()
    -- 1. Try common PPU/VRAM patterns
    local val, name = findMemoryType({"ppu", "vram", "videoram"})
    if val then
        -- Verify that reading VRAM or CHR returns real data
        local non_zero = 0
        for addr = 0x2000, 0x23BF, 16 do
            if (emu.read(addr, val) or 0) ~= 0 then non_zero = non_zero + 1 end
        end
        for addr = 0x0000, 0x1FFF, 128 do
            if (emu.read(addr, val) or 0) ~= 0 then non_zero = non_zero + 1 end
        end
        if non_zero > 0 then
            return val, name
        end
    end

    -- 2. Fallback: Test EVERY memory type in emu.memType to see which one reads VRAM
    for k, v in pairs(emu.memType) do
        local non_zero = 0
        for addr = 0x2000, 0x23BF, 16 do
            if (emu.read(addr, v) or 0) ~= 0 then non_zero = non_zero + 1 end
        end
        if non_zero > 0 then
            return v, tostring(k)
        end
    end

    return val, name
end

logAvailableMemoryTypes()

local function getTargetDirectory()
    local rom_info = emu.getRomInfo()
    local rom_path = (rom_info and rom_info.path) or ""
    local dir = rom_path:match("^(.*[/\\])") or ""
    local filename = rom_path:sub(#dir + 1)
    local rom_name = filename:match("^(.-)%.[^%.]+$") or filename
    if rom_name == "" then rom_name = "captures" end
    
    local is_windows = package.config:sub(1,1) == '\\'
    local sep = is_windows and "\\" or "/"
    local target_dir = dir .. rom_name .. sep
    
    if is_windows then
        os.execute('mkdir "' .. target_dir .. '" 2>nul')
    else
        os.execute('mkdir -p "' .. target_dir .. '" 2>/dev/null')
    end
    return target_dir, rom_name
end

local TARGET_DIR, ROM_NAME = getTargetDirectory()

local function dumpPpuState(json_path)
    local PPU_MEM, ppu_name = resolvePpuMemType()
    local PAL_MEM, pal_name = findMemoryType({"pal", "cgram"})
    local CHR_MEM, chr_name = findMemoryType({"chr"})

    emu.log(string.format("[Capture] Using PPU: emu.memType.%s | Palette: %s", tostring(ppu_name), tostring(pal_name)))

    -- 1. Read Palette RAM ($3F00 - $3F1F)
    local pal = {}
    for i = 0, 31 do
        local v = 0
        if PAL_MEM then v = emu.read(i, PAL_MEM) or emu.read(0x3F00 + i, PAL_MEM) or 0 end
        if v == 0 and PPU_MEM then v = emu.read(0x3F00 + i, PPU_MEM) or 0 end
        table.insert(pal, string.format("\"%02X\"", v))
    end

    -- 2. Read Active CHR Pattern Tables ($0000 - $1FFF = 8192 bytes)
    local chr_tbl = {}
    local mem_for_chr = PPU_MEM
    for a = 0, 0x1FFF do
        local b = emu.read(a, mem_for_chr) or 0
        table.insert(chr_tbl, string.format("%02X", b))
    end
    local chr_hex = table.concat(chr_tbl)

    -- If PPU read returned all zeroes for CHR, fall back to dedicated CHR type if available
    if string.match(chr_hex, "^0+$") and CHR_MEM then
        chr_tbl = {}
        for a = 0, 0x1FFF do
            local b = emu.read(a, CHR_MEM) or 0
            table.insert(chr_tbl, string.format("%02X", b))
        end
        chr_hex = table.concat(chr_tbl)
    end

    -- 3. Determine Background Pattern Table Base ($0000 or $1000)
    local bg_base = 0
    local state = emu.getState()
    if state then
        local p_addr = state["ppu.control.backgroundPatternAddr"] or state["ppu.control.bgPatternAddr"]
        if p_addr == 1 or p_addr == 4096 or p_addr == 0x1000 then
            bg_base = 0x1000
        elseif state["ppu.control"] then
            local c = state["ppu.control"]
            if type(c) == "number" and (c & 0x10) ~= 0 then
                bg_base = 0x1000
            end
        end
    end

    -- 4. Dump 4 Nametables (960 tile bytes + 64 attribute bytes each = 1024 bytes)
    local nts = {}
    for nt = 0, 3 do
        local base_addr = 0x2000 + (nt * 0x400)
        local t_tbl = {}
        for i = 0, 959 do
            local b = emu.read(base_addr + i, PPU_MEM) or 0
            table.insert(t_tbl, string.format("\"%02X\"", b))
        end
        local a_tbl = {}
        for i = 0, 63 do
            local b = emu.read(base_addr + 960 + i, PPU_MEM) or 0
            table.insert(a_tbl, string.format("\"%02X\"", b))
        end
        table.insert(nts, string.format([[{"index":%d,"base":%d,"tiles":[%s],"attributes":[%s]}]],
            nt, base_addr, table.concat(t_tbl, ","), table.concat(a_tbl, ",")))
    end

    local json_content = string.format([[{"bg_pattern_base":%d,"palette":[%s],"chr_hex":"%s","nametables":[%s]} ]],
        bg_base, table.concat(pal, ","), chr_hex, table.concat(nts, ","))

    local jf = io.open(json_path, "w")
    if jf then
        jf:write(json_content)
        jf:close()
    end
end

function captureData()
    capture_count = capture_count + 1
    local prefix = string.format("%scapture_%03d", TARGET_DIR, capture_count)
    local png_path = prefix .. ".png"
    local json_path = prefix .. "_ppu.json"

    local png_data = emu.takeScreenshot()
    if png_data then
        local img_file = io.open(png_path, "wb")
        if img_file then
            img_file:write(png_data)
            img_file:close()
        end
    end

    dumpPpuState(json_path)

    emu.displayMessage("Captured #" .. capture_count, "Saved to " .. ROM_NAME .. "/")
    emu.log(string.format("[Capture #%03d] Saved PNG & PPU JSON to %s", capture_count, TARGET_DIR))
end

local function onFrame()
    local is_pressed = emu.isKeyPressed("Q")
    if is_pressed and not key_was_pressed then
        captureData()
        key_was_pressed = true
    elseif not is_pressed then
        key_was_pressed = false
    end
end

emu.addEventCallback(onFrame, emu.eventType.endFrame)
emu.displayMessage("Script", "V8 Ready! Press 'Q' to capture.")