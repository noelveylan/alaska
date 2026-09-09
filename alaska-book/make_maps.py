#!/usr/bin/env python3
"""
Generate the book's maps as PNG files in images/.

Geographic maps use PUBLIC-DOMAIN Natural Earth coastline data (ne_land.geojson).
Schematic maps (the Denali road diagram, the booking timeline) are drawn directly.
Every file is 4.75 in wide at 300 dpi to match the 6x9 live text block.

Filenames match the atlas keys used in the manuscript, so if you later generate
survey-accurate maps with the TIGER atlas on a machine with census.gov access,
just drop those PNGs in here under the same names and rebuild. No HTML changes needed.
"""
import json, os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.font_manager import FontProperties
from matplotlib import patheffects

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
os.makedirs(IMG, exist_ok=True)
LAND = os.path.join(HERE, "ne_land.geojson")   # public-domain Natural Earth

# palette -- module globals so a second script can import this module,
# override these (and IMG), and call build_geo()/build_schematic() to
# render a differently-colored edition (e.g. the bonus-pack color maps)
# without duplicating the drawing code.
INK = "#111111"; GREY = "#8a8a8a"; LAND_FILL = "#e9e9e9"; LT = "#bbbbbb"; BG = "white"

def halo():
    # a halo behind text, in the current background color, so labels stay
    # readable when a route, ferry line, or coastline detail crosses under
    # them -- a function (not a constant) so it tracks BG if overridden
    return [patheffects.withStroke(linewidth=2.5, foreground=BG)]

try:
    FP = FontProperties(fname=os.path.join(HERE, "fonts", "Archivo-SemiBold.ttf"))
    FPB = FontProperties(fname=os.path.join(HERE, "fonts", "Archivo-Bold.ttf"))
except Exception:
    FP = FPB = FontProperties()

# ---- town coordinates (lon, lat) ----
T = {
 "Anchorage":(-149.90,61.22),"Seward":(-149.44,60.10),"Homer":(-151.55,59.64),
 "Soldotna":(-151.06,60.49),"Kenai":(-151.26,60.55),"Whittier":(-148.68,60.77),
 "Portage":(-148.83,60.79),"Denali":(-148.92,63.73),"Talkeetna":(-150.11,62.32),
 "Cantwell":(-148.95,63.39),"Fairbanks":(-147.72,64.84),"Juneau":(-134.42,58.30),
 "Ketchikan":(-131.65,55.34),"Sitka":(-135.33,57.05),"Skagway":(-135.31,59.46),
 "Haines":(-135.45,59.24),"Wrangell":(-132.38,56.47),"Glennallen":(-145.55,62.11),
 "Valdez":(-146.35,61.13),"Chitina":(-144.44,61.52),"McCarthy":(-142.92,61.43),
 "Paxson":(-145.49,63.02),
}

def _rings(geom):
    out=[]
    if geom["type"]=="Polygon":
        out.append(geom["coordinates"][0])
    elif geom["type"]=="MultiPolygon":
        for poly in geom["coordinates"]:
            out.append(poly[0])
    return out

_LAND_RINGS=None
def land_rings():
    global _LAND_RINGS
    if _LAND_RINGS is None:
        gj=json.load(open(LAND))
        r=[]
        for f in gj["features"]:
            r+=_rings(f["geometry"])
        _LAND_RINGS=r
    return _LAND_RINGS

