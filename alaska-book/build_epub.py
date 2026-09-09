#!/usr/bin/env python3
# Build the reflowable Kindle EPUB from the same 5 manuscript files.
import re, html, glob
from ebooklib import epub
import glob as _g

import os
HERE=os.path.dirname(os.path.abspath(__file__))
FILES = sorted(glob.glob(os.path.join(HERE,"manuscript","*.md")))

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t

# split manuscript into (heading, level, html_body) chapters
chapters = []  # (title, xhtml)
def new_chapter(title):
    chapters.append([title, []])

mapcount = [0]
def render_lines(lines):
    out = []
    para = []
    in_list = False
    def flush():
        nonlocal para
        if para:
            txt = " ".join(para).strip()
            if txt: out.append(f"<p>{inline(txt)}</p>")
            para = []
    def closel():
        nonlocal in_list
        if in_list: out.append("</ul>"); in_list = False
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("## VERIFICATION LOG"): break
        if (s.startswith("# ALASKA BY LAND AND SEA") or s.startswith("### Manuscript source")
            or s.startswith("### Draft") or s.startswith("> ") or s == "---"):
            i += 1; continue
        if s == "":
            flush(); closel(); i += 1; continue
        m = re.match(r'#\s+CHAPTER\s+(\d+)', s)
        if m:
            flush(); closel()
            n = int(m.group(1)); title = ""
            j = i + 1
            while j < len(lines):
                if lines[j].strip().startswith("## "): title = lines[j].strip()[3:].strip(); break
                j += 1
            i = j
            if out: chapters[-1][1] = out; out = []
            new_chapter(f"{n}. {title}")
            out = chapters[-1][1]
            out.append(f'<h1><span class="chnum">{n:02d}</span><br/>{inline(title)}</h1>')
            i += 1; continue
        if re.match(r'#\s+HOW TO USE THIS BOOK', s):
            flush(); closel()
            if out: chapters[-1][1] = out
            new_chapter("How to Use This Book"); out = chapters[-1][1]
            out.append('<h1>How to Use This Book</h1>'); i += 1; continue
        if re.match(r'#\s+PART FIVE', s):
            flush(); closel()
            title = "Ready-Made Itineraries"; j = i+1
            while j < len(lines):
                if lines[j].strip().startswith("## "): title = lines[j].strip()[3:].strip(); break
                j += 1
            i = j
            if out: chapters[-1][1] = out
            new_chapter(title); out = chapters[-1][1]
            out.append(f'<h1>{inline(title)}</h1>'); i += 1; continue
        if re.match(r'#\s+BACK MATTER', s):
            i += 1; continue
        if s.startswith("## "):
            flush(); closel()
            title = s[3:].strip()
            if out: chapters[-1][1] = out
            new_chapter(title); out = chapters[-1][1]
            out.append(f'<h1>{inline(title)}</h1>'); i += 1; continue
        if s.startswith("### "):
            flush(); closel(); out.append(f"<h2>{inline(s[4:].strip())}</h2>"); i += 1; continue
        if s.startswith("[MAP:"):
            flush(); closel()
            key = re.search(r'Atlas key:\s*(\w+)', s)
            key = key.group(1) if key else None
            mapcount[0] += 1
            desc = re.sub(r'\[MAP:\s*', '', s).strip().rstrip(']')
            desc = re.split(r'\.\s|Atlas key', desc)[0].strip().rstrip('.')
            if key:
                out.append(f'<figure class="map"><img src="images/{key}.png" alt="{html.escape(desc)}"/>'
                           f'<figcaption>Map {mapcount[0]}. {inline(desc)}. Full colour in the free companion pack.</figcaption></figure>')
            i += 1; continue
        if s.startswith("- "):
            flush()
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(s[2:].strip())}</li>"); i += 1; continue
        if s.startswith("*") and s.endswith("*") and ("mistake first-timers make here" in s or s.startswith("*The mistake")):
            flush(); closel()
            body = s.strip("*").strip()
            lab, rest = (body.split(":", 1) + [""])[:2] if ":" in body else ("The mistake first-timers make here", body)
            rest = rest.strip(); rest = rest[:1].upper() + rest[1:]
            out.append(f'<div class="callout"><p class="lab">{inline(lab.strip())}</p><p>{inline(rest)}</p></div>')
            i += 1; continue
        closel(); para.append(s); i += 1
    flush(); closel()
    if chapters: chapters[-1][1] = out

