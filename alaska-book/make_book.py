#!/usr/bin/env python3
"""
Generate book.html from the markdown in manuscript/.
- References external images/<key>.png (regenerate with make_maps.py)
- Links external style.css (edit that for design changes)
- Fixes: drop caps apply ONLY to real prose chapters, never to reference/back-matter
Run this to (re)build book.html, then edit book.html directly, then run build.py for the PDF.
"""
import re, html, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
MANU = sorted(glob.glob(os.path.join(HERE, "manuscript", "*.md")))

def part_tab(n):
    if n is None: return "Start Here"
    if 1 <= n <= 6:  return "Decide"
    if 7 <= n <= 11: return "Book"
    if 12 <= n <= 17:return "Drive It"
    if 18 <= n <= 23:return "Do It Well"
    return "Reference"

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t

def map_figure(raw, mapcount):
    key = re.search(r'Atlas key:\s*(\w+)', raw)
    key = key.group(1) if key else "map"
    desc = re.sub(r'\[MAP:\s*', '', raw).strip().rstrip(']')
    desc = re.split(r'\.\s|\. ?4\.75|Atlas key', desc)[0].strip().rstrip('.')
    return (f'<figure class="map"><div class="frame">'
            f'<div class="caphead"><span>MAP {mapcount}</span><span>FULL COLOUR IN BONUS PACK</span></div>'
            f'<div class="art"><img src="images/{key}.png" alt="{html.escape(desc)}"></div></div>'
            f'<figcaption>Map {mapcount}. {inline(desc)}.</figcaption></figure>')

def parse_file(path, st):
    lines = open(path).read().split("\n")
    out=[]; para=[]; in_list=False; i=0
    def flush():
        nonlocal para
        if para:
            txt=" ".join(para).strip()
            if txt:
                cls=""
                if st.get("await_lead"):
                    cls=' class="lead"'; st["await_lead"]=False
                    st["await_drop"]=st.get("allow_drop",False)
                elif st.get("await_drop"):
                    cls=' class="drop"'; st["await_drop"]=False
                body = inline(txt)
                if cls==' class="drop"':
                    # wrap the first letter in a real <span> the CSS floats
                    # for the drop cap -- not ::first-letter, which WeasyPrint
                    # can lay out overlapping the rest of the line
                    body = re.sub(r'^(<strong>)?(.)', r'\1<span class="dropcap">\2</span>', body)
                out.append(f"<p{cls}>{body}</p>")
            para=[]
    def closel():
        nonlocal in_list
        if in_list: out.append("</ul>"); in_list=False

    while i < len(lines):
        s=lines[i].strip()
        if s.startswith("## VERIFICATION LOG"): break
        if (s.startswith("# ALASKA BY LAND AND SEA") or s.startswith("### Manuscript source")
            or s.startswith("### Draft") or s.startswith("> ") or s=="---"):
            i+=1; continue
        if s=="":
            flush(); closel(); i+=1; continue

        m=re.match(r'#\s+CHAPTER\s+(\d+)', s)
        if m:
            flush(); closel()
            if st["open"]: out.append("</section>"); st["open"]=False
            n=int(m.group(1)); title=""; j=i+1
            while j<len(lines):
                if lines[j].strip().startswith("## "): title=lines[j].strip()[3:].strip(); break
                j+=1
            i=j; cid=f"ch{n}"; st["toc"].append((cid,f"{n}. {title}"))
            out.append(f'<section class="chapter" id="{cid}">'
                       f'<div class="opener"><div class="tabrow"><span class="tab">{html.escape(part_tab(n))}</span></div>'
                       f'<div class="num">{n:02d}</div><h2>{inline(title)}</h2><div class="hr"></div></div>')
            st["open"]=True; st["await_lead"]=True; st["allow_drop"]=True; st["await_drop"]=False
            i+=1; continue

        if re.match(r'#\s+HOW TO USE THIS BOOK', s):
            flush(); closel()
            if st["open"]: out.append("</section>"); st["open"]=False
            cid="howto"; st["toc"].append((cid,"How to Use This Book"))
            out.append(f'<section class="chapter" id="{cid}">'
                       f'<div class="opener"><div class="tabrow"><span class="tab">Start Here</span></div>'
                       f'<h2 class="noNum">How to Use This Book</h2><div class="hr"></div></div>')
            st["open"]=True; st["await_lead"]=True; st["allow_drop"]=True; st["await_drop"]=False
            i+=1; continue

        if re.match(r'#\s+PART FIVE', s):
            flush(); closel()
            if st["open"]: out.append("</section>"); st["open"]=False
            title="Ready-Made Itineraries"; j=i+1
            while j<len(lines):
                if lines[j].strip().startswith("## "): title=lines[j].strip()[3:].strip(); break
                j+=1
            i=j; cid="itineraries"; st["toc"].append((cid,title)); st["part_tab"]="Itineraries"
            out.append(f'<section class="chapter" id="{cid}">'
                       f'<div class="opener"><div class="tabrow"><span class="tab">Itineraries</span></div>'
                       f'<h2 class="noNum">{inline(title)}</h2><div class="hr"></div></div>')
            st["open"]=True; st["await_lead"]=True; st["allow_drop"]=False; st["await_drop"]=False
            i+=1; continue

        if re.match(r'#\s+BACK MATTER', s):
            flush(); closel(); st["part_tab"]="Reference"; i+=1; continue

        if s.startswith("## "):   # standalone back-matter section: NO lead, NO drop
            flush(); closel()
            if st["open"]: out.append("</section>"); st["open"]=False
            title=s[3:].strip(); cid="sec_"+re.sub(r'[^a-z0-9]+','',title.lower())[:20]
            st["toc"].append((cid,title)); tab=st.get("part_tab","Reference")
            out.append(f'<section class="chapter" id="{cid}">'
                       f'<div class="opener"><div class="tabrow"><span class="tab">{html.escape(tab)}</span></div>'
                       f'<h2 class="noNum small">{inline(title)}</h2><div class="hr"></div></div>')
            st["open"]=True; st["await_lead"]=False; st["allow_drop"]=False; st["await_drop"]=False
            i+=1; continue

        if s.startswith("### "):
            flush(); closel(); out.append(f"<h3>{inline(s[4:].strip())}</h3>"); i+=1; continue

        if s.startswith("[MAP:"):
            flush(); closel(); st["mapcount"]+=1
            out.append(map_figure(s, st["mapcount"])); i+=1; continue

        if s.startswith("- "):
            flush()
            if not in_list: out.append("<ul>"); in_list=True
            out.append(f"<li>{inline(s[2:].strip())}</li>"); i+=1; continue

        if s.startswith("*") and s.endswith("*") and ("mistake first-timers make here" in s or s.startswith("*The mistake")):
            flush(); closel()
            body=s.strip("*").strip()
            if ":" in body: lab,rest=body.split(":",1)
            else: lab,rest="The mistake first-timers make here",body
            rest=rest.strip(); rest=rest[:1].upper()+rest[1:] if rest else rest
            out.append(f'<div class="callout"><span class="lab">{inline(lab.strip())}</span><p>{inline(rest)}</p></div>')
            i+=1; continue

        closel(); para.append(s); i+=1

    flush(); closel()
    if st["open"]: out.append("</section>"); st["open"]=False
    return "\n".join(out)

