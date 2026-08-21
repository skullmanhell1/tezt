#!/usr/bin/env python3
"""
JDM YARD spec-sheet poster.

Clean stock, one oversized wordmark, photo plates, a spec table and a dense
information bar along the base. Deliberately minimal - the opposite of the
aged magazine treatment in poster.py.

Usage:  python3 spec.py                 # 1654 x 2339  (A4 @ 200dpi)
        SPEC_W=2480 python3 spec.py     # A4 @ 300dpi, print
Output: out/spec.png
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from build import blur_regions, font, track, track_w, FONTS, ASSETS

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

W = int(os.environ.get("SPEC_W", 1654))
H = int(round(W * 297 / 210.0))
SC = W / 1654.0


def s(px):
    return max(1, int(round(px * SC)))


# ---------------------------------------------------------------- palette
PAPER = (246, 246, 245)
INK = (17, 17, 19)
INK_2 = (72, 72, 76)
INK_3 = (128, 128, 133)
RULE = (206, 206, 204)
RED = (198, 24, 32)
BAR = (16, 16, 18)

# ---------------------------------------------------------------- copy
MAST = "JDM YARD"
MODEL = "NISSAN 370Z"
MODEL_SUB = "Z34"

HEAD_META = [
    "MANUFACTURED BY NISSAN MOTOR CO., LTD.",
    "ORIGIN : JAPAN",
    "CHASSIS : Z34",
]

JP_ACCENT = "日本車専門店"

# Commonly cited Z34 figures - adjust to your car's actual spec.
SPECS = [
    ("ENGINE", "VQ37VHR"),
    ("DISPLACEMENT", "3.7 L V6"),
    ("POWER", "328 HP"),
    ("TORQUE", "366 NM"),
    ("LAYOUT", "FRONT ENGINE / RWD"),
    ("GEARBOX", "6MT / 7AT"),
    ("0-100 KM/H", "5.1 S"),
    ("KERB WEIGHT", "1520 KG"),
    ("WHEELS", '19" FORGED'),
    ("PRODUCTION", "2009 - 2020"),
]

MAIN = dict(src="7.jpg", bias_y=0.46, zoom=1.02, plate=None)

PLATE_8 = [(0.345, 0.636, 0.672, 0.714)]
PLATES = [
    dict(src="9.jpg", cap="THREE QUARTER", bias_y=0.48, zoom=1.10, plate=None),
    dict(src="8.jpg", cap="FRONT", bias_y=0.40, zoom=1.04, plate=PLATE_8),
    dict(src="3.JPG", cap="FORGED WHEEL", bias_y=0.46, zoom=1.02, plate=None),
]

FOOT_TITLE = "NISSAN 370Z (2009 - 2020)"
FOOT_BODY = [
    "A FRONT-ENGINE, REAR-WHEEL-DRIVE JDM SPORTS COUPE BUILT",
    "AROUND THE NATURALLY ASPIRATED VQ37VHR V6, A SHORT",
    "WHEELBASE AND A HYDRAULIC STEERING RACK.",
]
FOOT_RIGHT = [
    "NISSAN 370Z",
    "2009 - 2020  /  Z34  /  RWD",
    "VQ37VHR  ·  3.7 L  ·  V6",
    "THE MODERN Z",
]
FOOT_BRAND = "JDM YARD"
FOOT_HANDLE = "@jdmyard"
FOOT_TAG = "REAL PARTS. REAL PERFORMANCE."

# ---------------------------------------------------------------- fonts
ANTON = FONTS / "Anton-Regular.ttf"
ARCHIVO = FONTS / "Archivo[wdth,wght].ttf"
OSWALD = FONTS / "Oswald[wght].ttf"
ROBOTO = FONTS / "RobotoCondensed.ttf"
NOTOJP = FONTS / "NotoSansJP[wght].ttf"


def arch(sz, w="SemiBold"):
    return font(ARCHIVO, s(sz), w)


def osw(sz, w="Bold"):
    return font(OSWALD, s(sz), w)


def rob(sz, w="Regular"):
    return font(ROBOTO, s(sz), w)


def njp(sz, w="Bold"):
    return font(NOTOJP, s(sz), w)


def fit_font(path, text, target_w, lo=40, hi=1000):
    """Solve for the point size whose rendered width fills target_w."""
    for _ in range(24):
        mid = (lo + hi) / 2
        if font(path, int(mid)).getlength(text) < target_w:
            lo = mid
        else:
            hi = mid
    return font(path, int(lo))


# ---------------------------------------------------------------- photo
def clean_grade(img):
    """
    Bright neutral treatment. The photos sit on near-white stock, so the moody
    grade used elsewhere would fight the page. Pull saturation back, lift a
    touch, keep it honest.
    """
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(0.58)
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Brightness(img).enhance(1.05)

    def curve(v):
        v = v / 255.0
        v = max(0.0, (v - 0.02) / 0.98)
        v = v ** 0.95
        return int(min(255, v * 255))
    return img.point([curve(i) for i in range(256)] * 3)


def load(spec, tw, th):
    p = ASSETS / spec["src"]
    if not p.exists():
        im = Image.new("RGB", (tw, th), (228, 228, 226))
        d = ImageDraw.Draw(im)
        f = rob(14, "Bold")
        t = f"[ {spec['src']} missing ]"
        d.text(((tw - d.textlength(t, font=f)) / 2, th / 2), t, font=f, fill=INK_3)
        return im
    img = Image.open(p).convert("RGB")
    if spec.get("plate"):
        img = blur_regions(img, spec["plate"])
    iw, ih = img.size
    sc = max(tw / iw, th / ih) * spec.get("zoom", 1.0)
    nw, nh = max(tw, int(iw * sc + .5)), max(th, int(ih * sc + .5))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = int((nw - tw) * 0.5)
    top = int((nh - th) * spec.get("bias_y", 0.5))
    return clean_grade(img.crop((left, top, left + tw, top + th)))


# ---------------------------------------------------------------- build
def build_spec():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    M = s(46)
    inner_w = W - M * 2

    # thin frame
    fi = s(20)
    d.rectangle([fi, fi, W - fi - 1, H - fi - 1], outline=(214, 214, 212),
                width=max(1, s(2)))

    # ================================================ MASTHEAD
    y = s(58)
    f_mast = fit_font(ANTON, MAST, inner_w)
    mb = d.textbbox((0, y), MAST, font=f_mast)
    d.text((M - mb[0], y), MAST, font=f_mast, fill=INK)
    mast_bot = mb[3]

    # red hairline directly under the wordmark
    d.rectangle([M, mast_bot + s(10), W - M, mast_bot + s(10) + s(4)], fill=RED)

    # ---- meta block left, model right
    my = mast_bot + s(28)
    f_meta = arch(11.5, "Bold")
    for i, line in enumerate(HEAD_META):
        track(d, (M, my + i * s(19)), line, f_meta, INK_2, spacing=s(1.6))

    f_model = font(ANTON, s(62))
    mdw = d.textlength(MODEL, font=f_model)
    mdb = d.textbbox((0, my - s(6)), MODEL, font=f_model)
    d.text((W - M - mdw, my - s(6)), MODEL, font=f_model, fill=INK)
    f_msub = arch(15, "Bold")
    msw = track_w(d, MODEL_SUB, f_msub, s(5))
    track(d, (W - M - msw, mdb[3] + s(4)), MODEL_SUB, f_msub, RED, spacing=s(5))

    head_bot = max(my + len(HEAD_META) * s(19), mdb[3] + s(26))

    # ================================================ GEOMETRY (bottom-up)
    bar_h = s(226)
    bar_top = H - M - bar_h
    spec_h = s(120)
    spec_top = bar_top - s(26) - spec_h
    plate_h = s(300)
    plate_top = spec_top - s(24) - plate_h
    main_top = head_bot + s(22)
    main_h = plate_top - s(20) - main_top

    # ================================================ MAIN PLATE
    main = load(MAIN, inner_w, main_h)
    canvas.paste(main, (M, main_top))
    d = ImageDraw.Draw(canvas)
    d.rectangle([M, main_top, M + inner_w - 1, main_top + main_h - 1],
                outline=(196, 196, 194), width=max(1, s(2)))

    # corner caption on the main plate
    cap = "FEATURED CAR"
    f_cap = arch(11, "Bold")
    cw = track_w(d, cap, f_cap, s(2)) + s(20)
    d.rectangle([M, main_top, M + cw, main_top + s(26)], fill=INK)
    track(d, (M + s(10), main_top + s(7)), cap, f_cap, PAPER, spacing=s(2))

    # vertical Japanese accent down the right of the main plate
    f_jp = njp(15)
    jx = M + inner_w - s(30)
    jy = main_top + s(40)
    for ch in JP_ACCENT:
        d.text((jx, jy), ch, font=f_jp, fill=(238, 238, 236))
        jy += s(21)

    # ================================================ DETAIL PLATES
    gap = s(16)
    pw = (inner_w - gap * 2) // 3
    for i, p in enumerate(PLATES):
        px = M + (pw + gap) * i
        img = load(p, pw, plate_h)
        canvas.paste(img, (px, plate_top))
        d = ImageDraw.Draw(canvas)
        d.rectangle([px, plate_top, px + pw - 1, plate_top + plate_h - 1],
                    outline=(196, 196, 194), width=max(1, s(2)))
        # index + caption strip across the base of the plate
        f_ix = arch(11, "Bold")
        strip_y = plate_top + plate_h - s(24)
        d.rectangle([px, strip_y, px + pw, plate_top + plate_h], fill=INK)
        d.rectangle([px, strip_y, px + s(30), plate_top + plate_h], fill=RED)
        track(d, (px + s(8), strip_y + s(6)), f"{i + 1:02d}", f_ix, PAPER,
              spacing=s(1))
        track(d, (px + s(40), strip_y + s(6)), p["cap"], f_ix, PAPER,
              spacing=s(1.6))

    # ================================================ SPEC TABLE
    d.rectangle([M, spec_top, W - M, spec_top + s(3)], fill=INK)
    cols = 5
    rows = 2
    cell_w = inner_w / cols
    cell_h = (spec_h - s(10)) / rows
    f_k = arch(10, "Bold")
    f_v = osw(19, "SemiBold")
    for i, (k, v) in enumerate(SPECS[:cols * rows]):
        c, r = i % cols, i // cols
        cx = M + cell_w * c
        cy = spec_top + s(12) + cell_h * r
        track(d, (cx, cy), k, f_k, INK_3, spacing=s(1.6))
        track(d, (cx, cy + s(15)), v, f_v, INK, spacing=s(0.4))
        if c < cols - 1:
            d.line([(cx + cell_w - s(10), cy - s(2)),
                    (cx + cell_w - s(10), cy + cell_h - s(14))],
                   fill=RULE, width=max(1, s(1)))
        if r == 0:
            d.line([(M, spec_top + s(10) + cell_h - s(6)),
                    (W - M, spec_top + s(10) + cell_h - s(6))],
                   fill=RULE, width=max(1, s(1)))

    # ================================================ INFORMATION BAR
    d.rectangle([M, bar_top, W - M, bar_top + bar_h], fill=BAR)
    d.rectangle([M, bar_top, W - M, bar_top + s(5)], fill=RED)

    bx = M + s(24)
    by = bar_top + s(26)
    f_ft = arch(17, "Bold")
    f_fb = rob(15, "Regular")
    track(d, (bx, by), FOOT_TITLE, f_ft, PAPER, spacing=s(1.4))
    for i, line in enumerate(FOOT_BODY):
        d.text((bx, by + s(30) + i * s(21)), line, font=f_fb, fill=(196, 196, 198))

    # brand block, bottom left of the bar
    f_bd = font(ANTON, s(30))
    d.text((bx, bar_top + bar_h - s(58)), FOOT_BRAND, font=f_bd, fill=PAPER)
    f_hd = rob(15, "Bold")
    d.text((bx + d.textlength(FOOT_BRAND, font=f_bd) + s(14),
            bar_top + bar_h - s(44)), FOOT_HANDLE, font=f_hd, fill=RED)

    # right column, right aligned
    rx = W - M - s(24)
    f_r1 = arch(15, "Bold")
    ry = by
    for i, line in enumerate(FOOT_RIGHT):
        f = f_r1 if i == 0 else f_fb
        col = PAPER if i == 0 else (190, 190, 192)
        lw = d.textlength(line, font=f)
        d.text((rx - lw, ry), line, font=f, fill=col)
        ry += s(24) if i == 0 else s(21)

    f_tag = arch(12, "Bold")
    tw = track_w(d, FOOT_TAG, f_tag, s(2.6))
    track(d, (rx - tw, bar_top + bar_h - s(34)), FOOT_TAG, f_tag, RED,
          spacing=s(2.6))

    out = OUT / (f"spec@{W}.png" if W != 1654 else "spec.png")
    canvas.save(out, "PNG")
    print(f"wrote {out}  ({W}x{H})  main={MAIN['src']}  "
          f"plates={[p['src'] for p in PLATES]}")
    return out


if __name__ == "__main__":
    build_spec()
