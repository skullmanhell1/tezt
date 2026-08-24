#!/usr/bin/env python3
"""
Builds "APEX PREDATOR MMA - Marketing Booklet" as a print-ready A4 PDF.

Subculture: MIXED MARTIAL ARTS (MMA)

Run:  python3 build_mma_booklet.py
Out:  APEX-MMA-Marketing-Booklet.pdf

Photography
-----------
Every photograph in this booklet is a *slot*. Drop your own image into
./photos/ named after the slot code (e.g. photos/hero-01.jpg) and re-run the
script - it will be cropped to fit automatically. Any slot without a file is
drawn as a labelled placeholder frame showing the shot brief, so the layout is
finished before the shoot. Slot codes and briefs live in SHOTS below.
"""
import os
import math
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "APEX-MMA-Marketing-Booklet.pdf")
PHOTOS = os.path.join(HERE, "photos")
BRAND = os.path.join(HERE, "brand")
FONTS = os.path.join(HERE, "fonts")

PW, PH = A4                       # 595.28 x 841.89 pt
M = 44                            # page margin
CW = PW - 2 * M                   # content width = 507.28

# ---------------------------------------------------------------- palette
# Sampled from the APEX PREDATOR MMA cover page.
INK    = (0.031, 0.031, 0.039)    # #08080A  near-black base
INK2   = (0.078, 0.078, 0.090)    # #141417  raised dark panel
PAPER  = (0.961, 0.953, 0.941)    # #F5F3F0  off-white stock
RED    = (0.902, 0.098, 0.122)    # #E6191F  primary accent
RED_HI = (1.000, 0.353, 0.322)    # #FF5A52  highlight
RED_LO = (0.486, 0.039, 0.051)    # #7C0A0D  deep / shadow
SILVER = (0.788, 0.800, 0.824)    # #C9CCD2  brushed silver
GREY   = (0.435, 0.439, 0.467)    # #6F7077
LGREY  = (0.851, 0.839, 0.824)    # #D9D6D2  hairline on paper
DGREY  = (0.220, 0.220, 0.250)    # hairline on dark
WHITE  = (1, 1, 1)

# ---------------------------------------------------------------- type
for _f in ("Anton-Regular", "BarlowCondensed-Bold", "BarlowCondensed-Medium",
           "BarlowCondensed-SemiBold"):
    pdfmetrics.registerFont(TTFont(_f, os.path.join(FONTS, _f + ".ttf")))

DISP = "Anton-Regular"            # display headlines
LBL  = "BarlowCondensed-Bold"     # kickers, tabs, small caps
LBLM = "BarlowCondensed-Medium"   # captions, table labels
LBLS = "BarlowCondensed-SemiBold"
REG  = "Helvetica"                # body
BOLD = "Helvetica-Bold"
OBL  = "Helvetica-Oblique"

# ---------------------------------------------------------------- shot list
# slot code -> (short label, shot brief)
SHOTS = {
    "hero-01":  ("HERO / COVER",
                 "Fighter mid-roundhouse on the pads, shot from low and slightly "
                 "behind, hard rim light from a window or a single LED panel, gym "
                 "dark behind. Underexpose the background by 2 stops."),
    "strip-01": ("HAND WRAPS",
                 "Tight crop on hands being wrapped - the ritual before training. "
                 "Side light, shallow depth of field."),
    "strip-02": ("GLOVE DETAIL",
                 "Worn 4oz gloves resting on the cage or the mat edge. Show the "
                 "scuffs; do not clean them up."),
    "strip-03": ("MAT TEXTURE",
                 "Overhead of the tatami seams and chalk-dusted mat, feet just "
                 "entering frame."),
    "gym-01":   ("THE ROOM",
                 "Wide of the whole gym mid-class, bodies blurred by a slow shutter "
                 "(1/30s) so the room reads busy and alive."),
    "def-01":   ("GRAPPLING",
                 "Two athletes in a clinch or a guard pass. Get low, fill the frame, "
                 "keep both faces partly visible."),
    "def-02":   ("STRIKING",
                 "Pad work with sweat spray caught in the light. Fast shutter "
                 "(1/500s) and a high ISO."),
    "demo-01":  ("THE CLASS",
                 "The whole class lined up at the end of session - deliberately show "
                 "the mixed ages, genders and backgrounds in the room."),
    "demo-02":  ("WOMEN TRAIN",
                 "Female athlete drilling or sparring, framed exactly like the male "
                 "athletes: as an athlete, never as decoration."),
    "belief-01":("THE COACH",
                 "Coach correcting a student's stance mid-round, hand on shoulder. "
                 "Documentary, unposed."),
    "belief-02":("RESPECT",
                 "The glove touch or the bow at the start of a round - the gesture "
                 "that turns violence into sport."),
    "semio-01": ("THE BELT",
                 "Close crop on a worn BJJ belt being tied, frayed and faded. The "
                 "wear is the whole point."),
    "semio-02": ("THE CAGE",
                 "Cage mesh close-up with a fighter soft-focused behind it. Shoot "
                 "through the fence, do not shoot the fence."),
    "mood-01":  ("MOOD / SWEAT",
                 "High-contrast black and white of a fighter's back and shoulders, "
                 "sweat catching the light."),
    "mood-02":  ("MOOD / NIGHT",
                 "Arena or gym lights flaring in the dark - atmosphere, no subject."),
    "mood-03":  ("MOOD / STILL",
                 "A fighter sitting alone on the mat between rounds, head down, "
                 "breathing. The quiet side of the sport."),
    "prod-01":  ("PRODUCT / RASHGUARD",
                 "The APEX rashguard worn and actually trained in - sweat-marked, "
                 "on the mat, not on a hanger."),
    "prod-02":  ("PRODUCT / TEE",
                 "The FIGHT CLUB tee worn outside the gym, street context, so it "
                 "reads as everyday clothing too."),
    "prod-03":  ("PRODUCT / KIT",
                 "Flat lay: gloves, wraps, mouthguard, shorts, rashguard, water "
                 "bottle. Top-down, single soft source."),
    "market-01":("THE WALKOUT",
                 "Fighter walking out under the lights with the brand visible on the "
                 "kit - the moment the logo gets broadcast."),
}

IMGB = lambda n: os.path.join(BRAND, n)


