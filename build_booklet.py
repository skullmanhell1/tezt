#!/usr/bin/env python3
"""
Builds "JDM YARD - Marketing Booklet" as a print-ready A4 PDF.

Run:  python3 build_booklet.py
Out:  JDM-YARD-Marketing-Booklet.pdf
"""
import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "JDM-YARD-Marketing-Booklet.pdf")

PW, PH = A4                      # 595.28 x 841.89 pt
M = 44                           # page margin
CW = PW - 2 * M                  # content width

# ---------------------------------------------------------------- palette
INK    = (0.055, 0.055, 0.063)   # near-black
PAPER  = (0.957, 0.949, 0.937)   # off-white
RED    = (0.784, 0.063, 0.180)   # JDM red
GREY   = (0.451, 0.451, 0.471)
LGREY  = (0.855, 0.843, 0.827)
WHITE  = (1, 1, 1)

BOLD   = "Helvetica-Bold"
REG    = "Helvetica"
OBL    = "Helvetica-Oblique"
JP     = "HeiseiKakuGo-W5"
pdfmetrics.registerFont(UnicodeCIDFont(JP))

IMG = lambda n: os.path.join(HERE, n)


# ---------------------------------------------------------------- helpers
def cover_reader(path, tw, th):
    """Centre-crop an image to the target aspect ratio (like CSS object-fit: cover)."""
    im = Image.open(path).convert("RGB")
    tr, ir = tw / th, im.width / im.height
    if ir > tr:
        nw = int(im.height * tr)
        left = (im.width - nw) // 2
        im = im.crop((left, 0, left + nw, im.height))
    else:
        nh = int(im.width / tr)
        top = int((im.height - nh) * 0.42)          # bias slightly above centre
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


class Book:
    def __init__(self, path):
        self.c = rl_canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("JDM YARD - Marketing Booklet")
        self.c.setAuthor("JDM YARD")
        self.c.setSubject("Marketing booklet - JDM car subculture")
        self.page = 0

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

    def line(self, x, y, w, col=LGREY, lw=0.7):
        self.c.setStrokeColorRGB(*col)
        self.c.setLineWidth(lw)
        self.c.line(x, y, x + w, y)

    def frame(self, x, y, w, h, col=LGREY, lw=0.7, dash=None):
        self.c.saveState()
        self.c.setStrokeColorRGB(*col)
        self.c.setLineWidth(lw)
        if dash:
            self.c.setDash(dash, 3)
        self.c.rect(x, y, w, h, stroke=1, fill=0)
        self.c.restoreState()

    def img_cover(self, path, x, y, w, h):
        self.c.drawImage(cover_reader(path, w, h), x, y, w, h,
                         preserveAspectRatio=False, anchor="c")

    def img_fit(self, path, x, y, w, h, align="c"):
        r, iw, ih = fit_reader(path, w, h)
        ox = x + (w - iw) / 2 if align == "c" else x
        oy = y + (h - ih) / 2
        self.c.drawImage(r, ox, oy, iw, ih)
        return ox, oy, iw, ih

    # ---------- type
    def txt(self, s, x, y, font=REG, size=9, col=INK, space=0, align="l"):
        c = self.c
        w = pdfmetrics.stringWidth(s, font, size) + space * max(0, len(s) - 1)
        if align == "r":
            x -= w
        elif align == "c":
            x -= w / 2
        c.saveState()
        c.setFillColorRGB(*col)
        t = c.beginText(x, y)
        t.setFont(font, size)
        if space:
            t.setCharSpace(space)
        t.textOut(s)
        c.drawText(t)
        c.restoreState()

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

    def para(self, s, x, y, width, font=REG, size=9.3, leading=13.6, col=INK, space=0):
        for ln in self.wrap(s, font, size, width, space):
            self.txt(ln, x, y, font, size, col, space)
            y -= leading
        return y

    def bullets(self, items, x, y, width, size=9.2, leading=13.2, gap=5.5,
                col=INK, dot=RED, bullet="\u25a0", bsize=5.2):
        for it in items:
            first = True
            for ln in self.wrap(it, REG, size, width - 14):
                if first:
                    self.txt(bullet, x, y + 0.6, BOLD, bsize, dot)
                    first = False
                self.txt(ln, x + 14, y, REG, size, col)
                y -= leading
            y -= gap
        return y

    # ---------- furniture
    def kicker(self, s, x, y, col=RED, size=7.4, font=BOLD):
        self.txt(s, x, y, font, size, col, space=2.6)

    def heading(self, s, x, y, size=25, col=INK):
        self.txt(s, x, y, BOLD, size, col, space=-0.4)

    def section_head(self, num, kicker, title, y=PH - 92, col=INK, rule=True):
        self.txt(num, M, y + 26, BOLD, 44, RED, space=-1.5)
        self.kicker(kicker, M + (58 if num else 0), y + 40)
        self.heading(title, M + (58 if num else 0), y + 12, 24, col)
        if rule:
            self.line(M, y - 8, CW, LGREY if col == INK else (0.25, 0.25, 0.28))
        return y - 30

    def footer(self, label, light=False):
        col = GREY if not light else (0.62, 0.62, 0.66)
        self.line(M, 46, CW, LGREY if not light else (0.22, 0.22, 0.26))
        self.txt("JDM YARD", M, 33, BOLD, 7, col, space=1.6)
        self.txt(label.upper(), PW / 2, 33, REG, 7, col, space=1.6, align="c")
        self.txt(f"PAGE {self.page}", PW - M, 33, REG, 7, col, space=1.6, align="r")

    def tagline_strip(self, y, h=20, dark=True):
        self.rect(0, y, PW, h, INK if dark else RED)
        self.txt("\u672c\u7269\u306e\u30d1\u30fc\u30c4\u3002\u672c\u7269\u306e\u30d1\u30d5\u30a9\u30fc\u30de\u30f3\u30b9\u3002",
                 PW / 2, y + h / 2 - 3.6, JP, 8.5, WHITE, space=1, align="c")

    def new(self, dark=False):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.bg(INK if dark else PAPER)

    def save(self):
        self.c.save()


