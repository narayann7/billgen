# Driver Bill Generator Guide

This guide explains how to generate monthly driver salary receipts using the Bill Generator tool.

---

## Overview

The driver bill generator reads monthly entries from `input/driver/source.json` and employer/driver settings from `input/driver/config.json`. It produces one A4 PDF per month in the `output/driver/` directory.

Each PDF contains two sections:
1. **Driver Salary Receipt** — the employer's certification of payment
2. **Receipt Acknowledgement** — the driver's signed acknowledgement

---

## Script

### `src/scripts/generate_driver_bills.py` — Bulk generation

```bash
python src/scripts/generate_driver_bills.py

# If using uv:
uv run python src/scripts/generate_driver_bills.py
```

Output files are prefixed with a sequence number (e.g. `001_DRV-202502-481293.pdf`) so they sort in source order.

---

## Input Files

### `input/driver/source.json`

A JSON array where each object represents one month's salary:

```json
[
  { "month": "2025-02" },
  { "month": "2025-03" },
  { "month": "2025-04", "amount": 1200 }
]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `month` | string | ✅ | Year-month in `YYYY-MM` format |
| `amount` | int | ❌ | Override monthly salary (₹). Falls back to `monthly_amount` in config if omitted. |

---

### `input/driver/config.json`

All employer, driver, and output settings:

```json
{
  "employee_name": "Narayan Reddy",
  "driver": {
    "name": "Saroj Kumar Sahu",
    "vehicle_number": "KA05JZ1755",
    "bill_prefix": "DRV",
    "monthly_amount": 900
  },
  "output": {
    "base_dir": "output/driver"
  }
}
```

| Field | Description |
|-------|-------------|
| `employee_name` | Owner/employer name shown on the receipt |
| `driver.name` | Driver's full name |
| `driver.vehicle_number` | Vehicle registration number |
| `driver.bill_prefix` | Prefix for auto-generated bill numbers (e.g. `"DRV"` → `DRV-202503-481293`) |
| `driver.monthly_amount` | Default salary per month in ₹ (can be overridden per entry in `source.json`) |
| `output.base_dir` | Directory where PDFs are written |

---

## Signature Image

The driver's signature is automatically embedded in the acknowledgement section if the file exists:

```
data/driver/signature.png
```

Place a PNG image of the driver's signature here. If the file is absent, the signature line is left blank.

---

## Python API

You can also call the generator directly from Python:

```python
from billgen import generate_bill  # or: from billgen.generator import generate_bill

bill_data = {
    "bill_type":      "driver",
    "bill_number":    "DRV-202503-481293",
    "bill_date":      "2025-03-31",
    "vendor_name":    "Narayan Reddy",      # employer name
    "salary_month":   "March",
    "salary_year":    2025,
    "driver_name":    "Saroj Kumar Sahu",
    "vehicle_number": "KA05JZ1755",
    "items": [
        {
            "name":     "Driver Salary for March 2025",
            "quantity": 1,
            "unit":     "month",
            "rate":     900
        }
    ]
}

output_path = generate_bill(
    data=bill_data,
    template_id=1,
    output_dir="output/driver",
    filename="march_2025.pdf"   # Optional
)
```

---

## Data Fields Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `bill_type` | string | Must be `"driver"` |
| `bill_number` | string | Receipt number |
| `bill_date` | string | Date in `YYYY-MM-DD` format (typically last day of month) |
| `vendor_name` | string | Employer/owner name |
| `salary_month` | string | Full month name, e.g. `"March"` |
| `salary_year` | int | Year, e.g. `2025` |
| `driver_name` | string | Driver's full name |
| `items` | list | One item with `name`, `quantity=1`, `unit="month"`, `rate=<amount>` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_number` | string | Vehicle registration shown on the receipt |
| `notes` | string | Additional remarks |

---

## Output

PDFs are written to `output/driver/` (or `base_dir` from config). Each file is named:

```
{seq}_{bill_number}.pdf
```

e.g. `001_DRV-202502-481293.pdf`

The numeric prefix ensures files sort in the same order as the source data, making it easy to merge them in chronological order.

---

## Merging into a Single PDF

After generating, you can combine all receipts into one file:

```bash
python src/billgen/utils/merge_pdf.py -i output/driver -o output/final/driver_salary_2025.pdf
```

See [`utility_guide.md`](utility_guide.md) for more details on merging and compression.
