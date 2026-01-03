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

@app.post("/upload-pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Endpoint to receive PDF files from frontend.
    Extracts text from PDFs and saves to ocr_text.json
    
    This is the recommended endpoint for your workflow:
    1. Frontend sends PDFs
    2. Backend extracts text
    3. Text saved to ocr_text.json
    4. Returns success confirmation
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
        
        # Save to ocr_text.json
        ocr_data = {
            "text": formatted_text
        }
        
        with open(OCR_TEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'message': f'Successfully processed {result["successful_extractions"]} PDF(s) and saved to {OCR_TEXT_FILE}',
            'extracted_text': formatted_text,
            'total_pdfs': result['total_pdfs'],
            'successful_extractions': result['successful_extractions'],
            'text_length': len(formatted_text),
            'saved_to': OCR_TEXT_FILE,
            'details': result['results']
        }
    except Exception as e:
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
