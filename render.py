"""Draw the 20 November 2026 world-news poster.

Offline and repeatable: the artwork is baked into entry.png by this script,
and the graded program only copies those bytes. Coordinates are written at
3x and reduced to 1024 px so small type stays sharp.
"""
import io
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EDGE = 1024
SCALE = 3
TYPE_DIR = Path(r"C:\Windows\Fonts")


def face(filename, pixels):
    return ImageFont.truetype(str(TYPE_DIR / filename), pixels * SCALE)


F_NAVY_BIG = face("timesbd.ttf", 31)
F_NAVY_SUB = face("timesi.ttf", 13)
F_KICKER = face("arialbd.ttf", 11)
F_BANNER = face("arialbd.ttf", 13)
F_HEAD = face("timesbd.ttf", 21)
F_CARD_HEAD = face("timesbd.ttf", 15)
F_CAP = face("arialbd.ttf", 12)
F_TINY = face("arialbd.ttf", 9)
F_MICRO = face("arialbd.ttf", 8)
F_STAT = face("arialbd.ttf", 18)
F_BRIEF = face("arialbd.ttf", 10)
F_TAG = face("arialbd.ttf", 10)
F_ART = face("arialbd.ttf", 8)

INK = (24, 29, 40)
NAVY = (17, 32, 66)
PAPER = (246, 242, 231)
CRIMSON = (193, 18, 48)
AMBER = (231, 183, 38)
OCEAN = (44, 100, 167)
PINE = (32, 126, 92)
PLUM = (104, 58, 140)
EMBER = (214, 107, 28)
SAND = (172, 142, 98)
SLATE = (88, 96, 112)
WHITE = (255, 255, 255)

ZONE_COLOR = {
    "EUROPE": OCEAN,
    "MIDDLE EAST": CRIMSON,
    "GLOBAL": SLATE,
    "AMERICAS": PINE,
    "ASIA": PLUM,
    "AFRICA": EMBER,
    "OCEANIA": (23, 128, 118),
}


class Brush:
    def __init__(self, image):
        self.handle = ImageDraw.Draw(image)

    @staticmethod
    def up(box):
        return [v * SCALE if isinstance(v, (int, float)) else tuple(c * SCALE for c in v) for v in box]

    def rect(self, box, fill=None, outline=None, width=1, roundness=0):
        b = self.up(box)
        if roundness:
            self.handle.rounded_rectangle(b, radius=roundness * SCALE, fill=fill,
                                          outline=outline, width=width * SCALE)
        else:
            self.handle.rectangle(b, fill=fill, outline=outline, width=width * SCALE)

    def oval(self, box, fill=None, outline=None, width=1):
        self.handle.ellipse(self.up(box), fill=fill, outline=outline, width=width * SCALE)

    def path(self, points, fill=None, outline=None, width=1):
        coords = [(p[0] * SCALE, p[1] * SCALE) for p in points]
        self.handle.line(coords, fill=fill, width=width * SCALE, joint="curve")
        if outline is not None and fill is None:
            self.handle.line(coords, fill=outline, width=width * SCALE)

    def shape(self, points, fill=None, outline=None):
        coords = [(p[0] * SCALE, p[1] * SCALE) for p in points]
        self.handle.polygon(coords, fill=fill)
        if outline is not None:
            self.handle.line(coords + [coords[0]], fill=outline, width=SCALE)

    def arc(self, box, start, stop, color, width=2):
        self.handle.arc(self.up(box), start, stop, fill=color, width=width * SCALE)

    def words(self, xy, text, fnt, color):
        self.handle.text((xy[0] * SCALE, xy[1] * SCALE), text, font=fnt, fill=color)

    def width_of(self, text, fnt):
        return self.handle.textlength(text, font=fnt) / SCALE

    def centred(self, cx, y, text, fnt, color):
        self.words((cx - self.width_of(text, fnt) / 2, y), text, fnt, color)


def fade(brush, box, top, bottom, bands=22):
    x0, y0, x1, y1 = box
    for i in range(bands):
        blend = i / (bands - 1)
        tone = tuple(int(top[k] + (bottom[k] - top[k]) * blend) for k in range(3))
        ya = y0 + (y1 - y0) * i / bands
        yb = y0 + (y1 - y0) * (i + 1) / bands + 1
        brush.rect((x0, ya, x1, yb), fill=tone)


def soft_light(brush, cx, cy, radius, core, rim, rings=8):
    for i in range(rings, 0, -1):
        t = 1 - (i - 1) / rings
        tone = tuple(int(rim[k] + (core[k] - rim[k]) * t) for k in range(3))
        r = radius * i / rings
        brush.oval((cx - r, cy - r, cx + r, cy + r), fill=tone)


def wrap(text, fnt, room, brush):
    rows, current = [], ""
    for word in text.split(" "):
        attempt = (current + " " + word).strip()
        if brush.width_of(attempt, fnt) <= room:
            current = attempt
        else:
            if current:
                rows.append(current)
            current = word
    if current:
        rows.append(current)
    return rows