b = Book(OUT)

# =====================================================================
# 1 - COVER
# =====================================================================
b.new(dark=True)
b.img_cover(IMG("7.jpg"), 0, 232, PW, PH - 232)
b.rect(0, 232, PW, PH - 232, INK, 0.42)
b.rect(0, 232, PW, 150, INK, 0.30)

b.rect(0, PH - 34, PW, 34, RED)
b.txt("\u65e5\u672c\u8eca\u5c02\u9580\u30d1\u30fc\u30c4  \u00b7  JAPANESE PERFORMANCE PARTS",
      PW / 2, PH - 23, JP, 8, WHITE, space=1.4, align="c")

b.txt("MARKETING BOOKLET  \u00b7  UNIT OF WORK", M, PH - 66, BOLD, 8, WHITE, space=3)
b.txt("JDM", M - 4, PH - 168, BOLD, 96, WHITE, space=-3)
b.txt("YARD", M - 4, PH - 262, BOLD, 96, RED, space=-3)
b.rect(M, PH - 288, 150, 3.5, WHITE)
b.txt("REAL PARTS. REAL OWNERS. REAL PERFORMANCE.",
      M, PH - 308, BOLD, 9.4, WHITE, space=1.9)

b.rect(M, 300, 4, 74, RED)
y = 362
for ln in ["A parts brand built for the",
           "JDM car subculture."]:
    b.txt(ln, M + 18, y, BOLD, 19, WHITE, space=-0.3)
    y -= 25
b.txt("Featuring the Nissan 370Z (Z34)", M + 18, 306, REG, 9.5, (0.78, 0.78, 0.8), space=1)

b.tagline_strip(232, 22)

# cover foot: contact-sheet strip + credit
sw = (CW - 2 * 9) / 3
for i, f in enumerate(["3.JPG", "4.jpg", "5.jpg"]):
    b.img_cover(IMG(f), M + i * (sw + 9), 108, sw, 92)
b.txt("SUBCULTURE", M, 82, BOLD, 7.4, RED, space=2.4)
b.txt("JDM \u00b7 JAPANESE DOMESTIC MARKET CAR CULTURE", M, 66, REG, 9, WHITE, space=1)
b.txt("DESIGNER", PW - M, 82, BOLD, 7.4, RED, space=2.4, align="r")
b.txt("@jdmyard  \u00b7  ISSUE 01 / 2026", PW - M, 66, REG, 9, WHITE, space=1, align="r")
b.line(M, 50, CW, (0.3, 0.3, 0.34))

# =====================================================================
# 2 - CONTENTS
# =====================================================================
b.new()
y = b.section_head("", "MARKETING BOOKLET", "CONTENTS")
y = b.para(
    "This booklet presents JDM YARD \u2014 a Japanese performance parts brand designed and marketed "
    "for the JDM car subculture. It follows the research into the group, the meaning of their symbols, "
    "the design of the product, and the plan for selling it to them.",
    M, y - 6, CW * 0.78, REG, 9.6, 14.2)

rows = [("01", "Introduction / About", "3"),
        ("02", "Subculture Research \u2014 Definition & Demographics", "4"),
        ("03", "Subculture Research \u2014 Interests, Beliefs & Lifestyle", "5"),
        ("04", "Visual / Semiotic Analysis \u2014 Signs & Symbols", "6"),
        ("05", "Visual / Semiotic Analysis \u2014 Meaning & Misreading", "7"),
        ("06", "The Product / Design \u2014 Mood Board", "8"),
        ("07", "The Product / Design \u2014 Development & Sketches", "9"),
        ("08", "The Product / Design \u2014 Photography & Contact Sheet", "10"),
        ("09", "Marketing Plan", "11"),
        ("10", "Conclusion / Call to Action", "12")]

y -= 24
for n, t, p in rows:
    b.txt(n, M, y, BOLD, 10.5, RED, space=1)
    b.txt(t, M + 34, y, REG, 10.5, INK)
    b.txt(p, PW - M, y, BOLD, 10.5, INK, align="r")
    b.line(M, y - 9, CW, LGREY, 0.5)
    y -= 25

# hero image + caption
ih = 186
b.img_cover(IMG("2.jpg"), M, y - ih - 14, CW, ih)
b.txt("The brand's hero car: a Nissan 370Z (Z34) \u2014 photographed for the campaign and used across "
      "the magazine, website and posters.", M, y - ih - 28, OBL, 8, GREY)
b.footer("Contents")

