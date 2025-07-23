#!/usr/bin/env python3
"""
Test script for OpenRouter integration with PDF2MD Ollama

This script demonstrates how to use OpenRouter as an external LLM provider
instead of local Ollama for PDF to Markdown conversion.

Setup Instructions:
1. Get an OpenRouter API key from https://openrouter.ai/
2. Set the environment variable: set OPENROUTER_API_KEY=your_api_key_here
3. Install dependencies: pip install -r requirements.txt
4. Run this test script: python test_openrouter.py

Usage Examples:
- Test with image: python src/img2md.py test_image.png -p openrouter
- Test with PDF: python src/pdf2md.py sample.pdf -p openrouter
"""

import os
import sys
import subprocess
from pathlib import Path

def check_openrouter_setup():
    """Check if OpenRouter is properly configured"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set!")
        print("\nTo set up OpenRouter:")
        print("1. Get an API key from https://openrouter.ai/")
        print("2. Set environment variable:")
        print("   Windows: set OPENROUTER_API_KEY=your_api_key_here")
        print("   Linux/Mac: export OPENROUTER_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ OpenRouter API key found: {api_key[:8]}...")
    return True

def test_openrouter_client():
    """Test OpenRouter client directly"""
    try:
        sys.path.append('src')
        from openrouter_client import OpenRouterClient, get_openrouter_model
        
        client = OpenRouterClient()
        print("✅ OpenRouter client initialized successfully")
        
        # Test model mapping
        test_models = ["gemma3:12b", "gemma3:4b", "llama3"]
        print("\n📋 Model mappings:")
        for model in test_models:
            mapped = get_openrouter_model(model)
            print(f"  {model} → {mapped}")
        
        return True
    except Exception as e:
        print(f"❌ OpenRouter client test failed: {e}")
        return False

def test_image_conversion():
    """Test image to markdown conversion with OpenRouter"""
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image '{test_image}' not found, skipping image test")
        return True
    
    try:
        print(f"\n🖼️  Testing image conversion with OpenRouter...")
        result = subprocess.run([
            sys.executable, "src/img2md.py", 
            test_image, 
            "-p", "openrouter",
            "-o", "test_output_openrouter.md"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Image conversion with OpenRouter successful!")
            if os.path.exists("test_output_openrouter.md"):
                with open("test_output_openrouter.md", "r", encoding="utf-8") as f:
                    content = f.read()[:200]
                print(f"📄 Output preview: {content}...")
            return True
        else:
            print(f"❌ Image conversion failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Image conversion timed out")
        return False
    except Exception as e:
        print(f"❌ Image conversion error: {e}")
        return False

def test_pdf_conversion():
    """Test PDF to markdown conversion with OpenRouter"""
    # Look for any PDF file in the current directory
    pdf_files = list(Path(".").glob("*.pdf"))
    if not pdf_files:
        print("⚠️  No PDF files found, skipping PDF test")
        return True
    
    test_pdf = str(pdf_files[0])
    print(f"\n📄 Testing PDF conversion with OpenRouter using: {test_pdf}")
    
    try:
        result = subprocess.run([
            sys.executable, "src/pdf2md.py", 
            test_pdf, 
            "-p", "openrouter",
            "-o", "test_pdf_output_openrouter.md"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ PDF conversion with OpenRouter successful!")
            if os.path.exists("test_pdf_output_openrouter.md"):
                with open("test_pdf_output_openrouter.md", "r", encoding="utf-8") as f:
                    content = f.read()[:200]
                print(f"📄 Output preview: {content}...")
            return True
        else:
            print(f"❌ PDF conversion failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ PDF conversion timed out")
        return False
    except Exception as e:
        print(f"❌ PDF conversion error: {e}")
        return False

def main():
    """Run all OpenRouter tests"""
    print("🧪 Testing OpenRouter Integration for PDF2MD Ollama")
    print("=" * 50)
    
    # Check setup
    if not check_openrouter_setup():
        sys.exit(1)
    
    # Test client
    if not test_openrouter_client():
        sys.exit(1)
    
    # Test conversions
    image_ok = test_image_conversion()
    pdf_ok = test_pdf_conversion()
    
    print("\n" + "=" * 50)
    if image_ok and pdf_ok:
        print("🎉 All OpenRouter tests passed!")
        print("\nYou can now use OpenRouter with any of the conversion scripts:")
        print("  python src/pdf2md.py your_file.pdf -p openrouter")
        print("  python src/img2md.py your_image.png -p openrouter")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()