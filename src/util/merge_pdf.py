import argparse
from pathlib import Path
from pypdf import PdfWriter


def merge_pdfs(input_dir: str, output_path: str):
    """
    Finds all PDF files in input_dir, merges them in alphabetical order
    (which now matches chronological order due to numbered file prefixes),
    and saves the output to output_path.
    """
    input_path = Path(input_dir)
    out_path = Path(output_path)

    if not input_path.is_dir():
        print(f"Error: Input directory '{input_dir}' does not exist or is not a directory.")
        return

    # Create parent directories for output if they don't exist
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Glob all PDFs and sort alphabetically (relies on generation script numbering)
    pdf_files = sorted(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'")
        return

    merger = PdfWriter()

    print(f"Finding PDFs in {input_path}...")
    for pdf in pdf_files:
        try:
            merger.append(pdf)
            print(f"  Added: {pdf.name}")
        except Exception as e:
            print(f"  Failed to add {pdf.name}: {e}")

    try:
        merger.write(out_path)
        merger.close()
        print(f"\nSuccessfully merged {len(pdf_files)} PDFs into {out_path}")
    except Exception as e:
        print(f"\nError writing merged PDF to {out_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge all PDFs in a directory into a single PDF.")
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Path to the directory containing input PDFs"
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Path for the output merged PDF file"
    )

    args = parser.parse_args()
    merge_pdfs(args.input, args.output)
