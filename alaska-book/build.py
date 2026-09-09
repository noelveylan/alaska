#!/usr/bin/env python3
"""
Build the print-ready interior PDF from book.html.

    python3 build.py                 -> Alaska_2027_INTERIOR.pdf
    python3 build.py my_output.pdf   -> custom filename

Edit book.html and style.css freely, then re-run this.
Requires: pip install weasyprint   (and the fonts in fonts/ installed or resolvable)
"""
import sys, os
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
src  = os.path.join(HERE, "book.html")
out  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Alaska_2027_INTERIOR.pdf")

# base_url = project folder so relative images/, fonts/, style.css resolve
HTML(filename=src, base_url=HERE).write_pdf(out)

# quick sanity report
try:
    from pypdf import PdfReader
    n = len(PdfReader(out).pages)
    print(f"Built {os.path.basename(out)}  ({n} pages)")
except Exception:
    print(f"Built {os.path.basename(out)}")
