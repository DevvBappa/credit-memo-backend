from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel as PydanticBaseModel
from models import Memo
from llm import generate_memo
from batch_processor import BatchPDFProcessor
from typing import List
import os
import json

app = FastAPI(title="Credit Memo Generator")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OCR_TEXT_FILE = "ocr_text.json"

class OCRRequest(PydanticBaseModel):
    text: str  # Raw OCR text from your friends' service

@app.get("/")
async def root():
    """Root endpoint showing available API endpoints"""
    return {
        "message": "Credit Memo Generator API",
        "version": "1.0",
        "endpoints": {
            "POST /upload-pdfs": "Upload PDF files for text extraction",
            "POST /generate-memo": "Generate credit memo from OCR text (body: {\"text\": \"...\"})",
        },
        "status": "running"
    }

@app.post("/upload-pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Complete workflow endpoint:
    1. Receives PDF files from frontend
    2. Extracts text from PDFs
    3. Saves text to ocr_text.json
    4. Generates credit memo using LLM
    5. Returns complete memo data to frontend
    """
    try:
        # Validate that files were provided
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Process uploaded PDFs
        result = await BatchPDFProcessor.process_uploaded_files(files)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Processing failed'))
        
        # Format text with page separators for ocr_text.json
        formatted_text = result['text']
        
        print(f"\n{'='*80}")
        print(f"TEXT EXTRACTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total PDFs processed: {result['total_pdfs']}")
        print(f"Successful extractions: {result['successful_extractions']}")
        print(f"Extracted text length: {len(formatted_text)} characters")
        print(f"Text preview (first 200 chars):\n{formatted_text[:200]}...")
        print(f"{'='*80}\n")
        
        # Save to ocr_text.json
        ocr_data = {
            "text": formatted_text
        }
        
        with open(OCR_TEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, indent=2, ensure_ascii=False)
        
        # Generate memo using LLM
        print(f"{'='*80}")
        print(f"GENERATING MEMO FROM EXTRACTED TEXT")
        print(f"{'='*80}")
        memo = generate_memo(formatted_text)
        
        # Convert memo to dict for response
        memo_dict = memo.model_dump()
        
        print(f"\n{'='*80}")
        print(f"MEMO GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Company: {memo_dict.get('company_info', {}).get('name', 'N/A')}")
        print(f"Buyer: {memo_dict.get('buyer_info', {}).get('name', 'N/A')}")
        print(f"Executive Summary bullets: {len(memo_dict.get('executive_summary', []))}")
        print(f"Key Metrics: {len(memo_dict.get('key_metrics', []))}")
        print(f"Top Risks: {len(memo_dict.get('top_risks', []))}")
        if memo_dict.get('top_risks'):
            for i, risk in enumerate(memo_dict['top_risks'], 1):
                print(f"  Risk {i}: {risk.get('title')} ({risk.get('severity')})")
        print(f"Line Items: {len(memo_dict.get('memo_items', []))}")
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'message': f'Successfully processed {result["successful_extractions"]} PDF(s), saved to {OCR_TEXT_FILE}, and generated memo',
            'total_pdfs': result['total_pdfs'],
            'successful_extractions': result['successful_extractions'],
            'text_length': len(formatted_text),
            'saved_to': OCR_TEXT_FILE,
            'memo': memo_dict  # Complete memo data for frontend
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-memo", response_model=Memo)
async def generate(request: OCRRequest):
    try:
        memo = generate_memo(request.text)
        return memo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
