import cv2
import os
import json
from dotenv import load_dotenv
from PIL import Image
import pytesseract
from openai import OpenAI
from openpyxl import Workbook

# Load environment variables from .env
load_dotenv()

# Debug checks
print("API:", os.getenv("OPENROUTER_API_KEY"))
print("BASE:", os.getenv("OPENROUTER_BASE_URL"))
print("MODEL:", os.getenv("OPENROUTER_MODEL"))

# Read environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
MODEL_NAME = os.getenv("OPENROUTER_MODEL")

# Safety validation
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing. Check your .env file.")

if not OPENROUTER_BASE_URL:
    raise ValueError("OPENROUTER_BASE_URL is missing. Check your .env file.")

if not MODEL_NAME:
    raise ValueError("OPENROUTER_MODEL is missing. Check your .env file.")

# Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Create OpenRouter client
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def extract_text_from_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # OCR pass 1: original image
    original_text = pytesseract.image_to_string(Image.open(image_path))

    # OCR pass 2: enhanced image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    scale_percent = 200
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    denoised = cv2.fastNlMeansDenoising(resized, None, 30, 7, 21)
    enhanced = cv2.equalizeHist(denoised)

    threshold = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    cv2.imwrite("outputs/enhanced_ocr_image.png", threshold)

    custom_config = r"--oem 3 --psm 6"
    enhanced_text = pytesseract.image_to_string(threshold, config=custom_config)

    combined_text = f"""
OCR PASS 1 - ORIGINAL IMAGE:
{original_text}

OCR PASS 2 - ENHANCED IMAGE:
{enhanced_text}
"""

    return combined_text


def extract_structured_data(raw_text):
    prompt = f"""
You are an AI logistics container label extraction assistant.

This image is a logistics shipment/container label, not an item load plan.

Extract operational shipment information from the OCR text.

Return ONLY valid JSON.
Do not include markdown.
Do not include ```json.
Do not include explanation.

IMPORTANT BUSINESS RULES:
- Yellow main label means equipment_type = "FLAT RACK".
- GEMCO is the customer.
- GROOTE EYLANDT is the destination.
- VIA DARWIN is the route.
- Shipment number starts with CEN, for example CEN182026.
- Shipment dates may appear in format like 24/04 - 30/04.
- Container number may look like TIHU7000087#1.
- Quantity may appear as "1 item", but it is not a main business field.
- Do not put customer name under description.
- Do not use the field name "description" for this document type.
- If OCR text is unclear but the business rule is obvious from the label, infer cautiously and mark confidence as needs_review.
- If a value is not visible or not available, return an empty string.

Required JSON format:
{{
  "document_type": "container_label",
  "equipment_type": "",
  "shipment_number": "",
  "shipment_dates": "",
  "container_number": "",
  "customer": "",
  "destination": "",
  "route": "",
  "quantity": "",
  "confidence": "clear / unclear / needs_review",
  "notes": ""
}}

OCR TEXT:
{raw_text}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You extract logistics container label data into clean valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    # Extra safety if AI returns markdown-style JSON
    result = result.replace("```json", "").replace("```", "").strip()

    return json.loads(result)


def export_to_excel(data, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Container Label"

    headers = [
        "Document Type",
        "Equipment Type",
        "Shipment Number",
        "Shipment Dates",
        "Container Number",
        "Customer",
        "Destination",
        "Route",
        "Quantity",
        "Confidence",
        "Notes"
    ]

    ws.append(headers)

    ws.append([
        data.get("document_type", ""),
        data.get("equipment_type", ""),
        data.get("shipment_number", ""),
        data.get("shipment_dates", ""),
        data.get("container_number", ""),
        data.get("customer", ""),
        data.get("destination", ""),
        data.get("route", ""),
        data.get("quantity", ""),
        data.get("confidence", ""),
        data.get("notes", "")
    ])

    wb.save(output_path)


def main():
    image_path = "input_images/sample_load_plan.jpeg"
    output_excel = "outputs/container_label_output.xlsx"
    output_json = "outputs/container_label_output.json"

    print("Extracting OCR text...")
    raw_text = extract_text_from_image(image_path)

    print("\n===== OCR TEXT =====\n")
    print(raw_text)

    print("\nSending text to AI...")
    structured_data = extract_structured_data(raw_text)

    print("\n===== STRUCTURED JSON =====\n")
    print(json.dumps(structured_data, indent=4))

    print("\nSaving JSON...")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=4)

    print("Exporting Excel...")
    export_to_excel(structured_data, output_excel)

    print("\nDone.")
    print(f"Excel saved: {output_excel}")
    print(f"JSON saved: {output_json}")


if __name__ == "__main__":
    main()