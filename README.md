# Bill Generator

A modular Python tool for generating PDF bills, receipts, and salary documents.

## Bill Types

| Type | Script | Description |
|------|--------|-------------|
| **Fuel** | `src/scripts/generate_fuel_bills.py` | Petrol-pump receipts (IndianOil, HP, BPCL templates) |
| **Driver** | `src/scripts/generate_driver_bills.py` | Monthly driver salary receipts with signature |

## Quick Start

```bash
# Install dependencies (using uv)
uv sync

# Generate fuel bills from source data
python src/scripts/generate_fuel_bills.py

# Generate driver salary receipts
python src/scripts/generate_driver_bills.py

# Generate a single sample fuel bill
python src/scripts/generate_sample.py

# Preview all 3 template styles side-by-side
python src/scripts/generate_all_templates.py
```

## Project Structure

```
bill gen/
├── src/
│   ├── billgen/                     # Core library package
│   │   ├── __init__.py              # Public API: from billgen import generate_bill
│   │   ├── generator.py             # generate_bill() orchestrator
│   │   ├── renderer.py              # PDF rendering (fuel receipt + driver salary)
│   │   ├── models/
│   │   │   ├── base.py              # BillData base model, BillItem, enums
│   │   │   ├── fuel.py              # FuelBillData model
│   │   │   └── driver.py            # DriverSalaryData model
│   │   └── utils/
│   │       ├── merge_pdf.py         # Merge PDFs in a directory
│   │       ├── compress_pdf.py      # Compress a single PDF
│   │       ├── compress_images.py   # Batch compress PNG/JPEG/HEIC images
│   │       └── images_to_pdf.py     # Convert images to PDF
│   └── scripts/
│       ├── generate_fuel_bills.py   # Bulk fuel bill generator (data-driven)
│       ├── generate_driver_bills.py # Driver salary receipt generator
│       ├── generate_sample.py       # Single sample fuel bill
│       └── generate_all_templates.py# Preview all 3 fuel template styles
│
├── input/
│   ├── fuel/
│   │   ├── source.json              # Transaction records (date, amount, vehicle, address)
│   │   └── config.json              # Vendors, petrol rates, vehicle numbers, output dir
│   └── driver/
│       ├── source.json              # Monthly salary entries (YYYY-MM format)
│       └── config.json              # Employee, driver name, vehicle, monthly amount
│
├── output/
│   ├── fuel/                        # Generated fuel PDFs
│   └── driver/                      # Generated driver salary PDFs
│
└── data/
    ├── fuel/logos/                  # Brand logos for fuel templates (logo_1/2/3.png)
    └── driver/signature.png         # Driver's signature image for receipts
```

## Using the Library API

```python
from billgen import generate_bill   # or: from billgen.generator import generate_bill

output_path = generate_bill(
    data={...},        # bill_data dict (see guides)
    template_id=1,     # 1=IndianOil, 2=HP, 3=BPCL
    output_dir="output/fuel",
)
```

## Utility Scripts

Run standalone from the project root:

```bash
# Merge all PDFs in a folder into one file
python src/billgen/utils/merge_pdf.py -i output/fuel -o output/final/fuel.pdf

# Compress a PDF
python src/billgen/utils/compress_pdf.py output/final/fuel.pdf output/final/fuel_compressed.pdf

# Batch-compress images
python src/billgen/utils/compress_images.py data/fuel/logos data/fuel/logos_out

# Convert images to PDF
python src/billgen/utils/images_to_pdf.py -i data/scans -o output/final/scans.pdf
```

See [`guide/utility_guide.md`](guide/utility_guide.md) for full argument reference.

## Guides

- [`guide/fuel_guide.md`](guide/fuel_guide.md) — Fuel bill configuration, data fields, and examples
- [`guide/driver_guide.md`](guide/driver_guide.md) — Driver salary receipt configuration and usage
- [`guide/utility_guide.md`](guide/utility_guide.md) — Utility scripts reference

## Dependencies

- **Python** ≥ 3.10 · managed with [`uv`](https://github.com/astral-sh/uv)
- `pydantic` — data validation and modelling
- `reportlab` — PDF generation
- `pypdf` — PDF merging
- `pillow` + `pillow-heif` — image processing (logos, signatures, HEIC support)