"""
PDF Renderer — generates fuel receipt PDFs using ReportLab.

Each template number corresponds to a visual style. The renderer
reads the original PDF template as background and overlays dynamic
text on top, OR generates the receipt entirely from scratch when
the template is purely decorative (no form fields).

This module is designed to be extended:
  • Add a new renderer class for each bill type
  • Register it in the RENDERERS dict
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white, HexColor
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from billgen.models.base import BillData, BillType


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Receipt size matching templates: 226 x 400 points  ≈ 79.7mm x 141.1mm
RECEIPT_W = 190
RECEIPT_H = 400

CREAM_BG = Color(1, 0.996, 0.980)  # warm cream from templates
MARGIN = 14
CONTENT_W = RECEIPT_W - 2 * MARGIN


# ---------------------------------------------------------------------------
# Abstract base renderer
# ---------------------------------------------------------------------------

class BillRenderer(ABC):
    """Abstract base for all bill renderers."""

    @abstractmethod
    def render(self, context: dict[str, Any], output_path: Path, template_id: int) -> Path:
        """Generate a PDF bill and return the output path."""
        ...


# ---------------------------------------------------------------------------
# Fuel receipt renderer
# ---------------------------------------------------------------------------

class FuelReceiptRenderer(BillRenderer):
    """Generates fuel receipts matching the template style.

    Supports 3 template variants (template_id 1, 2, 3) which differ
    only in branding/logo. Since the original PDFs have no form fields,
    we recreate the layout with ReportLab.
    """

    # Logo directory (relative to project root)
    LOGO_DIR = Path("data/fuel/logos")

    BRAND_CONFIG = {
        1: {
            "name": "INDIAN OIL",
            "color": HexColor("#E8600A"),  # IndianOil orange
            "accent": HexColor("#1B4F72"),
            "logo": "logo_1.png",
        },
        2: {
            "name": "HINDUSTAN PETROLEUM",
            "color": HexColor("#003B73"),  # HP blue
            "accent": HexColor("#00843D"),
            "logo": "logo_2.png",
        },
        3: {
            "name": "BHARAT PETROLEUM",
            "color": HexColor("#FFD700"),  # BPCL yellow
            "accent": HexColor("#C62828"),
            "logo": "logo_3.png",
        },
    }

    def render(self, context: dict[str, Any], output_path: Path, template_id: int = 1) -> Path:
        """Generate a fuel receipt PDF.

        Args:
            context: Flat dict from `FuelBillData.to_template_context()`
            output_path: Where to save the PDF
            template_id: Which brand style to use (1=IOC, 2=HP, 3=BPCL)

        Returns:
            The output path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        brand = self.BRAND_CONFIG.get(template_id, self.BRAND_CONFIG[1])

        c = Canvas(str(output_path), pagesize=(RECEIPT_W, RECEIPT_H))

        # -- Background -----------------------------------------------------
        c.setFillColor(CREAM_BG)
        c.rect(0, 0, RECEIPT_W, RECEIPT_H, fill=1, stroke=0)




        y = RECEIPT_H - MARGIN  # Start from top

        # -- Brand header ---------------------------------------------------
        y -= 4

        # Logo (40x40, centered, matching template layout)
        logo_file = self.LOGO_DIR / brand["logo"]
        if logo_file.exists():
            logo_size = 40
            logo_x = (RECEIPT_W - logo_size) / 2
            c.drawImage(
                str(logo_file), logo_x, y - logo_size,
                width=logo_size, height=logo_size,
                preserveAspectRatio=True, mask='auto',
            )
            y -= logo_size + 16

        # Company name
        c.setFont("Courier", 11)
        c.setFillColor(black)
        self._draw_centered(c, brand["name"], y)
        y -= 14

        # Address (may wrap)
        c.setFont("Courier", 7)
        addr_parts = []
        if context.get("vendor_address_line1"):
            addr_parts.append(context["vendor_address_line1"])
        if context.get("vendor_address_line2"):
            addr_parts.append(context["vendor_address_line2"])
        city_state = ", ".join(filter(None, [
            context.get("vendor_city"),
            context.get("vendor_state"),
            context.get("vendor_pincode"),
        ]))
        if city_state:
            addr_parts.append(city_state)

        full_addr = ", ".join(addr_parts) if addr_parts else context.get("vendor_name", "")
        # Wrap long addresses
        lines = self._wrap_text(full_addr, 38)
        for line in lines:
            self._draw_centered(c, line, y)
            y -= 9
        y -= 2

        # -- "FUEL RECEIPT" header ------------------------------------------
        c.setFont("Courier", 10)
        self._draw_centered(c, "FUEL RECEIPT", y)
        y -= 4

        # Dashed separator
        self._draw_dashed_line(c, y)
        y -= 12

        # -- Receipt details ------------------------------------------------
        c.setFont("Courier", 8)
        detail_fields = [
            ("RECEIPT NO", context.get("bill_number", "")),
            ("DATE", context.get("bill_date", "")),
            ("TIME", context.get("bill_time", "")),
        ]
        for label, value in detail_fields:
            self._draw_field_row(c, label, value, y)
            y -= 12

        # Vehicle number (if present)
        if context.get("vehicle_number"):
            self._draw_field_row(c, "VEHICLE NO", context["vehicle_number"], y)
            y -= 12

        # Separator
        self._draw_dashed_line(c, y)
        y -= 12

        # -- Fuel details ---------------------------------------------------
        fuel_fields = [
            ("PRODUCT", f"{context.get('fuel_type', '')} {context.get('fuel_grade', '')}".strip()),
            ("VOLUME", f"{context.get('quantity', '')} {context.get('unit', '').upper()}"),
            ("RATE/{unit}".format(unit=context.get("unit", "UNIT").upper()), f"Rs. {context.get('rate', '')}"),
        ]
        for label, value in fuel_fields:
            self._draw_field_row(c, label, value, y)
            y -= 12

        # Nozzle (if present)
        if context.get("nozzle_number"):
            self._draw_field_row(c, "NOZZLE", context["nozzle_number"], y)
            y -= 12

        # Density (if present)
        if context.get("density_at_15c"):
            self._draw_field_row(c, "DENSITY@15C", context["density_at_15c"], y)
            y -= 12

        # Separator
        self._draw_dashed_line(c, y)
        y -= 14

        # -- Total amount (highlighted) ------------------------------------
        c.setFont("Courier", 10)
        self._draw_field_row(c, "TOTAL AMOUNT", f"Rs. {context.get('total_amount', '')}", y)
        y -= 6

        # Separator
        self._draw_dashed_line(c, y)
        y -= 12

        # -- Payment info ---------------------------------------------------
        c.setFont("Courier", 7)
        if context.get("payment_mode"):
            self._draw_field_row(c, "PAYMENT", context["payment_mode"], y)
            y -= 10

        if context.get("transaction_id"):
            self._draw_field_row(c, "Trans ID", context["transaction_id"], y)
            y -= 10

        # -- Customer info --------------------------------------------------
        if context.get("customer_name"):
            self._draw_field_row(c, "CUSTOMER", context["customer_name"], y)
            y -= 10

        if context.get("customer_gstin"):
            self._draw_field_row(c, "GSTIN", context["customer_gstin"], y)
            y -= 10

        y -= 6

        # -- Footer messages ------------------------------------------------
        footer_lines = context.get("footer_lines") or []
        c.setFont("Courier", 7)
        for line in footer_lines:
            self._draw_centered(c, line, y)
            y -= 10
        y -= 4

        # -- GSTIN of vendor ------------------------------------------------
        if context.get("vendor_gstin"):
            c.setFont("Courier", 6)
            self._draw_centered(c, f"GSTIN: {context['vendor_gstin']}", y)
            y -= 10



        c.save()
        return output_path

    # -----------------------------------------------------------------------
    # Drawing helpers
    # -----------------------------------------------------------------------

    def _draw_centered(self, c: Canvas, text: str, y: float) -> None:
        """Draw text centered on the receipt."""
        tw = c.stringWidth(text, c._fontname, c._fontsize)
        x = (RECEIPT_W - tw) / 2
        c.drawString(x, y, text)

    def _draw_field_row(self, c: Canvas, label: str, value: str, y: float) -> None:
        """Draw a label: value row."""
        c.drawString(MARGIN, y, f"{label}:")
        c.drawRightString(RECEIPT_W - MARGIN, y, str(value))

    def _draw_dashed_line(self, c: Canvas, y: float) -> None:
        """Draw a dashed separator line."""
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.setDash(2, 1.2)
        c.line(MARGIN, y, RECEIPT_W - MARGIN, y)
        c.setDash()  # reset

    @staticmethod
    def _wrap_text(text: str, max_chars: int) -> list[str]:
        """Simple word-wrap for receipt text."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if current and len(current) + 1 + len(word) > max_chars:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}" if current else word
        if current:
            lines.append(current)
        return lines


# ---------------------------------------------------------------------------
# Driver salary renderer
# ---------------------------------------------------------------------------

_A4_W, _A4_H = A4   # 595.27 x 841.89 points
_DOC_MARGIN_H = 72  # 1-inch horizontal margin
_DOC_MARGIN_V = 60  # top/bottom margin
_DOC_CONTENT_W = _A4_W - 2 * _DOC_MARGIN_H

_FONT_REG  = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"


class DriverSalaryRenderer(BillRenderer):
    """Generates A4 driver salary receipt PDFs matching the template layout.

    The document has two sections separated by a horizontal rule:
      1. Driver Salary Receipt  — employer certifies payment
      2. Receipt Acknowledgement — driver acknowledges receipt + Signature
    """

    def render(self, context: dict[str, Any], output_path: Path, template_id: int = 1) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = Canvas(str(output_path), pagesize=A4)

        # White background
        c.setFillColor(white)
        c.rect(0, 0, _A4_W, _A4_H, fill=1, stroke=0)
        c.setFillColor(black)  # reset fill to black for all text

        y = _A4_H - _DOC_MARGIN_V  # start near top

        amount   = context["amount"]
        driver   = context["driver_name"]
        month    = context["salary_month"]
        employee = context["employee_name"]
        date_str = context["bill_date"]
        veh_no   = context.get("vehicle_number", "")

        # ── SECTION 1: Driver Salary Receipt ──────────────────────────────

        c.setFont(_FONT_BOLD, 16)
        self._centered(c, "Driver Salary Receipt", y)
        y -= 28

        # Certification paragraph (inline bold via HTML markup)
        cert_html = (
            f"This is to certify that I have paid <b>Rs. {amount}</b> to driver, "
            f"<b>{driver}</b> for the month of <b>{month}</b> "
            "(Acknowledged receipt enclosed). I also declare that the driver is "
            "exclusively utilized for official purpose only. Please reimburse the "
            "above amount. I further declare that what is stated above is correct "
            "and true."
        )
        y = self._draw_paragraph(c, cert_html, y, font_size=11, leading=17)
        y -= 18

        self._label_value(c, "Employee Name", employee, y)
        y -= 20

        self._label_value(c, "Date", date_str, y)
        y -= 30

        # ── Horizontal separator ──────────────────────────────────────────
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.setDash()
        c.line(_DOC_MARGIN_H, y, _A4_W - _DOC_MARGIN_H, y)
        y -= 30

        # ── SECTION 2: Receipt Acknowledgement ───────────────────────────

        c.setFont(_FONT_BOLD, 14)
        self._centered(c, "Receipt Acknowledgement", y)
        y -= 28

        for label, value in [
            ("Date of Receipt", date_str),
            ("For the Month of", month),
            ("Name of Driver", driver),
            ("Vehicle No", veh_no),
        ]:
            self._label_value(c, label, value, y)
            y -= 20

        y -= 14

        recv_html = (
            f"Received a sum of <b>Rs. {amount}</b> only for the month of "
            f"<b>{month}</b> from <b>Mr. {employee}</b>."
        )
        y = self._draw_paragraph(c, recv_html, y, font_size=11, leading=17)
        y -= 50

        # ── Signature ────────────────────────────────────────────────────────
        sig_text = "Signature"
        c.setFont(_FONT_REG, 11)
        sig_w = c.stringWidth(sig_text, _FONT_REG, 11)
        c.drawString(_A4_W - _DOC_MARGIN_H - sig_w, y, sig_text)
        y -= 6

        # Signature image (shifted further right than the label)
        sig_img_path = Path("data/driver/signature.png")
        if sig_img_path.exists():
            sig_img_w = 140
            sig_img_h = 50
            c.drawImage(
                str(sig_img_path),
                _A4_W - 30 - sig_img_w,
                y - sig_img_h,
                width=sig_img_w,
                height=sig_img_h,
                preserveAspectRatio=True,
                mask='auto',
            )

        c.save()
        return output_path

    # -----------------------------------------------------------------------
    # Drawing helpers
    # -----------------------------------------------------------------------

    def _centered(self, c: Canvas, text: str, y: float) -> None:
        tw = c.stringWidth(text, c._fontname, c._fontsize)
        c.drawString((_A4_W - tw) / 2, y, text)

    def _label_value(self, c: Canvas, label: str, value: str, y: float) -> None:
        label_text = f"{label}: "
        c.setFont(_FONT_BOLD, 11)
        c.drawString(_DOC_MARGIN_H, y, label_text)
        lw = c.stringWidth(label_text, _FONT_BOLD, 11)
        c.setFont(_FONT_REG, 11)
        c.drawString(_DOC_MARGIN_H + lw, y, value)

    def _draw_paragraph(self, c: Canvas, html: str, y_top: float,
                        font_size: int = 11, leading: int = 17) -> float:
        """Render a Paragraph with HTML markup; return updated y (bottom of para)."""
        style = ParagraphStyle(
            "drv_para",
            fontName=_FONT_REG,
            fontSize=font_size,
            leading=leading,
        )
        para = Paragraph(html, style)
        _, h = para.wrapOn(c, _DOC_CONTENT_W, 400)
        y_bottom = y_top - h
        para.drawOn(c, _DOC_MARGIN_H, y_bottom)
        return y_bottom


# ---------------------------------------------------------------------------
# Renderer registry — add new bill types here
# ---------------------------------------------------------------------------

RENDERERS: dict[BillType, type[BillRenderer]] = {
    BillType.FUEL: FuelReceiptRenderer,
    BillType.DRIVER: DriverSalaryRenderer,
}


def get_renderer(bill_type: BillType) -> BillRenderer:
    """Factory: get the appropriate renderer for a bill type."""
    renderer_cls = RENDERERS.get(bill_type)
    if not renderer_cls:
        raise ValueError(f"No renderer registered for bill type: {bill_type}")
    return renderer_cls()
