import sys
import os
from dotenv import load_dotenv

# Load .env first
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.stock import get_low_stock_products, get_all_products, update_stock, load_stock, update_price
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
  print("   AI INVENTORY MANAGEMENT SYSTEM")
  print("="*45)
  print(" 1. View Stock")
  print(" 2.  Low Stock Alerts")
  print(" 3. Create New Bill")
  print(" 4. Scan Bill to Update Stock")
  print(" 5. Distributor Margin Report")
  print(" 6. Khata Book")
  print(" 7. Receive Payment")
  print(" 8. AI Inventory Analysis")
  print(" 9. Barcode Scan Test")
  print(" 10. Update Product Price")
  print(" 11. Exit")
  print("="*45)

def show_stock():
  products = get_all_products()
  print("\n=== STOCK LIST ===")
  for p in products:
    status = " " if p["current_stock"] <= p["min_stock"] else ""
    print(f"{status} {p['name']} — {p['current_stock']} {p['unit']} | Buy: ₹{p['purchase_price']} | Sell: ₹{p['selling_price']}")

def show_low_stock():
  low = get_low_stock_products()
  if not low:
    print("\n All stock is fine!")
    return
  print("\n=== LOW STOCK ALERT ===")
  for p in low:
    emoji = "" if p["status"] == "CRITICAL" else ""
    print(f"{emoji} {p['name']} — {p['status']}")
    print(f"  Remaining: {p['current_stock']} | Minimum: {p['min_stock']} {p['unit']}")

def new_bill():
  print("\n=== NEW BILL ===")
  customer_id = input("Enter Customer ID (C001, C002...): ").strip()

  items = []
  while True:
    print("\nHow to add product?")
    print("1. Scan barcode")
    print("2. Enter manual ID")
    print("3. Complete bill")

    choice = input("Choice (1/2/3): ").strip()

    if choice == "3":
      break

    elif choice == "1":
      result = scan_barcode_from_camera()
      if result["success"]:
        product = result["product"]
        print(f" Found: {product['name']} — ₹{product['selling_price']}/{product['unit']}")
        quantity = float(input("Enter quantity: "))
        items.append({
          "product_id": product["id"],
          "quantity": quantity
        })
      else:
        print(f" {result['message']}")

    elif choice == "2":
      print("\nAvailable Products:")
      for p in get_all_products():
        print(f" {p['id']} — {p['name']} — ₹{p['selling_price']}/{p['unit']}")
      product_id = input("Enter Product ID: ").strip()
      quantity = float(input("Enter quantity: "))
      items.append({"product_id": product_id, "quantity": quantity})

  if not items:
    print(" No item added!")
    return

  print("\nPayment mode:")
  print("1. Cash")
  print("2. Credit")
  mode_choice = input("Choice (1/2): ").strip()
  payment_mode = "cash" if mode_choice == "1" else "udhari"

  result = create_bill(customer_id, items, payment_mode)
  if result["success"]:
    print_bill(result["bill"])

    # Generate PDF
    pdf_choice = input("\nGenerate PDF? (y/n): ").strip()
    if pdf_choice.lower() == "y":
      pdf_file = generate_pdf_bill(result["bill"])
      print(f" PDF saved: {pdf_file}")
  else:
    print(f" Error: {result['message']}")

def scan_bill_update_stock():
  print("\n=== BILL SCAN ===")
  print("1. Upload bill image (File Explorer)")
  print("2. Enter bill image path manually")
  print("3. Cancel")
  
  choice = input("Choice (1/2/3): ").strip()
  
  if choice == "1":
    try:
      import tkinter as tk
      from tkinter import filedialog
      root = tk.Tk()
      root.withdraw() # Hide the main window
      root.attributes('-topmost', True) # Bring dialog to front
      image_path = filedialog.askopenfilename(
          title="Select Bill Image",
          filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
      )
      if not image_path:
        print(" No file selected!")
        return
    except ImportError:
      print(" UI upload not supported in this environment, please enter path manually.")
      image_path = input("Enter bill image path: ").strip()
  elif choice == "2":
    image_path = input("Enter bill image path: ").strip()
  elif choice == "3":
    return
  else:
    print(" Invalid choice!")
    return

  if not os.path.exists(image_path):
    print(" Image not found!")
    return

  print(" AI is scanning the bill...")
  result = scan_bill(image_path)

  print("\n Scan Result:")
  print(f"Store: {result['store_name']}")
  print(f"Date: {result['date']}")
  print(f"Items found: {len(result['items'])}")

  for item in result["items"]:
    print(f" - {item['name']}: {item['quantity']} units @ ₹{item['price']}")

  # Update stock
  update_choice = input("\nUpdate stock? (y/n): ").strip()
  if update_choice.lower() == "y":
    for item in result["items"]:
      products = get_all_products()
      found = False
      for p in products:
        if p["name"].lower() == item["name"].lower():
          update_stock(p["id"], item["quantity"], "add")
          print(f" {p['name']} stock updated — +{item['quantity']}")
          found = True
          break
      if not found:
        print(f" Warning: Product '{item['name']}' not found in inventory. Stock not updated.")