# ---------------------------------------------------------------- helpers
def find_photo(slot):
    """Return the path of a user-supplied photo for this slot, or None."""
    for ext in (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"):
        p = os.path.join(PHOTOS, slot + ext)
        if os.path.exists(p):
            return p
    return None


def cover_reader(path, tw, th, bias=0.42):
    """Centre-crop an image to the target aspect ratio (CSS object-fit: cover)."""
    im = Image.open(path).convert("RGB")
    tr, ir = tw / th, im.width / im.height
    if ir > tr:
        nw = int(im.height * tr)
        left = (im.width - nw) // 2
        im = im.crop((left, 0, left + nw, im.height))
    else:
        nh = int(im.width / tr)
        top = int((im.height - nh) * bias)
        im = im.crop((0, top, im.width, top + nh))
    cap = int(tw * 2.6)
    if im.width > cap:
        im = im.resize((cap, max(1, int(cap / tr))), Image.LANCZOS)
    return ImageReader(im)


def fit_reader(path, maxw, maxh):
    """Scale an image to fit inside a box, return (reader, w, h)."""
    im = Image.open(path).convert("RGB")
    s = min(maxw / im.width, maxh / im.height)
    w, h = im.width * s, im.height * s
    cap = int(w * 2.6)
    if im.width > cap:
        im = im.resize((cap, max(1, int(cap * im.height / im.width))), Image.LANCZOS)
    return ImageReader(im), w, h


def silhouette_reader(path, tint=None, alpha=1.0):
    """An RGBA cut-out, optionally recoloured and faded.

    Kept as RGBA and drawn with mask='auto' so it composites over whatever is
    already on the page - flattening it onto a flat colour would leave a
    visible rectangle wherever the background is a gradient.
    """
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    if tint is not None:
        im = Image.new("RGBA", im.size, tuple(int(c * 255) for c in tint) + (255,))
    if alpha < 1.0:
        a = a.point(lambda v: int(v * alpha))
    im.putalpha(a)
    return ImageReader(im)


def glow_reader(w, h, base, col, power=1.6, cx=0.5, cy=0.5):
    """Radial gradient from `col` at the centre out to `base`, as a flat image."""
    sw, sh = 220, max(1, int(220 * h / w))
    im = Image.new("RGB", (sw, sh))
    px = im.load()
    b = [int(c * 255) for c in base]
    t = [int(c * 255) for c in col]
    fx, fy = cx * sw, cy * sh
    mx = max((fx, sw - fx)) ** 2 + max((fy, sh - fy)) ** 2
    for y in range(sh):
        for x in range(sw):
            d = ((x - fx) ** 2 + (y - fy) ** 2) / mx
            k = max(0.0, 1.0 - d) ** power
            px[x, y] = (int(b[0] + (t[0] - b[0]) * k),
                        int(b[1] + (t[1] - b[1]) * k),
                        int(b[2] + (t[2] - b[2]) * k))
    return ImageReader(im.resize((sw * 3, sh * 3), Image.BICUBIC))


class Book:
    def __init__(self, path):
        self.c = rl_canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("APEX PREDATOR MMA - Marketing Booklet")
        self.c.setAuthor("APEX PREDATOR MMA")
        self.c.setSubject("Marketing booklet - the MMA (mixed martial arts) subculture")
        self.page = 0
        self.dark = False
        self.missing = []

    # ---------- primitives
    def bg(self, col):
        self.c.setFillColorRGB(*col)
        self.c.rect(0, 0, PW, PH, stroke=0, fill=1)

    def rect(self, x, y, w, h, col, alpha=1):
        self.c.saveState()
        self.c.setFillAlpha(alpha)
        self.c.setFillColorRGB(*col)
        self.c.rect(x, y, w, h, stroke=0, fill=1)
        self.c.restoreState()

    def line(self, x, y, w, col=None, lw=0.7, alpha=1):
        col = col or (DGREY if self.dark else LGREY)
        self.c.saveState()
        self.c.setStrokeAlpha(alpha)
        self.c.setStrokeColorRGB(*col)
        self.c.setLineWidth(lw)
        self.c.line(x, y, x + w, y)
        self.c.restoreState()

    def vline(self, x, y, h, col=None, lw=0.7, alpha=1):
        col = col or (DGREY if self.dark else LGREY)
        self.c.saveState()
        self.c.setStrokeAlpha(alpha)
        self.c.setStrokeColorRGB(*col)
        self.c.setLineWidth(lw)
        self.c.line(x, y, x, y + h)
        self.c.restoreState()

    def frame(self, x, y, w, h, col=None, lw=0.7, dash=None, alpha=1):
        col = col or (DGREY if self.dark else LGREY)
        self.c.saveState()
        self.c.setStrokeAlpha(alpha)
        self.c.setStrokeColorRGB(*col)
        self.c.setLineWidth(lw)
        if dash:
            self.c.setDash(dash, 2)
        self.c.rect(x, y, w, h, stroke=1, fill=0)
        self.c.restoreState()

    def mesh(self, x, y, w, h, col=WHITE, alpha=0.05, step=17, lw=0.6):
        """Cage-mesh diagonals, clipped to a box - the brand's signature texture."""
        c = self.c
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0)
        c.setStrokeAlpha(alpha)
        c.setStrokeColorRGB(*col)
        c.setLineWidth(lw)
        n = int((w + h) / step) + 2
        for i in range(-2, n):
            o = i * step
            c.line(x + o, y, x + o - h, y + h)
            c.line(x + o, y, x + o + h, y + h)
        c.restoreState()

    def glow(self, x, y, w, h, base, col, power=1.6, cx=0.5, cy=0.5, alpha=1):
        self.c.saveState()
        self.c.setFillAlpha(alpha)
        self.c.drawImage(glow_reader(w, h, base, col, power, cx, cy), x, y, w, h)
        self.c.restoreState()

    def img_cover(self, path, x, y, w, h, bias=0.42):
        self.c.drawImage(cover_reader(path, w, h, bias), x, y, w, h,
                         preserveAspectRatio=False, anchor="c")

    def img_fit(self, path, x, y, w, h):
        r, iw, ih = fit_reader(path, w, h)
        ox, oy = x + (w - iw) / 2, y + (h - ih) / 2
        self.c.drawImage(r, ox, oy, iw, ih)
        return ox, oy, iw, ih

    # ---------- photo slots
    def photo(self, slot, x, y, w, h, bias=0.42, cap=None, brief=True):
        """Draw a user photo if present, else a labelled placeholder frame."""
        p = find_photo(slot)
        if p:
            self.img_cover(p, x, y, w, h, bias)
        else:
            if slot not in self.missing:
                self.missing.append(slot)
            label, sb = SHOTS.get(slot, (slot.upper(), ""))
            base = INK2 if self.dark else (0.902, 0.894, 0.882)
            self.rect(x, y, w, h, base)
            self.mesh(x, y, w, h, WHITE if self.dark else (0, 0, 0),
                      0.05 if self.dark else 0.035, 15)
            self.frame(x, y, w, h, RED if self.dark else GREY, 0.8,
                       dash=(3, 3), alpha=0.65)
            # camera mark
            mx, my = x + 13, y + h - 17
            self.rect(mx, my, 15, 10.5, RED, 0.95)
            self.rect(mx + 4.6, my + 10.5, 5.6, 2.2, RED, 0.95)
            self.c.saveState()
            self.c.setFillColorRGB(*(base))
            self.c.circle(mx + 7.5, my + 5.2, 3.0, stroke=0, fill=1)
            self.c.restoreState()
            tcol = SILVER if self.dark else (0.35, 0.35, 0.38)
            # keep placeholder copy inside the page margins even on full-bleed slots
            tx = max(x + 34, M)
            tw = min(w - (tx - x) - 12, PW - M - tx)
            self.txt("PHOTOGRAPH " + slot.upper(), tx, y + h - 15.5,
                     LBL, 8.2, RED, space=1.5)
            self.txt(label, tx, y + h - 26, LBLM, 7.6, tcol, space=1.1)
            if brief and h > 88:
                yy = y + h - 45
                for ln in self.wrap(sb, OBL, 7.5, tw):
                    if yy < y + 14:
                        break
                    self.txt(ln, tx, yy, OBL, 7.5, tcol)
                    yy -= 10.4
        if cap:
            self.caption(cap, x, y - 11, w)
        return x, y, w, h

    def caption(self, s, x, y, w):
        col = (0.62, 0.62, 0.66) if self.dark else GREY
        for ln in self.wrap(s, OBL, 7.6, w):
            self.txt(ln, x, y, OBL, 7.6, col)
            y -= 9.8
        return y

    # ---------- type
    def txt(self, s, x, y, font=REG, size=9, col=None, space=0, align="l", alpha=1):
        col = col if col is not None else (PAPER if self.dark else INK)
        c = self.c
        w = pdfmetrics.stringWidth(s, font, size) + space * max(0, len(s) - 1)
        if align == "r":
            x -= w
        elif align == "c":
            x -= w / 2
        c.saveState()
        c.setFillAlpha(alpha)
        c.setFillColorRGB(*col)
        t = c.beginText(x, y)
        t.setFont(font, size)
        if space:
            t.setCharSpace(space)
        t.textOut(s)
        c.drawText(t)
        c.restoreState()
        return w

    def wrap(self, s, font, size, width, space=0):
        words, lines, cur = s.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if pdfmetrics.stringWidth(t, font, size) + space * len(t) <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def para(self, s, x, y, width, font=REG, size=9.3, leading=13.6, col=None, space=0):
        for ln in self.wrap(s, font, size, width, space):
            self.txt(ln, x, y, font, size, col, space)
            y -= leading
        return y

    def bullets(self, items, x, y, width, size=9.1, leading=13.0, gap=5.4,
                col=None, dot=RED, bw=6.0, bh=6.0, indent=15):
        """Square-bulleted list. 'Lead in - rest' sets the lead in bold.

        The wrap is font-aware: each word is measured in the font it will
        actually be drawn in, so a bold lead-in can never push a line past
        the column edge.
        """
        tw = width - indent
        spw = pdfmetrics.stringWidth(" ", REG, size)
        for it in items:
            lead, rest = None, it
            if " \u2014 " in it:
                lead, rest = it.split(" \u2014 ", 1)
            toks = []
            if lead:
                toks += [(w, BOLD) for w in (lead + " \u2014").split()]
            toks += [(w, REG) for w in rest.split()]

            lines, cur, curw = [], [], 0.0
            for t, f in toks:
                wd = pdfmetrics.stringWidth(t, f, size)
                add = wd if not cur else wd + spw
                if cur and curw + add > tw:
                    lines.append(cur)
                    cur, curw = [(t, f)], wd
                else:
                    cur.append((t, f))
                    curw += add
            if cur:
                lines.append(cur)

            first = True
            for ln in lines:
                if first:
                    self.rect(x, y + 1.4, bw, bh, dot)
                    first = False
                cx = x + indent
                for j, (t, f) in enumerate(ln):
                    if j:
                        cx += spw
                    cx += self.txt(t, cx, y, f, size, col)
                y -= leading
            y -= gap
        return y

    def table(self, x, y, cols, rows, head=None, size=8.0, leading=10.8,
              pad=8.5, hsize=7.6, gap=12, tint=None, fonts=None, sizes=None,
              colours=None):
        """Zebra-striped table. `cols` are column widths; row height is
        measured per column in that column's own font, so nothing clips."""
        n = len(cols)
        fonts = fonts or ([LBL] + [REG] * (n - 1))
        sizes = sizes or ([size + 0.5] + [size] * (n - 1))
        colours = colours or ([RED] + [None] * (n - 1))
        tint = tint or (INK2 if self.dark else (0.925, 0.918, 0.906))
        total = sum(cols) + gap * (n - 1)
        xs, cx = [], x
        for w in cols:
            xs.append(cx)
            cx += w + gap

        if head:
            self.rect(x, y - 17, total, 17, INK)
            for i, h in enumerate(head):
                self.txt(h, xs[i] + 7, y - 12, LBL, hsize,
                         PAPER if i else RED_HI, space=1.5)
            y -= 17

        for r, row in enumerate(rows):
            wrapped = [self.wrap(str(c), fonts[i], sizes[i], cols[i] - 14)
                       for i, c in enumerate(row)]
            h = max(len(w) for w in wrapped) * leading + pad
            if r % 2 == 0:
                self.rect(x, y - h, total, h, tint)
            for i, lines in enumerate(wrapped):
                yy = y - pad / 2 - leading + 3.0
                for ln in lines:
                    self.txt(ln, xs[i] + 7, yy, fonts[i], sizes[i], colours[i])
                    yy -= leading
            y -= h
        self.line(x, y, total, RED, 1.2)
        return y

    # ---------- furniture
    def kicker(self, s, x, y, col=RED, size=8.4, font=LBL):
        self.txt(s, x, y, font, size, col, space=2.4)

    def heading(self, s, x, y, size=27, col=None):
        self.txt(s, x, y, DISP, size, col, space=0.2)

    def section_head(self, num, kicker, title, y=PH - 96, col=None, rule=True):
        """Big red section number, kicker, Anton headline, hairline rule."""
        off = 0
        if num:
            self.txt(num, M, y + 24, DISP, 46, RED, space=-0.5)
            off = pdfmetrics.stringWidth(num, DISP, 46) + 18
        self.kicker(kicker, M + off, y + 40)
        self.heading(title, M + off, y + 10, 27, col)
        if rule:
            self.line(M, y - 12, CW)
        return y - 34

    def sub(self, s, x, y, col=None, size=13.5, rule=None):
        """Sub-heading inside a section."""
        self.txt(s, x, y, DISP, size, col, space=0.2)
        if rule:
            self.line(x, y - 7, rule, RED, 1.4)
        return y - 20

    def label(self, s, x, y, col=RED, size=8.2):
        self.txt(s, x, y, LBL, size, col, space=1.9)
        return y - 13

    def panel(self, x, y, w, h, dark=None, mesh=False):
        dark = self.dark if dark is None else dark
        self.rect(x, y, w, h, INK2 if dark else (0.925, 0.918, 0.906))
        if mesh:
            self.mesh(x, y, w, h, WHITE if dark else (0, 0, 0),
                      0.05 if dark else 0.03, 15)
        self.rect(x, y + h - 3, w, 3, RED)
        return x, y, w, h

    def octagon(self, cx, cy, r, col=RED, lw=1.6, fill=False, alpha=1, rot=22.5):
        """The octagon / cage crest - the brand's core mark."""
        pts = [(cx + r * math.cos(math.radians(rot + i * 45)),
                cy + r * math.sin(math.radians(rot + i * 45))) for i in range(8)]
        c = self.c
        c.saveState()
        c.setStrokeAlpha(alpha)
        c.setFillAlpha(alpha)
        c.setStrokeColorRGB(*col)
        c.setFillColorRGB(*col)
        c.setLineWidth(lw)
        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        c.drawPath(p, stroke=0 if fill else 1, fill=1 if fill else 0)
        c.restoreState()

    def claw(self, cx, cy, r, col=None, lw=2.2, alpha=0.9):
        """Three angled slashes - the claw mark inside the crest."""
        col = col if col is not None else (PAPER if self.dark else PAPER)
        c = self.c
        c.saveState()
        c.setStrokeAlpha(alpha)
        c.setStrokeColorRGB(*col)
        c.setLineCap(1)
        for i, o in enumerate((-0.42, 0.0, 0.42)):
            c.setLineWidth(lw * (0.72 if i != 1 else 1.0))
            k = 0.80 if i != 1 else 1.0
            c.line(cx + o * r - 0.30 * r * k, cy - 0.58 * r * k,
                   cx + o * r + 0.30 * r * k, cy + 0.58 * r * k)
        c.restoreState()

    def crest(self, cx, cy, r, ring=RED, alpha=1):
        self.octagon(cx, cy, r, ring, 1.7, False, alpha)
        self.octagon(cx, cy, r * 0.72, ring, 0.8, False, alpha * 0.55)
        self.claw(cx, cy, r * 0.60, alpha=alpha * 0.95)

    def tab(self, label):
        """Vertical red section tab on the outer edge."""
        c = self.c
        h = 176
        y0 = PH / 2 - h / 2
        self.rect(PW - 20, y0, 7, h, RED)
        c.saveState()
        c.translate(PW - 26, y0)
        c.rotate(90)
        c.setFillColorRGB(*(SILVER if self.dark else GREY))
        t = c.beginText(0, 0)
        t.setFont(LBL, 7.6)
        t.setCharSpace(2.2)
        t.textOut(label.upper())
        c.drawText(t)
        c.restoreState()

    def footer(self, label):
        col = (0.55, 0.55, 0.60) if self.dark else GREY
        self.line(M, 48, CW)
        self.rect(M, 32, 6, 6, RED)
        self.txt("APEX PREDATOR MMA", M + 13, 33.6, LBL, 8, col, space=1.4)
        self.txt(label.upper(), PW / 2, 33.6, LBLM, 8, col, space=1.4, align="c")
        self.txt("PAGE %d" % self.page, PW - M, 33.6, LBLM, 8, col,
                 space=1.4, align="r")

    def strip(self, y, h=21, text="DISCIPLINE. STRENGTH. HONOR.", col=RED,
              tcol=WHITE):
        self.rect(0, y, PW, h, col)
        self.txt(text, PW / 2, y + h / 2 - 3.2, LBL, 9, tcol, space=3.4,
                 align="c")

    def new(self, dark=False):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.dark = dark
        self.bg(INK if dark else PAPER)

    def save(self):
        self.c.save()