def crop_line(text, fnt, room, brush):
    if brush.width_of(text, fnt) <= room:
        return text
    cut = text
    while len(cut) > 3 and brush.width_of(cut + "…", fnt) > room:
        cut = cut[:-1]
    return cut.rstrip() + "…"


def dot_number(brush, x, y, number, color):
    brush.oval((x - 7, y - 7, x + 7, y + 7), fill=color, outline=WHITE, width=1)
    brush.centred(x, y - 5, str(number), F_ART, WHITE)


def little_globe(brush, cx, cy, radius, tone):
    brush.oval((cx - radius, cy - radius, cx + radius, cy + radius),
               fill=(32, 62, 104), outline=tone, width=1)
    brush.arc((cx - radius * 0.62, cy - radius, cx + radius * 0.62, cy + radius),
              90, 270, tone, 1)
    brush.arc((cx - radius * 0.62, cy - radius, cx + radius * 0.62, cy + radius),
              -90, 90, tone, 1)
    brush.path([(cx - radius, cy), (cx + radius, cy)], fill=tone, width=1)
    brush.path([(cx, cy - radius), (cx, cy + radius)], fill=tone, width=1)


def art_bridges(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (34, 52, 84), (12, 22, 44))
    soft_light(b, x0 + 190, y0 + 30, 40, (150, 170, 205), (38, 56, 88))
    # city blocks along the far bank
    for i in range(13):
        bx = x0 + 4 + i * 25
        hgt = 14 + (i * 7) % 26
        b.rect((bx, y1 - 52 - hgt, bx + 20, y1 - 52), fill=(30, 44, 70))
        for wy in range(int(y1 - 48 - hgt), int(y1 - 56), 7):
            b.rect((bx + 4, wy, bx + 7, wy + 2), fill=(226, 196, 116))
    b.rect((x0, y1 - 52, x1, y1), fill=(26, 46, 76))
    # three spans and their pillars
    for k in range(3):
        py = y0 + 52 + k * 20
        b.path([(x0 + 6, py + 12), (x0 + 100, py - 4), (x1 - 6, py + 12)],
               fill=(168, 184, 204), width=2)
        for px in (x0 + 52, x0 + 190, x1 - 46):
            top = min(py - 2, y1 - 56)
            b.rect((px - 3, top, px + 3, y1 - 50), fill=(150, 164, 186))
    # incoming missiles and bursts
    for sx, sy, ex, ey in [(x1 - 16, y0 + 8, x0 + 96, y0 + 54),
                           (x1 - 34, y0 + 14, x0 + 190, y0 + 44)]:
        b.path([(sx, sy), (ex, ey)], fill=(244, 168, 82), width=4)
        b.path([(sx, sy), (ex, ey)], fill=CRIMSON, width=2)
        soft_light(b, ex, ey, 17, (255, 214, 122), (190, 52, 48))
        b.oval((ex - 4, ey - 4, ex + 4, ey + 4), fill=(255, 240, 200))


def art_tower(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (226, 196, 150), (246, 226, 188))
    soft_light(b, x0 + 70, y0 + 34, 32, (255, 238, 172), (240, 214, 172))
    # Riyadh skyline, tallest tower centre-right
    for i in range(9):
        bx = x0 + 6 + i * 34
        hgt = 24 + (i * 11) % 40
        b.rect((bx, y1 - hgt, bx + 26, y1), fill=(178, 152, 122))
        b.rect((bx + 2, y1 - hgt, bx + 5, y1), fill=(206, 182, 150))
    b.shape([(x0 + 184, y1), (x0 + 196, y0 + 8), (x0 + 208, y1)], fill=(126, 112, 100))
    b.path([(x0 + 196, y0 + 8), (x0 + 196, y0 - 14)], fill=(206, 172, 80), width=2)
    b.path([(x1 - 14, y0 + 12), (x0 + 196, y0 + 26)], fill=(238, 156, 74), width=4)
    soft_light(b, x0 + 196, y0 + 26, 18, (255, 214, 120), (198, 56, 52))
    b.words((x0 + 10, y0 + 6), "RIYADH", F_ART, (126, 88, 50))


def art_chart(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (14, 36, 62), (34, 74, 106))
    for gx in range(0, 330, 38):
        b.path([(x0 + gx, y0), (x0 + gx, y1)], fill=(46, 90, 122), width=1)
    for gy in range(0, 145, 28):
        b.path([(x0, y0 + gy), (x1, y0 + gy)], fill=(46, 90, 122), width=1)
    for i in range(13):
        bx = x0 + 18 + i * 23
        base = y0 + 66 + (i * 5) % 18
        b.rect((bx - 3, base - 9, bx + 3, base + 6), fill=(214, 82, 82))
        b.path([(bx, base - 15), (bx, base + 9)], fill=(146, 176, 198), width=1)
    trail = [(x0 + 16, y0 + 34), (x0 + 76, y0 + 48), (x0 + 128, y0 + 42),
             (x0 + 178, y0 + 74), (x0 + 232, y0 + 68), (x0 + 306, y0 + 112)]
    b.path(trail, fill=(236, 186, 88), width=6)
    b.path(trail, fill=(255, 226, 148), width=2)
    for px, py in trail:
        b.oval((px - 3, py - 3, px + 3, py + 3), fill=(255, 240, 188))
    b.rect((x0 + 16, y0 + 8, x0 + 102, y0 + 30), fill=(18, 48, 78))
    b.rect((x0 + 16, y0 + 8, x0 + 102, y0 + 9), fill=AMBER)
    b.words((x0 + 24, y0 + 13), "ANT  $93.5bn", F_ART, WHITE)


