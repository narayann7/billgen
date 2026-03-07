"""Quick smoke test for the data models."""

import json
import sys
sys.path.insert(0, ".")

from src.models.fuel import FuelBillData

# Sample JSON input — what a user would provide to generate a bill
sample_input = {
    "bill_type": "fuel",
    "bill_number": "INV-2026-00142",
    "bill_date": "2026-03-07",
    "bill_time": "14:30:00",
    "vendor_name": "Bharat Petroleum - Highway Station",
    "vendor_address": {
        "line1": "NH-48, Near Toll Plaza",
        "city": "Pune",
        "state": "Maharashtra",
        "pincode": "411001",
    },
    "vendor_gstin": "27AABCU9603R1ZP",
    "vehicle_number": "MH-12-AB-1234",
    "customer_name": "Narayan",
    "fuel_type": "petrol",
    "fuel_grade": "Power 99",
    "nozzle_number": "3",
    "density_at_15c": 0.745,
    "items": [
        {
            "name": "Petrol (Power 99)",
            "quantity": 25.50,
            "unit": "litre",
            "rate": 104.45,
        }
    ],
    "payment_mode": "upi",
    "transaction_id": "UPI/426713829164",
}

# 1. Create from dict
bill = FuelBillData(**sample_input)

print("✅ Model created successfully!")
print(f"   Bill ID   : {bill.bill_id}")
print(f"   Bill #    : {bill.bill_number}")
print(f"   Fuel Type : {bill.fuel_type.value}")
print(f"   Quantity  : {bill.items[0].quantity} {bill.items[0].unit}")
print(f"   Rate      : ₹{bill.items[0].rate}")
print(f"   Item Amt  : ₹{bill.items[0].amount}")
print(f"   Subtotal  : ₹{bill.subtotal}")
print(f"   Tax       : ₹{bill.tax_amount} ({bill.tax_percent}%)")
print(f"   Total     : ₹{bill.total_amount}")
print()

# 2. Validate domain rules
bill.validate_domain_rules()
print("✅ Domain rules passed!")
print()

# 3. Template context
ctx = bill.to_template_context()
print("✅ Template context generated:")
for k, v in ctx.items():
    if k != "items":
        print(f"   {k:25s} = {v}")
print()

# 4. JSON round-trip
json_str = bill.to_json()
bill2 = FuelBillData.from_json(json_str)
assert bill2.bill_number == bill.bill_number
assert bill2.total_amount == bill.total_amount
print("✅ JSON round-trip passed!")
print()

# 5. Validation error test
print("Testing validation (pump_reading_end < start)...")
try:
    bad = sample_input.copy()
    bad["pump_reading_start"] = 1000.0
    bad["pump_reading_end"] = 500.0
    FuelBillData(**bad)
    print("❌ Should have raised an error!")
except ValueError as e:
    print(f"✅ Correctly caught: {e}")

print("\n🎉 All tests passed!")
