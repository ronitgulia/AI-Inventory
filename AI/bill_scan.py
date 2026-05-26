from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import base64

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def scan_bill(image_path):
    # Convert image to base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
    This is an image of a bill/invoice.
    Scan this and give me the data in JSON format:
    {
        "store_name": "dukan ka naam",
        "date": "bill ki date",
        "items": [
            {
                "name": "product ka naam",
                "quantity": 1,
                "price": 0.0,
                "total": 0.0
            }
        ],
        "subtotal": 0.0,
        "tax": 0.0,
        "grand_total": 0.0
    }
    Only JSON do, kuch more mat likho.
    """

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # Clean response
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    # Parse JSON
    data = json.loads(text)
    return data

# Test
result = scan_bill("bill.jpg")
print(json.dumps(result, indent=2, ensure_ascii=False))