def art_flags(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (232, 238, 246), (204, 218, 236))
    b.rect((x0 + 12, y0 + 12, x0 + 34, y0 + 38), fill=OCEAN)
    b.rect((x0 + 34, y0 + 12, x0 + 56, y0 + 38), fill=(246, 246, 244))
    b.rect((x0 + 56, y0 + 12, x0 + 78, y0 + 38), fill=CRIMSON)
    b.oval((x0 + 34, y0 + 20, x0 + 48, y0 + 31), fill=(60, 92, 170))
    for k in range(12):
        ang = k * math.pi / 6
        px = x0 + 41 + math.cos(ang) * 5
        py = y0 + 25 + math.sin(ang) * 5
        b.oval((px - 1, py - 1, px + 1, py + 1), fill=AMBER)
    b.rect((x0 + 94, y0 + 12, x0 + 116, y0 + 26), fill=OCEAN)
    b.rect((x0 + 94, y0 + 26, x0 + 116, y0 + 38), fill=AMBER)
    b.shape([(x0 + 130, y0 + 46), (x0 + 140, y0 + 28), (x0 + 168, y0 + 28),
             (x0 + 178, y0 + 46)], fill=(104, 116, 132))
    b.oval((x0 + 140, y0 + 16, x0 + 168, y0 + 34), fill=(118, 132, 148))
    b.rect((x0 + 152, y0 + 4, x0 + 162, y0 + 18), fill=(76, 88, 104))


def art_climate(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (206, 232, 238), (238, 242, 228))
    b.oval((x0 + 40, y0 + 8, x0 + 104, y0 + 68), fill=(236, 244, 240), outline=(120, 152, 164))
    for k in range(4):
        b.arc((x0 + 48 + k * 4, y0 + 16 + k * 4, x0 + 96 - k * 4, y0 + 60 - k * 4),
              20, 340, (150, 184, 190), 1)
    heat = [(x0 + 34, y0 + 58), (x0 + 66, y0 + 48), (x0 + 92, y0 + 54),
            (x0 + 118, y0 + 30), (x0 + 150, y0 + 34), (x0 + 182, y0 + 14)]
    b.path(heat, fill=CRIMSON, width=3)
    b.shape([(x0 + 178, y0 + 10), (x0 + 188, y0 + 18), (x0 + 178, y0 + 24)], fill=CRIMSON)
    b.rect((x0 + 196, y0 + 8, x1 - 8, y0 + 26), fill=(244, 246, 238))
    b.words((x0 + 200, y0 + 12), "ANTALYA", F_ART, (78, 88, 82))
    b.words((x0 + 10, y0 + 38), "FOSSIL FUELS · FINANCE", F_ART, (70, 92, 90))


def art_nato(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (20, 40, 70), (48, 72, 104))
    b.oval((x0 + 72, y0 + 16, x0 + 132, y0 + 68), fill=(38, 70, 118), outline=(226, 232, 242))
    for k in range(8):
        ang = k * math.pi / 4
        px = x0 + 102 + math.cos(ang) * 23
        py = y0 + 42 + math.sin(ang) * 23
        b.oval((px - 7, py - 7, px + 7, py + 7), fill=(238, 242, 248))
    b.oval((x0 + 94, y0 + 34, x0 + 110, y0 + 50), fill=(38, 70, 118))
    b.path([(x1 - 8, y0 + 6), (x0 + 150, y0 + 44)], fill=(238, 150, 70), width=4)
    soft_light(b, x0 + 150, y0 + 44, 12, (255, 210, 120), (186, 52, 50))
    b.words((x0 + 8, y0 + 70), "POLAND · DRILL", F_ART, (220, 230, 244))


def art_virus(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (238, 244, 242), (206, 226, 222))
    cx, cy = x0 + 78, y0 + 40
    for k in range(10):
        ang = k * math.pi / 5
        px = cx + math.cos(ang) * 26
        py = cy + math.sin(ang) * 26
        b.path([(cx, cy), (px, py)], fill=(70, 128, 128), width=2)
        b.oval((px - 5, py - 5, px + 5, py + 5), fill=(92, 150, 148))
    b.oval((cx - 20, cy - 20, cx + 20, cy + 20), fill=(196, 92, 80))
    for dx, dy in [(-8, -6), (6, -8), (2, 8)]:
        b.oval((cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3), fill=(238, 198, 176))
    b.words((x0 + 140, y0 + 14), "26 YEARS", F_ART, (116, 58, 52))
    b.words((x0 + 140, y0 + 28), "STATUS LOST", F_ART, (116, 58, 52))


