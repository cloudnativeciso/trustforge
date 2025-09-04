from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Protocol

from ..common.md import parse_policy_markdown
from ..common.theme import load_theme
from ..models import PolicyMeta


# ---- Minimal typing surface we rely on (no import from common.theme) ----
class _Brand(Protocol):
    logo_path: str | None
    logo_height_mm: int | float


class _Color(Protocol):
    primary: str
    text: str
    muted: str
    border: str
    background: str


class _PDF(Protocol):
    link_color: str
    heading_color: str


class _HTML(Protocol):
    heading_weight: int


class _Layout(Protocol):
    page_margins_mm: int | float


class ThemeTokensProto(Protocol):
    brand: _Brand
    color: _Color
    pdf: _PDF
    html: _HTML
    layout: _Layout


# ------------------------------------------------------------------------

LATEX_TMPL = Path("templates/latex/eisvogel-lite.tex")


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_policy(policy_path: Path) -> tuple[PolicyMeta, str]:
    text = policy_path.read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text)
    return meta, body_md


def _load_tokens(theme_path: str | Path) -> ThemeTokensProto:
    # load_theme returns an object that conforms to ThemeTokensProto
    return load_theme(str(theme_path))  # type: ignore[return-value]


def _copy_logo(tokens: ThemeTokensProto, out_dir: Path) -> Path | None:
    """
    Copy brand logo next to the .tex so LaTeX can always load it (relative path).
    Returns the path to the copied logo or None.
    """
    if not tokens.brand.logo_path:
        return None
    src = Path(tokens.brand.logo_path)
    if not src.exists():
        # Do not fail rendering because of a missing logo; just skip it.
        return None
    dst = out_dir / "logo.png"
    _ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