b = Book(OUT)
COLW = (CW - 27) / 2          # two-column width = 240.14
C3 = (CW - 2 * 20) / 3        # three-column width = 155.76

# =====================================================================
# 1 - COVER
# =====================================================================
b.new(dark=True)
b.glow(0, 0, PW, PH, INK, (0.115, 0.016, 0.024), power=2.0, cx=0.5, cy=0.42)
b.mesh(0, 0, PW, PH, WHITE, 0.055, 19)

b.strip(808, 34, "DISCIPLINE.  STRENGTH.  HONOR.", RED, WHITE)
b.txt("MARKETING BOOKLET   \u00b7   SUBCULTURE RESEARCH   \u00b7   2026",
      M, 776, LBL, 8.6, SILVER, space=2.6)

b.photo("hero-01", 0, 556, PW, 204, bias=0.34)
b.rect(0, 552, PW, 2.2, RED)

b.txt("APEX PREDATOR", M - 2, 496, DISP, 68, PAPER, space=0.4)
b.txt("MMA", M - 2, 396, DISP, 112, RED, space=0.4)

b.txt("FIGHT CLUB", 288, 452, DISP, 34, SILVER, space=0.6)
b.txt("TRAINING \u00b7 SPARRING \u00b7 FIGHT NIGHTS", 288, 432, LBL, 8.2,
      RED, space=1.5)
b.crest(PW - M - 32, 440, 32)

b.rect(M, 368, 186, 4, PAPER)
b.txt("WHERE LEGENDS ARE MADE.", M, 346, LBL, 11.5, PAPER, space=2.8)

b.rect(M, 244, 4, 80, RED)
b.txt("A fight-wear brand built for the", M + 18, 300, DISP, 20, PAPER, space=0.2)
b.txt("mixed martial arts subculture.", M + 18, 276, DISP, 20, PAPER, space=0.2)
b.txt("Product line: FIGHT CLUB \u2014 rashguards, shorts, tees, gloves.",
      M + 18, 254, REG, 9.2, (0.70, 0.70, 0.74))

sw = (CW - 18) / 3
for i, s in enumerate(("strip-01", "strip-02", "strip-03")):
    b.photo(s, M + i * (sw + 9), 112, sw, 100)

b.txt("SUBCULTURE", M, 88, LBL, 8, RED, space=2.2)
b.txt("MMA \u00b7 MIXED MARTIAL ARTS", M, 72, LBLM, 9.6, PAPER, space=1)
b.txt("DESIGNER", PW - M, 88, LBL, 8, RED, space=2.2, align="r")
b.txt("@apexmma  \u00b7  ISSUE 01 / 2026", PW - M, 72, LBLM, 9.6, PAPER,
      space=1, align="r")
b.line(M, 54, CW, (0.30, 0.30, 0.34))

# =====================================================================
# 2 - CONTENTS
# =====================================================================
b.new()
y = b.section_head("", "MARKETING BOOKLET", "CONTENTS")
y = b.para(
    "This booklet presents APEX PREDATOR MMA \u2014 a fight-wear brand designed and marketed to the "
    "mixed martial arts subculture. It works through the research into the group, the meaning "
    "carried by their signs and symbols, the development of the design, and the plan for selling "
    "it to them.", M, y - 4, CW * 0.80, REG, 9.6, 14.2)

rows = [("01", "Introduction / About the Brand", "3"),
        ("02", "The Subculture \u2014 Definition", "4"),
        ("03", "The Subculture \u2014 Demographics", "5"),
        ("04", "Shared Interests, Activities & Values", "6"),
        ("05", "Shared Lifestyle & Attitudes", "7"),
        ("06", "Semiotics \u2014 Signs & Symbols", "8"),
        ("07", "Semiotics \u2014 Meaning & Misreading", "9"),
        ("08", "Mood Board", "10"),
        ("09", "Ideation \u2014 Brainstorm, Mind Map & Thumbnails", "11"),
        ("10", "The Product \u2014 Design System", "12"),
        ("11", "Photography Plan & Contact Sheet", "13"),
        ("12", "Marketability \u2014 Who Buys It", "14"),
        ("13", "Marketing Plan \u2014 How We Reach Them", "15"),
        ("14", "Conclusion / Call to Action", "16")]

y -= 22
for n, t, p in rows:
    b.txt(n, M, y, LBL, 11, RED, space=1)
    b.txt(t, M + 32, y, REG, 10.2, INK)
    b.txt(p, PW - M, y, LBL, 11, INK, align="r")
    b.line(M, y - 7.5, CW, LGREY, 0.5)
    y -= 21

b.photo("gym-01", M, 176, CW, 140, cap="The room the whole brand is built around: "
        "a suburban MMA gym mid-session. Every photograph in this booklet is shot on "
        "location in a working gym rather than a studio.")
b.footer("Contents")


# =====================================================================
# 3 - 01 INTRODUCTION / ABOUT THE BRAND
# =====================================================================
b.new()
y = b.section_head("01", "SECTION", "INTRODUCTION / ABOUT")
CX2 = M + COLW + 27

yy = b.para(
    "APEX PREDATOR MMA is a fight-wear and training-gear brand built for one group of people: "
    "the mixed martial arts subculture. Its range is called FIGHT CLUB \u2014 rashguards, shorts, "
    "tees and gloves designed to be trained in rather than posed in.",
    M, y - 4, COLW, REG, 9.4, 13.8)
b.para(
    "The name does two jobs at once. An apex predator sits at the top of the food chain, which "
    "is exactly how a fighter is taught to think about a division. \u201cApex\u201d is also the highest "
    "point of a climb \u2014 the peak you train towards.",
    M, yy - 8, COLW, REG, 9.4, 13.8)

yy = b.para(
    "The brand exists because fight gear sits in an awkward gap. Mainstream sportswear treats "
    "fighters as an afterthought: seams in the wrong place for grappling, sizing cut for runners, "
    "and graphics drawn by people who have never been tapped.",
    CX2, y - 4, COLW, REG, 9.4, 13.8)
b.para(
    "The specialist fight labels understand the sport but often look crude \u2014 skulls, flames, "
    "barbed wire, gothic type. APEX aims at the space between the two: real technical credibility "
    "with a design language a 22-year-old would actually wear on the street.",
    CX2, yy - 8, COLW, REG, 9.4, 13.8)

# --- the range
b.panel(M, 392, CW, 132)
b.txt("THE RANGE", M + 16, 494, DISP, 15, INK, space=0.2)
b.txt("INDICATIVE RRP", PW - M - 16, 496, LBL, 7.8, GREY, space=1.8, align="r")
b.line(M + 16, 484, CW - 32, LGREY, 0.6)

pw4 = (CW - 32 - 3 * 16) / 4
items = [("01", "RASHGUARD", "$79",
          "Sublimated print, flatlock seams, four-way stretch. The core identity piece."),
         ("02", "FIGHT SHORTS", "$69",
          "Split hem and silicone waist grip. Built to kick in without riding up."),
         ("03", "TEE / HOODIE", "$45 / $95",
          "Heavyweight cotton. The off-mat, street-facing half of the brand."),
         ("04", "4OZ GLOVES", "$89",
          "Moulded foam, thumb lock. The entry purchase for a new member.")]
for i, (n, nm, pr, dsc) in enumerate(items):
    x = M + 16 + i * (pw4 + 16)
    b.txt(n, x, 464, LBL, 8.4, RED, space=1.6)
    b.txt(nm, x, 449, DISP, 12.5, INK, space=0.2)
    b.txt(pr, x, 434, LBL, 9.4, RED, space=1)
    b.para(dsc, x, 420, pw4, REG, 7.9, 10.8, GREY)

sw2 = (CW - 18) / 2
ph3 = 392 - 34 - 152
b.photo("prod-03", M, 152, sw2, ph3)
b.photo("prod-01", M + sw2 + 18, 152, sw2, ph3)
b.caption("Left: the full FIGHT CLUB kit shot flat. Right: the rashguard photographed after "
          "a session rather than on a hanger \u2014 the subculture reads worn-in gear as proof "
          "the brand is actually used.", M, 140, CW)
b.tab("01 \u00b7 Introduction")
b.footer("Introduction / About")

# =====================================================================
# 4 - 02 THE SUBCULTURE: DEFINITION
# =====================================================================
b.new()
y = b.section_head("02", "SUBCULTURE RESEARCH", "DEFINITION OF THE GROUP")

y = b.para(
    "Mixed martial arts is a full-contact combat sport that allows both striking and grappling, "
    "standing up and on the ground. It draws its techniques from boxing, Muay Thai, kickboxing, "
    "wrestling, Brazilian jiu-jitsu, judo and sambo, then tests them against each other inside "
    "a fenced cage.", M, y - 4, CW, REG, 9.6, 14.0)

y = b.para(
    "The MMA subculture is the community that has grown around that sport, and it is far wider "
    "than the people who actually compete. Most members will never take a professional fight. It "
    "is made up of hobbyists who turn up four nights a week, amateur competitors, coaches and "
    "referees, and fans who will happily argue about a guard pass for an hour. What separates it "
    "from ordinary sports fandom is that membership is proven by participation \u2014 you are in it "
    "because you train, not because you bought a ticket. It should not be confused with gym or "
    "bodybuilding culture, which is organised around how a body looks rather than what it can do, "
    "nor with traditional martial arts, where forms and grading can matter more than live sparring.",
    M, y - 10, CW, REG, 9.6, 14.0)

