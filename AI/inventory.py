from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Yeh hamara sample stock data hai
# Real app mein yeh database se aayega
stock_data = {
    "Paneer Tikka": {"current_stock": 5, "min_stock": 10, "unit": "kg"},
    "Veg Biryani": {"current_stock": 2, "min_stock": 15, "unit": "kg"},
    "Fresh Lime Soda": {"current_stock": 50, "min_stock": 20, "unit": "bottles"},
    "Butter Naan": {"current_stock": 8, "min_stock": 30, "unit": "pieces"},
    "Dal Makhani": {"current_stock": 3, "min_stock": 10, "unit": "kg"},
}

def analyze_inventory(stock_data):
    prompt = f"""
    Tu ek smart inventory manager hai Indian wholesale business ke liye.
    
    Yeh mera current stock data hai:
    {json.dumps(stock_data, indent=2)}
    
    Mujhe yeh batao JSON format mein:
    {{
        "shortages": [
            {{
                "product": "product naam",
                "current_stock": 0,
                "min_stock": 0,
                "status": "CRITICAL ya LOW",
                "restock_amount": 0
            }}
        ],
        "healthy_stock": ["product1", "product2"],
        "recommendations": [
            "recommendation 1",
            "recommendation 2"
        ],
        "urgent_restock": ["sabse pehle yeh mangao"]
    }}
    
    Rules:
    - Agar current_stock < min_stock ka 30% hai toh CRITICAL
    - Agar current_stock < min_stock hai toh LOW
    - Sirf JSON do, kuch aur mat likho
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
result = analyze_inventory(stock_data)
print(json.dumps(result, indent=2, ensure_ascii=False))