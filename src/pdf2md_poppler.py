import os
import tempfile
import subprocess
from pathlib import Path

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

def query_gemma3_with_images(image_bytes_list, model="gemma3:12b", prompt=prompt):
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

    pdf_path = "mypdf.pdf"  # Replace with your PDF file
    images = convert_pdf_to_images(pdf_path)

    if images:
        print(f"Converted {len(images)} pages to images.")
    
        extracted_text = query_gemma3_with_images(images)
    
        with open("output.md", "w", encoding="utf-8") as md_file:
            md_file.write(extracted_text)
        print("\nMarkdown Conversion Complete! Check `output.md`.")
    else:
        print("No images found in the PDF.")
