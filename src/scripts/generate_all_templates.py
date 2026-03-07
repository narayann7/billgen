"""Generate fuel bills with all 3 templates for verification.

Run from the project root:
    python src/generate_all_templates.py
"""

import sys
from pathlib import Path

# Add src/ to path so 'billgen.*' imports resolve correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from billgen.generator import generate_bill

# Same bill data, different templates
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

for template_id in [1, 2, 3]:
    path = generate_bill(
        data=bill_data,
        template_id=template_id,
        output_dir="output/fuel",
        filename=f"template_{template_id}.pdf",
    )
    print(f"✅ Template {template_id}: {path}")
