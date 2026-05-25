import json
from datetime import datetime

CUSTOMERS_FILE = "data/customers.json"

def load_customers():
    with open(CUSTOMERS_FILE, "r") as f:
        return json.load(f)

def save_customers(data):
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_customers():
    """Saare customers return karo"""
    data = load_customers()
    return data["customers"]

def get_customer_by_id(customer_id):
    """ID se customer dhundo"""
    customers = get_all_customers()
    for c in customers:
        if c["id"] == customer_id:
            return c
    return None

def add_customer(name, phone, address=""):
    """Naya customer add karo"""
    data = load_customers()
    new_num = len(data["customers"]) + 1
    new_customer = {
        "id": f"C{new_num:03d}",
        "name": name,
        "phone": phone,
        "address": address,
        "balance_due": 0,
        "transactions": [],
        "joined_date": datetime.now().strftime("%d/%m/%Y")
    }
    data["customers"].append(new_customer)
    save_customers(data)
    return {"success": True, "customer": new_customer}

def add_payment(customer_id, amount, note="Cash payment"):
    """Customer ne payment ki"""
    data = load_customers()
    
    for customer in data["customers"]:
        if customer["id"] == customer_id:
            if amount > customer["balance_due"]:
                return {
                    "success": False,
                    "message": f"Payment zyada hai! Balance sirf ₹{customer['balance_due']} hai"
                }
            
            customer["balance_due"] -= amount
            customer["balance_due"] = round(customer["balance_due"], 2)
            customer["transactions"].append({
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "type": "payment",
                "amount": amount,
                "description": note,
                "balance_after": customer["balance_due"]
            })
            
            save_customers(data)
            return {
                "success": True,
                "customer_name": customer["name"],
                "amount_paid": amount,
                "remaining_balance": customer["balance_due"]
            }
    
    return {"success": False, "message": "Customer nahi mila!"}

def get_customer_statement(customer_id):
    """Customer ka poora hisaab"""
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return None
    
    total_credit = sum(
        t["amount"] for t in customer["transactions"] 
        if t["type"] == "credit"
    )
    total_paid = sum(
        t["amount"] for t in customer["transactions"] 
        if t["type"] == "payment"
    )
    
    return {
        "customer": customer["name"],
        "phone": customer["phone"],
        "total_credit": total_credit,
        "total_paid": total_paid,
        "balance_due": customer["balance_due"],
        "transactions": customer["transactions"]
    }

def print_statement(customer_id):
    """Statement print karo"""
    statement = get_customer_statement(customer_id)
    
    if not statement:
        print("Customer nahi mila!")
        return
    
    print("\n" + "="*45)
    print(f"   KHATA STATEMENT — {statement['customer']}")
    print(f"   Phone: {statement['phone']}")
    print("="*45)
    
    for t in statement["transactions"]:
        if t["type"] == "credit":
            print(f"  📤 {t['date']} | Udhari: ₹{t['amount']}")
            print(f"     {t['description']}")
        else:
            print(f"  📥 {t['date']} | Payment: ₹{t['amount']}")
            print(f"     {t['description']}")
    
    print("-"*45)
    print(f"  Total Udhari:  ₹{statement['total_credit']}")
    print(f"  Total Payment: ₹{statement['total_paid']}")
    print(f"  Balance Due:   ₹{statement['balance_due']}")
    print("="*45)

def get_all_pending():
    """Saare pending customers"""
    customers = get_all_customers()
    pending = []
    
    for c in customers:
        if c["balance_due"] > 0:
            pending.append({
                "id": c["id"],
                "name": c["name"],
                "phone": c["phone"],
                "balance_due": c["balance_due"]
            })
    
    pending.sort(key=lambda x: x["balance_due"], reverse=True)
    return pending

# Test karo
if __name__ == "__main__":
    print("=== Pending Customers ===")
    pending = get_all_pending()
    for c in pending:
        print(f"👤 {c['name']} — ₹{c['balance_due']} pending")
    
    print("\n=== Payment Add karo ===")
    result = add_payment("C001", 5000, "Cash payment aaya")
    print(f"Payment result: {result}")
    
    print("\n=== C001 ka Statement ===")
    print_statement("C001")