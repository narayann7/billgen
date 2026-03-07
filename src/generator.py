"""
Bill Generator Service — orchestrates model → renderer → PDF.

Usage:
    from src.generator import generate_bill
    
    output = generate_bill(json_data, template_id=1)
    # → Path("output/fuel/INV-2026-00142.pdf")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.base import BillType
from src.models.fuel import FuelBillData
from src.models.driver import DriverSalaryData
from src.renderer import get_renderer


# ---------------------------------------------------------------------------
# Model registry — maps BillType → concrete model class
# ---------------------------------------------------------------------------

MODEL_REGISTRY = {
    BillType.FUEL: FuelBillData,
    BillType.DRIVER: DriverSalaryData,
}

# Default output base directory
DEFAULT_OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_bill(
    data: dict[str, Any] | str,
    template_id: int = 1,
    output_dir: Path | str | None = None,
    filename: str | None = None,
) -> Path:
    """Generate a bill PDF from a JSON object.

    Args:
        data: A dict or JSON string with bill data.
              Must include `bill_type` to route to the correct model.
        template_id: Template variant to use (1, 2, or 3).
        output_dir: Override the output directory. Defaults to `output/<bill_type>/`.
        filename: Override the output filename. Defaults to `<bill_number>.pdf`.

    Returns:
        Path to the generated PDF.
    """
    # Parse JSON string if needed
    if isinstance(data, str):
        data = json.loads(data)

    # Determine bill type
    bill_type_str = data.get("bill_type")
    if not bill_type_str:
        raise ValueError("Missing 'bill_type' in input data")

    bill_type = BillType(bill_type_str)

    # Get the correct model class
    model_cls = MODEL_REGISTRY.get(bill_type)
    if not model_cls:
        raise ValueError(f"No model registered for bill type: {bill_type}")

    # Validate and create the model
    bill = model_cls(**data)
    bill.validate_domain_rules()

    # Get template context
    context = bill.to_template_context()

    # Determine output path
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR / bill_type.value
    else:
        output_dir = Path(output_dir)

    if filename is None:
        safe_number = bill.bill_number.replace("/", "-").replace("\\", "-")
        filename = f"{safe_number}.pdf"

    output_path = output_dir / filename

    # Render
    renderer = get_renderer(bill_type)
    renderer.render(context, output_path, template_id=template_id)

    return output_path
