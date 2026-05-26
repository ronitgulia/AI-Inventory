from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI(
  api_key=os.getenv("GROK_API_KEY"),
  base_url="https://api.groq.com/openai/v1"
)

# This is our sample stock data
# In real app, this will come from database
stock_data = {
  "Paneer Tikka": {"current_stock": 5, "min_stock": 10, "unit": "kg"},
  "Veg Biryani": {"current_stock": 2, "min_stock": 15, "unit": "kg"},
  "Fresh Lime Soda": {"current_stock": 50, "min_stock": 20, "unit": "bottles"},
  "Butter Naan": {"current_stock": 8, "min_stock": 30, "unit": "pieces"},
  "Dal Makhani": {"current_stock": 3, "min_stock": 10, "unit": "kg"},
}

def analyze_inventory(stock_data):
  prompt = f"""
  You are a smart inventory manager for an Indian wholesale business.
  
  This is my current stock data:
  {json.dumps(stock_data, indent=2)}
  
  Tell me this in JSON format:
  {{
    "shortages": [
      {{
        "product": "product name",
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
    "urgent_restock": ["order this first"]
  }}
  
  Rules:
  - If current_stock < 30% of min_stock then CRITICAL
  - If current_stock < min_stock then LOW
  - Only JSON do, kuch more mat likho
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
result = analyze_inventory(stock_data)
print(json.dumps(result, indent=2, ensure_ascii=False))