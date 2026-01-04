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
You are a senior credit analyst creating a complete credit memo with financial analysis.

⚠️ CRITICAL RULE: You MUST use ONLY the EXACT numbers that appear in the provided text. 
DO NOT make up, estimate, or calculate numbers that are not explicitly stated.
DO NOT use example numbers or placeholders.
If a number is not in the document, DO NOT include that metric.

You MUST return a JSON object that matches this EXACT structure:

{
  "company_info": {
    "name": string,
    "address": string,
    "gstin": string,
    "state": string,
    "state_code": string,
    "email": string | null,
    "phone": string | null
  },
  "buyer_info": {
    "name": string,
    "address": string,
    "gstin": string,
    "state": string,
    "state_code": string
  },
  "memo_meta": {
    "credit_note_no": string,
    "date": string,
    "buyers_ref": string,
    "buyers_order_no": string,
    "order_date": string,
    "dispatch_doc_no": string,
    "dispatch_through": string,
    "destination": string,
    "terms": string
  },
  "memo_items": [
    {
      "description": string,
      "batch": string | null,
      "hsn": string,
      "quantity": number,
      "rate": number,
      "per": string,
      "amount": number
    }
  ],
  "cgst_rate": number,
  "sgst_rate": number,
  "executive_summary": [string, string, string, string, string],
  "key_metrics": [
    {
      "name": string,
      "value": string,
      "period": string | null,
      "direction": "increase" | "decrease" | "stable" | null,
      "source_pages": number[],
      "confidence": "strong" | "calculated" | "incomplete_data"
    }
  ],
  "top_risks": [
    {
      "title": string,
      "description": string,
      "severity": "low" | "medium" | "high",
      "source_pages": number[],
      "confidence": "strong" | "calculated" | "incomplete_data"
    }
  ]
}

EXTRACTION RULES FOR CREDIT MEMO FIELDS:
- company_info: Extract seller/company details (name, address, GSTIN, state, state code, email, phone)
- buyer_info: Extract buyer details (name, address, GSTIN, state, state code)
- memo_meta: Extract all document metadata (credit note no, dates, references, dispatch info)
- memo_items: Extract all line items with description, batch, HSN/SAC, quantity, rate, unit, amount
- cgst_rate, sgst_rate: Extract tax rates if mentioned (default to 0 if not found)
- IMPORTANT: If credit memo fields are not present, use EMPTY STRINGS (""), NOT null
- For optional fields like email/phone, you can use null
- For all required string fields in memo_meta, use "" if data not found

STRICT RULES FOR EXECUTIVE SUMMARY (5 bullets):
- EXACTLY 5 bullet points summarizing key findings
- Focus on: revenue growth, profitability, liquidity, key ratios, major concerns
- Each bullet should be concise (1-2 sentences max)
- Highlight year-over-year changes with percentages

STRICT RULES FOR KEY METRICS TABLE:
- Extract all major financial metrics found in the document
- Include: Revenue, Profit, EBITDA, Cash Flow, Assets, Liabilities, Ratios, etc.
- ALWAYS include source_pages showing which page each metric came from (look for "--- PAGE X ---" markers)

CONFIDENCE LEVELS - USE CAREFULLY:
- "strong": ONLY for metrics directly stated in the document (e.g., "Sales Revenue: 18,750,000")
- "calculated": For computed ratios/metrics NOT directly stated (e.g., ROE, Debt-to-Equity, Growth %)
  * For calculated metrics, include formula in the name (e.g., "ROE (PAT/Avg Equity)")
  * Show calculation: "20.6% (2,670,000 / 12,975,000)"
- "incomplete_data": For metrics with missing data or unclear values

- Show direction: "increase", "decrease", or "stable" based on year-over-year comparisons
- For calculated metrics, cite source pages of ALL components used in calculation

STRICT RULES FOR TOP 3 RISKS:
- EXACTLY 3 risks (most critical credit risks)
- Focus on: debt levels, cash flow issues, declining margins, market risks
- Each risk needs: clear title, description explaining impact, severity level
- ALWAYS include source_pages for traceability
- Use "high" severity for critical risks, "medium" for concerning, "low" for minor

