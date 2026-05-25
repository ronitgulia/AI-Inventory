import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.billing import create_bill, print_bill

print("=== Bill Banana Test ===")

# Cash bill
result = create_bill(
    customer_id="C001",
    items=[
        {"product_id": "P001", "quantity": 5},
        {"product_id": "P002", "quantity": 2}
    ],
    payment_mode="cash"
)

if result["success"]:
    print_bill(result["bill"])
else:
    print(f"Error: {result['message']}")

# Udhari bill
result2 = create_bill(
    customer_id="C002",
    items=[
        {"product_id": "P003", "quantity": 3}
    ],
    payment_mode="udhari"
)

if result2["success"]:
    print_bill(result2["bill"])
    print("Udhari mein add ho gaya!")
else:
    print(f"Error: {result2['message']}")