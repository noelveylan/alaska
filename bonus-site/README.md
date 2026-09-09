# Alaska by Land & Sea — Bonus Pack

The free companion website for *Alaska by Land & Sea 2027* by Noel Veylan. Plain HTML/CSS,
no build step, no backend — safe to serve straight off GitHub Pages.

**What's here:** full-color versions of every map in the book, a printable booking-countdown
calendar, a budget worksheet (with a downloadable spreadsheet), season-specific packing
checklists, a curated list of official reservation/status links, and an update log. See
`index.html` for the live structure — this pack intentionally does **not** include the book's
paid content (the manuscript, the print PDF, the EPUB); only the free bonus resources live here.

## Before you go live

1. **Pick your URL.** GitHub Pages gives you `https://<username>.github.io/<repo>/` for free, or
   point a custom domain at Pages if you own one.
2. **Bake it in.** Two places need the real URL:
   - `tools/make_qr.py` — set `SITE_URL`, then run `python3 tools/make_qr.py` to regenerate
     `assets/img/qr-code.png`.
   - Every `https://YOUR-USERNAME.github.io/alaska-bonus-pack/` placeholder in these HTML files
     (search for it) — update the footer GitHub links and any other self-references.
3. **Wire it into the book.** `alaska-book/book.html` has a `TODO before print` comment right
   above the "Your Bonus Pack" section (search for `YOUR-USERNAME`) with the same three
   placeholders: the address text (appears twice — "Your Bonus Pack" and "About Noel Veylan"),
   and `images/qr_code.png`, which should be the same file this script generates (copy
   `bonus-site/assets/img/qr-code.png` over it). Rebuild the PDF afterward: `python3 build.py`.
4. **Deploy.** Push this repo to GitHub, then in the repo's Settings → Pages, deploy from the
   `main` branch (root, since these files sit at the repo root already).

## Regenerating the maps

The full-color maps in `assets/maps/` are generated, not drawn by hand — they come from
`../alaska-book/make_maps_color.py`, which imports `../alaska-book/make_maps.py` and overrides
its palette (see that script's docstring). If you edit a route, a town, or a label in
`make_maps.py` for the print book, re-run both scripts to keep the black-and-white print maps
and these color bonus-pack maps in sync:

```bash
cd ../alaska-book
python3 make_maps.py          # -> alaska-book/images/*.png (print, B&W)
python3 make_maps_color.py    # -> bonus-site/assets/maps/*.png (bonus pack, color)
```

## Content sources

The calendar, budget, and packing pages are transcribed and lightly reorganized from Chapters
5, 7, and 22 of the book, so a wording or number change in the manuscript should be mirrored
here. The links page is hand-curated and checked against the live agency sites — recheck it
periodically and log anything that moved on `updates.html`.

## License

The code (HTML/CSS) here is free to reuse. The written content — the calendar, budget figures,
packing lists, and any book text — is © Noel Veylan and is published here specifically as the
book's free companion pack, not under an open license.
