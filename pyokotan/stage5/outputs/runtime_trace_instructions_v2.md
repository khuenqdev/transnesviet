# Pyokotan runtime trace capture (FCEUX) — v2

This procedure captures runtime evidence needed to validate the character table and identify the game's text-rendering route. The logger is read-only.

## Files

- `tools/pyokotan_fceux_text_trace_v2.lua` — watches CPU reads in `$DE86-$E01D`, Mapper 69 command/parameter writes, PRG bank registers, CHR bank registers, and PPU register writes including the approximate PPU address written through `$2007`.
- `tools/trace_log_analyzer_v2.py` — processes the capture into summary JSON and a CSV of `$2007` writes with estimated CHR tile addresses.
- `outputs/pyokotan_chr_tile_inventory_v5.csv` and `reference/chr_tiles_*.png` — visual/byte references for mapping observed tile reads and writes.

## Capture steps

1. Make a separate copy of the original ROM for experimentation and open `pyokotan.nes` in FCEUX.
2. Open the FCEUX Lua Script window and load `pyokotan_fceux_text_trace_v2.lua`.
3. The default output is `pyokotan_runtime_trace_v2.csv` in the Lua script's working directory. If file creation fails, edit `TRACE_PATH` to an absolute path in a writable folder.
4. Start from power-on. Let the title screen appear; exercise the menu; then visit text-bearing screens. Allow a few seconds per screen.
5. Stop the Lua script after capture. If the script reaches the 200,000-row cap, it flushes and closes the CSV.
6. Analyze it from a terminal:

   ```sh
   python tools/trace_log_analyzer_v2.py pyokotan_runtime_trace_v2.csv --outdir outputs/runtime_analysis
   ```

7. Keep these generated files: `runtime_analysis/pyokotan_runtime_trace_summary_v2.json`, `runtime_analysis/pyokotan_text_read_bank_context_v2.json`, and `runtime_analysis/pyokotan_ppu_tile_writes_v2.csv`.

## How to interpret the events

- `text_region_read`: a CPU read in the candidate table/trailer span. The snapshot includes the observed raw PRG `$C000-$DFFF` bank parameter if the script has seen command `$0B`.
- `mapper_command_write`: the command value written in `$8000-$9FFF`.
- `mapper_parameter_write`: the parameter written in `$A000-$BFFF`; `mapper_register` shows which command was selected. Commands 0–7 update CHR bank state; 9–11 update the three switchable PRG bank values.
- `ppu_register_write`: CPU write to `$2000-$2007`. For `$2007`, `ppu_addr_write_target` is the logger's estimated PPU address before the write. When the target is a nametable address `$2000-$2FFF`, the analyzer derives a possible pattern-table tile and physical CHR offset using PPUCTRL and the currently observed CHR bank.

## Caveats

- This is a trace helper, not a guarantee that every PPU access is observed correctly. The estimated PPU address latch can lose alignment if writes are missed or the game uses unusual PPU access patterns.
- A blank CHR bank state means the script has not observed a corresponding mapper write yet, not necessarily that the hardware bank is zero.
- A zero count for candidate text-region reads does not prove that the table is unused; the active bank, scene, or address assumptions may differ.
- The fixed table's 2-byte trailers remain unexplained. Do not edit them as strings/pointers based only on shape.
