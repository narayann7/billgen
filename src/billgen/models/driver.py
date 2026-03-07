"""
Driver salary data model.

Extends `BillData` for monthly driver salary receipts.
Each receipt is a two-part document: the employer's certification and
the driver's acknowledgement.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from billgen.models.base import BillData, BillType


class DriverSalaryData(BillData):
    """Concrete bill model for driver monthly salary receipts.

    Example JSON input
    ------------------
    ```json
    {
        "bill_type": "driver",
        "bill_number": "DRV-202503-123456",
        "bill_date": "2026-03-31",
        "vendor_name": "Narayan",
        "salary_month": "March",
        "salary_year": 2026,
        "driver_name": "Mr. Jhon Doe",
        "vehicle_number": "KA05JZ1755",
        "items": [
            {
                "name": "Driver Salary for March",
                "quantity": 1,
                "unit": "month",
                "rate": 1200
            }
        ]
    }
    ```
    """

    # -- Bill type locked to DRIVER ----------------------------------------
    bill_type: BillType = Field(default=BillType.DRIVER, frozen=True)

    # -- Driver-specific fields --------------------------------------------
    salary_month: str = Field(..., description="Month name for which salary is paid, e.g. 'March'")
    salary_year: int = Field(..., description="Year for which salary is paid, e.g. 2026")
    driver_name: str = Field(..., description="Full name of driver, e.g. 'Mr. Jhon Doe'")

    # -----------------------------------------------------------------------
    # Domain rules
    # -----------------------------------------------------------------------

    def validate_domain_rules(self) -> None:
        """Run driver-salary-specific business validations."""
        for item in self.items:
            if item.unit.lower() != "month":
                raise ValueError(
                    f"Driver salary items should use unit 'month', got '{item.unit}'"
                )

    # -----------------------------------------------------------------------
    # Template context
    # -----------------------------------------------------------------------

    def to_template_context(self) -> dict[str, Any]:
        """Build a flat dict for PDF template rendering."""
        amount = int(self.total_amount)

        ctx: dict[str, Any] = {
            "bill_number": self.bill_number,
            "bill_date": self.bill_date.strftime("%d %B %Y"),
            "salary_month": self.salary_month,
            "salary_year": self.salary_year,
            "employee_name": self.vendor_name,
            "driver_name": self.driver_name,
            "vehicle_number": self.vehicle_number or "",
            "amount": str(amount),
            "notes": self.notes or "",
        }

        return ctx
