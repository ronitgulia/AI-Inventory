import json
import os
from datetime import datetime
from core.stock import get_product_by_barcode, get_product_by_id, update_stock

CUSTOMERS_FILE = "data/customers.json"
BILLS_FILE = "data/bills.json"

def load_customers():
    with open(CUSTOMERS_FILE, "r") as f:
        return json.load(f)

def save_customers(data):
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_bills():
    if not os.path.exists(BILLS_FILE):
        return {"bills": []}
    with open(BILLS_FILE, "r") as f:
        return json.load(f)

def save_bills(data):
    with open(BILLS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_bill_number():
    """Unique bill number generate karo"""
    bills = load_bills()
    count = len(bills["bills"]) + 1
    return f"BILL-{datetime.now().strftime('%Y%m')}-{count:04d}"

def create_bill(customer_id, items, payment_mode="cash"):
    """
    Naya bill banao
    items = [{"product_id": "P001", "quantity": 2}, ...]
    """
    bill_items = []
    subtotal = 0

    # Har item process karo
    for item in items:
        product = get_product_by_id(item["product_id"])
        
        if not product:
            return {"success": False, "message": f"Product {item['product_id']} nahi mila!"}

        # Stock check karo
        if product["current_stock"] < item["quantity"]:
            return {
                "success": False,
                "message": f"{product['name']} ka sirf {product['current_stock']} {product['unit']} bacha hai!"
            }

        item_total = product["selling_price"] * item["quantity"]
        subtotal += item_total

        bill_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "barcode": product["barcode"],
            "quantity": item["quantity"],
            "unit": product["unit"],
            "price_per_unit": product["selling_price"],
            "total": item_total
        })

    # GST calculate karo (simple 5% for now)
    tax = round(subtotal * 0.05, 2)
    grand_total = round(subtotal + tax, 2)

    # Bill object banao
    bill = {
        "bill_number": generate_bill_number(),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "customer_id": customer_id,
        "items": bill_items,
        "subtotal": subtotal,
        "tax": tax,
        "grand_total": grand_total,
        "payment_mode": payment_mode,
        "status": "paid" if payment_mode == "cash" else "pending"
    }

    # Stock update karo
    for item in items:
        update_stock(item["product_id"], item["quantity"], "subtract")

    # Bill save karo
    bills_data = load_bills()
    bills_data["bills"].append(bill)
    save_bills(bills_data)

    # Agar udhari hai toh customer balance update karo
    if payment_mode == "udhari":
        customers_data = load_customers()
        for customer in customers_data["customers"]:
            if customer["id"] == customer_id:
                customer["balance_due"] += grand_total
                customer["transactions"].append({
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "type": "credit",
                    "amount": grand_total,
                    "bill_number": bill["bill_number"],
                    "description": f"Bill {bill['bill_number']}"
                })
        save_customers(customers_data)

    return {"success": True, "bill": bill}

def print_bill(bill):
    """Bill print karo terminal mein"""
    print("\n" + "="*45)
    print(f"         BILL — {bill['bill_number']}")
    print(f"         Date: {bill['date']}")
    print("="*45)
    
    for item in bill["items"]:
        print(f"{item['name']}")
        print(f"  {item['quantity']} {item['unit']} x ₹{item['price_per_unit']} = ₹{item['total']}")
    
    print("-"*45)
    print(f"Subtotal:     ₹{bill['subtotal']}")
    print(f"GST (5%):     ₹{bill['tax']}")
    print(f"GRAND TOTAL:  ₹{bill['grand_total']}")
    print(f"Payment:      {bill['payment_mode'].upper()}")
    print("="*45)
    print("       Dhanyavaad! Phir aana! 🙏")
    print("="*45 + "\n")

# Test karo
if __name__ == "__main__":
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
        print("Udhari mein add ho gaya customer ke khate mein!")
    else:
        print(f"Error: {result2['message']}")