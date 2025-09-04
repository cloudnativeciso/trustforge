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
make pdf
```

Produces a themed PDF at `out/<policy>.pdf`.

### Generate HTML

```bash
make html
```

Produces a themed HTML file at `out/<policy>.html`.

### Generate CSV Index

```bash
make index
```

Builds `out/policies.csv` with metadata from all Markdown policies.

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
