from __future__ import annotations

import re
from typing import Iterable

from trustforge.common.theme import ThemeTokens
from trustforge.models import PolicyMeta

_LATEX_ESC = [
    ("\\", r"\textbackslash{}"),
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


def _escape_latex(s: str) -> str:
    out = s
    for a, b in _LATEX_ESC:
        out = out.replace(a, b)
    # en dash / em dash
    out = out.replace("–", "--").replace("—", "---")
    return out


def _lines(md: str) -> Iterable[str]:
    for ln in md.splitlines():
        yield ln.rstrip("\n")


def md_to_latex_body(body_md: str, *, tokens: ThemeTokens, meta: PolicyMeta) -> str:
    """
    Minimal md -> LaTeX transformer good enough for headings & paragraphs.
    This is intentionally simple; we can enrich later (lists, code, tables).
    """
    out: list[str] = []

    # Title page (already in template header), just ensure first page break handled by template.

    # Headings & paragraphs
    para_buf: list[str] = []

    def flush_para() -> None:
        if not para_buf:
            return
        out.append(_escape_latex(" ".join(para_buf)))
        out.append("")  # blank line between paragraphs
        para_buf.clear()

    for raw in _lines(body_md):
        line = raw.strip()
        if not line:
            flush_para()
            continue

        # ATX headings
        if line.startswith("### "):
            flush_para()
            out.append(r"\subsubsection{" + _escape_latex(line[4:].strip()) + "}")
            out.append("")
            continue
        if line.startswith("## "):
            flush_para()
            out.append(r"\subsection{" + _escape_latex(line[3:].strip()) + "}")
            out.append("")
            continue
        if line.startswith("# "):
            flush_para()
            out.append(r"\section{" + _escape_latex(line[2:].strip()) + "}")
            out.append("")
            continue

        # Ignore explicit heading IDs like `{#id}` at line end
        line = re.sub(r"\s*\{#[-a-zA-Z0-9_]+\}\s*$", "", line)

        # Simple bullets -> itemize (best-effort)
        if line.startswith(("- ", "* ")):
            flush_para()
            # collect contiguous bullet block
            items: list[str] = [line[2:].strip()]
            out.append(r"\begin{itemize}")
            out.append(r"\item " + _escape_latex(items[0]))
            continue  # next lines will not be joined; keep simple

        # Accumulate paragraph
        para_buf.append(line)

    flush_para()

    # Make sure toc can pick up headings with \section etc.
    # Template already includes \tableofcontents and the hyperref/bookmarks setup.

    return "\n".join(out).strip() + "\n"
