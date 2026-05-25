from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Sample order data
# Real app mein yeh bill scan se aayega
order_data = {
    "seller": {
        "name": "Sharma General Store",
        "gstin": "07AAACS1234A1Z5",
        "address": "123 Main Market, Delhi"
    },
    "buyer": {
        "name": "Ramesh Traders",
        "gstin": "07AABCR5678B1Z3",
        "address": "456 Shop Road, Delhi"
    },
    "invoice_number": "INV-2024-001",
    "date": "24/05/2026",
    "items": [
        {"name": "Basmati Rice", "quantity": 50, "unit": "kg", "price_per_unit": 80},
        {"name": "Refined Oil", "quantity": 20, "unit": "litre", "price_per_unit": 120},
        {"name": "Sugar", "quantity": 30, "unit": "kg", "price_per_unit": 45},
        {"name": "Wheat Flour", "quantity": 25, "unit": "kg", "price_per_unit": 35}
    ],
    "supply_type": "intra"  # intra = same state, inter = different state
}

def calculate_gst(order_data):
    prompt = f"""
    Tu ek GST expert hai Indian taxation ka.
    
    Yeh order data hai:
    {json.dumps(order_data, indent=2)}
    
    Har item ke liye:
    1. Sahi HSN code batao
    2. GST rate batao
    3. Agar supply_type "intra" hai toh CGST + SGST lagao (dono equal)
    4. Agar supply_type "inter" hai toh sirf IGST lagao
    5. Total amount calculate karo
    
    Mujhe JSON format mein do:
    {{
        "invoice_number": "INV-2024-001",
        "date": "date",
        "seller": {{}},
        "buyer": {{}},
        "items": [
            {{
                "name": "product naam",
                "hsn_code": "HSN code",
                "quantity": 0,
                "unit": "unit",
                "price_per_unit": 0,
                "taxable_amount": 0,
                "gst_rate": 0,
                "cgst_rate": 0,
                "cgst_amount": 0,
                "sgst_rate": 0,
                "sgst_amount": 0,
                "igst_rate": 0,
                "igst_amount": 0,
                "total_amount": 0
            }}
        ],
        "summary": {{
            "total_taxable_amount": 0,
            "total_cgst": 0,
            "total_sgst": 0,
            "total_igst": 0,
            "total_tax": 0,
            "grand_total": 0
        }}
    }}
    
    Sirf JSON do, kuch aur mat likho.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)
    return data

# Test karo
result = calculate_gst(order_data)
print(json.dumps(result, indent=2, ensure_ascii=False))