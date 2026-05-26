import cv2
import zxingcpp
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.stock import get_product_by_barcode, update_stock

def scan_barcode_from_camera():
    """
    Camera se barcode scan karo
    'q' dabao band karne ke liye
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {"success": False, "message": "Camera nahi mila!"}

    print("\n📷 Camera chalu ho gaya!")
    print("   Barcode camera ke saamne rakho — auto detect hoga")
    print("   'q' dabao band karne ke liye")

    scanned_product = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Barcode detect karo
        results = zxingcpp.read_barcodes(frame)

        for result in results:
            barcode_data = result.text

            # Green box draw karo barcode ke around
            pos = result.position
            pts = [
                (pos.top_left.x, pos.top_left.y),
                (pos.top_right.x, pos.top_right.y),
                (pos.bottom_right.x, pos.bottom_right.y),
                (pos.bottom_left.x, pos.bottom_left.y)
            ]
            for i in range(4):
                cv2.line(frame, pts[i], pts[(i+1) % 4], (0, 255, 0), 2)

            # Barcode data dikhao
            cv2.putText(
                frame, barcode_data,
                (pos.top_left.x, pos.top_left.y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 255, 0), 2
            )

            # Product dhundo
            product = get_product_by_barcode(barcode_data)

            if product:
                cv2.putText(
                    frame,
                    f"✓ {product['name']} | Rs.{product['selling_price']}",
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
                    "message": "Product database mein nahi hai!"
                }

            # Auto return kar do jab barcode mile
            cap.release()
            cv2.destroyAllWindows()
            return scanned_product

        # Frame dikhao
        cv2.imshow("Barcode Scanner — 'q' band karne ke liye", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"success": False, "message": "Scan cancel kiya"}

def scan_barcode_from_image(image_path):
    """
    Image se barcode scan karo
    """
    image = cv2.imread(image_path)

    if image is None:
        return {"success": False, "message": "Image nahi mili!"}

    results = zxingcpp.read_barcodes(image)

    if not results:
        return {"success": False, "message": "Koi barcode nahi mila image mein!"}

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
    Barcode se item dhundo aur stock update karo
    operation = subtract — sale hui
    operation = add — naya stock aaya
    """
    product = get_product_by_barcode(barcode_data)

    if not product:
        return {
            "success": False,
            "message": f"Barcode {barcode_data} ka product nahi mila!"
        }

    result = update_stock(product["id"], quantity, operation)
    return result

# Test karo
if __name__ == "__main__":
    print("=== Barcode Scanner Test ===")
    print("1. Camera se scan")
    print("2. Image se scan")

    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        result = scan_barcode_from_camera()
        print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")

    elif choice == "2":
        path = input("Image path daalo: ").strip()
        result = scan_barcode_from_image(path)
        print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")