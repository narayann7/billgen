# Utility Guide

This guide provides information on how to use the utility scripts located in `src/billgen/utils/`.

---

## Merge PDFs

**File:** `src/billgen/utils/merge_pdf.py`

Combines all PDF files inside a directory into a single PDF. Files are merged in alphabetical order based on their filenames (which matches chronological order when bills are prefixed with a sequence number).

### Usage

```bash
python src/billgen/utils/merge_pdf.py -i <input_directory> -o <output_pdf>

# If using uv:
uv run python src/billgen/utils/merge_pdf.py -i <input_directory> -o <output_pdf>
```

Any missing parent directories in the output path are created automatically.

### Example

```bash
# Merge all fuel bills into a single file
python src/billgen/utils/merge_pdf.py -i output/fuel -o output/final/fuel.pdf
```

### Arguments

| Argument         | Required | Description                                                   |
| ---------------- | -------- | ------------------------------------------------------------- |
| `-i`, `--input`  | Yes      | Directory containing the source PDFs                          |
| `-o`, `--output` | Yes      | Output path for the merged PDF (e.g. `output/final/fuel.pdf`) |

---

## Compress PDF

**File:** `src/billgen/utils/compress_pdf.py`

Reduces the file size of a single PDF by compressing embedded images and removing duplicate objects.

### Usage

```bash
python src/billgen/utils/compress_pdf.py <input_pdf> <output_pdf> [-l <level>]

# If using uv:
uv run python src/billgen/utils/compress_pdf.py <input_pdf> <output_pdf> [-l <level>]
```

### Compression Levels

| Level                | Image Quality | Flag        |
| -------------------- | ------------- | ----------- |
| `low`                | 75%           | `-l low`    |
| `medium` *(default)* | 50%           | `-l medium` |
| `high`               | 30%           | `-l high`   |

### Examples

```bash
# Compress with default (medium) level
python src/billgen/utils/compress_pdf.py output/final/fuel.pdf output/final/fuel_compressed.pdf

# Compress with high compression
python src/billgen/utils/compress_pdf.py output/final/fuel.pdf output/final/fuel_compressed.pdf -l high
```

### Arguments

| Argument        | Required | Description                                                       |
| --------------- | -------- | ----------------------------------------------------------------- |
| `input`         | Yes      | Path to the source PDF file                                       |
| `output`        | Yes      | Path to save the compressed PDF                                   |
| `-l`, `--level` | No       | Compression level: `low`, `medium`, or `high` (default: `medium`) |

---

## Compress Images

**File:** `src/billgen/utils/compress_images.py`

Batch-compresses PNG, JPEG, and (optionally) HEIC/HEIF images from an input directory into an output directory. The original directory structure is preserved. Requires `pillow-heif` to be installed for HEIC/HEIF support.

### Usage

```bash
python src/billgen/utils/compress_images.py <input_dir> <output_dir> [-q <quality>]

# If using uv:
uv run python src/billgen/utils/compress_images.py <input_dir> <output_dir> [-q <quality>]
```

### Supported Formats

- PNG (lossless, `compress_level=9`)
- JPEG / JPG (lossy, controlled by `--quality`)
- HEIC / HEIF (lossy, controlled by `--quality` — requires `pillow-heif`)

### Examples

```bash
# Compress all images with default quality (85)
python src/billgen/utils/compress_images.py data/fuel/logos data/fuel/logos_compressed

# Compress with lower quality for smaller files
python src/billgen/utils/compress_images.py data/fuel/logos data/fuel/logos_compressed -q 70
```

### Arguments

| Argument          | Required | Description                                               |
| ----------------- | -------- | --------------------------------------------------------- |
| `input_dir`       | Yes      | Source directory containing images (searched recursively) |
| `output_dir`      | Yes      | Destination directory for compressed images               |
| `-q`, `--quality` | No       | JPEG/HEIC quality from 1–100 (default: `85`)              |

---

## Images to PDF

**File:** `src/billgen/utils/images_to_pdf.py`

Converts all images in a directory to PDF. Supports two modes: merge all images into a single PDF, or produce one PDF per image. Requires `pillow-heif` for HEIC/HEIF support.

### Usage

```bash
python src/billgen/utils/images_to_pdf.py -i <input_dir> -o <output> [-m <mode>]

# If using uv:
uv run python src/billgen/utils/images_to_pdf.py -i <input_dir> -o <output> [-m <mode>]
```

### Modes

| Mode                 | Behaviour                      | Output path is…                             |
| -------------------- | ------------------------------ | ------------------------------------------- |
| `single` *(default)* | Merges all images into one PDF | A file path (e.g. `output/final/scans.pdf`) |
| `multiple`           | Creates one PDF per image      | A directory path (e.g. `output/scans/`)     |

### Supported Formats

PNG, JPG/JPEG, BMP, GIF, TIFF/TIF, WEBP, HEIC/HEIF (with `pillow-heif`)

### Examples

```bash
# Merge all images in a folder into one PDF
python src/billgen/utils/images_to_pdf.py -i data/scans -o output/final/scans.pdf

# Convert each image to its own PDF
python src/billgen/utils/images_to_pdf.py -i data/scans -o output/scans/ -m multiple
```

### Arguments

| Argument         | Required | Description                                                        |
| ---------------- | -------- | ------------------------------------------------------------------ |
| `-i`, `--input`  | Yes      | Directory containing source images                                 |
| `-o`, `--output` | Yes      | Output file path (single mode) or output directory (multiple mode) |
| `-m`, `--mode`   | No       | `single` (default) or `multiple`                                   |