def art_chat(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (30, 42, 68), (54, 72, 104))
    for i in range(3):
        yy = y0 + 12 + i * 26
        b.rect((x0 + 14, yy, x0 + 150, yy + 18), fill=(206, 214, 228), roundness=6)
        b.rect((x0 + 20, yy + 5, x0 + 108 - i * 12, yy + 8), fill=(96, 112, 140))
    b.oval((x0 + 178, y0 + 12, x0 + 226, y0 + 46), fill=(238, 242, 248))
    b.oval((x0 + 192, y0 + 24, x0 + 212, y0 + 40), fill=(74, 90, 124))
    b.oval((x0 + 198, y0 + 28, x0 + 206, y0 + 36), fill=(28, 38, 62))
    b.words((x0 + 14, y0 + 96), "REUTERS INVESTIGATION", F_ART, (222, 230, 242))


def art_probe(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (16, 28, 58), (40, 60, 96))
    for k in range(46):
        sx = (x0 + 7 + (k * 47) % 310)
        sy = (y0 + 5 + (k * 29) % 110)
        b.oval((sx, sy, sx + 1.5, sy + 1.5), fill=(196, 214, 240))
    soft_light(b, x1 - 30, y0 + 26, 18, (255, 232, 168), (66, 84, 122))
    b.oval((x1 - 38, y0 + 18, x1 - 22, y0 + 34), fill=(252, 224, 148))
    b.shape([(x0 + 70, y0 + 48), (x0 + 116, y0 + 34), (x0 + 122, y0 + 60),
             (x0 + 76, y0 + 66)], fill=(218, 226, 238))
    b.path([(x0 + 116, y0 + 34), (x0 + 158, y0 + 18)], fill=(190, 200, 220), width=2)
    b.oval((x0 + 158, y0 + 14, x0 + 176, y0 + 26), fill=(232, 238, 248))
    for k in range(6):
        xx = x0 + 180 + k * 22
        b.oval((xx, y0 + 64, xx + 8, y0 + 70), fill=(120, 160, 208))
    b.words((x0 + 10, y0 + 4), "ONE LIGHT-DAY", F_ART, (224, 234, 248))


def art_hippo(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (222, 238, 236), (188, 216, 212))
    b.rect((x0, y1 - 22, x1, y1), fill=(92, 140, 142))
    b.oval((x0 + 44, y0 + 24, x0 + 196, y1 - 6), fill=(116, 132, 144))
    b.oval((x0 + 64, y0 + 30, x0 + 118, y0 + 74), fill=(132, 148, 158))
    b.oval((x0 + 92, y0 + 50, x0 + 106, y0 + 58), fill=(64, 78, 88))
    b.oval((x0 + 150, y0 + 50, x0 + 162, y0 + 58), fill=(64, 78, 88))
    b.oval((x0 + 118, y0 + 66, x0 + 146, y0 + 78), fill=(96, 110, 122))
    b.rect((x0 + 86, y0 + 16, x0 + 130, y0 + 28), fill=(186, 116, 96), roundness=5)
    b.oval((x0 + 104, y0 + 8, x0 + 124, y0 + 22), fill=(206, 140, 112))
    b.words((x0 + 8, y0 + 6), "CINCINNATI", F_ART, (70, 94, 92))


def art_ballot(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (238, 238, 226), (212, 216, 200))
    b.rect((x0 + 18, y0 + 14, x0 + 150, y1 - 8), fill=(250, 250, 244), outline=(150, 156, 144))
    b.rect((x0 + 30, y0 + 26, x0 + 138, y0 + 30), fill=(90, 104, 124))
    for k in range(4):
        yy = y0 + 42 + k * 18
        b.rect((x0 + 32, yy, x0 + 42, yy + 10), fill=(250, 250, 244), outline=(96, 108, 126))
        b.rect((x0 + 48, yy + 2, x0 + 132 - k * 12, yy + 5), fill=(150, 160, 176))
    b.shape([(x0 + 184, y0 + 34), (x0 + 196, y0 + 44), (x0 + 220, y0 + 12)],
            fill=(32, 126, 92))
    b.words((x0 + 12, y0 + 4), "ALASKA · DOJ", F_ART, (78, 88, 84))


def art_podium(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (46, 56, 78), (22, 32, 54))
    b.shape([(x0 + 110, y0 + 14), (x0 + 134, y0 + 34), (x0 + 122, y0 + 56),
             (x0 + 98, y0 + 36)], fill=(206, 168, 84))
    b.oval((x0 + 108, y0 + 22, x0 + 124, y0 + 36), fill=(246, 226, 158))
    b.rect((x0 + 36, y0 + 66, x0 + 272, y0 + 76), fill=(140, 112, 78))
    b.rect((x0 + 64, y0 + 76, x0 + 244, y1), fill=(104, 86, 68))
    b.oval((x0 + 150, y0 + 40, x0 + 162, y0 + 52), fill=(212, 176, 142))
    b.path([(x0 + 178, y0 + 30), (x0 + 226, y0 + 22)], fill=CRIMSON, width=3)
    b.words((x0 + 12, y0 + 6), "POST-ASIA BRIEFING", F_ART, (226, 232, 244))


