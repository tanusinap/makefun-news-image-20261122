#!/usr/bin/env python3
"""Draw the news-image entry: a one-page newspaper summing up the world news
of Sunday 22 November 2026. 35 stories: 3 illustrated leads, 8 illustrated
secondaries, 24 numbered briefs, a UTC timeline and a DATE CHECK box.

Output: entry.png in this directory (PNG, at most 1 MiB, 1024x1024).
Run: python3 draw_news.py
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 233)
INK = (24, 22, 18)
NAVY = (30, 58, 95)
RED = (176, 32, 32)
GOLD = (200, 150, 40)
MUTED = (110, 105, 95)
LINE = (200, 192, 172)
WHITE = (255, 255, 255)
BLUE = (43, 108, 176)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

REGION_COLORS = {
    "ASIA": (190, 90, 30), "EUROPE": (43, 108, 176), "AMERICAS": (60, 140, 90),
    "AFRICA": (150, 110, 30), "MIDDLE EAST": (150, 60, 120), "OCEANIA": (60, 130, 150),
    "GLOBAL": (120, 60, 160),
}

# (region, topic, headline, summary, source)
LEADS = [
    ("MIDDLE EAST", "IRAN WAR", "Iran strikes US assets in Bahrain",
     "IRGC claims missile and drone attack on two US Patriot radars; Bahrain says a civilian site was set ablaze.",
     "REUTERS \u00b7 AP"),
    ("AMERICAS", "CARTELS", "Mexico captures FBI's most-wanted El Chapo Isidro",
     "Fausto Isidro Meza Flores arrested in a Sinaloa raid; gunfights, vehicle fires and road blockades follow.",
     "AP \u00b7 REUTERS"),
    ("EUROPE", "BALTIC", "Russian cargo ship ablaze after drone strike off Finland",
     "Sparta II catches fire in the Gulf of Finland after a suspected Ukrainian drone strike; all 16 crew evacuated.",
     "REUTERS"),
]

SECONDARIES = [
    ("GLOBAL", "CLIMATE", "COP31 nears deal after all-night talks",
     "New package aims to resolve fossil fuel and adaptation finance disputes; president says close to agreement.", "UNFCCC"),
    ("MIDDLE EAST", "GULF", "Two more tankers struck near Hormuz",
     "UK maritime agency reports projectile strikes on tankers leaving the strait; Iran claims a mine hit another.", "REUTERS"),
    ("AMERICAS", "WEATHER", "Florida river breaks 73-year flood record",
     "St. Johns River tops its record near Cocoa after days of rain; flooding may last into January.", "AP"),
    ("ASIA", "CRICKET", "India declare at 720/9, highest on NZ soil",
     "Pant 128 and Rahul 136 power India to a record total in Wellington; lead of 352.", "REUTERS"),
    ("EUROPE", "PROTESTS", "Strasbourg clashes as protests hit sixth week",
     "Masked demonstrators throw fireworks at police; nationwide cost-of-living unrest enters sixth weekend.", "AP"),
    ("AMERICAS", "QUAKE", "6.7 quake shakes Peru's Andes, 15 injured",
     "Magnitude 6.7-6.8 earthquake hits the Jun\u00edn region; no deaths reported.", "USGS"),
    ("MIDDLE EAST", "IRAQ", "Fire at Basra power station kills four",
     "Blaze at the Hartha plant injures 35; cause unknown.", "AP"),
    ("ASIA", "HEALTH", "Toxic alcohol kills 11 in Manipur",
     "More than 180 hospitalised after drinking tainted liquor in northeast India.", "PTI"),
]

BRIEFS = [
    ("Lviv", "Russian strike kills 2, injures 10"),
    ("Geneva", "UN talks fail on killer-robot ban"),
    ("Paris", "France beat Argentina 45-17, reach final"),
    ("Bhopal", "India beat Korea 2-1 in hockey"),
    ("Madrid", "Real Madrid beat Celta 2-1"),
    ("London", "Chelsea routed 1-4 by Leeds"),
    ("Rome", "Roma destroy Parma 5-1"),
    ("Parepare", "PSM hold Persija 1-1"),
    ("New Delhi", "Nepal PM Shah arrives for two-day visit"),
    ("Ottawa", "Canada joins NATO Innovation Fund"),
    ("Naypyitaw", "4.1 quake strikes Myanmar"),
    ("Helsinki", "Orpo: Ukraine war spills into Finland"),
    ("Accra", "Ghana unveils Heritage banknotes"),
    ("Mogadishu", "Al-Shabaab claims deadly ambush"),
    ("Oslo", "Norway court voids disputed oil licences"),
    ("Mekelle", "New Tigray mayor vows elections"),
    ("Niamey", "Sahel states restart ECOWAS dialogue"),
    ("Nairobi", "Kenya secures 293,600 Saudi jobs"),
    ("Indore", "Anupama wins second snooker world title"),
    ("Sydney", "Australia bowl first, Smith out of decider"),
    ("Port-au-Prince", "El Salvador troops reclaim stadium"),
    ("Brussels", "Soil decay may cost EU up to \u20ac509bn"),
    ("New Delhi", "US envoy marks 251st US birthday"),
    ("Abu Dhabi", "UAE president meets US security chief"),
]

BRIEF_REGIONS = [
    "EUROPE", "GLOBAL", "EUROPE", "ASIA",
    "EUROPE", "EUROPE", "EUROPE", "ASIA",
    "ASIA", "AMERICAS", "ASIA", "EUROPE",
    "AFRICA", "AFRICA", "EUROPE", "AFRICA",
    "AFRICA", "AFRICA", "ASIA", "OCEANIA",
    "AMERICAS", "EUROPE", "ASIA", "MIDDLE EAST",
]

TIMELINE = [
    ("OVERNIGHT", "Iran strikes Bahrain"),
    ("MORNING", "Sparta II ablaze"),
    ("04:45 UTC", "El Chapo captured"),
    ("MIDDAY", "COP31 nears deal"),
    ("AFTERNOON", "India 720/9 in Wellington"),
    ("14:30 UTC", "France 45-17 Argentina"),
    ("EVENING", "Strasbourg clashes"),
    ("LATE", "Florida flood record"),
]


def region_counts():
    counts = {}
    for region, *_ in LEADS + SECONDARIES:
        counts[region] = counts.get(region, 0) + 1
    for r in BRIEF_REGIONS:
        counts[r] = counts.get(r, 0) + 1
    return counts


def text_block(draw, x, y, text, fnt, fill, max_w, line_h, max_lines):
    """Draw wrapped text, return the y just below the last line."""
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=1000) or [""])
    wrapped = []
    for ln in lines:
        while draw.textlength(ln, font=fnt) > max_w and len(ln) > 1:
            cut = len(ln) - 1
            while cut > 0 and draw.textlength(ln[:cut], font=fnt) > max_w:
                cut -= 1
            while cut > 0 and ln[cut] != " ":
                cut -= 1
            wrapped.append(ln[:cut].rstrip())
            ln = ln[cut:].strip()
        wrapped.append(ln)
    wrapped = wrapped[:max_lines]
    for i, ln in enumerate(wrapped):
        draw.text((x, y + i * line_h), ln, font=fnt, fill=fill)
    return y + len(wrapped) * line_h


# ---------- illustrations (all drawn in code) ----------

def illo_bahrain(draw, x, y, w, h):
    # night missile strike on Bahrain: dark sky, missile trails, radar base, fire
    draw.rectangle([x, y, x + w, y + h], fill=(20, 18, 35))
    for sx, sy in [(30, 18), (90, 10), (150, 24), (210, 12), (270, 20), (310, 30)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(200, 200, 220))
    # missile trails arcing down
    for mx, my, mlen in [(40, 8, 44), (120, 4, 58), (200, 10, 50), (280, 6, 62)]:
        draw.line([(x + mx, y + my), (x + mx + 14, y + my + mlen)], fill=(255, 200, 90), width=2)
        draw.ellipse([x + mx + 10, y + my + mlen - 4, x + mx + 18, y + my + mlen + 4],
                     fill=(255, 220, 130))
    # radar dishes + base buildings
    for bx in (40, 130, 220):
        draw.rectangle([x + bx, y + h - 30, x + bx + 50, y + h - 10], fill=(80, 80, 100))
    for rx in (65, 155, 245):
        draw.arc([x + rx - 12, y + h - 52, x + rx + 12, y + h - 28], start=180, end=360,
                 fill=(180, 180, 200), width=3)
        draw.line([(x + rx, y + h - 40), (x + rx, y + h - 30)], fill=(180, 180, 200), width=2)
    # explosions
    for ex, ey, r in [(100, h - 34, 12), (220, h - 36, 10)]:
        draw.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r], fill=(255, 150, 40))
        draw.ellipse([x + ex - r // 2, y + ey - r // 2, x + ex + r // 2, y + ey + r // 2],
                     fill=(255, 230, 150))
    draw.rectangle([x + 8, y + 6, x + 190, y + 24], fill=RED)
    draw.text((x + 12, y + 8), "2 PATRIOT RADARS TARGETED", font=font(SANS_B, 9), fill=WHITE)
    draw.text((x + 8, y + h - 18), "BAHRAIN \u00b7 US BASES HIT", font=font(SANS_B, 9), fill=WHITE)


def illo_chapo(draw, x, y, w, h):
    # cartel capture in Sinaloa: desert road, military vehicles, roadblock, smoke
    draw.rectangle([x, y, x + w, y + h], fill=(200, 170, 120))
    # sky
    draw.rectangle([x, y, x + w, y + 50], fill=(180, 200, 230))
    draw.ellipse([x + 260, y + 8, x + 290, y + 38], fill=(255, 240, 180))
    # mountains
    draw.polygon([(x, y + 50), (x + 80, y + 10), (x + 160, y + 50)], fill=(150, 130, 100))
    draw.polygon([(x + 120, y + 50), (x + 200, y + 15), (x + 280, y + 50)], fill=(140, 120, 90))
    # road
    draw.rectangle([x, y + 70, x + w, y + h], fill=(90, 85, 80))
    for lx in range(0, w, 30):
        draw.rectangle([x + lx, y + h // 2 + 15, x + lx + 16, y + h // 2 + 19], fill=(255, 230, 100))
    # military truck
    draw.rectangle([x + 30, y + h - 55, x + 120, y + h - 25], fill=(60, 90, 50))
    draw.rectangle([x + 90, y + h - 70, x + 120, y + h - 55], fill=(60, 90, 50))
    for wx in (45, 75, 100):
        draw.ellipse([x + wx, y + h - 28, x + wx + 12, y + h - 16], fill=(30, 30, 30))
    # burning vehicle (roadblock)
    draw.rectangle([x + 180, y + h - 45, x + 250, y + h - 20], fill=(100, 30, 30))
    for fx, fh in [(190, 28), (210, 38), (230, 30)]:
        draw.polygon([(x + fx, y + h - 45), (x + fx + 10, y + h - 45 - fh),
                      (x + fx + 20, y + h - 45)], fill=(255, 150, 30))
    for sx, sy, r in [(210, 30, 10), (230, 22, 12), (250, 28, 9)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(90, 90, 90))
    draw.rectangle([x + 8, y + 6, x + 180, y + 24], fill=RED)
    draw.text((x + 12, y + 8), "FBI'S MOST-WANTED CAUGHT", font=font(SANS_B, 9), fill=WHITE)
    draw.text((x + 8, y + h - 18), "SINALOA \u00b7 EL CHAPO ISIDRO", font=font(SANS_B, 9), fill=WHITE)


def illo_sparta(draw, x, y, w, h):
    # cargo ship on fire in the Baltic: grey sea, burning vessel, smoke
    draw.rectangle([x, y, x + w, y + h], fill=(100, 120, 140))
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(40, 70, 100))
    # waves
    for wx in range(0, w, 40):
        draw.arc([x + wx, y + h - 28, x + wx + 30, y + h - 12], start=180, end=360,
                 fill=(150, 180, 210), width=2)
    # cargo ship hull
    draw.rectangle([x + 30, y + h - 62, x + 280, y + h - 34], fill=(50, 70, 90))
    draw.rectangle([x + 30, y + h - 62, x + 280, y + h - 56], fill=(120, 120, 130))
    # containers
    for cx, cc in [(50, (200, 60, 40)), (100, (40, 120, 180)), (150, (60, 160, 80)), (200, (200, 150, 40))]:
        draw.rectangle([x + cx, y + h - 84, x + cx + 40, y + h - 62], fill=cc)
    # bridge
    draw.rectangle([x + 240, y + h - 90, x + 270, y + h - 62], fill=(220, 220, 220))
    # flames on containers
    for fx, fh in [(60, 30), (110, 42), (160, 34), (210, 26)]:
        draw.polygon([(x + fx, y + h - 84), (x + fx + 12, y + h - 84 - fh),
                      (x + fx + 24, y + h - 84)], fill=(255, 150, 30))
        draw.polygon([(x + fx + 6, y + h - 84), (x + fx + 12, y + h - 84 - fh + 14),
                      (x + fx + 18, y + h - 84)], fill=(255, 220, 120))
    # smoke
    for sx, sy, r in [(120, 16, 13), (150, 8, 15), (180, 14, 11)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(70, 70, 80))
    draw.text((x + 8, y + 6), "GULF OF FINLAND", font=font(SANS_B, 11), fill=WHITE)
    draw.text((x + 8, y + h - 18), "SPARTA II \u00b7 16 CREW EVACUATED", font=font(SANS_B, 10), fill=GOLD)


def illo_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 80))
    draw.ellipse([x + 12, y + 8, x + 52, y + 48], fill=(60, 160, 220))
    draw.ellipse([x + 22, y + 14, x + 40, y + 30], fill=(90, 180, 90))
    draw.text((x + 66, y + 6), "NEAR DEAL", font=font(SANS_B, 20), fill=WHITE)
    draw.text((x + 66, y + 30), "NEW PACKAGE AFTER ALL-NIGHT TALKS", font=font(SANS_B, 8), fill=(160, 230, 210))
    draw.text((x + 66, y + h - 16), "ANTALYA \u00b7 SECOND OVERTIME DAY", font=font(SANS_B, 9), fill=(160, 230, 210))


def illo_hormuz2(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(35, 55, 85))
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(25, 80, 120))
    draw.text((x + 8, y + 4), "2 TANKERS HIT", font=font(SANS_B, 14), fill=WHITE)
    draw.text((x + 130, y + 4), "STRAIT OF HORMUZ", font=font(SANS_B, 8), fill=GOLD)
    # two tankers
    for tx in (12, 130):
        draw.rectangle([x + tx, y + h - 30, x + tx + 90, y + h - 16], fill=(180, 60, 50))
        draw.rectangle([x + tx + 65, y + h - 42, x + tx + 85, y + h - 30], fill=(200, 200, 200))
        # flame on first tanker
        if tx == 12:
            draw.polygon([(x + tx + 20, y + h - 30), (x + tx + 30, y + h - 48),
                          (x + tx + 40, y + h - 30)], fill=(255, 150, 30))


def illo_florida(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(120, 160, 200))
    draw.text((x + 8, y + 4), "73-YEAR RECORD", font=font(SANS_B, 14), fill=WHITE)
    draw.text((x + 8, y + 22), "ST. JOHNS RIVER", font=font(SANS_B, 9), fill=WHITE)
    # rain (below the text)
    for rx in range(10, w, 25):
        draw.line([(x + rx, y + 36), (x + rx - 5, y + 46)], fill=(200, 220, 245), width=2)
    # houses half-submerged
    for hx in (20, 90, 160):
        draw.rectangle([x + hx, y + h - 30, x + hx + 50, y + h - 8], fill=(200, 180, 140))
        draw.polygon([(x + hx - 4, y + h - 30), (x + hx + 25, y + h - 44),
                      (x + hx + 54, y + h - 30)], fill=(150, 60, 50))
    # flood water
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(40, 90, 140))
    for wx in range(0, w, 30):
        draw.arc([x + wx, y + h - 12, x + wx + 24, y + h - 2], start=180, end=360,
                 fill=(150, 200, 240), width=2)


def illo_india(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 90, 50))
    # cricket bat + ball
    draw.rounded_rectangle([x + 14, y + 8, x + 40, y + 40], radius=4, fill=(220, 190, 130))
    draw.rectangle([x + 24, y + 40, x + 30, y + 52], fill=(180, 150, 100))
    draw.ellipse([x + 52, y + 14, x + 68, y + 30], fill=RED)
    draw.arc([x + 54, y + 16, x + 66, y + 28], start=90, end=270, fill=WHITE, width=1)
    draw.text((x + 82, y + 6), "720/9 DEC", font=font(SANS_B, 18), fill=WHITE)
    draw.text((x + 82, y + 28), "HIGHEST ON NZ SOIL", font=font(SANS_B, 9), fill=(170, 230, 190))
    draw.text((x + 82, y + h - 16), "PANT 128 \u00b7 RAHUL 136", font=font(SANS_B, 9), fill=(170, 230, 190))


def illo_strasbourg(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 60, 80))
    # crowd silhouettes
    for px in (20, 50, 80, 110):
        draw.ellipse([x + px, y + 20, x + px + 14, y + 34], fill=(30, 30, 40))
        draw.rectangle([x + px + 2, y + 34, x + px + 12, y + h - 8], fill=(30, 30, 40))
    # tear gas clouds
    for gx, gy, r in [(160, 20, 12), (185, 14, 14), (210, 22, 10)]:
        draw.ellipse([x + gx - r, y + gy - r, x + gx + r, y + gy + r], fill=(180, 180, 160))
    # fireworks sparks
    for sx, sy in [(150, 40), (170, 48), (190, 38), (205, 50)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 220, 100))
    draw.text((x + 8, y + 4), "6TH WEEKEND", font=font(SANS_B, 14), fill=WHITE)
    draw.text((x + 140, y + h - 16), "STRASBOURG", font=font(SANS_B, 9), fill=(200, 200, 220))


def illo_peru(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(120, 100, 80))
    # Andes mountains
    draw.polygon([(x, y + h), (x + 60, y + 10), (x + 120, y + h)], fill=(100, 80, 60))
    draw.polygon([(x + 80, y + h), (x + 150, y + 20), (x + 220, y + h)], fill=(90, 70, 50))
    # snow caps
    draw.polygon([(x + 50, y + 20), (x + 60, y + 10), (x + 70, y + 20)], fill=WHITE)
    draw.polygon([(x + 140, y + 30), (x + 150, y + 20), (x + 160, y + 30)], fill=WHITE)
    # seismic waves
    for r in (15, 25, 35):
        draw.arc([x + 190 - r, y + h - 20 - r, x + 190 + r, y + h - 20 + r],
                 start=270, end=90, fill=(255, 100, 100), width=2)
    draw.text((x + 8, y + 4), "M6.7", font=font(SANS_B, 20), fill=WHITE)
    draw.text((x + 8, y + 28), "JUN\u00cdN \u00b7 15 INJURED", font=font(SANS_B, 9), fill=(255, 220, 200))


def illo_basra(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 40, 50))
    # power station cooling towers
    for tx in (20, 80):
        draw.polygon([(x + tx, y + h - 8), (x + tx + 8, y + 20), (x + tx + 32, y + 20),
                      (x + tx + 40, y + h - 8)], fill=(150, 150, 160))
        draw.ellipse([x + tx + 8, y + 16, x + tx + 32, y + 24], fill=(120, 120, 130))
    # flames
    for fx, fh in [(140, 28), (165, 38), (190, 30)]:
        draw.polygon([(x + fx, y + h - 8), (x + fx + 12, y + h - 8 - fh),
                      (x + fx + 24, y + h - 8)], fill=(255, 150, 30))
    # smoke
    for sx, sy, r in [(155, 16, 11), (180, 10, 13), (205, 16, 10)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(90, 90, 100))
    draw.text((x + 8, y + 4), "4 DEAD \u00b7 35 HURT", font=font(SANS_B, 12), fill=WHITE)
    draw.text((x + 130, y + h - 16), "HARTHA PLANT", font=font(SANS_B, 9), fill=(200, 200, 220))


def illo_manipur(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 220))
    # bottle with skull warning
    draw.rectangle([x + 20, y + 10, x + 50, y + h - 8], fill=(100, 140, 80))
    draw.rectangle([x + 28, y + 2, x + 42, y + 12], fill=(80, 120, 60))
    draw.ellipse([x + 28, y + 18, x + 42, y + 32], fill=WHITE)
    draw.ellipse([x + 31, y + 22, x + 34, y + 25], fill=INK)
    draw.ellipse([x + 36, y + 22, x + 39, y + 25], fill=INK)
    draw.text((x + 66, y + 6), "11 DEAD", font=font(SANS_B, 20), fill=RED)
    draw.text((x + 66, y + 30), "180+ HOSPITALISED", font=font(SANS_B, 10), fill=INK)
    draw.text((x + 66, y + h - 16), "TOXIC ALCOHOL \u00b7 MANIPUR", font=font(SANS_B, 9), fill=MUTED)


LEAD_ILLOS = [illo_bahrain, illo_chapo, illo_sparta]
SEC_ILLOS = [illo_cop31, illo_hormuz2, illo_florida, illo_india,
             illo_strasbourg, illo_peru, illo_basra, illo_manipur]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((8, 6), "THE WORLD IN ONE DAY", font=font(SANS_B, 12), fill=RED)
    d.text((W - 8, 6), "SUNDAY'S NEWS \u00b7 ONE PAGE \u00b7 35 STORIES",
           font=font(SANS_B, 11), fill=MUTED, anchor="ra")
    d.line([(8, 26), (W - 8, 26)], fill=INK, width=2)
    d.text((8, 30), "Sunday 22 November 2026", font=font(SERIF_B, 54), fill=INK)
    # calendar badge
    d.rectangle([W - 66, 30, W - 8, 84], outline=RED, width=2)
    d.text((W - 37, 32), "22", font=font(SANS_B, 26), fill=RED, anchor="ma")
    d.text((W - 37, 62), "NOV", font=font(SANS_B, 12), fill=RED, anchor="ma")
    d.text((8, 92), "Iran strikes US assets in Bahrain \u00b7 El Chapo Isidro captured \u00b7 COP31 nears a deal",
           font=font(SERIF, 15), fill=RED)
    d.line([(8, 116), (W - 8, 116)], fill=INK, width=2)

    # ---- region bar
    counts = region_counts()
    total = sum(counts.values())
    assert total == 35, f"story count {total} != 35"
    order = ["ASIA", "EUROPE", "AMERICAS", "AFRICA", "MIDDLE EAST", "OCEANIA", "GLOBAL"]
    x = 8
    for region in order:
        label = f"{region} {counts[region]}"
        tw = d.textlength(label, font=font(SANS_B, 10)) + 16
        d.rectangle([x, 118, x + tw, 132], fill=REGION_COLORS[region])
        d.text((x + 8, 119), label, font=font(SANS_B, 10), fill=WHITE)
        x += tw + 2

    # ---- timeline strip (two rows of four)
    d.rectangle([0, 126, W, 164], fill=(235, 230, 215))
    d.text((14, 130), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    for row_i in range(2):
        tx = 130 if row_i == 0 else 14
        ty = 130 if row_i == 0 else 147
        for time, label in TIMELINE[row_i * 4:(row_i + 1) * 4]:
            d.text((tx, ty), time, font=font(SANS_B, 10), fill=RED)
            tw = d.textlength(time, font=font(SANS_B, 10))
            d.text((tx + tw + 5, ty), label, font=font(SANS, 10), fill=INK)
            tx += tw + 5 + d.textlength(label, font=font(SANS, 10)) + 22
    d.line([(0, 164), (W, 164)], fill=LINE, width=1)

    # ---- three leads
    lw = 330
    for i, (region, topic, head, summ, src) in enumerate(LEADS):
        lx = 8 + i * (lw + 4)
        ly = 168
        LEAD_ILLOS[i](d, lx, ly, lw, 120)
        d.text((lx, ly + 124), f"{i + 1}  {region} \u00b7 {topic}",
               font=font(SANS_B, 10), fill=REGION_COLORS[region])
        y = text_block(d, lx, ly + 140, head, font(SERIF_B, 20), INK, lw, 23, max_lines=2)
        text_block(d, lx, y + 2, summ, font(SANS, 12), INK, lw, 15, max_lines=2)
        d.text((lx, 452), src, font=font(SANS_B, 9), fill=MUTED)

    d.line([(8, 460), (W - 8, 460)], fill=INK, width=2)

    # ---- eight secondaries, two rows of four (124px pitch, one-line summaries)
    sw = 248
    for row in range(2):
        for col in range(4):
            i = row * 4 + col
            region, topic, head, summ, src = SECONDARIES[i]
            sx = 8 + col * (sw + 4)
            sy = 464 + row * 124
            SEC_ILLOS[i](d, sx, sy, sw, 58)
            d.text((sx, sy + 62), f"{i + 4}  {region} \u00b7 {topic}",
                   font=font(SANS_B, 9), fill=REGION_COLORS[region])
            y = text_block(d, sx, sy + 76, head, font(SERIF_B, 14), INK, sw, 16, max_lines=2)
            text_block(d, sx, y + 1, summ, font(SANS, 10), MUTED, sw, 13, max_lines=1)

    d.line([(8, 716), (W - 8, 716)], fill=INK, width=2)

    # ---- briefs
    d.text((8, 722), "ALSO ON SUNDAY 22 NOVEMBER", font=font(SANS_B, 12), fill=NAVY)
    bw = 330
    for col in range(3):
        bx = 8 + col * (bw + 6)
        for r in range(8):
            i = col * 8 + r
            place, brief = BRIEFS[i]
            by = 742 + r * 25
            d.text((bx, by), str(12 + i), font=font(SANS_B, 11), fill=REGION_COLORS[BRIEF_REGIONS[i]])
            d.text((bx + 24, by), f"{place}: ", font=font(SANS_B, 11), fill=INK)
            pw = d.textlength(f"{place}: ", font=font(SANS_B, 11))
            text_block(d, bx + 24 + pw, by, brief, font(SANS, 11), INK, bw - 24 - pw, 14, max_lines=1)

    # ---- date check box
    d.rectangle([8, 934, W - 8, 980], outline=RED, width=2)
    d.text((16, 938), "DATE CHECK", font=font(SANS_B, 11), fill=RED)
    dc = ("Left out, first reported on Saturday 21 November: the EU-Indonesia trade deal. "
          "Friday 20 November: Russia's Kyiv barrage \u00b7 Cyclone Akvan \u00b7 the Hormuz tanker \u00b7 COP31's draft \u00b7 Anthropic -6% \u00b7 "
          "Pakistan's Test win \u00b7 Hungary's veto lift. "
          "Thursday 19 November: the Shenzhen summit \u00b7 the ICJ Rohingya judgment \u00b7 Anthropic's IPO \u00b7 GTA VI's launch.")
    text_block(d, 16, 954, dc, font(SANS, 10), INK, W - 32, 13, max_lines=2)

    # ---- footer
    d.text((8, 988), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 PTI \u00b7 ANI \u00b7 USGS \u00b7 UNFCCC \u00b7 WHO",
           font=font(SANS, 9), fill=MUTED)
    d.text((W - 8, 988), "Reads at three sizes: date and leads at thumbnail size \u00b7 all stories at full size.",
           font=font(SANS, 9), fill=MUTED, anchor="ra")

    img.save("entry.png", "PNG", optimize=True)
    print(f"wrote entry.png, size {img.size}, region counts {counts}")


if __name__ == "__main__":
    main()
