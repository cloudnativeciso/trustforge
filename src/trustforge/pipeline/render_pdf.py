from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..common.fs import ensure_dir
from ..common.md import parse_policy_markdown
from ..common.theme import load_theme, tokens_to_latex_vars
from ..config import load_settings

LATEX_TMPL = Path("templates/latex/eisvogel-lite.tex")
BODY_TOKEN = "__POLICY_BODY__"
TOC_HDR_RE = re.compile(r"^\s{0,3}#{1,6}\s+table of contents\s*$", re.I)


def latex_escape(s: str) -> str:
    """Escape LaTeX specials in plain metadata strings (title, owner, etc.)."""
    repl = [
        ("\\", r"\\"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("$", r"\$"),
        ("&", r"\&"),
        ("#", r"\#"),
        ("%", r"\%"),
        ("_", r"\_"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    out = s
    for a, b in repl:
        out = out.replace(a, b)
    return out


def strip_manual_toc(md: str) -> str:
    """Remove a 'Table of Contents' section from Markdown (header + until next header)."""
    lines = md.splitlines()
    out: list[str] = []
    skipping = False
    for ln in lines:
        if not skipping and TOC_HDR_RE.match(ln):
            skipping = True
            continue
        if skipping:
            if re.match(r"^\s{0,3}#{1,6}\s+", ln):
                skipping = False
                out.append(ln)
            # else: keep skipping lines until next header
        else:
            out.append(ln)
    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def uniquify_duplicate_headings(md: str) -> str:
    """If the same heading text appears multiple times, add an id suffix so Pandoc makes unique labels."""
    seen: dict[str, int] = {}
    out: list[str] = []
    hdr_re = re.compile(r"^(\s{0,3})(#{1,6})\s+(.+?)\s*(\{#[-a-z0-9]+\})?\s*$", re.I)

    def slugify(s: str) -> str:
        s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
        s = re.sub(r"[\s_-]+", "-", s)
        return s

    for ln in md.splitlines():
        m = hdr_re.match(ln)
        if not m:
            out.append(ln)
            continue
        indent, hashes, title, existing_id = m.groups()
        if existing_id:
            out.append(ln)
            continue
        base = slugify(title)
        cnt = seen.get(base, 0) + 1
        seen[base] = cnt
        suffix = "" if cnt == 1 else f"-{cnt}"
        out.append(f"{indent}{hashes} {title} {{#{base}{suffix}}}")
    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def clean_aux_for(stem: Path) -> None:
    """Delete LaTeX aux files for a clean, hermetic build."""
    for ext in (".aux", ".toc", ".out", ".lof", ".lot", ".log"):
        p = stem.with_suffix(ext)
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass


def render_pdf(policy_path: Path) -> Path:
    settings = load_settings()
    tokens = load_theme(settings.theme_path)
    text = Path(policy_path).read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text)

    # Sanitize markdown for PDF
    body_md = strip_manual_toc(body_md)
    body_md = uniquify_duplicate_headings(body_md)

    # Load template and check placeholder
    latex = LATEX_TMPL.read_text(encoding="utf-8")
    if latex.count(BODY_TOKEN) != 1:
        raise RuntimeError(
            "PDF template invariant failed: expected a single __POLICY_BODY__ placeholder."
        )

    # Markdown -> LaTeX via pandoc (force numbered sections; top-level is section)
    out_dir = ensure_dir(settings.out_dir)
    stem = out_dir / policy_path.stem
    with tempfile.TemporaryDirectory() as td:
        tmp_md = Path(td) / "body.md"
        tmp_md.write_text(body_md, encoding="utf-8")
        body_tex = subprocess.check_output(
            [
                "pandoc",
                "-f",
                "markdown",
                "-t",
                "latex",
                "--number-sections",
                "--top-level-division=section",
                str(tmp_md),
            ],
            text=True,
        )

    # Safety net: make sure headings are numbered (de-star if needed)
    body_tex = re.sub(r"\\section\*\{", r"\\section{", body_tex)
    body_tex = re.sub(r"\\subsection\*\{", r"\\subsection{", body_tex)

    # Write debug artefact
    (stem.with_suffix(".body.tex")).write_text(body_tex, encoding="utf-8")

    # Apply theme tokens
    for k, v in tokens_to_latex_vars(tokens).items():
        latex = latex.replace(k, v)

    # Handle logo
    logo_dst = out_dir / "logo.png"
    has_logo = False
    if tokens.brand.logo_path:
        logo_src = Path(tokens.brand.logo_path)
        if logo_src.exists():
            try:
                if logo_src.resolve() != logo_dst.resolve():
                    shutil.copyfile(logo_src, logo_dst)
                has_logo = True
            except Exception:
                has_logo = False

    # Blocks & fields
    subtitle_str = getattr(meta, "subtitle", None)
    if subtitle_str:
        subtitle_block = (
            "{\\vspace{2mm}\\color{TFText}\\Large\\sffamily\\itshape "
            + latex_escape(subtitle_str)
            + "}\\par\n"
        )
    else:
        subtitle_block = ""

    footer_str = getattr(meta, "footer", None) or "cloudnativeciso.com"
    footer_block = "{\\color{TFText}\\small " + latex_escape(footer_str) + "}\\par"

    latex = latex.replace("SUBTITLE_BLOCK", subtitle_block)
    latex = latex.replace("FOOTER_BLOCK", footer_block)
    latex = latex.replace("LOGO_PATH", "logo.png" if has_logo else "")

    latex = (
        latex.replace("TITLE", latex_escape(meta.title))
        .replace("VERSION", latex_escape(meta.version))
        .replace("OWNER", latex_escape(meta.owner))
        .replace("LAST_REVIEWED", latex_escape(str(meta.last_reviewed)))
        .replace(BODY_TOKEN, body_tex)
    )

    # Write TeX and build
    tex_path = stem.with_suffix(".tex")
    tex_path.write_text(latex, encoding="utf-8")
    clean_aux_for(stem)
    # Two-pass compile: TOC + bookmarks/refs need the second pass
    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
        cwd=str(out_dir),
        check=True,
    )
    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
        cwd=str(out_dir),
        check=True,
    )
    return stem.with_suffix(".pdf")
