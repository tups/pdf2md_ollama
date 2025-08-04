#!/usr/bin/env python3
"""
Test script to verify progressive output functionality
"""
import os
import sys
import tempfile
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_image():
    """Create a simple test image as bytes"""
    img = Image.new('RGB', (100, 100), color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def test_progressive_output():
    """Test that progressive output writes pages incrementally"""
    print("Testing progressive output functionality...")
    
    # Import after adding src to path
    from pdf2md import query_gemma3_with_images_progressive
    
    # Create test images
    test_images = [create_test_image() for _ in range(3)]
    
    # Mock ollama.chat to return predictable responses
    mock_responses = [
        {"message": {"content": "Content for page 1"}},
        {"message": {"content": "Content for page 2"}},
        {"message": {"content": "Content for page 3"}}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        with patch('pdf2md.ollama.chat') as mock_chat:
            mock_chat.side_effect = mock_responses
            
            # Test progressive output
            query_gemma3_with_images_progressive(
                test_images, 
                temp_filename, 
                model="test-model", 
                provider="ollama"
            )
            
            # Verify the output file was created and contains expected content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print("Generated content:")
            print(content)
            print("\n" + "="*50)
            
            # Verify structure
            assert "## Page 1" in content, "Page 1 header not found"
            assert "## Page 2" in content, "Page 2 header not found"
            assert "## Page 3" in content, "Page 3 header not found"
            assert "Content for page 1" in content, "Page 1 content not found"
            assert "Content for page 2" in content, "Page 2 content not found"
            assert "Content for page 3" in content, "Page 3 content not found"
            assert "---" in content, "Page separators not found"
            
            print("✓ Progressive output test passed!")
            print("✓ All pages were written with proper headers and separators")
            print("✓ Content structure is correct")
            
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

if __name__ == "__main__":
    test_progressive_output()