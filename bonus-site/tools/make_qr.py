#!/usr/bin/env python3
"""
Generate the QR code that goes on the book's back-matter page and title
page, pointing at this site.

The book (see book.html, "Your Bonus Pack" and "About Noel Veylan"
sections) currently has the address hard-coded as a placeholder:
"[your site]/alaska". Before this repo goes live:

  1. Decide the real URL (e.g. GitHub Pages: https://<you>.github.io/<repo>/,
     or a custom domain via Pages).
  2. Update SITE_URL below and re-run this script.
  3. Find-and-replace "https://YOUR-USERNAME.github.io/alaska-bonus-pack/"
     across bonus-site/*.html and book.html/manuscript with the real URL.
  4. Re-run this script to regenerate assets/img/qr-code.png, then rebuild
     the print PDF (python3 build.py) so the printed QR code is correct.
     Test the printed code at 6x9 size and at 1 inch minimum before print,
     per the note already in the book's back matter.

Requires: pip install qrcode[pil]
"""
import os
import qrcode

# ---- change this before the real launch ----
SITE_URL = "https://YOUR-USERNAME.github.io/alaska-bonus-pack/"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "img", "qr-code.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_M,  # tolerant of print wear
    box_size=20,
    border=4,
)
qr.add_data(SITE_URL)
qr.make(fit=True)
img = qr.make_image(fill_color="#141414", back_color="#F7F3EA")
img.save(OUT)
print(f"wrote {OUT}  ({img.size[0]}x{img.size[1]}px)  ->  {SITE_URL}")
print("PLACEHOLDER URL" if "YOUR-USERNAME" in SITE_URL else "")
