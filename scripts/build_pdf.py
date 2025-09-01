#!/usr/bin/env python3
import os, sys, subprocess, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "policies"
OUT_DIR = ROOT / "out" / "pdf"
TEMPLATE_DIR = ROOT / "templates" / "pandoc"
EIS_TEMPLATE = TEMPLATE_DIR / "eisvogel.latex"
META_FILE = TEMPLATE_DIR / "metadata.yaml"
BRAND_FILE = ROOT / "brand" / "config.yml"

def sh(cmd, cwd=None):
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)

def load_brand():
    with open(BRAND_FILE, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    from datetime import datetime
    year = str(datetime.utcnow().year)
    cfg["footer_text"] = cfg.get("footer_text","").replace("{{year}}", year)
    return cfg

def render_one(md_path: pathlib.Path, brand: dict):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = md_path.stem
    pdf_path = OUT_DIR / f"{slug}.pdf"

    if not EIS_TEMPLATE.exists():
        print(f"ERROR: Missing template {EIS_TEMPLATE}. Run `make template` and retry.", file=sys.stderr)
        sys.exit(2)

    args = [
        "pandoc",
        str(md_path),
        "--from", "markdown+yaml_metadata_block",
        "--template", str(EIS_TEMPLATE),
        "--metadata-file", str(META_FILE),
        "--pdf-engine", brand.get("pdf_engine", "xelatex"),
        "-V", f"titlepage=true",
        "-V", f"colorlinks=true",
        "-V", f"maincolor={brand.get('primary_color','#1A73E8')}",
        "-V", f"accentcolor={brand.get('accent_color','#0B57D0')}",
        "-V", f"header-left={brand.get('org_name','')}",
        "-V", f"footer-left={brand.get('footer_text','')}",
        "-V", f"logo={brand.get('logo','')}",
        "-V", f"papersize={brand.get('paper_size','a4')}",
        "-V", f"toc={'true' if brand.get('include_toc',True) else 'false'}",
        "-V", f"numbersections={'true' if brand.get('number_sections',True) else 'false'}",
        "-o", str(pdf_path),
    ]
    sh(args)
    print(f"✔ Wrote {pdf_path}")

def main():
    if not POLICY_DIR.exists():
        print("ERROR: policies/ directory not found.", file=sys.stderr)
        sys.exit(1)
    if not META_FILE.exists():
        print(f"ERROR: Missing metadata file {META_FILE}.", file=sys.stderr)
        sys.exit(1)
    if not BRAND_FILE.exists():
        print(f"ERROR: Missing brand config {BRAND_FILE}.", file=sys.stderr)
        sys.exit(1)

    brand = load_brand()
    md_files = sorted(POLICY_DIR.glob("*.md"))
    if not md_files:
        print("No policy markdown files found in policies/. Add one and re-run.", file=sys.stderr)
        sys.exit(1)
    for md in md_files:
        render_one(md, brand)

if __name__ == "__main__":
    main()
