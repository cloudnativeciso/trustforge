from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import copy2

from trustforge.common.errors import (
    AssetNotFoundError,
    LaTeXError,
    MissingDependencyError,
    TemplateError,
)
from trustforge.common.md import parse_policy_markdown
from trustforge.common.theme import ThemeTokens, load_theme
from trustforge.config import Settings
from trustforge.pipeline.render_pdf_body import (
    md_to_latex_body,  # local helper that turns md -> LaTeX body
)

LATEX_TMPL = Path("templates/latex/eisvogel-lite.tex")


def _check_binary(name: str) -> None:
    from shutil import which

    if which(name) is None:
        raise MissingDependencyError(name)


def _inject_minted_preamble(latex: str) -> str:
    """
    Insert a small minted setup block before \\begin{document} if not already present.
    We avoid touching the template file directly.
    """
    if "\\usepackage{minted}" in latex:
        return latex  # already present

    preamble = r"""
% --- Trustforge injected minted setup ---
\usepackage[cache=false]{minted} % requires -shell-escape and pygmentize
\setminted{
  fontsize=\small,
  breaklines=true,
  breakanywhere=true,
  autogobble=true,
  tabsize=2,
}
% ----------------------------------------
""".strip("\n")

    marker = r"\begin{document}"
    idx = latex.find(marker)
    if idx == -1:
        # No begin document? template is malformed.
        raise TemplateError("<inline>", "LaTeX template missing \\begin{document}")
    # Insert just before \begin{document}
    return latex[:idx] + preamble + "\n" + latex[idx:]


def render_pdf(policy_path: Path) -> Path:
    """
    Render a policy Markdown file to themed PDF via XeLaTeX.
    """
    settings = Settings()
    _check_binary("xelatex")

    # Inputs
    text = policy_path.read_text(encoding="utf-8")
    meta, body_md = parse_policy_markdown(text, source=policy_path)
    tokens: ThemeTokens = load_theme(settings.theme_path)

    # Copy logo into out/ so LaTeX can embed it regardless of CWD
    logo_path = Path(tokens.brand.logo_path) if tokens.brand.logo_path else None
    if logo_path:
        if not logo_path.exists():
            raise AssetNotFoundError(logo_path)
        target_logo = Path(settings.out_dir) / "logo.png"
        target_logo.parent.mkdir(parents=True, exist_ok=True)
        copy2(logo_path, target_logo)

    # Read LaTeX template and assert single BODY token
    try:
        latex = LATEX_TMPL.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise TemplateError(LATEX_TMPL, "LaTeX template not found") from e
    if latex.count("BODY") != 1:
        raise TemplateError(LATEX_TMPL, "Expected single BODY placeholder in LaTeX template")

    # md -> latex (body)
    out_dir = Path(settings.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    body_tex = md_to_latex_body(body_md, tokens=tokens, meta=meta)
    latex = latex.replace("BODY", body_tex)

    # Inject minted preamble (only if not already in the template)
    latex = _inject_minted_preamble(latex)

    # Write .tex
    tex_path = out_dir / f"{policy_path.stem}.tex"
    tex_path.write_text(latex, encoding="utf-8")

    # Compile with XeLaTeX (+ shell-escape for minted/pygmentize)
    try:
        subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-shell-escape",
                tex_path.name,
            ],
            cwd=str(out_dir),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        log = out_dir / f"{policy_path.stem}.log"
        raise LaTeXError(tex_file=tex_path, log_file=log if log.exists() else None) from e

    pdf_path = out_dir / (policy_path.stem + ".pdf")
    return pdf_path