def _hex_to_rgb_frac(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return (r, g, b)


def _escape_tex(text: str) -> str:
    # Minimal escaping for LaTeX special characters.
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _md_to_latex(md: str) -> str:
    """
    Very small markdown->LaTeX pass for headings, paragraphs, and bullet lists.
    This is intentionally simple and deterministic (no pandoc dependency).
    """
    lines = md.splitlines()
    out: list[str] = []
    in_list = False

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(r"\end{itemize}")
            in_list = False

    for raw in lines:
        line = raw.rstrip()

        # Headings
        if line.startswith("### "):
            flush_list()
            out.append(rf"\subsubsection{{{_escape_tex(line[4:])}}}")
            continue
        if line.startswith("## "):
            flush_list()
            out.append(rf"\subsection{{{_escape_tex(line[3:])}}}")
            continue
        if line.startswith("# "):
            flush_list()
            out.append(rf"\section{{{_escape_tex(line[2:])}}}")
            continue

        # Bullet
        if line.lstrip().startswith(("- ", "* ")):
            if not in_list:
                out.append(r"\begin{itemize}")
                in_list = True
            item_txt = line.lstrip()[2:]
            out.append(rf"\item {_escape_tex(item_txt)}")
            continue

        # Blank line => paragraph break
        if not line.strip():
            flush_list()
            out.append("")  # a blank line in LaTeX paragraph context
            continue

        # Paragraph
        flush_list()
        out.append(_escape_tex(line))

    flush_list()
    return "\n".join(out).strip() + "\n"


def _replace_all(s: str, mapping: Iterable[tuple[str, str]]) -> str:
    for k, v in mapping:
        s = s.replace(k, v)
    return s


def render_pdf(policy_path: Path) -> Path:
    """
    Render a policy Markdown file to themed PDF via XeLaTeX.
    - Reads YAML frontmatter and body markdown.
    - Applies theme tokens (colors, fonts, margins).
    - Injects a branded cover page, ToC, and PDF bookmarks.
    - Compiles with xelatex (twice) to ensure ToC + bookmarks are populated.
    """
    # Inputs
    meta, body_md = _read_policy(policy_path)
    tokens = _load_tokens("themes/cnciso.yaml")  # default; user can swap theme file

    out_dir = _ensure_dir(Path("out"))
    logo_dst = _copy_logo(tokens, out_dir)

    # Prepare color macros from theme
    pr, pg, pb = _hex_to_rgb_frac(tokens.color.primary)
    tr, tg, tb = _hex_to_rgb_frac(tokens.color.text)
    lr, lg, lb = _hex_to_rgb_frac(tokens.pdf.link_color)
    hr, hg, hb = _hex_to_rgb_frac(tokens.pdf.heading_color)

    # Read LaTeX template and assert single BODY token
    latex = LATEX_TMPL.read_text(encoding="utf-8")
    if latex.count("BODY CONTENT START") != 1 or latex.count("BODY CONTENT END") != 1:
        raise RuntimeError("PDF template invariant failed: expected single BODY region.")

    # Convert the body markdown to LaTeX
    body_tex = _md_to_latex(body_md)

    # Build metadata blocks
    title_str = meta.title or "Policy"
    subtitle_str = (getattr(meta, "subtitle", None) or "").strip()
    footer_str = (getattr(meta, "footer", None) or "").strip()

    # Inject simple vars
    replacements: list[tuple[str, str]] = [
        ("PAGE_MARGINS_MM", str(tokens.layout.page_margins_mm)),
        ("LINK_COLOR_HTML", tokens.pdf.link_color.lstrip("#")),
        ("TEXT_COLOR_HTML", tokens.color.text.lstrip("#")),
        ("HEADING_COLOR_HTML", tokens.pdf.heading_color.lstrip("#")),
        ("HEADING_WEIGHT", str(tokens.html.heading_weight)),
        ("TITLE_TEXT", title_str),
        ("SUBTITLE_TEXT", subtitle_str),
        ("FOOTER_TEXT", footer_str),
        ("LOGO_HEIGHT_MM", str(getattr(tokens.brand, "logo_height_mm", 24))),
    ]
    latex = _replace_all(latex, replacements)

    # Inject color definitions (0..1)
    color_block = (
        r"\definecolor{TFPrimary}{rgb}{"
        f"{pr:.4f},{pg:.4f},{pb:.4f}" + "}\n"
        r"\definecolor{TFText}{rgb}{"
        f"{tr:.4f},{tg:.4f},{tb:.4f}" + "}\n"
        r"\definecolor{TFLink}{rgb}{"
        f"{lr:.4f},{lg:.4f},{lb:.4f}" + "}\n"
        r"\definecolor{TFHeading}{rgb}{"
        f"{hr:.4f},{hg:.4f},{hb:.4f}" + "}\n"
    )
    latex = latex.replace("% COLOR_MACROS_HERE", color_block)

    # Optional blocks
    subtitle_block = ""
    if subtitle_str:
        subtitle_block = (
            "{\\vspace{2mm}\\color{TFText}\\Large\\sffamily\\itshape "
            f"{_escape_tex(subtitle_str)}"
            "}\\par\n"
        )
    latex = latex.replace("% SUBTITLE_BLOCK_HERE", subtitle_block)

    footer_block = ""
    if footer_str:
        footer_block = f"{{\\color{{TFText}}\\small {_escape_tex(footer_str)}}}\\par"
    latex = latex.replace("% FOOTER_BLOCK_HERE", footer_block)

    # Logo include
    logo_include = ""
    if logo_dst:
        logo_include = (
            "\\includegraphics[height="
            + f"{getattr(tokens.brand, 'logo_height_mm', 24)}mm"
            + "]{logo.png}"
        )
    latex = latex.replace("% LOGO_INCLUDE_HERE", logo_include)

    # Put the body into the template
    latex = latex.replace("% BODY CONTENT START\n% BODY CONTENT END", body_tex)

    # Write .tex and compile
    tex_path = out_dir / (policy_path.stem + ".tex")
    tex_path.write_text(latex, encoding="utf-8")

    # Run xelatex twice to populate ToC + bookmarks
    for _ in range(2):
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(out_dir),
            check=True,
        )

    pdf_path = out_dir / (policy_path.stem + ".pdf")
    return pdf_path
