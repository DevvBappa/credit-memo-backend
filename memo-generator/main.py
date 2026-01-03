from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticBaseModel
from models import Memo
from llm import generate_memo
import os

app = FastAPI(title="Credit Memo Generator")

class OCRRequest(PydanticBaseModel):
    text: str  # Raw OCR text from your friends' service

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
