#!/usr/bin/env python3
"""
JDM YARD magazine-style poster.

Builds an A4-proportioned cover poster: masthead block, round badge, big
outlined headline, full-bleed hero, a feature strip and three owner cards,
over a bottom social bar.

Layout language is modelled on newsstand car-magazine covers. Branding,
masthead and all copy are JDM Yard's own - no third-party magazine name,
logo or trade dress is reproduced.

Usage:  python3 poster.py            # 1654 x 2339  (A4 @ 200dpi)
        POSTER_W=2480 python3 poster.py   # A4 @ 300dpi
Output: out/poster.png
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from build import (jdm_grade, cover, blur_regions, font, track, track_w,
                   vgrad, FONTS, ASSETS, PLATE_2)

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
INK = (16, 16, 19)
RED = (206, 22, 32)
RED_HI = (232, 42, 52)
WHITE = (255, 255, 255)
BONE = (238, 238, 242)
GREY = (150, 150, 156)
DIM = (104, 104, 111)
HAIR = (44, 44, 50)

# ---------------------------------------------------------------- copy
STRIP = "REAL PARTS   ·   REAL OWNERS   ·   REAL PERFORMANCE"
MAST_1, MAST_2 = "JDM", "YARD"
SUBHEAD = "MAGAZINE"
TAGLINE = "Home Of Modified And JDM Cars"
JP_TAGLINE = "日本車専門誌"
BADGE = ("TUNED", "MODIFIED", "PERFECTED")
HEAD_1 = "JDM CLASSICS"
HEAD_2 = "THE Z34"

# hero photo: swap `src` to the new photo once it is in the repo
HERO = dict(src="1.jpg", bias_y=0.52, zoom=1.04, expo=0.96, plate=None)

FEATURE = dict(name="Owner Name", car="2013 Nissan 370Z", ig="@yourhandle")

# three owner cards along the bottom - swap src to 7/8/9.jpg when uploaded
CARDS = [
    dict(src="3.JPG", name="Owner One", car="370Z Forged Wheels",
         ig="@handle_one", bias_y=0.46, zoom=1.02, expo=0.96),
    dict(src="4.jpg", name="Owner Two", car="VQ37VHR Engine Bay",
         ig="@handle_two", bias_y=0.34, zoom=1.04, expo=0.92),
    dict(src="5.jpg", name="Owner Three", car="370Z Interior",
         ig="@handle_three", bias_y=0.22, zoom=1.02, expo=1.00),
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
    """Darken the base of an image so type sits on it cleanly."""
    w, h = img.size
    sh = int(h * frac)
    ramp = vgrad((w, sh), 0, peak, gamma=gamma)
    region = img.crop((0, h - sh, w, h))
    region = Image.composite(Image.new("RGB", (w, sh), (0, 0, 0)), region, ramp)
    img.paste(region, (0, h - sh))
    return img


def soft_shadow(canvas, box, draw_fn, blur=4, boost=2.4):
    """Render type into a mask, blur it, composite black - keeps text legible."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    mask = Image.new("L", (mw, mh), 0)
    draw_fn(ImageDraw.Draw(mask), -x0, -y0)
    mask = mask.filter(ImageFilter.GaussianBlur(s(blur)))
    mask = mask.point(lambda v: min(255, int(v * boost)))
    canvas.paste(Image.new("RGB", (mw, mh), (0, 0, 0)), (x0, y0), mask)