y = b.sub("WHAT MAKES IT DIFFERENT FROM THE WIDER CULTURE", M, y - 16, rule=CW)

left = ["Consented violence \u2014 the wider culture is organised around avoiding physical "
        "confrontation. This one deliberately seeks it, under strict rules, and treats it as the "
        "most honest test of a person available.",
        "Earned status \u2014 no amount of money, followers or talk moves you up. A blue belt beats "
        "a beginner every time, and everyone in the room knows it.",
        "Public losing \u2014 a hobbyist is submitted by training partners several times a week. "
        "Elsewhere failure is hidden; here it is timetabled, witnessed and treated as information."]
right = ["Closeness with strangers \u2014 grappling needs a level of body contact the wider culture "
         "reserves for intimacy or medicine. On the mat it is completely unremarkable.",
         "Chosen hardship \u2014 weight cuts, 6am runs, ice baths, no alcohol during camp. "
         "Discomfort is not endured here, it is sought out on purpose.",
         "The body keeps the record \u2014 cauliflower ear, taped fingers, scar tissue. Members "
         "carry permanent, visible proof of belonging."]
e1 = b.bullets(left, M, y - 4, COLW, size=8.9, leading=12.5, gap=6.5)
e2 = b.bullets(right, CX2, y - 4, COLW, size=8.9, leading=12.5, gap=6.5)

ph4 = min(e1, e2) - 26 - 152
b.photo("def-01", M, 152, sw2, ph4)
b.photo("def-02", M + sw2 + 18, 152, sw2, ph4)
b.caption("The two halves of the sport in one spread: grappling (left) and striking (right). "
          "Almost every visual signal the subculture uses comes out of one of these two worlds.",
          M, 140, CW)
b.tab("02 \u00b7 Subculture Research")
b.footer("Definition of the Group")

# =====================================================================
# 5 - 03 THE SUBCULTURE: DEMOGRAPHICS
# =====================================================================
b.new()
y = b.section_head("03", "SUBCULTURE RESEARCH", "DEMOGRAPHICS OF THE GROUP")

y = b.para(
    "Who is actually in the room. The figures below are indicative estimates drawn from gym-level "
    "observation, promotion audience reporting and participation data rather than a formal survey, "
    "so they are given as ranges.", M, y - 4, CW, REG, 9.6, 14.0)

# --- stats strip
sy, shh = y - 74, 66
b.rect(M, sy, CW, shh, INK)
b.mesh(M, sy, CW, shh, WHITE, 0.07, 15)
stats = [("18\u201329", "CORE TRAINING AGE"), ("~75%", "MALE PARTICIPATION"),
         ("4\u20136", "SESSIONS PER WEEK"), ("40+", "COUNTRIES WITH PRO CARDS")]
scw = CW / 4
for i, (big, lab) in enumerate(stats):
    cx = M + i * scw + scw / 2
    b.txt(big, cx, sy + 30, DISP, 26, RED if i % 2 == 0 else PAPER, space=0.2, align="c")
    b.txt(lab, cx, sy + 14, LBL, 7.6, (0.62, 0.62, 0.66), space=1.6, align="c")
    if i:
        b.vline(M + i * scw, sy + 12, shh - 24, (0.28, 0.28, 0.32), 0.6)

BLOCKS = [
    ("AGE", "What age group are they mostly?",
     "The training population is young. The core sits at 18\u201329, inside a broader active range of "
     "16\u201334. Under-16s arrive through kids' and teens' programs, now a major part of most gyms' "
     "income, and masters divisions keep competitors going well past 35. Spectatorship skews a "
     "little older than participation, roughly 18\u201344, because watching costs far less time than "
     "training does. APEX targets 16\u201328: old enough to buy their own gear, young enough to still "
     "be building an identity around the gym."),
    ("GENDER", "Is it mainly male, female, or mixed?",
     "Still majority male \u2014 around three-quarters of gym membership and a similar share of the "
     "audience. But women's participation is the fastest-growing part of the sport, pushed along by "
     "athletes such as Ronda Rousey, Amanda Nunes, Zhang Weili and Alexa Grasso, and by women "
     "entering through self-defence and fitness classes rather than competition. Most fight labels "
     "still treat women's kit as a shrunken, pinker version of the men's. That is an obvious gap, "
     "and APEX is built to fill it."),
    ("NATIONALITY", "Where are they from?",
     "Global, with clear strongholds: the United States, Brazil, Russia and Dagestan, Japan, "
     "Thailand, Ireland, England, Poland, Mexico, Kazakhstan, and Australia and New Zealand. In "
     "Australia the sport is concentrated in the outer suburbs of Sydney, Melbourne, Brisbane and "
     "Perth, and Australian gyms punch well above their weight internationally. APEX is positioned "
     "as an Australian brand that still reads as globally credible."),
    ("CULTURAL IDENTITY", "What backgrounds or influences do they have?",
     "MMA is multicultural by construction: its techniques come from Brazil, Japan, Thailand, the "
     "United States and Russia, and the gym's vocabulary borrows with them \u2014 oss, mongkhon, "
     "kimura, sambo. Australian gyms are among the most mixed rooms you will find, with Pacific "
     "Islander, Maori, Lebanese, Vietnamese, Sudanese and Anglo-Australian athletes on one mat. "
     "Dagestani and wider Muslim influence has made prayer and fasting normal in elite camps, and "
     "the culture keeps deep working-class roots."),
]

# --- four blocks on a fixed 2 x 2 grid, so nothing can collide with the photos
LIM, BLEAD = 9, 12.2                      # max body lines per block
yh1 = sy - 24
yh2 = yh1 - 34 - LIM * BLEAD - 18
for i, (h, q, txt) in enumerate(BLOCKS):
    x = M if i % 2 == 0 else CX2
    yh = yh1 if i < 2 else yh2
    n = len(b.wrap(txt, REG, 8.7, COLW))
    if n > LIM:
        print("  ! p5 overflow: %-18s %d lines (max %d)" % (h, n, LIM))
    b.txt(h, x, yh, DISP, 15, INK, space=0.2)
    b.line(x, yh - 7, COLW, RED, 1.4)
    b.txt(q, x, yh - 20, OBL, 8.1, GREY)
    b.para(txt, x, yh - 34, COLW, REG, 8.7, BLEAD)

ph5 = (yh2 - 34 - LIM * BLEAD - 20) - 152
b.photo("demo-01", M, 152, sw2, ph5)
b.photo("demo-02", M + sw2 + 18, 152, sw2, ph5)
b.caption("Shooting the class as it actually is \u2014 mixed ages, genders and backgrounds \u2014 does "
          "more marketing work than any slogan, because the target buyer recognises their own room.",
          M, 140, CW)
b.tab("03 \u00b7 Subculture Research")
b.footer("Demographics of the Group")

# =====================================================================
# 6 - 04 SHARED INTERESTS, ACTIVITIES & VALUES
# =====================================================================
b.new()
y = b.section_head("04", "SUBCULTURE RESEARCH", "INTERESTS, ACTIVITIES & VALUES")

y = b.para(
    "What the members of this subculture actually have in common \u2014 the things they do together, "
    "and the ideas they agree on. These are the hooks a brand can legitimately hang itself on.",
    M, y - 4, CW, REG, 9.6, 14.0)

ya = b.sub("HOBBIES & ACTIVITIES", M, y - 16, rule=COLW)
b.bullets([
    "Training \u2014 four to six sessions a week across striking, grappling and strength, plus open "
    "mats at the weekend.",
    "Competing \u2014 amateur \u201csmokers\u201d, BJJ tournaments, Muay Thai interclubs and local fight cards.",
    "Watching together \u2014 UFC and ONE cards are social events, watched in groups at odd hours "
    "because of time zones.",
    "Analysis \u2014 breaking fights down frame by frame, technique channels, podcasts and coaches' "
    "breakdowns.",
    "Gear \u2014 comparing gloves, shin pads, rashguards and mouthguards is a hobby in its own right.",
    "Recovery \u2014 ice baths, saunas, physio, macro tracking and managing weight.",
], M, ya - 2, COLW, size=8.8, leading=12.3, gap=6.0)

yb = b.sub("VALUES & BELIEFS", CX2, y - 16, rule=COLW)
e2 = b.bullets([
    "Respect \u2014 touch gloves, shake hands, thank your partner, and protect them in sparring.",
    "Leave your ego at the door \u2014 being beaten is data, not humiliation.",
    "Discipline over motivation \u2014 turning up when you do not feel like it is the entire skill.",
    "Meritocracy \u2014 rank is demonstrated, never claimed. The mats settle it.",
    "Controlled aggression \u2014 violence has a place, a time and a rule set. Fighters are often the "
    "calmest people outside it.",
    "Loyalty and lineage \u2014 you represent a gym and a coach, and you say whose student you are.",
    "Self-mastery \u2014 the real opponent is your own comfort.",
], CX2, yb - 2, COLW, size=8.8, leading=12.3, gap=6.0)

# --- pull quote + photo, anchored to the base line so no dead space is left
qy = 152
qh = e2 - 26 - qy
b.rect(M, qy, COLW, qh, INK)
b.mesh(M, qy, COLW, qh, WHITE, 0.07, 14)
b.rect(M, qy + qh - 3, COLW, 3, RED)
qm = qy + qh / 2                       # vertically centre the quote block
b.txt("\u201cLEAVE YOUR", M + 16, qm + 30, DISP, 23, PAPER, space=0.2)
b.txt("EGO AT THE", M + 16, qm + 6, DISP, 23, PAPER, space=0.2)
b.txt("DOOR.\u201d", M + 16, qm - 18, DISP, 23, RED, space=0.2)
b.txt("THE MOST REPEATED LINE IN ANY GYM", M + 16, qm - 40, LBL, 7.6,
      (0.62, 0.62, 0.66), space=1.5)
b.photo("belief-02", CX2, qy, COLW, qh)
b.caption("The glove touch: the gesture that converts a fight into a sport, and the single most "
          "useful image the brand has.", CX2, qy - 11, COLW)
b.tab("04 \u00b7 Subculture Research")
b.footer("Interests, Activities & Values")

# =====================================================================
# 7 - 05 SHARED LIFESTYLE & ATTITUDES
# =====================================================================
b.new()
y = b.section_head("05", "SUBCULTURE RESEARCH", "LIFESTYLE & ATTITUDES")

y = b.para(
    "How belonging to this subculture actually shapes a week, a body and a set of opinions. This is "
    "the part a brand has to get right, because the audience can smell an outsider instantly.",
    M, y - 4, CW, REG, 9.6, 14.0)

y = b.sub("LIFESTYLE & ATTITUDES", M, y - 16, rule=CW)
lifeL = ["Built around the timetable \u2014 meals, sleep and social life bend to the training "
         "schedule, not the other way around.",
         "Sacrifice is normal \u2014 diet, alcohol and late nights go first, and weight cuts before "
         "competition are brutal and accepted.",
         "Pain is reframed \u2014 soreness is expected, injuries become stories, and strapping tape "
         "is everyday equipment."]
