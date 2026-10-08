import argparse
import os
import glob
import json
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

# Canonical NES 2C02 RGB Master Palette
NES_PALETTE = [
    (0x66, 0x66, 0x66), (0x00, 0x2A, 0x88), (0x14, 0x12, 0xA7), (0x3B, 0x00, 0xA4),
    (0x5C, 0x00, 0x7E), (0x6E, 0x00, 0x40), (0x6C, 0x06, 0x00), (0x56, 0x1D, 0x00),
    (0x33, 0x35, 0x00), (0x0B, 0x48, 0x00), (0x00, 0x52, 0x00), (0x00, 0x4F, 0x08),
    (0x00, 0x40, 0x4D), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xAD, 0xAD, 0xAD), (0x15, 0x5F, 0xD9), (0x42, 0x40, 0xFF), (0x75, 0x27, 0xFE),
    (0xA0, 0x1A, 0xCC), (0xB7, 0x1E, 0x7B), (0xB5, 0x31, 0x20), (0x99, 0x4E, 0x00),
    (0x6B, 0x6D, 0x00), (0x38, 0x87, 0x00), (0x0C, 0x93, 0x00), (0x00, 0x8F, 0x32),
    (0x00, 0x7C, 0x8D), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xFF, 0xFF, 0xFF), (0x64, 0xB0, 0xFF), (0x92, 0x90, 0xFF), (0xC6, 0x76, 0xFF),
    (0xF3, 0x6A, 0xFF), (0xFE, 0x6E, 0xCC), (0xFE, 0x81, 0x70), (0xEA, 0x9E, 0x22),
    (0xBC, 0xBE, 0x00), (0x88, 0xD8, 0x00), (0x5C, 0xE4, 0x30), (0x45, 0xE0, 0x82),
    (0x48, 0xCD, 0xDE), (0x4F, 0x4F, 0x4F), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
    (0xFF, 0xFF, 0xFF), (0xC0, 0xDF, 0xFF), (0xD3, 0xD2, 0xFF), (0xE8, 0xC8, 0xFF),
    (0xFB, 0xC2, 0xFF), (0xFE, 0xC4, 0xEA), (0xFE, 0xCC, 0xC5), (0xF7, 0xD8, 0xA5),
    (0xE4, 0xE5, 0x94), (0xCF, 0xEF, 0x96), (0xBD, 0xF4, 0xAB), (0xB3, 0xF3, 0xCC),
    (0xB5, 0xEB, 0xF2), (0xB8, 0xB8, 0xB8), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00)
]

def render_tile_pix(tile_bytes, pal_indices, scale=4):
    """Renders 8x8 tile with palette and magnifies it."""
    if len(tile_bytes) < 16:
        tile_bytes = tile_bytes + bytes(16 - len(tile_bytes))
    img = Image.new("RGB", (8, 8))
    pix = img.load()
    for y in range(8):
        b0 = tile_bytes[y]
        b1 = tile_bytes[y + 8]
        for x in range(8):
            bit0 = (b0 >> (7 - x)) & 1
            bit1 = (b1 >> (7 - x)) & 1
            color_idx = (bit1 << 1) | bit0
            nes_color = pal_indices[color_idx]
            pix[x, y] = NES_PALETTE[nes_color & 0x3F]
    return img.resize((8 * scale, 8 * scale), Image.NEAREST)

