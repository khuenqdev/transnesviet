import argparse
import os
import json
import re

def load_table(tbl_path):
    table = {}
    with open(tbl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('/') or '=' not in line:
                continue
            h, c = line.split('=', 1)
            c = " " if c == "[SPACE]" else c
            table[h.upper()] = c
    return table

def extract_clean_screen_text(json_path, tbl_path, output_path):
    table = load_table(tbl_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nametables = data["nametables"]
    extracted_lines = []

    for nt in nametables:
        nt_idx = nt["index"]
        base_addr = nt["base"]
        tiles = nt["tiles"]

        for r in range(30):
            row_tiles = tiles[r * 32 : (r + 1) * 32]
            
            # Decode the 32-tile row
            decoded_chars = [table.get(t.upper(), ".") for t in row_tiles]
            raw_text = "".join(decoded_chars)

            # Strip leading/trailing spaces and filler dots
            stripped_text = raw_text.strip(" .")

            # Check if row contains genuine text (at least 2 letters or numbers)
            letters = [c for c in stripped_text if c.isalnum() or c in "©-:.,!?'\""]
            if len(letters) >= 2:
                # Find the start and end column of the text
                start_c = raw_text.find(stripped_text[0])
                end_c = start_c + len(stripped_text)
                
                text_tiles = row_tiles[start_c:end_c]
                ppu_addr = base_addr + r * 32 + start_c

                extracted_lines.append({
                    "nt": nt_idx,
                    "row": r,
                    "ppu_addr": ppu_addr,
                    "text": stripped_text,
                    "hex": " ".join(text_tiles),
                    "length": len(text_tiles)
                })

    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"=== EXTRACTED SCREEN SCRIPT (PPU STREAM) ===\n")
        out.write(f"Source: {os.path.basename(json_path)} | Table: {os.path.basename(tbl_path)}\n\n")

        for line in extracted_lines:
            out.write(f"Nametable {line['nt']} [Row {line['row']:02d} | PPU ${line['ppu_addr']:04X}] | Length: {line['length']} bytes\n")
            out.write(f"Text: {line['text']}\n")
            out.write(f"Hex : {line['hex']}\n")
            out.write("-" * 55 + "\n")

    print(f"Success! Extracted {len(extracted_lines)} clean screen lines to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract clean text from PPU Nametable JSON snapshot.")
    parser.add_argument("json_file", help="Path to capture_xxx_ppu.json")
    parser.add_argument("tbl_file", help="Path to .tbl mapping file")
    parser.add_argument("-o", "--output", default="screen_script.txt", help="Output text file")
    args = parser.parse_args()

    extract_clean_screen_text(args.json_file, args.tbl_file, args.output)