lifeR = ["Function over fashion on the mat \u2014 but strong loyalty to labels seen as legitimate, "
         "and instant contempt for the rest.",
         "Zero tolerance for fakes \u2014 poseurs, gym-only tough guys and McDojo black belts are the "
         "culture's favourite target. Authenticity is the highest currency there is.",
         "The gym as therapy \u2014 one of the most commonly stated reasons for training is managing "
         "stress, anger and anxiety."]
ey1 = b.bullets(lifeL, M, y - 4, COLW, size=8.9, leading=12.5, gap=6.5)
ey2 = b.bullets(lifeR, CX2, y - 4, COLW, size=8.9, leading=12.5, gap=6.5)

# --- a training week
wy = b.sub("A TRAINING WEEK \u2014 THE COMMITTED HOBBYIST", M, min(ey1, ey2) - 12, rule=CW)
WEEK = [("MON", [("RUN 6AM", GREY), ("MUAY THAI", RED)]),
        ("TUE", [("S&C", GREY), ("BJJ \u00b7 GI", INK)]),
        ("WED", [("MMA SPAR", RED)]),
        ("THU", [("RUN 6AM", GREY), ("MUAY THAI", RED)]),
        ("FRI", [("BJJ \u00b7 NO-GI", INK)]),
        ("SAT", [("OPEN MAT", INK)]),
        ("SUN", [("RECOVERY", None)])]
gapw, nday = 5.0, 7
dw = (CW - gapw * (nday - 1)) / nday
top = wy - 6
for i, (day, chips) in enumerate(WEEK):
    x = M + i * (dw + gapw)
    b.rect(x, top - 15, dw, 15, INK2 if False else (0.90, 0.893, 0.881))
    b.txt(day, x + dw / 2, top - 11, LBL, 8.2, INK, space=1.4, align="c")
    cy = top - 15 - 4
    for lab, col in chips:
        if col is None:
            b.frame(x, cy - 19, dw, 19, LGREY, 0.8, dash=(2, 2))
            b.txt(lab, x + dw / 2, cy - 12.5, LBL, 7.2, GREY, space=0.8, align="c")
        else:
            b.rect(x, cy - 19, dw, 19, col)
            b.txt(lab, x + dw / 2, cy - 12.5, LBL, 7.2, PAPER, space=0.8, align="c")
        cy -= 23
legy = top - 15 - 4 - 2 * 23 - 12
for i, (lab, col) in enumerate([("STRIKING", RED), ("GRAPPLING", INK),
                                ("STRENGTH / RUNNING", GREY), ("REST", None)]):
    lx = M + i * 128
    if col is None:
        b.frame(lx, legy, 9, 9, LGREY, 0.8, dash=(2, 2))
    else:
        b.rect(lx, legy, 9, 9, col)
    b.txt(lab, lx + 14, legy + 1.6, LBLM, 7.6, GREY, space=1.2)

b.photo("belief-01", M, 152, CW, legy - 26 - 152)
b.caption("Coaching mid-round. The relationship between coach and student is the emotional centre "
          "of the subculture, and the reason gym-level endorsement outperforms paid advertising.",
          M, 140, CW)
b.tab("05 \u00b7 Subculture Research")
b.footer("Lifestyle & Attitudes")


# =====================================================================
# 8 - 06 SEMIOTICS: SIGNS & SYMBOLS
# =====================================================================
b.new()
y = b.section_head("06", "SEMIOTIC INVESTIGATION", "SIGNS & SYMBOLS")

y = b.para(
    "The signifiers this subculture uses to recognise its own members, and what each one actually "
    "means to somebody inside the gym. Almost none of these meanings are decorative \u2014 they are "
    "claims about how much work a person has done.",
    M, y - 4, CW, REG, 9.6, 14.0)

# --- denotation / connotation definitions
dy, dh = y - 74, 60
b.rect(M, dy, CW, dh, INK)
b.mesh(M, dy, CW, dh, WHITE, 0.06, 15)
b.rect(M, dy + dh - 3, CW, 3, RED)
hw = (CW - 40) / 2
b.txt("DENOTATION", M + 16, dy + 38, DISP, 13, RED_HI, space=0.2)
b.para("The literal meaning \u2014 what the thing plainly is, before any "
       "interpretation.", M + 16, dy + 24, hw, REG, 8.4, 11.4, (0.78, 0.78, 0.82))
b.vline(M + CW / 2, dy + 12, dh - 24, (0.30, 0.30, 0.34), 0.7)
b.txt("CONNOTATION", M + CW / 2 + 16, dy + 38, DISP, 13, RED_HI, space=0.2)
b.para("The implied meaning \u2014 what it represents to the group that uses it.",
       M + CW / 2 + 16, dy + 24, hw, REG, 8.4, 11.4, (0.78, 0.78, 0.82))

SEMIO = [
    ("THE OCTAGON / THE CAGE",
     "An eight-sided competition area enclosed by chain-link fencing.",
     "The ultimate proving ground. Nowhere to hide and no way out, so it reads as a complete test "
     "of a person \u2014 close to sacred ground."),
    ("4OZ OPEN-FINGER GLOVES",
     "Minimal padding across the knuckles with the fingers left free.",
     "The real thing. Free fingers mean grappling is allowed, so this is a whole fight rather than "
     "just boxing."),
    ("WRAPPED HANDS",
     "Cotton or elastic wrap supporting the wrist and knuckles.",
     "Ritual and preparation \u2014 the deliberate few minutes before violence. Reads as craft, not "
     "rage, which is why it is the most useful image the culture owns."),
    ("THE BJJ BELT",
     "A coloured cloth belt, running white through to black.",
     "Verified time served. A black belt is a decade of work, and it is the one credential here "
     "that cannot be bought, inherited or talked into existence."),
    ("CAULIFLOWER EAR",
     "Scar tissue in the outer ear caused by repeated friction and impact.",
     "Irrefutable proof of real mat mileage. Worn as a badge of honour, and often left untreated "
     "on purpose."),
    ("TEAM RASHGUARD & GYM PATCH",
     "A compression top printed with a gym name, crest or sponsor marks.",
     "Affiliation, exactly like a football jersey. It announces who you represent and whose student "
     "you are."),
    ("PREDATOR IMAGERY",
     "Skulls, wolves, big cats, snakes and claw marks.",
     "Killer instinct and dominance \u2014 sitting at the top of the food chain in your division. This "
     "is the signifier APEX PREDATOR MMA is built on."),
    ("BLACK + BLOOD RED",
     "A near-black base carrying a single saturated red accent.",
     "Black for discipline, seriousness and fight night. Red for blood, danger and adrenaline. "
     "Brushed silver for hardness and steel."),
    ("THE GLOVE TOUCH / BOW",
     "A brief physical gesture exchanged before and after a round.",
     "Mutual consent and respect. It is the signal that converts an assault into a sport, and both "
     "athletes know it."),
    ("KANJI, THAI & PORTUGUESE",
     "Non-English words and characters on gear and gym walls.",
     "Respect paid to where the techniques came from. Read as lineage and authenticity rather than "
     "decoration \u2014 but only if spelled correctly."),
]
b.table(M, dy - 22, [104, 176, 203.28], SEMIO,
        head=("SIGNIFIER", "DENOTATION \u2014 WHAT IT IS",
              "CONNOTATION \u2014 WHAT IT MEANS TO THEM"),
        size=8.0, leading=10.8, pad=8.5)
b.tab("06 \u00b7 Semiotic Analysis")
b.footer("Signs & Symbols")

# =====================================================================
# 9 - 07 SEMIOTICS: MEANING & MISREADING
# =====================================================================
b.new()
y = b.section_head("07", "SEMIOTIC INVESTIGATION", "MEANING & MISREADING")

y = b.para(
    "Every signifier on the previous page carries a second, unintended reading for people outside "
    "the subculture. This matters commercially as well as ethically: the same image that earns "
    "respect on the mat can lose a stockist, a sponsor or a parent's permission outside it.",
    M, y - 4, CW, REG, 9.6, 14.0)

y = b.table(M, y - 20, [104, 187, 192.28], [
    ("THE CAGE",
     "A safety structure that stops fighters falling out of the ring, and the sport's "
     "proving ground.",
     "\u201cHuman cockfighting\u201d \u2014 the phrase a US senator used against the sport in the 1990s. "
     "Animals in a pen; barbarism."),
    ("CAULIFLOWER EAR",
     "A credential. Evidence of years of honest work on the mat.",
     "Disfigurement, or proof that somebody is a thug. Often the first thing a non-training "
     "parent notices."),
    ("PREDATOR & SKULL IMAGERY",
     "Competitive mindset and dominance within a weight division.",
     "Glorifying real violence \u2014 and in some contexts read as gang or extremist coding."),
    ("THE NAME \u201cFIGHT CLUB\u201d",
     "The ordinary, everyday word for a training group at a gym.",
     "The Fincher film: illegal, unsupervised, bare-knuckle fighting."),
    ("THE NAME \u201cAPEX PREDATOR\u201d",
     "Top of the food chain, competitively \u2014 the athlete nobody can solve.",
     "\u201cPredatory\u201d, which is a genuinely unhelpful word to have circling a brand aimed partly "
     "at teenagers."),
    ("BLACK + RED, TATTOOS,\nSHAVED HEADS",
     "The standard, unremarkable aesthetic of fight culture.",
     "Intimidating; occasionally confused with football-hooligan or far-right visual coding."),
    ("WOMEN TRAINING",
     "Athletes doing exactly what the men in the room are doing.",
     "Easily read as sexualised if it is shot using the conventions of fashion rather than "
     "those of sport."),
], head=("SIGNIFIER", "READ INSIDE THE SUBCULTURE", "MISREAD BY EVERYONE ELSE"),
    size=8.0, leading=10.8, pad=8.5)

y = b.sub("WHAT THIS MEANS FOR THE DESIGN", M, y - 22, rule=CW)
dl = ["Keep the octagon, lose the blood \u2014 the cage is used as geometry, a crest and a frame, "
      "never as a picture of somebody being hurt.",
      "No skulls \u2014 the predator idea is carried by the claw slash and the word APEX alone.",
      "Photograph the discipline, not the damage \u2014 wraps, coaching, the empty gym at 6am. "
      "Effort reads as aspirational to insiders and outsiders alike."]
dr = ["Frame FIGHT CLUB as sport every time \u2014 it never appears without TRAINING \u00b7 SPARRING \u00b7 "
      "FIGHT NIGHTS beneath it, so the underground-fighting reading never lands.",
      "Shoot women exactly like men \u2014 same lenses, same angles, same sweat, same crops.",
      "Get the technique right \u2014 a wrong guard or a bad stance in an advert is mocked "
      "instantly, and the credibility does not come back."]
e1 = b.bullets(dl, M, y - 4, COLW, size=8.8, leading=12.3, gap=6.0)
e2 = b.bullets(dr, CX2, y - 4, COLW, size=8.8, leading=12.3, gap=6.0)

