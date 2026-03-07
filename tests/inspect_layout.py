"""Extract detailed layout info from PDF templates."""
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
    page = reader.pages[0]
    
    # Get resources
    resources = page.get("/Resources")
    if resources:
        # Check for fonts
        fonts = resources.get("/Font")
        if fonts:
            print(f"\n   🔤 Fonts:")
            for font_name, font_obj in fonts.items():
                resolved = font_obj.get_object() if hasattr(font_obj, 'get_object') else font_obj
                base_font = resolved.get("/BaseFont", "unknown")
                print(f"      {font_name}: {base_font}")
        
        # Check for images/XObjects
        xobjects = resources.get("/XObject")
        if xobjects:
            print(f"\n   🖼️  XObjects (images/graphics):")
            for name, obj in xobjects.items():
                resolved = obj.get_object() if hasattr(obj, 'get_object') else obj
                subtype = resolved.get("/Subtype", "unknown")
                if subtype == "/Image":
                    width = resolved.get("/Width", "?")
                    height = resolved.get("/Height", "?")
                    print(f"      {name}: Image {width}x{height}")
                else:
                    print(f"      {name}: {subtype}")
        
        # Colors
        color_spaces = resources.get("/ColorSpace")
        if color_spaces:
            print(f"\n   🎨 Color Spaces:")
            for name, cs in color_spaces.items():
                print(f"      {name}: {cs}")
    
    # Raw content stream snippets (first 2000 chars)
    content = page.get("/Contents")
    if content:
        resolved = content.get_object() if hasattr(content, 'get_object') else content
        if hasattr(resolved, 'get_data'):
            raw = resolved.get_data().decode('latin-1', errors='replace')
            print(f"\n   📜 Content stream (first 2000 chars):")
            print(f"      {raw[:2000]}")
