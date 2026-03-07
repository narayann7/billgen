"""
Generate driver salary receipt PDFs from input/driver/source.json.

All configuration is loaded from input/driver/config.json.

Each source entry maps to one monthly DriverSalaryData payload and is
rendered as an A4 PDF into output/driver/.
"""

import sys
import json
import hashlib
import calendar
from pathlib import Path
from datetime import date

sys.path.insert(0, ".")
from src.generator import generate_bill

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

CONFIG_PATH = Path("input/driver/config.json")

with open(CONFIG_PATH) as _f:
    _CFG = json.load(_f)

_MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bill_number(prefix: str, year: int, month: int, amount: int) -> str:
    key = f"{prefix}{year}{month:02d}{amount}"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    suffix = str(h % 900000 + 100000)
    return f"{prefix}-{year}{month:02d}-{suffix}"


def last_day_of_month(year: int, month: int) -> date:
    last = calendar.monthrange(year, month)[1]
    return date(year, month, last)


# ---------------------------------------------------------------------------
# Bill data builder
# ---------------------------------------------------------------------------

def build_bill_data(entry: dict) -> dict:
    """Return bill_data dict for one source entry."""
    year, month = map(int, entry["month"].split("-"))
    amount = entry["amount"]

    driver_cfg = _CFG["driver"]
    employee   = _CFG["employee_name"]
    month_name = _MONTH_NAMES[month]
    bill_date  = last_day_of_month(year, month)
    bill_num   = bill_number(driver_cfg["bill_prefix"], year, month, amount)

    return {
        "bill_type":       "driver",
        "bill_number":     bill_num,
        "bill_date":       bill_date.isoformat(),
        "vendor_name":     employee,
        "salary_month":    month_name,
        "salary_year":     year,
        "driver_name":     driver_cfg["name"],
        "vehicle_number":  driver_cfg["vehicle_number"],
        "items": [
            {
                "name":     f"Driver Salary for {month_name} {year}",
                "quantity": 1,
                "unit":     "month",
                "rate":     amount,
            }
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    source_path = Path("input/driver/source.json")
    output_base = Path(_CFG["output"]["base_dir"])

    with open(source_path) as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} entries from {source_path}")
    print(f"Config : {CONFIG_PATH}\n")

    ok = 0
    failed = 0

    for idx, entry in enumerate(entries):
        try:
            bill_data = build_bill_data(entry)
            year, month = map(int, entry["month"].split("-"))
            month_name = _MONTH_NAMES[month]

            filename = f"{idx+1:03d}_{bill_data['bill_number']}.pdf"
            output_base.mkdir(parents=True, exist_ok=True)

            path = generate_bill(
                data=bill_data,
                template_id=1,
                output_dir=str(output_base),
                filename=filename,
            )

            print(
                f"  [{idx+1:02d}/{len(entries)}] {filename}"
                f"  (Rs. {entry['amount']}  {month_name} {year})"
            )
            ok += 1

        except Exception as e:
            print(f"  [{idx+1:02d}/{len(entries)}] FAILED — {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Generated : {ok} receipts")
    if failed:
        print(f"Failed    : {failed} receipts")
    print(f"Output dir: {output_base.resolve()}")


if __name__ == "__main__":
    main()
