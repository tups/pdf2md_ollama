import fitz  # PyMuPDF for PDFs
import ollama
import io
import os
import argparse
import sys
import re
from PIL import Image
from openrouter_client import OpenRouterClient, get_openrouter_model

def convert_pdf_to_images(pdf_path):
    images = []
    doc = fitz.open(pdf_path)  # Open the PDF
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()  # Render page to pixel map
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convert to PIL image
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")  # Save as in-memory PNG
        images.append(img_buffer.getvalue())  # Raw PNG bytes
    return images

def get_completed_pages(output_file):
    """Parse existing output file to detect which pages have already been processed"""
    if not os.path.exists(output_file):
        return set()
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all page headers like "## Page 1", "## Page 2", etc.
        page_pattern = r'^## Page (\d+)$'
        matches = re.findall(page_pattern, content, re.MULTILINE)
        completed_pages = set(int(page_num) for page_num in matches)
        
        return completed_pages
    except Exception as e:
        print(f"Warning: Could not parse existing output file: {e}")
        return set()

prompt = "Extract all readable text from these images and format it as structured Markdown."
prompt = "Extract all readable text and text chunks from this image" + \
         " and format it as structured Markdown." + \
         " Look in the entire image always and try to retrieve all text!"

def query_gemma3_with_images_progressive(image_bytes_list, output_file, model="gemma3:12b", prompt=prompt, provider="ollama", request_delay=1.0, max_retries=3, start_page=1):
    """Query LLM with images using either Ollama or OpenRouter, writing output progressively"""
    
    # Determine if we're resuming from a specific page
    completed_pages = get_completed_pages(output_file)
    is_resuming = start_page > 1 or len(completed_pages) > 0
    
    # Determine file opening mode
    file_mode = "a" if is_resuming and os.path.exists(output_file) else "w"
    
    # Validate start_page
    if start_page < 1:
        start_page = 1
    if start_page > len(image_bytes_list):
        print(f"Error: Start page {start_page} is greater than total pages {len(image_bytes_list)}")
        return
    
    # Show resume information
    if is_resuming:
        print(f"Resuming from page {start_page}. Found {len(completed_pages)} completed pages in existing output.")
        if completed_pages:
            print(f"Already completed pages: {sorted(completed_pages)}")
    
    if provider.lower() == "openrouter":
        try:
            client = OpenRouterClient(request_delay=request_delay, max_retries=max_retries)
            openrouter_model = get_openrouter_model(model)
            
            # Process images one by one for OpenRouter and write progressively
            with open(output_file, file_mode, encoding="utf-8") as f:
                for i, image_bytes in enumerate(image_bytes_list):
                    page_num = i + 1
                    
                    # Skip pages before start_page or already completed pages
                    if page_num < start_page or page_num in completed_pages:
                        if page_num < start_page:
                            print(f"Skipping page {page_num} (before start page {start_page})")
                        else:
                            print(f"Skipping page {page_num} (already completed)")
                        continue
                    
                    print(f"Processing page {page_num}/{len(image_bytes_list)} with OpenRouter...")
                    page_prompt = f"{prompt}\n\nThis is page {page_num} of {len(image_bytes_list)}."
                    response = client.chat_with_images(openrouter_model, page_prompt, [image_bytes])
                    
                    # Write page content immediately
                    # Add separator if this is not the first page being written to the file
                    if file_mode == "a" or (file_mode == "w" and page_num > start_page):
                        f.write("\n\n---\n\n")
                    f.write(f"## Page {page_num}\n\n{response}")
                    f.flush()  # Ensure content is written immediately
                    print(f"✓ Page {page_num} written to {output_file}")
            
        except Exception as e:
            print(f"OpenRouter error: {e}")
            print("Make sure OPENROUTER_API_KEY environment variable is set.")
            sys.exit(1)
    else:
        # For Ollama, process pages individually to enable progressive output
        with open(output_file, file_mode, encoding="utf-8") as f:
            for i, image_bytes in enumerate(image_bytes_list):
                page_num = i + 1
                
                # Skip pages before start_page or already completed pages
                if page_num < start_page or page_num in completed_pages:
                    if page_num < start_page:
                        print(f"Skipping page {page_num} (before start page {start_page})")
                    else:
                        print(f"Skipping page {page_num} (already completed)")
                    continue
                
                print(f"Processing page {page_num}/{len(image_bytes_list)} with Ollama...")
                response = ollama.chat(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": f"{prompt}\n\nThis is page {page_num} of {len(image_bytes_list)}.",
                        "images": [image_bytes]
                    }]
                )
                
                # Write page content immediately
                # Add separator if this is not the first page being written to the file
                if file_mode == "a" or (file_mode == "w" and page_num > start_page):
                    f.write("\n\n---\n\n")
                f.write(f"## Page {page_num}\n\n{response['message']['content']}")
                f.flush()  # Ensure content is written immediately
                print(f"✓ Page {page_num} written to {output_file}")

def query_gemma3_with_images(image_bytes_list, model="gemma3:12b", prompt=prompt, provider="ollama", request_delay=1.0, max_retries=3):
    """Query LLM with images using either Ollama or OpenRouter (legacy batch mode)"""
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
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown using LLM via Ollama or OpenRouter')
    parser.add_argument('input_file', help='Path to the input PDF file')
    parser.add_argument('-o', '--output', default='output.md', help='Output Markdown file (default: output.md)')
    parser.add_argument('-m', '--model', default='gemma3:12b', help='Model to use (default: gemma3:12b)')
    parser.add_argument('-p', '--provider', choices=['ollama', 'openrouter'], default='ollama', 
                       help='LLM provider to use (default: ollama). OpenRouter requires OPENROUTER_API_KEY env var.')
    parser.add_argument('--request-delay', type=float, default=1.0,
                       help='Delay in seconds between OpenRouter requests to avoid rate limiting (default: 1.0)')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='Maximum number of retries for rate-limited requests (default: 3)')
    parser.add_argument('--progressive', action='store_true',
                       help='Write output progressively page by page (default: enabled for large documents)')
    parser.add_argument('--start-page', type=int, default=1,
                       help='Page number to start processing from (useful for resuming after failures, default: 1)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    print(f"Converting PDF: {args.input_file}")
    print(f"Using provider: {args.provider}")
    images = convert_pdf_to_images(args.input_file)

    if images:
        print(f"Converted {len(images)} pages to images.")
        
        # Use progressive output by default for documents with more than 1 page, or if explicitly requested
        use_progressive = args.progressive or len(images) > 1
        
        if use_progressive:
            print(f"Using progressive output mode - writing pages as they are processed...")
            query_gemma3_with_images_progressive(images, args.output, model=args.model, provider=args.provider, 
                                                request_delay=args.request_delay, max_retries=args.max_retries, 
                                                start_page=args.start_page)
            print(f"\nMarkdown Conversion Complete! Check `{args.output}`.")
        else:
            # Fallback to batch mode for single pages
            extracted_text = query_gemma3_with_images(images, model=args.model, provider=args.provider, 
                                                      request_delay=args.request_delay, max_retries=args.max_retries)
        
            with open(args.output, "w", encoding="utf-8") as md_file:
                md_file.write(extracted_text)
            print(f"\nMarkdown Conversion Complete! Check `{args.output}`.")
    else:
        print("No images found in the PDF.")
