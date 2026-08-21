#!/usr/bin/env python3
"""
JDM YARD poster - aged Japanese car-magazine treatment.

Cream stock rather than black. Oversized masthead that the hero photo cuts
across, giant stacked kanji with hard offset shadows, category-chipped cover
lines, a red banner, a big issue block, and three bordered owner cards.
Finished with a warm faded grade, halftone screen and paper texture.

Layout language follows Japanese car-magazine convention. All branding and
copy are JDM Yard's own - no third-party magazine name, logo, masthead or
trade dress is reproduced.

Usage:  python3 poster.py                 # 1654 x 2339  (A4 @ 200dpi)
        POSTER_W=2480 python3 poster.py   # A4 @ 300dpi, print
Output: out/poster.png
"""

import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

from build import blur_regions, font, track, track_w, vgrad, FONTS, ASSETS

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

W = int(os.environ.get("POSTER_W", 1654))
H = int(round(W * 297 / 210.0))
SC = W / 1654.0


def s(px):
    return max(1, int(round(px * SC)))


# ---------------------------------------------------------------- palette
CREAM = (234, 226, 206)
CREAM_D = (216, 205, 180)
CREAM_L = (243, 237, 222)
INK = (30, 27, 25)
INK_S = (58, 52, 48)
RED = (183, 30, 33)
RED_D = (132, 18, 22)
GOLD = (212, 166, 52)
TEAL = (88, 112, 106)

# ---------------------------------------------------------------- copy
STRIP_ITEMS = ["最新パーツ情報", "実測データ", "オーナー特集"]
STRIP_EN = "REAL PARTS · REAL OWNERS · REAL PERFORMANCE"

MAST = "JDMYARD"
MAST_SUB = "日本車専門誌"
MAST_EN = "MAGAZINE"

STACK = ["最強", "ゼット", "列伝"]
STACK_YEARS = "2009 → 2020"
BANNER_JP = "特集"

COVER_LINES = [
    ("徹底比較", "VQ37VHR 実測パワー検証"),
    ("新作", "エアロパーツ最新カタログ"),
    ("基礎", "足回りセッティング入門"),
    ("完全版", "排気系チューン全ガイド"),
]

RED_BANNER = "本物のパーツ。本物のパフォーマンス。"

ISSUE_NO = "01"
ISSUE_YEAR = "2026"
ISSUE_MONTH = "AUGUST"
ISSUE_JP = "8月号"

FEATURE = dict(name="Owner Name", car="2013 Nissan 370Z", ig="@yourhandle")

PLATE_8 = [(0.345, 0.636, 0.672, 0.714)]

HERO = dict(src=os.environ.get("POSTER_HERO", "7.jpg"),
            bias_y=0.46, zoom=1.02, plate=None)

CARDS = [
    dict(src="8.jpg", idx="01", jp="正面", name="Owner One",
         car="370Z · Front End", ig="@handle_one",
         bias_y=0.40, zoom=1.04, plate=PLATE_8),
    dict(src="9.jpg", idx="02", jp="斜め前", name="Owner Two",
         car="370Z · Three Quarter", ig="@handle_two",
         bias_y=0.48, zoom=1.12, plate=None),
    dict(src="3.JPG", idx="03", jp="ホイール", name="Owner Three",
         car="370Z · Forged Wheels", ig="@handle_three",
         bias_y=0.46, zoom=1.02, plate=None),
]

FOOT_HANDLE = "@jdmyard"
FOOT_L = "FIND US ON SOCIAL MEDIA"
FOOT_M = "YOUR MONTHLY DOSE OF INSPIRATION · MOTIVATION · STANCE"
FOOT_STAMP = "日本製"

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


def njp(sz, w="Bold"):
    return font(NOTOJP, s(sz), w)


# ---------------------------------------------------------------- treatment
def vintage_grade(img):
    """
    Warm, faded newsstand-print look - the opposite of the cool crushed grade
    used for the website hero. Blacks lift rather than crush, highlights warm,
    saturation drops but does not die.
    """
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(0.62)
    img = ImageEnhance.Contrast(img).enhance(1.04)

    # fade: lift the toe, pull the shoulder down
    def curve(v):
        v = v / 255.0
        v = 0.055 + v * 0.90            # faded black + white point
        v = v ** 0.98
        return int(min(255, max(0, v * 255)))
    img = img.point([curve(i) for i in range(256)] * 3)

    # warm split-tone: amber highlights, softly cool shadows
    r, g, b = img.split()
    r = r.point(lambda v: min(255, v + int(16 * (v / 255) + 5)))
    g = g.point(lambda v: min(255, v + int(5 * (v / 255))))
    b = b.point(lambda v: max(0, v - int(14 * (v / 255)) + 4))
    return Image.merge("RGB", (r, g, b))