def build_compact_payload(capture_dir, rom_path=None):
    json_files = sorted(glob.glob(os.path.join(capture_dir, "*_ppu.json")))
    if not json_files:
        print(f"Error: No '_ppu.json' files found in {capture_dir}")
        return

    all_unique_glyphs = {}
    dialogue_lines_text = []
    space_candidates = Counter()
    screenshot_paths = []
    rom_search_keys = []

    for jf in json_files:
        base_name = os.path.basename(jf).replace("_ppu.json", "")
        img_p = os.path.join(capture_dir, f"{base_name}.png")
        if os.path.exists(img_p):
            screenshot_paths.append(img_p)

        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bg_base = data.get("bg_pattern_base", 0)
        palette_ram = [int(x, 16) for x in data["palette"]]
        chr_bytes = bytes.fromhex(data["chr_hex"])
        nametables = data["nametables"]

        # 1. Identify dominant background filler byte across this screen
        all_screen_tiles = []
        for nt in nametables:
            all_screen_tiles.extend([int(x, 16) for x in nt["tiles"]])
        screen_bg_byte = Counter(all_screen_tiles).most_common(1)[0][0]

        # 2. Extract dialogue rows from active Nametables
        screen_lines = []
        for nt in nametables:
            tiles = [int(x, 16) for x in nt["tiles"]]
            attrs = [int(x, 16) for x in nt["attributes"]]
            base_addr = nt["base"]

            for r in range(30):
                row_tiles = tiles[r * 32 : (r + 1) * 32]
                non_bg = [t for t in row_tiles if t != screen_bg_byte]
                
                # A dialogue row typically has between 4 and 28 non-filler tiles
                if 4 <= len(non_bg) <= 28:
                    start_c = next(i for i, t in enumerate(row_tiles) if t != screen_bg_byte)
                    end_c = len(row_tiles) - next(i for i, t in enumerate(reversed(row_tiles)) if t != screen_bg_byte)
                    line_chunk = row_tiles[start_c:end_c]
                    
                    screen_lines.append(line_chunk)
                    
                    # Track unique glyphs and calculate attributes
                    for col_idx, tile_id in enumerate(line_chunk, start=start_c):
                        attr_r = r // 4
                        attr_c = col_idx // 4
                        attr_idx = attr_r * 8 + attr_c
                        attr_data = attrs[attr_idx] if attr_idx < len(attrs) else 0
                        
                        shift = (((r % 4) // 2) * 2 + ((col_idx % 4) // 2)) * 2
                        pal_idx = (attr_data >> shift) & 0x03
                        
                        pal_indices = [
                            palette_ram[0] if palette_ram else 0,
                            palette_ram[pal_idx * 4 + 1] if len(palette_ram) > pal_idx * 4 + 1 else 0,
                            palette_ram[pal_idx * 4 + 2] if len(palette_ram) > pal_idx * 4 + 2 else 0,
                            palette_ram[pal_idx * 4 + 3] if len(palette_ram) > pal_idx * 4 + 3 else 0
                        ]

                        tile_ppu_addr = bg_base + tile_id * 16
                        tile_bytes = chr_bytes[tile_ppu_addr : tile_ppu_addr + 16] if tile_ppu_addr + 16 <= len(chr_bytes) else bytes(16)

                        # Detect if tile is completely solid (potential space)
                        if len(set(tile_bytes)) == 1:
                            space_candidates[f"{tile_id:02X}"] += 1

                        if tile_id not in all_unique_glyphs:
                            all_unique_glyphs[tile_id] = {
                                "bytes": tile_bytes,
                                "pal": pal_indices,
                                "hex": f"{tile_id:02X}"
                            }

        if screen_lines:
            dialogue_lines_text.append((base_name, screen_lines))
            # Save first line for ROM search
            rom_search_keys.append([f"{t:02X}" for t in screen_lines[0]])

    # Auto-detect Space tile
    space_tile = "3F"
    if space_candidates:
        space_tile = space_candidates.most_common(1)[0][0]

    # --- BUILD IMAGE: ai_multimodal_reference.png ---
    # Top: Thumbnails of screenshots (up to 4 key panels)
    # Bottom: Unique Glyph Dictionary
    sample_images = [Image.open(p).convert("RGB") for p in screenshot_paths[:4]]
    thumb_w, thumb_h = 256, 240
    thumbs_per_row = min(len(sample_images), 2)
    top_rows = (len(sample_images) + thumbs_per_row - 1) // thumbs_per_row if thumbs_per_row else 1
    
    header_h = 24
    top_section_w = max(512, thumbs_per_row * thumb_w)
    top_section_h = top_rows * (thumb_h + header_h) if sample_images else 0

    # Glyph Grid: 8 columns, 32x32 tiles with labels
    glyph_list = [all_unique_glyphs[k] for k in sorted(all_unique_glyphs.keys())]
    cols = 8
    glyph_cell_w = 64
    glyph_cell_h = 56
    glyph_rows = (len(glyph_list) + cols - 1) // cols
    glyph_section_h = glyph_rows * glyph_cell_h + 40
    
    canvas_w = max(top_section_w, cols * glyph_cell_w + 20)
    canvas_h = top_section_h + glyph_section_h + 20

    sheet = Image.new("RGB", (canvas_w, canvas_h), color=(0x18, 0x18, 0x18))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    # Draw Thumbnails
    curr_y = 10
    if sample_images:
        for idx, img in enumerate(sample_images):
            r, c = idx // thumbs_per_row, idx % thumbs_per_row
            tx = c * thumb_w + 10
            ty = curr_y + r * (thumb_h + header_h)
            draw.rectangle([tx, ty, tx + thumb_w, ty + header_h], fill=(0x25, 0x25, 0x25))
            draw.text((tx + 6, ty + 6), f"Reference Screenshot [{idx+1}]", fill=(0xFF, 0xD7, 0x00), font=font)
            sheet.paste(img.resize((thumb_w, thumb_h), Image.NEAREST), (tx, ty + header_h))
        curr_y += top_section_h + 10

    # Draw Glyph Catalog Banner
    draw.rectangle([10, curr_y, canvas_w - 10, curr_y + 26], fill=(0x25, 0x25, 0x25))
    draw.text((16, curr_y + 6), f"=== UNIQUE DIALOGUE GLYPHS (${len(glyph_list)} Tiles) ===", fill=(0x61, 0xAF, 0xEF), font=font)
    curr_y += 34

    # Draw Glyph Cells
    for idx, g in enumerate(glyph_list):
        r, c = idx // cols, idx % cols
        gx = 10 + c * glyph_cell_w
        gy = curr_y + r * glyph_cell_h

        # Hex code label
        draw.text((gx + 14, gy), f"${g['hex']}", fill=(0xFF, 0xD7, 0x00), font=font)
        # Rendered 32x32 tile
        tile_render = render_tile_pix(g["bytes"], g["pal"], scale=4)
        sheet.paste(tile_render, (gx + 16, gy + 14))
        draw.rectangle([gx + 15, gy + 13, gx + 16 + 32, gy + 14 + 32], outline=(0x44, 0x44, 0x44))

    out_image_path = os.path.join(capture_dir, "ai_multimodal_reference.png")
    sheet.save(out_image_path)
    print(f"Generated visual reference: {os.path.basename(out_image_path)}")

    # --- BUILD TEXT PROMPT: ai_compact_prompt.txt ---
    # Extract CPU ROM gaps if ROM file is provided
    rom_transitions = []
    if rom_path and os.path.exists(rom_path):
        with open(rom_path, 'rb') as rf:
            rom_data = rf.read()
        for i in range(len(rom_search_keys) - 1):
            k1 = "".join(rom_search_keys[i][:6])
            k2 = "".join(rom_search_keys[i+1][:6])
            s1 = bytes.fromhex(k1)
            s2 = bytes.fromhex(k2)
            pos1 = rom_data.find(s1)
            if pos1 != -1:
                pos2 = rom_data.find(s2, pos1)
                if pos2 != -1 and (pos2 - (pos1 + len(s1))) <= 24:
                    gap = rom_data[pos1 + len(s1) : pos2].hex(" ").upper()
                    rom_transitions.append(f"Between Line [{i+1}] and [{i+2}]: ROM Gap Bytes = [{gap}]")

    out_prompt_path = os.path.join(capture_dir, "ai_compact_prompt.txt")
    with open(out_prompt_path, 'w', encoding='utf-8') as pf:
        pf.write("[CRITICAL: Do NOT execute Python code or use tools. Reason directly in text.]\n\n")
        pf.write("You are an expert retro ROM hacker creating an NES character mapping table (.tbl).\n")
        pf.write("I have uploaded 'ai_multimodal_reference.png'. It shows the game screen on top, and an isolated, magnified catalog of all unique dialogue glyphs with their Hex IDs on the bottom.\n\n")
        
        pf.write(f"=== KNOWN BASELINE ===\n")
        pf.write(f"{space_tile}=[SPACE]  (Solid blank tile separating words)\n\n")

        pf.write("=== ACTIVE DIALOGUE TEXT STREAMS ===\n")
        pf.write("Below are the exact lines of dialogue extracted from memory. Compare these sequences to the screenshots in the image to read full sentences:\n\n")
        for s_idx, (name, lines) in enumerate(dialogue_lines_text, 1):
            pf.write(f"[{name}]\n")
            for l_i, l_tokens in enumerate(lines, 1):
                hex_str = " ".join([f"{t:02X}" for t in l_tokens])
                pf.write(f"  Line {l_i}: {hex_str}\n")
            pf.write("\n")

        if rom_transitions:
            pf.write("=== CPU ROM MEMORY GAPS (CONTROL CODES) ===\n")
            pf.write("The exact bytes between these dialogue lines in the ROM binary:\n")
            for t in rom_transitions:
                pf.write(f"- {t}\n")
            pf.write("\n")

        pf.write("=== YOUR TASK ===\n")
        pf.write("1. Look at each glyph in 'ai_multimodal_reference.png' (e.g. $0A, $21, $25). Identify its character (distinguish UPPERCASE, lowercase, and punctuation).\n")
        pf.write("2. Analyze the ROM Gap Bytes to deduce control codes: [NEWLINE], [WAIT_INPUT], [CLEAR_BOX], and timers [DELAY_x].\n")
        pf.write("3. Output ONLY the complete .tbl mapping file. Format: XX=Char or XX=[CODE]. Do not add conversational text.\n")

    print(f"Generated compact prompt: {os.path.basename(out_prompt_path)}")
    print("\n-------------------------------------------------------------")
    print("DONE! Upload ONLY these 2 tiny files to Gemini:")
    print(f"1. Image : ai_multimodal_reference.png")
    print(f"2. Prompt: ai_compact_prompt.txt (or paste into chat)")
    print("-------------------------------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Ultra-Compact Multimodal Payload for LLMs.")
    parser.add_argument("--capture-dir", required=True, help="Directory containing captures")
    parser.add_argument("--rom", help="Optional path to .nes ROM for automatic control code extraction")
    args = parser.parse_args()
    build_compact_payload(args.capture_dir, args.rom)