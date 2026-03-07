# Fuel Bill Generator Guide

This guide explains how to generate fuel bills using the Bill Generator tool.

## Overview

The Bill Generator allows you to generate PDF fuel bills by providing a structured dictionary of data and passing it to the `generate_bill` function along with a chosen template ID.

## How to Generate a Fuel Bill

### 1. Using Python Scripts

You can use the provided scripts to generate bills. There are two primary ways currently set up in the repository:

**Generate a single sample bill (`generate_sample.py`)**:
This script generates a bill using template ID 1 and outputs some details to the console.
```bash
python generate_sample.py
```

**Generate all templates (`generate_all_templates.py`)**:
This script will iterate over all available template IDs (1, 2, 3) and output a PDF for each.
```bash
python generate_all_templates.py
```

### 2. Basic Example

Here is a basic example of how to configure the `bill_data` block:

```python
from src.generator import generate_bill

bill_data = {
    "bill_type": "fuel",
    "bill_number": "INV-2026-034871",
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
    
    "vehicle_number": "KA-01-MJ-5678",
    "customer_name": "Narayan",
    
    "fuel_type": "petrol",
    "fuel_grade": "XtraPremium",
    "nozzle_number": "4",
    "density_at_15c": 0.741,
    
    "items": [
        {
            "name": "Petrol (XtraPremium)",
            "quantity": 30.00,
            "unit": "litre",
            "rate": 102.86
        }
    ],
    "payment_mode": "upi",
    "transaction_id": "UPI/426713829164"
}

output_path = generate_bill(
    data=bill_data,
    template_id=1,        # 1, 2, or 3
    output_dir="output/fuel",
    filename="my_bill.pdf"  # Optional
)
```

## Data Fields Explanation

The `bill_data` dictionary maps to the `FuelBillData` schema (which inherits from `BillData`). Here are the key fields you need:

### Required Fields 
(These are common back-bone fields required for the base generator, minus auto-calculated totals)

- `bill_type`: Should always be `"fuel"`.
- `bill_number`: Invoice number string (e.g. `"INV-2026-034871"`).
- `bill_date`: Transaction date (format `"YYYY-MM-DD"`).
- `vendor_name`: Name of the station (e.g. `"IndianOil"`).
- `items`: A list containing at least one line item dictionary.
    - `name` (string)
    - `quantity` (float)
    - `unit` (string: typically `"litre"`, `"kg"`, or `"unit"`)
    - `rate` (float)
- `fuel_type`: Can be `"petrol"`, `"diesel"`, `"cng"`, or `"ev"`.

### Optional/Specific Fields for Fuel

- `fuel_grade`: String for the grade of fuel like `"Power 99"`, `"XtraPremium"`.
- `nozzle_number`: Pump identifier string.
- `density_at_15c`: Float value (e.g. `0.741`) commonly printed on Indian fuel bills.
- `pump_reading_start` / `pump_reading_end`: Floats representing starting and ending meter blocks. `end` must be strictly greater than `start`.
- `vehicle_number`: Very useful in fuel billing (e.g. `"KA-01-MJ-5678"`). *Note: Generates a warning if skipped.*
- `bill_time`: Format `"HH:MM:SS"`.
- `payment_mode`: e.g. `"upi"`, `"cash"`, `"credit_card"`, `"debit_card"`, `"wallet"`. Defaults to `"cash"`.
- `transaction_id`: Usually the UPI or Card reference number.
- `vendor_address`: Dictionary with `line1`, `line2`, `city`, `state`, `pincode`.
- `vendor_gstin`: String representing the 15-character GSTIN.
- `vendor_phone`: Phone number string.

## Auto-calculated Fields

If not provided, the total amounts are auto-calculated:
- `amount` (on item level) = `quantity` × `rate`
- `subtotal` = Sum of all `amount`s
- `tax_amount` = `subtotal` × `tax_percent` / 100
- `total_amount` = `subtotal` + `tax_amount` - `discount`

## Output Generation

The files generated default to `output_dir`.
Currently supported templates: `template_id` `1`, `2`, and `3`. Each will render a different styled PDF.
