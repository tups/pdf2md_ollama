import ollama
import base64
import argparse
import sys
import os
from openrouter_client import OpenRouterClient, get_openrouter_model


prompt = "Extract text from this image"
prompt = "Extract all readable text and text chunks from this image" + \
         " and format it as structured Markdown." + \
         " Look in the entire image always and try to retrieve all text!"

def image_to_text(image_path, model="gemma3:12b", prompt=prompt, provider="ollama", request_delay=1.0, max_retries=3):
    """Convert image to text using either Ollama or OpenRouter"""
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    if provider.lower() == "openrouter":
        try:
            client = OpenRouterClient(request_delay=request_delay, max_retries=max_retries)
            openrouter_model = get_openrouter_model(model)
            return client.chat_with_images(openrouter_model, prompt, [image_data])
        except Exception as e:
            print(f"OpenRouter error: {e}")
            print("Make sure OPENROUTER_API_KEY environment variable is set.")
            sys.exit(1)
    else:
        # Default to Ollama
        response = ollama.chat(model=model,
                               messages=[{"role": "user",
                                          "content": prompt,
                                          "images": [image_data]}])
        return response["message"]["content"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to Markdown using LLM via Ollama or OpenRouter')
    parser.add_argument('input_file', help='Path to the input image file')
    parser.add_argument('-o', '--output', default='output.md', help='Output Markdown file (default: output.md)')
    parser.add_argument('-m', '--model', default='gemma3:12b', help='Model to use (default: gemma3:12b)')
    parser.add_argument('-p', '--provider', choices=['ollama', 'openrouter'], default='ollama', 
                       help='LLM provider to use (default: ollama). OpenRouter requires OPENROUTER_API_KEY env var.')
    parser.add_argument('--request-delay', type=float, default=1.0,
                       help='Delay in seconds between OpenRouter requests to avoid rate limiting (default: 1.0)')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Maximum number of retries for rate-limited requests (default: 3)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    print(f"Converting image: {args.input_file}")
    print(f"Using provider: {args.provider}")
    extracted_text = image_to_text(args.input_file, model=args.model, provider=args.provider,
                                   request_delay=args.request_delay, max_retries=args.max_retries)
    
    with open(args.output, "w", encoding="utf-8") as md_file:
        md_file.write(extracted_text)
    print(f"\nMarkdown Conversion Complete! Check `{args.output}`.")
