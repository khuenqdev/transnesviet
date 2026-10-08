import argparse
import os

def search_text_in_rom(rom_path, script_path):
    with open(rom_path, 'rb') as f:
        rom_data = f.read()

    print(f"Scanning ROM ({os.path.basename(rom_path)}) for extracted text sequences...\n")

    current_text = None
    current_hex = None
    matches_found = 0

    with open(script_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Text:"):
                current_text = line.replace("Text:", "").strip()
            elif line.startswith("Hex :"):
                current_hex = line.replace("Hex :", "").strip()
                
                if current_text and current_hex:
                    # Clean tokens
                    hex_bytes = bytes.fromhex(current_hex)
                    
                    # 1. Search for full string
                    offset = rom_data.find(hex_bytes)
                    
                    # 2. If full string not found, search without spaces (words only)
                    if offset == -1 and len(hex_bytes) > 6:
                        # Search for longest word chunk (e.g. "RESERVED" or "NAMCO")
                        words = current_hex.split(" 10 ")
                        for w in words:
                            w_bytes = bytes.fromhex(w)
                            if len(w_bytes) >= 4:
                                w_off = rom_data.find(w_bytes)
                                if w_off != -1:
                                    print(f"[PARTIAL MATCH] Word '{current_text}' found at File Offset: 0x{w_off:06X}")
                                    print(f"  ROM Bytes: {w}")
                                    matches_found += 1
                                    break
                    else:
                        if offset != -1:
                            print(f"[EXACT MATCH] \"{current_text}\" found at File Offset: 0x{offset:06X}")
                            print(f"  Length: {len(hex_bytes)} bytes | ROM Hex: {current_hex}")
                            matches_found += 1
                        else:
                            print(f"[NOT FOUND] \"{current_text}\" (May be compressed or procedurally drawn)")

                    current_text = None
                    current_hex = None

    print(f"\nDone. Located {matches_found} text blocks in the ROM.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Locate extracted screen text inside the ROM binary.")
    parser.add_argument("rom_file", help="Path to .nes ROM file")
    parser.add_argument("script_file", help="Path to galaxian_clean.txt")
    args = parser.parse_args()

    search_text_in_rom(args.rom_file, args.script_file)