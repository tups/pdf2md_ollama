import os
import tempfile
import subprocess
import argparse
import sys
import ollama
from pathlib import Path
from openrouter_client import OpenRouterClient, get_openrouter_model

def convert_pdf_to_images(pdf_path, dpi=300):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_prefix = os.path.join(tmpdir, "page")

        # The Poppler's pdftoppm call
        subprocess.run([
            "pdftoppm",
            "-png",
            "-r", str(dpi),
            pdf_path,
            output_prefix
        ], check=True)

        # Collect all generated PNG images as byte arrays
        png_files = sorted(Path(tmpdir).glob("*.png"))
        images_bytes = [Path(p).read_bytes() for p in png_files]

        return images_bytes

prompt = "Extract all readable text from these images and format it as structured Markdown."

prompt = "Extract all readable text and text chunks from this image" + \
         " and format it as structured Markdown." + \
         " Look in the entire image always and try to retrieve all text!"

def query_gemma3_with_images(image_bytes_list, model="gemma3:12b", prompt=prompt, provider="ollama", request_delay=1.0, max_retries=3):
    """Query LLM with images using either Ollama or OpenRouter"""
    if provider.lower() == "openrouter":
        try:
            client = OpenRouterClient(request_delay=request_delay, max_retries=max_retries)
            openrouter_model = get_openrouter_model(model)
            
            # Process images one by one for OpenRouter (some models don't support multiple images)
            all_responses = []
            for i, image_bytes in enumerate(image_bytes_list):
                print(f"Processing page {i + 1}/{len(image_bytes_list)} with OpenRouter...")
                page_prompt = f"{prompt}\n\nThis is page {i + 1} of {len(image_bytes_list)}."
                response = client.chat_with_images(openrouter_model, page_prompt, [image_bytes])
                all_responses.append(f"## Page {i + 1}\n\n{response}")
            
            # Combine all responses
            return "\n\n---\n\n".join(all_responses)
            
        except Exception as e:
            print(f"OpenRouter error: {e}")
            print("Make sure OPENROUTER_API_KEY environment variable is set.")
            sys.exit(1)
    else:
        # Default to Ollama (supports multiple images)
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": image_bytes_list
            }]
        )
        return response["message"]["content"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown using Poppler and LLM via Ollama or OpenRouter')
    parser.add_argument('input_file', help='Path to the input PDF file')
    parser.add_argument('-o', '--output', default='output.md', help='Output Markdown file (default: output.md)')
    parser.add_argument('-m', '--model', default='gemma3:12b', help='Model to use (default: gemma3:12b)')
    parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for image conversion (default: 300)')
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
    
    print(f"Converting PDF: {args.input_file}")
    print(f"Using provider: {args.provider}")
    images = convert_pdf_to_images(args.input_file, dpi=args.dpi)

    if images:
        print(f"Converted {len(images)} pages to images.")
    
        extracted_text = query_gemma3_with_images(images, model=args.model, provider=args.provider,
                                                  request_delay=args.request_delay, max_retries=args.max_retries)
    
        with open(args.output, "w", encoding="utf-8") as md_file:
            md_file.write(extracted_text)
        print(f"\nMarkdown Conversion Complete! Check `{args.output}`.")
    else:
        print("No images found in the PDF.")
