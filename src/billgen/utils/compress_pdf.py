#!/usr/bin/env python3
"""
PDF Compression Script
Compresses PDF files by reducing image quality and removing unnecessary data.
"""

import argparse
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False
        print("Error: pypdf or PyPDF2 not installed. Please install with: pip install pypdf")


def compress_pdf(input_path: str, output_path: str, compression_level: str = "medium"):
    """
    Compress a PDF file by reducing image quality and removing unnecessary data.
    
    Args:
        input_path: Path to the input PDF file
        output_path: Path to save the compressed PDF
        compression_level: Compression level - "low", "medium", or "high" (default: "medium")
    """
    if not PYPDF_AVAILABLE:
        print("Error: PDF processing library not available.")
        return False
    
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # Validate input file
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        return False
    
    if not input_file.is_file():
        print(f"Error: '{input_path}' is not a file.")
        return False
    
    if input_file.suffix.lower() != '.pdf':
        print(f"Error: Input file must be a PDF. Got: {input_file.suffix}")
        return False
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read the input PDF
        print(f"Reading PDF: {input_path}")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages to writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Set compression level
        if compression_level == "high":
            compression_quality = 30
        elif compression_level == "low":
            compression_quality = 75
        else:  # medium
            compression_quality = 50
        
        # Compress images in the PDF
        print(f"Compressing PDF with {compression_level} compression (quality: {compression_quality})...")
        for page in writer.pages:
            page.compress_content_streams()
            if hasattr(page, "images"):
                for img in page.images:
                    img.replace(img.image, quality=compression_quality)
        
        # Remove duplicate objects and compress
        writer.compress_identical_objects(remove_identicals=True)
        
        # Get file sizes
        input_size = input_file.stat().st_size
        
        # Write the compressed PDF
        with open(output_path, 'wb') as output_stream:
            writer.write(output_stream)
        
        output_size = output_file.stat().st_size
        
        # Calculate compression ratio
        compression_ratio = (1 - output_size / input_size) * 100
        
        print(f"✓ Compressed PDF saved to: {output_path}")
        print(f"  Original size: {input_size / 1024:.2f} KB")
        print(f"  Compressed size: {output_size / 1024:.2f} KB")
        print(f"  Reduction: {compression_ratio:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error compressing PDF: {e}")
        return False


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compress PDF files by reducing image quality and removing unnecessary data."
    )
    parser.add_argument(
        "input",
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "output",
        help="Path to save the compressed PDF file"
    )
    parser.add_argument(
        "-l", "--level",
        choices=["low", "medium", "high"],
        default="medium",
        help="Compression level: low (75%% quality), medium (50%% quality), high (30%% quality). Default: medium"
    )
    
    args = parser.parse_args()
    
    # Compress the PDF
    success = compress_pdf(args.input, args.output, args.level)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
