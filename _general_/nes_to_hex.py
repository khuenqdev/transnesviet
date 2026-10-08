import argparse
import os

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

def parse_ines_header(header):
    """Parses the 16-byte iNES header of the ROM."""
    if len(header) < 16 or header[0:4] != b'NES\x1a':
        return None, "Invalid or missing iNES header. File might not be an NES ROM."

    prg_banks = header[4]
    chr_banks = header[5]
    prg_size = prg_banks * 16384
    chr_size = chr_banks * 8192
    flags6 = header[6]
    flags7 = header[7]
    mapper = (flags7 & 0xF0) | ((flags6 & 0xF0) >> 4)
    has_trainer = bool(flags6 & 4)
    
    info_str = (
        f"=== NES ROM Metadata (iNES Format) ===\n"
        f"PRG ROM (Code/Data): {prg_banks} banks x 16KB ({prg_size} bytes)\n"
        f"CHR ROM (Graphics) : {chr_banks} banks x 8KB ({chr_size} bytes)\n"
        f"Mapper Number      : {mapper}\n"
        f"Mirroring          : {'Vertical' if flags6 & 1 else 'Horizontal'}\n"
        f"Battery RAM (Save) : {'Yes' if flags6 & 2 else 'No'}\n"
        f"Trainer Present    : {'Yes' if has_trainer else 'No'}\n"
        f"======================================\n\n"
    )
    
    metadata = {
        'prg_size': prg_size,
        'chr_size': chr_size,
        'has_trainer': has_trainer,
        'info_str': info_str
    }
    
    return metadata, None

def create_hex_dump(data, start_address=0):
    """Yields formatted hex dump lines."""
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join((chr(b) if 32 <= b <= 126 else '.') for b in chunk)
        yield f"{start_address + i:08X}: {hex_str:<47} | {ascii_str}\n"

def export_chr_to_image(chr_data, output_path):
    """Decodes NES 2bpp CHR data and saves it as a PNG sprite sheet."""
    num_tiles = len(chr_data) // 16
    tiles_per_row = 16
    num_rows = (num_tiles + tiles_per_row - 1) // tiles_per_row
    
    width = tiles_per_row * 8
    height = num_rows * 8
    
    img = Image.new('RGB', (width, height), color='black')
    pixels = img.load()
    
    # Standard Grayscale Palette for CHR extraction (Black, Dark Gray, Light Gray, White)
    palette = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
    
    for i in range(num_tiles):
        tile_bytes = chr_data[i*16 : i*16+16]
        if len(tile_bytes) < 16:
            break
            
        tile_x = (i % tiles_per_row) * 8
        tile_y = (i // tiles_per_row) * 8
        
        for y in range(8):
            b1 = tile_bytes[y]
            b2 = tile_bytes[y+8]
            for x in range(8):
                bit0 = (b1 >> (7 - x)) & 1
                bit1 = (b2 >> (7 - x)) & 1
                color_idx = bit0 | (bit1 << 1)
                
                pixels[tile_x + x, tile_y + y] = palette[color_idx]
                
    # Scale 2x using Nearest Neighbor so it's clearer for humans and AI vision
    img = img.resize((width * 2, height * 2), Image.NEAREST)
    img.save(output_path)
    return os.path.basename(output_path)

def main():
    parser = argparse.ArgumentParser(description="Convert NES ROM to LLM context (Hex Dump + CHR Image).")
    parser.add_argument("input_file", help="Path to the input .nes ROM file")
    parser.add_argument("-o", "--output", help="Path to the output .txt file")
    parser.add_argument("--code-only", action="store_true", 
                        help="Extract ONLY the PRG-ROM (code/data) to save LLM context tokens.")
    parser.add_argument("--export-chr", action="store_true",
                        help="Export the CHR-ROM graphics as a PNG image sheet.")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    base_name = os.path.splitext(input_path)[0]
    output_txt = args.output if args.output else f"{base_name}_hexdump.txt"
    output_img = f"{base_name}_sprites.png"

    try:
        with open(input_path, 'rb') as f:
            rom_data = f.read()

        metadata, error = parse_ines_header(rom_data[:16])
        
        with open(output_txt, 'w', encoding='utf-8') as out_f:
            if error:
                out_f.write("Warning: No valid iNES header detected.\n\n")
                dump_data = rom_data
                start_addr = 0
            else:
                out_f.write(metadata['info_str'])
                
                prg_start = 16 + (512 if metadata['has_trainer'] else 0)
                prg_end = prg_start + metadata['prg_size']
                chr_start = prg_end
                chr_end = chr_start + metadata['chr_size']

                # Handle CHR Export
                if args.export_chr:
                    if metadata['chr_size'] == 0:
                        print("Notice: This ROM uses CHR-RAM (0 bytes CHR-ROM). No image exported.")
                    elif not HAS_PILLOW:
                        print("Error: The 'Pillow' library is required for --export-chr.")
                        print("Please run: pip install Pillow")
                        return
                    else:
                        print("Exporting CHR-ROM to image...")
                        chr_data = rom_data[chr_start:chr_end]
                        img_filename = export_chr_to_image(chr_data, output_img)
                        print(f"Graphics saved to: {img_filename}")
                        
                        # Add coordinate mapping instructions to the text file for the LLM
                        mapping_instructions = (
                            f"=== CHR-ROM (Graphics) Reference ===\n"
                            f"The graphics payload has been excluded from the hex dump to save tokens.\n"
                            f"Instead, it has been provided to you as an image file: {img_filename}\n\n"
                            f"To modify a specific graphic tile, use the following formula to find its address:\n"
                            f"- CHR-ROM Start Offset in ROM : 0x{chr_start:08X}\n"
                            f"- Image Grid Layout           : 16 tiles per row\n"
                            f"- Bytes per Tile              : 16 bytes (8x8 pixels, 2bpp NES format)\n\n"
                            f"Formula: Address = 0x{chr_start:08X} + (Row_Index * 16 + Column_Index) * 16\n"
                            f"(Note: Row and Column indices start at 0 from the top-left of the image)\n"
                            f"====================================\n\n"
                        )
                        out_f.write(mapping_instructions)

                # Determine hex dump payload
                if args.code_only:
                    print("Writing PRG-ROM (Code/Data) Hex Dump...")
                    dump_data = rom_data[prg_start:prg_end]
                    start_addr = prg_start 
                    out_f.write(f"--- HEX DUMP (PRG-ROM ONLY, offset 0x{prg_start:04X}) ---\n")
                else:
                    print("Writing Full ROM Hex Dump...")
                    dump_data = rom_data
                    start_addr = 0
                    out_f.write("--- HEX DUMP (FULL ROM) ---\n")

            for line in create_hex_dump(dump_data, start_address=start_addr):
                out_f.write(line)

        print(f"Success! Hex dump saved to: {output_txt}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()