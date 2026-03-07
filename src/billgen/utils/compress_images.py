#!/usr/bin/env python3
"""
Image Compression Script
Compresses PNG, JPEG, and HEIC images from input directory to output directory.
"""

import argparse
import os
from pathlib import Path
from PIL import Image

# Try to import pillow_heif for HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False
    print("Warning: pillow-heif not installed. HEIC/HEIF support disabled.")


def compress_image(input_path: Path, output_path: Path, quality: int = 85):
    """
    Compress an image and save it to the output path.
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the compressed image
        quality: Compression quality (1-100, default 85)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if saving as JPEG
            if output_path.suffix.lower() in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Save with compression
            if output_path.suffix.lower() == '.png':
                img.save(output_path, 'PNG', optimize=True, compress_level=9)
            elif output_path.suffix.lower() in ['.jpg', '.jpeg']:
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
            elif output_path.suffix.lower() in ['.heic', '.heif']:
                img.save(output_path, 'HEIF', quality=quality)
            else:
                img.save(output_path, quality=quality, optimize=True)
            
            # Calculate compression ratio
            input_size = input_path.stat().st_size
            output_size = output_path.stat().st_size
            ratio = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
            
            print(f"✓ Compressed: {input_path.name}")
            print(f"  {input_size / 1024:.2f} KB → {output_size / 1024:.2f} KB ({ratio:.1f}% reduction)")
            
            return True
    except Exception as e:
        print(f"✗ Error compressing {input_path.name}: {str(e)}")
        return False


def compress_images_in_directory(input_dir: str, output_dir: str, quality: int = 85):
    """
    Compress all PNG, JPEG, and HEIC images in the input directory.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        quality: Compression quality (1-100)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Validate input directory
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory.")
        return
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported image extensions
    supported_extensions = {'.png', '.jpg', '.jpeg'}
    if HEIF_SUPPORT:
        supported_extensions.update({'.heic', '.heif'})
    
    # Find all images
    image_files = [
        f for f in input_path.rglob('*')
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not image_files:
        print(f"No supported images found in '{input_dir}'")
        print(f"Supported formats: PNG, JPEG, HEIC/HEIF")
        return
    
    print(f"\nFound {len(image_files)} image(s) to compress")
    print(f"Quality setting: {quality}")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for image_file in image_files:
        # Calculate relative path to maintain directory structure
        relative_path = image_file.relative_to(input_path)
        output_file = output_path / relative_path
        
        # Create subdirectories in output if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Compress the image
        if compress_image(image_file, output_file, quality):
            success_count += 1
        else:
            fail_count += 1
        print()
    
    print("-" * 60)
    print(f"\nCompression complete!")
    print(f"✓ Successful: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
    print(f"\nOutput directory: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description='Compress PNG, JPEG, and HEIC images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/input /path/to/output
  %(prog)s /path/to/input /path/to/output --quality 90
  %(prog)s ./images ./compressed_images -q 75
        """
    )
    
    parser.add_argument(
        'input_dir',
        help='Input directory containing images'
    )
    
    parser.add_argument(
        'output_dir',
        help='Output directory for compressed images'
    )
    
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='1-100',
        help='Compression quality for JPEG/HEIC (1-100, default: 85)'
    )
    
    args = parser.parse_args()
    
    compress_images_in_directory(args.input_dir, args.output_dir, args.quality)


if __name__ == '__main__':
    main()
