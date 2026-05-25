import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.stock import get_low_stock_products, get_all_products, update_stock
from core.billing import create_bill, print_bill
from core.distributor import print_margin_report
from core.khata import get_all_pending, add_payment, print_statement
from ai.bill_scan import scan_bill
from ai.inventory import analyze_inventory
from ai.gst import calculate_gst
from ai.khata import analyze_khata

def show_menu():
    print("\n" + "="*45)
    print("     🏪 AI INVENTORY MANAGEMENT SYSTEM")
    print("="*45)
    print("  1. 📦 Stock Dekhna")
    print("  2. ⚠️  Low Stock Alerts")
    print("  3. 🛒 Naya Bill Banana")
    print("  4. 📷 Bill Scan Karke Stock Update")
    print("  5. 📊 Distributor Margin Report")
    print("  6. 📒 Khata Book")
    print("  7. 💰 Payment Lena")
    print("  8. 🤖 AI Inventory Analysis")
    print("  9. 🚪 Bahar Jaana")
    print("="*45)

def show_stock():
    products = get_all_products()
    print("\n=== STOCK LIST ===")
    for p in products:
        status = "⚠️" if p["current_stock"] <= p["min_stock"] else "✅"
        print(f"{status} {p['name']} — {p['current_stock']} {p['unit']}")

def show_low_stock():
    low = get_low_stock_products()
    if not low:
        print("\n✅ Sab stock theek hai!")
        return
    print("\n=== LOW STOCK ALERT ===")
    for p in low:
        emoji = "🔴" if p["status"] == "CRITICAL" else "🟡"
        print(f"{emoji} {p['name']} — {p['status']}")
        print(f"   Bacha: {p['current_stock']} | Minimum: {p['min_stock']} {p['unit']}")

def new_bill():
    print("\n=== NAYA BILL ===")
    customer_id = input("Customer ID daalo (C001, C002...): ").strip()
    
    items = []
    while True:
        product_id = input("Product ID daalo (ya 'done' likho bill khatam karne ke liye): ").strip()
        if product_id.lower() == "done":
            break
        quantity = float(input("Quantity daalo: "))
        items.append({"product_id": product_id, "quantity": quantity})
    
    print("Payment mode: 1. Cash  2. Udhari")
    mode_choice = input("Choice (1/2): ").strip()
    payment_mode = "cash" if mode_choice == "1" else "udhari"
    
    result = create_bill(customer_id, items, payment_mode)
    if result["success"]:
        print_bill(result["bill"])
    else:
        print(f"❌ Error: {result['message']}")

def scan_bill_update_stock():
    print("\n=== BILL SCAN ===")
    image_path = input("Bill ki image ka path daalo: ").strip()
    
    if not os.path.exists(image_path):
        print("❌ Image nahi mili!")
        return
    
    print("🤖 AI bill scan kar raha hai...")
    result = scan_bill(image_path)
    
    print("\n📋 Scan Result:")
    print(f"Store: {result['store_name']}")
    print(f"Date: {result['date']}")
    print(f"Items: {len(result['items'])}")
    
    for item in result["items"]:
        print(f"  - {item['name']}: {item['quantity']} units @ ₹{item['price']}")

def show_khata():
    pending = get_all_pending()
    if not pending:
        print("\n✅ Koi udhari nahi hai!")
        return
    print("\n=== KHATA BOOK ===")
    for c in pending:
        print(f"👤 {c['name']} — ₹{c['balance_due']} pending")
    
    choice = input("\nKisi ka statement dekhna hai? (ID daalo ya Enter skip karo): ").strip()
    if choice:
        print_statement(choice)

def receive_payment():
    print("\n=== PAYMENT LENA ===")
    customer_id = input("Customer ID daalo: ").strip()
    amount = float(input("Amount daalo: ₹"))
    note = input("Note (optional): ").strip() or "Cash payment"
    
    result = add_payment(customer_id, amount, note)
    if result["success"]:
        print(f"✅ ₹{result['amount_paid']} payment li — {result['customer_name']}")
        print(f"   Remaining: ₹{result['remaining_balance']}")
    else:
        print(f"❌ Error: {result['message']}")

def ai_analysis():
    from core.stock import load_stock
    print("\n🤖 AI Inventory Analysis chal raha hai...")
    
    stock = load_stock()
    stock_dict = {}
    for p in stock["products"]:
        stock_dict[p["name"]] = {
            "current_stock": p["current_stock"],
            "min_stock": p["min_stock"],
            "unit": p["unit"]
        }
    
    result = analyze_inventory(stock_dict)
    
    print("\n=== AI ANALYSIS ===")
    print(f"🔴 Critical/Low items: {len(result['shortages'])}")
    for s in result["shortages"]:
        print(f"   {s['product']} — {s['status']}")
    
    print(f"\n✅ Healthy stock: {', '.join(result['healthy_stock'])}")
    
    print("\n💡 Recommendations:")
    for r in result["recommendations"]:
        print(f"   • {r}")

def main():
    print("🏪 AI Inventory System mein aapka swagat hai!")
    
    while True:
        show_menu()
        choice = input("\nChoice daalo (1-9): ").strip()
        
        if choice == "1":
            show_stock()
        elif choice == "2":
            show_low_stock()
        elif choice == "3":
            new_bill()
        elif choice == "4":
            scan_bill_update_stock()
        elif choice == "5":
            print_margin_report()
        elif choice == "6":
            show_khata()
        elif choice == "7":
            receive_payment()
        elif choice == "8":
            ai_analysis()
        elif choice == "9":
            print("\n🙏 Dhanyavaad! Phir milenge!")
            break
        else:
            print("❌ Galat choice! 1-9 mein se chuno.")

if __name__ == "__main__":
    main()