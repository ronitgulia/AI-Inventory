import json
import os
from datetime import datetime

# Data file ka path
STOCK_FILE = "data/stock.json"

def load_stock():
    """JSON se stock data load karo"""
    with open(STOCK_FILE, "r") as f:
        return json.load(f)

def save_stock(data):
    """Stock data JSON mein save karo"""
    with open(STOCK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_products():
    """Saare products return karo"""
    data = load_stock()
    return data["products"]

def get_product_by_barcode(barcode):
    """Barcode se product dhundo"""
    products = get_all_products()
    for product in products:
        if product["barcode"] == barcode:
            return product
    return None

def get_product_by_id(product_id):
    """ID se product dhundo"""
    products = get_all_products()
    for product in products:
        if product["id"] == product_id:
            return product
    return None

def update_stock(product_id, quantity_change, operation="add"):
    """
    Stock update karo
    operation = "add" → naya stock aaya
    operation = "subtract" → sale hui
    """
    data = load_stock()
    
    for product in data["products"]:
        if product["id"] == product_id:
            if operation == "add":
                product["current_stock"] += quantity_change
            elif operation == "subtract":
                if product["current_stock"] < quantity_change:
                    return {"success": False, "message": f"Sirf {product['current_stock']} {product['unit']} stock hai!"}
                product["current_stock"] -= quantity_change
            
            product["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_stock(data)
            
            return {
                "success": True,
                "product": product["name"],
                "new_stock": product["current_stock"],
                "unit": product["unit"]
            }
    
    return {"success": False, "message": "Product nahi mila!"}

def add_new_product(product_data):
    """Naya product add karo"""
    data = load_stock()
    
    # Naya ID generate karo
    existing_ids = [p["id"] for p in data["products"]]
    new_num = len(existing_ids) + 1
    product_data["id"] = f"P{new_num:03d}"
    product_data["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    data["products"].append(product_data)
    save_stock(data)
    
    return {"success": True, "product_id": product_data["id"]}

def get_low_stock_products():
    """Kam stock wale products dhundo"""
    products = get_all_products()
    low_stock = []
    
    for product in products:
        if product["current_stock"] <= product["min_stock"]:
            status = "CRITICAL" if product["current_stock"] <= product["min_stock"] * 0.3 else "LOW"
            low_stock.append({
                "id": product["id"],
                "name": product["name"],
                "current_stock": product["current_stock"],
                "min_stock": product["min_stock"],
                "unit": product["unit"],
                "status": status
            })
    
    return low_stock

# Test karo
if __name__ == "__main__":
    print("=== Saare Products ===")
    products = get_all_products()
    for p in products:
        print(f"{p['name']} — Stock: {p['current_stock']} {p['unit']}")
    
    print("\n=== Low Stock Alert ===")
    low = get_low_stock_products()
    for p in low:
        print(f"⚠️ {p['name']} — {p['status']} — Sirf {p['current_stock']} {p['unit']} bacha!")
    
    print("\n=== Stock Update Test ===")
    result = update_stock("P001", 50, "add")
    print(f"Stock update: {result}")