# --- closing rule, filling the remaining space
py = 152
phh = min(e1, e2) - 24 - py
b.rect(M, py, CW, phh, INK)
b.mesh(M, py, CW, phh, WHITE, 0.06, 15)
b.rect(M, py + phh - 3, CW, 3, RED)
b.txt("THE TEST APPLIED TO EVERY SYMBOL IN THIS BRAND", M + 16, py + phh - 24,
      LBL, 8.2, RED_HI, space=1.9)
b.txt("If it only works inside the gym it is a liability.", M + 16, py + phh - 44,
      DISP, 14, PAPER, space=0.2)
b.txt("If it only works outside, it is invisible.", M + 16, py + phh - 62,
      DISP, 14, SILVER, space=0.2)
b.tab("07 \u00b7 Semiotic Analysis")
b.footer("Meaning & Misreading")


# =====================================================================
# 10 - 08 MOOD BOARD
# =====================================================================
b.new(dark=True)
b.glow(0, 0, PW, PH, INK, (0.105, 0.014, 0.022), power=2.1, cx=0.42, cy=0.40)
b.mesh(0, 0, PW, PH, WHITE, 0.05, 19)
y = b.section_head("08", "THE PRODUCT / DESIGN", "MOOD BOARD", col=PAPER)

y = b.para(
    "The visual territory the brand is aiming at: low light, hard rim light, worn equipment, "
    "steel and chalk, and effort rather than injury. Assembled before any layout work began.",
    M, y - 4, CW * 0.86, REG, 9.4, 13.6, (0.76, 0.76, 0.80))

# --- the finished cover artwork, left
POW = 176
POH = 302
ptop = y - 18
b.rect(M, ptop - POH, POW, POH, INK2)
b.img_fit(IMGB("APEX-MMA-poster.png"), M, ptop - POH, POW, POH)
b.frame(M, ptop - POH, POW, POH, (0.30, 0.30, 0.34), 0.8)
b.txt("THE RESULT \u00b7 COVER ARTWORK", M, ptop - POH - 12, LBL, 7.4, RED, space=1.6)

# --- four mood tiles, right
rx = M + POW + 16
tw2 = (PW - M - rx - 14) / 2
th2 = (POH - 14) / 2
for i, s in enumerate(("mood-01", "mood-02", "semio-01", "semio-02")):
    tx = rx + (i % 2) * (tw2 + 14)
    ty = ptop - th2 if i < 2 else ptop - POH
    b.photo(s, tx, ty, tw2, th2)

# --- mood-03 + the mood palette
by = 152
bh2 = 182
b.photo("mood-03", M, by, COLW, bh2)
b.rect(CX2, by, COLW, bh2, INK2)
b.mesh(CX2, by, COLW, bh2, WHITE, 0.06, 14)
b.rect(CX2, by + bh2 - 3, COLW, 3, RED)
b.txt("MOOD PALETTE", CX2 + 14, by + bh2 - 22, LBL, 8.2, RED_HI, space=1.9)
SWA = [(INK, "NIGHT"), (INK2, "STEEL"), (RED_LO, "OLD BLOOD"),
       (RED, "FIGHT NIGHT"), (RED_HI, "ADRENALINE"), (SILVER, "CHALK")]
