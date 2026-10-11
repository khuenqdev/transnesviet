import argparse
import math
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library is not installed.")
    print("Please install it by running: pip install Pillow")
    sys.exit(1)

def encode_rom_to_image(rom_path, image_path):
    """Encodes an NES ROM into a lossless PNG image."""
    try:
        with open(rom_path, 'rb') as f:
            rom_data = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file {rom_path}")
        sys.exit(1)

    file_size = len(rom_data)
    
    # We prepend a 16-byte header to the data.
    # Bytes 0-3 store the original file size so we can decode it accurately.
    # Bytes 4-15 are zeros (padding).
    # We use exactly 16 bytes to ensure the NES internal data structures 
    # remain perfectly aligned visually in the image.
    header = file_size.to_bytes(4, byteorder='little') + b'\x00' * 12
    full_data = bytearray(header + rom_data)

    # A width of 256 is standard for NES and beautifully aligns 16-byte data chunks.
    width = 256
    height = math.ceil(len(full_data) / width)

    # Pad the end with zeros to complete the final row of pixels
    required_bytes = width * height
    full_data.extend(b'\x00' * (required_bytes - len(full_data)))

    # Create a Greyscale ('L') image where 1 byte = 1 pixel
    img = Image.frombytes('L', (width, height), bytes(full_data))
    
    # Save as PNG (Must be PNG. Lossy formats like JPG will corrupt the data)
    img.save(image_path, 'PNG')
    print(f"[+] Success! Encoded {file_size} bytes into {image_path}")
    print(f"[+] Image Dimensions: {width}x{height} pixels")

def decode_image_to_rom(image_path, rom_path):
    """Decodes the PNG image back into a fully playable NES ROM."""
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Could not find file {image_path}")
        sys.exit(1)
        
    # Ensure image is evaluated as greyscale bytes
    img = img.convert('L')
    full_data = img.tobytes()

    # Read original file size from the first 4 bytes of our custom header
    file_size = int.from_bytes(full_data[:4], byteorder='little')

    # Sanity check
    if file_size == 0 or file_size > len(full_data) - 16:
        print("Error: Image does not appear to contain valid ROM data encoded by this tool.")
        sys.exit(1)

    # Extract the original ROM, skipping the 16-byte header
    rom_data = full_data[16:16+file_size]

    with open(rom_path, 'wb') as f:
        f.write(rom_data)
        
    print(f"[+] Success! Restored {file_size} bytes to {rom_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert NES ROMs to Images and back.")
    parser.add_argument("mode", choices=['encode', 'decode'], help="Action: 'encode' (ROM to Image) or 'decode' (Image to ROM)")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("output", help="Output file path")
    
    args = parser.parse_args()
    
    if args.mode == 'encode':
        if not args.output.lower().endswith('.png'):
            print("Warning: Output image should be a .png file to prevent data loss!")
        encode_rom_to_image(args.input, args.output)
    else:
        decode_image_to_rom(args.input, args.output)

if __name__ == "__main__":
    main()