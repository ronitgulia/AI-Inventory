import json
from datetime import datetime

DISTRIBUTORS_FILE = "data/distributors.json"

def load_distributors():
  with open(DISTRIBUTORS_FILE, "r") as f:
    return json.load(f)

def save_distributors(data):
  with open(DISTRIBUTORS_FILE, "w") as f:
    json.dump(data, f, indent=2)

def get_all_distributors():
  """Return all distributors"""
  data = load_distributors()
  return data["distributors"]

def get_distributor_by_id(distributor_id):
  """Find distributor by ID"""
  distributors = get_all_distributors()
  for d in distributors:
    if d["id"] == distributor_id:
      return d
  return None

def add_distributor(distributor_data):
  """Add new distributor"""
  data = load_distributors()
  existing_ids = [d["id"] for d in data["distributors"]]
  new_num = len(existing_ids) + 1
  distributor_data["id"] = f"D{new_num:03d}"
  distributor_data["joined_date"] = datetime.now().strftime("%d/%m/%Y")
  data["distributors"].append(distributor_data)
  save_distributors(data)
  return {"success": True, "distributor_id": distributor_data["id"]}

def calculate_margins(selling_price, purchase_price):
  """Calculate margin"""
  margin_amount = selling_price - purchase_price
  margin_percent = round((margin_amount / purchase_price) * 100, 2)
  return {
    "purchase_price": purchase_price,
    "selling_price": selling_price,
    "margin_amount": margin_amount,
    "margin_percent": margin_percent
  }

def get_distributor_margins():
  """
  Compare margin of each distributor
  Stock data se purchase price lenge
  """
  from core.stock import get_all_products

  distributors = get_all_distributors()
  products = get_all_products()

  result = []

  for distributor in distributors:
    dist_products = []

    for product in products:
      if product["distributor_id"] == distributor["id"]:
        margin = calculate_margins(
          product["selling_price"],
          product["purchase_price"]
        )
        dist_products.append({
          "product": product["name"],
          "unit": product["unit"],
          "purchase_price": margin["purchase_price"],
          "selling_price": margin["selling_price"],
          "margin_amount": margin["margin_amount"],
          "margin_percent": margin["margin_percent"]
        })

    result.append({
      "distributor_id": distributor["id"],
      "distributor_name": distributor["name"],
      "area": distributor["area"],
      "phone": distributor["phone"],
      "outstanding": distributor["outstanding"],
      "products": dist_products
    })

  return result

def print_margin_report():
  """Print margin report"""
  margins = get_distributor_margins()

  print("\n" + "="*50)
  print("    DISTRIBUTOR MARGIN REPORT")
  print("="*50)

  for dist in margins:
    print(f"\n {dist['distributor_name']} — {dist['area']}")
    print(f"  Phone: {dist['phone']}")
    print(f"  Outstanding: ₹{dist['outstanding']}")
    print(f"  {'-'*40}")

    for p in dist["products"]:
      print(f"  {p['product']}")
      print(f"  Buy: ₹{p['purchase_price']} | Sell: ₹{p['selling_price']} | Margin: {p['margin_percent']}%")

  print("\n" + "="*50)

# Test
if __name__ == "__main__":
  print_margin_report()