scw2 = (COLW - 28 - 2 * 8) / 3
for i, (c, nm) in enumerate(SWA):
    sx = CX2 + 14 + (i % 3) * (scw2 + 8)
    sy2 = by + bh2 - 50 - (i // 3) * 62 - 40
    b.rect(sx, sy2, scw2, 40, c)
    b.frame(sx, sy2, scw2, 40, (0.34, 0.34, 0.38), 0.6)
    b.txt(nm, sx, sy2 - 11, LBLM, 6.9, (0.66, 0.66, 0.70), space=0.9)
b.caption("Left: atmosphere reference. Right: the palette pulled straight out of the "
          "photographs rather than chosen first.", M, by - 12, CW)
b.tab("08 \u00b7 The Product / Design")
b.footer("Mood Board")

# =====================================================================
# 11 - 09 IDEATION
# =====================================================================
b.new()
y = b.section_head("09", "THE PRODUCT / DESIGN", "IDEATION & DEVELOPMENT")
y = b.para(
    "Turning the research into something that can be drawn. The mind map converts each researched "
    "signifier into a usable design device; the thumbnails test how those devices sit on a page.",
    M, y - 4, CW, REG, 9.6, 14.0)

# --- mind map
y = b.sub("MIND MAP \u2014 FROM RESEARCH TO DESIGN DEVICE", M, y - 16, rule=CW)
mtop, mbot = y - 6, 402
cxm = M + CW / 2
cym = (mtop + mbot) / 2
cbw, cbh = 150, 48
b.rect(cxm - cbw / 2, cym - cbh / 2, cbw, cbh, INK)
b.rect(cxm - cbw / 2, cym + cbh / 2 - 3, cbw, 3, RED)
b.txt("APEX PREDATOR", cxm, cym + 8, DISP, 15, PAPER, space=0.2, align="c")
b.txt("MMA", cxm, cym - 10, DISP, 15, RED, space=0.2, align="c")

BW, BH = 120, 46
NODES = [("THE OCTAGON", "crest \u00b7 frame \u00b7 8-sided grid", 0, 0),
         ("WRAPS & TAPE", "hero photo \u00b7 texture", 0, 1),
         ("SWEAT & GRAIN", "duotone \u00b7 film grain", 0, 2),
         ("CLAW / PREDATOR", "3-slash mark \u00b7 logo", 1, 0),
         ("BLACK + BLOOD RED", "palette \u00b7 one accent", 1, 1),
         ("LINEAGE & RESPECT", "small caps \u00b7 credits", 1, 2)]
rows_y = [mtop - BH, (mtop + mbot) / 2 - BH / 2, mbot]
for label, leaf, side, row in NODES:
    bx = M if side == 0 else PW - M - BW
    by2 = rows_y[row]
    b.rect(bx, by2, BW, BH, (0.925, 0.918, 0.906))
    b.rect(bx if side == 0 else bx + BW - 3, by2, 3, BH, RED)
    b.txt(label, bx + 9, by2 + BH - 17, LBL, 9.0, INK, space=0.8)
    b.para(leaf, bx + 9, by2 + BH - 29, BW - 18, LBLM, 7.2, 9.2, GREY)
    # elbow connector
    ex = bx + BW if side == 0 else bx
    tx2 = cxm - cbw / 2 if side == 0 else cxm + cbw / 2
    mid = (ex + tx2) / 2
    b.line(min(ex, mid), by2 + BH / 2, abs(mid - ex), LGREY, 0.9)
    b.vline(mid, min(by2 + BH / 2, cym), abs(cym - (by2 + BH / 2)), LGREY, 0.9)
    b.line(min(mid, tx2), cym, abs(tx2 - mid), LGREY, 0.9)

# --- thumbnails
y = b.sub("THUMBNAIL SKETCHES", M, 382, rule=CW)
TN = [("CAGE FRAME", "octagon border", False),
      ("SPLIT TYPE", "red / silver split", True),
      ("FULL BLEED", "photo to edge", False),
      ("CREST LOCKUP", "centred, symmetrical", False),
      ("SLAB STACK", "3 stacked slabs", False)]
tnw = (CW - 4 * 12) / 5
tny, tnh = 258, 110
for i, (nm, note, chosen) in enumerate(TN):
    tx = M + i * (tnw + 12)
    b.rect(tx, tny, tnw, tnh, (0.925, 0.918, 0.906))
    b.frame(tx, tny, tnw, tnh, RED if chosen else LGREY, 1.4 if chosen else 0.7)
    ix, iy, iw, ih = tx + 9, tny + 9, tnw - 18, tnh - 18
    if i == 0:
        b.octagon(ix + iw / 2, iy + ih / 2, min(iw, ih) / 2 - 2, GREY, 1.0)
        b.rect(ix + iw / 2 - 18, iy + ih / 2 - 3, 36, 6, INK)
    elif i == 1:
        b.rect(ix, iy + ih - 30, iw, 13, RED)
        b.rect(ix, iy + ih - 46, iw, 13, GREY)
        b.rect(ix, iy, iw, ih - 54, (0.80, 0.79, 0.78))
    elif i == 2:
        b.rect(ix, iy, iw, ih, (0.80, 0.79, 0.78))
        b.rect(ix, iy, iw, 22, INK)
        b.rect(ix + 5, iy + 7, iw - 30, 8, RED)
    elif i == 3:
        b.octagon(ix + iw / 2, iy + ih - 34, 17, RED, 1.2)
        b.rect(ix + 8, iy + 22, iw - 16, 9, INK)
        b.rect(ix + 20, iy + 10, iw - 40, 5, GREY)
    else:
        for k in range(3):
            b.rect(ix, iy + ih - 20 - k * 26, iw, 18,
                   [INK, RED, GREY][k])
    b.txt("%02d" % (i + 1), tx, tny - 12, LBL, 8.0, RED, space=1.2)
    b.txt(nm, tx + 18, tny - 12, LBL, 8.0, INK, space=0.8)
    b.para(note, tx, tny - 24, tnw, OBL, 6.9, 9.0, GREY)
    if chosen:
        b.rect(tx, tny + tnh - 14, 56, 14, RED)
        b.txt("SELECTED", tx + 5, tny + tnh - 10, LBL, 7.2, WHITE, space=1.1)

# --- brainstorm
y = b.sub("BRAINSTORM", M, 214, rule=CW)
WORDS = [("APEX", 17, RED), ("cage", 11, GREY), ("OCTAGON", 14, INK),
         ("wraps", 11, GREY), ("CLAW", 16, RED), ("lineage", 10, GREY),
         ("SWEAT", 13, INK), ("oss", 10, GREY), ("PREDATOR", 15, INK),
         ("blood red", 12, RED), ("tap", 10, GREY), ("DISCIPLINE", 14, INK),
         ("mat time", 11, GREY), ("HONOR", 13, RED), ("steel", 10, GREY),
         ("cauliflower", 11, GREY), ("WARRIOR", 15, INK), ("6am", 10, GREY)]
wx, wy = M, 186
for w, sz, cc in WORDS:
    ww = pdfmetrics.stringWidth(w, DISP, sz) + 14
    if wx + ww > PW - M:
        wx, wy = M, wy - 22
    b.txt(w, wx, wy, DISP, sz, cc, space=0.2)
    wx += ww
b.tab("09 \u00b7 The Product / Design")
b.footer("Ideation & Development")

# =====================================================================
# 12 - 10 THE PRODUCT: DESIGN SYSTEM
# =====================================================================
b.new()
y = b.section_head("10", "THE PRODUCT / DESIGN", "THE DESIGN SYSTEM")
y = b.para(
    "The finished kit of parts, and the research reason behind each decision. Every element here "
    "traces back to a signifier identified in sections 06 and 07.",
    M, y - 4, CW, REG, 9.6, 14.0)

# --- logo
y = b.sub("LOGO / LOCKUP", M, y - 16, rule=CW)
lgh = 128
lgy = y - 8 - lgh
b.rect(M, lgy, COLW, lgh, INK)
b.mesh(M, lgy, COLW, lgh, WHITE, 0.06, 14)
b.rect(M, lgy + lgh - 3, COLW, 3, RED)
b.crest(M + 42, lgy + lgh / 2 + 2, 30)
b.txt("APEX PREDATOR", M + 82, lgy + lgh / 2 + 8, DISP, 19, PAPER, space=0.3)
b.txt("MMA", M + 82, lgy + lgh / 2 - 14, DISP, 19, RED, space=0.3)
b.txt("PRIMARY LOCKUP", M + 14, lgy + 14, LBL, 7.2, (0.58, 0.58, 0.62), space=1.6)
b.bullets([
    "The crest \u2014 a true eight-sided octagon, taken straight from the cage. It is the one shape "
    "the subculture cannot mistake for anything else.",
    "The claw \u2014 three slashes, the centre one longest. Carries the predator idea without "
    "resorting to a skull.",
    "The split \u2014 APEX PREDATOR in silver, MMA in red, so the sport is always the loudest word "
    "in the lockup.",
], CX2, y - 12, COLW, size=8.6, leading=12.0, gap=6.0)

# --- palette
y = b.sub("COLOUR PALETTE", M, lgy - 26, rule=CW)
PAL = [(INK, "#08080A", "Base"), (INK2, "#141417", "Panels"),
       (RED_LO, "#7C0A0D", "Shadow"), (RED, "#E6191F", "Accent"),
       (RED_HI, "#FF5A52", "Highlight"), (SILVER, "#C9CCD2", "Type")]
pw6 = (CW - 5 * 8) / 6
py2 = y - 8 - 64
for i, (c, hexv, use) in enumerate(PAL):
    px = M + i * (pw6 + 8)
    b.rect(px, py2 + 22, pw6, 42, c)
    b.frame(px, py2 + 22, pw6, 42, LGREY, 0.6)
    b.txt(hexv, px, py2 + 12, LBL, 7.6, INK, space=0.6)
    b.txt(use.upper(), px, py2 + 2, LBLM, 6.9, GREY, space=0.9)

# --- type
y = b.sub("TYPEFACES", M, py2 - 26, rule=CW)
ty2 = y - 8 - 78
b.rect(M, ty2, COLW, 78, (0.925, 0.918, 0.906))
b.txt("ANTON", M + 12, ty2 + 56, DISP, 28, INK, space=0.2)
b.txt("DISPLAY \u00b7 HEADLINES \u00b7 THE LOCKUP", M + 12, ty2 + 38, LBL, 7.4, RED, space=1.6)
b.para("Heavy, condensed and unapologetic. It behaves like stencilled arena signage, "
       "and it holds up at poster scale.", M + 12, ty2 + 26, COLW - 24, REG, 7.8, 10.4, GREY)
b.rect(CX2, ty2, COLW, 78, (0.925, 0.918, 0.906))
b.txt("Barlow Condensed", CX2 + 12, ty2 + 56, LBLS, 26, INK, space=0.2)
b.txt("LABELS \u00b7 SMALL CAPS \u00b7 CAPTIONS", CX2 + 12, ty2 + 38, LBL, 7.4, RED, space=1.6)
b.para("Narrow enough to set the long technical strings the sport is full of without "
       "shouting over the display face.", CX2 + 12, ty2 + 26, COLW - 24, REG, 7.8, 10.4, GREY)

# --- applications
y = b.sub("APPLICATIONS", M, ty2 - 26, rule=CW)
apw = (CW - 3 * 14) / 4
apy, aph = 142, 74
for i, nm in enumerate(("RASHGUARD", "TEE", "POSTER", "INSTAGRAM")):
    ax = M + i * (apw + 14)
    b.rect(ax, apy, apw, aph, INK)
    b.mesh(ax, apy, apw, aph, WHITE, 0.06, 12)
    ccx, ccy = ax + apw / 2, apy + aph / 2 + 6
    if i == 0:
        b.rect(ccx - 20, ccy - 20, 40, 40, INK2)
        b.rect(ccx - 20, ccy + 12, 40, 8, RED)
        b.crest(ccx, ccy - 4, 9)
    elif i == 1:
        b.rect(ccx - 22, ccy - 18, 44, 36, INK2)
        b.rect(ccx - 30, ccy + 6, 12, 8, INK2)
        b.rect(ccx + 18, ccy + 6, 12, 8, INK2)
        b.crest(ccx, ccy, 10)
    elif i == 2:
        b.rect(ccx - 15, ccy - 22, 30, 44, INK2)
        b.rect(ccx - 12, ccy + 8, 24, 6, RED)
        b.rect(ccx - 12, ccy - 2, 18, 4, SILVER)
    else:
        b.rect(ccx - 20, ccy - 20, 40, 40, INK2)
        for r in range(2):
            for c2 in range(2):
                b.rect(ccx - 18 + c2 * 19, ccy - 18 + r * 19, 17, 17,
                       RED if (r + c2) % 2 == 0 else (0.22, 0.22, 0.25))
    b.txt(nm, ax + 8, apy + 8, LBL, 7.4, (0.66, 0.66, 0.70), space=1.4)
b.txt("Every application is built from the same three parts: the crest, the split wordmark, "
      "and exactly one red accent.", M, apy - 16, OBL, 8.2, GREY)
b.tab("10 \u00b7 The Product / Design")
b.footer("The Design System")

# =====================================================================
# 13 - 11 PHOTOGRAPHY PLAN & CONTACT SHEET
# =====================================================================
b.new()
y = b.section_head("11", "PRODUCTION", "PHOTOGRAPHY PLAN")
y = b.para(
    "Photography is a required element of this product, and it is also the single biggest "
    "credibility test the brand faces. Every frame is shot on location in a working gym, using "
    "people who actually train.",
    M, y - 4, CW, REG, 9.6, 14.0)

y = b.sub("HOW THESE ARE SHOT", M, y - 16, rule=CW)
b.bullets([
    "Available light first \u2014 one window or a single LED panel, with the background deliberately "
    "underexposed so the subject is rim-lit rather than evenly lit.",
    "Fast glass, high ISO \u2014 1/500s and above to freeze strikes; 1/30s deliberately for the wide "
    "room shots so movement smears and the gym reads as busy.",
], M, y - 4, COLW, size=8.7, leading=12.2, gap=6.0)
b.bullets([
    "Documentary, not directed \u2014 nothing is staged twice. Sweat, tape and scuffed gear stay in "
    "frame because removing them removes the proof.",
    "Consent and safety \u2014 written permission from the gym and from every athlete, and nobody is "
    "photographed mid-injury.",
], CX2, y - 4, COLW, size=8.7, leading=12.2, gap=6.0)

# --- contact sheet: every slot in the booklet
y = b.sub("CONTACT SHEET \u2014 ALL %d FRAMES" % len(SHOTS), M, 546, rule=CW)
cols5 = 5
ctw = (CW - (cols5 - 1) * 8) / cols5
cth = 76
for i, slot in enumerate(SHOTS):
    r, c = divmod(i, cols5)
    cx2 = M + c * (ctw + 8)
    cy2 = y - 8 - (r + 1) * cth - r * 22
    p = find_photo(slot)
    if p:
        b.img_cover(p, cx2, cy2, ctw, cth)
    else:
        if slot not in b.missing:
            b.missing.append(slot)
        b.rect(cx2, cy2, ctw, cth, (0.902, 0.894, 0.882))
        b.mesh(cx2, cy2, ctw, cth, (0, 0, 0), 0.035, 13)
        b.frame(cx2, cy2, ctw, cth, GREY, 0.7, dash=(3, 3), alpha=0.6)
        b.txt("TO SHOOT", cx2 + ctw / 2, cy2 + cth / 2 - 3, LBL, 7.4, GREY,
              space=1.4, align="c")
    b.txt("%02d" % (i + 1), cx2, cy2 - 11, LBL, 7.4, RED, space=1.0)
    b.txt(slot.upper(), cx2 + 16, cy2 - 11, LBLM, 7.4, INK, space=0.7)
b.tab("11 \u00b7 Production")
b.footer("Photography Plan")


# =====================================================================
# 14 - 12 MARKETABILITY: WHO BUYS IT
# =====================================================================
b.new()
y = b.section_head("12", "MARKETABILITY", "WHO WOULD BUY THIS")
y = b.para(
    "Being specific about the target audience matters more here than in almost any other market, "
    "because this subculture actively polices who is allowed to claim membership. The three buyers "
    "below are ranked by how much credibility they carry, not by how much they spend.",
    M, y - 4, CW, REG, 9.6, 14.0)

PERSONAS = [
    ("TYSON", "19", "THE COMMITTED HOBBYIST", "PRIMARY TARGET", True,
     [("TRAINS", "5 nights a week, 18 months in"),
      ("LEVEL", "one amateur Muay Thai bout"),
      ("BUYS", "2\u20133 rashguards a year, shorts, mouthguards"),
      ("SPEND", "$250\u2013400 a year")],
     "Wants gear that says he is serious rather than brand new. He is the buyer whose approval "
     "everyone else copies."),
    ("AISHA", "23", "THE COMPETITOR", "HIGHEST VALUE", False,
     [("TRAINS", "6 sessions a week plus S&C"),
      ("LEVEL", "BJJ blue belt, competes quarterly"),
      ("BUYS", "competition-legal kit, walkout wear"),
      ("SPEND", "$400\u2013700 a year")],
     "Judges fit and performance before anything else. A brand that finally cuts properly for "
     "women earns loyalty that is very hard to shift."),
    ("JACK", "17", "THE FAN AT THE EDGE", "HIGHEST VOLUME", False,
     [("TRAINS", "once or twice a week"),
      ("LEVEL", "no competition, watches every card"),
      ("BUYS", "tees and hoodies only"),
      ("SPEND", "$80\u2013150 a year")],
     "Buys the look and the belonging. Essential for volume, but must never be served at the "
     "expense of the two buyers above."),
]
pnh = 250
pny = y - 18 - pnh
for i, (nm, age, role, flag, prim, facts, note) in enumerate(PERSONAS):
    px = M + i * (C3 + 20)
    b.rect(px, pny, C3, pnh, INK if prim else (0.925, 0.918, 0.906))
    b.rect(px, pny + pnh - 3, C3, 3, RED)
    tc = PAPER if prim else INK
    sc = (0.66, 0.66, 0.70) if prim else GREY
    b.rect(px + 12, pny + pnh - 24, pdfmetrics.stringWidth(flag, LBL, 7.0)
           + 2.0 * len(flag) + 10, 13, RED)
    b.txt(flag, px + 16, pny + pnh - 20.5, LBL, 7.0, WHITE, space=2.0)
    b.txt(nm, px + 12, pny + pnh - 52, DISP, 24, tc, space=0.2)
    b.txt(age, px + 12 + pdfmetrics.stringWidth(nm, DISP, 24) + 8,
          pny + pnh - 52, DISP, 15, RED, space=0.2)
    b.txt(role, px + 12, pny + pnh - 66, LBL, 7.8, RED if not prim else RED_HI,
          space=1.4)
    b.line(px + 12, pny + pnh - 74, C3 - 24,
           (0.28, 0.28, 0.32) if prim else LGREY, 0.7)
    fy = pny + pnh - 88
    for k, v in facts:
        b.txt(k, px + 12, fy, LBL, 7.0, sc, space=1.5)
        fy = b.para(v, px + 12, fy - 10, C3 - 24, REG, 7.7, 10.2, tc) - 6
    b.line(px + 12, fy + 4, C3 - 24,
           (0.28, 0.28, 0.32) if prim else LGREY, 0.7)
    b.para(note, px + 12, fy - 10, C3 - 24, OBL, 7.6, 10.2, sc)

# --- B2B + who we are not chasing
y = b.sub("TWO MORE THINGS THE PLAN DEPENDS ON", M, pny - 26, rule=CW)
e1 = b.bullets([
    "Gyms are the real customer \u2014 a single team-kit order for one gym outsells dozens of "
    "individual sales, and it puts the logo on a whole room at once. This is the biggest "
    "revenue lever the brand has.",
], M, y - 4, COLW, size=8.8, leading=12.3, gap=6.0)
e2 = b.bullets([
    "Who we are deliberately not chasing \u2014 general activewear buyers, and anyone drawn to "
    "street-fighting imagery. Serving either one would cost the credibility that everything "
    "else here depends on.",
], CX2, y - 4, COLW, size=8.8, leading=12.3, gap=6.0)

b.photo("market-01", M, 152, CW, min(e1, e2) - 26 - 152)
b.caption("The walkout: a sponsored amateur wearing the kit under the lights. This is the single "
          "highest-value placement the brand can buy, and it costs almost nothing.", M, 140, CW)
b.tab("12 \u00b7 Marketability")
b.footer("Who Would Buy This")

# =====================================================================
# 15 - 13 MARKETING PLAN: HOW WE REACH THEM
# =====================================================================
b.new()
y = b.section_head("13", "MARKETABILITY", "HOW WE REACH THEM")
y = b.para(
    "This audience does not respond to conventional advertising, and it is unusually good at "
    "spotting a brand run by people who do not train. The plan therefore spends most of its effort "
    "inside gyms and at events, and treats social media as documentation rather than promotion.",
    M, y - 4, CW, REG, 9.6, 14.0)

y = b.sub("CHANNELS", M, y - 16, rule=CW)
CHAN = [
    ("01", "INSTAGRAM & TIKTOK",
     "Short technique clips, sparring rounds, gear checks and fight-camp footage. Athlete-shot "
     "and vertical, never studio-polished. Posted daily."),
    ("02", "ATHLETE & GYM SEEDING",
     "Free kit to local amateurs and coaches in exchange for walkout and training wear. Cheap, "
     "and it buys the one thing money normally cannot: insider endorsement."),
    ("03", "EVENTS & INTERCLUBS",
     "A merch booth and cage banner at local fight nights, BJJ comps and Muay Thai interclubs. "
     "Sponsor one card per quarter."),
    ("04", "GYM STOCKISTS",
     "Wholesale racks inside partner gyms plus bulk team-kit deals, so the brand is bought at the "
     "exact place identity is formed."),
    ("05", "ONLINE STORE",
     "Shopify, with an honest fit guide by discipline, and limited drops to create the scarcity "
     "this audience already responds to."),
    ("06", "LONG-FORM & COMMUNITY",
     "YouTube breakdowns, podcast sponsorship, and a genuine presence in the sport's forums and "
     "Discords rather than paid comments."),
]
chh = 132
for i, (n, nm, dsc) in enumerate(CHAN):
    cxx = M + (i % 3) * (C3 + 20)
    cyy = y - 8 - chh if i < 3 else y - 8 - 2 * chh - 14
    b.rect(cxx, cyy, C3, chh, (0.925, 0.918, 0.906))
    b.rect(cxx, cyy + chh - 3, C3, 3, RED)
    b.txt(n, cxx + 12, cyy + chh - 26, DISP, 17, RED, space=0.2)
    b.para(nm, cxx + 12, cyy + chh - 44, C3 - 24, DISP, 12, 13.4, INK)
    b.para(dsc, cxx + 12, cyy + chh - 74, C3 - 24, REG, 7.8, 10.6, GREY)

# --- budget split
y = b.sub("BUDGET SPLIT \u2014 YEAR ONE", M, y - 8 - 2 * chh - 14 - 26, rule=CW)
BUD = [("ATHLETE & GYM SEEDING", 28, RED),
       ("PHOTOGRAPHY & CONTENT", 24, INK),
       ("EVENTS & SPONSORSHIP", 20, RED_LO),
       ("PAID SOCIAL", 16, GREY),
       ("STORE & SAMPLING", 12, (0.72, 0.72, 0.75))]
bary, barh = y - 42, 30
bx = M
for nm, pct, c in BUD:
    seg = CW * pct / 100.0
    b.rect(bx, bary, seg, barh, c)
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]     # keep %% legible
    b.txt("%d%%" % pct, bx + seg / 2, bary + 10.5, LBL, 9.4,
          INK if lum > 0.55 else WHITE, space=0.8, align="c")
    bx += seg