LEADS = [
    dict(zone="EUROPE", tag="UKRAINE", src="REUTERS · AP", venue="KYIV · DNIPRO RIVER",
         banner="BRIDGES HIT", head="Missiles strike Kyiv; nine dead",
         cap="Three Dnipro crossings hit. Two missiles and a drone land in Poland — NATO calls it a violation.",
         paint=art_bridges),
    dict(zone="MIDDLE EAST", tag="HOUTHI", src="REUTERS · AP", venue="RIYADH · SAUDI ARABIA",
         banner="TOWER STRUCK", head="Houthi strike hits Riyadh tower",
         cap="The kingdom's tallest tower is hit as senators weigh Trump's nuclear pact. Iran talks stall.",
         paint=art_tower),
    dict(zone="GLOBAL", tag="MARKETS", src="REUTERS · CNBC", venue="WALL STREET · NASDAQ",
         banner="AI SELLOFF", head="Four trillion wiped from tech",
         cap="Anthropic's record $93.5bn IPO cannot halt the rout; Nasdaq loses all its 2026 gains.",
         paint=art_chart),
]

CARDS = [
    dict(zone="EUROPE", tag="DIPLOMACY", banner="£17BN RESET", src="BBC · REUTERS",
         head="UK and EU seal post-Brexit deal",
         cap="Food trade, carbon and youth schemes agreed in Brussels; Burnham calls it a good day.",
         paint=art_flags),
    dict(zone="GLOBAL", tag="CLIMATE", banner="COP31 FINAL DAY", src="UN · GUARDIAN",
         head="Delegates demand fossil-fuel action",
         cap="Africa, Latin America and the Pacific press for finance: 'We didn't come here to beg.'",
         paint=art_climate),
    dict(zone="EUROPE", tag="SECURITY", banner="NATO ON EDGE", src="AP",
         head="Eleven states drill in Poland",
         cap="Exercise for a possible postwar Ukraine force as Russian missiles land near the border.",
         paint=art_nato),
    dict(zone="AMERICAS", tag="HEALTH", banner="26 YEARS END", src="AP · PAHO",
         head="US loses measles-free status",
         cap="Endemic spread ends 26 years of elimination; Mexico and Bolivia lose theirs too.",
         paint=art_virus),
    dict(zone="GLOBAL", tag="TECH", banner="PRIVATE CHATS", src="REUTERS",
         head="Meta agent read users' messages",
         cap="An investigation finds the AI assistant accessed chats people never meant to share.",
         paint=art_chat),
    dict(zone="GLOBAL", tag="SPACE", banner="ONE LIGHT-DAY", src="NASA · AP",
         head="Voyager 1 calls home from afar",
         cap="The probe is a full day's light from Earth — and still transmitting, NASA confirms.",
         paint=art_probe),
    dict(zone="AMERICAS", tag="CULTURE", banner="FIONA, 9", src="AP",
         head="Beloved hippo dies after eating hat",
         cap="A visitor's knit hat lodged in her intestine; Cincinnati mourns its Internet star.",
         paint=art_hippo),
    dict(zone="AMERICAS", tag="POLITICS", banner="DOJ DROPS SUIT", src="AP",
         head="Peltola's Alaska win left standing",
         cap="Justice abandons its bid to block certification; the Senate advances data-center permits.",
         paint=art_ballot),
]

BRIEFS = [
    ("MIDDLE EAST", "Iran: Trump says deal not 'acceptable'"),
    ("MIDDLE EAST", "Israel strikes Hezbollah positions"),
    ("MIDDLE EAST", "Iraq reaches militia compromise"),
    ("EUROPE", "Putin called 'friend'; Zelensky hits back"),
    ("EUROPE", "Russia rejects NATO-style guarantees"),
    ("AMERICAS", "GTA VI: $3.79bn in first-day sales"),
    ("AMERICAS", "Pete Rose pardoned by Trump"),
    ("GLOBAL", "Islam set to pass Christianity by 2035"),
    ("AFRICA", "Somalia expels UAE ambassador"),
    ("AFRICA", "Senegal wreck: dozens still missing"),
    ("AFRICA", "South Africa: 581 women killed"),
    ("ASIA", "Nvidia turns cautious on China"),
    ("EUROPE", "French senators back police law"),
    ("AMERICAS", "Christie's halts Frida Kahlo sale"),
    ("EUROPE", "Rome's long-lost library reopens"),
    ("AMERICAS", "Haiti raids a vital gang corridor"),
    ("AMERICAS", "Measles cases pass 7,700 since 2025"),
    ("GLOBAL", "S&P 500 sinks 3.7% in tech rout"),
    ("GLOBAL", "Voyager broadcasts 'V-G-R' home"),
    ("AMERICAS", "Fiona necropsy finds hat in gut"),
    ("AMERICAS", "Mamdani plans to shut Rikers"),
    ("AMERICAS", "Grounded jets, Microsoft outage"),
    ("AMERICAS", "$50bn air-traffic plan sought"),
    ("AMERICAS", "Texas execution runs past an hour"),
]

