import os
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel
from groq import Groq
from typing import Any
from models import Memo

# Load environment variables from .env file
load_dotenv()

client = instructor.from_groq(
    Groq(api_key=os.getenv("GROQ_API_KEY"))
)

def generate_memo(ocr_text: str) -> Memo:
    """Generate memo from OCR text"""
    return client.messages.create(
        model="llama-3.1-8b-instant",  # Or llama-3.1-8b
        response_model=Memo,
        messages=[
            {
                "role": "system",
                "content": """You are a senior credit analyst.

You read messy OCR text from financial documents and produce a structured memo.

Rules:
- Only use numbers explicitly in the text. Do not invent.
- source_pages: use page numbers from markers like 'PAGE 1'
- If data missing, omit the metric or set confidence to "incomplete_data"
- Executive summary: 3-5 short bullets in plain English.
- Top risks: 3 most important credit risks.

Output valid JSON matching the schema exactly."""
            },
            {
                "role": "user",
                "content": f"""OCR text from financial document:

{ocr_text}

Respond with JSON only."""
            }
        ],
        temperature=0.1,
        max_retries=3  # Instructor auto-retries if invalid
    )
