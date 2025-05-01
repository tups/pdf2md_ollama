import fitz  # PyMuPDF
import ollama
import io
from PIL import Image

def convert_pdf_to_images(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        images.append(buf.getvalue())
    return images

def query_gemma3_with_images(image_bytes_list, model="gemma3:12b", prompt="Extract all readable text from these images and format it as structured Markdown."):
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
    pdf_path = "mypdf.pdf"
    images = convert_pdf_to_images(pdf_path)
    if images:
        print(f"Converted {len(images)} pages to images.")
        result = query_gemma3_with_images(images)
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result)
        print("Markdown Conversion Complete! Check `output.md`.")
    else:
        print("No images found in the PDF.")
