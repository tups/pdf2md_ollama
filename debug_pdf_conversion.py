#!/usr/bin/env python3
"""
Debug script to test PDF conversion scenario with multiple images
"""
import sys
import os
import fitz  # PyMuPDF
from PIL import Image
import io

# Add src to path
sys.path.append('src')
from openrouter_client import OpenRouterClient, get_openrouter_model

def convert_pdf_to_images_debug(pdf_path, max_pages=2):
    """Convert PDF to images (limited pages for testing)"""
    images = []
    doc = fitz.open(pdf_path)
    
    # Limit to first few pages for testing
    num_pages = min(len(doc), max_pages)
    print(f"Converting {num_pages} pages from PDF...")
    
    for page_num in range(num_pages):
        pix = doc[page_num].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        image_bytes = img_buffer.getvalue()
        images.append(image_bytes)
        
        # Check image size
        print(f"Page {page_num + 1}: {len(image_bytes)} bytes, {img.width}x{img.height} pixels")
    
    doc.close()
    return images

def test_pdf_conversion_debug():
    """Test PDF conversion with debug info"""
    print("🔍 Debugging PDF conversion with OpenRouter...")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        return
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test with the PDF file
    pdf_path = "Referentiel_NF525_V2.3_Fiche_Tarifaire_LORD_OF_WEB.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Convert PDF to images (limited pages)
    try:
        images = convert_pdf_to_images_debug(pdf_path, max_pages=2)
        print(f"✅ Successfully converted {len(images)} pages to images")
    except Exception as e:
        print(f"❌ Failed to convert PDF: {e}")
        return
    
    # Test with the working model
    model = "meta-llama/llama-3.2-11b-vision-instruct:free"
    prompt = "Extract all readable text and text chunks from this image and format it as structured Markdown. Look in the entire image always and try to retrieve all text!"
    
    client = OpenRouterClient()
    
    # Test with single image first
    print(f"\n🧪 Testing with single image...")
    try:
        response = client.chat_with_images(
            model=model,
            prompt=prompt,
            image_bytes_list=[images[0]],  # Just first image
            max_tokens=1000
        )
        print(f"✅ Single image test successful!")
        print(f"📄 Response preview: {response[:200]}...")
    except Exception as e:
        print(f"❌ Single image test failed: {e}")
        return
    
    # Test with multiple images
    print(f"\n🧪 Testing with {len(images)} images...")
    try:
        response = client.chat_with_images(
            model=model,
            prompt=prompt,
            image_bytes_list=images,  # All images
            max_tokens=2000
        )
        print(f"✅ Multiple images test successful!")
        print(f"📄 Response preview: {response[:200]}...")
        
        # Save the result
        with open("debug_output.md", "w", encoding="utf-8") as f:
            f.write(response)
        print(f"💾 Full response saved to debug_output.md")
        
    except Exception as e:
        print(f"❌ Multiple images test failed: {e}")
        
        # Try to get more error details
        if "400" in str(e):
            print("🔍 Investigating 400 error...")
            
            # Check if it's a size issue
            total_size = sum(len(img) for img in images)
            print(f"📊 Total images size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
            
            # Try with smaller images
            print("🔄 Trying with reduced image quality...")
            try:
                # Reduce image quality
                smaller_images = []
                for i, img_bytes in enumerate(images):
                    img = Image.open(io.BytesIO(img_bytes))
                    # Resize to smaller dimensions
                    img = img.resize((img.width // 2, img.height // 2), Image.Resampling.LANCZOS)
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG", optimize=True)
                    smaller_images.append(img_buffer.getvalue())
                    print(f"  Reduced page {i+1}: {len(smaller_images[i])} bytes")
                
                response = client.chat_with_images(
                    model=model,
                    prompt=prompt,
                    image_bytes_list=smaller_images,
                    max_tokens=2000
                )
                print(f"✅ Reduced quality test successful!")
                print(f"📄 Response preview: {response[:200]}...")
                
            except Exception as e2:
                print(f"❌ Reduced quality test also failed: {e2}")

if __name__ == "__main__":
    test_pdf_conversion_debug()