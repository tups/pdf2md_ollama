# Resume Functionality - PDF Processing Recovery

## Overview

The PDF to Markdown conversion tools now support **resume functionality** to handle processing failures gracefully. When processing large documents, if an error occurs (like API failures, network issues, or rate limiting), you can resume processing from the exact page where it failed instead of starting over from the beginning.

## Problem Solved

**Original Issue**: When processing large PDFs (e.g., 208 pages), if processing fails at page 47 due to an OpenRouter API error, the user had to restart from page 1, wasting time and resources on already completed pages.

**Solution**: The new `--start-page` parameter allows resuming from any specific page number, automatically detecting and skipping already processed pages.

## How It Works

### Automatic Detection
- The system automatically detects which pages have already been processed by parsing the existing output file
- It looks for page headers like `## Page 1`, `## Page 2`, etc.
- Already completed pages are automatically skipped

### Smart File Handling
- **Append Mode**: When resuming, new content is appended to the existing output file
- **Overwrite Mode**: When starting fresh, the output file is overwritten
- **Proper Separators**: Page separators (`---`) are added correctly regardless of resume mode

## Usage Examples

### Basic Resume from Specific Page

```bash
# Resume processing from page 47 (the example from the issue)
python src/pdf2md.py document.pdf --start-page 47

# Resume with OpenRouter provider
python src/pdf2md.py document.pdf -p openrouter --start-page 47

# Resume with custom output file
python src/pdf2md.py document.pdf -o custom_output.md --start-page 47
```

### Real-World Scenario

Based on the original issue log:
```
Processing page 44/208 with OpenRouter...
✓ Page 44 written to .\4062_REGLEMENT_DE_COPROPRIETE.md
Processing page 45/208 with OpenRouter...
✓ Page 45 written to .\4062_REGLEMENT_DE_COPROPRIETE.md
Processing page 46/208 with OpenRouter...
✓ Page 46 written to .\4062_REGLEMENT_DE_COPROPRIETE.md
Processing page 47/208 with OpenRouter...
OpenRouter error: OpenRouter API request failed: Response ended prematurely
```

**Recovery Command**:
```bash
python src/pdf2md.py 4062_REGLEMENT_DE_COPROPRIETE.pdf -p openrouter --start-page 47 -o 4062_REGLEMENT_DE_COPROPRIETE.md
```

### All Implementations Support Resume

```bash
# PyMuPDF-based implementation
python src/pdf2md.py document.pdf --start-page 47

# pdf2image-based implementation  
python src/pdf2md_poppler_short.py document.pdf --start-page 47

# Subprocess Poppler-based implementation
python src/pdf2md_poppler.py document.pdf --start-page 47
```

### Combined with Rate Limiting

```bash
# Resume with rate limiting to prevent future failures
python src/pdf2md.py document.pdf -p openrouter --start-page 47 --request-delay 5.0 --max-retries 5
```

## Resume Process Details

### What Happens When You Resume

1. **Detection Phase**:
   ```
   Resuming from page 47. Found 46 completed pages in existing output.
   Already completed pages: [1, 2, 3, ..., 46]
   ```

2. **Skipping Phase**:
   ```
   Skipping page 1 (already completed)
   Skipping page 2 (already completed)
   ...
   Skipping page 46 (already completed)
   ```

3. **Processing Phase**:
   ```
   Processing page 47/208 with OpenRouter...
   ✓ Page 47 written to output.md
   Processing page 48/208 with OpenRouter...
   ✓ Page 48 written to output.md
   ```

### Validation and Safety

- **Page Range Validation**: If `--start-page` is greater than total pages, an error is displayed
- **Automatic Detection**: Already completed pages are detected automatically, even if not specified
- **File Integrity**: Existing content is preserved and new content is properly appended
- **Progress Tracking**: Clear feedback shows which pages are being skipped vs. processed

## Command Line Options

### New Parameter

- `--start-page N`: Start processing from page N (default: 1)
  - Useful for resuming after failures
  - Automatically detects and skips already completed pages
  - Validates that N is within the document's page range

### Compatible with Existing Options

The resume functionality works with all existing parameters:

- `--progressive`: Progressive output mode (default for multi-page documents)
- `-p openrouter`: Use OpenRouter provider
- `--request-delay`: Rate limiting delay
- `--max-retries`: Retry attempts for failed requests
- `-o output.md`: Custom output file name

## Best Practices

### For Large Documents

1. **Use Rate Limiting**: Combine resume with rate limiting to prevent future failures
   ```bash
   python src/pdf2md.py large_doc.pdf -p openrouter --request-delay 3.0 --max-retries 5
   ```

2. **Monitor Progress**: Watch the console output to note the last successful page
   ```
   Processing page 156/300 with OpenRouter...
   ✓ Page 156 written to output.md
   ```

3. **Resume Immediately**: If processing fails, resume from the next page
   ```bash
   python src/pdf2md.py large_doc.pdf -p openrouter --start-page 157
   ```

### For Unreliable Networks

1. **Conservative Settings**: Use longer delays and more retries
   ```bash
   python src/pdf2md.py doc.pdf -p openrouter --request-delay 10.0 --max-retries 10
   ```

2. **Checkpoint Strategy**: For very large documents, consider processing in chunks
   ```bash
   # Process pages 1-50
   python src/pdf2md.py doc.pdf --start-page 1 --progressive
   # If it fails at page 30, resume from there
   python src/pdf2md.py doc.pdf --start-page 30
   ```

## Technical Implementation

### Page Detection Algorithm

The system uses regex pattern matching to detect completed pages:
```python
page_pattern = r'^## Page (\d+)$'
matches = re.findall(page_pattern, content, re.MULTILINE)
completed_pages = set(int(page_num) for page_num in matches)
```

### File Handling Logic

```python
# Determine file opening mode
file_mode = "a" if is_resuming and os.path.exists(output_file) else "w"

# Smart separator handling
if file_mode == "a" or (file_mode == "w" and page_num > start_page):
    f.write("\n\n---\n\n")
```

## Troubleshooting

### Common Issues

1. **"Error: Start page X is greater than total pages Y"**
   - Solution: Check the document's total page count and use a valid page number

2. **Pages appear duplicated**
   - Solution: The system automatically detects duplicates, but ensure you're using the correct output file

3. **Missing page separators**
   - Solution: The system handles separators automatically; this shouldn't occur with the new implementation

### Verification

To verify resume functionality is working:
1. Check console output for "Resuming from page X" message
2. Look for "Already completed pages: [...]" list
3. Confirm "Skipping page X (already completed)" messages
4. Verify final output file contains all pages without duplicates

## Files Modified

The resume functionality has been implemented in all three PDF processing implementations:

1. **`src/pdf2md.py`**: PyMuPDF-based implementation
2. **`src/pdf2md_poppler_short.py`**: pdf2image-based implementation  
3. **`src/pdf2md_poppler.py`**: Subprocess Poppler-based implementation

All implementations share the same interface and behavior for consistency.