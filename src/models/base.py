"""
Base data models for the Bill Generator.

This module defines the abstract base classes and shared models
that all bill types (fuel, grocery, etc.) must extend.
The design follows the Open/Closed Principle — new bill types
can be added without modifying existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, time
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BillType(str, Enum):
    """Registry of supported bill categories.

    Add a new member here when introducing a new bill domain
    (e.g. GROCERY = "grocery").
    """
    FUEL = "fuel"


class PaymentMode(str, Enum):
    """How the customer paid."""
    CASH = "cash"
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WALLET = "wallet"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

class Address(BaseModel):
    """A physical address, used for both the vendor and customer."""
    line1: str
    line2: str | None = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class BillItem(BaseModel):
    """A single line‑item on a bill.

    For a fuel bill there will typically be just one item,
    but multi‑item support keeps the model generic.
    """
    name: str
    description: str | None = None
    quantity: float = Field(..., gt=0, description="Quantity (litres, kg, units, etc.)")
    unit: str = Field(default="unit", description="Unit of measurement")
    rate: float = Field(..., gt=0, description="Price per unit (₹)")
    amount: float | None = Field(
        default=None,
        description="Total for this line‑item. Auto‑calculated if omitted.",
    )

    @model_validator(mode="after")
    def _compute_amount(self) -> "BillItem":
        """Auto-calculate amount = quantity × rate when not provided."""
        if self.amount is None:
            self.amount = round(self.quantity * self.rate, 2)
        return self


# ---------------------------------------------------------------------------
# Abstract base: every bill domain extends this
# ---------------------------------------------------------------------------

class BillData(BaseModel, ABC):
    """Abstract base for all bill data.

    Subclasses MUST:
      • set  `bill_type`  as a class‑level literal
      • implement `validate_domain_rules()` for any domain‑specific checks
      • implement `to_template_context()` to return a flat dict the PDF
        renderer can use

    All shared fields (customer, vendor, totals, payment, …) live here
    so that every bill type gets them for free.
    """

    # -- identity -----------------------------------------------------------
    bill_id: UUID = Field(default_factory=uuid4, description="Unique bill identifier")
    bill_type: BillType = Field(..., description="Type of bill")
    bill_number: str = Field(..., min_length=1, description="Human‑readable bill/invoice number")

    # -- date & time --------------------------------------------------------
    bill_date: date = Field(..., description="Date of the transaction")
    bill_time: time | None = Field(default=None, description="Time of the transaction")

    # -- vendor / seller ----------------------------------------------------
    vendor_name: str = Field(..., min_length=1)
    vendor_address: Address | None = None
    vendor_gstin: str | None = Field(default=None, description="GST Identification Number")
    vendor_phone: str | None = None

    # -- customer / buyer ---------------------------------------------------
    customer_name: str | None = None
    customer_address: Address | None = None
    customer_phone: str | None = None
    customer_gstin: str | None = None
    vehicle_number: str | None = Field(default=None, description="Vehicle registration (for fuel / service bills)")

    # -- line items ---------------------------------------------------------
    items: list[BillItem] = Field(..., min_length=1, description="At least one line‑item required")

    # -- totals -------------------------------------------------------------
    subtotal: float | None = Field(default=None, description="Sum of item amounts before tax")
    tax_percent: float = Field(default=0.0, ge=0)
    tax_amount: float | None = Field(default=None, description="Auto‑calculated if omitted")
    discount: float = Field(default=0.0, ge=0, description="Flat discount (₹)")
    total_amount: float | None = Field(default=None, description="Grand total. Auto‑calculated if omitted.")

    # -- payment ------------------------------------------------------------
    payment_mode: PaymentMode = PaymentMode.CASH
    transaction_id: str | None = Field(default=None, description="UPI / card txn reference")

    # -- misc ---------------------------------------------------------------
    notes: str | None = None

    # -----------------------------------------------------------------------
    # Auto‑calculations
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def _compute_totals(self) -> "BillData":
        """Derive subtotal, tax_amount, and total_amount when not explicitly set."""
        if self.subtotal is None:
            self.subtotal = round(sum(item.amount for item in self.items), 2)

        if self.tax_amount is None:
            self.tax_amount = round(self.subtotal * self.tax_percent / 100, 2)

        if self.total_amount is None:
            self.total_amount = round(self.subtotal + self.tax_amount - self.discount, 2)

        return self

    # -----------------------------------------------------------------------
    # Extension points
    # -----------------------------------------------------------------------

    @abstractmethod
    def validate_domain_rules(self) -> None:
        """Run domain‑specific validations (called after Pydantic checks).

        Raise `ValueError` with a descriptive message on failure.
        """
        ...

    @abstractmethod
    def to_template_context(self) -> dict[str, Any]:
        """Return a flat dictionary that the PDF template renderer can consume.

        Keys should match placeholder names in the corresponding PDF template.
        """
        ...

    # -----------------------------------------------------------------------
    # Convenience helpers
    # -----------------------------------------------------------------------

    def to_json(self, **kwargs) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2, **kwargs)

    @classmethod
    def from_json(cls, raw: str | bytes) -> "BillData":
        """Deserialize from a JSON string."""
        return cls.model_validate_json(raw)
