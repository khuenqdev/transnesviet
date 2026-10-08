import argparse
import os
import glob
import json
from PIL import Image, ImageDraw, ImageFont

# Canonical NES 2C02 RGB Master Palette (64 Colors)
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

def render_8x8_tile(tile_bytes, palette_indices, scale=5):
    """Renders an 8x8 2bpp tile using the provided palette."""
    if len(tile_bytes) < 16:
        tile_bytes = tile_bytes + bytes(16 - len(tile_bytes))

    tile_img = Image.new("RGB", (8, 8))
    pixels = tile_img.load()

    for y in range(8):
        b0 = tile_bytes[y]
        b1 = tile_bytes[y + 8]
        for x in range(8):
            bit0 = (b0 >> (7 - x)) & 1
            bit1 = (b1 >> (7 - x)) & 1
            color_idx = (bit1 << 1) | bit0
            nes_color = palette_indices[color_idx]
            rgb = NES_PALETTE[nes_color & 0x3F]
            pixels[x, y] = rgb

    return tile_img.resize((8 * scale, 8 * scale), Image.NEAREST)

def build_nametable_sheet(json_path, output_img_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    bg_pattern_base = data.get("bg_pattern_base", 0)
    palette_ram = [int(x, 16) for x in data["palette"]]
    chr_bytes = bytes.fromhex(data["chr_hex"])
    nametables = data["nametables"]

    CARD_W = 138
    CARD_H = 265
    SPACING_X = 8
    ROW_HEADER_H = 32
    ROW_SPACING = 24
    PADDING = 16

    nt_rows = []
    max_cards = 0

    for nt in nametables:
        nt_idx = nt["index"]
        base_addr = nt["base"]
        tiles = [int(x, 16) for x in nt["tiles"]]
        attributes = [int(x, 16) for x in nt["attributes"]]

        unique_tiles = {}

        for r in range(30):
            for c in range(32):
                tile_id = tiles[r * 32 + c]
                if tile_id not in unique_tiles:
                    # Calculate attribute address & palette index
                    attr_r = r // 4
                    attr_c = c // 4
                    attr_index = attr_r * 8 + attr_c
                    attr_data = attributes[attr_index] if attr_index < len(attributes) else 0
                    attr_addr = base_addr + 0x3C0 + attr_index

                    sub_c = (c % 4) // 2
                    sub_r = (r % 4) // 2
                    shift = (sub_r * 2 + sub_c) * 2
                    palette_idx = (attr_data >> shift) & 0x03
                    pal_addr = 0x3F00 + palette_idx * 4

                    pal_indices = [
                        palette_ram[0] if palette_ram else 0,
                        palette_ram[palette_idx * 4 + 1] if len(palette_ram) > palette_idx * 4 + 1 else 0,
                        palette_ram[palette_idx * 4 + 2] if len(palette_ram) > palette_idx * 4 + 2 else 0,
                        palette_ram[palette_idx * 4 + 3] if len(palette_ram) > palette_idx * 4 + 3 else 0
                    ]

                    tile_ppu_addr = bg_pattern_base + tile_id * 16
                    tile_bytes = chr_bytes[tile_ppu_addr : tile_ppu_addr + 16] if tile_ppu_addr + 16 <= len(chr_bytes) else bytes(16)
                    tilemap_addr = base_addr + r * 32 + c

                    unique_tiles[tile_id] = {
                        "tile_id": tile_id,
                        "col": c, "row": r,
                        "x": c * 8, "y": r * 8,
                        "tilemap_addr": tilemap_addr,
                        "tile_ppu_addr": tile_ppu_addr,
                        "palette_idx": palette_idx,
                        "palette_addr": pal_addr,
                        "attr_addr": attr_addr,
                        "attr_data": attr_data,
                        "pal_indices": pal_indices,
                        "tile_bytes": tile_bytes
                    }

        sorted_tiles = [unique_tiles[k] for k in sorted(unique_tiles.keys())]
        nt_rows.append({
            "index": nt_idx,
            "base_addr": base_addr,
            "tiles": sorted_tiles
        })
        max_cards = max(max_cards, len(sorted_tiles))

    canvas_w = max(1024, max_cards * (CARD_W + SPACING_X) + PADDING * 2)
    row_h = ROW_HEADER_H + CARD_H
    canvas_h = PADDING * 2 + 4 * row_h + 3 * ROW_SPACING

    sheet = Image.new("RGB", (canvas_w, canvas_h), color=(0x17, 0x17, 0x17))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    curr_y = PADDING

    for row in nt_rows:
        nt_idx = row["index"]
        base_addr = row["base_addr"]
        tiles = row["tiles"]

        # Banner
        banner_text = f"=== Nametable {nt_idx} (${base_addr:04X}) === [{len(tiles)} Unique Tile{'s' if len(tiles) != 1 else ''}]"
        draw.rectangle([PADDING, curr_y, canvas_w - PADDING, curr_y + ROW_HEADER_H - 4], fill=(0x25, 0x25, 0x25))
        draw.text((PADDING + 10, curr_y + 8), banner_text, fill=(0xFF, 0xD7, 0x00), font=font)

        card_start_y = curr_y + ROW_HEADER_H

        if not tiles:
            draw.text((PADDING + 10, card_start_y + 15), "[EMPTY TABLE]", fill=(0x88, 0x88, 0x88), font=font)
        else:
            for idx, t in enumerate(tiles):
                cx = PADDING + idx * (CARD_W + SPACING_X)
                cy = card_start_y

                draw.rectangle([cx, cy, cx + CARD_W, cy + CARD_H], fill=(0x21, 0x21, 0x21), outline=(0x38, 0x38, 0x38))

                # Magnified tile preview
                tile_img = render_8x8_tile(t["tile_bytes"], t["pal_indices"], scale=5)
                tx = cx + (CARD_W - 40) // 2
                ty = cy + 10
                sheet.paste(tile_img, (tx, ty))
                draw.rectangle([tx - 1, ty - 1, tx + 40, ty + 40], outline=(0x55, 0x55, 0x55))

                # Palette Swatches
                swatch_y = ty + 46
                swatch_size = 11
                swatch_total_w = 4 * swatch_size
                swatch_x = cx + (CARD_W - swatch_total_w) // 2

                for p_i in range(4):
                    rgb = NES_PALETTE[t["pal_indices"][p_i] & 0x3F]
                    sx = swatch_x + p_i * swatch_size
                    draw.rectangle([sx, swatch_y, sx + swatch_size, swatch_y + swatch_size], fill=rgb, outline=(0, 0, 0))

                div_y = swatch_y + 16
                draw.line([(cx + 6, div_y), (cx + CARD_W - 6, div_y)], fill=(0x38, 0x38, 0x38))

                meta_y = div_y + 6
                lh = 13

                draw.text((cx + 8, meta_y + 0*lh), f"Col, Row: {t['col']}, {t['row']}", fill=(0xDD, 0xDD, 0xDD), font=font)
                draw.text((cx + 8, meta_y + 1*lh), f"X, Y: {t['x']}, {t['y']}", fill=(0xDD, 0xDD, 0xDD), font=font)
                draw.text((cx + 8, meta_y + 2*lh), f"Size: 8x8", fill=(0xAA, 0xAA, 0xAA), font=font)
                draw.text((cx + 8, meta_y + 3*lh), f"Tilemap: ${t['tilemap_addr']:04X}", fill=(0x98, 0xC3, 0x79), font=font)
                draw.text((cx + 8, meta_y + 4*lh), f"Tile idx: ${t['tile_id']:02X}", fill=(0xFF, 0xD7, 0x00), font=font)
                draw.text((cx + 8, meta_y + 5*lh), f"PPU Addr: ${t['tile_ppu_addr']:04X}", fill=(0x61, 0xAF, 0xEF), font=font)
                draw.text((cx + 8, meta_y + 6*lh), f"CHR Addr: ${t['tile_ppu_addr']:04X}", fill=(0x61, 0xAF, 0xEF), font=font)
                draw.text((cx + 8, meta_y + 7*lh), f"Palette: {t['palette_idx']} (${t['palette_addr']:04X})", fill=(0xE5, 0xC0, 0x7B), font=font)
                draw.text((cx + 8, meta_y + 8*lh), f"Attr: ${t['attr_data']:02X} (${t['attr_addr']:04X})", fill=(0xBE, 0x50, 0x46), font=font)

        curr_y += row_h + ROW_SPACING

    sheet.save(output_img_path)
    print(f"Generated Nametable sheet: {os.path.basename(output_img_path)}")

def main():
    parser = argparse.ArgumentParser(description="Generate Nametable Tile Inspection Sheets.")
    parser.add_argument("--capture-dir", required=True, help="Directory containing capture files")
    args = parser.parse_args()

    json_files = sorted(glob.glob(os.path.join(args.capture_dir, "*_ppu.json")))
    if not json_files:
        print(f"No '_ppu.json' files found in {args.capture_dir}.")
        return

    for jf in json_files:
        base_name = os.path.basename(jf).replace("_ppu.json", "")
        out_img = os.path.join(args.capture_dir, f"{base_name}_nametables.png")
        build_nametable_sheet(jf, out_img)

if __name__ == "__main__":
    main()