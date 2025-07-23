import requests
import base64
import os
import json
import time
import random
from typing import List, Optional

class OpenRouterClient:
    """Client for OpenRouter API with vision support and rate limiting"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 request_delay: float = 1.0,
                 max_retries: int = 3,
                 backoff_factor: float = 2.0):
        """
        Initialize OpenRouter client with rate limiting
        
        Args:
            api_key: OpenRouter API key
            request_delay: Delay in seconds between requests (default: 1.0)
            max_retries: Maximum number of retries for 429 errors (default: 3)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pdf2md-ollama",
            "X-Title": "PDF2MD Ollama"
        }
        
        # Rate limiting configuration
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.last_request_time = 0
    
    def encode_images_to_base64(self, image_bytes_list: List[bytes]) -> List[str]:
        """Convert list of image bytes to base64 encoded strings"""
        return [base64.b64encode(img_bytes).decode('utf-8') for img_bytes in image_bytes_list]
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting delay between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            print(f"⏱️  Rate limiting: waiting {sleep_time:.1f}s before next request...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def chat_with_images(self, 
                        model: str, 
                        prompt: str, 
                        image_bytes_list: List[bytes],
                        max_tokens: int = 4000) -> str:
        """
        Send images and prompt to OpenRouter vision model with rate limiting
        
        Args:
            model: Model name (e.g., 'google/gemini-pro-vision', 'anthropic/claude-3-haiku:beta')
            prompt: Text prompt for image analysis
            image_bytes_list: List of image data as bytes
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        
        # Apply rate limiting delay
        self._wait_for_rate_limit()
        
        # Encode images to base64
        base64_images = self.encode_images_to_base64(image_bytes_list)
        
        # Prepare message content with images
        content = [{"type": "text", "text": prompt}]
        
        # Add images to content
        for img_b64 in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        # Retry logic with exponential backoff for rate limiting
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=120
                )
                
                # Handle rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        # Calculate exponential backoff delay with jitter
                        backoff_delay = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                        result = response.json()
                        print(
                            f"🚫 Rate limited (429): {result.get('error', {}).get('message', 'No error message')}. Retrying in {backoff_delay:.1f}s... (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(backoff_delay)
                        continue
                    else:
                        raise Exception(f"OpenRouter API request failed: 429 Too Many Requests after {self.max_retries} retries")
                
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries and "429" in str(e):
                    # Handle 429 errors that come through as RequestException
                    backoff_delay = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                    print(f"🚫 Rate limited. Retrying in {backoff_delay:.1f}s... (attempt {attempt + 1}/{self.max_retries + 1})")
                    time.sleep(backoff_delay)
                    continue
                else:
                    raise Exception(f"OpenRouter API request failed: {str(e)}")
            except KeyError as e:
                raise Exception(f"Unexpected response format from OpenRouter: {str(e)}")
        
        # This should never be reached, but just in case
        raise Exception("Maximum retries exceeded")
    
    def get_available_models(self) -> List[dict]:
        """Get list of available models from OpenRouter"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch models: {str(e)}")

# Model mappings from Ollama to OpenRouter
OPENROUTER_MODEL_MAPPING = {
    "gemma3:12b": "google/gemma-3-27b-it:free",  # Working free vision model
    "gemma3:4b": "google/gemma-3-27b-it:free",   # Same model for smaller version
    "llama3": "meta-llama/llama-3-8b-instruct",
    "llama3:70b": "meta-llama/llama-3-70b-instruct",
    # Vision-capable models for image processing
    "vision": "meta-llama/llama-3.2-11b-vision-instruct:free",
    "claude-vision": "anthropic/claude-3-haiku:beta",
    "gpt4-vision": "openai/gpt-4o-mini"
}

def get_openrouter_model(ollama_model: str) -> str:
    """Map Ollama model name to OpenRouter equivalent"""
    # For vision tasks, we'll use LLaMA 3.2 11B Vision as default (free and vision-capable)
    if ollama_model.startswith("gemma"):
        return "google/gemma-3-27b-it:free"
    return OPENROUTER_MODEL_MAPPING.get(ollama_model, "google/gemma-3-27b-it:free")