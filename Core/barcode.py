import cv2
import zxingcpp
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.stock import get_product_by_barcode, update_stock

def scan_barcode_from_camera():
  """
  Scan barcode with camera
  Press 'q' to close
  """
  cap = cv2.VideoCapture(0)

  if not cap.isOpened():
    return {"success": False, "message": "Camera not found!"}

  print("\n Camera started!")
  print("  Place barcode in front of camera — it will auto detect")
  print("  Press 'q' to close")

  scanned_product = None

  while True:
    ret, frame = cap.read()
    if not ret:
      break

    # Detect barcode
    results = zxingcpp.read_barcodes(frame)

    for result in results:
      barcode_data = result.text

      # Draw green box around barcode
      pos = result.position
      pts = [
        (pos.top_left.x, pos.top_left.y),
        (pos.top_right.x, pos.top_right.y),
        (pos.bottom_right.x, pos.bottom_right.y),
        (pos.bottom_left.x, pos.bottom_left.y)
      ]
      for i in range(4):
        cv2.line(frame, pts[i], pts[(i+1) % 4], (0, 255, 0), 2)

      # Show barcode data
      cv2.putText(
        frame, barcode_data,
        (pos.top_left.x, pos.top_left.y - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
        (0, 255, 0), 2
      )

      # Find product
      product = get_product_by_barcode(barcode_data)

      if product:
        cv2.putText(
          frame,
          f" {product['name']} | Rs.{product['selling_price']}",
          (pos.top_left.x, pos.top_left.y + 30),
          cv2.FONT_HERSHEY_SIMPLEX, 0.6,
          (255, 165, 0), 2
        )
        scanned_product = {
          "success": True,
          "barcode": barcode_data,
          "product": product
        }
      else:
        scanned_product = {
          "success": False,
          "barcode": barcode_data,
          "message": "Product is not in the database!"
        }

      # Auto return when barcode is found
      cap.release()
      cv2.destroyAllWindows()
      return scanned_product

    # Show frame
    cv2.imshow("Barcode Scanner — 'q' band karne ke liye", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  cv2.destroyAllWindows()
  return {"success": False, "message": "Scan cancelled"}

def scan_barcode_from_image(image_path):
  """
  Scan barcode from image
  """
  image = cv2.imread(image_path)

  if image is None:
    return {"success": False, "message": "Image nahi mili!"}

  results = zxingcpp.read_barcodes(image)

  if not results:
    return {"success": False, "message": "No barcode found in image!"}

  output = []
  for result in results:
    barcode_data = result.text
    product = get_product_by_barcode(barcode_data)

    output.append({
      "barcode": barcode_data,
      "type": str(result.format),
      "product": product if product else None,
      "found_in_stock": product is not None
    })

  return {"success": True, "results": output}

def add_item_by_barcode(barcode_data, quantity, operation="subtract"):
  """
  Find item by barcode and update stock
  operation = subtract — sale made
  operation = add — new stock arrived
  """
  product = get_product_by_barcode(barcode_data)

  if not product:
    return {
      "success": False,
      "message": f"Barcode {barcode_data} product not found!"
    }

  result = update_stock(product["id"], quantity, operation)
  return result

# Test
if __name__ == "__main__":
  print("=== Barcode Scanner Test ===")
  print("1. Scan with camera")
  print("2. Scan from image")

  choice = input("Choice (1/2): ").strip()

  if choice == "1":
    result = scan_barcode_from_camera()
    print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")

  elif choice == "2":
    path = input("Enter image path: ").strip()
    result = scan_barcode_from_image(path)
    print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")