lgw = CW / len(BUD)                     # evenly spaced legend, not segment-aligned
for i, (nm, pct, c) in enumerate(BUD):
    lx = M + i * lgw
    b.rect(lx, bary - 18, 8, 8, c)
    b.para(nm, lx + 12, bary - 17, lgw - 18, LBLM, 6.9, 8.6, GREY)

y = b.sub("THE THREE RULES", M, bary - 44, rule=CW)
b.bullets([
    "Use real athletes from real gyms \u2014 a model who has never trained is spotted in one frame.",
    "Never fake credentials \u2014 no invented lineage, no borrowed belts, no stolen fight records.",
    "Support before selling \u2014 sponsor the local card, pay the photographer, kit out the coach.",
], M, y - 4, CW, size=8.9, leading=12.5, gap=5.5)
b.tab("13 \u00b7 Marketability")
b.footer("How We Reach Them")

# =====================================================================
# 16 - 14 CONCLUSION / BACK COVER
# =====================================================================
b.new(dark=True)
b.glow(0, 0, PW, PH, INK, (0.125, 0.017, 0.026), power=1.9, cx=0.5, cy=0.50)
b.mesh(0, 0, PW, PH, WHITE, 0.055, 19)

# silhouette watermark, composited over the glow via a real alpha mask
sil_h = 470
sil_w = sil_h * 1469 / 1780
b.c.drawImage(silhouette_reader(IMGB("hero-fighter.png"), (0.0, 0.0, 0.0), 0.42),
              PW - sil_w - 6, 150, sil_w, sil_h, mask="auto")

b.strip(808, 34, "DISCIPLINE.  STRENGTH.  HONOR.", RED, WHITE)
y = b.section_head("14", "SECTION", "CONCLUSION", col=PAPER)

y = b.para(
    "APEX PREDATOR MMA takes a subculture that is built on proof rather than talk, and answers it "
    "with a brand that can survive being looked at closely.",
    M, y - 4, CW * 0.62, REG, 9.6, 14.0, (0.78, 0.78, 0.82))

SUMS = [("WHAT THE RESEARCH FOUND",
         "A community organised around earned status, chosen hardship and a total intolerance "
         "of anything fake."),
        ("WHAT THE SYMBOLS MEAN",
         "The octagon, the wraps, the belt and the worn-in gear all say the same thing: this "
         "person has done the work."),
        ("WHAT THE DESIGN DOES",
         "Uses those signs as geometry and restraint rather than as gore, so it reads as "
         "credible inside the gym and safe outside it.")]
cyy = y - 22
for h, t in SUMS:
    b.txt(h, M, cyy, LBL, 8.4, RED_HI, space=1.9)
    b.rect(M, cyy - 9, 40, 2, RED)
    cyy = b.para(t, M, cyy - 24, CW * 0.56, REG, 9.0, 12.6, (0.76, 0.76, 0.80)) - 14

b.rect(M, 352, 4, 86, RED)
b.txt("WARRIOR", M + 18, 410, DISP, 38, RED, space=0.3)
b.txt("SPIRIT", M + 18, 368, DISP, 38, SILVER, space=0.3)

b.crest(PW - M - 40, 620, 40)

# --- call to action
b.rect(0, 176, PW, 52, RED)
b.txt("JOIN THE ELITE   |   APEX FIGHT CLUB", PW / 2, 202, DISP, 21, WHITE,
      space=0.6, align="c")
b.txt("TRAINING \u00b7 SPARRING \u00b7 FIGHT NIGHTS", PW / 2, 185, LBL, 8.2,
      (1, 0.86, 0.86), space=2.6, align="c")

b.txt("WWW.APEXMMA.COM", PW / 2, 140, DISP, 17, PAPER, space=1.2, align="c")
b.txt("@APEXMMA   \u00b7   #UNLEASHTHEBEAST", PW / 2, 122, LBL, 8.4, SILVER,
      space=2.4, align="c")
b.line(M, 100, CW, (0.30, 0.30, 0.34))
b.txt("APEX PREDATOR MMA", M, 82, LBL, 8, (0.55, 0.55, 0.60), space=1.6)
b.txt("MARKETING BOOKLET \u00b7 ISSUE 01 / 2026", PW / 2, 82, LBLM, 8,
      (0.55, 0.55, 0.60), space=1.4, align="c")
b.txt("PAGE %d" % b.page, PW - M, 82, LBLM, 8, (0.55, 0.55, 0.60),
      space=1.4, align="r")

b.save()

# ---------------------------------------------------------------- shot list
# Emitted from SHOTS so the shot list can never drift from the layout.
with open(os.path.join(HERE, "SHOT-LIST.md"), "w") as f:
    f.write("# APEX PREDATOR MMA \u2014 Photography Shot List\n\n")
    f.write("%d frames. Shoot each one, then save it into `photos/` named after "
            "its slot code (for example `photos/hero-01.jpg`) and re-run "
            "`python3 build_mma_booklet.py`. Images are cropped to fit "
            "automatically, so the exact aspect ratio does not matter.\n\n"
            % len(SHOTS))
    f.write("Any frame you have not shot yet appears in the booklet as a "
            "labelled placeholder showing this brief, so the layout stays "
            "finished while you work through the list.\n\n")
    f.write("| # | Save as | Frame | Brief |\n|---:|---|---|---|\n")
    for i, (slot, (label, brief)) in enumerate(SHOTS.items(), 1):
        f.write("| %d | `photos/%s.jpg` | **%s** | %s |\n"
                % (i, slot, label, brief))
    f.write("\n## Consent\n\nGet written permission from the gym owner and from "
            "every person who appears in a frame before shooting, and keep it "
            "with the files. Do not photograph anyone mid-injury.\n")

# ---------------------------------------------------------------- report
print("Wrote %s  (%d pages)" % (os.path.basename(OUT), b.page))
print("Wrote SHOT-LIST.md  (%d frames)" % len(SHOTS))
if b.missing:
    print("Photo slots still to shoot (%d of %d):" % (len(b.missing), len(SHOTS)))
    for s in b.missing:
        print("   photos/%s.jpg   %s" % (s, SHOTS[s][0]))
else:
    print("All %d photo slots filled." % len(SHOTS))
