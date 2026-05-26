import sys
import os
from dotenv import load_dotenv

# Sabse pehle .env load karo
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.stock import get_low_stock_products, get_all_products, update_stock, load_stock
from core.billing import create_bill, print_bill
from core.distributor import print_margin_report
from core.khata import get_all_pending, add_payment, print_statement
from core.barcode import scan_barcode_from_camera, add_item_by_barcode
from core.pdf_bill import generate_pdf_bill
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
    print("  9. 🔍 Barcode Scan Test")
    print(" 10. 🚪 Bahar Jaana")
    print("="*45)

def show_stock():
    products = get_all_products()
    print("\n=== STOCK LIST ===")
    for p in products:
        status = "⚠️ " if p["current_stock"] <= p["min_stock"] else "✅"
        print(f"{status} {p['name']} — {p['current_stock']} {p['unit']} | Buy: ₹{p['purchase_price']} | Sell: ₹{p['selling_price']}")

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
        print("\nProduct kaise add karein?")
        print("1. Barcode scan karke")
        print("2. Manual ID daalo")
        print("3. Bill complete karo")

        choice = input("Choice (1/2/3): ").strip()

        if choice == "3":
            break

        elif choice == "1":
            result = scan_barcode_from_camera()
            if result["success"]:
                product = result["product"]
                print(f"✅ Mila: {product['name']} — ₹{product['selling_price']}/{product['unit']}")
                quantity = float(input("Quantity daalo: "))
                items.append({
                    "product_id": product["id"],
                    "quantity": quantity
                })
            else:
                print(f"❌ {result['message']}")

        elif choice == "2":
            print("\nAvailable Products:")
            for p in get_all_products():
                print(f"  {p['id']} — {p['name']} — ₹{p['selling_price']}/{p['unit']}")
            product_id = input("Product ID daalo: ").strip()
            quantity = float(input("Quantity daalo: "))
            items.append({"product_id": product_id, "quantity": quantity})

    if not items:
        print("❌ Koi item add nahi kiya!")
        return

    print("\nPayment mode:")
    print("1. Cash")
    print("2. Udhari")
    mode_choice = input("Choice (1/2): ").strip()
    payment_mode = "cash" if mode_choice == "1" else "udhari"

    result = create_bill(customer_id, items, payment_mode)
    if result["success"]:
        print_bill(result["bill"])

        # PDF generate karo
        pdf_choice = input("\nPDF generate karni hai? (y/n): ").strip()
        if pdf_choice.lower() == "y":
            pdf_file = generate_pdf_bill(result["bill"])
            print(f"✅ PDF save hui: {pdf_file}")
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
    print(f"Items found: {len(result['items'])}")

    for item in result["items"]:
        print(f"  - {item['name']}: {item['quantity']} units @ ₹{item['price']}")

    # Stock update karo
    update_choice = input("\nStock update karni hai? (y/n): ").strip()
    if update_choice.lower() == "y":
        for item in result["items"]:
            products = get_all_products()
            for p in products:
                if p["name"].lower() == item["name"].lower():
                    update_stock(p["id"], item["quantity"], "add")
                    print(f"✅ {p['name']} stock update hua — +{item['quantity']}")

def show_khata():
    pending = get_all_pending()
    if not pending:
        print("\n✅ Koi udhari nahi hai!")
        return

    print("\n=== KHATA BOOK ===")
    total = 0
    for c in pending:
        print(f"👤 {c['name']} — ₹{c['balance_due']} pending | Phone: {c['phone']}")
        total += c['balance_due']
    print(f"\n💰 Total Pending: ₹{total}")

    choice = input("\nKisi ka statement dekhna hai? (ID daalo ya Enter skip karo): ").strip()
    if choice:
        print_statement(choice)

def receive_payment():
    print("\n=== PAYMENT LENA ===")

    pending = get_all_pending()
    if not pending:
        print("✅ Koi udhari nahi hai!")
        return

    print("Pending customers:")
    for c in pending:
        print(f"  {c['id']} — {c['name']} — ₹{c['balance_due']}")

    customer_id = input("\nCustomer ID daalo: ").strip()
    amount = float(input("Amount daalo: ₹"))
    note = input("Note (optional): ").strip() or "Cash payment"

    result = add_payment(customer_id, amount, note)
    if result["success"]:
        print(f"✅ ₹{result['amount_paid']} payment li — {result['customer_name']}")
        print(f"   Remaining balance: ₹{result['remaining_balance']}")
    else:
        print(f"❌ Error: {result['message']}")

def ai_analysis():
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

    print("\n=== AI ANALYSIS REPORT ===")

    if result["shortages"]:
        print(f"\n⚠️  Shortage Items ({len(result['shortages'])}):")
        for s in result["shortages"]:
            emoji = "🔴" if s["status"] == "CRITICAL" else "🟡"
            print(f"  {emoji} {s['product']} — {s['status']}")
            print(f"     Bacha: {s['current_stock']} | Chahiye: {s['restock_amount']} aur")

    if result["healthy_stock"]:
        print(f"\n✅ Healthy Stock: {', '.join(result['healthy_stock'])}")

    print(f"\n🚨 Urgent Restock: {', '.join(result['urgent_restock'])}")

    print("\n💡 AI Recommendations:")
    for r in result["recommendations"]:
        print(f"   • {r}")

def barcode_test():
    print("\n=== BARCODE SCAN TEST ===")
    print("1. Camera se scan")
    print("2. Cancel")

    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        result = scan_barcode_from_camera()
        if result["success"]:
            product = result["product"]
            print(f"\n✅ Product mila!")
            print(f"   Naam: {product['name']}")
            print(f"   Stock: {product['current_stock']} {product['unit']}")
            print(f"   Price: ₹{product['selling_price']}")
        else:
            print(f"❌ {result['message']}")

def main():
    print("🏪 AI Inventory System mein aapka swagat hai!")

    while True:
        show_menu()
        choice = input("\nChoice daalo (1-10): ").strip()

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
            barcode_test()
        elif choice == "10":
            print("\n🙏 Dhanyavaad! Phir milenge!")
            break
        else:
            print("❌ Galat choice! 1-10 mein se chuno.")

if __name__ == "__main__":
    main()