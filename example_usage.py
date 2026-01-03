"""
Example Usage - Credit Memo PDF Extractor
This script demonstrates how to use the PDF extractor
"""

from pdf_extractor import PDFExtractor
from batch_processor import BatchPDFProcessor

# Example 1: Extract and display all text
def example_basic_extraction(pdf_path):
    """Basic extraction example"""
    print("Example 1: Basic PDF Text Extraction")
    print("=" * 80)
    
    extractor = PDFExtractor(pdf_path)
    result = extractor.extract_text()
    
    if result['success']:
        print(f"✅ Successfully extracted text from {result['pages_with_text']} pages")
        extractor.display_text()
    else:
        print(f"❌ Error: {result['error']}")


# Example 2: Extract specific page
def example_page_extraction(pdf_path, page_number):
    """Extract specific page example"""
    print("\n\nExample 2: Extract Specific Page")
    print("=" * 80)
    
    extractor = PDFExtractor(pdf_path)
    extractor.extract_text()
    
    page_text = extractor.get_page_text(page_number)
    
    if page_text:
        print(f"\n📄 Text from Page {page_number}:")
        print("─" * 80)
        print(page_text)
    else:
        print(f"❌ Page {page_number} not found")


# Example 3: Get all text as single string
def example_full_text(pdf_path):
    """Get full text example"""
    print("\n\nExample 3: Get All Text as Single String")
    print("=" * 80)
    
    extractor = PDFExtractor(pdf_path)
    extractor.extract_text()
    
    full_text = extractor.get_full_text()
    
    print(f"📊 Total characters extracted: {len(full_text)}")
    print(f"📊 Total words (approx): {len(full_text.split())}")
    print("\nFirst 500 characters:")
    print("─" * 80)
    print(full_text[:500] + "...")


# Example 4: Save extracted text
def example_save_text(pdf_path):
    """Save extracted text example"""
    print("\n\nExample 4: Save Extracted Text to File")
    print("=" * 80)
    
    extractor = PDFExtractor(pdf_path)
    result = extractor.extract_text()
    
    if result['success']:
        output_file = pdf_path.replace('.pdf', '_extracted.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Extracted from: {result['metadata']['filename']}\n")
            f.write(f"Total Pages: {result['total_pages']}\n")
            f.write(f"Pages with Text: {result['pages_with_text']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(extractor.get_full_text())
        
        print(f"✅ Text saved to: {output_file}")
    else:
        print(f"❌ Error: {result['error']}")


# Example 5: Batch process multiple PDFs
def example_batch_processing():
    """Batch processing example"""
    print("\n\nExample 5: Batch Process Multiple PDFs")
    print("=" * 80)
    
    # Example with multiple PDFs
    pdf_paths = []
    
    print("\nEnter paths to multiple PDFs (or press Enter to skip):")
    while True:
        path = input(f"  PDF #{len(pdf_paths) + 1} (or Enter to finish): ").strip().strip('"')
        
        # Ask if user wants to try batch processing
        batch = input("\n\nWould you like to try batch processing multiple PDFs? (y/n): ").lower()
        if batch == 'y':
            example_batch_processing()
    else:
        print("\nNo PDF provided. Here's how to use the extractor:")
        print("\n1. Run: python pdf_extractor.py (single PDF)")
        print("2. Run: python batch_processor.py (multiple PDFs)")
        print("3. Or import: from pdf_extractor import PDFExtractor")
        print("4. See examples in this file for more usage patterns")


if __name__ == "__main__":
    print("\n🚀 Credit Memo Auto-Generator - Example Usage\n")
    
    # Get PDF path from user
    pdf_path = input("Enter the path to your PDF file (or press Enter to skip examples): ").strip().strip('"')
    
    if pdf_path:
        # Run all examples
        example_basic_extraction(pdf_path)
        example_page_extraction(pdf_path, page_number=1)
        example_full_text(pdf_path)
        example_save_text(pdf_path)
    else:
        print("\nNo PDF provided. Here's how to use the extractor:")
        print("\n1. Run: python pdf_extractor.py")
        print("2. Or import: from pdf_extractor import PDFExtractor")
        print("3. See examples in this file for more usage patterns")
