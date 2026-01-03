# Credit Memo Auto-Generator

A tool that reads financial PDFs and produces clear first-draft summaries.

## Current Features

- ✅ PDF text extraction
- ✅ Page-by-page text display
- ✅ Save extracted text to file

## Coming Soon

- 📊 Executive summary generation
- 📈 Key metrics extraction
- ⚠️ Risk identification
- 🔍 Source page highlighting
- 📝 Export to Word/Markdown

## Installation

1. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python pdf_extractor.py
```

Then enter the path to your PDF file when prompted.

### Programmatic Usage

```python
from pdf_extractor import PDFExtractor

# Create extractor instance
extractor = PDFExtractor("path/to/your/financial_report.pdf")

# Extract text
result = extractor.extract_text()

# Display text
extractor.display_text()

# Get full text as string
full_text = extractor.get_full_text()

# Get specific page text
page_1_text = extractor.get_page_text(1)
```

## Project Structure

```
credit memo/
├── pdf_extractor.py      # Main PDF extraction module
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Example Output

```
================================================================================
DOCUMENT: financial_report.pdf
TOTAL PAGES: 15
================================================================================

────────────────────────────────────────────────────────────────────────────────
PAGE 1
────────────────────────────────────────────────────────────────────────────────

[Extracted text from page 1...]

────────────────────────────────────────────────────────────────────────────────
PAGE 2
────────────────────────────────────────────────────────────────────────────────

[Extracted text from page 2...]
```

## Future Roadmap

1. **Phase 1** (Current): Basic PDF text extraction ✅
2. **Phase 2**: AI-powered summary generation
3. **Phase 3**: Financial metrics extraction
4. **Phase 4**: Risk analysis
5. **Phase 5**: Export capabilities (Word, Markdown)
