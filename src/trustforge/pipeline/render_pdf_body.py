# src/trustforge/pipeline/render_pdf_body.py
from __future__ import annotations

import re
from typing import Iterable

from trustforge.common.theme import ThemeTokens
from trustforge.models import PolicyMeta

# ---------------------------------------------------------------------------
# Minimal Markdown → LaTeX body converter (dependency-free)
#
# Features:
# - Headings (#, ##, ###) → \section / \subsection / \subsubsection (+ \label)
# - Paragraphs with tiny inline formatting (bold/italic/inline-code)
# - Inline links: [text](url) and autolinks <https://…>
# - Unordered lists ("- ", "* ") → itemize
# - Ordered lists ("1. ", "2. ") → enumerate
# - Fenced code blocks (```lang ... ```) → small italic caption + verbatim
# - Block quotes ("> …") → quote
# - Simple pipe tables (GitHub-style) → tabular with L/C/R alignment
# - Horizontal rule: a line with only --- → a thin rule
#
# Design goals:
# - Keep XeLaTeX dependency-free (no minted/listings)
# - Escape LaTeX special chars consistently (except inside verbatim)
# - Small, readable, and mypy/ruff clean
# ---------------------------------------------------------------------------

# Order matters: escape backslash first.
_LATEX_ESC: list[tuple[str, str]] = [
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

# Remove trailing pandoc-style heading IDs: `{#id}`
_HEADING_ID_RE = re.compile(r"\s*\{#[A-Za-z0-9_-]+\}\s*$")

# Very small inline markup (process code first to avoid nested style)
_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^\*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^\*]+)\*(?!\*)")  # avoid matching bold pairs

# Inline links: [text](url)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")

# Fenced code blocks
_FENCE_START_RE = re.compile(r"^```([A-Za-z0-9+_.-]*)\s*$")
_FENCE_END_RE = re.compile(r"^```\s*$")

# Ordered list items: "1. something" (leading spaces allowed)
_OL_ITEM_RE = re.compile(r"^\s*\d+\.\s+(.*)$")

# Pipe-table detection
# - header row and/or data rows like: | a | b | c |
# - separator row like: | --- | :---: | ---: |
_PIPE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_SEP_CELL_RE = re.compile(r"^\s*:?-{3,}:?\s*$")  # ---, :---, ---:, :---:

# Blockquote
_BLOCKQUOTE_RE = re.compile(r"^\s*>\s?(.*)$")

# Horizontal rule (line containing only ---)
_HR_RE = re.compile(r"^\s*-{3,}\s*$")


def _escape_latex(s: str) -> str:
    """Escape LaTeX special characters and convert en/em dashes."""
    out = s
    for a, b in _LATEX_ESC:
        out = out.replace(a, b)
    # en dash / em dash → LaTeX style
    out = out.replace("–", "--").replace("—", "---")
    return out


def _escape_link_text(s: str) -> str:
    """Escape link text (regular LaTeX rules)."""
    return _escape_latex(s)


def _slugify(text: str) -> str:
    """
    Very small slugifier suitable for \label{...}:
    - lowercase
    - keep alnum, replace other runs with '-'
    - trim leading/trailing '-'
    """
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "section"


def _inline_md_to_tex(s: str) -> str:
    # Autolinks first
    def autolink_sub(m: re.Match[str]) -> str:
        url = m.group(1)
        # hyperref provides \url
        return r"\url{" + url + "}"

    s = _AUTOLINK_RE.sub(autolink_sub, s)

    # Links: [text](url) → \href{url}{text}
    def link_sub(m: re.Match[str]) -> str:
        text = _escape_latex(m.group(1))
        url = _escape_latex(m.group(2))
        return r"\href{" + url + "}{" + text + "}"

    s = _LINK_RE.sub(link_sub, s)

    # Code spans next, escape inside \texttt{}
    def code_sub(m: re.Match[str]) -> str:
        inner = _escape_latex(m.group(1))
        return r"\texttt{" + inner + "}"

    s = _CODE_RE.sub(code_sub, s)

    # Bold then italic (escape inside)
    def bold_sub(m: re.Match[str]) -> str:
        return r"\textbf{" + _escape_latex(m.group(1)) + "}"

    def italic_sub(m: re.Match[str]) -> str:
        return r"\emph{" + _escape_latex(m.group(1)) + "}"

    s = _BOLD_RE.sub(bold_sub, s)
    s = _ITALIC_RE.sub(italic_sub, s)

    # Escape the rest
    return _escape_latex(s)


def _lines(md: str) -> Iterable[str]:
    for ln in md.splitlines():
        yield ln.rstrip("\n")


