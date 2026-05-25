from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import base64

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def scan_bill(image_path):
    # Image ko base64 mein convert karo
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
    Yeh ek bill/invoice ki image hai.
    Isse scan karke mujhe JSON format mein yeh data do:
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
    Sirf JSON do, kuch aur mat likho.
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

    # Response clean karo
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    # JSON parse karo
    data = json.loads(text)
    return data

# Test karo
result = scan_bill("bill.jpg")
print(json.dumps(result, indent=2, ensure_ascii=False))