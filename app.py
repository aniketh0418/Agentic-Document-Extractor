import streamlit as st
import os
import json
import tempfile
from pipeline import run_pipeline

st.set_page_config(page_title="Document Extraction", layout="wide")

st.title("🤖 Agentic Document Extractor")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a document (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

# --- Sidebar options ---
st.sidebar.header("⚙️ Options")
doc_type_hint = st.sidebar.selectbox("Document Type Hint", ["", "invoice", "medical_bill", "prescription"])
expected_fields = st.sidebar.text_input("Expected Fields (comma separated)", "")

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info(f"Processing file: **{uploaded_file.name}**")

    # Run pipeline
    if st.button("🔍 Run Extraction"):
        exp_fields = [f.strip() for f in expected_fields.split(",") if f.strip()] or None
        result = run_pipeline(input_path=tmp_path, expected_fields=exp_fields, doc_type_hint=doc_type_hint or None)

        # Show document type + confidence
        st.subheader("📌 Document Info")
        st.write(f"**Detected Type:** {result['doc_type']}")
        st.write(f"**Overall Confidence:** {result['overall_confidence']}")

        # Show extracted fields
        st.subheader("📋 Extracted Fields")
        fields = result.get("fields", [])
        if fields:
            st.table([{ "Name": f["name"], "Value": f["value"], "Confidence": f["confidence"] } for f in fields])
        else:
            st.warning("No fields extracted.")

        # Show QA rules
        st.subheader("✅ Validation & QA")
        st.json(result.get("qa", {}))

        # Download JSON
        st.subheader("📥 Download")
        st.download_button("Download JSON", json.dumps(result, indent=2, ensure_ascii=False), file_name="extraction.json", mime="application/json")