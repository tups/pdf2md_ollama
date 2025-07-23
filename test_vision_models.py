#!/usr/bin/env python3
"""
Test script to find working vision models for the user's API key
"""
import sys
import os
import requests
import base64
from PIL import Image
import io

# Add src to path
sys.path.append('src')
from openrouter_client import OpenRouterClient

def create_simple_test_image():
    """Create a simple test image with text"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple white image with black text
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((10, 30), "Hello World! Test Image", fill='black', font=font)
    draw.text((10, 50), "Can you read this text?", fill='black', font=font)
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def test_specific_vision_models():
    """Test specific vision models that might work with free tier"""
    print("🔍 Testing specific vision models for free tier compatibility...")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        return None
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Models to test - focusing on free/accessible ones
    test_models = [
        # Free models that might support vision
        "google/gemma-2-9b-it:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "meta-llama/llama-3.2-90b-vision-instruct:free",
        "qwen/qwen-2-vl-7b-instruct:free",
        "microsoft/phi-3.5-vision-instruct:free",
        # Potentially accessible vision models
        "google/gemini-flash-1.5",
        "google/gemini-2.5-flash-lite",
        "anthropic/claude-3-haiku",
        "openai/gpt-4o-mini",
    ]
    
    # Create test image
    test_image = create_simple_test_image()
    prompt = "What text do you see in this image? Please extract all readable text."
    
    client = OpenRouterClient()
    working_models = []
    
    for model in test_models:
        print(f"\n🧪 Testing: {model}")
        try:
            response = client.chat_with_images(
                model=model,
                prompt=prompt,
                image_bytes_list=[test_image],
                max_tokens=200
            )
            print(f"✅ SUCCESS with {model}")
            print(f"📄 Response: {response[:150]}...")
            working_models.append(model)
            
            # If we find a working vision model, we can stop
            if "hello world" in response.lower() or "test image" in response.lower():
                print(f"🎉 Found working vision model: {model}")
                return model
                
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"❌ 403 Forbidden - {model} (not accessible with current API key)")
            elif "400" in error_msg:
                print(f"❌ 400 Bad Request - {model} (invalid model or request)")
            elif "text-only" in error_msg.lower():
                print(f"❌ Text-only model - {model}")
            else:
                print(f"❌ Error with {model}: {error_msg[:100]}...")
    
    if working_models:
        print(f"\n✅ Working models found: {working_models}")
        return working_models[0]
    else:
        print("\n❌ No working vision models found")
        return None

def test_direct_api_call():
    """Test direct API call to understand the issue better"""
    print("\n🔍 Testing direct API call...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return
    
    # Try a simple text-only request first
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/pdf2md-ollama",
        "X-Title": "PDF2MD Ollama"
    }
    
    # Simple text request
    payload = {
        "model": "google/gemma-2-9b-it:free",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you respond to this message?"
            }
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Text-only API call successful")
            result = response.json()
            print(f"📄 Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"❌ Text-only API call failed: {response.status_code}")
            if response.content:
                print(f"Error: {response.json()}")
                
    except Exception as e:
        print(f"❌ Direct API call error: {e}")

if __name__ == "__main__":
    working_model = test_specific_vision_models()
    test_direct_api_call()
    
    if working_model:
        print(f"\n🎯 RECOMMENDATION: Update model mapping to use: {working_model}")
    else:
        print("\n💡 SUGGESTION: The API key might not have access to vision models.")
        print("   Try getting a different API key or check OpenRouter pricing.")