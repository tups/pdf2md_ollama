#!/usr/bin/env python3
"""
Debug script for OpenRouter API issues
"""
import sys
import os
import requests
import base64
from PIL import Image
import io

# Add src to path
sys.path.append('src')
from openrouter_client import OpenRouterClient, get_openrouter_model

def create_test_image():
    """Create a simple test image"""
    # Create a simple white image with black text
    img = Image.new('RGB', (200, 100), color='white')
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    return img_buffer.getvalue()

def test_openrouter_models():
    """Test different OpenRouter models"""
    print("🧪 Testing OpenRouter API with different models...")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set!")
        return
    
    print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test models to try
    test_models = [
        "google/gemini-pro-vision",
        "google/gemini-flash-1.5",
        "anthropic/claude-3-haiku:beta",
        "openai/gpt-4o-mini",
        "google/gemma-2-9b-it:free"
    ]
    
    # Create test image
    test_image = create_test_image()
    prompt = "What do you see in this image?"
    
    client = OpenRouterClient()
    
    for model in test_models:
        print(f"\n🔍 Testing model: {model}")
        try:
            # Test with a simple request first
            response = client.chat_with_images(
                model=model,
                prompt=prompt,
                image_bytes_list=[test_image],
                max_tokens=100
            )
            print(f"✅ Success with {model}")
            print(f"📄 Response: {response[:100]}...")
            break  # If successful, we found a working model
            
        except Exception as e:
            print(f"❌ Failed with {model}: {str(e)}")
            
            # If it's a 400 error, let's get more details
            if "400" in str(e):
                print("   Trying to get more error details...")
                try:
                    # Make a direct request to see the full error
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/pdf2md-ollama",
                        "X-Title": "PDF2MD Ollama"
                    }
                    
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64.b64encode(test_image).decode('utf-8')}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 100
                    }
                    
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code != 200:
                        error_detail = response.json() if response.content else "No error details"
                        print(f"   Error details: {error_detail}")
                        
                except Exception as detail_error:
                    print(f"   Could not get error details: {detail_error}")
    
    # Test the current model mapping
    print(f"\n🔍 Current model mapping for gemma3:12b:")
    mapped_model = get_openrouter_model("gemma3:12b")
    print(f"   gemma3:12b → {mapped_model}")

def test_available_models():
    """Test getting available models from OpenRouter"""
    print("\n🔍 Testing available models from OpenRouter...")
    try:
        client = OpenRouterClient()
        models = client.get_available_models()
        
        print(f"✅ Found {len(models)} available models")
        
        # Look for vision-capable models
        vision_models = []
        for model in models:
            model_id = model.get('id', '')
            if any(keyword in model_id.lower() for keyword in ['vision', 'gemini', 'claude', 'gpt-4']):
                vision_models.append(model_id)
        
        print(f"\n📋 Vision-capable models found ({len(vision_models)}):")
        for model in vision_models[:10]:  # Show first 10
            print(f"   {model}")
        
        if len(vision_models) > 10:
            print(f"   ... and {len(vision_models) - 10} more")
            
    except Exception as e:
        print(f"❌ Failed to get available models: {e}")

if __name__ == "__main__":
    test_openrouter_models()
    test_available_models()