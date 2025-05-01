import ollama
import base64


prompt = "Extract text from this image"
prompt = "Extract all readable text and text chunks from this image" + \
         " and format it as structured Markdown." + \
         " Look in the entire image always and try to retrieve all text!"

def image_to_text(image_path, model="gemma3:12b", prompt=prompt):
    with(open(image_path, "rb") as f:
        image_data = f.read()
    response = ollama.chat(model=model,
                           messages=[{"role": "user",
                                      "content": prompt,
                                      "images": [image_data]}])
    return response["message"]["content"]