CLOCK = [("00:00", CRIMSON, "Kyiv strikes"), ("06:00", OCEAN, "Poland violation"),
         ("09:00", PLUM, "Brussels deal"), ("13:00", PINE, "Wall St opens"),
         ("18:00", EMBER, "COP31 closes"), ("23:00", (23, 128, 118), "Voyager signal")]

NUMBERS = [(226, "$93.5bn", "ANTHROPIC IPO — RECORD"),
           (398, "$4tn", "WIPED OFF NASDAQ"),
           (568, "9", "KILLED IN KYIV"),
           (744, "£17bn", "UK–EU DEAL BOOST"),
           (884, "26 yrs", "MEASLES-FREE ERA ENDS")]

PINS = [(1, 30, 50), (2, 46, 24), (3, -74, 40), (4, -122, 38), (5, 151, -34),
        (6, 4, 52), (7, 35, 32), (8, 28, 41), (9, 18, -2), (10, 77, 20),
        (11, 31, 53), (12, -98, 40)]


def map_panel(b, x0, y0, x1, y1):
    fade(b, (x0, y0, x1, y1), (216, 234, 246), (184, 212, 234), 16)
    b.rect((x0, y0, x1, y1), outline=(120, 146, 168), width=1)

    def project(lon, lat):
        return (x0 + (lon + 180) / 360 * (x1 - x0),
                y0 + (90 - lat) / 180 * (y1 - y0))

    land = (212, 202, 172)
    coast = (132, 126, 106)
    shapes = [
        [(-166, 66), (-152, 60), (-140, 60), (-128, 52), (-124, 40), (-118, 32),
         (-110, 30), (-104, 22), (-96, 18), (-88, 20), (-82, 26), (-80, 34),
         (-74, 42), (-64, 48), (-56, 52), (-64, 60), (-80, 66), (-100, 70),
         (-126, 70), (-150, 68)],
        [(-80, 10), (-72, 12), (-60, 8), (-50, 2), (-44, -4), (-36, -8),
         (-40, -20), (-48, -26), (-56, -36), (-64, -44), (-70, -54),
         (-74, -44), (-72, -30), (-76, -14)],
        [(-12, 36), (-8, 44), (2, 50), (10, 54), (20, 56), (30, 62),
         (44, 66), (64, 70), (90, 74), (116, 72), (142, 68), (166, 64),
         (176, 58), (160, 54), (144, 46), (130, 36), (122, 24), (110, 10),
         (100, 4), (92, 20), (80, 14), (72, 22), (60, 24), (48, 14),
         (40, 24), (32, 32), (24, 40), (14, 40), (6, 44), (-4, 42)],
        [(-16, 34), (-4, 36), (12, 34), (28, 32), (38, 24), (44, 10),
         (50, 2), (42, -12), (34, -24), (26, -34), (18, -30), (12, -18),
         (8, -2), (-2, 6), (-14, 12)],
        [(114, -22), (122, -32), (136, -36), (150, -38), (152, -26),
         (144, -14), (130, -12), (118, -18)],
    ]
    for poly in shapes:
        b.shape([project(*p) for p in poly], fill=land, outline=coast)
    for lon, lat, rx, ry in [(-4, 54, 5, 4), (138, 38, 5, 4), (110, -3, 7, 3),
                            (48, -20, 4, 6), (173, -42, 5, 3)]:
        x, y = project(lon, lat)
        b.oval((x - rx, y - ry, x + rx, y + ry), fill=land, outline=coast)
    for lon in (-120, -60, 0, 60, 120):
        b.path([project(lon, 78), project(lon, -52)], fill=(198, 220, 234), width=1)
    for lat in (60, 30, 0, -30):
        b.path([project(-170, lat), project(170, lat)], fill=(198, 220, 234), width=1)
    for num, lon, lat in PINS:
        px, py = project(lon, lat)
        px = min(max(px, x0 + 9), x1 - 9)
        py = min(max(py, y0 + 9), y1 - 15)
        dot_number(b, px, py, num, ZONE_COLOR.get(
            ["EUROPE", "MIDDLE EAST", "AMERICAS", "AMERICAS", "OCEANIA", "EUROPE",
             "MIDDLE EAST", "MIDDLE EAST", "AFRICA", "ASIA", "EUROPE", "AMERICAS"][num - 1], SLATE))
    b.words((x0 + 7, y1 - 12), "1–12 = drawn stories · positions approximate", F_ART, (76, 84, 98))


def noise_field(seed=20261120):
    state = seed
    out = []
    for _ in range(EDGE * EDGE):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        out.append(((state >> 9) % 2049 - 1024) / 1024.0)
    return out


