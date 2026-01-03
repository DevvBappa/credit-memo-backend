"""
Batch PDF Processor - Process multiple PDFs at once
Handles multiple financial PDFs and creates separate outputs for each
"""

from pdf_extractor import PDFExtractor
import os
from pathlib import Path


class BatchPDFProcessor:
    """Process multiple PDF files and generate separate outputs"""
    
    def __init__(self, pdf_paths):
        """
        Initialize batch processor
        
        Args:
            pdf_paths (list): List of PDF file paths
        """
        self.pdf_paths = pdf_paths
        self.results = []
        
    def process_all(self, save_individual_files=True):
        """
        Process all PDFs and generate separate outputs
        
        Args:
            save_individual_files (bool): Save separate text file for each PDF
            
        Returns:
            list: List of processing results
        """
        print(f"\n🚀 Starting batch processing of {len(self.pdf_paths)} PDFs...")
        print("=" * 80)
        
        for idx, pdf_path in enumerate(self.pdf_paths, start=1):
            print(f"\n📄 Processing {idx}/{len(self.pdf_paths)}: {os.path.basename(pdf_path)}")
            print("─" * 80)
            
            if not os.path.exists(pdf_path):
                result = {
                    'pdf_path': pdf_path,
                    'filename': os.path.basename(pdf_path),
                    'success': False,
                    'error': 'File not found'
                }
                print(f"❌ Error: File not found")
                self.results.append(result)
                continue
            
            # Extract text from PDF
            extractor = PDFExtractor(pdf_path)
            extraction_result = extractor.extract_text()
            
            if extraction_result['success']:
                print(f"✅ Extracted {extraction_result['pages_with_text']} pages")
                
                result = {
                    'pdf_path': pdf_path,
                    'filename': extraction_result['metadata']['filename'],
                    'success': True,
                    'total_pages': extraction_result['total_pages'],
                    'pages_with_text': extraction_result['pages_with_text'],
                    'extractor': extractor,
                    'text': extractor.get_full_text()
                }
                
                # Save individual file if requested
                if save_individual_files:
                    output_file = pdf_path.replace('.pdf', '_extracted.txt')
                    self._save_individual_file(extractor, extraction_result, output_file)
                    result['output_file'] = output_file
                    print(f"💾 Saved to: {os.path.basename(output_file)}")
                
                self.results.append(result)
            else:
                result = {
                    'pdf_path': pdf_path,
                    'filename': os.path.basename(pdf_path),
                    'success': False,
                    'error': extraction_result['error']
                }
                print(f"❌ Error: {extraction_result['error']}")
                self.results.append(result)
        
        return self.results
    
    def _save_individual_file(self, extractor, metadata, output_file):
        """Save extracted text to individual file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Extracted from: {metadata['metadata']['filename']}\n")
            f.write(f"Total Pages: {metadata['total_pages']}\n")
            f.write(f"Pages with Text: {metadata['pages_with_text']}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write each page with clear separators
            for page_data in extractor.text_content:
                f.write(f"{'─' * 80}\n")
                f.write(f"PAGE {page_data['page']}\n")
                f.write(f"{'─' * 80}\n\n")
                f.write(page_data['text'])
                f.write("\n\n")
    
    def display_summary(self):
        """Display summary of batch processing"""
        print("\n\n" + "=" * 80)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 80)
        
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        
        print(f"\n📊 Total PDFs: {len(self.results)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        print("\n" + "─" * 80)
        print("Individual Results:")
        print("─" * 80)
        
        for idx, result in enumerate(self.results, start=1):
            status = "✅" if result['success'] else "❌"
            print(f"{idx}. {status} {result['filename']}", end="")
            
            if result['success']:
                print(f" - {result['pages_with_text']} pages, {len(result['text'])} chars")
            else:
                print(f" - {result['error']}")


def main():
    """Main function for batch PDF processing"""
    
    print("Credit Memo Auto-Generator - Batch PDF Processor")
    print("=" * 80)
    print("\nThis tool processes multiple PDFs and creates separate outputs for each.\n")
    
    # Get PDF file paths from user
    pdf_paths = []
    
    print("Enter PDF file paths (one per line).")
    print("Press Enter twice when done, or type 'done' to finish:\n")
    
    while True:
        path = input(f"PDF #{len(pdf_paths) + 1}: ").strip().strip('"')
        
        if not path or path.lower() == 'done':
            break
        
        if os.path.exists(path) and path.lower().endswith('.pdf'):
            pdf_paths.append(path)
            print(f"  ✅ Added: {os.path.basename(path)}")
        else:
            print(f"  ⚠️ Skipped: Invalid path or not a PDF file")
    
    if not pdf_paths:
        print("\n❌ No valid PDF files provided. Exiting.")
        return
    
    print(f"\n📋 Ready to process {len(pdf_paths)} PDF(s)")
    
    # Ask if user wants to save individual files
    save_files = input("\nSave separate text file for each PDF? (y/n, default=y): ").lower()
    save_individual = save_files != 'n'
    
    # Process all PDFs
    processor = BatchPDFProcessor(pdf_paths)
    results = processor.process_all(save_individual_files=save_individual)
    
    # Display summary
    processor.display_summary()
    
    print("\n" + "=" * 80)
    print("✅ Batch processing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