def paper(size):
    """Cream stock with mottling, so flat areas are not dead digital fill."""
    base = Image.new("RGB", size, CREAM)
    blotch = Image.effect_noise(size, 26).filter(
        ImageFilter.GaussianBlur(max(2, s(9))))
    blotch = blotch.point(lambda v: 118 + int((v - 128) * 0.55))
    tinted = ImageChops.multiply(base, blotch.convert("RGB").point(
        lambda v: 170 + int(v * 0.34)))
    return Image.blend(base, tinted, 0.55)


def print_pass(img, dot_alpha=0.05, grain=0.09):
    """Halftone dot screen + grain."""
    w, h = img.size
    cell = max(3, s(5))
    tile = Image.new("L", (cell, cell), 255)
    td = ImageDraw.Draw(tile)
    r = max(1, cell * 0.30)
    td.ellipse([cell / 2 - r, cell / 2 - r, cell / 2 + r, cell / 2 + r], fill=176)
    screen = Image.new("L", (w + cell, h + cell))
    for y in range(0, h + cell, cell):
        for x in range(0, w + cell, cell):
            screen.paste(tile, (x, y))
    screen = screen.crop((0, 0, w, h)).filter(ImageFilter.GaussianBlur(0.6))
    img = Image.blend(img, ImageChops.multiply(img, screen.convert("RGB")),
                      dot_alpha)
    noise = Image.effect_noise((w, h), 12).convert("RGB")
    return Image.blend(img, ImageChops.add(img, noise, scale=1.0, offset=-112),
                       grain)


