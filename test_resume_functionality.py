#!/usr/bin/env python3
"""
Test script to verify resume functionality
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

def create_partial_output_file(filename, completed_pages):
    """Create a partial output file with some completed pages"""
    with open(filename, 'w', encoding='utf-8') as f:
        for page_num in completed_pages:
            if page_num > min(completed_pages):
                f.write("\n\n---\n\n")
            f.write(f"## Page {page_num}\n\nContent for page {page_num}")

def test_get_completed_pages():
    """Test the get_completed_pages function"""
    print("Testing get_completed_pages function...")
    
    from pdf2md import get_completed_pages
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Test with non-existent file
        completed = get_completed_pages("non_existent_file.md")
        assert completed == set(), f"Expected empty set, got {completed}"
        print("✓ Non-existent file test passed")
        
        # Test with partial output file
        create_partial_output_file(temp_filename, [1, 3, 5])
        completed = get_completed_pages(temp_filename)
        expected = {1, 3, 5}
        assert completed == expected, f"Expected {expected}, got {completed}"
        print("✓ Partial output file test passed")
        
        # Test with sequential pages
        create_partial_output_file(temp_filename, [1, 2, 3, 4])
        completed = get_completed_pages(temp_filename)
        expected = {1, 2, 3, 4}
        assert completed == expected, f"Expected {expected}, got {completed}"
        print("✓ Sequential pages test passed")
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

def test_resume_functionality():
    """Test that resume functionality works correctly"""
    print("\nTesting resume functionality...")
    
    from pdf2md import query_gemma3_with_images_progressive
    
    # Create test images (5 pages)
    test_images = [create_test_image() for _ in range(5)]
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Create partial output (pages 1-2 already completed)
        create_partial_output_file(temp_filename, [1, 2])
        
        # Mock ollama.chat to return predictable responses
        mock_responses = [
            {"message": {"content": "Content for page 3"}},
            {"message": {"content": "Content for page 4"}},
            {"message": {"content": "Content for page 5"}}
        ]
        
        with patch('pdf2md.ollama.chat') as mock_chat:
            mock_chat.side_effect = mock_responses
            
            # Test resuming from page 3
            query_gemma3_with_images_progressive(
                test_images, 
                temp_filename, 
                model="test-model", 
                provider="ollama",
                start_page=3
            )
            
            # Verify the output file contains all pages
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print("Generated content:")
            print(content)
            print("\n" + "="*50)
            
            # Verify all pages are present
            for page_num in range(1, 6):
                assert f"## Page {page_num}" in content, f"Page {page_num} header not found"
                assert f"Content for page {page_num}" in content, f"Page {page_num} content not found"
            
            # Verify separators are present
            assert content.count("---") >= 3, "Not enough page separators found"
            
            print("✓ Resume functionality test passed!")
            print("✓ All pages are present in the output")
            print("✓ Content structure is correct")
            
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

def test_start_page_validation():
    """Test start page validation"""
    print("\nTesting start page validation...")
    
    from pdf2md import query_gemma3_with_images_progressive
    
    # Create test images (3 pages)
    test_images = [create_test_image() for _ in range(3)]
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Test with start_page > total pages (should print error and return)
        print("Testing start_page > total pages...")
        query_gemma3_with_images_progressive(
            test_images, 
            temp_filename, 
            model="test-model", 
            provider="ollama",
            start_page=10  # Greater than 3 pages
        )
        
        # File should be empty or not created since function returns early
        if os.path.exists(temp_filename):
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                assert content == "", "File should be empty when start_page > total pages"
        
        print("✓ Start page validation test passed!")
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

if __name__ == "__main__":
    print("Testing Resume Functionality")
    print("=" * 40)
    
    try:
        test_get_completed_pages()
        test_resume_functionality()
        test_start_page_validation()
        
        print("\n" + "=" * 40)
        print("✅ All resume functionality tests passed!")
        print("\nThe resume functionality is working correctly:")
        print("- Can detect already completed pages")
        print("- Can resume from a specific page number")
        print("- Validates start page parameter")
        print("- Handles file opening modes correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)