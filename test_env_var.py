#!/usr/bin/env python3
"""
Diagnostic script to test environment variable reading
"""
import os
import sys

def test_environment_variable():
    """Test if OPENROUTER_API_KEY environment variable is accessible"""
    print("🔍 Testing OPENROUTER_API_KEY environment variable...")
    print("=" * 50)
    
    # Test direct os.getenv
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"os.getenv('OPENROUTER_API_KEY'): {api_key}")
    
    if api_key:
        print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")
        print(f"📏 Length: {len(api_key)} characters")
    else:
        print("❌ API key not found!")
        
    # Test all environment variables containing 'OPENROUTER'
    print("\n🔍 All environment variables containing 'OPENROUTER':")
    openrouter_vars = {k: v for k, v in os.environ.items() if 'OPENROUTER' in k.upper()}
    if openrouter_vars:
        for key, value in openrouter_vars.items():
            print(f"  {key}: {value[:8]}...{value[-4:] if len(value) > 12 else value}")
    else:
        print("  None found")
    
    # Test Python executable and environment
    print(f"\n🐍 Python executable: {sys.executable}")
    print(f"🔧 Python version: {sys.version}")
    
    # Test if we can import the OpenRouter client
    try:
        sys.path.append('src')
        from openrouter_client import OpenRouterClient
        print("✅ OpenRouter client import successful")
        
        # Try to initialize the client
        try:
            client = OpenRouterClient()
            print("✅ OpenRouter client initialization successful")
        except ValueError as e:
            print(f"❌ OpenRouter client initialization failed: {e}")
            
    except ImportError as e:
        print(f"❌ OpenRouter client import failed: {e}")
    
    return api_key is not None

if __name__ == "__main__":
    success = test_environment_variable()
    if not success:
        print("\n💡 Troubleshooting suggestions:")
        print("1. Make sure you set the variable in the same PowerShell session:")
        print("   set OPENROUTER_API_KEY=your_api_key_here")
        print("2. Try using $env: syntax:")
        print("   $env:OPENROUTER_API_KEY='your_api_key_here'")
        print("3. Restart PowerShell and set the variable again")
        print("4. Use the full path to python.exe:")
        print("   .venv\\Scripts\\python.exe test_env_var.py")