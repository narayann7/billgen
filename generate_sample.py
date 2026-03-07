"""Generate a fuel bill for IndianOil - Trinity Service Station."""

import sys
sys.path.insert(0, ".")

from src.generator import generate_bill

# Bill data from IndianOil - Trinity Service Station, Bengaluru
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

# Generate using Template 1 (IndianOil style)
output_path = generate_bill(
    data=bill_data,
    template_id=1,
    output_dir="output/fuel",
)

print(f"✅ Bill generated: {output_path}")
print(f"   Size: {output_path.stat().st_size:,} bytes")

# Also show the model data
from src.models.fuel import FuelBillData
bill = FuelBillData(**bill_data)
print(f"\n📋 Bill Summary:")
print(f"   Bill #     : {bill.bill_number}")
print(f"   Station    : {bill.vendor_name}")
print(f"   Vehicle    : {bill.vehicle_number}")
print(f"   Fuel       : {bill.fuel_type.value.title()} ({bill.fuel_grade})")
print(f"   Quantity   : {bill.items[0].quantity} {bill.items[0].unit}")
print(f"   Rate       : ₹{bill.items[0].rate}/litre")
print(f"   Total      : ₹{bill.total_amount}")
print(f"   Payment    : {bill.payment_mode.value.upper()}")
print(f"   Trans ID   : {bill.transaction_id}")
