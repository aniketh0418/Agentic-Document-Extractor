import re
from typing import Dict, Any, List

DATE_RE = re.compile(r"""\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b""")
AMOUNT_RE = re.compile(r"""\b(?:₹|INR|Rs\.?\s*)?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b""", re.IGNORECASE)

def _coerce_amount(val):
    if val is None:
        return None
    s = str(val)
    s = re.sub(r"[^0-9.]+", "", s)
    try:
        return float(s)
    except ValueError:
        return None

def validate_fields_and_rules(extraction: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    fields = extraction.get("fields", [])
    passed, failed, notes = [], [], []

    # Regex/format validation flags
    for f in fields:
        name = (f.get("name") or "").lower()
        val = f.get("value")

        if "date" in name and val:
            if DATE_RE.search(str(val)):
                passed.append(f"date_format:{f.get('name')}")
            else:
                failed.append(f"date_format:{f.get('name')}")

        if any(k in name for k in ["amount", "total", "subtotal"]):
            amt = _coerce_amount(val)
            if amt is not None:
                passed.append(f"amount_numeric:{f.get('name')}")
            else:
                failed.append(f"amount_numeric:{f.get('name')}")

    # Cross-field rules (example: totals)
    totals = { (f.get("name") or "").lower(): _coerce_amount(f.get("value")) for f in fields }
    total = None
    subtotal = None
    tax = None

    for k, v in totals.items():
        if k in ["total", "totalamount", "grandtotal"]:
            total = v
        if k in ["subtotal", "sub_total"]:
            subtotal = v
        if k in ["tax", "gst", "igst", "sgst", "cgst"]:
            tax = (tax or 0.0) + (v or 0.0)

    if subtotal is not None and total is not None and tax is not None:
        if abs((subtotal + tax) - total) < 0.01:
            passed.append("totals_match")
        else:
            failed.append("totals_match")

    return {"passed_rules": passed, "failed_rules": failed, "notes": "; ".join(notes)}
