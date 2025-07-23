# Convert PDFs to Markdown with Local or External LLMs

Fast, private, and free PDF-to-Markdown conversion using either local LLMs (via Ollama) or external LLM infrastructure (via OpenRouter). Choose between complete privacy with local models or free external access to powerful vision models like Gemma 3 12B.

**Article**: [Convert PDFs to Markdown using Local LLMs — Fast, Private, and Free](https://medium.com/data-science-collective/convert-pdfs-to-markdown-using-local-llms-c5232f3b50fc?sk=9b0036a7ff93a1c48bae7dd8216dc671)

---

## Installation (Option 1: Using [uv](https://github.com/astral-sh/uv))

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install -r requirements.txt
```
Then run:
```bash
uv run src/pdf2md.py
```

## Installation (Option 2: Using pip)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Then run:
```bash
python src/pdf2md.py
```

---

## 🌐 OpenRouter Integration (NEW!)

**Use external LLM infrastructure for FREE!** Instead of running models locally, you can now use OpenRouter to access powerful vision models like Gemma 3 12B through external infrastructure at no cost.

### Benefits of OpenRouter:
- ✅ **Free access** to Gemma 3 12B and other powerful vision models
- ✅ **No local GPU required** - runs on any machine
- ✅ **No model downloads** - instant access
- ✅ **Multiple model options** - Gemini Pro Vision, Claude 3, GPT-4 Vision
- ✅ **Same interface** - just add `-p openrouter` to any command

### Setup OpenRouter:

1. **Get a free API key** from [OpenRouter.ai](https://openrouter.ai/)
2. **Set environment variable:**
   ```bash
   # Windows
   set OPENROUTER_API_KEY=your_api_key_here
   $env:OPENROUTER_API_KEY='your_api_key_here'
   
   # Linux/Mac
   export OPENROUTER_API_KEY=your_api_key_here
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage with OpenRouter:

```bash
# Convert PDF using OpenRouter (external infrastructure)
python src/pdf2md.py your_file.pdf -p openrouter

# Convert image using OpenRouter
python src/img2md.py your_image.png -p openrouter

# Use different implementations with OpenRouter
python src/pdf2md_poppler.py your_file.pdf -p openrouter
python src/pdf2md_poppler_short.py your_file.pdf -p openrouter
```

### 🚦 Rate Limiting (NEW!)

**Avoid 429 "Too Many Requests" errors** with built-in rate limiting features:

```bash
# Use custom delays to avoid rate limiting
python src/pdf2md.py your_file.pdf -p openrouter --request-delay 5.0

# Configure retry behavior for 429 errors
python src/pdf2md.py your_file.pdf -p openrouter --max-retries 5

# Combine both for maximum reliability
python src/pdf2md.py your_file.pdf -p openrouter --request-delay 3.0 --max-retries 5
```

**Rate Limiting Features:**
- ⏱️ **Configurable delays** between requests (default: 1.0s)
- 🔄 **Exponential backoff** for 429 error retries
- 📊 **Progress monitoring** with user-friendly messages
- ⚙️ **Customizable retry limits** (default: 3 attempts)

**Recommended Settings:**
- **Light usage**: `--request-delay 2.0` (2 seconds between requests)
- **Heavy usage**: `--request-delay 5.0 --max-retries 5` (5 seconds + 5 retries)
- **Very strict APIs**: `--request-delay 10.0` (10 seconds between requests)

### Test OpenRouter Integration:

```bash
# Test basic OpenRouter functionality
python test_openrouter.py

# Test rate limiting features
python test_rate_limiting.py
```

---

## 🏠 Local Ollama Usage (Original)

For complete privacy and offline usage, you can still use local Ollama models:

```bash
# Convert PDF using local Ollama (default)
python src/pdf2md.py your_file.pdf -p ollama

# Or simply (ollama is default)
python src/pdf2md.py your_file.pdf
```

---

## Dependencies

### Core Dependencies:
- **PyMuPDF** (for PDF rendering) — not free for commercial use
- **Pillow** (image processing)
- **requests** (for OpenRouter API calls)

### Provider-Specific Dependencies:
- **Ollama** (for local LLM usage) + local models like gemma3:12b or gemma3:4b
- **OpenRouter API key** (for external LLM usage) - get free key at [openrouter.ai](https://openrouter.ai/)
- **pdf2image** (for poppler-based implementations)

---

## Alternative: Fully Open Source Version

Use `pdf2image` + `Poppler` instead of `pymupdf`.

```bash
brew install poppler  # or sudo apt install poppler-utils
pip install pdf2image pillow ollama
```
Then run:
```bash
python src/pdf2md_poppler.py
```

---

## Features

- 🔄 **Dual Provider Support**: Choose between local Ollama or external OpenRouter
- 📄 **Multiple PDF Processing Methods**: PyMuPDF, Poppler, or pdf2image
- 🖼️ **Image Processing**: Direct image-to-markdown conversion
- 📱 **Scanned PDF Support**: Handles image-based PDFs via OCR-like processing
- 🎯 **Clean Output**: Structured Markdown with proper formatting
- 🔒 **Privacy Options**: Complete offline processing or external API
- 💰 **Cost Effective**: Free local processing or free-tier external access
- 🚀 **Easy CLI**: Simple command-line interface with provider selection

## Available Scripts

| Script | Description | Best For |
|--------|-------------|----------|
| `pdf2md.py` | PyMuPDF-based (fastest) | Development, personal use |
| `pdf2md_poppler.py` | Poppler subprocess | Commercial, open source |
| `pdf2md_poppler_short.py` | pdf2image wrapper | Clean code, balanced approach |
| `img2md.py` | Direct image processing | Individual images, scanned docs |

## CLI Usage Examples

```bash
# Basic usage (defaults to Ollama)
python src/pdf2md.py document.pdf

# Use OpenRouter for external processing
python src/pdf2md.py document.pdf -p openrouter

# Specify custom output file and model
python src/pdf2md.py document.pdf -o my_output.md -m gemma3:4b -p openrouter

# Process image directly
python src/img2md.py scan.png -p openrouter

# Use poppler with custom DPI
python src/pdf2md_poppler.py document.pdf -d 600 -p openrouter

# Get help for any script
python src/pdf2md.py --help
```

---

## Convert pdf to image

```bash
pip install pdf2image
brew install poppler    # or in Linux: sudo apt install poppler-utils
```
