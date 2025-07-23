#!/usr/bin/env python3
"""
Simple test to verify img2md functionality works.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_img2md_basic():
    """Test basic img2md functionality with existing test image."""
    try:
        import img2md
        
        # Use the existing test image
        test_image_path = "test_image.png"
        
        if not Path(test_image_path).exists():
            print(f"Test image {test_image_path} not found. Skipping test.")
            return False
        
        print(f"Testing img2md with {test_image_path}...")
        
        # Test with available model
        result = img2md.image_to_text(
            test_image_path, 
            model="JetBrains/Mellum-4b-base:latest"
        )
        
        print("✓ img2md test successful!")
        print(f"Result length: {len(result)} characters")
        print("First 100 characters:")
        print(result[:100] + "..." if len(result) > 100 else result)
        
        return True
        
    except Exception as e:
        print(f"✗ img2md test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple PDF2MD Test ===")
    success = test_img2md_basic()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")