def geo_map(fname, bbox, towns, routes=None, ferries=None, unpaved=None, labels=None,
            road_out=None, title=None, big=None, figfrac_h=None, label_offsets=None):
    """bbox=(lon_min,lon_max,lat_min,lat_max)
    routes = paved roads (solid black); ferries = ferry legs (grey dashed);
    unpaved = gravel/unpaved roads (grey dotted); road_out = stub lines to
    an off-map connection, as (town, dx_deg, dy_deg, label); label_offsets
    overrides the default (5,3)pt label placement for specific towns, as
    {town: (dx_pt, dy_pt)}, for towns close enough together that the
    default offset would print one label on top of another."""
    lon0,lon1,lat0,lat1=bbox
    latm=(lat0+lat1)/2
    asp=1/math.cos(math.radians(latm))            # simple equirectangular correction
    W=4.75
    # height from bbox aspect
    h = W * ((lat1-lat0)/(lon1-lon0)) * asp
    h = max(2.2, min(h, 6.0))
    fig,ax=plt.subplots(figsize=(W,h),dpi=300)
    # land
    for ring in land_rings():
        xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
        if max(xs)<lon0-2 or min(xs)>lon1+2 or max(ys)<lat0-2 or min(ys)>lat1+2:
            continue
        ax.add_patch(MplPolygon(list(zip(xs,ys)), closed=True,
                     facecolor=LAND_FILL, edgecolor=INK, linewidth=0.6, zorder=1))
    # routes (solid paved roads)
    for a,b in (routes or []):
        ax.plot([T[a][0],T[b][0]],[T[a][1],T[b][1]], color=INK, lw=1.6, zorder=3)
    # ferries (dashed)
    for a,b in (ferries or []):
        ax.plot([T[a][0],T[b][0]],[T[a][1],T[b][1]], color=GREY, lw=1.2, ls=(0,(4,3)), zorder=3)
    # unpaved/gravel roads (dotted, visually distinct from ferries)
    for a,b in (unpaved or []):
        ax.plot([T[a][0],T[b][0]],[T[a][1],T[b][1]], color=GREY, lw=1.3, ls=(0,(1,1.6)), zorder=3)
    # stub lines to an off-map connection (e.g. "road to Canada")
    for name,dx,dy,lab in (road_out or []):
        x,y=T[name]
        ax.plot([x,x+dx],[y,y+dy], color=INK, lw=1.6, zorder=3)
        ax.text(x+dx,y+dy,lab,fontproperties=FP,fontsize=6.8,color=INK,
                 ha="left" if dx>=0 else "right", va="bottom" if dy>=0 else "top",
                 zorder=6, path_effects=halo())
    # towns
    for name in towns:
        x,y=T[name]
        isbig = big and name in big
        ax.plot(x,y,'o',ms=6 if isbig else 4,color=INK,zorder=5)
        off = (label_offsets or {}).get(name,(5,3))
        ax.annotate(name,(x,y),xytext=off,textcoords="offset points",
                    fontproperties=FPB if isbig else FP, fontsize=8.5 if isbig else 7.5,
                    color=INK, zorder=6, path_effects=halo())
    # freeform region labels
    for txt,(lx,ly),sz in (labels or []):
        ax.text(lx,ly,txt,fontproperties=FPB,fontsize=sz,color=INK,ha="center",zorder=4,
                 path_effects=halo())
    ax.set_xlim(lon0,lon1); ax.set_ylim(lat0,lat1)
    ax.set_aspect(asp)
    ax.axis("off")
    if title:
        ax.text(0.5,0.98,title,transform=ax.transAxes,ha="center",va="top",
                fontproperties=FPB,fontsize=10,color=INK, path_effects=halo())
    fig.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
    fig.savefig(os.path.join(IMG,fname),dpi=300,facecolor=BG,
                bbox_inches="tight",pad_inches=0.04)
    plt.close(fig)
    print("wrote "+os.path.join(IMG,fname))

def schematic(fname, draw, w=4.75, h=1.7):
    fig,ax=plt.subplots(figsize=(w,h),dpi=300)
    # NOTE: the draw callbacks below all place elements on a fixed 0-100 x 0-100
    # coordinate grid (matching the x-axis), regardless of the figure's aspect
    # ratio -- so the y-limit must stay 0-100 too. (It used to be scaled by
    # h/w, which put most of the artwork above the visible frame and made
    # these diagrams render as a near-empty white box.)
    ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
    draw(ax)
    fig.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
    fig.savefig(os.path.join(IMG,fname),dpi=300,facecolor=BG,
                bbox_inches="tight",pad_inches=0.05)
    plt.close(fig)
    print("wrote "+os.path.join(IMG,fname))

