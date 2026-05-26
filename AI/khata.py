from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Sample khata data
# In real app, this will come from database
khata_data = {
    "customers": [
        {
            "name": "Ramesh Sharma",
            "phone": "9876543210",
            "transactions": [
                {"date": "01/04/2026", "type": "credit", "amount": 5000, "description": "Grocery saman"},
                {"date": "15/04/2026", "type": "credit", "amount": 3000, "description": "Oil more dal"},
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
    You are an Indian shop's khata manager.
    Today's date is: {today}
    
    This is the khata data:
    {json.dumps(khata_data, indent=2)}
    
    For each customer:
    1. Calculate total credit (credit - payment)
    2. How many days pending
    3. Tell the status (CLEAR, PENDING, OVERDUE)
    4. Create WhatsApp reminder message
    
    OVERDUE = pending for more than 45 days
    PENDING = pending for less than 45 days
    CLEAR = no credit pending
    
    Provide in JSON format:
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
                "reminder_message": "WhatsApp message in Hindi"
            }}
        ],
        "total_udhari": 0,
        "urgent_collections": ["collect from these first"],
        "business_insight": "overall business status"
    }}
    
    Only JSON do, kuch more mat likho.
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

# Test
result = analyze_khata(khata_data)
print(json.dumps(result, indent=2, ensure_ascii=False))