# =====================================================================
# 3 - INTRODUCTION / ABOUT
# =====================================================================
b.new()
y = b.section_head("01", "SECTION", "INTRODUCTION / ABOUT")
colw = (CW - 26) / 2

yy = b.para(
    "JDM YARD is an online store and brand that sells parts for Japanese performance cars, aimed "
    "directly at the JDM car subculture in Australia. The name says exactly what it is \u2014 a \u201cyard\u201d "
    "of Japanese Domestic Market parts \u2014 so it reads as insider language straight away.",
    M, y - 8, colw, REG, 9.5, 14)

b.kicker("WHAT THE PRODUCT IS", M, yy - 14)
yy = b.bullets([
    "An online parts store (jdmyard.com) selling six categories: exhaust & exterior, interior parts, "
    "lighting, aero parts, wheels & accessories, and performance.",
    "A printed magazine-style zine \u2014 JDM YARD Issue 01 \u2014 sent free in every order and handed out at meets.",
    "Limited-run merchandise, posters and sticker packs carrying the brand mark.",
], M, yy - 32, colw)

b.kicker("WHAT SUBCULTURE IT TARGETS", M, yy - 8)
yy = b.para(
    "The JDM (Japanese Domestic Market) car subculture \u2014 people who own, build, tune and photograph "
    "Japanese performance cars. The core buyer is 18\u201330, active on Instagram, TikTok and YouTube, and "
    "spends real money on their build.",
    M, yy - 26, colw, REG, 9.5, 14)

# at-a-glance box (left column)
gh = 132
gy = yy - 26 - gh
b.rect(M, gy, colw, gh, INK)
b.txt("AT A GLANCE", M + 14, gy + gh - 22, BOLD, 7.6, RED, space=2.2)
glance = [("BRAND", "JDM YARD"),
          ("PRODUCT", "JDM parts store + print zine"),
          ("HERO CAR", "Nissan 370Z (Z34)"),
          ("MARKET", "Australia, shipped nationwide"),
          ("CORE BUYER", "Enthusiasts aged 18\u201330"),
          ("PRICE RANGE", "$8 stickers \u2013 $3,000 wheels")]
gyy = gy + gh - 40
for k, v in glance:
    b.txt(k, M + 14, gyy, BOLD, 7.4, (0.62, 0.62, 0.66), space=1.2)
    b.txt(v, M + colw - 14, gyy, REG, 8.4, WHITE, align="r")
    gyy -= 15

# right column
x2 = M + colw + 26
b.img_cover(IMG("9.jpg"), x2, PH - 372, colw, 236)
b.rect(x2, PH - 372, colw, 26, RED)
b.txt("\u672c\u7269\u306e\u30d1\u30fc\u30c4", x2 + 10, PH - 364, JP, 9, WHITE, space=1)
b.txt("REAL PARTS", x2 + colw - 10, PH - 364, BOLD, 8.4, WHITE, space=1.6, align="r")

yb = PH - 400
b.kicker("THE IDEA, BRIEFLY", x2, yb)
yb = b.para(
    "Most parts websites look like spreadsheets \u2014 grey, cheap and full of fakes. JDM YARD treats parts "
    "retail like the culture treats cars: dark, high-contrast, motorsport-styled, with Japanese type, "
    "real owner cars and honest specifications. The shop, the magazine and the poster all use one visual "
    "language so the brand feels like it belongs to the scene rather than advertising at it.",
    x2, yb - 16, colw, REG, 9.5, 14)

b.frame(x2, yb - 96, colw, 84, LGREY)
b.rect(x2, yb - 96, 3.5, 84, RED)
b.txt("POSITIONING STATEMENT", x2 + 14, yb - 28, BOLD, 7.4, RED, space=2.2)
b.para("\u201cGenuine and quality aftermarket JDM parts, sold by people who actually "
       "understand the cars \u2014 shipped Australia-wide.\u201d",
       x2 + 14, yb - 46, colw - 28, OBL, 9.2, 13)

b.footer("Introduction / About")

# =====================================================================
# 4 - RESEARCH: DEFINITION & DEMOGRAPHICS
# =====================================================================
b.new()
y = b.section_head("02", "SUBCULTURE RESEARCH", "DEFINITION & DEMOGRAPHICS")

y = b.para(
    "JDM stands for Japanese Domestic Market. Strictly, it means cars and parts built by Japanese "
    "manufacturers to be sold inside Japan only. The term has since grown into a worldwide subculture "
    "based on owning, tuning and modifying Japanese performance cars, mostly from the 1980s onwards. "
    "Hero models \u2014 the Nissan Skyline GT-R (R32/R33/R34), Toyota Supra MK4, Mazda RX-7 FD, Honda Civic "
    "and Integra Type R, Subaru WRX STI, Mitsubishi Lancer Evolution and the Nissan Z cars \u2014 are treated "
    "almost like celebrities inside the community.",
    M, y - 8, CW, REG, 9.6, 14.2)

qh = 58
b.rect(M, y - 12 - qh, CW, qh, INK)
b.rect(M, y - 12 - qh, 4, qh, RED)
b.para("To most people a car is just transport. In this subculture the car is self-expression \u2014 so "
       "members reject the ordinary \u201cstandard\u201d car and personalise everything: engine, body kit, "
       "wheels and paint.",
       M + 20, y - 32, CW - 40, OBL, 9.8, 14, WHITE)