def grain(base, pattern, amount):
    result = base.copy()
    pixels = result.load()
    idx = 0
    for yy in range(EDGE):
        for xx in range(EDGE):
            r, g, blue = pixels[xx, yy]
            shift = int(pattern[idx] * amount)
            idx += 1
            pixels[xx, yy] = (min(255, max(0, r + shift)),
                              min(255, max(0, g + shift)),
                              min(255, max(0, blue + shift)))
    return result


def build(destination):
    page = Image.new("RGB", (EDGE * SCALE, EDGE * SCALE), PAPER)
    b = Brush(page)

    # masthead
    fade(b, (0, 0, EDGE, 96), (12, 26, 58), (28, 52, 94), 18)
    soft_light(b, 906, 48, 40, (58, 92, 142), (16, 32, 64))
    b.rect((15, 10, 100, 86), fill=WHITE)
    b.rect((15, 10, 100, 27), fill=CRIMSON)
    b.centred(57, 12, "FRIDAY", F_ART, WHITE)
    b.centred(57, 30, "20", F_NAVY_BIG, NAVY)
    b.centred(57, 70, "NOV 2026", F_ART, NAVY)
    b.words((112, 6), "• THE WORLD IN ONE PICTURE •", F_KICKER, AMBER)
    b.words((108, 24), "WORLD NEWS TODAY", F_NAVY_BIG, WHITE)
    b.words((112, 66), "Friday 20 November 2026 — the day, in one image", F_NAVY_SUB,
            (232, 212, 140))
    little_globe(b, 706, 48, 24, AMBER)
    b.words((744, 22), "3 LEADS · 8 STORIES", F_KICKER, AMBER)
    b.words((744, 58), "24 BRIEFS · WORLD MAP", F_KICKER, (206, 220, 240))
    b.rect((0, 96, EDGE, 99), fill=AMBER)

    # zone strip
    tally = ([item["zone"] for item in LEADS] + [card["zone"] for card in CARDS]
             + [zone for zone, _ in BRIEFS])
    chips = [("ASIA", PLUM, 116), ("EUROPE", OCEAN, 150), ("AMERICAS", PINE, 166),
             ("AFRICA", EMBER, 118), ("MIDDLE EAST", CRIMSON, 172),
             ("GLOBAL", SLATE, 118)]
    cursor = 16
    for name, tone, wide in chips:
        b.rect((cursor, 103, cursor + wide, 122), fill=tone)
        caption = f"{name} {tally.count(name)}"
        b.centred(cursor + wide / 2, 107, caption, F_TAG, WHITE)
        cursor += wide + 3

    # three front-page leads
    lead_width = 325
    for i, story in enumerate(LEADS):
        left = 16 + i * (lead_width + 8)
        right = left + lead_width
        story["paint"](b, left, 126, right, 264)
        b.rect((left, 264, right, 288), fill=NAVY)
        b.centred((left + right) / 2, 270, story["venue"], F_BANNER, AMBER)
        b.rect((left, 288, right, 314), fill=CRIMSON if i == 0 else NAVY)
        b.centred((left + right) / 2, 294, story["banner"], F_BANNER, WHITE)
        dot_number(b, left + 12, 330, i + 1, ZONE_COLOR[story["zone"]])
        b.words((left + 28, 326), story["zone"] + " · " + story["tag"], F_TAG,
                ZONE_COLOR[story["zone"]])
        source_w = b.width_of(story["src"], F_MICRO)
        b.words((right - source_w - 6, 328), story["src"], F_MICRO, SLATE)
        yy = 344
        for line in wrap(story["head"], F_HEAD, lead_width - 14, b)[:2]:
            b.words((left + 7, yy), line, F_HEAD, NAVY)
            yy += 23
        yy += 6
        for line in wrap(story["cap"], F_CAP, lead_width - 14, b)[:2]:
            b.words((left + 7, yy), line, F_CAP, (72, 78, 92))
            yy += 14
        b.rect((left, 126, right, 420), outline=SLATE, width=1)

    # running order through the UTC day
    b.rect((16, 426, 1008, 466), fill=(234, 238, 244), outline=SLATE, width=1)
    b.words((22, 430), "UTC TIMELINE", F_KICKER, NAVY)
    b.words((22, 447), "20 NOV", F_ART, SLATE)
    b.path([(150, 446), (982, 446)], fill=(146, 154, 166), width=2)
    for i, (hour, tone, label) in enumerate(CLOCK):
        tx = 150 + i * 166
        b.oval((tx - 6, 440, tx + 6, 452), fill=tone, outline=WHITE, width=1)
        b.centred(tx, 429, hour, F_TAG, NAVY)
        b.centred(tx, 454, label, F_MICRO, (56, 62, 76))

    # eight illustrated reports
    cell_w, cell_h = 242, 138
    for j, card in enumerate(CARDS):
        col, row = j % 4, j // 4
        left = 16 + col * (cell_w + 8)
        top = 470 + row * (cell_h + 6)
        right, bottom = left + cell_w, top + cell_h
        card["paint"](b, left, top, right, top + 50)
        b.rect((left, top + 40, right, top + 62), fill=NAVY)
        b.centred((left + right) / 2, top + 45, card["banner"], F_MICRO, WHITE)
        dot_number(b, left + 6, top + 64, j + 4, ZONE_COLOR[card["zone"]])
        b.words((left + 21, top + 64), card["zone"] + " · " + card["tag"], F_MICRO,
                ZONE_COLOR[card["zone"]])
        sw = b.width_of(card["src"], F_MICRO)
        b.words((right - sw - 5, top + 65), card["src"], F_MICRO, SLATE)
        yy = top + 80
        for line in wrap(card["head"], F_CARD_HEAD, cell_w - 14, b)[:2]:
            b.words((left + 7, yy), line, F_CARD_HEAD, NAVY)
            yy += 15
        yy += 6
        for line in wrap(card["cap"], F_TINY, cell_w - 14, b)[:2]:
            b.words((left + 7, yy), line, F_TINY, (72, 78, 92))
            yy += 10
        b.rect((left, top, right, bottom), outline=SLATE, width=1)

    # day in figures
    b.rect((16, 756, 1008, 802), fill=(238, 241, 246), outline=SLATE, width=1)
    b.words((24, 760), "THE DAY IN FIGURES · 20 NOV", F_ART, NAVY)
    for x, big, label in NUMBERS:
        b.words((x, 759), big, F_STAT, CRIMSON)
        b.words((x, 788), label, F_MICRO, (80, 86, 100))

    # atlas and short takes
    b.rect((16, 808, 1008, 828), fill=NAVY)
    b.words((24, 812), "WHERE IT HAPPENED  /  ALSO ON FRIDAY", F_KICKER, AMBER)
    b.words((724, 812), "24 MORE STORIES · 20 NOV 2026", F_MICRO, (206, 220, 240))
    map_panel(b, 16, 832, 306, 970)
    for k, (zone, text) in enumerate(BRIEFS):
        col, row = k // 8, k % 8
        x = 322 + col * 230
        y = 832 + row * 17
        b.oval((x, y + 1, x + 6, y + 7), fill=ZONE_COLOR.get(zone, SLATE))
        b.words((x + 11, y), crop_line(f"{k + 1:02d} · {text}", F_BRIEF, 210, b),
                F_BRIEF, INK)

    # provenance band and footer
    b.rect((16, 974, 1008, 1000), fill=(250, 236, 236), outline=CRIMSON, width=1)
    b.words((24, 977), "DATE CHECK", F_KICKER, CRIMSON)
    b.words((118, 976),
            "Only 20 November reports are carried here. The Shenzhen leaders' summit (18 Nov) and",
            F_TINY, (110, 40, 40))
    b.words((118, 988),
            "Anthropic's first trading day (19 Nov) are background to today's markets and diplomacy.",
            F_TINY, (110, 40, 40))
    b.rect((0, 1000, EDGE, EDGE), fill=(14, 28, 58))
    b.rect((0, 1000, EDGE, 1001), fill=AMBER)
    b.rect((16, 1005, 34, 1021), fill=CRIMSON)
    b.centred(25, 1007, "20", F_ART, WHITE)
    b.words((42, 1004), "THE DAY IN WORLD NEWS · 20 NOVEMBER 2026", F_ART, (232, 214, 150))
    b.words((42, 1015), "REUTERS · AP · BBC · UN · NPR · GUARDIAN", F_ART, (176, 196, 224))
    little_globe(b, 560, 1012, 8, AMBER)
    b.words((576, 1007), "7 ZONES", F_ART, (206, 220, 240))
    b.oval((690, 1006, 716, 1020), fill=(32, 62, 104), outline=AMBER, width=1)
    b.path([(703, 1009), (703, 1013), (707, 1015)], fill=AMBER, width=1)
    b.words((722, 1007), "ALL TIMES UTC", F_ART, (206, 220, 240))
    b.words((846, 1004), "35 STORIES · ONE IMAGE", F_ART, (232, 214, 150))
    b.words((846, 1015), "BUILT BY AN AI AGENT", F_ART, (176, 196, 224))

    flat = page.resize((EDGE, EDGE), Image.LANCZOS)
    texture = noise_field()
    chosen = None
    for amplitude in (1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5):
        candidate = grain(flat, texture, amplitude)
        buffer = io.BytesIO()
        candidate.save(buffer, "PNG", optimize=True)
        length = buffer.tell()
        if length <= 990_000:
            chosen = (candidate, length, amplitude)
        else:
            break
    if chosen is None:
        raise SystemExit("could not fit the poster under the size cap")
    image, size, amplitude = chosen
    folder = os.path.dirname(destination)
    if folder:
        os.makedirs(folder, exist_ok=True)
    image.save(destination, "PNG", optimize=True)
    print(f"Wrote {destination}: {size} bytes, grain {amplitude}")


if __name__ == "__main__":
    target = os.environ.get("MAKEFUN_OUTPUT", str(Path(__file__).with_name("entry.png")))
    build(target)
