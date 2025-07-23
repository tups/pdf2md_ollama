# Command Line Usage Guide

All PDF2MD Ollama scripts now support command-line arguments for specifying input files and options.

## Usage Examples

### PDF to Markdown Conversion

#### PyMuPDF Implementation (pdf2md.py)
```bash
# Basic usage
python src/pdf2md.py input.pdf

# Specify output file
python src/pdf2md.py input.pdf -o my_output.md

# Use different model
python src/pdf2md.py input.pdf -m gemma3:4b

# All options
python src/pdf2md.py input.pdf -o output.md -m gemma3:12b
```

#### Poppler Implementation (pdf2md_poppler.py)
```bash
# Basic usage
python src/pdf2md_poppler.py input.pdf

# With custom DPI
python src/pdf2md_poppler.py input.pdf -d 150

# All options
python src/pdf2md_poppler.py input.pdf -o output.md -m gemma3:12b -d 300

python src/pdf2md_poppler.py Referentiel_NF525_V2.3_Fiche_Tarifaire_LORD_OF_WEB.pdf -o output.md -m gemma3:4b -d 150
```

#### PDF2Image Implementation (pdf2md_poppler_short.py)
```bash
# Basic usage (requires pdf2image package)
python src/pdf2md_poppler_short.py input.pdf

# With custom DPI
python src/pdf2md_poppler_short.py input.pdf -d 200

# All options
python src/pdf2md_poppler_short.py input.pdf -o output.md -m gemma3:12b -d 300
```

### Image to Markdown Conversion

#### Direct Image Processing (img2md.py)
```bash
# Basic usage
python src/img2md.py image.png

# Specify output file
python src/img2md.py image.jpg -o image_text.md

# Use different model
python src/img2md.py scan.png -m gemma3:4b

# All options
python src/img2md.py document.png -o extracted.md -m gemma3:12b
```

## Command Line Options

### Common Options (All Scripts)
- `input_file`: Required positional argument - path to input file
- `-o, --output`: Output Markdown file (default: output.md)
- `-m, --model`: Ollama model to use (default: gemma3:12b)
- `-h, --help`: Show help message

### Additional Options
- `-d, --dpi`: DPI for image conversion (pdf2md_poppler.py and pdf2md_poppler_short.py only, default: 300)

## Prerequisites

1. **Ollama**: Must be installed and running
2. **Models**: Required model must be pulled (e.g., `ollama pull gemma3:12b`)
3. **Dependencies**: Install required packages via `pip install -r requirements.txt`
4. **Optional**: For pdf2md_poppler_short.py, install pdf2image: `pip install pdf2image`
5. **Optional**: For pdf2md_poppler.py, install Poppler utilities

## Error Handling

The scripts now include proper error handling:
- File existence validation
- Clear error messages for missing files
- Model availability checking (handled by Ollama)

## Migration from Previous Version

**Before (hardcoded):**
```python
pdf_path = "mypdf.pdf"  # Had to edit source code
```

**Now (CLI):**
```bash
python src/pdf2md.py mypdf.pdf  # Specify file directly
```