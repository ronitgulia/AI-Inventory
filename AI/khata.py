from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Sample khata data
# Real app mein yeh database se aayega
khata_data = {
    "customers": [
        {
            "name": "Ramesh Sharma",
            "phone": "9876543210",
            "transactions": [
                {"date": "01/04/2026", "type": "credit", "amount": 5000, "description": "Grocery saman"},
                {"date": "15/04/2026", "type": "credit", "amount": 3000, "description": "Oil aur dal"},
                {"date": "20/04/2026", "type": "payment", "amount": 2000, "description": "Cash payment"},
                {"date": "01/05/2026", "type": "credit", "amount": 4000, "description": "Monthly saman"},
            ]
        },
        {
            "name": "Suresh Gupta",
            "phone": "9765432100",
            "transactions": [
                {"date": "10/04/2026", "type": "credit", "amount": 8000, "description": "Wholesale order"},
                {"date": "25/04/2026", "type": "payment", "amount": 8000, "description": "Full payment"},
                {"date": "05/05/2026", "type": "credit", "amount": 6000, "description": "New order"},
            ]
        },
        {
            "name": "Mahesh Verma",
            "phone": "9654321000",
            "transactions": [
                {"date": "05/03/2026", "type": "credit", "amount": 12000, "description": "Bulk order"},
                {"date": "20/03/2026", "type": "payment", "amount": 5000, "description": "Partial payment"},
            ]
        }
    ]
}

def analyze_khata(khata_data):
    today = datetime.now().strftime("%d/%m/%Y")
    
    prompt = f"""
    Tu ek Indian dukan ka khata manager hai.
    Aaj ki date hai: {today}
    
    Yeh khata data hai:
    {json.dumps(khata_data, indent=2)}
    
    Har customer ke liye:
    1. Total udhari (credit - payment) calculate karo
    2. Kitne din se pending hai
    3. Status batao (CLEAR, PENDING, OVERDUE)
    4. WhatsApp reminder message banao Hindi mein
    
    OVERDUE = 45 din se zyada pending
    PENDING = 45 din se kam pending
    CLEAR = koi udhari nahi
    
    JSON format mein do:
    {{
        "summary": [
            {{
                "name": "customer naam",
                "phone": "number",
                "total_credit": 0,
                "total_paid": 0,
                "balance_due": 0,
                "days_pending": 0,
                "status": "CLEAR/PENDING/OVERDUE",
                "reminder_message": "Hindi mein WhatsApp message"
            }}
        ],
        "total_udhari": 0,
        "urgent_collections": ["sabse pehle in se lena hai"],
        "business_insight": "overall business ka haal"
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
result = analyze_khata(khata_data)
print(json.dumps(result, indent=2, ensure_ascii=False))