# ---------- GEOGRAPHIC MAPS (real coastlines) ----------
def build_geo():
    geo_map("alaska_overview.png",(-172,-129,51,72),
        towns=["Anchorage","Fairbanks","Juneau","Ketchikan","Denali"],
        big=["Anchorage"],
        # region labels moved off the town dots/labels and off the busiest
        # coastline detail (Southcentral fjords, the SE archipelago) so they
        # read as open-area labels instead of overlapping other text
        labels=[("SOUTHEAST",(-137.5,55.0),8),("INTERIOR",(-157,66.5),8),
                ("SOUTHCENTRAL",(-152.5,58.2),8),("SOUTHWEST",(-160,57),8)],
        title="Alaska, by region")
    # itineraries overview = same base map, different title. Seward dropped:
    # at this zoom it sits right on top of Anchorage's dot/label and only
    # duplicates it -- Anchorage already anchors that part of the map.
    geo_map("itineraries_overview.png",(-172,-129,51,72),
        towns=["Anchorage","Fairbanks","Juneau","Ketchikan","Denali"],
        big=["Anchorage"], title="Where the trips go")
    geo_map("kenai.png",(-152.8,-147.8,59.3,61.6),
        towns=["Anchorage","Seward","Homer","Soldotna","Kenai","Whittier","Portage"],
        big=["Anchorage"],
        routes=[("Anchorage","Portage"),("Portage","Seward"),("Seward","Soldotna"),
                ("Soldotna","Homer"),("Soldotna","Kenai")],
        ferries=[("Portage","Whittier")],
        # Portage and Whittier sit only a few miles apart, close enough that
        # the default label offset put one name on top of the other
        label_offsets={"Portage":(-6,7),"Whittier":(5,-9)},
        title="Southcentral & the Kenai Peninsula")
    geo_map("interior.png",(-152.5,-143.0,60.6,64.4),
        towns=["Anchorage","Talkeetna","Cantwell","Denali","Paxson","Glennallen","Valdez"],
        big=["Anchorage","Denali"],
        routes=[("Anchorage","Talkeetna"),("Talkeetna","Cantwell"),("Cantwell","Denali"),
                ("Paxson","Glennallen"),("Glennallen","Valdez")],
        unpaved=[("Cantwell","Paxson")],
        title="The Interior & the road to Denali")
    # new: Chapter 15 (the Glenn Highway & Copper River country) referenced
    # McCarthy, Kennecott, and Chitina in the text but had no map at all --
    # T already had coordinates for Chitina and McCarthy sitting unused.
    geo_map("copper_river.png",(-150.5,-142.0,60.6,62.6),
        towns=["Anchorage","Glennallen","Chitina","McCarthy","Valdez"],
        big=["Anchorage","Glennallen"],
        routes=[("Anchorage","Glennallen"),("Glennallen","Chitina"),("Glennallen","Valdez")],
        unpaved=[("Chitina","McCarthy")],
        title="The Glenn Highway & the Copper River country")
    geo_map("inside_passage.png",(-137.6,-129.8,54.5,60.2),
        towns=["Ketchikan","Wrangell","Sitka","Juneau","Haines","Skagway"],
        big=["Juneau"],
        ferries=[("Ketchikan","Wrangell"),("Wrangell","Sitka"),("Sitka","Juneau"),
                 ("Juneau","Haines"),("Haines","Skagway")],
        title="The Inside Passage")
    # southeast by land: same ferry network as the Inside Passage map, plus
    # the actual point of this chapter -- the two road connections out of
    # the panhandle to the Yukon, drawn as stub lines off the top edge
    # (bbox stretched north so they have room), which the old version of
    # this map promised in its caption but never drew.
    geo_map("southeast.png",(-137.6,-129.8,54.5,61.6),
        towns=["Ketchikan","Wrangell","Sitka","Juneau","Haines","Skagway"],
        big=["Juneau"],
        ferries=[("Ketchikan","Wrangell"),("Wrangell","Sitka"),("Sitka","Juneau"),
                 ("Juneau","Haines"),("Haines","Skagway")],
        # extra headroom above (lat1 raised to 61.6) keeps these stub labels
        # well clear of the title band at the top of the frame
        road_out=[("Skagway",0.3,0.65,"Klondike Hwy\nto Yukon, Canada"),
                   ("Haines",-0.5,0.65,"Haines Hwy\nto Yukon, Canada")],
        title="Southeast by land and ferry")

