#!/usr/bin/env python3
"""
JDM YARD magazine-style poster.

A4 cover poster: dense top strip, masthead block, full-bleed hero carrying a
round badge / stacked kanji headline / cover lines / issue box, then three
owner cards over a social bar. Finished with a halftone + grain print pass.

Typographic density (stacked outlined kanji, marker-led cover lines, gold and
red on near-black, issue box, print texture) follows Japanese car-magazine
convention. All branding and copy are JDM Yard's own - no third-party
magazine name, logo or trade dress is reproduced.

Usage:  python3 poster.py                 # 1654 x 2339  (A4 @ 200dpi)
        POSTER_W=2480 python3 poster.py   # A4 @ 300dpi, print
Output: out/poster.png
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

from build import (jdm_grade, cover, blur_regions, font, track, track_w,
                   vgrad, FONTS, ASSETS)

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- canvas
W = int(os.environ.get("POSTER_W", 1654))
H = int(round(W * 297 / 210.0))            # A4 portrait
SC = W / 1654.0


def s(px):
    return max(1, int(round(px * SC)))


# ---------------------------------------------------------------- palette
BLACK = (9, 9, 11)
INK = (15, 15, 18)
PANEL = (13, 13, 16)
RED = (198, 20, 30)
RED_HI = (232, 42, 52)
GOLD = (228, 182, 62)
GOLD_DIM = (150, 118, 38)
WHITE = (255, 255, 255)
BONE = (236, 236, 240)
GREY = (150, 150, 156)
DIM = (104, 104, 111)
HAIR = (46, 46, 52)

# ---------------------------------------------------------------- copy
# Top strip: short dense cover lines, marker-separated
STRIP_ITEMS = ["最新パーツ情報", "REAL PARTS", "実測データ", "REAL PERFORMANCE"]

MAST_1, MAST_2 = "JDM", "YARD"
SUBHEAD = "MAGAZINE"
TAGLINE = "Home Of Modified And JDM Cars"
JP_TAGLINE = "日本車専門誌"

BADGE = ("TUNED", "MODIFIED", "PERFECTED")

# hero
HEAD_1 = "JDM CLASSICS"
HEAD_2 = "THE Z34"
STACK = ["最強", "ゼット", "列伝"]          # "strongest Z chronicles"
STACK_YEARS = "2009 → 2020"
BANNER_JP = "特集"                          # "special feature"

# marker-led cover lines, right side of the hero
COVER_LINES = [
    ("VQ37VHR", "実測パワー検証"),
    ("WHEELS", "ホイール徹底比較"),
    ("AERO", "エアロパーツ新作情報"),
    ("EXHAUST", "排気系チューン完全ガイド"),
    ("SUSPENSION", "足回りセッティングの基礎"),
]

ISSUE_NO = "01"
ISSUE_DATE = "2026年8月"
ISSUE_EN = "AUGUST"

FEATURE = dict(name="Owner Name", car="2013 Nissan 370Z", ig="@yourhandle")

# Plate is legible in 8.jpg (dead-on front). Same treatment as 2.jpg.
PLATE_8 = [(0.345, 0.636, 0.672, 0.714)]

# three owner cards along the bottom
CARDS = [
    dict(src="7.jpg", idx="01", jp="夕陽のZ", name="Owner One",
         car="370Z · Golden Hour", ig="@handle_one",
         bias_y=0.42, zoom=1.06, expo=0.94, plate=None),
    dict(src="8.jpg", idx="02", jp="正面", name="Owner Two",
         car="370Z · Front End", ig="@handle_two",
         bias_y=0.40, zoom=1.04, expo=0.98, plate=PLATE_8),
    dict(src="9.jpg", idx="03", jp="斜め前", name="Owner Three",
         car="370Z · Three Quarter", ig="@handle_three",
         bias_y=0.48, zoom=1.12, expo=0.96, plate=None),
]

# hero photo
HERO = dict(src="1.jpg", bias_y=0.52, zoom=1.04, expo=0.96, plate=None)

# Variant B: promote the golden-hour shot to the hero. 1.jpg is a tight crop of
# spoiler and taillight - it does not read as a car at cover size. 7.jpg is the
# only full-car shot dramatic enough to carry the page, so it moves up and the
# wheel shot backfills the third card.
if os.environ.get("POSTER_VARIANT", "a").lower() == "b":
    HERO = dict(src="7.jpg", bias_y=0.46, zoom=1.02, expo=0.92, plate=None)
    CARDS = [
        dict(src="8.jpg", idx="01", jp="正面", name="Owner One",
             car="370Z · Front End", ig="@handle_one",
             bias_y=0.40, zoom=1.04, expo=0.98, plate=PLATE_8),
        dict(src="9.jpg", idx="02", jp="斜め前", name="Owner Two",
             car="370Z · Three Quarter", ig="@handle_two",
             bias_y=0.48, zoom=1.12, expo=0.96, plate=None),
        dict(src="3.JPG", idx="03", jp="ホイール", name="Owner Three",
             car="370Z · Forged Wheels", ig="@handle_three",
             bias_y=0.46, zoom=1.02, expo=0.96, plate=None),
    ]

BOT_L1, BOT_L2 = "FIND US ON", "SOCIAL MEDIA"
BOT_HANDLE = "@jdmyard"
BOT_M1 = "YOUR MONTHLY DOSE OF"
BOT_M2 = "INSPIRATION. MOTIVATION. STANCE."
BOT_R1, BOT_R2 = "GET", "INSPIRED"
BOT_R3, BOT_R4 = "SHARE", "THE PASSION"

# ---------------------------------------------------------------- fonts
ANTON = FONTS / "Anton-Regular.ttf"
KAUSHAN = FONTS / "KaushanScript-Regular.ttf"
ARCHIVO = FONTS / "Archivo[wdth,wght].ttf"
OSWALD = FONTS / "Oswald[wght].ttf"
ROBOTO = FONTS / "RobotoCondensed.ttf"
NOTOJP = FONTS / "NotoSansJP[wght].ttf"


def anton(sz):
    return font(ANTON, s(sz))


def kaushan(sz):
    return font(KAUSHAN, s(sz))


def arch(sz, w="SemiBold"):
    return font(ARCHIVO, s(sz), w)


def osw(sz, w="Bold"):
    return font(OSWALD, s(sz), w)


def rob(sz, w="Regular"):
    return font(ROBOTO, s(sz), w)


def njp(sz, w="Medium"):
    return font(NOTOJP, s(sz), w)


# ---------------------------------------------------------------- helpers
def load(spec, tw, th):
    """Graded, cropped photo for a spec dict. Falls back to a dark panel."""
    p = ASSETS / spec["src"]
    if not p.exists():
        im = Image.new("RGB", (tw, th), (30, 31, 34))
        d = ImageDraw.Draw(im)
        f = rob(15, "Bold")
        t = f"[ {spec['src']} missing ]"
        d.text(((tw - d.textlength(t, font=f)) / 2, th / 2), t, font=f,
               fill=(96, 96, 102))
        return im, False
    img = Image.open(p).convert("RGB")
    if spec.get("plate"):
        img = blur_regions(img, spec["plate"])
    img = cover(img, tw, th, spec.get("bias_y", 0.5), 0.5, spec.get("zoom", 1.0))
    img = jdm_grade(img)
    e = spec.get("expo", 1.0)
    if e != 1.0:
        img = ImageEnhance.Brightness(img).enhance(e)
    return img, True


def scrim_bottom(img, frac, peak, gamma=1.8):
    w, h = img.size
    sh = int(h * frac)
    ramp = vgrad((w, sh), 0, peak, gamma=gamma)
    region = img.crop((0, h - sh, w, h))
    region = Image.composite(Image.new("RGB", (w, sh), (0, 0, 0)), region, ramp)
    img.paste(region, (0, h - sh))
    return img


def scrim_top(img, px, peak):
    w, h = img.size
    ramp = vgrad((w, px), peak, 0, gamma=0.85)
    region = img.crop((0, 0, w, px))
    region = Image.composite(Image.new("RGB", (w, px), (0, 0, 0)), region, ramp)
    img.paste(region, (0, 0))
    return img


def soft_shadow(canvas, box, draw_fn, blur=5, boost=2.3):
    """Blurred black behind type so it survives any background."""
    x0, y0, x1, y1 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(canvas.width, x1), min(canvas.height, y1)
    mw, mh = x1 - x0, y1 - y0
    if mw <= 0 or mh <= 0:
        return
    mask = Image.new("L", (mw, mh), 0)
    draw_fn(ImageDraw.Draw(mask), -x0, -y0)
    mask = mask.filter(ImageFilter.GaussianBlur(s(blur)))
    mask = mask.point(lambda v: min(255, int(v * boost)))
    canvas.paste(Image.new("RGB", (mw, mh), (0, 0, 0)), (x0, y0), mask)


def star(d, cx, cy, r, fill):
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def badge(size):
    ss = 4
    d0 = size * ss
    im = Image.new("RGBA", (d0, d0), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, d0 - 1, d0 - 1], fill=(150, 12, 20, 255))
    d.ellipse([0, 0, d0 - 1, d0 - 1], outline=(255, 255, 255, 195),
              width=max(1, d0 // 42))
    inset = d0 * 0.055
    d.ellipse([inset, inset, d0 - inset, d0 - inset],
              outline=(232, 182, 62, 130), width=max(1, d0 // 80))
    im = im.resize((size, size), Image.LANCZOS)

    d = ImageDraw.Draw(im)
    f = font(ARCHIVO, max(7, int(size * 0.115)), "Bold")
    for t, fy in zip(BADGE, (0.24, 0.42, 0.60)):
        sp = max(1, int(size * 0.012))
        tw = track_w(d, t, f, sp)
        track(d, ((size - tw) / 2, size * fy), t, f, WHITE + (255,), spacing=sp)
    cy = size * 0.80
    cw = size * 0.42
    cx = (size - cw) / 2
    d.rounded_rectangle([cx, cy, cx + cw, cy + size * 0.085],
                        radius=size * 0.03, outline=WHITE + (230,),
                        width=max(1, size // 60))
    d.arc([cx + cw * 0.16, cy - size * 0.055, cx + cw * 0.84, cy + size * 0.055],
          180, 360, fill=WHITE + (230,), width=max(1, size // 60))
    return im


def diagonal_banner(text, box_w, box_h, angle=-14):
    """Red corner flash with gold Japanese text, rotated."""
    ss = 3
    im = Image.new("RGBA", (box_w * ss, box_h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, box_w * ss, box_h * ss], fill=(190, 18, 28, 245))
    d.rectangle([0, 0, box_w * ss, box_h * ss], outline=(232, 182, 62, 220),
                width=max(1, int(3 * ss * SC)))
    f = font(NOTOJP, int(box_h * ss * 0.52), "Black")
    tw = d.textlength(text, font=f)
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((box_w * ss - tw) / 2, (box_h * ss - (bb[3] - bb[1])) / 2 - bb[1]),
           text, font=f, fill=(246, 226, 160, 255))
    im = im.resize((box_w, box_h), Image.LANCZOS)
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def print_pass(img, dot_alpha=0.055, grain=0.10, warm=6):
    """Halftone dot screen + grain + slight warm tint - a print feel."""
    w, h = img.size
    cell = max(3, s(5))
    # dot screen tile
    tile = Image.new("L", (cell, cell), 255)
    td = ImageDraw.Draw(tile)
    r = max(1, cell * 0.30)
    td.ellipse([cell / 2 - r, cell / 2 - r, cell / 2 + r, cell / 2 + r], fill=170)
    screen = Image.new("L", (w + cell, h + cell))
    for y in range(0, h + cell, cell):
        for x in range(0, w + cell, cell):
            screen.paste(tile, (x, y))
    screen = screen.crop((0, 0, w, h)).filter(ImageFilter.GaussianBlur(0.6))
    img = Image.blend(img, ImageChops.multiply(img, screen.convert("RGB")),
                      dot_alpha)

    # grain
    noise = Image.effect_noise((w, h), 12).convert("RGB")
    img = Image.blend(img, ImageChops.add(img, noise, scale=1.0, offset=-112),
                      grain)

    # warm tint
    r_, g_, b_ = img.split()
    r_ = r_.point(lambda v: min(255, v + warm))
    b_ = b_.point(lambda v: max(0, v - warm // 2))
    return Image.merge("RGB", (r_, g_, b_))


# ---------------------------------------------------------------- build
def build_poster():
    canvas = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(canvas)

    # ---------------- geometry
    strip_h = s(40)
    mast_h = s(352)
    bot_h = s(126)
    card_pad = s(20)
    card_img_h = s(408)
    card_txt_h = s(104)
    cards_block = card_pad + card_img_h + card_txt_h

    hero_top = strip_h + mast_h
    hero_h = H - strip_h - mast_h - bot_h - cards_block
    hero_bot = hero_top + hero_h
    cards_top = hero_bot

    # ================================================ TOP STRIP
    d.rectangle([0, 0, W, strip_h], fill=INK)
    d.rectangle([0, 0, s(10), strip_h], fill=RED)
    d.line([(0, strip_h - 1), (W, strip_h - 1)], fill=GOLD_DIM, width=s(1))

    f_sj = njp(13, "Medium")
    f_se = arch(11, "Bold")
    widths = []
    for i, t in enumerate(STRIP_ITEMS):
        f = f_se if t.isascii() else f_sj
        widths.append(track_w(d, t, f, s(2.0)))
    marker = s(22)
    total = sum(widths) + marker * (len(STRIP_ITEMS) - 1)
    sx = (W - total) / 2 + s(6)
    for i, t in enumerate(STRIP_ITEMS):
        f = f_se if t.isascii() else f_sj
        col = GOLD if t.isascii() else BONE
        track(d, (sx, strip_h / 2 - s(8)), t, f, col, spacing=s(2.0))
        sx += widths[i]
        if i < len(STRIP_ITEMS) - 1:
            cx = sx + marker / 2
            d.rectangle([cx - s(2.5), strip_h / 2 - s(2.5),
                         cx + s(2.5), strip_h / 2 + s(2.5)], fill=RED_HI)
            sx += marker

    # ================================================ MASTHEAD
    d.rectangle([0, strip_h, W, hero_top], fill=BLACK)
    glow = Image.new("RGB", (W, mast_h), BLACK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.12, mast_h * 0.10, W * 0.88, mast_h * 0.78],
               fill=(48, 9, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(s(70)))
    canvas.paste(glow, (0, strip_h))
    d = ImageDraw.Draw(canvas)

    f_mast = anton(146)
    sp = s(-2)
    w1 = track_w(d, MAST_1, f_mast, sp)
    w2 = track_w(d, MAST_2, f_mast, sp)
    gap = s(14)
    mx = (W - (w1 + gap + w2)) / 2
    my = strip_h + s(26)
    track(d, (mx, my), MAST_1, f_mast, WHITE, spacing=sp)
    track(d, (mx + w1 + gap, my), MAST_2, f_mast, RED_HI, spacing=sp)
    mast_ink_bot = d.textbbox((mx, my), MAST_1 + MAST_2, font=f_mast)[3]

    # stars + MAGAZINE, flanked by gold rules
    f_sub = anton(44)
    subw = track_w(d, SUBHEAD, f_sub, s(10))
    star_r = s(13)
    star_block = star_r * 6.6
    total = star_block + s(26) + subw
    sx = (W - total) / 2
    sy = mast_ink_bot + s(14)
    for k in range(3):
        star(d, sx + star_r + k * star_r * 2.6, sy + s(24), star_r, GOLD)
    track(d, (sx + star_block + s(26), sy), SUBHEAD, f_sub, BONE, spacing=s(10))
    sub_bot = d.textbbox((0, sy), SUBHEAD, font=f_sub)[3]
    ry = sy + s(24)
    d.line([(s(60), ry), (sx - s(28), ry)], fill=GOLD_DIM, width=s(1))
    d.line([(sx + total + s(20), ry), (W - s(60), ry)], fill=GOLD_DIM, width=s(1))

    f_tag = rob(17, "Regular")
    tw = d.textlength(TAGLINE, font=f_tag)
    d.text(((W - tw) / 2, sub_bot + s(12)), TAGLINE, font=f_tag, fill=GREY)
    f_jt = njp(14, "Medium")
    jw = track_w(d, JP_TAGLINE, f_jt, s(4))
    jp_y = sub_bot + s(40)
    track(d, ((W - jw) / 2, jp_y), JP_TAGLINE, f_jt, (156, 48, 56), spacing=s(4))

    mast_content_bot = d.textbbox((0, jp_y), JP_TAGLINE, font=f_jt)[3]
    if mast_content_bot > hero_top - s(6):
        print(f"  WARNING masthead overflows: {mast_content_bot} vs "
              f"hero_top {hero_top} - raise mast_h by "
              f"~{mast_content_bot - hero_top + s(12)}px")
    else:
        print(f"  masthead fits: clearance "
              f"{hero_top - mast_content_bot}px")

    # ================================================ HERO
    hero, hero_ok = load(HERO, W, hero_h)
    hero = scrim_bottom(hero, 0.46, 220, gamma=1.9)
    hero = scrim_top(hero, s(190), 195)
    canvas.paste(hero, (0, hero_top))
    d = ImageDraw.Draw(canvas)

    # ---- English headline, centred upper
    f_h1 = anton(96)
    f_h2 = kaushan(70)
    h1w = track_w(d, HEAD_1, f_h1, s(1))
    hx = (W - h1w) / 2
    hy = hero_top + s(58)

    def _h(md, ox, oy):
        track(md, (hx + ox, hy + oy), HEAD_1, f_h1, 255, spacing=s(1))
    soft_shadow(canvas, (hx - s(50), hy - s(36), hx + h1w + s(50), hy + s(150)),
                _h, blur=8, boost=2.0)
    d = ImageDraw.Draw(canvas)
    track(d, (hx, hy), HEAD_1, f_h1, WHITE, spacing=s(1))

    h1_bot = d.textbbox((hx, hy), HEAD_1, font=f_h1)[3]
    h2_bb = d.textbbox((0, 0), HEAD_2, font=f_h2)
    h2_tw, h2_th = h2_bb[2] - h2_bb[0], h2_bb[3] - h2_bb[1]
    padx, pady = s(40), s(30)
    h2_layer = Image.new("RGBA", (h2_tw + padx * 2, h2_th + pady * 2),
                         (0, 0, 0, 0))
    h2d = ImageDraw.Draw(h2_layer)
    h2d.text((padx - h2_bb[0], pady - h2_bb[1]), HEAD_2, font=f_h2,
             fill=GOLD + (255,), stroke_width=max(1, s(3)),
             stroke_fill=(22, 16, 5, 240))
    h2_layer = h2_layer.transform(h2_layer.size, Image.AFFINE,
                                  (1, 0.22, -s(20), 0, 1, 0),
                                  resample=Image.BICUBIC)
    canvas.paste(h2_layer, (int(hx + h1w - h2_tw - padx * 1.2),
                            int(h1_bot - s(8))), h2_layer)
    d = ImageDraw.Draw(canvas)

    # ---- badge, upper left
    bsz = s(178)
    bimg = badge(bsz)
    canvas.paste(bimg, (s(30), hero_top + s(34)), bimg)
    d = ImageDraw.Draw(canvas)

    # ---- diagonal 特集 banner, upper right
    ban = diagonal_banner(BANNER_JP, s(150), s(66), angle=-14)
    canvas.paste(ban, (W - ban.width - s(24), hero_top + s(30)), ban)
    d = ImageDraw.Draw(canvas)

    # ---- stacked kanji headline, lower left
    f_st = njp(92, "Black")
    st_x = s(38)
    line_h = s(96)
    # lifted clear of the feature strip below - the gold year chip and the
    # script owner name were overlapping by ~12px
    st_y = hero_bot - s(210) - line_h * len(STACK)
    for i, ln in enumerate(STACK):
        ly = st_y + i * line_h
        # offset drop shadow, then gold outline over white
        d.text((st_x + s(7), ly + s(7)), ln, font=f_st, fill=(8, 6, 6))
        d.text((st_x, ly), ln, font=f_st, fill=WHITE,
               stroke_width=max(1, s(4)), stroke_fill=RED)
    f_yr = arch(19, "Bold")
    yw = track_w(d, STACK_YEARS, f_yr, s(2))
    yy = st_y + line_h * len(STACK) + s(6)
    d.rectangle([st_x, yy, st_x + yw + s(20), yy + s(32)], fill=GOLD)
    track(d, (st_x + s(10), yy + s(7)), STACK_YEARS, f_yr, (24, 18, 6),
          spacing=s(2))

    # ---- marker-led cover lines, right side
    f_cl_en = arch(15, "Bold")
    f_cl_jp = njp(17, "Medium")
    cl_right = W - s(34)
    cl_y = hero_top + hero_h * 0.44
    for en, jp_ in COVER_LINES:
        ew = track_w(d, en, f_cl_en, s(1.6))
        jw2 = track_w(d, jp_, f_cl_jp, s(1.2))
        block_w = max(ew, jw2)
        bx = cl_right - block_w
        # red marker bar
        d.rectangle([bx - s(14), cl_y + s(2), bx - s(7), cl_y + s(40)],
                    fill=RED_HI)
        shx, shy = bx, cl_y

        def _cl(md, ox, oy, _e=en, _j=jp_, _ew=ew, _jw=jw2):
            track(md, (shx + ox + (block_w - _ew), shy + oy), _e, f_cl_en, 255,
                  spacing=s(1.6))
            track(md, (shx + ox + (block_w - _jw), shy + oy + s(20)), _j,
                  f_cl_jp, 255, spacing=s(1.2))
        soft_shadow(canvas, (bx - s(30), cl_y - s(12),
                             cl_right + s(20), cl_y + s(56)),
                    _cl, blur=4, boost=2.6)
        d = ImageDraw.Draw(canvas)
        track(d, (bx + (block_w - ew), cl_y), en, f_cl_en, GOLD, spacing=s(1.6))
        track(d, (bx + (block_w - jw2), cl_y + s(20)), jp_, f_cl_jp, BONE,
              spacing=s(1.2))
        cl_y += s(58)

    # ---- issue box, bottom right
    ib_w, ib_h = s(150), s(104)
    ib_x, ib_y = W - ib_w - s(30), hero_bot - ib_h - s(26)
    d.rectangle([ib_x, ib_y, ib_x + ib_w, ib_y + ib_h], fill=GOLD)
    d.rectangle([ib_x, ib_y, ib_x + ib_w, ib_y + ib_h], outline=(24, 18, 6),
                width=s(2))
    f_no = anton(60)
    nb = d.textbbox((0, 0), ISSUE_NO, font=f_no)
    d.text((ib_x + (ib_w - (nb[2] - nb[0])) / 2 - nb[0], ib_y + s(4) - nb[1]),
           ISSUE_NO, font=f_no, fill=(24, 18, 6))
    f_id = njp(14, "Bold")
    iw = track_w(d, ISSUE_DATE, f_id, s(1))
    track(d, (ib_x + (ib_w - iw) / 2, ib_y + s(64)), ISSUE_DATE, f_id,
          (40, 30, 10), spacing=s(1))
    f_ie = arch(11, "Bold")
    ew2 = track_w(d, ISSUE_EN, f_ie, s(2.4))
    track(d, (ib_x + (ib_w - ew2) / 2, ib_y + s(85)), ISSUE_EN, f_ie,
          (70, 54, 18), spacing=s(2.4))

    # ---- feature strip, bottom left
    fy = hero_bot - s(112)
    d.rectangle([0, fy - s(4), s(10), fy + s(96)], fill=RED)
    f_name = kaushan(46)
    f_meta = rob(16, "Regular")
    d.text((s(28), fy - s(12)), FEATURE["name"], font=f_name,
           fill=(240, 226, 176), stroke_width=max(1, s(2)),
           stroke_fill=(18, 14, 6))
    d.text((s(30), fy + s(46)), FEATURE["car"], font=f_meta, fill=BONE)
    d.text((s(30), fy + s(68)), f"Instagram: {FEATURE['ig']}", font=f_meta,
           fill=GREY)

    # ================================================ OWNER CARDS
    d.rectangle([0, cards_top, W, cards_top + cards_block], fill=PANEL)
    d.line([(0, cards_top), (W, cards_top)], fill=GOLD_DIM, width=s(2))

    pad = s(20)
    gap = s(16)
    cw = (W - pad * 2 - gap * 2) // 3
    for i, c in enumerate(CARDS):
        cx = pad + (cw + gap) * i
        cy = cards_top + card_pad
        ph, ok = load(c, cw, card_img_h)
        canvas.paste(ph, (cx, cy))
        d = ImageDraw.Draw(canvas)
        d.rectangle([cx, cy, cx + cw - 1, cy + card_img_h - 1], outline=HAIR,
                    width=max(1, s(1)))

        # index chip over the photo corner
        chip = s(40)
        d.rectangle([cx, cy, cx + chip, cy + chip], fill=GOLD)
        f_ix = anton(24)
        ib = d.textbbox((0, 0), c["idx"], font=f_ix)
        d.text((cx + (chip - (ib[2] - ib[0])) / 2 - ib[0],
                cy + (chip - (ib[3] - ib[1])) / 2 - ib[1]),
               c["idx"], font=f_ix, fill=(24, 18, 6))

        ty = cy + card_img_h + s(12)
        f_jl = njp(13, "Medium")
        f_cn = osw(20, "SemiBold")
        f_cm = rob(14, "Regular")
        track(d, (cx + s(2), ty), c["jp"], f_jl, RED_HI, spacing=s(1.5))
        track(d, (cx + s(2), ty + s(22)), c["name"], f_cn, WHITE, spacing=s(0.5))
        d.text((cx + s(2), ty + s(48)), c["car"], font=f_cm, fill=BONE)
        d.text((cx + s(2), ty + s(68)), f"Instagram: {c['ig']}", font=f_cm,
               fill=DIM)

    # ================================================ BOTTOM BAR
    by0 = H - bot_h
    d.rectangle([0, by0, W, H], fill=BLACK)
    d.line([(0, by0), (W, by0)], fill=RED, width=s(3))

    f_b1 = arch(15, "Bold")
    f_b2 = rob(15, "Regular")
    track(d, (s(30), by0 + s(28)), BOT_L1, f_b1, WHITE, spacing=s(1.2))
    track(d, (s(30), by0 + s(50)), BOT_L2, f_b1, WHITE, spacing=s(1.2))
    d.text((s(30), by0 + s(76)), BOT_HANDLE, font=f_b2, fill=GOLD)

    mid_x = W * 0.40
    track(d, (mid_x, by0 + s(34)), BOT_M1, f_b1, WHITE, spacing=s(1.4))
    track(d, (mid_x, by0 + s(58)), BOT_M2, f_b1, RED_HI, spacing=s(1.4))

    right_margin = s(30)
    lbl_sp = s(1)
    w_pass = max(track_w(d, BOT_R3, f_b1, lbl_sp),
                 track_w(d, BOT_R4, f_b1, lbl_sp))
    w_insp = max(track_w(d, BOT_R1, f_b1, lbl_sp),
                 track_w(d, BOT_R2, f_b1, lbl_sp))
    icon_w, icon_gap, pair_gap = s(32), s(12), s(34)

    ex_lbl = W - right_margin - w_pass
    ex = ex_lbl - icon_gap - icon_w
    d.rectangle([ex, by0 + s(36), ex + icon_w, by0 + s(58)], outline=WHITE,
                width=max(1, s(1)))
    d.line([(ex, by0 + s(36)), (ex + icon_w / 2, by0 + s(50))], fill=WHITE,
           width=max(1, s(1)))
    d.line([(ex + icon_w, by0 + s(36)), (ex + icon_w / 2, by0 + s(50))],
           fill=WHITE, width=max(1, s(1)))
    track(d, (ex_lbl, by0 + s(34)), BOT_R3, f_b1, WHITE, spacing=lbl_sp)
    track(d, (ex_lbl, by0 + s(54)), BOT_R4, f_b1, WHITE, spacing=lbl_sp)

    rx_lbl = ex - pair_gap - w_insp
    rx = rx_lbl - icon_gap - icon_w
    hr = icon_w / 2
    d.polygon([(rx, by0 + s(47)), (rx + hr, by0 + s(34)),
               (rx + hr * 2, by0 + s(47)), (rx + hr, by0 + s(62))],
              outline=WHITE)
    track(d, (rx_lbl, by0 + s(34)), BOT_R1, f_b1, WHITE, spacing=lbl_sp)
    track(d, (rx_lbl, by0 + s(54)), BOT_R2, f_b1, WHITE, spacing=lbl_sp)

    # ================================================ PRINT PASS
    canvas = print_pass(canvas)

    suffix = "" if W == 1654 else f"@{W}"
    out = OUT / f"poster{suffix}.png"
    canvas.save(out, "PNG")
    cards = ", ".join(c["src"] for c in CARDS)
    print(f"wrote {out}  ({W}x{H})  hero={HERO['src']}  cards=[{cards}]")
    return out


if __name__ == "__main__":
    build_poster()
