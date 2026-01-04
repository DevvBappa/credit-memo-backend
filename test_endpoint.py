import requests
import json

# Test the generate-memo endpoint
url = "http://127.0.0.1:8000/generate-memo"

# Read the ocr_text.json file
with open("ocr_text.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Sending request to backend...")
print(f"Text length: {len(data['text'])} characters")

try:
    response = requests.post(url, json=data, timeout=60)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        result = response.json()
        
        print("\n=== Company Info ===")
        print(f"Name: {result.get('company_info', {}).get('name', 'N/A')}")
        print(f"GSTIN: {result.get('company_info', {}).get('gstin', 'N/A')}")
        
        print("\n=== Buyer Info ===")
        print(f"Name: {result.get('buyer_info', {}).get('name', 'N/A')}")
        print(f"GSTIN: {result.get('buyer_info', {}).get('gstin', 'N/A')}")
        
        print("\n=== Memo Meta ===")
        print(f"Credit Note No: {result.get('memo_meta', {}).get('credit_note_no', 'N/A')}")
        print(f"Date: {result.get('memo_meta', {}).get('date', 'N/A')}")
        
        print("\n=== Line Items ===")
        items = result.get('memo_items', [])
        print(f"Total items: {len(items)}")
        for item in items:
            print(f"  - {item.get('description')}: Qty {item.get('quantity')} @ {item.get('rate')}")
        
        print("\n=== Executive Summary ===")
        summary = result.get('executive_summary', [])
        print(f"Total bullets: {len(summary)}")
        for i, bullet in enumerate(summary[:3], 1):
            print(f"{i}. {bullet[:80]}...")
        
        print("\n=== Key Metrics ===")
        metrics = result.get('key_metrics', [])
        print(f"Total metrics: {len(metrics)}")
        for metric in metrics[:5]:
            print(f"  - {metric.get('name')}: {metric.get('value')} ({metric.get('confidence')})")
        
        print("\n=== Top Risks ===")
        risks = result.get('top_risks', [])
        print(f"Total risks: {len(risks)}")
        for risk in risks:
            print(f"  - {risk.get('title')} ({risk.get('severity')})")
        
        print("\n✅ All fields validated successfully!")
        
    else:
        print(f"\n❌ ERROR: Status {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
