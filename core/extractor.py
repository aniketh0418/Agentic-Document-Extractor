import streamlit as st
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rapidfuzz import fuzz, process
from openai import OpenAI

# --- Load env ---
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENAI_MODEL = st.secrets.get("OPENROUTER_MODEL", "openai/gpt-oss-120b")  # default model via OpenRouter

if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ Missing OPENROUTER_API_KEY in .env")

# --- Configure OpenRouter client ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Data Models ---
class FieldItem(BaseModel):
    name: str
    value: str | float | int | None = None
    confidence: float = 0.0
    source: dict = Field(default_factory=dict)

class ExtractionResult(BaseModel):
    doc_type: str
    fields: List[FieldItem]
    overall_confidence: float = 0.0
    qa: Dict[str, Any] = Field(default_factory=dict)

# --- Extract JSON safely ---
def extract_json_from_text(text: str):
    try:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("⚠️ JSON parsing error:", e)
    return {"fields": []}

# --- Prompt Builder ---
def _make_instructions(doc_type: str, expected_fields: Optional[list[str]]):
    expect = (
        "If provided, only extract these fields (map synonyms, keep names EXACT): "
        + ", ".join(expected_fields)
        if expected_fields
        else "Extract the most relevant fields for this document type."
    )
    target_names = expected_fields or ["InvoiceNumber", "Date", "TotalAmount"]
    return f"""
You are a precise information extraction engine for {doc_type} documents.
{expect}

Rules:
- Output ONLY valid JSON with this shape: {{"fields":[{{"name": "...","value": "...", "confidence": 0-1, "source": {{"page": 1, "bbox": null}}}}]]}}
- Use exact field names: {target_names}
- If a field is missing, include it with value=null and confidence<=0.3.
- Do not include any text outside JSON.

Example output:
{{
  "fields": [
    {{"name":"InvoiceNumber","value":"12345","confidence":0.95,"source":{{"page":1,"bbox":null}}}},
    {{"name":"Date","value":"01/02/2024","confidence":0.93,"source":{{"page":1,"bbox":null}}}},
    {{"name":"TotalAmount","value":"€500","confidence":0.92,"source":{{"page":1,"bbox":null}}}}
  ]
}}
""".strip()

def _build_user_message(instructions: str, plain_text: str) -> str:
    if len(plain_text) > 30000:
        plain_text = plain_text[:30000]
    return instructions + "\n\nDocument text:\n\n" + plain_text

# --- Call OpenRouter/OpenAI ---
def _call_openai(single_user_message: str, model: str = OPENAI_MODEL) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a strict JSON information extractor."},
            {"role": "user", "content": single_user_message},
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    text_output = response.choices[0].message.content
    return text_output

# --- Fuzzy normalize field names ---
def _normalize_fields(fields, expected_fields):
    if not expected_fields:
        return fields
    normalized = []
    for f in fields:
        name = f.get("name")
        if not name:
            continue
        match, score = process.extractOne(name, expected_fields, scorer=fuzz.partial_ratio)
        if score and score > 70:
            f["name"] = match
        normalized.append(f)
    return normalized

# --- Main extraction ---
def extract_fields_structured(
    doc_type: str, pages: list[dict], plain_text: str, expected_fields: Optional[list[str]] = None
) -> dict:
    instructions = _make_instructions(doc_type, expected_fields)
    user_msg = _build_user_message(instructions, plain_text)

    raw = _call_openai(user_msg, model=OPENAI_MODEL)
    data = extract_json_from_text(raw) or {}
    fields = data.get("fields", [])

    fields = _normalize_fields(fields, expected_fields)

    # Map source text to page numbers if available
    for f in fields:
        if isinstance(f, dict) and f.get("value"):
            val_str = str(f["value"]).strip()
            for p in pages:
                if val_str and val_str in (p.get("text") or ""):
                    f["source"] = {"page": p["page_no"], "bbox": None}
                    break

    return {
        "doc_type": doc_type,
        "fields": fields,
        "overall_confidence": 0.0,
        "qa": {"passed_rules": [], "failed_rules": [], "notes": ""},
    }