# ---------------------------- Table helpers ---------------------------------


def _split_pipe_row(row: str) -> list[str]:
    """
    Split a pipe table row into cells. Leading/trailing pipes are optional.
    Example: "| a | b |" → ["a", "b"]
    """
    # Remove leading/trailing pipe, then split
    row_stripped = row.strip()
    if row_stripped.startswith("|"):
        row_stripped = row_stripped[1:]
    if row_stripped.endswith("|"):
        row_stripped = row_stripped[:-1]
    parts = [c.strip() for c in row_stripped.split("|")]
    return parts


def _is_pipe_table_line(line: str) -> bool:
    return bool(_PIPE_ROW_RE.match(line))


def _is_separator_row(cells: list[str]) -> bool:
    # All cells must match --- / :--- / ---: / :---:
    if not cells:
        return False
    return all(bool(_SEP_CELL_RE.match(c)) for c in cells)


def _align_from_sep_cell(cell: str) -> str:
    """
    Return LaTeX alignment char ('l', 'c', 'r') based on a separator cell.
      :---   → left
      :---:  → center
      ---:   → right
      ---    → left (default)
    """
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return "c"
    if right:
        return "r"
    return "l"


def _emit_table(rows: list[list[str]], out: list[str]) -> None:
    """
    Emit a LaTeX tabular from parsed pipe-table rows.
    - First row is header (optional if no separator present; we still treat it as body).
    - If the second row is a separator, use it to set column alignment; otherwise default to 'l'.
    """
    if not rows:
        return

    aligns: list[str]
    body_rows: list[list[str]]

    if len(rows) >= 2 and _is_separator_row(rows[1]):
        aligns = [_align_from_sep_cell(c) for c in rows[1]]
        header = rows[0]
        body_rows = rows[2:]
        has_header = True
    else:
        aligns = ["l"] * len(rows[0])
        header = rows[0]
        body_rows = rows[1:]
        has_header = False

    # Ensure all rows have consistent column count
    ncols = len(aligns) if aligns else len(header)
    fmt = "|".join(aligns or ["l"] * ncols)
    out.append(r"\begin{tabular}{" + fmt + "}")
    out.append(r"\hline")

    def emit_row(cells: list[str]) -> None:
        esc = [_inline_md_to_tex(c) for c in cells]
        # Pad/truncate to ncols to avoid LaTeX errors
        if len(esc) < ncols:
            esc = esc + [""] * (ncols - len(esc))
        elif len(esc) > ncols:
            esc = esc[:ncols]
        out.append(" & ".join(esc) + r" \\")
        out.append(r"\hline")

    # Emit header then body
    emit_row(header)
    if has_header:
        pass
    for r in body_rows:
        emit_row(r)

    out.append(r"\end{tabular}")
    out.append("")


# ---------------------------- Main transformer ------------------------------


