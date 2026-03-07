"""
Generate fuel bills from input/fuel/source.json.

All configuration is loaded from input/fuel/config.json — no hardcoded
lookup tables live in this file.

Each source entry is mapped to a complete FuelBillData payload and
rendered as a PDF into output/fuel/<ProviderName>/.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, ".")
from src.generator import generate_bill

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

CONFIG_PATH = Path("input/fuel/config.json")

with open(CONFIG_PATH) as _f:
    _CFG = json.load(_f)

# Build fast address-keyed lookups from the config
_VENDOR_BY_ADDRESS: dict[str, dict] = {}   # address -> {provider, station, meta}
for _provider, _meta in _CFG["vendor_meta"].items():
    for _station in _meta["stations"]:
        _VENDOR_BY_ADDRESS[_station["address"]] = {
            "provider": _provider,
            "station": _station,
            "meta": _meta,
        }

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def petrol_rate_for_date(dt: datetime) -> float:
    """Return Bengaluru petrol price (₹/litre) for the given date from config."""
    key = dt.strftime("%Y-%m")
    rates = _CFG["petrol_rates"]
    if key in rates["monthly"]:
        return rates["monthly"][key]
    if dt.year < 2025:
        return rates["default_before_2025"]
    return rates["default_from_2026"]


def nozzle_for_index(idx: int) -> str:
    return str((idx % 6) + 1)


def bill_number(bill_prefix: str, dt: datetime, amount: int) -> str:
    date_part = dt.strftime("%Y%m%d")
    h = int(hashlib.md5(f"{bill_prefix}{dt}{amount}".encode()).hexdigest(), 16)
    suffix = str(h % 900000 + 100000)
    return f"{bill_prefix}-{date_part}-{suffix}"


def provider_subdir(provider: str) -> str:
    """Convert a provider name into a filesystem-safe folder name."""
    return provider.replace(" ", "_").replace("/", "-")


# ---------------------------------------------------------------------------
# Bill data builder
# ---------------------------------------------------------------------------

def build_bill_data(idx: int, entry: dict) -> tuple[dict, str]:
    """Return (bill_data_dict, provider_name) for one source entry."""
    dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
    amount = entry["amount"]
    vehicle_type = entry["vehicle_type"]
    address = entry["address"]

    # Resolve vendor from config via address
    vendor_info = _VENDOR_BY_ADDRESS.get(address)
    if vendor_info is None:
        raise ValueError(f"Address not found in config: {address!r}")

    provider = vendor_info["provider"]
    station  = vendor_info["station"]
    meta     = vendor_info["meta"]

    rate      = petrol_rate_for_date(dt)
    quantity  = round(amount / rate, 2)
    fuel_grade = meta["fuel_grade"]

    vendor_gstin = f"{meta['gstin_prefix']}{station['gstin_suffix']}"
    bill_num     = bill_number(meta["bill_prefix"], dt, amount)

    vehicle_numbers = _CFG["vehicle_numbers"]
    vehicle_num = vehicle_numbers.get(vehicle_type, "KA-00-XX-0000")

    density = meta["density"]

    template_id = meta.get("template_id", 1)

    bill_data = {
        "bill_type":      "fuel",
        "bill_number":    bill_num,
        "bill_date":      dt.strftime("%Y-%m-%d"),
        "bill_time":      dt.strftime("%H:%M:%S"),
        "vendor_name":    station["name"],
        "vendor_address": station["address_parsed"],
        "vendor_gstin":   vendor_gstin,
        "vendor_phone":   station["phone"],
        "vehicle_number": vehicle_num,
        "fuel_type":      "petrol",
        "fuel_grade":     fuel_grade,
        "nozzle_number":  nozzle_for_index(idx),
        "density_at_15c": density,
        "footer_lines": meta.get("footer_lines", []),
        "items": [
            {
                "name":     f"Petrol ({fuel_grade})",
                "quantity": quantity,
                "unit":     "litre",
                "rate":     rate,
            }
        ],
    }

    return bill_data, provider, template_id


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    source_path = Path("input/fuel/source.json")
    output_base = Path(_CFG["output"]["base_dir"])
    subdir_by_provider: bool = _CFG["output"].get("subdir_by_provider", False)

    with open(source_path) as f:
        entries = json.load(f)

    print(f"📋 Loaded {len(entries)} bills from {source_path}")
    print(f"⚙️  Config : {CONFIG_PATH}\n")

    ok = 0
    failed = 0
    for idx, entry in enumerate(entries):
        try:
            bill_data, provider, template_id = build_bill_data(idx, entry)
            dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
            # Prefix filename with sequence number to maintain source order sorting
            filename = f"{idx+1:03d}_{bill_data['bill_number']}.pdf"

            if subdir_by_provider:
                output_dir = output_base / provider_subdir(provider)
            else:
                output_dir = output_base

            output_dir.mkdir(parents=True, exist_ok=True)

            path = generate_bill(
                data=bill_data,
                template_id=template_id,
                output_dir=str(output_dir),
                filename=filename,
            )
            label = provider_subdir(provider) if subdir_by_provider else ""
            print(
                f"  ✅ [{idx+1:02d}/{len(entries)}] {label}/{filename}"
                f"  (₹{entry['amount']}  {entry['vehicle_type']}  {dt.strftime('%d %b %Y')})"
            )
            ok += 1
        except Exception as e:
            print(f"  ❌ [{idx+1:02d}/{len(entries)}] FAILED — {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Generated : {ok} bills")
    if failed:
        print(f"Failed    : {failed} bills")
    print(f"Output dir: {output_base.resolve()}")


if __name__ == "__main__":
    main()
