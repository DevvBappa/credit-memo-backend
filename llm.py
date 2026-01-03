import os
import json
from dotenv import load_dotenv
from groq import Groq
from models import Memo
from pydantic import ValidationError

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_memo(ocr_text: str) -> Memo:
    """
    Generate a structured credit memo from OCR text.
    Uses strict JSON output + Pydantic validation (NO function calling).
    """

    system_prompt = """
You are a senior credit analyst.

You MUST return a JSON object that matches this EXACT structure:

{
  "executive_summary": [string, string, string],
  "key_metrics": [
    {
      "name": string,
      "value": string,
      "period": string | null,
      "direction": "increase" | "decrease" | "stable" | null,
      "source_pages": number[],
      "confidence": "strong" | "incomplete_data"
    }
  ],
  "top_risks": [
    {
      "title": string,
      "description": string,
      "severity": "low" | "medium" | "high",
      "source_pages": number[],
      "confidence": "strong" | "incomplete_data"
    }
  ]
}

STRICT RULES:
- Output ONLY the keys shown above
- DO NOT add extra keys (no company, no source_pages at root)
- top_risks MUST be an array of OBJECTS, not strings
- If no risks exist, return: "top_risks": []
- Use ONLY numbers present in the text
- source_pages must be numeric page numbers (e.g., 1, 2)
- Executive summary MUST have 3–5 bullets
- Output valid JSON ONLY
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        top_p=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
OCR TEXT:
{ocr_text}

Return JSON only.
"""
            }
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # Optional: print raw output for debugging
    # print(raw_output)

    try:
        # Validate and parse JSON into Pydantic model
        memo = Memo.model_validate_json(raw_output)
        return memo

    except ValidationError as e:
        raise ValueError(
            f"Model returned invalid JSON structure:\n{e}\n\nRaw output:\n{raw_output}"
        )

    except json.JSONDecodeError:
        raise ValueError(
            f"Model did not return valid JSON.\nRaw output:\n{raw_output}"
        )
