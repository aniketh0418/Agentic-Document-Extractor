import os
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import pytesseract
import fitz

def _pdf_to_images(path: str) -> list[Image.Image]:
    try:
        return convert_from_path(path, dpi=300)
    except Exception:
        # try bytes route
        with open(path, "rb") as f:
            b = f.read()
        return convert_from_bytes(b, dpi=300)

def _image_to_text_and_boxes(img: Image.Image) -> tuple[str, list[dict]]:
    # OCR to text and data frame-like dicts
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    text = pytesseract.image_to_string(img)

    # Build boxes
    n = len(data.get("text", []))
    boxes = []
    for i in range(n):
        if data["text"][i].strip():
            boxes.append({
                "text": data["text"][i],
                "conf": float(data["conf"][i]) if data["conf"][i] != "-1" else 0.0,
                "bbox": [int(data["left"][i]), int(data["top"][i]), int(data["left"][i])+int(data["width"][i]), int(data["top"][i])+int(data["height"][i])]
            })
    return text, boxes

def load_and_ocr(path: str) -> tuple[list[dict], str]:
    """Return (pages, plain_text)."""

    ext = os.path.splitext(path)[1].lower()
    pages: list[dict] = []

    plain_text = ""

    if ext == ".pdf":
        # Try direct text extraction
        doc = fitz.open(path)
        text_blocks = []
        for i, page in enumerate(doc, start=1):
            txt = page.get_text("text")
            text_blocks.append(txt)
            pages.append({"page_no": i, "text": txt, "boxes": []})
        plain_text = "\n\n".join(text_blocks)

        # If nothing extracted, fallback to OCR
        if not plain_text.strip():
            images = _pdf_to_images(path)
            for i, img in enumerate(images, start=1):
                t, boxes = _image_to_text_and_boxes(img)
                pages.append({"page_no": i, "text": t, "boxes": boxes})
                plain_text += "\n\n" + t

    else:
        # Non-PDF (image file)
        img = Image.open(path).convert("RGB")
        t, boxes = _image_to_text_and_boxes(img)
        pages.append({"page_no": 1, "text": t, "boxes": boxes})
        plain_text = t

    return pages, plain_text