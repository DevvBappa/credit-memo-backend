"""
Credit Memo Auto-Generator - PDF Text Extractor
Reads financial PDFs and extracts text content
"""

import pdfplumber
import os
from pathlib import Path


class PDFExtractor:
    """Extract text from PDF files"""
    
    def __init__(self, pdf_path):
        """
        Initialize the PDF extractor
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.text_content = []
        self.metadata = {}
        
    def extract_text(self):
        """
        Extract text from PDF file
        
        Returns:
            dict: Dictionary containing extracted text and metadata
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Get metadata
                self.metadata = {
                    'total_pages': len(pdf.pages),
                    'filename': os.path.basename(self.pdf_path)
                }
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    if text:
                        self.text_content.append({
                            'page': page_num,
                            'text': text.strip()
                        })
                
                return {
                    'success': True,
                    'metadata': self.metadata,
                    'content': self.text_content,
                    'total_pages': self.metadata['total_pages'],
                    'pages_with_text': len(self.text_content)
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'error': f"PDF file not found: {self.pdf_path}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error extracting PDF: {str(e)}"
            }
    
    def get_full_text(self):
        """
        Get all extracted text as a single string
        
        Returns:
            str: Complete text from all pages
        """
        return "\n\n".join([page['text'] for page in self.text_content])
    
    def get_page_text(self, page_number):
        """
        Get text from a specific page
        
        Args:
            page_number (int): Page number (1-indexed)
            
        Returns:
            str: Text from the specified page
        """
        for page in self.text_content:
            if page['page'] == page_number:
                return page['text']
        return None
    
    def display_text(self):
        """Display extracted text in a formatted way"""
        if not self.text_content:
            print("No text extracted. Please run extract_text() first.")
            return
        
        print("=" * 80)
        print(f"DOCUMENT: {self.metadata.get('filename', 'Unknown')}")
        print(f"TOTAL PAGES: {self.metadata.get('total_pages', 0)}")
        print("=" * 80)
        print()
        
        for page_data in self.text_content:
            print(f"\n{'─' * 80}")
            print(f"PAGE {page_data['page']}")
            print(f"{'─' * 80}\n")
            print(page_data['text'])
            print()


def main():
    """Main function to demonstrate PDF extraction"""
    
    print("Credit Memo Auto-Generator - PDF Text Extractor")
    print("=" * 80)
    print()
    
    # Get PDF file path from user
    pdf_path = input("Enter the path to your PDF file: ").strip().strip('"')
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"\n❌ Error: File not found - {pdf_path}")
        return
    
    # Check if it's a PDF file
    if not pdf_path.lower().endswith('.pdf'):
        print(f"\n❌ Error: File must be a PDF - {pdf_path}")
        return
    
    print(f"\n📄 Processing: {os.path.basename(pdf_path)}")
    print("Please wait...\n")
    
    # Create extractor and extract text
    extractor = PDFExtractor(pdf_path)
    result = extractor.extract_text()
    
    if result['success']:
        print(f"✅ Successfully extracted text from {result['pages_with_text']} pages")
        print()
        
        # Display extracted text
        extractor.display_text()
        
        # Ask if user wants to save to file
        save_option = input("\n\nWould you like to save the extracted text to a file? (y/n): ").lower()
        if save_option == 'y':
            output_file = pdf_path.replace('.pdf', '_extracted.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Extracted from: {result['metadata']['filename']}\n")
                f.write(f"Total Pages: {result['total_pages']}\n")
                f.write("=" * 80 + "\n\n")
                f.write(extractor.get_full_text())
            print(f"✅ Text saved to: {output_file}")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    main()
