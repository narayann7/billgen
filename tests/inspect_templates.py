"""Inspect the PDF templates to understand their structure."""
import sys
sys.path.insert(0, ".")

from pypdf import PdfReader
from pathlib import Path

template_dir = Path("data/fuel")

for pdf_path in sorted(template_dir.glob("*.pdf")):
    print(f"\n{'='*70}")
    print(f"📄 {pdf_path.name}")
    print(f"{'='*70}")
    
    reader = PdfReader(str(pdf_path))
    print(f"   Pages: {len(reader.pages)}")
    print(f"   File size: {pdf_path.stat().st_size:,} bytes")
    
    # Check for form fields
    fields = reader.get_form_text_fields()
    if fields:
        print(f"\n   📝 Form Fields ({len(fields)}):")
        for name, value in fields.items():
            print(f"      {name}: '{value}'")
    else:
        print(f"\n   📝 No form fields found")
    
    # Check all field types
    if reader.get_fields():
        all_fields = reader.get_fields()
        print(f"\n   📋 All Fields ({len(all_fields)}):")
        for name, field in all_fields.items():
            field_type = field.get('/FT', 'unknown')
            print(f"      {name} (type={field_type}): {field.get('/V', '')}")
    
    # Extract text from each page
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"\n   📃 Page {i+1} text:")
        if text:
            for line in text.strip().split('\n'):
                print(f"      {line}")
        else:
            print(f"      (no extractable text)")
    
    # Page dimensions
    page = reader.pages[0]
    box = page.mediabox
    print(f"\n   📐 Dimensions: {float(box.width):.0f} x {float(box.height):.0f} points")
    print(f"                  ({float(box.width)/72:.1f} x {float(box.height)/72:.1f} inches)")
