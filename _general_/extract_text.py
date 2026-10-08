import argparse
import os
import re
from collections import Counter

def load_table_file(tbl_path):
    """Loads a Thingy format .tbl file, supporting multi-byte hex sequences."""
    table = {}
    try:
        with open(tbl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '=' not in line or line.startswith('/'):
                    continue
                    
                hex_str, char = line.split('=', 1)
                try:
                    hex_bytes = tuple(int(b, 16) for b in hex_str.split())
                    table[hex_bytes] = char
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"Error: Table file '{tbl_path}' not found.")
        return None
        
    return dict(sorted(table.items(), key=lambda item: len(item[0]), reverse=True))

def clean_text_for_evaluation(raw_text):
    """Strips tags like [SPACE], [END], etc., to evaluate true visible text content."""
    # Strip any tag enclosed in [] or {}
    clean = re.sub(r'\[.*?\]|\{.*?\}', '', raw_text)
    return clean.strip()

def is_genuine_dialogue(clean_text, min_letters=3):
    """
    Heuristic filter that distinguishes genuine human text from
    6502 opcodes, padding, and math lookup tables.
    """
    if len(clean_text) == 0:
        return False

    # 1. Must contain at least `min_letters` alphabetic letters or Japanese Kana
    letters = [c for c in clean_text if c.isalpha() or '\u3040' <= c <= '\u30ff']
    if len(letters) < min_letters:
        return False

    # 2. Entropy check: Reject strings where one character dominates (e.g. "000000", "AAAAAA")
    counts = Counter(clean_text)
    most_common_count = counts.most_common(1)[0][1]
    if (most_common_count / len(clean_text)) > 0.60:
        return False

    # 3. Pattern check: Reject 2-character repeating opcode loops (e.g. "STSTSTST", "202020")
    if len(set(clean_text)) <= 2 and len(clean_text) >= 6:
        return False

    # 4. Reject strings dominated by numbers/symbols rather than text (e.g. math tables)
    if (len(letters) / len(clean_text)) < 0.35:
        return False

    return True

def scan_rom_for_text(rom_data, table, min_length=4, min_letters=3):
    """Greedy scanning with anti-garbage heuristic filters."""
    extracted_strings = []
    current_string = ""
    current_start_addr = -1
    current_bytes = []
    
    terminators = ["[END]", "[EOF]", "[STOP]", "[CLOSE]"]
    
    addr = 0
    rom_len = len(rom_data)
    
    while addr < rom_len:
        match_found = False
        
        for hex_seq, char in table.items():
            seq_len = len(hex_seq)
            
            if addr + seq_len <= rom_len:
                if tuple(rom_data[addr:addr+seq_len]) == hex_seq:
                    if current_start_addr == -1:
                        current_start_addr = addr
                        
                    current_string += char
                    current_bytes.extend(hex_seq)
                    
                    match_found = True
                    addr += seq_len
                    
                    if char in terminators:
                        clean_text = clean_text_for_evaluation(current_string)
                        if len(clean_text) >= min_length and is_genuine_dialogue(clean_text, min_letters):
                            extracted_strings.append((current_start_addr, current_string, current_bytes))
                        
                        current_string = ""
                        current_start_addr = -1
                        current_bytes = []
                    break
        
        if not match_found:
            if current_start_addr != -1:
                clean_text = clean_text_for_evaluation(current_string)
                if len(clean_text) >= min_length and is_genuine_dialogue(clean_text, min_letters):
                    extracted_strings.append((current_start_addr, current_string, current_bytes))
                    
                current_string = ""
                current_start_addr = -1
                current_bytes = []
                
            addr += 1

    return extracted_strings

def main():
    parser = argparse.ArgumentParser(description="Extract genuine dialogue text from an NES ROM (V3 - Heuristic Filter).")
    parser.add_argument("rom_file", help="Path to the NES ROM file")
    parser.add_argument("tbl_file", help="Path to the .tbl table file")
    parser.add_argument("-o", "--output", help="Output text file", default="extracted_script.txt")
    parser.add_argument("--min", type=int, default=4, help="Minimum visible text length (default: 4)")
    parser.add_argument("--min-letters", type=int, default=3, help="Minimum actual alphabetic letters required (default: 3)")
    parser.add_argument("--start", type=lambda x: int(x, 16), help="Start hex offset (e.g. 0x1000)")
    parser.add_argument("--end", type=lambda x: int(x, 16), help="End hex offset (e.g. 0x4000)")
    
    args = parser.parse_args()

    table = load_table_file(args.tbl_file)
    if not table:
        return

    try:
        with open(args.rom_file, 'rb') as f:
            rom_data = f.read()

        # Skip 16-byte iNES header
        prg_data = rom_data[16:]
        
        if args.start is not None or args.end is not None:
            s = (args.start - 16) if args.start else 0
            e = (args.end - 16) if args.end else len(prg_data)
            prg_data = prg_data[max(0, s):min(len(prg_data), e)]
            offset_bias = max(0, s) + 16
        else:
            offset_bias = 16

        print(f"Scanning ROM with anti-garbage filters (min length: {args.min}, min letters: {args.min_letters})...")
        strings = scan_rom_for_text(prg_data, table, min_length=args.min, min_letters=args.min_letters)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"=== EXTRACTED NES SCRIPT ===\n")
            f.write(f"Table used: {os.path.basename(args.tbl_file)}\n\n")
            
            for addr, text, byte_seq in strings:
                true_addr = addr + offset_bias
                byte_len = len(byte_seq)
                
                f.write(f"Address: 0x{true_addr:08X} | Max Bytes Allowed: {byte_len}\n")
                f.write(f"Original: {text}\n")
                f.write(f"Hex     : {' '.join(f'{b:02X}' for b in byte_seq)}\n")
                f.write("-" * 45 + "\n")

        print(f"Success! Extracted {len(strings)} genuine text blocks to {args.output}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()