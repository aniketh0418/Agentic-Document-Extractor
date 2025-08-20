from core.router import detect_doc_type
from core.ocr import load_and_ocr
from core.extractor import extract_fields_structured
from core.validator import validate_fields_and_rules
from core.scorer import score_fields_and_overall

def run_pipeline(input_path: str, expected_fields=None, doc_type_hint: str | None = None):
    # 1) OCR / Ingestion
    pages, plain_text = load_and_ocr(input_path)

    # 2) Routing
    doc_type = doc_type_hint or detect_doc_type(plain_text)

    # 3) LLM extraction
    extraction = extract_fields_structured(
        doc_type=doc_type,
        pages=pages,
        plain_text=plain_text,
        expected_fields=expected_fields
    )

    # 4) Validation + QA
    qa = validate_fields_and_rules(extraction, doc_type)

    # 5) Confidence scoring
    scored = score_fields_and_overall(extraction, qa)

    return scored
