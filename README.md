# 🤖 Agentic Document Extractor

This project is an **intelligent document extraction pipeline** that:
- Accepts **PDFs or images** (invoices, medical bills, prescriptions).
- Runs **OCR** to extract raw text from files.
- Detects document type (`invoice`, `medical_bill`, `prescription`).
- Uses **LLM via OpenRouter** to extract structured fields.
- Validates extracted data (dates, amounts, totals).
- Computes **confidence scores** for fields and overall extraction.
- Provides an interactive **Streamlit UI** to upload documents, view results, and download structured JSON.

---

## 🚀 Features
- Upload PDF/JPG/PNG files.
- Auto-detect or manually select document type.
- Optionally provide **expected fields** (comma-separated).
- Run full extraction pipeline with one click.
- View results:
  - Document type
  - Extracted fields (name, value, confidence)
  - Validation & QA rules
  - Overall confidence score
- Download results as JSON.

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

**Main dependencies:**
- `streamlit`
- `pytesseract`
- `pdf2image`
- `pymupdf`
- `Pillow`
- `rapidfuzz`
- `openai`
- `python-dotenv` (local only)

Make sure you also have:
- **Tesseract OCR** installed:  
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Configure API Key

This project uses **OpenRouter** to access LLMs.

#### Get an API Key
1. Go to [OpenRouter](https://openrouter.ai/).  
2. Create an account (free).  
3. Navigate to **API Keys** in your dashboard.  
4. Generate a new key.  

---

## 🔐 Local Development (with `.env`)

For local runs, create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-oss-120b
```

Run locally:
```bash
streamlit run app.py
```

---


---

## 🖥️ Using the CLI

In addition to the Streamlit UI, you can run the pipeline directly from the command line.

### Run extraction on a file
```bash
python cli.py run path/to/document.pdf
```

### Options
- `--expect` → Comma-separated list of field names to extract  
  Example:
  ```bash
  python cli.py run path/to/invoice.pdf --expect "InvoiceNumber,Date,TotalAmount"
  ```

- `--doc-type` → Optional document type hint (`invoice`, `medical_bill`, `prescription`)  
  Example:
  ```bash
  python cli.py run path/to/bill.png --doc-type medical_bill
  ```

### Output
- Results are printed to the console as formatted JSON.  
- A copy is also saved in the `outputs/` directory as `<filename>.json`.


## 🌐 Deployment on Streamlit Cloud

Streamlit Cloud doesn’t support `.env` files, so you need `.streamlit/secrets.toml`.

### 1. Create `.streamlit/secrets.toml`
Do **not** commit this to GitHub if repo is public.
```toml
OPENROUTER_API_KEY = "your-api-key-here"
OPENROUTER_MODEL = "openai/gpt-oss-120b"
```

### 2. Update Code
Replace `.env` loading with `st.secrets`:

```python
import streamlit as st
from openai import OpenAI

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENAI_MODEL = st.secrets.get("OPENROUTER_MODEL", "openai/gpt-oss-120b")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
```

### 3. Deploy
1. Push your repo to GitHub.  
2. Go to [Streamlit Cloud](https://share.streamlit.io/).  
3. Deploy your repo.  
4. In **App Settings → Secrets**, paste:

```toml
OPENROUTER_API_KEY = "your-api-key-here"
OPENROUTER_MODEL = "openai/gpt-oss-120b"
```

5. Deploy & enjoy 🚀  

---

## 🖥️ Usage
1. Open the app (local or deployed).  
2. Upload a PDF or image of an invoice, bill, or prescription.  
3. (Optional) Enter **expected fields** like `InvoiceNumber, Date, TotalAmount`.  
4. (Optional) Select a **document type hint**.  
5. Click **Run Extraction**.  
6. View extracted structured data.  
7. Download JSON for further use.

---

## 📂 Project Structure
```
core/
 ├── extractor.py   # LLM-based structured field extraction
 ├── ocr.py         # OCR and text extraction
 ├── router.py      # Document type detection
 ├── scorer.py      # Confidence scoring
 └── validator.py   # Field validation rules
pipeline.py         # Orchestration of pipeline steps
cli.py              # CLI for batch runs
app.py              # Streamlit UI
data/               # Sample documents
outputs/            # JSON outputs
```

---

## 🛠️ Example
Upload `sample-invoice.pdf` → Output JSON:
```json
{
  "doc_type": "invoice",
  "fields": [
    {"name": "InvoiceNumber", "value": "INV-1001", "confidence": 0.95},
    {"name": "Date", "value": "2024-08-01", "confidence": 0.93},
    {"name": "TotalAmount", "value": "₹5000", "confidence": 0.92}
  ],
  "overall_confidence": 0.93,
  "qa": {
    "passed_rules": ["date_format:Date", "amount_numeric:TotalAmount", "totals_match"],
    "failed_rules": [],
    "notes": ""
  }
}
```
