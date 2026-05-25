import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.khata import get_all_pending, add_payment, print_statement

print("=== Pending Customers ===")
pending = get_all_pending()
for c in pending:
    print(f"👤 {c['name']} — ₹{c['balance_due']} pending")

print("\n=== Payment Add karo ===")
result = add_payment("C001", 5000, "Cash payment aaya")
print(f"Payment result: {result}")

print("\n=== C001 ka Statement ===")
print_statement("C001")