# ---------- SCHEMATIC DIAGRAMS ----------
def _denali_road(ax):
    ax.plot([6,94],[60,60],color=INK,lw=2.2,solid_capstyle="round")
    pts=[(8,"Entrance",False),(26,"Mi 15",False),(50,"Mi 43",True),
         (72,"Eielson\nMi 66",False),(84,"Wonder\nLk 85",False),(93,"Kantishna\n92",False)]
    ax.plot(58,60,'s',ms=9,color=INK); ax.text(58,72,"Pretty Rocks\nbridge",ha="center",fontproperties=FPB,fontsize=6.5,color=INK)
    for x,lab,red in pts:
        ax.plot(x,60,'o',ms=7 if red else 5,color="#E26D5A" if red else INK)
        ax.text(x,48,lab,ha="center",va="top",fontproperties=FP,fontsize=6.5,color=INK)
    ax.text(17,66,"private cars",ha="center",fontproperties=FP,fontsize=6,color=GREY)
    ax.text(40,66,"bus only  →",ha="center",fontproperties=FP,fontsize=6,color=GREY)
    ax.text(80,66,"reopens 2027",ha="center",fontproperties=FP,fontsize=6,color=GREY)

def _denali_detail(ax):
    ax.plot([6,94],[55,55],color=INK,lw=2.2,solid_capstyle="round")
    pts=[(8,"Entrance"),(20,"Riley Ck"),(30,"Savage R"),(50,"Teklanika"),
         (72,"Eielson"),(84,"Wonder\nLk"),(93,"Kantishna")]
    ax.plot(58,55,'s',ms=8,color=INK)
    for x,lab in pts:
        ax.plot(x,55,'o',ms=5,color=INK)
        ax.text(x,44,lab,ha="center",va="top",fontproperties=FP,fontsize=6.2,color=INK)
    for x in [20,30,50,84]:
        ax.plot(x,63,'^',ms=5,color=INK)
    # a drawn triangle marker as the legend key, not a unicode glyph -- the
    # Archivo font has no U+25B2 "▲" glyph, so that character was rendering
    # as a missing-glyph tofu box in the built PDF
    ax.plot(44,74,'^',ms=5,color=GREY)
    ax.text(46.5,74,"campgrounds",ha="left",va="center",fontproperties=FP,fontsize=6.5,color=GREY)
    ax.text(20,49,"cars to Mi 15",ha="left",fontproperties=FP,fontsize=6,color=GREY)

def _booking_timeline(ax):
    ax.plot([8,92],[52,52],color=INK,lw=2.0)
    for x,l in [(8,"12 mo"),(28,"9 mo"),(48,"6 mo"),(68,"3 mo"),(86,"1 mo"),(92,"go")]:
        ax.plot([x,x],[49,55],color=INK,lw=1.2); ax.text(x,42,l,ha="center",fontproperties=FP,fontsize=6,color=GREY)
    items=[(18,"Cruises",66),(48,"Ferry + Denali open",74),(68,"Flightseeing",66),(14,"Remote lodges",84)]
    for x,l,y in items:
        ax.plot([x,x],[y,52],color=GREY,lw=0.8,ls=(0,(2,2)))
        ax.plot(x,y,'o',ms=4,color=INK)
        ax.text(x+1.5,y,l,ha="left",va="center",fontproperties=FP,fontsize=6.5,color=INK)
    ax.text(50,30,"Book left to right. What opens first, sells first.",
            ha="center",fontproperties=FPB,fontsize=7,color=INK)

def build_schematic():
    schematic("denali_road.png",_denali_road,h=1.7)
    schematic("denali_detail.png",_denali_detail,h=1.7)
    schematic("booking_timeline.png",_booking_timeline,h=1.7)

if __name__=="__main__":
    build_geo()
    build_schematic()
    print("done:", len(os.listdir(IMG)), "images")
