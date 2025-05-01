import fitz  # PyMuPDF for PDFs
import ollama
import io
from PIL import Image

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
