# Utility Guide

This guide provides information on how to use various utility scripts included in the project.

## Merge PDFs

The utility script `merge_pdf.py` allows you to combine multiple PDF files located within a specific directory into a single PDF output. The PDFs will be appended in alphabetical order based on their filenames.

### File Location

The script is located at: `src/util/merge_pdf.py`

### Usage

The script requires an input directory containing the PDFs to merge, and an output path indicating where the single compiled PDF will be saved. Any non-existing parent directories in the output path will automatically be created.

```bash
# General usage
python src/util/merge_pdf.py -i <path_to_input_directory> -o <path_to_output_pdf>

# If using uv, run with:
uv run python src/util/merge_pdf.py -i <path_to_input_directory> -o <path_to_output_pdf>
```

### Examples

**Example (Fuel Bills):**

To merge all PDF fuel bills generated inside the `output/fuel/` folder into a single PDF at `output/final/fuel.pdf`:

```bash
python src/util/merge_pdf.py -i output/fuel -o output/final/fuel.pdf
```

### Arguments Overview

- `-i`, `--input`: **(Required)** Path of the directory which has the source PDFs.
- `-o`, `--output`: **(Required)** Path for the final output file (e.g., `output/final/fuel.pdf`).
