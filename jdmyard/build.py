#!/usr/bin/env python3
"""
JDM YARD hero image builder.

Renders a flat PNG of the JDM-themed category-grid hero.
Drop photos into assets/ named tile1.jpg ... tile6.jpg (any common format).
Missing photos fall back to a dark placeholder so the layout can be reviewed.

Usage:  python3 build.py
Output: out/jdmyard.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import os
import random

ROOT = Path(__file__).parent
FONTS = ROOT / "fonts"
ASSETS = ROOT / "assets"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- canvas spec
W = int(os.environ.get("JDM_W", 1600))     # output width; JDM_W=3200 for 2x
SCALE = W / 1024.0            # reference mock was 1024 wide
HEADER_H = int(84 * SCALE)
TRUST_H = int(52 * SCALE)
TILE_W = W // 3
TILE_H = int(178 * SCALE)
FOOTER_H = int(48 * SCALE)
H = HEADER_H + TRUST_H + TILE_H * 2 + FOOTER_H

# ---------------------------------------------------------------- palette
BLACK = (8, 8, 9)
NEAR_BLACK = (13, 13, 15)
RED = (214, 26, 36)
RED_BRIGHT = (232, 42, 52)
WHITE = (255, 255, 255)
GREY = (168, 168, 172)
DIM = (108, 108, 114)
HAIRLINE = (38, 38, 42)

# ---------------------------------------------------------------- options
# Number plate in 2.jpg is legible. Set False to leave it untouched.
BLUR_PLATE = True
PLATE_2 = [(0.325, 0.572, 0.690, 0.650)]     # normalised box around "1FCM597"

# ---------------------------------------------------------------- fonts
JP_PATH = FONTS / "NotoSansJP[wght].ttf"
OSW_PATH = FONTS / "Oswald[wght].ttf"
ROB_PATH = FONTS / "RobotoCondensed.ttf"


def font(path, size, weight=None):
    f = ImageFont.truetype(str(path), size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f


def jp(size, weight="Medium"):
    return font(JP_PATH, size, weight)


def osw(size, weight="Bold"):
    return font(OSW_PATH, size, weight)


def rob(size, weight="Regular"):
    return font(ROB_PATH, size, weight)


def s(px):
    """Scale a reference-pixel value to output canvas."""
    return max(1, int(round(px * SCALE)))


# ---------------------------------------------------------------- helpers
def track(draw, xy, text, fnt, fill, spacing=0, anchor_mid=False):
    """Draw text with manual letter-spacing. Returns total width."""
    x, y = xy
    if spacing == 0 and not anchor_mid:
        draw.text((x, y), text, font=fnt, fill=fill)
        return draw.textlength(text, font=fnt)
    total = sum(draw.textlength(c, font=fnt) for c in text) + spacing * (len(text) - 1)
    if anchor_mid:
        x -= total / 2
    cx = x
    for c in text:
        draw.text((cx, y), c, font=fnt, fill=fill)
        cx += draw.textlength(c, font=fnt) + spacing
    return total


def track_w(draw, text, fnt, spacing=0):
    return sum(draw.textlength(c, font=fnt) for c in text) + spacing * (len(text) - 1)


def vgrad(size, top_a, bot_a, gamma=1.0):
    """
    Vertical alpha ramp (single channel L image).
    gamma > 1 keeps the top of the ramp clearer and loads the opacity
    toward the bottom edge, so photos stay bright but type stays legible.
    """
    w, h = size
    g = Image.new("L", (1, h))
    px = g.load()
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        px[0, y] = int(top_a + (bot_a - top_a) * t)
    return g.resize((w, h))


# ---------------------------------------------------------------- JDM grade
def jdm_grade(img: Image.Image) -> Image.Image:
    """Crushed blacks, cool shadows, restrained saturation, vignette, grain."""
    img = img.convert("RGB")

    # These are bright daylight phone shots - grass, sky, brick, parked cars.
    # The grade has to pull them a long way toward the moody showroom look.

    # 1. desaturate to kill the green grass / blue sky giveaway, but not so
    #    far that the metallic grey paint goes flat
    img = ImageEnhance.Color(img).enhance(0.55)

    # 2. contrast + modest darkening - the subject must stay readable
    img = ImageEnhance.Contrast(img).enhance(1.16)
    img = ImageEnhance.Brightness(img).enhance(0.93)

    # 3. cool the shadows (teal lift), keep highlights neutral
    r, g, b = img.split()
    r = r.point(lambda v: max(0, v - int(14 * (1 - v / 255))))
    g = g.point(lambda v: max(0, v - int(4 * (1 - v / 255))))
    b = b.point(lambda v: min(255, v + int(20 * (1 - v / 255))))
    img = Image.merge("RGB", (r, g, b))

    # 4. crush blacks + roll off highlights so nothing blows out white
    def curve(v):
        v = v / 255.0
        v = max(0.0, (v - 0.040) / 0.960)      # lift black point
        v = v ** 1.05                           # darken midtones slightly
        v = v * 0.97                            # pull highlight ceiling down
        return int(min(255, v * 255))
    lut = [curve(i) for i in range(256)]
    img = img.point(lut * 3)

    # 5. vignette
    w, h = img.size
    vig = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(vig)
    pad = int(min(w, h) * 0.02)
    d.ellipse([-w * 0.22, -h * 0.42, w * 1.22, h * 1.42], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) * 0.22))
    dark = ImageEnhance.Brightness(img).enhance(0.70)
    img = Image.composite(img, dark, vig)

    # 6. fine grain
    rnd = random.Random(7)
    noise = Image.effect_noise((w, h), 11).point(lambda v: int((v - 128) * 0.30 + 128))
    img = ImageChops.overlay(img, noise.convert("RGB")) if False else Image.blend(
        img, ImageChops.add(img, noise.convert("RGB"), scale=1.0, offset=-108), 0.16
    )
    return img


def cover(img, tw, th, bias_y=0.5, bias_x=0.5, zoom=1.0):
    """
    Crop-to-fill tw x th (like CSS object-fit: cover).
    bias_y / bias_x pick which part of the frame survives the crop:
      0.0 = keep the top / left edge, 1.0 = keep the bottom / right edge.
    zoom > 1.0 tightens in on the subject before cropping.
    """
    iw, ih = img.size
    scale = max(tw / iw, th / ih) * zoom
    nw, nh = max(tw, int(iw * scale + 0.5)), max(th, int(ih * scale + 0.5))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = int((nw - tw) * bias_x)
    top = int((nh - th) * bias_y)
    return img.crop((left, top, left + tw, top + th))


def blur_regions(img, regions, strength=0.055):
    """
    Blur normalised (x0,y0,x1,y1) boxes in source coords - used to obscure
    the number plate. Applied BEFORE cropping so coords stay stable.
    """
    if not regions:
        return img
    iw, ih = img.size
    for (x0, y0, x1, y1) in regions:
        box = (int(x0 * iw), int(y0 * ih), int(x1 * iw), int(y1 * ih))
        w, h = box[2] - box[0], box[3] - box[1]
        if w <= 0 or h <= 0:
            continue
        patch = img.crop(box)
        # pixelate then blur - defeats sharpening/upscaling recovery
        small = patch.resize((max(1, w // 14), max(1, h // 14)), Image.BILINEAR)
        patch = small.resize((w, h), Image.NEAREST).filter(
            ImageFilter.GaussianBlur(max(2, int(min(w, h) * strength))))
        img.paste(patch, box)
    return img


def placeholder(tw, th, label, seed):
    """Dark textured stand-in when a photo is missing."""
    rnd = random.Random(seed)
    im = Image.new("RGB", (tw, th), (26, 27, 30))
    d = ImageDraw.Draw(im)
    for i in range(70):
        x0 = rnd.randint(-tw, tw)
        d.line([(x0, 0), (x0 + rnd.randint(-200, 200), th)],
               fill=(rnd.randint(30, 46),) * 3, width=rnd.randint(1, 3))
    im = im.filter(ImageFilter.GaussianBlur(s(3)))
    d = ImageDraw.Draw(im)
    f = rob(s(11), "Bold")
    t = f"[ {label} ]"
    tw2 = d.textlength(t, font=f)
    d.text(((tw - tw2) / 2, th * 0.40), t, font=f, fill=(88, 88, 94))
    f2 = rob(s(9))
    t2 = "photo pending"
    d.text(((tw - d.textlength(t2, font=f2)) / 2, th * 0.40 + s(16)), t2,
           font=f2, fill=(66, 66, 72))
    return im


def load_tile(src, label, tw, th, bias_y=0.5, bias_x=0.5, zoom=1.0, plate=None):
    p = ASSETS / src
    if not p.exists():
        return placeholder(tw, th, label, len(label) * 17), False
    img = Image.open(p).convert("RGB")
    if plate and BLUR_PLATE:
        img = blur_regions(img, plate)
    return cover(img, tw, th, bias_y, bias_x, zoom), True


# ---------------------------------------------------------------- icons
def icon_truck(d, x, y, sz, col):
    w = sz
    bh = sz * 0.52
    d.rounded_rectangle([x, y, x + w * 0.58, y + bh], radius=sz * 0.06,
                        outline=col, width=max(1, sz // 12))
    d.polygon([(x + w * 0.62, y + bh * 0.34), (x + w * 0.84, y + bh * 0.34),
               (x + w, y + bh * 0.62), (x + w, y + bh), (x + w * 0.62, y + bh)],
              outline=col, width=max(1, sz // 12))
    r = sz * 0.11
    for cx in (x + w * 0.20, x + w * 0.80):
        d.ellipse([cx - r, y + bh - r * 0.5, cx + r, y + bh + r * 1.5],
                  outline=col, width=max(1, sz // 12))


def icon_headset(d, x, y, sz, col):
    lw = max(1, sz // 12)
    d.arc([x, y, x + sz, y + sz * 0.92], 180, 360, fill=col, width=lw)
    ew, eh = sz * 0.20, sz * 0.34
    d.rounded_rectangle([x, y + sz * 0.40, x + ew, y + sz * 0.40 + eh],
                        radius=ew * 0.4, outline=col, width=lw)
    d.rounded_rectangle([x + sz - ew, y + sz * 0.40, x + sz, y + sz * 0.40 + eh],
                        radius=ew * 0.4, outline=col, width=lw)


def icon_return(d, x, y, sz, col):
    lw = max(1, sz // 12)
    d.arc([x, y, x + sz, y + sz], 30, 330, fill=col, width=lw)
    a = sz * 0.22
    d.polygon([(x + sz * 0.86, y + sz * 0.10), (x + sz * 0.86 + a * 0.7, y + sz * 0.30),
               (x + sz * 0.70, y + sz * 0.34)], fill=col)


def icon_shield(d, x, y, sz, col):
    lw = max(1, sz // 12)
    d.polygon([(x + sz / 2, y), (x + sz, y + sz * 0.20), (x + sz, y + sz * 0.56),
               (x + sz / 2, y + sz), (x, y + sz * 0.56), (x, y + sz * 0.20)],
              outline=col, width=lw)


def icon_search(d, x, y, sz, col):
    lw = max(1, sz // 9)
    r = sz * 0.36
    d.ellipse([x, y, x + r * 2, y + r * 2], outline=col, width=lw)
    d.line([(x + r * 1.72, y + r * 1.72), (x + sz, y + sz)], fill=col, width=lw)


def icon_user(d, x, y, sz, col):
    lw = max(1, sz // 9)
    r = sz * 0.22
    cx = x + sz / 2
    d.ellipse([cx - r, y + sz * 0.04, cx + r, y + sz * 0.04 + r * 2],
              outline=col, width=lw)
    d.arc([x + sz * 0.06, y + sz * 0.52, x + sz * 0.94, y + sz * 1.28],
          200, 340, fill=col, width=lw)


def icon_cart(d, x, y, sz, col):
    lw = max(1, sz // 9)
    d.line([(x, y + sz * 0.10), (x + sz * 0.18, y + sz * 0.10)], fill=col, width=lw)
    d.polygon([(x + sz * 0.18, y + sz * 0.10), (x + sz, y + sz * 0.10),
               (x + sz * 0.84, y + sz * 0.58), (x + sz * 0.32, y + sz * 0.58)],
              outline=col, width=lw)
    r = sz * 0.10
    for cx in (x + sz * 0.40, x + sz * 0.76):
        d.ellipse([cx - r, y + sz * 0.66, cx + r, y + sz * 0.66 + r * 2],
                  outline=col, width=lw)


# ---------------------------------------------------------------- build
def build():
    canvas = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(canvas)

    # ============================================= HEADER
    d.rectangle([0, 0, W, HEADER_H], fill=BLACK)

    # --- logo: JDM YARD (italic-ish via skew) + 日本車部品
    logo_layer = Image.new("RGBA", (s(300), s(70)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(logo_layer)
    f_logo = osw(s(30), "Bold")
    track(ld, (0, 0), "JDMYARD", f_logo, WHITE + (255,), spacing=s(0.5))
    # skew for the italic slant seen in the mock
    logo_layer = logo_layer.transform(
        logo_layer.size, Image.AFFINE, (1, 0.22, -s(9), 0, 1, 0),
        resample=Image.BICUBIC)
    lx, ly = s(24), s(18)
    canvas.paste(logo_layer, (lx, ly), logo_layer)

    # red "JDM" overlay portion - recolour first 3 glyphs
    red_layer = Image.new("RGBA", (s(300), s(70)), (0, 0, 0, 0))
    rd = ImageDraw.Draw(red_layer)
    track(rd, (0, 0), "JDM", f_logo, RED_BRIGHT + (255,), spacing=s(0.5))
    red_layer = red_layer.transform(
        red_layer.size, Image.AFFINE, (1, 0.22, -s(9), 0, 1, 0),
        resample=Image.BICUBIC)
    canvas.paste(red_layer, (lx, ly), red_layer)

    # 日本車部品 under logo
    f_jp_small = jp(s(10), "Medium")
    jw = track_w(d, "日本車部品", f_jp_small, s(2))
    track(d, (lx + s(6), ly + s(34)), "日本車部品", f_jp_small, RED, spacing=s(2))
    # thin red rules flanking
    ry = ly + s(40)
    d.line([(lx + s(6) + jw + s(6), ry), (lx + s(6) + jw + s(26), ry)],
           fill=(120, 20, 26), width=s(1))

    # --- nav
    nav = ["ホーム", "ショップ", "カテゴリー", "新着アイテム", "お問い合わせ"]
    f_nav = jp(s(12), "Medium")
    gap = s(30)
    widths = [track_w(d, t, f_nav, s(1)) for t in nav]
    nav_total = sum(widths) + gap * (len(nav) - 1)
    nx = (W - nav_total) / 2 + s(10)
    ny = HEADER_H / 2 - s(8)
    for i, (t, tw) in enumerate(zip(nav, widths)):
        col = WHITE if i == 0 else (206, 206, 210)
        track(d, (nx, ny), t, f_nav, col, spacing=s(1))
        if i == 0:
            d.rectangle([nx, ny + s(21), nx + tw, ny + s(21) + s(2)], fill=RED)
        nx += tw + gap

    # --- right icons
    isz = s(19)
    iy = HEADER_H / 2 - isz / 2
    icon_search(d, W - s(120), iy, isz, WHITE)
    icon_user(d, W - s(80), iy - s(1), isz, WHITE)
    icon_cart(d, W - s(40), iy - s(1), isz, WHITE)
    # cart badge
    br = s(8)
    bcx, bcy = W - s(40) + isz - s(1), iy - s(3)
    d.ellipse([bcx - br, bcy - br, bcx + br, bcy + br], fill=RED)
    f_badge = rob(s(9), "Bold")
    bt = "0"
    d.text((bcx - d.textlength(bt, font=f_badge) / 2, bcy - s(6)), bt,
           font=f_badge, fill=WHITE)

    # ============================================= TRUST BAR
    ty0 = HEADER_H
    d.rectangle([0, ty0, W, ty0 + TRUST_H], fill=NEAR_BLACK)
    d.line([(0, ty0), (W, ty0)], fill=HAIRLINE, width=s(1))

    trust = [
        (icon_truck, "FLAT RATE SHIPPING", "Australia Wide", "Excl. Large/Bulky Items"),
        (icon_headset, "LOCAL SUPPORT", "1300-647-2451", None),
        (icon_return, "EASY RETURNS", "T&Cs apply*", None),
        (icon_shield, "SECURE PAYMENT", "Afterpay / Zip / PayPal", None),
    ]
    f_t1 = rob(s(9.5), "Bold")
    f_t2 = rob(s(8), "Regular")
    seg = W / 4.0
    for i, (ico, title, sub, sub2) in enumerate(trust):
        cx = seg * i + seg / 2
        tw = track_w(d, title, f_t1, s(1.2))
        block = s(22) + s(9) + tw
        bx = cx - block / 2
        by = ty0 + TRUST_H / 2
        ico(d, bx, by - s(11), s(21), (232, 232, 236))
        tx = bx + s(22) + s(9)
        track(d, (tx, by - s(11)), title, f_t1, (238, 238, 242), spacing=s(1.2))
        d.text((tx, by - s(1)), sub, font=f_t2, fill=DIM)
        if sub2:
            d.text((tx, by + s(7)), sub2, font=f_t2, fill=(84, 84, 90))
        if i < 3:
            dx = seg * (i + 1)
            d.line([(dx, ty0 + s(12)), (dx, ty0 + TRUST_H - s(12))],
                   fill=HAIRLINE, width=s(1))

    # ============================================= TILE GRID
    # kicker, title, subtitle, source, bias_y, zoom, exposure, plate-blur
    # `exposure` evens out the grid - these are six separate handheld photos
    # shot at different angles to the sun, so each needs its own trim.
    tiles = [
        ("排気系・外装", "EXHAUST & EXTERIOR", "Performance & Styling",
         "6.jpg", 0.26, 1.10, 1.02, None),
        ("インテリア", "INTERIOR PARTS", "Comfort & Style",
         "5.jpg", 0.17, 1.00, 1.00, None),
        ("ライト・電装", "LIGHTING", "Visibility & Style",
         "1.jpg", 0.56, 1.18, 0.96, None),
        ("エアロパーツ", "AERO PARTS", "Form & Function",
         "2.jpg", 0.47, 1.34, 0.74, PLATE_2),
        ("ホイール・アクセサリー", "WHEELS & ACCESSORIES", "Stance & Performance",
         "3.JPG", 0.46, 1.02, 0.94, None),
        ("エンジン・駆動系", "PERFORMANCE", "Power & Reliability",
         "4.jpg", 0.30, 1.06, 0.90, None),
    ]

    gy0 = ty0 + TRUST_H
    found_count = 0
    f_kick = jp(s(8), "Medium")
    f_title = osw(s(17), "SemiBold")
    f_sub = rob(s(9), "Regular")

    for i, (kick, title, sub, src, bias_y, zoom, expo, plate) in enumerate(tiles):
        col, row = i % 3, i // 3
        # last column absorbs rounding remainder
        tw = TILE_W if col < 2 else W - TILE_W * 2
        tx0 = TILE_W * col
        ty = gy0 + TILE_H * row

        photo, found = load_tile(src, title, tw, TILE_H,
                                 bias_y=bias_y, zoom=zoom, plate=plate)
        found_count += found
        if found:
            photo = jdm_grade(photo)
            if expo != 1.0:
                photo = ImageEnhance.Brightness(photo).enhance(expo)

        # bottom scrim for legibility - gentle up top, firm at the base
        scrim_h = int(TILE_H * 0.58)
        ramp = vgrad((tw, scrim_h), 0, 226, gamma=1.9)
        black = Image.new("RGB", (tw, scrim_h), (0, 0, 0))
        region = photo.crop((0, TILE_H - scrim_h, tw, TILE_H))
        region = Image.composite(black, region, ramp)
        photo.paste(region, (0, TILE_H - scrim_h))

        canvas.paste(photo, (tx0, ty))

        # ---- text block, stacked bottom-up using measured glyph heights
        pad = s(15)
        tex = tx0 + pad
        bottom = ty + TILE_H - pad

        def bbox_h(txt, fnt):
            b = d.textbbox((0, 0), txt, font=fnt)
            return b[3] - b[1], b[1]

        sub_h, sub_off = bbox_h(sub, f_sub)
        ttl_h, ttl_off = bbox_h(title, f_title)
        kck_h, kck_off = bbox_h(kick, f_kick)

        LEAD = s(7)          # gap between lines
        sub_y = bottom - sub_h - sub_off
        ttl_y = sub_y + sub_off - LEAD - ttl_h - ttl_off
        kck_y = ttl_y + ttl_off - s(5) - kck_h - kck_off

        # soft drop-shadow pass: render the type into a mask, blur it, and
        # composite black through it. Keeps the red kicker readable over
        # bright chrome / taillights without darkening the whole photo.
        sh_h = int(TILE_H * 0.50)
        sh_top = ty + TILE_H - sh_h
        mask = Image.new("L", (tw, sh_h), 0)
        md = ImageDraw.Draw(mask)
        md.text((tex - tx0, sub_y - sh_top), sub, font=f_sub, fill=255)
        track(md, (tex - tx0, ttl_y - sh_top), title, f_title, 255, spacing=s(0.8))
        track(md, (tex - tx0, kck_y - sh_top), kick, f_kick, 255, spacing=s(1))
        mask = mask.filter(ImageFilter.GaussianBlur(s(3.2)))
        mask = mask.point(lambda v: min(255, int(v * 2.6)))
        canvas.paste(Image.new("RGB", (tw, sh_h), (0, 0, 0)), (tx0, sh_top), mask)

        # crisp type on top
        d.text((tex, sub_y), sub, font=f_sub, fill=(186, 186, 192))
        track(d, (tex, ttl_y), title, f_title, WHITE, spacing=s(0.8))
        track(d, (tex, kck_y), kick, f_kick, RED_BRIGHT, spacing=s(1))

        # ---- red arrow, bottom-right (kept fully inside the tile)
        a_len, a_head = s(15), s(5)
        ax1 = tx0 + tw - pad                    # arrow tip
        ax0 = ax1 - a_len - a_head              # shaft start
        ay = bottom - s(5)
        d.line([(ax0, ay), (ax1 - a_head, ay)], fill=RED_BRIGHT, width=s(2))
        d.polygon([(ax1 - a_head, ay - s(4)), (ax1, ay),
                   (ax1 - a_head, ay + s(4))], fill=RED_BRIGHT)

        # 1px separators
        d.rectangle([tx0, ty, tx0 + s(1), ty + TILE_H], fill=(0, 0, 0))
        d.rectangle([tx0, ty, tx0 + tw, ty + s(1)], fill=(0, 0, 0))

    # ============================================= FOOTER
    fy0 = gy0 + TILE_H * 2
    d.rectangle([0, fy0, W, H], fill=BLACK)
    f_fjp = jp(s(9.5), "Medium")
    f_fen = rob(s(8.5), "Bold")
    l1 = "本物のパーツ。本物のパフォーマンス。"
    l2 = "REAL PARTS. REAL PERFORMANCE."
    track(d, (W / 2, fy0 + s(6)), l1, f_fjp, (170, 170, 176), spacing=s(1.5),
          anchor_mid=True)
    track(d, (W / 2, fy0 + s(21)), l2, f_fen, (96, 96, 102), spacing=s(2.4),
          anchor_mid=True)

    # 日本製 stamp, right
    f_stamp = jp(s(15), "Bold")
    st = "日本製"
    stw = track_w(d, st, f_stamp, s(2))
    track(d, (W - s(24) - stw, fy0 + s(10)), st, f_stamp, (58, 58, 63), spacing=s(2))

    suffix = "" if W == 1600 else f"@{W}"
    out = OUT / f"jdmyard{suffix}.png"
    canvas.save(out, "PNG")
    print(f"wrote {out}  ({W}x{H})  photos found: {found_count}/6")
    return out


if __name__ == "__main__":
    build()
