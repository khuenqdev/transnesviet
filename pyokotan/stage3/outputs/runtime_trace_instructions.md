# Runtime tracing for Pyokotan no Dai Meiro

This stage includes a FCEUX Lua watcher because static analysis cannot confirm the actual bank state, dialogue terminators, or which ROM bytes are read while a menu is displayed.

## Files

- `tools/pyokotan_fceux_text_trace.lua` — watches data reads from `$DE86-$E01D`, writes in the mapper address window `$8000-$BFFF`, and CPU writes to PPU registers `$2000-$2007`.
- `tools/trace_log_analyzer.py` — summarizes the CSV output.
- `outputs/bank_mapping_audit.json` — current mapping hypothesis and supporting vector/layout evidence.

## Capture procedure

1. Make a backup of the original ROM and open the original `pyokotan.nes` in FCEUX. The script only observes reads/writes; it does not patch the ROM.
2. Open FCEUX's Lua script window and load `tools/pyokotan_fceux_text_trace.lua`.
3. If FCEUX cannot create `pyokotan_runtime_trace.csv`, edit the `TRACE_PATH` variable near the top of the Lua file to an absolute path in a writable folder. Do not put the trace file inside a read-only program folder.
4. Start from power-on and reach the title/menu and then a screen containing Japanese text. Exercise each screen for a few seconds. The logger is capped at 100,000 rows and periodically flushes data.
5. Stop/reload the Lua script after capture. Run:

   ```sh
   python tools/trace_log_analyzer.py pyokotan_runtime_trace.csv \
       --out outputs/runtime_trace_summary.json \
       --filtered-csv outputs/runtime_trace_interesting.csv
   ```

6. Share the resulting CSV or the generated JSON/CSV reports for the next analysis pass.

## How to read the trace

- `text_region_read`: CPU read from the candidate fixed-width table address range. The current watcher assumes bank 14 is mapped at `$C000` and the fixed final bank is mapped at `$E000`.
- `mapper_write`: write to a CPU address between `$8000` and `$BFFF`, used by the FME-7 mapper. Address and value are preserved, but this simple analyzer does not yet infer each bank register's final state.
- `ppu_register_write`: CPU write to one of `$2000-$2007`; `$2006`/$`2007` sequences can help identify rendered tiles and VRAM addresses.

If the trace contains zero `text_region_read` events, that is inconclusive. It may mean the selected screen was not exercised, another bank/address mapping is active, or the candidate bytes are never read. Do not infer that a table is unused from a zero count alone.

## Current limitations

This logger has not been run in an emulator in the present environment. It is based on the documented FCEUX Lua API shape (`memory.registerread`, `memory.registerwrite`, `memory.getregister`, and `emu.framecount`). Check the FCEUX Lua console for API/version errors and send any error text with the captured output.
