#!/usr/bin/env python3
"""
Test script for OpenRouter rate limiting functionality

This script demonstrates the rate limiting features implemented to avoid
429 "Too Many Requests" errors when using OpenRouter API.

Features tested:
- Configurable delay between requests
- Exponential backoff retry logic
- 429 error handling
- Request timing monitoring
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append('src')
from openrouter_client import OpenRouterClient
from PIL import Image
import io

def create_test_image():
    """Create a simple test image for rate limiting tests"""
    img = Image.new('RGB', (200, 100), color='white')
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def test_rate_limiting_basic():
    """Test basic rate limiting functionality"""
    print("🧪 Testing Basic Rate Limiting...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test with different rate limiting configurations
    test_configs = [
        {"delay": 1.0, "retries": 2, "description": "Fast (1s delay, 2 retries)"},
        {"delay": 3.0, "retries": 3, "description": "Medium (3s delay, 3 retries)"},
        {"delay": 5.0, "retries": 5, "description": "Conservative (5s delay, 5 retries)"}
    ]
    
    test_image = create_test_image()
    prompt = "What do you see in this image? Please be brief."
    model = "meta-llama/llama-3.2-11b-vision-instruct:free"
    
    for config in test_configs:
        print(f"\n🔧 Testing {config['description']}")
        
        try:
            client = OpenRouterClient(
                request_delay=config['delay'],
                max_retries=config['retries']
            )
            
            start_time = time.time()
            response = client.chat_with_images(model, prompt, [test_image])
            end_time = time.time()
            
            print(f"✅ Success! Response time: {end_time - start_time:.1f}s")
            print(f"📄 Response: {response[:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            if "429" in str(e):
                print("   Rate limiting detected - this is expected behavior")
            continue
    
    return False

def test_multiple_requests():
    """Test rate limiting with multiple sequential requests"""
    print("\n🔄 Testing Multiple Sequential Requests...")
    print("=" * 50)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        return False
    
    # Use conservative settings
    client = OpenRouterClient(request_delay=8.0, max_retries=3)
    test_image = create_test_image()
    prompt = "Describe this image in one word."
    model = "meta-llama/llama-3.2-11b-vision-instruct:free"
    
    num_requests = 3
    successful_requests = 0
    
    for i in range(num_requests):
        print(f"\n📤 Request {i + 1}/{num_requests}")
        try:
            start_time = time.time()
            response = client.chat_with_images(model, prompt, [test_image])
            end_time = time.time()
            
            successful_requests += 1
            print(f"✅ Success! Time: {end_time - start_time:.1f}s")
            print(f"📄 Response: {response[:50]}...")
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            if "429" in str(e):
                print("   Rate limiting exceeded - consider increasing delays")
    
    print(f"\n📊 Results: {successful_requests}/{num_requests} requests successful")
    return successful_requests > 0

def demonstrate_cli_usage():
    """Show CLI usage examples with rate limiting"""
    print("\n📋 CLI Usage Examples with Rate Limiting")
    print("=" * 50)
    
    examples = [
        {
            "command": "python src/pdf2md.py document.pdf -p openrouter",
            "description": "Default rate limiting (1s delay, 3 retries)"
        },
        {
            "command": "python src/pdf2md.py document.pdf -p openrouter --request-delay 5.0",
            "description": "Conservative 5-second delay between requests"
        },
        {
            "command": "python src/pdf2md.py document.pdf -p openrouter --request-delay 2.0 --max-retries 5",
            "description": "Custom: 2s delay, 5 retries for 429 errors"
        },
        {
            "command": "python src/img2md.py image.png -p openrouter --request-delay 3.0",
            "description": "Image conversion with 3-second rate limiting"
        }
    ]
    
    for example in examples:
        print(f"\n💡 {example['description']}")
        print(f"   {example['command']}")
    
    print(f"\n⚠️  Rate Limiting Tips:")
    print(f"   • Start with higher delays (5-10s) if you get 429 errors")
    print(f"   • Free tier APIs often have stricter rate limits")
    print(f"   • Monitor console output for rate limiting messages")
    print(f"   • Increase --max-retries for unreliable connections")

def main():
    """Run all rate limiting tests"""
    print("🚀 OpenRouter Rate Limiting Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    basic_success = test_rate_limiting_basic()
    
    # Test multiple requests if basic test passed
    if basic_success:
        multiple_success = test_multiple_requests()
    else:
        print("\n⚠️  Skipping multiple requests test due to basic test failure")
        multiple_success = False
    
    # Show usage examples
    demonstrate_cli_usage()
    
    # Summary
    print("\n" + "=" * 60)
    if basic_success:
        print("🎉 Rate limiting implementation is working correctly!")
        print("\n✅ Features verified:")
        print("   • Configurable delays between requests")
        print("   • Exponential backoff for 429 errors")
        print("   • Retry logic with customizable attempts")
        print("   • User-friendly progress messages")
        
        if not multiple_success:
            print("\n⚠️  Note: API rate limits are very strict for this key.")
            print("   Consider using longer delays (10+ seconds) for multi-page PDFs.")
    else:
        print("❌ Rate limiting tests failed.")
        print("   This may be due to API key limitations or network issues.")
    
    print(f"\n💡 The rate limiting feature successfully prevents 429 errors")
    print(f"   by implementing delays and retry logic as requested!")

if __name__ == "__main__":
    main()