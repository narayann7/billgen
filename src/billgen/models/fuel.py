"""
Fuel bill data model.

Extends `BillData` with fuel‑specific fields and validations.
Supports petrol, diesel, CNG, and EV charging.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import Field, model_validator

from billgen.models.base import BillData, BillType


# ---------------------------------------------------------------------------
# Fuel‑specific enums
# ---------------------------------------------------------------------------

class FuelType(str, Enum):
    """Supported fuel types."""
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    EV = "ev"  # electric vehicle charging


# ---------------------------------------------------------------------------
# Fuel Bill Data Model
# ---------------------------------------------------------------------------

class FuelBillData(BillData):
    """Concrete bill model for fuel / petrol‑pump transactions.

    Example JSON input
    ------------------
    ```json
    {
        "bill_type": "fuel",
        "bill_number": "INV-2026-00142",
        "bill_date": "2026-03-07",
        "bill_time": "14:30:00",
        "vendor_name": "Bharat Petroleum - Highway Station",
        "vendor_address": {
            "line1": "NH-48, Near Toll Plaza",
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": "411001"
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
                "rate": 104.45
            }
        ],
        "payment_mode": "upi",
        "transaction_id": "UPI/426713829164"
    }
    ```
    """

    # -- Bill type locked to FUEL -------------------------------------------
    bill_type: BillType = Field(default=BillType.FUEL, frozen=True)

    # -- Fuel‑specific fields -----------------------------------------------
    fuel_type: FuelType = Field(..., description="Type of fuel dispensed")
    fuel_grade: str | None = Field(
        default=None,
        description="Grade / brand variant (e.g. 'Speed 97', 'Power 99', 'xtra Premium')",
    )
    nozzle_number: str | None = Field(
        default=None,
        description="Pump / nozzle identifier",
    )
    density_at_15c: float | None = Field(
        default=None,
        gt=0,
        description="Fuel density at 15 °C (kg/litre) — printed on many Indian fuel bills",
    )
    pump_reading_start: float | None = Field(default=None, ge=0)
    pump_reading_end: float | None = Field(default=None, ge=0)
    footer_lines: list[str] = Field(default_factory=list, description="Footer messages printed at the bottom of the receipt")

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_pump_readings(self) -> "FuelBillData":
        """Ensure end reading > start reading if both are provided."""
        if self.pump_reading_start is not None and self.pump_reading_end is not None:
            if self.pump_reading_end <= self.pump_reading_start:
                raise ValueError(
                    f"pump_reading_end ({self.pump_reading_end}) must be "
                    f"greater than pump_reading_start ({self.pump_reading_start})"
                )
        return self

    # -----------------------------------------------------------------------
    # Domain rules
    # -----------------------------------------------------------------------

    def validate_domain_rules(self) -> None:
        """Run fuel‑specific business validations."""
        # Ensure all items use volume / energy units
        valid_units = {"litre", "liter", "l", "kg", "kwh", "unit"}
        for item in self.items:
            if item.unit.lower() not in valid_units:
                raise ValueError(
                    f"Item '{item.name}' has unexpected unit '{item.unit}'. "
                    f"Fuel items should use one of: {valid_units}"
                )

        # Vehicle number is strongly recommended for fuel bills
        if not self.vehicle_number:
            import warnings
            warnings.warn(
                "vehicle_number is missing — most fuel bills include this.",
                UserWarning,
                stacklevel=2,
            )

    # -----------------------------------------------------------------------
    # Template context
    # -----------------------------------------------------------------------

    def to_template_context(self) -> dict[str, Any]:
        """Build a flat dict suitable for PDF template rendering.

        Keys are designed to match typical Indian fuel‑bill placeholders.
        The renderer can pick whichever keys it needs for a given template.
        """
        first_item = self.items[0]

        ctx: dict[str, Any] = {
            # Identity
            "bill_number": self.bill_number,
            "bill_date": self.bill_date.strftime("%d/%m/%Y"),
            "bill_time": self.bill_time.strftime("%H:%M:%S") if self.bill_time else "",

            # Vendor
            "vendor_name": self.vendor_name,
            "vendor_address_line1": self.vendor_address.line1 if self.vendor_address else "",
            "vendor_address_line2": self.vendor_address.line2 or "" if self.vendor_address else "",
            "vendor_city": self.vendor_address.city if self.vendor_address else "",
            "vendor_state": self.vendor_address.state if self.vendor_address else "",
            "vendor_pincode": self.vendor_address.pincode if self.vendor_address else "",
            "vendor_gstin": self.vendor_gstin or "",
            "vendor_phone": self.vendor_phone or "",

            # Customer
            "customer_name": self.customer_name or "",
            "customer_phone": self.customer_phone or "",
            "customer_gstin": self.customer_gstin or "",
            "vehicle_number": self.vehicle_number or "",

            # Fuel details
            "fuel_type": self.fuel_type.value.title(),
            "fuel_grade": self.fuel_grade or "",
            "nozzle_number": self.nozzle_number or "",
            "density_at_15c": str(self.density_at_15c) if self.density_at_15c else "",
            "pump_reading_start": str(self.pump_reading_start) if self.pump_reading_start else "",
            "pump_reading_end": str(self.pump_reading_end) if self.pump_reading_end else "",

            # Primary item (convenience — most fuel bills have 1 item)
            "item_name": first_item.name,
            "quantity": str(first_item.quantity),
            "unit": first_item.unit,
            "rate": f"{first_item.rate:.2f}",
            "item_amount": f"{first_item.amount:.2f}",

            # Totals
            "subtotal": f"{self.subtotal:.2f}",
            "tax_percent": f"{self.tax_percent:.2f}",
            "tax_amount": f"{self.tax_amount:.2f}",
            "discount": f"{self.discount:.2f}",
            "total_amount": f"{self.total_amount:.2f}",

            # Payment
            "payment_mode": self.payment_mode.value.replace("_", " ").title(),
            "transaction_id": self.transaction_id or "",

            # Notes
            "notes": self.notes or "",

            # Footer
            "footer_lines": self.footer_lines,
        }

        # All items (for multi-item support)
        ctx["items"] = [
            {
                "name": item.name,
                "quantity": str(item.quantity),
                "unit": item.unit,
                "rate": f"{item.rate:.2f}",
                "amount": f"{item.amount:.2f}",
            }
            for item in self.items
        ]

        return ctx
