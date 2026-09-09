# Alaska by Land & Sea 2027 — book project

Everything to edit the book and rebuild the print PDF and the Kindle ebook. Open this folder
in VS Code. You edit plain HTML/CSS; a script turns it into a print-ready PDF.

## Quick start

```bash
pip install -r requirements.txt          # weasyprint, matplotlib, ebooklib, pypdf
# make the fonts findable (once):
mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts && fc-cache -f

python3 make_maps.py     # (re)generate the maps into images/   (optional; already done)
python3 build.py         # book.html  ->  Alaska_2027_INTERIOR.pdf
python3 build_epub.py    # manuscript ->  Alaska_2027_EBOOK.epub
```

Open `Alaska_2027_INTERIOR.pdf` to see the result. Edit, run `build.py`, repeat.

## What to edit

- **`book.html`** — the whole book as HTML. **This is the file you edit** to fix wording, fix
  anything that rendered wrong, add or remove text. It is plain HTML; edit it directly in VS Code.
- **`style.css`** — the design: page size, margins, fonts, chapter openers, the mistake callouts,
  map frames, spacing. Change the look here. It is commented.
- **`manuscript/*.md`** — the original text in Markdown, five files. If you would rather write in
  Markdown, edit these and run `python3 make_book.py` to regenerate `book.html`.
  **Note:** `make_book.py` overwrites `book.html`, so pick one source of truth. For small fixes,
  edit `book.html` directly. For big rewrites, edit the Markdown and regenerate.

## The maps

- `make_maps.py` builds every map into **`images/`** as PNG. `book.html` points at those files
  (`<img src="images/denali_road.png">`), so to change a map you replace the PNG and rebuild.
- The regional maps (`kenai`, `inside_passage`, `southeast`, `interior`, `copper_river`,
  `alaska_overview`, `itineraries_overview`) are drawn from **public-domain Natural Earth
  coastline data** (`ne_land.geojson`) — real geography, correct town positions, route lines on top.
- The road diagrams (`denali_road`, `denali_detail`) and `booking_timeline` are schematic by design.
- **To use survey-accurate TIGER atlas maps instead:** run the TIGER atlas (needs census.gov access,
  which works on your machine) and drop its PNGs into `images/` using the **same filenames**
  (`denali_road.png`, `kenai.png`, ...). No HTML change needed. The filenames already match the atlas keys.
- Edit town coordinates, which towns show, route lines, and bounding boxes near the top of
  `make_maps.py` (the `T = {...}` dict and the `build_geo()` frames).
- **`make_maps_color.py`** builds the same maps a second time in full color, into
  **`../bonus-site/assets/maps/`** — these are the "FULL COLOUR IN BONUS PACK" versions every map
  caption promises. It imports `make_maps.py` and overrides its palette rather than duplicating the
  drawing code, so a geography/route change made in `make_maps.py` only needs both scripts re-run,
  not two files edited. See `../bonus-site/README.md` for the bonus site itself.

## Files

```
book.html            the book, editable HTML          <- edit this
style.css            the design, editable CSS          <- and this
build.py             book.html  -> print PDF
build_epub.py        manuscript -> Kindle EPUB
make_book.py         manuscript -> book.html (regenerate)
make_maps.py         -> images/*.png  (real + schematic maps, B&W, for print)
make_maps_color.py   -> ../bonus-site/assets/maps/*.png  (same maps, full color, for the bonus pack)
manuscript/          five Markdown source files
images/              generated map PNGs
fonts/               embeddable fonts (Gelasio = Georgia-compatible; Archivo)
ne_land.geojson      public-domain coastline data for make_maps
Alaska_2027_INTERIOR.pdf   built print interior (example output)
Alaska_2027_EBOOK.epub     built Kindle edition (example output)
```

## KDP notes

- Interior PDF is 6x9, black on cream, mirrored margins, fonts embedded. Upload as the paperback interior.
- The **cover** is separate (needs the final page count for the spine + a cover photo). Not in this project.
- Fonts are Gelasio (open, Georgia-metric) and Archivo (open). Both are licensed for embedding/sale.
  Gelasio covers the `x̂` in "Unangax̂", so that character renders correctly.
- Before publishing, re-verify the time-sensitive facts (Denali 2027 road status, ferry dates, fees)
  against their official sources. Search the manuscript for `VERIFICATION LOG` — those notes list
  every figure and its source. (They are stripped from the built book automatically.)
- **Before publishing, also replace the bonus-pack URL.** `book.html` has a placeholder
  (`https://YOUR-USERNAME.github.io/alaska-bonus-pack/`, search for `YOUR-USERNAME`) in two spots
  and a placeholder QR code (`images/qr_code.png`) pointing at it. Once the bonus site's real URL
  is decided, see `../bonus-site/README.md` for the three-step swap, then rebuild the PDF.
```
