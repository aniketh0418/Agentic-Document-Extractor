from typing import Dict, Any

def score_fields_and_overall(extraction: Dict[str, Any], qa: Dict[str, Any]) -> Dict[str, Any]:
    fields = extraction.get("fields", [])
    # Start with LLM confidence if present, then adjust with validation
    boosts = 0.05 * len([r for r in qa.get("passed_rules", []) if "date_format" in r or "amount_numeric" in r])
    if "totals_match" in qa.get("passed_rules", []):
        boosts += 0.1

    penalties = 0.05 * len(qa.get("failed_rules", []))

    overall = 0.0
    for f in fields:
        base = float(f.get("confidence") or 0.0)
        adj = max(0.0, min(1.0, base + boosts - penalties))
        f["confidence"] = round(adj, 3)
        overall += adj

    overall = round(overall / max(1, len(fields)), 3)

    return {
        "doc_type": extraction.get("doc_type"),
        "fields": fields,
        "overall_confidence": overall,
        "qa": qa
    }
