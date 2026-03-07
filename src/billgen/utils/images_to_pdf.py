#!/usr/bin/env python3
"""
Images to PDF Conversion Script
Converts all images in a directory into a single or multiple PDF files.
"""

import argparse
from pathlib import Path
from PIL import Image

# Try to import pillow_heif for HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False


def images_to_pdf(input_dir: str, output_path: str, mode: str = "single"):
    """
    Convert all images in input_dir to PDF(s).
    
    Args:
        input_dir: Directory containing images
        output_path: Path to save the PDF (for single mode) or directory (for multiple mode)
        mode: "single" to merge all images into one PDF, "multiple" for one PDF per image
    """
    input_path = Path(input_dir)
    out_path = Path(output_path)

    if not input_path.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is not a directory.")
        return

    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
    if HEIF_SUPPORT:
        image_extensions.update({'.heic', '.heif'})

    # Find all image files and sort them
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f"*{ext}"))
        image_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    image_files = sorted(set(image_files))

    if not image_files:
        print(f"No image files found in '{input_dir}'")
        print(f"Supported formats: {', '.join(sorted(image_extensions))}")
        return

    print(f"Found {len(image_files)} image(s) in {input_path}")

    if mode == "single":
        _merge_images_to_single_pdf(image_files, out_path)
    else:
        _convert_images_to_multiple_pdfs(image_files, out_path)


def _merge_images_to_single_pdf(image_files: list[Path], output_path: Path):
    """
    Merge all images into a single PDF file.
    
    Args:
        image_files: List of image file paths
        output_path: Path to save the merged PDF
    """
    # Create parent directories for output if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    converted_images = []
    
    print("\nConverting images to PDF...")
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            
            # Convert to RGB mode if necessary (PDF doesn't support all modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            converted_images.append(img)
            print(f"  Added: {img_path.name}")
        except Exception as e:
            print(f"  Failed to process {img_path.name}: {e}")

    if not converted_images:
        print("\nNo images could be processed.")
        return

    try:
        # Save the first image and append the rest
        if len(converted_images) == 1:
            converted_images[0].save(output_path, 'PDF', resolution=100.0)
        else:
            converted_images[0].save(
                output_path, 
                'PDF', 
                resolution=100.0, 
                save_all=True, 
                append_images=converted_images[1:]
            )
        
        print(f"\nSuccessfully merged {len(converted_images)} image(s) into {output_path}")
        
        # Close all images
        for img in converted_images:
            img.close()
            
    except Exception as e:
        print(f"\nError writing PDF to {output_path}: {e}")


def _convert_images_to_multiple_pdfs(image_files: list[Path], output_dir: Path):
    """
    Convert each image to a separate PDF file.
    
    Args:
        image_files: List of image file paths
        output_dir: Directory to save the PDF files
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nConverting images to individual PDFs...")
    success_count = 0
    
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            
            # Convert to RGB mode if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create output filename
            output_path = output_dir / f"{img_path.stem}.pdf"
            img.save(output_path, 'PDF', resolution=100.0)
            img.close()
            
            print(f"  Created: {output_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  Failed to convert {img_path.name}: {e}")

    print(f"\nSuccessfully converted {success_count}/{len(image_files)} image(s) to PDF(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert images to PDF(s). Merges all images into one PDF by default."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input directory containing images"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output path (file for single mode, directory for multiple mode)"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["single", "multiple"],
        default="single",
        help="'single' to merge all images into one PDF (default), 'multiple' for one PDF per image"
    )

    args = parser.parse_args()
    images_to_pdf(args.input, args.output, args.mode)