st={"toc":[], "mapcount":0, "part_tab":"Reference", "open":False,
    "await_lead":False, "allow_drop":False, "await_drop":False}
body="\n".join(parse_file(f, st) for f in MANU)

toc_rows="".join(
    f'<div class="tocrow"><a href="#{cid}"><span class="tt">{inline(title)}</span></a></div>'
    for cid,title in st["toc"])

front=f"""
<section class="titlepage">
  <div class="eyebrow">2027 Edition</div>
  <h1>Alaska<br>by Land<br>&amp; Sea</h1>
  <div class="series">Land and Sea Travel Guides</div>
  <div class="trule"></div>
  <div class="fmt">Travel Guide 2027</div>
  <div class="author">Noel Veylan</div>
</section>
<section class="copyright">
  <p class="cw">ALASKA BY LAND &amp; SEA TRAVEL GUIDE 2027</p>
  <p>Copyright &copy; 2026 Noel Veylan. All rights reserved.</p>
  <p>No part of this book may be reproduced or transmitted in any form without written permission from the publisher, except brief quotations in a review.</p>
  <p class="cw2">A planning note.</p>
  <p>This guide is built for planning. Road conditions, ferry schedules, park access, fees, and booking windows in Alaska change with the season and sometimes overnight. Every figure in this book was checked against a primary source at the time of writing. Verify anything that carries a date, a price, or a booking rule against the official source before you book. The free companion page listed in the back tracks what changes after printing.</p>
  <p class="cw2">Land and Sea Travel Guides</p>
  <p>Travel guides built on research, not reminiscence.</p>
  <p class="csmall">First edition. Printed for the 2027 season.</p>
</section>
<section class="toc">
  <div class="opener"><div class="tabrow"><span class="tab">Contents</span></div>
  <h2 class="noNum">Contents</h2><div class="hr"></div></div>
  {toc_rows}
</section>
"""

doc=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Alaska by Land &amp; Sea Travel Guide 2027</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
{front}
{body}
</body>
</html>"""

open(os.path.join(HERE,"book.html"),"w").write(doc)
print(f"wrote book.html  |  {len(st['toc'])} TOC entries  |  {st['mapcount']} maps referenced")