for f in FILES:
    render_lines(open(f).read().split("\n"))

# ---- build EPUB ----
book = epub.EpubBook()
book.set_identifier("alaska-land-and-sea-2027-noel-veylan")
book.set_title("Alaska by Land & Sea Travel Guide 2027")
book.set_language("en")
book.add_author("Noel Veylan")
book.add_metadata('DC', 'description',
  'Cruise ports, Denali, the Inside Passage and the Kenai ring road, with current 2026-2027 booking windows, real costs, RV routes and what to skip.')

style = """
body{font-family:serif;line-height:1.5;}
h1{font-family:sans-serif;font-size:1.5em;margin:1.2em 0 .2em;}
h1 .chnum{font-size:2.2em;font-weight:900;letter-spacing:.02em;}
h2{font-family:sans-serif;font-size:1.1em;margin:1.2em 0 .2em;}
p{margin:0 0 .7em;text-align:justify;}
.lead{font-size:1.1em;}
.callout{background:#f0ece2;border-left:4px solid #333;padding:.6em .9em;margin:1em 0;font-style:italic;}
.callout .lab{font-family:sans-serif;font-weight:bold;font-style:normal;text-transform:uppercase;font-size:.75em;letter-spacing:.08em;margin-bottom:.3em;}
figure.map{margin:1.2em 0;text-align:center;}
figure.map img{max-width:100%;border:1px solid #ccc;}
figcaption{font-style:italic;font-size:.85em;color:#444;margin-top:.4em;}
ul{margin:0 0 .7em 1.1em;}
li{margin:0 0 .3em;}
.frontnote{background:#f0ece2;padding:1em;margin:1.5em 0;font-size:.95em;}
"""
css = epub.EpubItem(uid="style", file_name="style/main.css", media_type="text/css", content=style)
book.add_item(css)

# add map images
import os
MAP_KEYS=[os.path.splitext(os.path.basename(p))[0] for p in _g.glob(os.path.join(HERE,"images","*.png"))]
for k in MAP_KEYS:
    with open(os.path.join(HERE,"images",f"{k}.png"),"rb") as fh:
        img = epub.EpubItem(uid=f"img_{k}", file_name=f"images/{k}.png",
                            media_type="image/png", content=fh.read())
        book.add_item(img)

# title/front chapter with the honest paperback note
front = epub.EpubHtml(title="Start Here", file_name="front.xhtml", lang="en")
front.add_item(css)
front.content = f"""<html><head><link rel="stylesheet" href="style/main.css"/></head><body>
<h1>Alaska by Land &amp; Sea</h1>
<p class="lead">Travel Guide 2027 &middot; Land and Sea Travel Guides &middot; Noel Veylan</p>
<div class="frontnote">
<p><strong>A note on this edition.</strong> This Kindle edition contains the complete guide: every chapter, every planning table, every booking window, and the same free companion pack as the paperback, with no email or purchase required.</p>
<p>The paperback edition adds a few things that only work on paper: the full-size map spreads, and the tear-out Quick Reference Card and itinerary pages, designed to photocopy and carry in a glovebox or daypack. If you like to plan on the page, the print edition is built for it. Either way, the planning information here is identical.</p>
</div>
<p>Travel guides built on research, not reminiscence.</p>
</body></html>"""
book.add_item(front)

spine = ['nav', front]
toc = []
for title, parts in chapters:
    body = "\n".join(parts if isinstance(parts, list) else [parts])
    fn = "ch_" + re.sub(r'[^a-z0-9]+','', title.lower())[:24] + ".xhtml"
    ch = epub.EpubHtml(title=title, file_name=fn, lang="en")
    ch.add_item(css)
    ch.content = f'<html><head><link rel="stylesheet" href="style/main.css"/></head><body>{body}</body></html>'
    book.add_item(ch); spine.append(ch); toc.append(ch)

# keep Kindle nav TOC concise (level 1 only) — already flat
book.toc = tuple(toc)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
book.spine = spine

epub.write_epub(os.path.join(HERE,"Alaska_2027_EBOOK.epub"), book)
print("EPUB written. chapters:", len(chapters), "| maps:", mapcount[0])
