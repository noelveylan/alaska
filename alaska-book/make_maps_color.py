#!/usr/bin/env python3
"""
Generate the FULL-COLOUR bonus-pack versions of the same maps, into
bonus-site/assets/maps/. Every black-and-white map in the print book says
"FULL COLOUR IN BONUS PACK" in its caption -- this is what fills that promise.

Reuses every drawing routine in make_maps.py unchanged: it imports that
module, overrides its palette (INK/GREY/LAND_FILL/LT/BG) and output
directory (IMG) as module globals, then calls the same build_geo() and
build_schematic() functions. Because those functions read the palette from
module globals at call time (not at import time), overriding them here is
enough -- there is no second copy of the map-drawing logic to keep in sync.

Run after make_maps.py, or standalone: python3 make_maps_color.py
"""
import os
import make_maps as mm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "bonus-site", "assets", "maps")
os.makedirs(OUT, exist_ok=True)
mm.IMG = OUT

# ---- bonus-pack color palette ----
mm.BG        = "#eaf3f8"   # water: soft cartographic blue
mm.LAND_FILL = "#f3f1e3"   # land: warm parchment
mm.INK       = "#1c2b3a"   # coastline / town dots / labels: deep navy ink
mm.GREY      = "#3f7f9e"   # ferries + unpaved-road grey slot: steamer blue
mm.LT        = "#a9c6d6"

if __name__ == "__main__":
    mm.build_geo()
    mm.build_schematic()
    print("done:", len(os.listdir(OUT)), "color maps ->", OUT)
