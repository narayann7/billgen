"""Extract logo images from fuel bill templates with proper transparency."""
import sys
sys.path.insert(0, ".")

from pypdf import PdfReader
from pathlib import Path
from PIL import Image
import io

template_dir = Path("data/fuel")
logo_dir = Path("data/fuel/logos")
logo_dir.mkdir(exist_ok=True)

for pdf_path in sorted(template_dir.glob("*.pdf")):
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    resources = page.get("/Resources")
    
    if not resources:
        continue
    
    xobjects = resources.get("/XObject")
    if not xobjects:
        continue
    
    template_num = pdf_path.stem.split("_")[-1]
    
    for name, obj in xobjects.items():
        resolved = obj.get_object() if hasattr(obj, 'get_object') else obj
        subtype = resolved.get("/Subtype")
        
        if str(subtype) != "/Image":
            continue
        
        width = resolved.get("/Width")
        height = resolved.get("/Height")
        
        print(f"\n📄 {pdf_path.name} → {name} ({width}x{height})")
        
        # Get the main image data
        data = resolved.get_data()
        
        # Check for SMask (alpha/transparency channel)
        smask = resolved.get("/SMask")
        
        # Create RGB image
        img = Image.frombytes("RGB", (width, height), data[:width * height * 3])
        
        if smask:
            smask_obj = smask.get_object() if hasattr(smask, 'get_object') else smask
            smask_w = smask_obj.get("/Width")
            smask_h = smask_obj.get("/Height")
            smask_data = smask_obj.get_data()
            
            print(f"   ✅ Found SMask (alpha channel): {smask_w}x{smask_h}")
            
            # Create alpha channel image
            alpha = Image.frombytes("L", (smask_w, smask_h), smask_data[:smask_w * smask_h])
            
            # Resize alpha if dimensions differ
            if (smask_w, smask_h) != (width, height):
                alpha = alpha.resize((width, height), Image.LANCZOS)
            
            # Merge RGB + Alpha → RGBA
            img = img.convert("RGBA")
            img.putalpha(alpha)
            print(f"   ✅ Applied transparency")
        else:
            print(f"   ⚠️  No SMask found — attempting background removal")
            # Fallback: make black pixels transparent
            img = img.convert("RGBA")
            pixels = img.load()
            for py in range(height):
                for px in range(width):
                    r, g, b, a = pixels[px, py]
                    # If pixel is very dark (near black), make transparent
                    if r < 15 and g < 15 and b < 15:
                        pixels[px, py] = (r, g, b, 0)
        
        # Save as PNG with transparency
        png_path = logo_dir / f"logo_{template_num}.png"
        img.save(str(png_path), "PNG")
        print(f"   ✅ Saved: {png_path} ({png_path.stat().st_size:,} bytes)")

# Clean up .raw files
for raw in logo_dir.glob("*.raw"):
    raw.unlink()
    print(f"   🗑️  Removed: {raw.name}")

print("\n📂 Final logos:")
for f in sorted(logo_dir.glob("*.png")):
    img = Image.open(str(f))
    print(f"   {f.name}: {img.size}, mode={img.mode}, {f.stat().st_size:,} bytes")