CRITICAL ACCURACY RULES:
- ⚠️ ABSOLUTE REQUIREMENT: Copy numbers EXACTLY as they appear in the document
- DO NOT calculate, estimate, or infer numbers that are not explicitly written
- DO NOT use rounded numbers unless they appear rounded in the document
- DO NOT make up example data - if it's not in the text, don't include it
- MANDATORY: Parse "--- PAGE X ---" markers to track exact page numbers
- source_pages must reference the ACTUAL page numbers where data appears
- If computing a ratio (e.g., Debt/Equity), source_pages = [all pages with components]
- Example: ROE needs PAT (Page 1) and Equity (Page 3) → source_pages: [1, 3]
- For calculated ratios, show the formula AND the exact source numbers used
- For risks based on trends, cite pages showing the concerning metrics
- Output valid JSON ONLY - no markdown, no code blocks

EXAMPLE OF CORRECT EXTRACTION:
Document says: "Total Assets: €684,204"
Your output: "value": "684,204", "period": "2022"
❌ WRONG: "value": "684,000" (rounded)
❌ WRONG: "value": "700,000" (estimated)

EXAMPLE OF CORRECT CALCULATION:
Document has: "Profit: €339,983" (Page 1) and "Shareholders' Funds: €684,204" (Page 2)
Your output: "name": "ROE (Profit/Equity)", "value": "49.7% (339,983 / 684,204)", "source_pages": [1, 2], "confidence": "calculated"
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Using larger model for better analysis
        temperature=0.3,  # Increased to prevent repetitive responses
        top_p=0.95,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
Analyze this document and generate a complete credit memo with financial analysis.

⚠️ CRITICAL INSTRUCTION: Use ONLY the EXACT numbers that appear in the OCR text below.
DO NOT make up, round, estimate, or fabricate any numbers.
If a number is not explicitly in the text, DO NOT include that metric.

OCR TEXT:
{ocr_text}

EXTRACTION CHECKLIST:
✓ Company/Seller info (name, address, GSTIN, state, email) - EXACT as written
✓ Buyer info (name, address, GSTIN, state) - EXACT as written
✓ Memo metadata (credit note no, dates, references) - EXACT as written
✓ Line items (description, HSN, quantity, rate, amount) - EXACT numbers
✓ Tax rates (CGST, SGST) - EXACT percentages
✓ 5-bullet executive summary - based on REAL numbers from text
✓ Key metrics with EXACT values from document + source pages + confidence tags
✓ Top 3 credit risks with severity - based on ACTUAL data trends

VERIFICATION STEPS:
1. Find the number in the OCR text above
2. Copy it EXACTLY (including currency symbols, decimals)
3. Record the page number where you found it
4. Mark confidence: "strong" if directly stated, "calculated" if you computed it from other numbers

Remember:
- Parse "--- PAGE X ---" markers for accurate page attribution
- Use "strong" confidence for direct extracts
- Use "calculated" confidence for computed ratios (show formula with source numbers)
- Include source_pages for all metrics and risks
- If credit memo fields not in document, use empty strings but extract all financial data

Return JSON only.
"""
            }
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # Remove markdown code blocks if present
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:]  # Remove ```json
    if raw_output.startswith("```"):
        raw_output = raw_output[3:]  # Remove ```
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3]  # Remove trailing ```
    raw_output = raw_output.strip()

    try:
        # Parse JSON first to sanitize it
        data = json.loads(raw_output)
        
        # Sanitize: Convert None to empty strings for required string fields
        def sanitize_strings(obj):
            if isinstance(obj, dict):
                return {k: sanitize_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_strings(item) for item in obj]
            elif obj is None:
                return ""  # Convert None to empty string
            return obj
        
        # Apply sanitization to memo_meta and other fields
        if "memo_meta" in data and data["memo_meta"]:
            data["memo_meta"] = sanitize_strings(data["memo_meta"])
        if "company_info" in data and data["company_info"]:
            # Keep email and phone as null if not present
            for field in ["name", "address", "gstin", "state", "state_code"]:
                if field in data["company_info"] and data["company_info"][field] is None:
                    data["company_info"][field] = ""
        if "buyer_info" in data and data["buyer_info"]:
            data["buyer_info"] = {k: (v if v is not None else "") for k, v in data["buyer_info"].items()}
        
        # Validate and parse into Pydantic model
        memo = Memo.model_validate(data)
        return memo

    except ValidationError as e:
        raise ValueError(
            f"Model returned invalid JSON structure:\n{e}\n\nRaw output:\n{raw_output}"
        )

    except json.JSONDecodeError:
        raise ValueError(
            f"Model did not return valid JSON.\nRaw output:\n{raw_output}"
        )
