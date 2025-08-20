DOC_TYPES = ["invoice", "medical_bill", "prescription"]

def detect_doc_type(text: str) -> str:
    t = text.lower()
    # Heuristic keyword routing
    if any(k in t for k in ["invoice #", "invoice no", "subtotal", "balance due", "gst", "igst", "cgst", "sgst"]):
        return "invoice"
    if any(k in t for k in ["discharge", "medical bill", "hospital", "procedure", "consultation fee"]):
        return "medical_bill"
    if any(k in t for k in ["rx", "prescription", "dosage", "refill", "doctor", "patient name"]):
        return "prescription"
    # fallback
    return "invoice"
