#!/usr/bin/env python3
"""Convert CS599 report from Markdown to PDF with navigation bookmarks."""

import sys
import os

sys.path.insert(0, r"C:\Users\lt\AppData\Local\Programs\Python\Python39\Lib\site-packages")

import markdown
from xhtml2pdf import pisa

CSS = """
body {
    font-family: "Microsoft YaHei", "SimSun", "STSong", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #333;
}

h1 {
    font-size: 20pt;
    color: #1a1a2e;
    border-bottom: 3px solid #1a1a2e;
    padding-bottom: 8px;
    margin-top: 40px;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 15pt;
    color: #16213e;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-top: 25px;
}

h3 {
    font-size: 12pt;
    color: #0f3460;
    margin-top: 18px;
}

h4 {
    font-size: 11pt;
    color: #533483;
    margin-top: 12px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 9.5pt;
}

th {
    background-color: #1a1a2e;
    color: white;
    padding: 6px 10px;
    text-align: left;
}

td {
    border: 1px solid #ddd;
    padding: 5px 10px;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

code {
    background-color: #f4f4f4;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9pt;
}

pre {
    background-color: #2d2d2d;
    color: #f8f8f2;
    padding: 12px;
    border-radius: 5px;
    font-size: 8.5pt;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
}

pre code {
    background: none;
    color: inherit;
    padding: 0;
}

blockquote {
    border-left: 4px solid #e94560;
    margin: 12px 0;
    padding: 8px 16px;
    background-color: #fff5f5;
    color: #555;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 25px 0;
}

strong {
    color: #1a1a2e;
}
"""


def convert(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown to HTML
    extensions = ["tables", "fenced_code", "toc"]
    html_body = markdown.markdown(md_text, extensions=extensions)

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    with open(pdf_path, "wb") as f:
        status = pisa.CreatePDF(full_html, dest=f, encoding="utf-8")

    if status.err:
        print(f"Error generating PDF: {status.err}")
        return False

    print(f"PDF generated: {pdf_path}")
    return True


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(base, "docs", "CS599_大作业报告.md")
    pdf_path = os.path.join(base, "docs", "CS599_大作业报告.pdf")
    convert(md_path, pdf_path)
