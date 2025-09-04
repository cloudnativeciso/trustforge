# Trustforge

**Trustforge** is a lightweight **Policy Foundry** for generating professional security documentation artifacts from Markdown sources.
It supports export to **HTML**, **PDF (XeLaTeX)**, and **CSV indexes**, with theming aligned to Cloud Native CISO branding.

---

## ✨ Features

- Write policies once in **Markdown with YAML frontmatter**.
- Export polished artifacts:
  - **PDF** with professional cover page, table of contents, fonts, and branding.
  - **HTML** with theme-aligned typography and colors.
  - **CSV Index** of policies for tracking metadata across your repository.
- **Custom theming system** (YAML-based) for brand colors, fonts, and layout tokens.
- **NIST CSF 2.0 Control Map**: Generate CSV/HTML crosswalks of controls for readiness assessments.
- **Risk Register**: Define risks in YAML/Markdown and export to CSV or PDF with scoring models.
- **Pre-commit hooks** with Ruff + Mypy ensure style and type safety.
- Simple **Makefile workflows** for install, lint, test, and build.

---

## 📦 Installation

Trustforge requires Python 3.13+ and [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone https://github.com/cloudnativeciso/trustforge.git
cd trustforge

# Install dependencies into a virtual environment
make install
```

Additional dependencies:
- **XeLaTeX** (via TeX Live) for PDF generation.
- System fonts (Inter, DM Sans, Satoshi, Fira Code) or included in `assets/fonts/`.

---

## 🛠 Usage

### Generate PDF

```bash
trustforge pdf  examples/policies/information-security-policy.md
```

Produces a themed PDF at `out/<policy>.pdf`.

### Generate HTML

```bash
trustforge html examples/policies/information-security-policy.md
```

Produces a themed HTML file at `out/<policy>.html`.

### Generate CSV Index

```bash
trustforge index --out out/policies.csv
```

Builds `out/policies.csv` with metadata from all Markdown policies.

### Control Map (NIST CSF 2.0)

```bash
trustforge control-map nist-csf20 --out out/control_map.csv
```

Outputs a CSV with columns:
`framework,function,category,control_id,title,description`.

### Risk Register

From YAML to CSV:

```bash
trustforge risk-export examples/risks.yaml --out out/risks.csv
```

CSV columns:
`id,title,description,severity,likelihood,owner,status,treatment,target_date,control_refs`.

`control_refs` are `;`-joined control IDs (e.g., `PR.AC-01;DE.AE-01`).

---

## 🧩 Project Structure

```
trustforge/
├── policies/                # Source Markdown policies
├── src/trustforge/          # Python package
│   ├── cli.py               # Typer CLI entrypoints
│   ├── common/              # Markdown + YAML parsing
│   └── pipeline/            # Renderers (HTML, PDF, CSV)
├── templates/latex/         # XeLaTeX templates
├── themes/                  # Theming tokens (YAML)
├── assets/                  # Logo + fonts
└── out/                     # Build output (PDF, HTML, CSV)
```

---

## 🔍 Development

Lint, type-check, and test before commits:

```bash
make lint
make test
```

Pre-commit hooks are enabled to run Ruff + Mypy + formatting automatically:

```bash
uv run pre-commit run --all-files
```

---

## 🚀 Roadmap

- Hardened PDF theming (cover pages, side bookmarks, watermarks).
- NIST CSF 2.0 control map and gap analysis.
- Risk register builder (Pydantic models + scoring).
- Optional Notion and GitHub Actions integrations.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and open a PR.

---

## 📜 License

This project is licensed under the MIT License.