def md_to_latex_body(body_md: str, *, tokens: ThemeTokens, meta: PolicyMeta) -> str:
    """
    Convert markdown body → LaTeX body string.

    Notes & Limitations:
      - Inline formatting is intentionally minimal (bold/italic/code, links).
      - Code blocks are verbatim (no syntax highlighting, no extra packages).
      - Tables support simple GitHub-style pipe tables with an optional
        alignment row. Advanced tables (row/col spans) are not supported.
      - Nested lists and nested block quotes are not supported.
    """
    out: list[str] = []

    # State
    para_buf: list[str] = []

    in_ul = False
    in_ol = False

    in_code = False
    code_buf: list[str] = []
    code_lang: str | None = None

    in_quote = False

    table_buf: list[list[str]] = []  # rows of cells for a pending table

    # ---------- state helpers ----------

    def flush_para() -> None:
        nonlocal para_buf
        if not para_buf:
            return
        out.append(_inline_md_to_tex(" ".join(para_buf)))
        out.append("")
        para_buf = []

    def open_ul() -> None:
        nonlocal in_ul, in_ol
        if in_ol:
            close_ol()
        if not in_ul:
            out.append(r"\begin{itemize}")
            in_ul = True

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append(r"\end{itemize}")
            out.append("")
            in_ul = False

    def open_ol() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            close_ul()
        if not in_ol:
            out.append(r"\begin{enumerate}")
            in_ol = True

    def close_ol() -> None:
        nonlocal in_ol
        if in_ol:
            out.append(r"\end{enumerate}")
            out.append("")
            in_ol = False

    def open_code(lang: str | None) -> None:
        nonlocal in_code, code_lang, code_buf
        flush_para()
        close_ul()
        close_ol()
        close_quote()
        flush_table()
        in_code = True
        code_lang = lang or None
        code_buf = []

    def close_code() -> None:
        nonlocal in_code, code_buf, code_lang
        if not in_code:
            return
        if code_lang:
            # Small, tasteful caption above code
            out.append(r"\textit{" + _escape_latex(code_lang) + r"}")
        out.append(r"\begin{verbatim}")
        out.extend(code_buf)  # raw content; verbatim handles special chars
        out.append(r"\end{verbatim}")
        out.append("")
        in_code = False
        code_lang = None
        code_buf = []

    def open_quote() -> None:
        nonlocal in_quote
        flush_para()
        close_ul()
        close_ol()
        flush_table()
        if not in_quote:
            out.append(r"\begin{quote}")
            in_quote = True

    def close_quote() -> None:
        nonlocal in_quote
        if in_quote:
            out.append(r"\end{quote}")
            out.append("")
            in_quote = False

    def flush_table() -> None:
        nonlocal table_buf
        if table_buf:
            _emit_table(table_buf, out)
            table_buf = []

    # ---------- main loop ----------

    for raw in _lines(body_md):
        # Inside code fence: only look for end fence
        if in_code:
            if _FENCE_END_RE.match(raw):
                close_code()
                continue
            code_buf.append(raw)
            continue

        # Fence start?
        m_fence = _FENCE_START_RE.match(raw.strip())
        if m_fence:
            open_code(m_fence.group(1) or None)
            continue

        # Block quote?
        m_quote = _BLOCKQUOTE_RE.match(raw)
        if m_quote:
            open_quote()
            # process the quoted text with inline formatting, but keep line breaks
            text = m_quote.group(1).strip()
            out.append(_inline_md_to_tex(text))
            continue
        else:
            # If we were in quote and hit a non-quote line, close it.
            close_quote()

        line = raw.strip()

        # Horizontal rule
        if _HR_RE.match(line):
            flush_para()
            close_ul()
            close_ol()
            flush_table()
            out.append(r"\noindent\hrulefill")
            out.append("")
            continue

        # Blank line → paragraph/table separation
        if not line:
            flush_para()
            close_ul()
            close_ol()
            flush_table()
            # quotes already handled above
            continue

        # Headings
        if line.startswith("# "):
            flush_para()
            close_ul()
            close_ol()
            close_quote()
            flush_table()
            text = _HEADING_ID_RE.sub("", line[2:].strip())
            lab = _slugify(text)
            out.append(r"\section{" + _inline_md_to_tex(text) + r"}\label{sec:" + lab + r"}")
            out.append("")
            continue
        if line.startswith("## "):
            flush_para()
            close_ul()
            close_ol()
            close_quote()
            flush_table()
            text = _HEADING_ID_RE.sub("", line[3:].strip())
            lab = _slugify(text)
            out.append(r"\subsection{" + _inline_md_to_tex(text) + r"}\label{subsec:" + lab + r"}")
            out.append("")
            continue
        if line.startswith("### "):
            flush_para()
            close_ul()
            close_ol()
            close_quote()
            flush_table()
            text = _HEADING_ID_RE.sub("", line[4:].strip())
            lab = _slugify(text)
            out.append(
                r"\subsubsection{" + _inline_md_to_tex(text) + r"}\label{subsubsec:" + lab + r"}"
            )
            out.append("")
            continue

        # Pipe table row?
        if _is_pipe_table_line(line):
            # Start/continue capturing a table. We won't emit paragraphs/lists while capturing.
            cells = _split_pipe_row(line)
            if cells:
                table_buf.append(cells)
            continue
        else:
            # If we were capturing a table and hit a non-table line, emit the table.
            flush_table()

        # Unordered list?
        if line.startswith("- ") or line.startswith("* "):
            flush_para()
            open_ul()
            item_text = line[2:].strip()
            out.append(r"\item " + _inline_md_to_tex(item_text))
            continue

        # Ordered list?
        m_ol = _OL_ITEM_RE.match(line)
        if m_ol:
            flush_para()
            open_ol()
            out.append(r"\item " + _inline_md_to_tex(m_ol.group(1).strip()))
            continue

        # Remove trailing {#id} if present on a normal line
        line = _HEADING_ID_RE.sub("", line)

        # Accumulate in paragraph
        para_buf.append(line)

    # ---------- finalize ----------
    flush_para()
    close_ul()
    close_ol()
    close_quote()
    flush_table()
    close_code()  # in case of unterminated fence, still emit what we have

    # Template has ToC/hyperref; our sectioning commands feed it.
    return "\n".join(out).strip() + "\n"
