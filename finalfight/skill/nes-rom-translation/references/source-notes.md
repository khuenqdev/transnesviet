# Source and Method Notes

## Project-derived facts

The Mighty Final Fight case-study facts in `mighty-final-fight-case-study.md` were derived from the supplied Step 20 project files, notably the README, translation plan, `.tbl`, pointer table, full translation catalog, scope report, build script, validation log, and independent validator. The guide does not infer that text outside the catalog has been translated.

## External technical reference

STONE BOAT, “Contra và Kontora” (Vietnamese article). Relevant transferable concepts include examining the game's actual text/PPU writing routine, using a logical mapping from an accented character to base glyph plus separately placed marks, handling characters with both an upper and lower mark, and using a bank-aware jump to a validated free area rather than shifting existing code addresses. This article is not the source of Mighty Final Fight's pointer values or mapper operations.

https://sites.google.com/view/sfc65816/famicom-nes/contra-v%C3%A0-kontora?authuser=0

## Mapper/debugger background references

- FCEUX Lua functions: https://fceux.com/web/help/LuaFunctionsList.html
- FCEUX 2.6.6 changes (for optional memory read callback availability): https://fceux.com/web/help/WhatsNew266.html
- NES 2.0: https://www.nesdev.org/wiki/NES_2.0
- MMC3: https://www.nesdev.org/wiki/MMC3

Validate current tool behavior and game-specific facts against the installed emulator/build and trace. A documentation page or a prior project's trace does not replace testing the target ROM.
