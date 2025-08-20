import os
import json
import click
from dotenv import load_dotenv
from pipeline import run_pipeline

@click.group()
def cli():
    pass

@cli.command(help="Run extraction pipeline on a file (PDF/Image).")
@click.argument("path", type=click.Path(exists=True))
@click.option("--expect", default="", help="Comma-separated list of field names to extract (optional).")
@click.option("--doc-type", "doc_type_hint", default="", help="Optional hint: invoice|medical_bill|prescription")
def run(path, expect, doc_type_hint):
    load_dotenv()
    expected_fields = [s.strip() for s in expect.split(",") if s.strip()] or None
    result = run_pipeline(input_path=path, expected_fields=expected_fields, doc_type_hint=doc_type_hint or None)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # write to outputs
    base = os.path.splitext(os.path.basename(path))[0]
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{base}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    cli()
