"""Render docs/filters*.md to a PDF.

Usage:
    python scripts/build_filters_pdf.py              # English
    python scripts/build_filters_pdf.py fr           # French (docs/filters.fr.md)
"""
import sys
from pathlib import Path

import markdown
from xhtml2pdf import pisa

ROOT = Path(__file__).resolve().parent.parent

LANGUAGES = {
    "en": {
        "source": ROOT / "docs" / "filters.md",
        "output": ROOT / "docs" / "filters.pdf",
        "title": "CV-Tools Filter Reference",
        "subtitle": "Every filter, parameter, and caveat in one document",
        "footer": "CV-Tools Filter Reference",
    },
    "fr": {
        "source": ROOT / "docs" / "filters.fr.md",
        "output": ROOT / "docs" / "filters.fr.pdf",
        "title": "CV-Tools — Référence des filtres",
        "subtitle": "Chaque filtre, paramètre et mise en garde en un seul document",
        "footer": "CV-Tools — Référence des filtres",
    },
}

CSS = """
@page {
    size: A4;
    margin: 2cm 1.8cm;
    @frame footer_frame {
        -pdf-frame-content: footer_content;
        bottom: 1cm; margin-left: 1.8cm; margin-right: 1.8cm; height: 1cm;
    }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 20pt; color: #12283d; margin-top: 0; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 13.5pt; color: #17405e; margin-top: 16pt; border-bottom: 0.75pt solid #c7d2db; padding-bottom: 3pt; }
h3 { font-size: 11pt; color: #17405e; }
p { margin: 5pt 0; }
code { font-family: Courier, monospace; font-size: 8.5pt; background-color: #eef1f4; padding: 1pt 2pt; }
pre { background-color: #eef1f4; padding: 6pt; font-family: Courier, monospace; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 8.5pt; }
th { background-color: #17405e; color: #ffffff; text-align: left; padding: 4pt 6pt; }
td { border-bottom: 0.5pt solid #d7dde2; padding: 4pt 6pt; vertical-align: top; }
tr:nth-child(even) td { background-color: #f5f7f9; }
hr { border: none; border-top: 0.75pt solid #c7d2db; margin: 14pt 0; }
strong { color: #12283d; }
a { color: #1a5fb4; }
ul, ol { margin: 4pt 0; padding-left: 16pt; }
li { margin: 2pt 0; }
"""

def build(lang: str) -> None:
    cfg = LANGUAGES[lang]
    md_text = cfg["source"].read_text(encoding="utf-8")
    body_html = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    title_html = f"""
<div style="text-align:center; margin-top:35%;">
  <h1 style="page-break-before:avoid; border:none; font-size:28pt;">{cfg['title']}</h1>
  <p style="font-size:11pt; color:#4a5a68;">{cfg['subtitle']}</p>
</div>
<pdf:nextpage />
"""
    footer_html = f"""
<div id="footer_content" style="text-align:center; font-size:8pt; color:#8a97a3;">
  {cfg['footer']} &mdash; page <pdf:pagenumber/>
</div>
"""
    full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{footer_html}
{title_html}
{body_html}
</body>
</html>"""

    output = cfg["output"]
    with output.open("wb") as f:
        result = pisa.CreatePDF(full_html, dest=f, encoding="utf-8")

    if result.err:
        sys.exit(f"PDF generation failed with {result.err} error(s)")

    print(f"Wrote {output} ({output.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    lang_arg = sys.argv[1] if len(sys.argv) > 1 else "en"
    if lang_arg not in LANGUAGES:
        sys.exit(f"Unknown language '{lang_arg}'. Choices: {', '.join(LANGUAGES)}")
    build(lang_arg)
