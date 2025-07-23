#!/usr/bin/env python3
"""
Simple test script to demonstrate PDF to Markdown conversion functionality.
This script creates a test PDF and tests the conversion process.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_test_pdf():
    """Create a simple test PDF with text content."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = "test_sample.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add some test content
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 700, "This is a sample PDF for testing the PDF to Markdown converter.")
        c.drawString(100, 650, "It contains simple text that should be extracted.")
        c.drawString(100, 600, "Line 1: Hello World")
        c.drawString(100, 550, "Line 2: This is a test")
        c.drawString(100, 500, "Line 3: PDF to Markdown conversion")
        
        c.save()
        print(f"Created test PDF: {pdf_path}")
        return pdf_path
    except ImportError:
        print("reportlab not available, creating a simple text file instead")
        # Create a simple text file as fallback
        test_file = "test_sample.txt"
        with open(test_file, "w") as f:
            f.write("Test Document\n")
            f.write("This is a sample document for testing.\n")
            f.write("Line 1: Hello World\n")
            f.write("Line 2: This is a test\n")
            f.write("Line 3: Text processing\n")
        return test_file

def test_img2md():
    """Test the img2md functionality with a simple image."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text to image
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
            
        draw.text((10, 10), "Test Image", fill='black', font=font)
        draw.text((10, 40), "This is sample text", fill='black', font=font)
        draw.text((10, 70), "for testing OCR", fill='black', font=font)
        
        test_image_path = "test_image.png"
        img.save(test_image_path)
        print(f"Created test image: {test_image_path}")
        
        # Test img2md function
        import img2md
        
        # Use available model instead of default gemma3:12b
        result = img2md.image_to_text(test_image_path, model="JetBrains/Mellum-4b-base:latest")
        
        print("Image to Markdown conversion result:")
        print(result)
        
        return test_image_path
        
    except Exception as e:
        print(f"Error testing img2md: {e}")
        return None

def test_pdf_conversion():
    """Test PDF to Markdown conversion."""
    try:
        # Create test PDF
        pdf_path = create_test_pdf()
        
        if pdf_path.endswith('.pdf'):
            # Test with PyMuPDF version
            import pdf2md
            
            # Modify the script to use our test file and available model
            images = pdf2md.convert_pdf_to_images(pdf_path)
            
            if images:
                print(f"Successfully converted {len(images)} pages to images")
                
                # Test with available model
                result = pdf2md.query_gemma3_with_images(
                    images, 
                    model="JetBrains/Mellum-4b-base:latest"
                )
                
                # Save result
                output_file = "test_output.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result)
                
                print(f"Conversion complete! Output saved to {output_file}")
                print("First 200 characters of result:")
                print(result[:200] + "..." if len(result) > 200 else result)
                
                return True
            else:
                print("No images generated from PDF")
                return False
        else:
            print("Skipping PDF test - no PDF created")
            return False
            
    except Exception as e:
        print(f"Error testing PDF conversion: {e}")
        return False

if __name__ == "__main__":
    print("=== PDF2MD Testing Suite ===")
    print()
    
    print("1. Testing image to markdown conversion...")
    test_img2md()
    print()
    
    print("2. Testing PDF to markdown conversion...")
    test_pdf_conversion()
    print()
    
    print("Testing complete!")