def edge_age(img, strength=0.30):
    """Darken and warm the sheet edges, like a shelf-worn cover."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    inset = int(min(w, h) * 0.055)
    d.rectangle([inset, inset, w - inset, h - inset], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.055))
    dark = ImageEnhance.Brightness(img).enhance(1.0 - strength)
    return Image.composite(img, dark, mask)


# ---------------------------------------------------------------- helpers
def load(spec, tw, th, grade=True):
    p = ASSETS / spec["src"]
    if not p.exists():
        im = Image.new("RGB", (tw, th), CREAM_D)
        d = ImageDraw.Draw(im)
        f = rob(15, "Bold")
        t = f"[ {spec['src']} missing ]"
        d.text(((tw - d.textlength(t, font=f)) / 2, th / 2), t, font=f, fill=INK_S)
        return im, False
    img = Image.open(p).convert("RGB")
    if spec.get("plate"):
        img = blur_regions(img, spec["plate"])
    iw, ih = img.size
    scale = max(tw / iw, th / ih) * spec.get("zoom", 1.0)
    nw, nh = max(tw, int(iw * scale + .5)), max(th, int(ih * scale + .5))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = int((nw - tw) * 0.5)
    top = int((nh - th) * spec.get("bias_y", 0.5))
    img = img.crop((left, top, left + tw, top + th))
    if grade:
        img = vintage_grade(img)
    return img, True


def hard_text(d, xy, text, fnt, fill, outline=None, ow=0, shadow=None, off=0,
              spacing=0):
    """Type with a hard offset shadow and optional outline - letterpress feel."""
    x, y = xy
    if shadow is not None and off:
        track(d, (x + off, y + off), text, fnt, shadow, spacing=spacing)
    if outline is not None and ow:
        # emulate an outer contour by stamping the glyphs around the centre
        for dx, dy in ((-ow, 0), (ow, 0), (0, -ow), (0, ow),
                       (-ow, -ow), (ow, -ow), (-ow, ow), (ow, ow)):
            track(d, (x + dx, y + dy), text, fnt, outline, spacing=spacing)
    track(d, (x, y), text, fnt, fill, spacing=spacing)


def chip(d, box, text, fnt, bg, fg, spacing=0):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=bg)
    tw = track_w(d, text, fnt, spacing)
    bb = d.textbbox((0, 0), text, font=fnt)
    track(d, (x0 + ((x1 - x0) - tw) / 2, y0 + ((y1 - y0) - (bb[3] - bb[1])) / 2
              - bb[1]), text, fnt, fg, spacing=spacing)


def badge_round(size):
    ss = 4
    d0 = size * ss
    im = Image.new("RGBA", (d0, d0), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, d0 - 1, d0 - 1], fill=RED + (250,))
    d.ellipse([0, 0, d0 - 1, d0 - 1], outline=CREAM + (235,),
              width=max(1, d0 // 40))
    ins = d0 * 0.062
    d.ellipse([ins, ins, d0 - ins, d0 - ins], outline=GOLD + (150,),
              width=max(1, d0 // 85))
    im = im.resize((size, size), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    f = font(ARCHIVO, max(7, int(size * 0.118)), "Bold")
    for t, fy in zip(("TUNED", "MODIFIED", "PERFECTED"), (0.25, 0.435, 0.62)):
        sp = max(1, int(size * 0.012))
        tw = track_w(d, t, f, sp)
        track(d, ((size - tw) / 2, size * fy), t, f, CREAM_L + (255,), spacing=sp)
    return im


def diagonal_flash(text, bw, bh, angle=-13):
    ss = 3
    im = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, bw * ss, bh * ss], fill=RED + (250,))
    d.rectangle([0, 0, bw * ss, bh * ss], outline=CREAM + (230,),
                width=max(1, int(3 * ss * SC)))
    f = font(NOTOJP, int(bh * ss * 0.54), "Black")
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((bw * ss - (bb[2] - bb[0])) / 2 - bb[0],
            (bh * ss - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f,
           fill=CREAM_L + (255,))
    return im.resize((bw, bh), Image.LANCZOS).rotate(
        angle, expand=True, resample=Image.BICUBIC)


# ---------------------------------------------------------------- build
def build_poster():
    canvas = paper((W, H))
    d = ImageDraw.Draw(canvas)

    # ---------------- geometry (bottom-up, so nothing can leave dead space)
    foot_h = s(126)
    cards_pad, card_img_h, card_txt_h = s(18), s(360), s(104)
    cards_block = cards_pad * 2 + card_img_h + card_txt_h
    banner_h = s(64)

    strip_h = s(62)
    mast_top = strip_h + s(6)
    mast_h = s(186)

    foot_top = H - foot_h
    cards_top = foot_top - cards_block
    banner_top = cards_top - banner_h
    hero_top = mast_top + mast_h - s(46)          # photo cuts into the masthead
    hero_bot = banner_top
    hero_h = hero_bot - hero_top

    # ================================================ TOP STRIP
    d.rectangle([0, 0, W, strip_h], fill=INK)
    d.rectangle([0, strip_h - s(5), W, strip_h], fill=RED)
    f_sj = njp(15, "Bold")
    f_se = arch(10.5, "Bold")
    sp = s(2.2)
    widths = [track_w(d, t, f_sj, sp) for t in STRIP_ITEMS]
    mark = s(26)
    total = sum(widths) + mark * (len(STRIP_ITEMS) - 1)
    sx = (W - total) / 2
    for i, t in enumerate(STRIP_ITEMS):
        track(d, (sx, s(9)), t, f_sj, CREAM_L, spacing=sp)
        sx += widths[i]
        if i < len(STRIP_ITEMS) - 1:
            cx = sx + mark / 2
            star_pts = []
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                rr = s(6) if k % 2 == 0 else s(2.6)
                star_pts.append((cx + rr * math.cos(a), s(18) + rr * math.sin(a)))
            d.polygon(star_pts, fill=GOLD)
            sx += mark
    ew = track_w(d, STRIP_EN, f_se, s(3))
    track(d, ((W - ew) / 2, s(36)), STRIP_EN, f_se, (176, 166, 148), spacing=s(3))

    # ================================================ MASTHEAD
    # Oversized wordmark, letter-spaced to span the sheet. Drawn now so the
    # hero photo can cut across its lower edge.
    f_mast = anton(178)
    base_sp = s(2)
    mw = track_w(d, MAST, f_mast, base_sp)
    avail = W - s(52)
    if mw > avail:                                 # tighten to fit the sheet
        base_sp = base_sp - (mw - avail) / max(1, len(MAST) - 1)
        mw = track_w(d, MAST, f_mast, base_sp)
    mx = (W - mw) / 2
    hard_text(d, (mx, mast_top), MAST, f_mast, INK, outline=CREAM_L,
              ow=s(5), shadow=RED_D, off=s(11), spacing=base_sp)

    # The wordmark's ink bottom sits below where the photo cuts across, so the
    # two small caps lines are drawn later, as hero overlays - otherwise they
    # are buried under the photo entirely.

    # ================================================ HERO
    hero, hero_ok = load(HERO, W, hero_h)

    # scrims: top so the masthead cut stays readable, bottom to hold type
    hero.paste(Image.new("RGB", (W, s(120)), (0, 0, 0)), (0, 0),
               vgrad((W, s(120)), 150, 0, gamma=0.9))
    sh = int(hero_h * 0.50)
    hero.paste(Image.new("RGB", (W, sh), (0, 0, 0)), (0, hero_h - sh),
               vgrad((W, sh), 0, 214, gamma=2.0))
    canvas.paste(hero, (0, hero_top))
    d = ImageDraw.Draw(canvas)

    # hairline frame so the photo sits on the stock rather than floating
    d.rectangle([0, hero_top, W - 1, hero_bot - 1], outline=CREAM_D, width=s(2))

    # masthead sub-lines, riding on the photo's top scrim
    f_msub = njp(16, "Bold")
    f_men = arch(13, "Bold")
    enw = track_w(d, MAST_EN, f_men, s(6))
    track(d, (mx + s(8), hero_top + s(14)), MAST_SUB, f_msub, (232, 150, 150),
          spacing=s(5))
    track(d, (mx + mw - enw - s(8), hero_top + s(18)), MAST_EN, f_men,
          CREAM_D, spacing=s(6))

    # ---- giant stacked kanji, left, overlapping the photo
    f_st = njp(132, "Black")
    st_x = s(34)
    line_h = s(134)
    st_y = hero_top + s(96)
    for i, ln in enumerate(STACK):
        ly = st_y + i * line_h
        d.text((st_x + s(10), ly + s(10)), ln, font=f_st, fill=(20, 14, 12))
        d.text((st_x, ly), ln, font=f_st, fill=CREAM_L,
               stroke_width=max(1, s(6)), stroke_fill=RED_D)

    # gold year chip beneath
    f_yr = arch(21, "Bold")
    yw = track_w(d, STACK_YEARS, f_yr, s(2))
    yy = st_y + line_h * len(STACK) + s(4)
    d.rectangle([st_x + s(4) + s(6), yy + s(6), st_x + s(4) + yw + s(30),
                 yy + s(40)], fill=(20, 14, 12))
    chip(d, (st_x + s(4), yy, st_x + s(4) + yw + s(24), yy + s(34)),
         STACK_YEARS, f_yr, GOLD, (26, 20, 8), spacing=s(2))

    # ---- badge + flash
    bsz = s(150)
    bimg = badge_round(bsz)
    canvas.paste(bimg, (W - bsz - s(30), hero_top + s(120)), bimg)
    fl = diagonal_flash(BANNER_JP, s(140), s(62))
    canvas.paste(fl, (W - fl.width - s(26), hero_top + s(26)), fl)
    d = ImageDraw.Draw(canvas)

    # ---- cover lines with category chips, lower left over the scrim
    f_cat = njp(13, "Bold")
    f_line = njp(21, "Bold")
    cl_x = s(34)
    cl_y = hero_bot - s(58) - s(52) * len(COVER_LINES)
    for cat, line in COVER_LINES:
        cwid = track_w(d, cat, f_cat, s(1.5)) + s(18)
        chip(d, (cl_x, cl_y + s(4), cl_x + cwid, cl_y + s(26)), cat, f_cat,
             RED, CREAM_L, spacing=s(1.5))
        d.text((cl_x + cwid + s(10), cl_y - s(2)), line, font=f_line,
               fill=CREAM_L, stroke_width=max(1, s(3)), stroke_fill=(16, 12, 10))
        cl_y += s(52)

    # ---- feature credit, bottom left under the cover lines
    f_name = kaushan(40)
    f_meta = rob(15, "Regular")
    fy = hero_bot - s(52)
    d.text((s(36), fy - s(6)), FEATURE["name"], font=f_name, fill=GOLD,
           stroke_width=max(1, s(2)), stroke_fill=(16, 12, 8))
    d.text((s(38) + track_w(d, FEATURE["name"], f_name, 0) + s(16), fy + s(12)),
           f"{FEATURE['car']}  ·  {FEATURE['ig']}", font=f_meta, fill=CREAM_D)

    # ---- issue block, bottom right of the hero
    ib_w, ib_h = s(168), s(126)
    ib_x, ib_y = W - ib_w - s(26), hero_bot - ib_h - s(22)
    d.rectangle([ib_x + s(7), ib_y + s(7), ib_x + ib_w + s(7), ib_y + ib_h + s(7)],
                fill=(18, 13, 11))
    d.rectangle([ib_x, ib_y, ib_x + ib_w, ib_y + ib_h], fill=CREAM_L)
    d.rectangle([ib_x, ib_y, ib_x + ib_w, ib_y + ib_h], outline=INK, width=s(3))
    d.rectangle([ib_x, ib_y, ib_x + ib_w, ib_y + s(8)], fill=RED)
    f_no = anton(74)
    nb = d.textbbox((0, 0), ISSUE_NO, font=f_no)
    d.text((ib_x + (ib_w - (nb[2] - nb[0])) / 2 - nb[0], ib_y + s(10) - nb[1]),
           ISSUE_NO, font=f_no, fill=INK)
    f_iy = arch(15, "Bold")
    yw2 = track_w(d, ISSUE_YEAR, f_iy, s(2.5))
    track(d, (ib_x + (ib_w - yw2) / 2, ib_y + s(80)), ISSUE_YEAR, f_iy, RED_D,
          spacing=s(2.5))
    f_im = njp(13, "Bold")
    mw2 = track_w(d, ISSUE_JP, f_im, s(1.5))
    track(d, (ib_x + (ib_w - mw2) / 2, ib_y + s(100)), ISSUE_JP, f_im, INK_S,
          spacing=s(1.5))

    # ================================================ RED BANNER
    d.rectangle([0, banner_top, W, banner_top + banner_h], fill=RED)
    d.rectangle([0, banner_top, W, banner_top + s(3)], fill=(96, 12, 15))
    f_bn = njp(23, "Bold")
    bw2 = track_w(d, RED_BANNER, f_bn, s(4))
    bb = d.textbbox((0, 0), RED_BANNER, font=f_bn)
    track(d, ((W - bw2) / 2, banner_top + (banner_h - (bb[3] - bb[1])) / 2 - bb[1]),
          RED_BANNER, f_bn, CREAM_L, spacing=s(4))

    # ================================================ OWNER CARDS
    pad = s(20)
    gap = s(16)
    cw = (W - pad * 2 - gap * 2) // 3
    for i, c in enumerate(CARDS):
        cx = pad + (cw + gap) * i
        cy = cards_top + cards_pad
        ph, ok = load(c, cw, card_img_h)
        # drop shadow then photo then keyline
        d.rectangle([cx + s(6), cy + s(6), cx + cw + s(6), cy + card_img_h + s(6)],
                    fill=CREAM_D)
        canvas.paste(ph, (cx, cy))
        d = ImageDraw.Draw(canvas)
        d.rectangle([cx, cy, cx + cw - 1, cy + card_img_h - 1], outline=INK,
                    width=s(3))

        ch2 = s(38)
        chip(d, (cx, cy, cx + ch2, cy + ch2), c["idx"], anton(23), RED, CREAM_L)

        ty = cy + card_img_h + s(14)
        track(d, (cx + s(2), ty), c["jp"], njp(14, "Bold"), RED_D, spacing=s(2))
        track(d, (cx + s(2), ty + s(24)), c["name"], osw(20, "SemiBold"), INK,
              spacing=s(0.5))
        d.text((cx + s(2), ty + s(50)), c["car"], font=rob(14), fill=INK_S)
        d.text((cx + s(2), ty + s(70)), f"Instagram: {c['ig']}", font=rob(14),
               fill=(122, 112, 100))

    # ================================================ FOOTER
    d.rectangle([0, foot_top, W, H], fill=CREAM)
    d.rectangle([0, foot_top, W, foot_top + s(4)], fill=INK)
    f_f1 = arch(14, "Bold")
    f_f2 = rob(15, "Regular")
    track(d, (s(30), foot_top + s(30)), FOOT_L, f_f1, INK, spacing=s(1.6))
    d.text((s(30), foot_top + s(56)), FOOT_HANDLE, font=rob(19, "Bold"),
           fill=RED_D)
    fmw = track_w(d, FOOT_M, f_f1, s(1.8))
    track(d, ((W - fmw) / 2, foot_top + s(84)), FOOT_M, f_f1, INK_S,
          spacing=s(1.8))
    f_stamp = njp(30, "Black")
    sw2 = track_w(d, FOOT_STAMP, f_stamp, s(3))
    track(d, (W - sw2 - s(30), foot_top + s(34)), FOOT_STAMP, f_stamp,
          CREAM_D, spacing=s(3))

    # ================================================ PRINT FINISH
    canvas = print_pass(canvas)
    canvas = edge_age(canvas)

    suffix = "" if W == 1654 else f"@{W}"
    out = OUT / f"poster{suffix}.png"
    canvas.save(out, "PNG")
    print(f"wrote {out}  ({W}x{H})  hero={HERO['src']}  "
          f"cards={[c['src'] for c in CARDS]}")
    return out


if __name__ == "__main__":
    build_poster()
