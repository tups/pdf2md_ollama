# PDF2MD Ollama - Development Guidelines

*Last updated: 2025-07-22 18:28*

## Project Overview

This project provides multiple approaches for converting PDFs to Markdown using local Large Language Models (LLMs) via Ollama. The primary goal is to offer fast, private, and free PDF-to-Markdown conversion without relying on cloud APIs or external services.

## Architecture & Implementation Approaches

The project offers three main implementation strategies:

### 1. PyMuPDF-based (`pdf2md.py`)
- **Library**: PyMuPDF (fitz)
- **Pros**: Fastest performance, direct PDF rendering
- **Cons**: Not free for commercial use
- **Use case**: Development, personal projects, or when performance is critical

### 2. Poppler-based (`pdf2md_poppler.py`)
- **Library**: Subprocess calls to `pdftoppm`
- **Pros**: Fully open source, no licensing restrictions
- **Cons**: Requires external Poppler installation, more complex setup
- **Use case**: Commercial projects requiring full open source stack
- **Note**: Missing `import ollama` statement - needs to be added

### 3. PDF2Image-based (`pdf2md_poppler_short.py`)
- **Library**: pdf2image (Python wrapper for Poppler)
- **Pros**: Fully open source, clean Python interface, concise code
- **Cons**: Additional dependency
- **Use case**: Best balance of open source compliance and code simplicity

### 4. Direct Image Processing (`img2md.py`)
- **Purpose**: Convert individual images to Markdown text
- **Use case**: Processing scanned documents or images directly

## Core Dependencies

### Required Dependencies
- **ollama**: LLM integration and chat interface
- **pillow**: Image processing and manipulation
- **pymupdf**: PDF rendering (commercial licensing considerations)

### Optional Dependencies
- **pdf2image**: Alternative PDF processing (open source)
- **poppler-utils**: System dependency for PDF processing

## LLM Configuration

### Default Model
- **Model**: `gemma3:12b`
- **Alternative**: `gemma3:4b` (lighter version)
- **Requirement**: Model must be pre-installed via Ollama

### Prompt Engineering
The project uses a refined prompt for optimal text extraction:
```
"Extract all readable text and text chunks from this image and format it as structured Markdown. Look in the entire image always and try to retrieve all text!"
```

## Development Patterns

### File Structure
```
src/
├── pdf2md.py              # PyMuPDF implementation
├── pdf2md_poppler.py      # Subprocess Poppler implementation
├── pdf2md_poppler_short.py # pdf2image implementation
└── img2md.py              # Direct image processing
```

### Common Patterns
1. **Image Conversion**: All approaches convert PDF pages to PNG images
2. **Batch Processing**: Images are processed as a list to Ollama
3. **Output Format**: Results are saved as `output.md` with UTF-8 encoding
4. **Error Handling**: Basic validation for image availability

### Code Quality Issues Identified
1. **Missing Import**: `pdf2md_poppler.py` lacks `import ollama`
2. **Syntax Fix Applied**: Removed extra parenthesis in `img2md.py` with statement
3. **Duplicate Prompts**: Some files have redundant prompt definitions

## Installation & Setup

### Environment Setup
The project supports both `uv` and traditional `pip` workflows:

**Using uv (recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv pip install -r requirements.txt
uv run src/pdf2md.py
```

**Using pip:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/pdf2md.py
```

### System Dependencies
For Poppler-based approaches:
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt install poppler-utils`
- **Windows**: Download Poppler binaries and add to PATH

## Testing & Quality Assurance

### Test Files Present
- `simple_test.py`
- `test_sample.py`
- `test_sample.txt`
- `test_image.png`

### Recommended Testing Approach
1. Test each implementation variant with sample PDFs
2. Verify output quality and formatting
3. Test with different PDF types (text-based, scanned, mixed)
4. Validate Ollama model integration

## Future Development Considerations

### Licensing Strategy
- Consider making PyMuPDF usage optional for commercial deployments
- Default to open source implementations for broader adoption
- Document licensing implications clearly

### Code Improvements
1. **Unified Interface**: Create a common interface for all implementations
2. **Configuration Management**: Add config file support for model selection, prompts, etc.
3. **Error Handling**: Improve error handling and user feedback
4. **Performance Optimization**: Add progress indicators for large PDFs
5. **Output Customization**: Allow custom output formats and file naming

### Feature Enhancements
1. **Batch Processing**: Support for multiple PDF files
2. **CLI Interface**: Add command-line argument parsing
3. **Quality Control**: Add text extraction quality metrics
4. **Model Flexibility**: Support for different LLM providers
5. **OCR Fallback**: Integrate traditional OCR for comparison/fallback

### Maintenance Tasks
1. Fix missing import in `pdf2md_poppler.py`
2. Standardize prompt definitions across files
3. Add comprehensive error handling
4. Create unit tests for each implementation
5. Add logging for debugging and monitoring

## Best Practices

### Code Style
- Follow PEP 8 conventions
- Use meaningful variable names
- Add docstrings for functions
- Handle exceptions gracefully

### Performance
- Consider DPI settings for image quality vs. processing speed
- Monitor memory usage with large PDFs
- Implement streaming for very large documents

### Security
- Validate input file paths
- Sanitize output content if needed
- Consider sandboxing for untrusted PDFs

## Related Resources

- **Article**: [Convert PDFs to Markdown using Local LLMs — Fast, Private, and Free](https://medium.com/data-science-collective/convert-pdfs-to-markdown-using-local-llms-c5232f3b50fc?sk=9b0036a7ff93a1c48bae7dd8216dc671)
- **Ollama Documentation**: https://ollama.ai/
- **PyMuPDF Documentation**: https://pymupdf.readthedocs.io/
- **Poppler Utils**: https://poppler.freedesktop.org/