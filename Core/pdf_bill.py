from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

OUTPUT_DIR = "data/bills"

def ensure_output_dir():
  if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_pdf_bill(bill_data, shop_info=None):
  """
  Generate PDF for the bill
  """
  ensure_output_dir()

  if shop_info is None:
    shop_info = {
      "name": "Meri Dukan",
      "address": "123 Main Market",
      "phone": "9876543210",
      "gstin": "07AAACS1234A1Z5"
    }

  # PDF file name
  filename = f"{OUTPUT_DIR}/{bill_data['bill_number']}.pdf"
  
  # Create canvas
  c = canvas.Canvas(filename, pagesize=A4)
  width, height = A4

  # ═══════════════════════════════
  # HEADER — Shop Name
  # ═══════════════════════════════
  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.rect(0, height - 80*mm, width, 80*mm, fill=1, stroke=0)

  c.setFillColor(colors.white)
  c.setFont("Helvetica-Bold", 24)
  c.drawCentredString(width/2, height - 25*mm, shop_info["name"])

  c.setFont("Helvetica", 11)
  c.drawCentredString(width/2, height - 35*mm, shop_info["address"])
  c.drawCentredString(width/2, height - 43*mm, f"Phone: {shop_info['phone']}")
  c.drawCentredString(width/2, height - 51*mm, f"GSTIN: {shop_info['gstin']}")

  # ═══════════════════════════════
  # BILL INFO
  # ═══════════════════════════════
  c.setFillColor(colors.HexColor("#f0f0f0"))
  c.rect(10*mm, height - 105*mm, width - 20*mm, 20*mm, fill=1, stroke=0)

  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.setFont("Helvetica-Bold", 11)
  c.drawString(15*mm, height - 92*mm, f"Bill No: {bill_data['bill_number']}")
  c.drawRightString(width - 15*mm, height - 92*mm, f"Date: {bill_data['date']}")

  c.setFont("Helvetica", 10)
  payment_color = colors.HexColor("#e74c3c") if bill_data['payment_mode'] == 'udhari' else colors.HexColor("#27ae60")
  c.setFillColor(payment_color)
  c.drawString(15*mm, height - 100*mm, f"Payment: {bill_data['payment_mode'].upper()}")
  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.drawRightString(width - 15*mm, height - 100*mm, f"Customer ID: {bill_data['customer_id']}")

  # ═══════════════════════════════
  # TABLE HEADER
  # ═══════════════════════════════
  table_y = height - 120*mm
  
  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.rect(10*mm, table_y - 8*mm, width - 20*mm, 10*mm, fill=1, stroke=0)

  c.setFillColor(colors.white)
  c.setFont("Helvetica-Bold", 10)
  c.drawString(15*mm, table_y - 5*mm, "Product")
  c.drawCentredString(110*mm, table_y - 5*mm, "Qty")
  c.drawCentredString(140*mm, table_y - 5*mm, "Unit")
  c.drawCentredString(165*mm, table_y - 5*mm, "Price")
  c.drawRightString(width - 15*mm, table_y - 5*mm, "Total")

  # ═══════════════════════════════
  # TABLE ROWS
  # ═══════════════════════════════
  row_y = table_y - 18*mm
  
  for i, item in enumerate(bill_data["items"]):
    # Alternate row color
    if i % 2 == 0:
      c.setFillColor(colors.HexColor("#f8f9fa"))
      c.rect(10*mm, row_y - 2*mm, width - 20*mm, 9*mm, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#2c2c2c"))
    c.setFont("Helvetica", 10)
    c.drawString(15*mm, row_y + 2*mm, item["name"])
    c.drawCentredString(110*mm, row_y + 2*mm, str(item["quantity"]))
    c.drawCentredString(140*mm, row_y + 2*mm, item["unit"])
    c.drawCentredString(165*mm, row_y + 2*mm, f"Rs.{item['price_per_unit']}")
    c.drawRightString(width - 15*mm, row_y + 2*mm, f"Rs.{item['total']}")

    row_y -= 10*mm

  # ═══════════════════════════════
  # TOTALS
  # ═══════════════════════════════
  totals_y = row_y - 5*mm

  # Line
  c.setStrokeColor(colors.HexColor("#1a1a2e"))
  c.setLineWidth(0.5)
  c.line(10*mm, totals_y, width - 10*mm, totals_y)

  totals_y -= 8*mm

  c.setFillColor(colors.HexColor("#2c2c2c"))
  c.setFont("Helvetica", 11)
  c.drawRightString(width - 50*mm, totals_y, "Subtotal:")
  c.drawRightString(width - 15*mm, totals_y, f"Rs.{bill_data['subtotal']}")

  totals_y -= 8*mm
  c.drawRightString(width - 50*mm, totals_y, "GST (5%):")
  c.drawRightString(width - 15*mm, totals_y, f"Rs.{bill_data['tax']}")

  # Grand Total box
  totals_y -= 12*mm
  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.rect(width - 80*mm, totals_y - 3*mm, 70*mm, 12*mm, fill=1, stroke=0)
  c.setFillColor(colors.white)
  c.setFont("Helvetica-Bold", 13)
  c.drawRightString(width - 50*mm, totals_y + 2*mm, "GRAND TOTAL:")
  c.drawRightString(width - 15*mm, totals_y + 2*mm, f"Rs.{bill_data['grand_total']}")

  # ═══════════════════════════════
  # FOOTER
  # ═══════════════════════════════
  c.setFillColor(colors.HexColor("#f0f0f0"))
  c.rect(0, 0, width, 25*mm, fill=1, stroke=0)

  c.setFillColor(colors.HexColor("#1a1a2e"))
  c.setFont("Helvetica-Bold", 12)
  c.drawCentredString(width/2, 17*mm, "Thank you! Visit again! ")
  c.setFont("Helvetica", 9)
  c.drawCentredString(width/2, 10*mm, "This is a computer generated bill")
  c.drawCentredString(width/2, 5*mm, f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

  c.save()
  print(f" PDF bill saved: {filename}")
  return filename

# Test
if __name__ == "__main__":
  import sys
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  
  # Sample bill data
  test_bill = {
    "bill_number": "BILL-202605-TEST",
    "date": "25/05/2026 12:00",
    "customer_id": "C001",
    "payment_mode": "cash",
    "items": [
      {
        "name": "Basmati Rice",
        "quantity": 5,
        "unit": "kg",
        "price_per_unit": 95,
        "total": 475
      },
      {
        "name": "Refined Oil",
        "quantity": 2,
        "unit": "litre",
        "price_per_unit": 140,
        "total": 280
      },
      {
        "name": "Sugar",
        "quantity": 3,
        "unit": "kg",
        "price_per_unit": 52,
        "total": 156
      }
    ],
    "subtotal": 911,
    "tax": 45.55,
    "grand_total": 956.55
  }

  filename = generate_pdf_bill(test_bill)
  print(f"PDF saved here: {filename}")