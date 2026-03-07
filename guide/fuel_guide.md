# Fuel Bill Generator Guide

This guide explains how to generate fuel bills using the Bill Generator tool.

---

## Overview

The fuel bill generator reads transaction data from `input/fuel/source.json` and vendor/rate settings from `input/fuel/config.json`. It produces one PDF per transaction in the `output/fuel/` directory (configurable).

---

## Scripts

### `src/scripts/generate_fuel_bills.py` — Bulk generation *(Recommended)*

The main script. Reads all entries from `input/fuel/source.json` and generates a PDF for each one.

```bash
python src/scripts/generate_fuel_bills.py

# If using uv:
uv run python src/scripts/generate_fuel_bills.py
```

Output files are prefixed with a sequence number (e.g. `001_IOC-20250301-382910.pdf`) so they sort in source order.

---

### `src/scripts/generate_sample.py` — Single sample bill

Generates one hardcoded bill using template 1 and prints a summary to the console.

```bash
python src/scripts/generate_sample.py
```

---

### `src/scripts/generate_all_templates.py` — Template preview

Generates the same bill using all 3 template styles — useful for comparing branding layouts.

```bash
python src/scripts/generate_all_templates.py
```

---

## Input Files

### `input/fuel/source.json`

A JSON array where each object represents one transaction:

```json
[
  {
    "date": "2025-03-01 10:30:00",
    "amount": 500,
    "vehicle_type": "Bike",
    "address": "Ground Floor, Trinity Circle, Mahatma Gandhi Rd, Gowthamapuram, Jogupalya"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Transaction date-time in `YYYY-MM-DD HH:MM:SS` format |
| `amount` | int | Amount paid in ₹ |
| `vehicle_type` | string | One of the vehicle types defined in `config.json` (e.g. `"Bike"`, `"Car"`) |
| `address` | string | Station address string — must exactly match one entry in `config.json` |

---

### `input/fuel/config.json`

All vendor, rate, and output settings live here — no hardcoded values in scripts.

#### `vendor_meta`

Maps each provider to its template, density, fuel grade, GSTIN prefix, and station list.

```json
"vendor_meta": {
  "IndianOil": {
    "template_id": 1,
    "fuel_grade": "XtraPremium",
    "density": 0.741,
    "gstin_prefix": "29AABCU9603R1Z",
    "bill_prefix": "IOC",
    "footer_lines": ["Thank you for fuelling at Indian Oil"],
    "stations": [
      {
        "name": "IndianOil - Trinity Service Station",
        "address": "Ground Floor, Trinity Circle, ...",
        "address_parsed": {
          "line1": "Ground Floor, Trinity Circle",
          "line2": "Mahatma Gandhi Rd, Gowthamapuram, Jogupalya",
          "city": "Bengaluru",
          "state": "Karnataka",
          "pincode": "560008"
        },
        "gstin_suffix": "M",
        "phone": "094480 85101"
      }
    ]
  }
}
```

**Template IDs** correspond to PDF brand styles:

| `template_id` | Brand |
|---|---|
| `1` | Indian Oil (orange) |
| `2` | Hindustan Petroleum (blue) |
| `3` | Bharat Petroleum (yellow/red) |

#### `vehicle_numbers`

Maps `vehicle_type` values from `source.json` to actual registration numbers:

```json
"vehicle_numbers": {
  "Bike": "KA-05-JZ-1755",
  "Car":  "KA-01-MJ-5678"
}
```

#### `petrol_rates`

Monthly Bengaluru petrol prices (₹/litre). The script looks up the rate by `YYYY-MM` from the transaction date:

```json
"petrol_rates": {
  "monthly": {
    "2025-03": 102.92,
    "2025-04": 102.92
  },
  "default_before_2025": 102.92,
  "default_from_2026": 102.86
}
```

#### `output`

```json
"output": {
  "base_dir": "output/fuel",
  "subdir_by_provider": false
}
```

- `base_dir`: Where to write generated PDFs.
- `subdir_by_provider`: If `true`, creates sub-folders per provider (e.g. `output/fuel/IndianOil/`).

---

## Python API

You can also call the generator directly from Python:

```python
from billgen import generate_bill  # or: from billgen.generator import generate_bill

bill_data = {
    "bill_type": "fuel",
    "bill_number": "IOC-20260307-123456",
    "bill_date": "2026-03-07",
    "bill_time": "14:45:00",

    "vendor_name": "IndianOil - Trinity Service Station",
    "vendor_address": {
        "line1": "Ground Floor, Trinity Circle",
        "line2": "Mahatma Gandhi Rd, Gowthamapuram, Jogupalya",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560008"
    },
    "vendor_gstin": "29AABCU9603R1ZM",
    "vendor_phone": "094480 85101",

    "vehicle_number": "KA-05-JZ-1755",
    "fuel_type": "petrol",
    "fuel_grade": "XtraPremium",
    "nozzle_number": "4",
    "density_at_15c": 0.741,

    "items": [
        {
            "name": "Petrol (XtraPremium)",
            "quantity": 4.86,
            "unit": "litre",
            "rate": 102.86
        }
    ],
    "payment_mode": "upi",
    "transaction_id": "UPI/426713829164",
    "footer_lines": ["Thank you for fuelling at Indian Oil"]
}

output_path = generate_bill(
    data=bill_data,
    template_id=1,       # 1=IOC, 2=HP, 3=BPCL
    output_dir="output/fuel",
    filename="my_bill.pdf"   # Optional, auto-generated if omitted
)
```

---

## Data Fields Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `bill_type` | string | Must be `"fuel"` |
| `bill_number` | string | Invoice/receipt number |
| `bill_date` | string | Date in `YYYY-MM-DD` format |
| `vendor_name` | string | Petrol station name |
| `fuel_type` | string | `"petrol"`, `"diesel"`, `"cng"`, or `"ev"` |
| `items` | list | At least one item with `name`, `quantity`, `unit`, `rate` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `bill_time` | string | Time in `HH:MM:SS` format |
| `fuel_grade` | string | e.g. `"XtraPremium"`, `"Power 99"` |
| `nozzle_number` | string | Pump/nozzle identifier |
| `density_at_15c` | float | Fuel density (e.g. `0.741`) |
| `pump_reading_start` | float | Meter reading at start |
| `pump_reading_end` | float | Meter reading at end (must be > start) |
| `vehicle_number` | string | e.g. `"KA-05-JZ-1755"` |
| `payment_mode` | string | `"upi"`, `"cash"`, `"credit_card"`, `"debit_card"`, or `"wallet"` |
| `transaction_id` | string | UPI/card reference |
| `vendor_address` | dict | Keys: `line1`, `line2`, `city`, `state`, `pincode` |
| `vendor_gstin` | string | 15-character GSTIN |
| `vendor_phone` | string | Phone number |
| `footer_lines` | list[str] | Lines printed at the bottom of the receipt |

---

## Auto-calculated Fields

If not provided, these are computed automatically:

| Field | Formula |
|-------|---------|
| `amount` (per item) | `quantity × rate` |
| `subtotal` | Sum of all item amounts |
| `tax_amount` | `subtotal × tax_percent / 100` |
| `total_amount` | `subtotal + tax_amount − discount` |

---

## Output

PDFs are written to `output/fuel/` (or the `base_dir` from config). Each file is named:

```
{seq}_{bill_number}.pdf
```

e.g. `001_IOC-20250301-382910.pdf`

The numeric prefix ensures files sort in the same order as the source data regardless of bill number.