y = y - 24 - qh

b.kicker("DEMOGRAPHICS OF THE GROUP", M, y)
y -= 18

cards = [
    ("AGE", "Mostly 16\u201335. Younger fans (16\u201324) arrive through games, anime and social media; the core "
            "(25\u201335) can actually afford to buy and modify; collectors (35\u201350+) chase rare classics."),
    ("GENDER", "Mainly male but increasingly mixed \u2014 more female enthusiasts, builders and drift drivers are "
               "visible online, so the brand must not assume an all-male audience."),
    ("NATIONALITY", "Global. Strong scenes in Japan, Australia, the USA, the UK, Canada, the UAE and across "
                    "South-East Asia and Europe. JDM YARD targets the Australian scene first."),
    ("CULTURAL IDENTITY", "A mix of Japanese heritage, street-racing and drift culture from the mountain "
                          "\u201ctouge\u201d roads, motorsport, and pop culture such as Initial D and Gran Turismo."),
]
cw2 = (CW - 18) / 2
ch = 96
for i, (t, d) in enumerate(cards):
    cx = M + (i % 2) * (cw2 + 18)
    cy = y - 18 - (i // 2) * (ch + 16) - ch
    b.frame(cx, cy, cw2, ch, LGREY)
    b.rect(cx, cy + ch - 3.5, cw2, 3.5, RED)
    b.txt(t, cx + 13, cy + ch - 22, BOLD, 8.2, INK, space=1.8)
    b.para(d, cx + 13, cy + ch - 40, cw2 - 26, REG, 8.7, 12.4, GREY)

y = y - 18 - 2 * (ch + 16)
b.rect(M, y - 6, 90, 3, RED)
y = b.para("Many members see themselves as knowledgeable \u201cinsiders\u201d who respect the culture rather "
           "than follow a trend. For a designer this is critical: the product has to feel authentic "
           "enough to be accepted by those insiders, or it gets dismissed instantly.",
           M, y - 24, CW * 0.88, REG, 9.4, 13.6)

bh4 = 132
b.txt("The kind of detail this audience actually spends money on \u2014 the owner's own car.",
      M, 70 + bh4 + 10, OBL, 8, GREY)
b.img_cover(IMG("6.jpg"), M, 70, CW, bh4)
b.footer("Subculture Research")

# =====================================================================
# 5 - RESEARCH: INTERESTS, BELIEFS, LIFESTYLE
# =====================================================================
b.new()
y = b.section_head("03", "SUBCULTURE RESEARCH", "INTERESTS, BELIEFS & LIFESTYLE")

col3 = (CW - 2 * 16) / 3
tops = [
    ("HOBBIES &\nACTIVITIES", [
        "Modifying and tuning \u2014 engine swaps, turbo upgrades, suspension, aero",
        "Car meets, shows and track days",
        "Drifting and grassroots motorsport",
        "Photography and video \u2014 posting car content on Instagram, YouTube, TikTok",
        "Racing games and sim racing",
        "Hunting rare OEM and aftermarket parts",
    ]),
    ("VALUES &\nBELIEFS", [
        "Authenticity over fakes \u2014 honest builds earn respect, a fake \u201cricer\u201d car does not",
        "Craftsmanship \u2014 doing the work yourself",
        "Heritage and nostalgia for 80s/90s Japanese engineering",
        "Individuality \u2014 every build is personal",
        "Community \u2014 sharing knowledge, trading parts",
        "\u201cForm and function\u201d \u2014 look good and perform",
    ]),
    ("LIFESTYLE &\nATTITUDES", [
        "Passionate and detail-obsessed; will spend real money and time",
        "Slightly rebellious and anti-mainstream",
        "Strong brand loyalty \u2014 Nissan, Honda and Mazda fans act like rival teams",
        "Style tribes exist: Bosozoku, Stance, VIP and Time Attack",
    ]),
]
ytop = y - 10
for i, (t, items) in enumerate(tops):
    cx = M + i * (col3 + 16)
    b.rect(cx, ytop - 4, col3, 3.5, RED)
    ly = ytop - 24
    for part in t.split("\n"):
        b.txt(part, cx, ly, BOLD, 10.6, INK, space=0.4)
        ly -= 13.5
    b.bullets(items, cx, ly - 8, col3, 8.6, 12.2, 5, GREY, RED, "\u2014", 7)

yq = 372
b.rect(0, yq, PW, 62, INK)
b.txt("\u201cFor this group, the car is an identity \u2014 not just a vehicle.\u201d",
      PW / 2, yq + 34, BOLD, 15, WHITE, align="c")
b.txt("RESEARCH FINDING \u00b7 SHARED BELIEFS", PW / 2, yq + 16, REG, 7.4, (0.65, 0.65, 0.7),
      space=2.4, align="c")

gw = (CW - 2 * 10) / 3
for i, f in enumerate(["4.jpg", "3.JPG", "5.jpg"]):
    b.img_cover(IMG(f), M + i * (gw + 10), 190, gw, 150)
caps = ["Engine bay \u2014 craftsmanship and \u201cdoing it properly\u201d",
        "Wheels and stance \u2014 status, taste and commitment",
        "Interior \u2014 the driver-focused, form-and-function attitude"]
for i, cp in enumerate(caps):
    b.para(cp, M + i * (gw + 10), 178, gw, OBL, 7.8, 10.4, GREY)

y2 = 148
b.kicker("WHAT THIS MEANS FOR JDM YARD", M, y2)
b.para("Every value in this research points at the same product decision: stock genuine and quality "
       "parts, explain them honestly, show real owner cars instead of stock photos, and make the "
       "packaging and print worth keeping. The brand should reward knowledge, not hide it.",
       M, y2 - 18, CW * 0.9, REG, 9.4, 13.6)
b.footer("Subculture Research")

# =====================================================================
# 6 - SEMIOTIC ANALYSIS: SIGNIFIERS
# =====================================================================
b.new()
y = b.section_head("04", "VISUAL / SEMIOTIC ANALYSIS", "SIGNS & SYMBOLS")
y = b.para(
    "This section looks at the signs and symbols the subculture uses, and what they actually mean to "
    "the people inside it. The terms signifier, denotation and connotation are used because they matter "
    "when analysing meaning.",
    M, y - 8, CW, REG, 9.6, 14.2)
intro_end = y

lw = CW * 0.46
b.kicker("SIGNIFIERS \u2014 ICONS & SYMBOLS", M, y - 16)
yy = b.bullets([
    "Brand and tuning logos \u2014 the GT-R badge, the Honda \u201cH\u201d, and tuner names like Nismo, Mugen, "
    "Spoon, HKS, TRD and Advan",
    "The Japanese rising sun motif, plus katakana and kanji text on liveries and stickers",
    "Wheels \u2014 the Volk TE37 and deep-dish Work wheels are treated as sacred symbols of taste",
    "Sounds \u2014 the rotary \u201cbraaap\u201d, the blow-off valve \u201cpsh\u201d and the boxer rumble",
    "Low stance, wide fenders and aggressive camber",
    "Clothing and merch \u2014 branded hoodies, racing jackets, lanyards",
], M, y - 36, lw, 9.1, 13, 6)

rx = M + lw + 26
rw = CW - lw - 26
mb_top = intro_end - 12
b.img_fit(IMG("JDM Culture Moodboard.png"), rx, mb_top - rw, rw, rw)
b.para("Mood board of subculture signifiers collected during research: rising sun, kanji plates, "
       "TRD / NISMO / Mugen marks, the AE86 and Supra, koi tattoo art and \u201cTokyo Drift\u201d neon.",
       rx, mb_top - rw - 12, rw, OBL, 7.8, 10.6, GREY)

yb = yy - 34
b.kicker("HOW JDM YARD USES THESE SIGNIFIERS", M, yb)
yb = b.bullets([
    "Japanese type set beside English (the store header reads \u201cJapanese car specialist parts\u201d in kanji) "
    "\u2014 this signals heritage and insider knowledge.",
    "A red / black / off-white palette borrowed from motorsport and the Japanese flag, never bright or "
    "novelty colours.",
    "Magazine layout language: issue numbers, technical data strips, numbered plates \u2014 signifying "
    "seriousness and real information.",
    "Real photographs of a real owner's car, which signifies honesty and rejects fakes.",
], M, yb - 18, lw, 9.1, 13, 6)

# bilingual lock-up example (drawn with a Japanese font)
bx, byy, bw2 = M, yb - 92, lw
b.rect(bx, byy, bw2, 76, INK)
b.txt("SIGNIFIER IN USE \u00b7 THE BILINGUAL LOCK-UP", bx + 14, byy + 60, BOLD, 7.2, RED, space=1.8)
b.txt("JDM", bx + 14, byy + 34, BOLD, 20, WHITE, space=-0.5)
b.txt("YARD", bx + 58, byy + 34, BOLD, 20, RED, space=-0.5)
b.txt("\u65e5\u672c\u8eca\u5c02\u9580\u30d1\u30fc\u30c4", bx + 14, byy + 18, JP, 9, (0.78, 0.78, 0.82), space=1.5)
b.txt("\u672c\u7269\u306e\u30d1\u30fc\u30c4\u3002", bx + bw2 - 14, byy + 34, JP, 9, WHITE, space=1, align="r")
b.txt("REAL PARTS.", bx + bw2 - 14, byy + 18, BOLD, 8, RED, space=1.4, align="r")

b.para("English display type carries the meaning to every reader; the kanji and katakana carry the "
       "cultural signal to the people inside the subculture. Both are needed for the brand to be "
       "read correctly.",
       bx, byy - 16, bw2, REG, 8.8, 12.2, GREY)

# right column: signifiers on the actual car
rgy = yb - 18
b.kicker("SIGNIFIERS ON THE CAR ITSELF", rx, rgy)
ih2 = 108
b.img_cover(IMG("1.jpg"), rx, rgy - 14 - ih2, rw, ih2)
b.para("Badging, spoiler, smoked tail lights and a low stance \u2014 the owner's car is already covered in "
       "signifiers. The brand's job is to sell the parts that create them, using the same language.",
       rx, rgy - 28 - ih2, rw, OBL, 7.9, 10.8, GREY)
b.footer("Visual / Semiotic Analysis")

# =====================================================================
# 7 - SEMIOTIC ANALYSIS: MEANING TABLE + MISREADING
# =====================================================================
b.new()
y = b.section_head("05", "VISUAL / SEMIOTIC ANALYSIS", "MEANING & MISREADING")

b.kicker("DENOTATION VS CONNOTATION", M, y - 6)
ty = y - 26
c1, c2, c3 = CW * 0.26, CW * 0.31, CW * 0.43
b.rect(M, ty - 20, CW, 20, INK)
b.txt("SIGNIFIER", M + 10, ty - 13.5, BOLD, 7.4, WHITE, space=1.6)
b.txt("DENOTATION (LITERAL)", M + c1 + 10, ty - 13.5, BOLD, 7.4, WHITE, space=1.6)
b.txt("CONNOTATION (MEANING TO THE GROUP)", M + c1 + c2 + 10, ty - 13.5, BOLD, 7.2, WHITE, space=1.1)

table = [("Nismo / Mugen badge", "A performance parts brand logo",
          "Authenticity, motorsport history, \u201cthe real deal\u201d"),
         ("Volk TE37 wheels", "A lightweight forged wheel",
          "Status, good taste and serious commitment"),
         ("Rising sun / kanji decals", "Japanese imagery and writing",
          "Loyalty and respect to the Japanese roots of the culture"),
         ("Loud modified exhaust", "A car sound",
          "Presence, individuality and belonging"),
         ("Low stance / camber", "The car's height and wheel angle",
          "Style and dedication \u2014 giving up comfort for identity")]
ry = ty - 20
for i, (a, d, cn) in enumerate(table):
    h = 30
    if i % 2 == 0:
        b.rect(M, ry - h, CW, h, (0.917, 0.909, 0.898))
    b.para(a, M + 10, ry - 13, c1 - 20, BOLD, 8.5, 11)
    b.para(d, M + c1 + 10, ry - 13, c2 - 20, REG, 8.5, 11, GREY)
    b.para(cn, M + c1 + c2 + 10, ry - 13, c3 - 20, REG, 8.5, 11)
    ry -= h
b.line(M, ry, CW, LGREY)

b.kicker("COULD ANYONE MISINTERPRET THESE SYMBOLS?", M, ry - 26)
yy = b.para("Yes \u2014 and this matters as a designer, because the same symbol carries different meanings "
            "for different audiences:", M, ry - 44, CW * 0.92, REG, 9.4, 13.4)
yy = b.bullets([
    "A loud exhaust and a low car signify passion and craftsmanship to insiders, but to the wider "
    "public, older people or the police they can signify \u201cboy racer\u201d, antisocial behaviour or reckless driving.",
    "The rising sun motif reads as heritage and pride to enthusiasts, but in some countries it carries "
    "negative historical and political meanings, so it is easily misread.",
    "Big wings and body kits signify serious performance to the group, but outsiders may dismiss them "
    "as fake \u201cricer\u201d styling.",
], M, yy - 10, CW * 0.92, 9.1, 13, 6)

bh = 92
b.rect(M, yy - 12 - bh, CW, bh, INK)
b.rect(M, yy - 12 - bh, 4, bh, RED)
b.txt("WHY THIS MATTERS FOR THE DESIGN", M + 18, yy - 34, BOLD, 8, RED, space=2.2)
b.para("JDM YARD deliberately uses the coded symbols insiders recognise \u2014 Japanese type, motorsport "
       "red, technical data, real cars \u2014 but avoids the rising sun flag and \u201cboy racer\u201d imagery. The "
       "result speaks fluently to the subculture while still looking premium and legitimate to parents, "
       "retailers and the wider public who see the packaging or the website.",
       M + 18, yy - 52, CW - 36, REG, 9.2, 13.2, (0.88, 0.88, 0.9))
b.footer("Visual / Semiotic Analysis")

# =====================================================================
# 8 - PRODUCT: MOOD BOARD
# =====================================================================
b.new(dark=True)
y = b.section_head("06", "THE PRODUCT / DESIGN", "MOOD BOARD", col=WHITE)
b.para("The mood board fixes the visual direction before any layout is made: what the culture looks "
       "like, the colours it uses, the type it uses, and the tone the brand has to hit.",
       M, y - 6, CW * 0.8, REG, 9.5, 13.8, (0.82, 0.82, 0.86))

size = min(CW, 400)
b.img_fit(IMG("JDM Culture Moodboard.png"), M + (CW - size) / 2, y - 30 - size, size, size)

yb = y - 42 - size
b.kicker("WHAT WAS TAKEN FROM IT", M, yb)
col2 = (CW - 24) / 2
left = b.bullets([
    "Palette: black, off-white and a single motorsport red.",
    "Bilingual type \u2014 English display type locked with Japanese kana and kanji.",
    "Photographic tone: night-time, low light, wet tarmac, garage lighting.",
], M, yb - 18, col2, 9.1, 13, 6, (0.85, 0.85, 0.88))
b.bullets([
    "Print references: magazine covers, stickers, number plates, workshop labels.",
    "Icons kept: TRD / NISMO / Mugen style marks, kanji plates, tuner silhouettes.",
    "Icons avoided: rising sun flag, cartoon or novelty imagery.",
], M + col2 + 24, yb - 18, col2, 9.1, 13, 6, (0.85, 0.85, 0.88))

b.tagline_strip(64, 20, dark=False)
b.footer("The Product / Design", light=True)

# =====================================================================
# 9 - PRODUCT: DESIGN DEVELOPMENT
# =====================================================================
b.new()
y = b.section_head("07", "THE PRODUCT / DESIGN", "DEVELOPMENT & SKETCHES")

lw = CW * 0.52
b.img_fit(IMG("poster.png"), M, y - 400, lw, 392, align="l")
b.para("Final poster / magazine cover \u2014 JDM YARD Issue 01. A2 print, built on a strict grid: masthead, "
       "hero image, Japanese feature headline, three-frame photo strip and a technical data footer.",
       M, y - 414, lw, OBL, 7.9, 10.8, GREY)

rx = M + lw + 24
rw = CW - lw - 24
b.kicker("DESIGN DECISIONS", rx, y - 8)
yy = b.bullets([
    "Masthead set in heavy condensed capitals so it reads across a room at a car meet.",
    "A Japanese feature headline meaning \u201clegends of the strongest Z\u201d, to signal authenticity to "
    "insiders rather than translate for outsiders.",
    "Issue number and date block, copied from real Japanese car magazines.",
    "Technical data strip \u2014 engine, displacement, power, torque, 0\u2013100, kerb weight \u2014 because this "
    "audience respects real numbers.",
    "Photo strip of the owner's own car, captioned like an editorial feature.",
], rx, y - 26, rw, 8.9, 12.6, 6)

b.kicker("SKETCH DEVELOPMENT", rx, yy - 6)
sh = 150
b.frame(rx, yy - 24 - sh, rw, sh, GREY, 0.8, [3, 3])
b.txt("MOUNT SCANNED SKETCHES HERE", rx + rw / 2, yy - 24 - sh / 2 - 3, BOLD, 8, GREY,
      space=1.8, align="c")
b.txt("(hand-drawn masthead, layout thumbnails, sticker ideas)",
      rx + rw / 2, yy - 24 - sh / 2 - 18, REG, 7.6, GREY, align="c")
b.para("Layout thumbnails and masthead lettering were sketched by hand first, then rebuilt digitally. "
       "The printed sketch page is filed with this booklet for checking.",
       rx, yy - 38 - sh, rw, REG, 8.8, 12.2, GREY)
b.footer("The Product / Design")

# =====================================================================
# 10 - PRODUCT: WEBSITE + CONTACT SHEET
# =====================================================================
b.new()
y = b.section_head("08", "THE PRODUCT / DESIGN", "STORE & CONTACT SHEET")

_, _, iw, ih = b.img_fit(IMG("jdmyard.png"), M, y - 236, CW, 228)
b.para("jdmyard.com \u2014 the store applies the same design system: dark interface, bilingual category "
       "labels, six shopping categories, and a service bar promising flat-rate Australia-wide shipping, "
       "local support, easy returns and secure payment.",
       M, y - 250, CW, OBL, 8, 11, GREY)

yc = y - 276
b.kicker("PHOTOGRAPHY \u00b7 CONTACT SHEET", M, yc)
b.para("Nine frames were shot for the campaign and contact-sheeted for selection. The three exterior "
       "frames (golden hour, front end, three-quarter) were chosen for the poster strip, while the "
       "detail frames \u2014 wheel, engine bay, interior and diffuser \u2014 became the six store category tiles.",
       M, yc - 16, CW * 0.72, REG, 8.9, 12.4, GREY)

cs = 288
b.img_fit(IMG("Contact sheet.png"), M + (CW - cs) / 2, yc - 58 - cs, cs, cs)
b.footer("The Product / Design")

# =====================================================================
# 11 - MARKETING PLAN
# =====================================================================
b.new()
y = b.section_head("09", "SECTION", "MARKETING PLAN")

colw = (CW - 26) / 2
b.kicker("KEY FEATURES", M, y - 6)
yy = b.bullets([
    "Genuine JDM and quality aftermarket parts across six categories.",
    "Model-specific fitment \u2014 search by chassis code (Z34, S15, FD3S, R34).",
    "Flat-rate shipping Australia-wide; local phone support on 1300 647 2451.",
    "Easy returns and secure payment \u2014 Afterpay, Zip and PayPal.",
    "Free JDM YARD magazine and sticker pack in every order.",
], M, y - 24, colw, 9, 12.6, 5.5)

b.kicker("WHY IT APPEALS TO THE SUBCULTURE", M, yy - 6)
yy = b.bullets([
    "It uses the culture's own visual language instead of generic retail styling.",
    "It backs the values the group ranks highest: authenticity, heritage and quality.",
    "Limited runs and customisable options let buyers feel individual yet part of the club.",
    "Real numbers and real cars respect the group's obsession with knowledge.",
], M, yy - 24, colw, 9, 12.6, 5.5)

x2 = M + colw + 26
b.kicker("WHO WILL BUY IT", x2, y - 6)
yb = b.bullets([
    "Primary: male and female enthusiasts 18\u201330 who own a JDM car or badly want one \u2014 active on "
    "social media, attend meets, and display their identity through what they buy.",
    "Secondary: younger fans 16\u201318 buying affordable merch, posters and stickers.",
    "Tertiary: collectors paying more for premium, limited-edition pieces.",
], x2, y - 24, colw, 9, 12.6, 5.5)

b.kicker("WHERE IT WILL BE SOLD", x2, yb - 6)
yb = b.bullets([
    "Online at jdmyard.com \u2014 the main channel.",
    "Instagram shop and TikTok Shop links for impulse merch.",
    "Stalls at car meets, shows and track days, where the poster and zine do the selling.",
    "Selected local workshops stocking consumables and stickers.",
], x2, yb - 24, colw, 9, 12.6, 5.5)

yl = min(yy, yb) - 12
BOXH = 128
b.rect(M, yl - BOXH, CW, BOXH, INK)
b.txt("HOW IT WILL BE ADVERTISED", M + 18, yl - 24, BOLD, 8, RED, space=2.4)
adv = [("SOCIAL MEDIA", "Instagram and TikTok reels: install clips, before-and-after builds, dyno "
                        "results. Short, loud, vertical."),
       ("CREATORS", "Paid and gifted partnerships with Australian car content creators and drift "
                    "drivers \u2014 parts fitted on camera."),
       ("PRINT", "The Issue 01 poster handed out at meets, plus stickers in every box \u2014 cheap, "
                 "long-lasting advertising on real cars."),
       ("OWNER FEATURES", "Customers' cars featured in the magazine and on the site, which turns "
                          "buyers into advocates.")]
aw = (CW - 36 - 3 * 14) / 4
for i, (t, d) in enumerate(adv):
    ax = M + 18 + i * (aw + 14)
    b.rect(ax, yl - 46, aw, 2.5, RED)
    b.txt(t, ax, yl - 62, BOLD, 7.8, WHITE, space=1.2)
    b.para(d, ax, yl - 78, aw, REG, 8.3, 11.6, (0.82, 0.82, 0.86))

# closing band: where the money comes from
band_y = yl - BOXH - 118
b.img_cover(IMG("1.jpg"), M, band_y, CW * 0.46, 104)
rx3 = M + CW * 0.46 + 18
b.kicker("SALES FUNNEL, SIMPLIFIED", rx3, band_y + 92)
b.bullets([
    "See the car content on Instagram or TikTok \u2192 follow the account.",
    "Meet the brand in person at a car meet \u2192 take a free poster and stickers.",
    "Buy a small part or merch item \u2192 receive Issue 01 in the box.",
    "Come back for the expensive parts \u2014 wheels, exhaust and aero.",
], rx3, band_y + 74, CW - CW * 0.46 - 18, 8.6, 12, 3.4)
b.footer("Marketing Plan")

# =====================================================================
# 12 - CONCLUSION / CALL TO ACTION
# =====================================================================
b.new(dark=True)
b.img_cover(IMG("3.JPG"), 0, PH - 300, PW, 300)
b.rect(0, PH - 300, PW, 300, INK, 0.55)
b.txt("10", M, PH - 96, BOLD, 44, RED, space=-1.5)
b.kicker("SECTION", M + 58, PH - 82)
b.heading("CONCLUSION / CALL TO ACTION", M + 58, PH - 110, 24, WHITE)

y = PH - 330
b.kicker("WHY THIS PRODUCT SUCCEEDS FOR THIS SUBCULTURE", M, y)
y = b.para(
    "JDM YARD works because every decision came out of the research rather than being decorated on "
    "afterwards. The subculture values authenticity, craftsmanship, heritage and knowledge \u2014 so the "
    "brand sells genuine parts, publishes real specifications, photographs real owner cars, and sets "
    "Japanese type next to English to show it understands where the culture came from. The semiotic "
    "research also told the brand what to leave out, which is why the rising sun and \u201cboy racer\u201d "
    "signals are avoided: they read badly outside the group and would cost the brand legitimacy.",
    M, y - 20, CW, REG, 10, 15, (0.88, 0.88, 0.9))

y = b.para(
    "The result is one consistent identity across three touchpoints \u2014 the store, the magazine and the "
    "poster \u2014 aimed at a defined buyer, sold through the channels that buyer already uses, and priced "
    "so both a 17-year-old buying a sticker pack and a collector buying forged wheels can join in.",
    M, y - 10, CW, REG, 10, 15, (0.88, 0.88, 0.9))

b.rect(M, y - 128, CW, 108, RED)
b.txt("BUILD IT PROPERLY.", M + 22, y - 52, BOLD, 24, WHITE, space=-0.4)
b.para("Shop the full range at jdmyard.com, follow @jdmyard for build content, and grab Issue 01 free "
       "with your first order. Real parts. Real owners. Real performance.",
       M + 22, y - 74, CW - 44, REG, 10, 14, WHITE)

b.txt("\u672c\u7269\u306e\u30d1\u30fc\u30c4\u3002\u672c\u7269\u306e\u30d1\u30d5\u30a9\u30fc\u30de\u30f3\u30b9\u3002",
      M, y - 154, JP, 11, WHITE, space=1.5)
b.txt("JDMYARD.COM  \u00b7  @JDMYARD  \u00b7  1300 647 2451", PW - M, y - 154, BOLD, 9, RED,
      space=1.6, align="r")

sw = (CW - 2 * 9) / 3
b.img_cover(IMG("5.jpg"), M, 92, sw, 96)
b.img_cover(IMG("4.jpg"), M + sw + 9, 92, sw, 96)
b.img_cover(IMG("8.jpg"), M + 2 * (sw + 9), 92, sw, 96)
b.footer("Conclusion / Call to Action", light=True)

b.save()
print("wrote", OUT, os.path.getsize(OUT), "bytes")