def star(d, cx, cy, r, fill):
    """Five-pointed star as a polygon - no font glyph needed."""
    import math
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def badge(size):
    """Circular TUNED / MODIFIED / PERFECTED stamp."""
    ss = 4                                     # supersample for clean edges
    d0 = size * ss
    im = Image.new("RGBA", (d0, d0), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, d0 - 1, d0 - 1], fill=(150, 12, 20, 255))
    d.ellipse([0, 0, d0 - 1, d0 - 1], outline=(255, 255, 255, 190),
              width=max(1, d0 // 42))
    inset = d0 * 0.055
    d.ellipse([inset, inset, d0 - inset, d0 - inset],
              outline=(255, 255, 255, 90), width=max(1, d0 // 90))
    im = im.resize((size, size), Image.LANCZOS)

    d = ImageDraw.Draw(im)
    f = font(ARCHIVO, max(7, int(size * 0.115)), "Bold")
    ys = [0.24, 0.42, 0.60]
    for t, fy in zip(BADGE, ys):
        tw = track_w(d, t, f, max(1, int(size * 0.012)))
        track(d, ((size - tw) / 2, size * fy), t, f, WHITE + (255,),
              spacing=max(1, int(size * 0.012)))
    # small car glyph
    cy = size * 0.80
    cw = size * 0.42
    cx = (size - cw) / 2
    d.rounded_rectangle([cx, cy, cx + cw, cy + size * 0.085],
                        radius=size * 0.03, outline=WHITE + (230,),
                        width=max(1, size // 60))
    d.arc([cx + cw * 0.16, cy - size * 0.055, cx + cw * 0.84, cy + size * 0.055],
          180, 360, fill=WHITE + (230,), width=max(1, size // 60))
    return im


# ---------------------------------------------------------------- build
def build_poster():
    canvas = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(canvas)

    # ---------------- geometry
    # Derive the hero height from what's left over, so there is no dead space
    # above the bottom bar. Card block height is content-driven.
    strip_h = s(34)
    mast_h = s(352)
    bot_h = s(126)
    card_pad = s(20)
    card_img_h = s(430)
    card_txt_h = s(92)
    cards_block = card_pad + card_img_h + card_txt_h

    hero_top = strip_h + mast_h
    hero_h = H - strip_h - mast_h - bot_h - cards_block
    hero_bot = hero_top + hero_h
    cards_top = hero_bot
    cards_h = cards_block

    # ================================================ TOP STRIP
    d.rectangle([0, 0, W, strip_h], fill=INK)
    d.rectangle([0, 0, s(9), strip_h], fill=RED)
    f_strip = arch(11, "SemiBold")
    tw = track_w(d, STRIP, f_strip, s(2.4))
    track(d, ((W - tw) / 2, strip_h / 2 - s(7)), STRIP, f_strip, BONE,
          spacing=s(2.4))

    # ================================================ MASTHEAD
    d.rectangle([0, strip_h, W, hero_top], fill=BLACK)
    # subtle red glow behind the wordmark
    glow = Image.new("RGB", (W, mast_h), BLACK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.12, mast_h * 0.10, W * 0.88, mast_h * 0.78],
               fill=(46, 8, 11))
    glow = glow.filter(ImageFilter.GaussianBlur(s(70)))
    canvas.paste(glow, (0, strip_h))
    d = ImageDraw.Draw(canvas)

    # wordmark
    f_mast = anton(146)
    sp = s(-2)
    w1 = track_w(d, MAST_1, f_mast, sp)
    w2 = track_w(d, MAST_2, f_mast, sp)
    gap = s(14)
    mx = (W - (w1 + gap + w2)) / 2
    my = strip_h + s(26)
    track(d, (mx, my), MAST_1, f_mast, WHITE, spacing=sp)
    track(d, (mx + w1 + gap, my), MAST_2, f_mast, RED_HI, spacing=sp)

    # measure the wordmark's real ink extent so nothing collides with it
    mb = d.textbbox((mx, my), MAST_1 + MAST_2, font=f_mast)
    mast_ink_bot = mb[3]

    # stars + MAGAZINE
    f_sub = anton(44)
    subw = track_w(d, SUBHEAD, f_sub, s(10))
    star_r = s(13)
    star_block = star_r * 6.6
    total = star_block + s(26) + subw
    sx = (W - total) / 2
    sy = mast_ink_bot + s(14)
    for k in range(3):
        star(d, sx + star_r + k * star_r * 2.6, sy + s(24), star_r,
             (214, 176, 74))
    track(d, (sx + star_block + s(26), sy), SUBHEAD, f_sub, BONE, spacing=s(10))
    sub_bot = d.textbbox((0, sy), SUBHEAD, font=f_sub)[3]

    # tagline + JP
    f_tag = rob(17, "Regular")
    tw = d.textlength(TAGLINE, font=f_tag)
    d.text(((W - tw) / 2, sub_bot + s(12)), TAGLINE, font=f_tag, fill=GREY)
    f_jt = njp(14, "Medium")
    jw = track_w(d, JP_TAGLINE, f_jt, s(4))
    jp_y = sub_bot + s(40)
    track(d, ((W - jw) / 2, jp_y), JP_TAGLINE, f_jt, (150, 46, 54),
          spacing=s(4))

    # guard: the masthead block is measured, so verify it actually fits inside
    # mast_h rather than sliding under the hero photo
    mast_content_bot = d.textbbox((0, jp_y), JP_TAGLINE, font=f_jt)[3]
    if mast_content_bot > hero_top - s(6):
        print(f"  WARNING masthead overflows: content bottom "
              f"{mast_content_bot} vs hero_top {hero_top} "
              f"- raise mast_h by ~{mast_content_bot - hero_top + s(12)}px")
    else:
        print(f"  masthead fits: content bottom {mast_content_bot}, "
              f"hero_top {hero_top}, clearance {hero_top - mast_content_bot}px")

    # ================================================ HERO
    hero, hero_ok = load(HERO, W, hero_h)
    hero = scrim_bottom(hero, 0.42, 214, gamma=1.9)
    # top scrim so the masthead edge blends into the photo
    tramp = vgrad((W, s(150)), 190, 0, gamma=0.8)
    treg = hero.crop((0, 0, W, s(150)))
    treg = Image.composite(Image.new("RGB", (W, s(150)), (0, 0, 0)), treg, tramp)
    hero.paste(treg, (0, 0))
    canvas.paste(hero, (0, hero_top))
    d = ImageDraw.Draw(canvas)

    # ---------------- headline
    f_h1 = anton(104)
    f_h2 = kaushan(74)
    h1w = track_w(d, HEAD_1, f_h1, s(1))
    hx = (W - h1w) / 2
    hy = hero_top + s(120)

    def _h(md, ox, oy):
        track(md, (hx + ox, hy + oy), HEAD_1, f_h1, 255, spacing=s(1))
    soft_shadow(canvas, (int(hx - s(40)), int(hy - s(30)),
                         int(hx + h1w + s(40)), int(hy + s(150))),
                _h, blur=7, boost=2.0)
    d = ImageDraw.Draw(canvas)
    track(d, (hx, hy), HEAD_1, f_h1, WHITE, spacing=s(1))

    # second line: gold script, skewed for an italic feel, kicked out to the
    # right so it reads as a subhead rather than colliding with line one
    h1_bot = d.textbbox((hx, hy), HEAD_1, font=f_h1)[3]
    h2_bb = d.textbbox((0, 0), HEAD_2, font=f_h2)
    h2_tw, h2_th = h2_bb[2] - h2_bb[0], h2_bb[3] - h2_bb[1]
    padx, pady = s(40), s(30)
    h2_layer = Image.new("RGBA", (h2_tw + padx * 2, h2_th + pady * 2),
                         (0, 0, 0, 0))
    h2d = ImageDraw.Draw(h2_layer)
    h2d.text((padx - h2_bb[0], pady - h2_bb[1]), HEAD_2, font=f_h2,
             fill=(228, 186, 70, 255),
             stroke_width=max(1, s(3)), stroke_fill=(24, 17, 5, 240))
    h2_layer = h2_layer.transform(h2_layer.size, Image.AFFINE,
                                  (1, 0.22, -s(20), 0, 1, 0),
                                  resample=Image.BICUBIC)
    h2x = int(hx + h1w - h2_tw - padx * 1.2)
    canvas.paste(h2_layer, (h2x, int(h1_bot - s(6))), h2_layer)
    d = ImageDraw.Draw(canvas)

    # ---------------- badge
    bsz = s(190)
    canvas.paste(badge(bsz), (s(34), hero_top + s(52)), badge(bsz))
    d = ImageDraw.Draw(canvas)

    # ---------------- feature strip (script name over hero base)
    fy = hero_bot - s(150)
    d.rectangle([0, fy - s(6), s(9), fy + s(120)], fill=RED)
    f_name = kaushan(52)
    f_meta = rob(17, "Regular")
    d.text((s(30), fy - s(14)), FEATURE["name"], font=f_name, fill=(238, 224, 170),
           stroke_width=max(1, s(2)), stroke_fill=(20, 16, 8, 220))
    d.text((s(32), fy + s(56)), FEATURE["car"], font=f_meta, fill=BONE)
    d.text((s(32), fy + s(82)), f"Instagram: {FEATURE['ig']}", font=f_meta,
           fill=GREY)

    # ================================================ OWNER CARDS
    d.rectangle([0, cards_top, W, cards_top + cards_h], fill=(13, 13, 15))
    pad = s(20)
    gap = s(16)
    cw = (W - pad * 2 - gap * 2) // 3
    ch_img = card_img_h
    for i, c in enumerate(CARDS):
        cx = pad + (cw + gap) * i
        cy = cards_top + pad
        ph, ok = load(c, cw, ch_img)
        canvas.paste(ph, (cx, cy))
        d = ImageDraw.Draw(canvas)
        d.rectangle([cx, cy, cx + cw - 1, cy + ch_img - 1], outline=HAIR,
                    width=max(1, s(1)))
        ty = cy + ch_img + s(10)
        f_cn = osw(21, "SemiBold")
        f_cm = rob(14, "Regular")
        track(d, (cx + s(2), ty), c["name"], f_cn, RED_HI, spacing=s(0.5))
        d.text((cx + s(2), ty + s(28)), c["car"], font=f_cm, fill=BONE)
        d.text((cx + s(2), ty + s(48)), f"Instagram: {c['ig']}", font=f_cm,
               fill=DIM)

    # ================================================ BOTTOM BAR
    by0 = H - bot_h
    d.rectangle([0, by0, W, H], fill=BLACK)
    d.line([(0, by0), (W, by0)], fill=RED, width=s(3))

    f_b1 = arch(15, "Bold")
    f_b2 = rob(15, "Regular")
    # left
    track(d, (s(30), by0 + s(28)), BOT_L1, f_b1, WHITE, spacing=s(1.2))
    track(d, (s(30), by0 + s(50)), BOT_L2, f_b1, WHITE, spacing=s(1.2))
    d.text((s(30), by0 + s(76)), BOT_HANDLE, font=f_b2, fill=GREY)
    # middle
    mid_x = W * 0.42
    track(d, (mid_x, by0 + s(34)), BOT_M1, f_b1, WHITE, spacing=s(1.4))
    track(d, (mid_x, by0 + s(58)), BOT_M2, f_b1, RED_HI, spacing=s(1.4))
    # right: two icon+label pairs, right-aligned so nothing clips the edge
    right_margin = s(30)
    lbl_sp = s(1)
    w_pass = max(track_w(d, BOT_R3, f_b1, lbl_sp),
                 track_w(d, BOT_R4, f_b1, lbl_sp))
    w_insp = max(track_w(d, BOT_R1, f_b1, lbl_sp),
                 track_w(d, BOT_R2, f_b1, lbl_sp))
    icon_w, icon_gap, pair_gap = s(32), s(12), s(34)

    # rightmost pair: SHARE / THE PASSION
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

    # inner pair: GET / INSPIRED
    rx_lbl = ex - pair_gap - w_insp
    rx = rx_lbl - icon_gap - icon_w
    hr = icon_w / 2
    d.polygon([(rx, by0 + s(47)), (rx + hr, by0 + s(34)),
               (rx + hr * 2, by0 + s(47)), (rx + hr, by0 + s(62))],
              outline=WHITE)
    track(d, (rx_lbl, by0 + s(34)), BOT_R1, f_b1, WHITE, spacing=lbl_sp)
    track(d, (rx_lbl, by0 + s(54)), BOT_R2, f_b1, WHITE, spacing=lbl_sp)

    suffix = "" if W == 1654 else f"@{W}"
    out = OUT / f"poster{suffix}.png"
    canvas.save(out, "PNG")
    print(f"wrote {out}  ({W}x{H})  hero={HERO['src']} ok={hero_ok}")
    return out


if __name__ == "__main__":
    build_poster()