def show_khata():
  pending = get_all_pending()
  if not pending:
    print("\n No credit pending!")
    return

  print("\n=== KHATA BOOK ===")
  total = 0
  for c in pending:
    print(f" {c['name']} — ₹{c['balance_due']} pending | Phone: {c['phone']}")
    total += c['balance_due']
  print(f"\n Total Pending: ₹{total}")

  choice = input("\nWant to view someone's statement? (Enter ID or press Enter to skip): ").strip()
  if choice:
    print_statement(choice)

def receive_payment():
  print("\n=== RECEIVE PAYMENT ===")

  pending = get_all_pending()
  if not pending:
    print(" No credit pending!")
    return

  print("Pending customers:")
  for c in pending:
    print(f" {c['id']} — {c['name']} — ₹{c['balance_due']}")

  customer_id = input("\nEnter Customer ID: ").strip()
  amount = float(input("Enter amount: ₹"))
  note = input("Note (optional): ").strip() or "Cash payment"

  result = add_payment(customer_id, amount, note)
  if result["success"]:
    print(f" ₹{result['amount_paid']} payment received — {result['customer_name']}")
    print(f"  Remaining balance: ₹{result['remaining_balance']}")
  else:
    print(f" Error: {result['message']}")

def ai_analysis():
  print("\n Running AI Inventory Analysis...")

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
    print(f"\n Shortage Items ({len(result['shortages'])}):")
    for s in result["shortages"]:
      emoji = "" if s["status"] == "CRITICAL" else ""
      print(f" {emoji} {s['product']} — {s['status']}")
      print(f"   Remaining: {s['current_stock']} | Needed: {s['restock_amount']} more")

  if result["healthy_stock"]:
    print(f"\n Healthy Stock: {', '.join(result['healthy_stock'])}")

  print(f"\n Urgent Restock: {', '.join(result['urgent_restock'])}")

  print("\n AI Recommendations:")
  for r in result["recommendations"]:
    print(f"  • {r}")

def barcode_test():
  print("\n=== BARCODE SCAN TEST ===")
  print("1. Scan with camera")
  print("2. Cancel")

  choice = input("Choice (1/2): ").strip()

  if choice == "1":
    result = scan_barcode_from_camera()
    if result["success"]:
      product = result["product"]
      print(f"\n Product found!")
      print(f"  Name: {product['name']}")
      print(f"  Stock: {product['current_stock']} {product['unit']}")
      print(f"  Price: ₹{product['selling_price']}")
    else:
      print(f" {result['message']}")

def update_product_price():
  print("\n=== UPDATE PRODUCT PRICE ===")
  products = get_all_products()
  for p in products:
    print(f" {p['id']} — {p['name']} | Buy: ₹{p['purchase_price']} | Sell: ₹{p['selling_price']}")
    
  product_id = input("\nEnter Product ID to update (e.g., P001): ").strip()
  
  # Check if exists
  product = next((p for p in products if p['id'] == product_id), None)
  if not product:
    print(" Product not found!")
    return
    
  print(f"\nUpdating {product['name']}")
  print(f"Current Selling Price: ₹{product['selling_price']}")
  try:
    new_sell = input("Enter new Selling Price (press Enter to keep current): ").strip()
    new_selling_price = float(new_sell) if new_sell else product['selling_price']
    
    print(f"Current Purchase Price: ₹{product['purchase_price']}")
    new_buy = input("Enter new Purchase Price (press Enter to keep current): ").strip()
    new_purchase_price = float(new_buy) if new_buy else product['purchase_price']
    
    result = update_price(product_id, new_selling_price, new_purchase_price)
    if result["success"]:
      print(f" Successfully updated {result['product']} prices!")
      print(f"  New Sell Price: ₹{result['new_selling_price']} | New Buy Price: ₹{result['new_purchase_price']}")
    else:
      print(f" Error: {result['message']}")
  except ValueError:
    print(" Invalid price entered! Please enter a valid number.")

def main():
  print(" Welcome to AI Inventory System!")

  while True:
    show_menu()
    choice = input("\nEnter choice (1-11): ").strip()

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
      update_product_price()
    elif choice == "11":
      print("\n Thank you! See you again!")
      break
    else:
      print(" Invalid choice! Choose from 1-11.")

if __name__ == "__main__":
  main()