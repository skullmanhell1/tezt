#!/usr/bin/env python3
"""
JDM YARD spec-sheet poster.

Clean stock, one oversized wordmark, a portrait main plate paired with a full
technical column, four captioned detail plates, a parts index and a
three-column information bar. Registration marks and a sheet code finish it.

Usage:  python3 spec.py                 # 1654 x 2339  (A4 @ 200dpi)
        SPEC_W=2480 python3 spec.py     # A4 @ 300dpi, print
Output: out/spec.png
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

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
PAPER_2 = (238, 238, 236)
INK = (17, 17, 19)
INK_2 = (74, 74, 78)
INK_3 = (132, 132, 137)
RULE = (204, 204, 202)
RULE_L = (222, 222, 220)
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

# Commonly cited Z34 figures - verify against the actual car before printing.
SPECS = [
    ("ENGINE", "VQ37VHR"),
    ("DISPLACEMENT", "3696 CC"),
    ("CONFIGURATION", "60° V6 · DOHC"),
    ("INDUCTION", "NATURALLY ASPIRATED"),
    ("POWER", "328 HP @ 7000 RPM"),
    ("TORQUE", "366 NM @ 5200 RPM"),
    ("LAYOUT", "FRONT ENGINE · RWD"),
    ("GEARBOX", "6-SPEED MANUAL"),
    ("0 - 100 KM/H", "5.1 SECONDS"),
    ("TOP SPEED", "250 KM/H"),
    ("KERB WEIGHT", "1520 KG"),
    ("DISTRIBUTION", "54 / 46 %"),
    ("WHEELBASE", "2550 MM"),
    ("LENGTH", "4250 MM"),
    ("BODY", "2-DOOR COUPE"),
    ("FRONT TYRE", "245 / 40 R19"),
    ("REAR TYRE", "275 / 35 R19"),
    ("PRODUCTION", "2009 - 2020"),
]

PARTS_INDEX = [
    ("排気系・外装", "EXHAUST & EXTERIOR"),
    ("インテリア", "INTERIOR PARTS"),
    ("ライト・電装", "LIGHTING"),
    ("エアロパーツ", "AERO PARTS"),
    ("エンジン・駆動系", "PERFORMANCE"),
]

PLATE_8 = [(0.345, 0.636, 0.672, 0.714)]

# tighter on the car - the previous crop left a large dead area of paving
MAIN = dict(src="7.jpg", bias_y=0.33, zoom=1.10, plate=None)

PLATES = [
    dict(src="9.jpg", cap="THREE QUARTER", bias_y=0.48, zoom=1.08, plate=None),
    dict(src="8.jpg", cap="FRONT", bias_y=0.40, zoom=1.04, plate=PLATE_8),
    dict(src="4.jpg", cap="ENGINE BAY", bias_y=0.34, zoom=1.02, plate=None),
    dict(src="5.jpg", cap="INTERIOR", bias_y=0.20, zoom=1.00, plate=None),
]

FOOT_TITLE = "NISSAN 370Z (2009 - 2020)"
FOOT_BODY = [
    "A FRONT-ENGINE, REAR-WHEEL-DRIVE JDM SPORTS COUPE",
    "BUILT AROUND THE NATURALLY ASPIRATED VQ37VHR V6,",
    "A SHORT WHEELBASE AND HYDRAULIC STEERING.",
]
FOOT_RIGHT = [
    "2009 - 2020  /  Z34  /  RWD",
    "VQ37VHR  ·  3.7 L  ·  V6",
    "328 HP  /  366 NM",
    "THE MODERN Z",
]
FOOT_BRAND = "JDM YARD"
FOOT_HANDLE = "@jdmyard"
FOOT_TAG = "REAL PARTS. REAL PERFORMANCE."
SHEET_CODE = "SHEET 01 / 01  ·  JY-Z34-2026"

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
    for _ in range(24):
        mid = (lo + hi) / 2
        if font(path, int(mid)).getlength(text) < target_w:
            lo = mid
        else:
            hi = mid
    return font(path, int(lo))


# ---------------------------------------------------------------- photo
def clean_grade(img):
    """Bright neutral treatment - the photos sit on near-white stock."""
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


def keyline(d, box, col=(196, 196, 194), w=2):
    d.rectangle([box[0], box[1], box[2] - 1, box[3] - 1], outline=col,
                width=max(1, s(w)))


def reg_marks(d, inset, ln, col=(188, 188, 186)):
    """Corner registration marks - a print-sheet cue."""
    w = max(1, s(1))
    for (cx, cy, sx, sy) in ((inset, inset, 1, 1),
                             (W - inset, inset, -1, 1),
                             (inset, H - inset, 1, -1),
                             (W - inset, H - inset, -1, -1)):
        d.line([(cx, cy), (cx + ln * sx, cy)], fill=col, width=w)
        d.line([(cx, cy), (cx, cy + ln * sy)], fill=col, width=w)


# ---------------------------------------------------------------- build
def build_spec():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    M = s(46)
    inner_w = W - M * 2
    reg_marks(d, s(20), s(26))

    # ================================================ MASTHEAD
    y = s(56)
    f_mast = fit_font(ANTON, MAST, inner_w)
    mb = d.textbbox((0, y), MAST, font=f_mast)
    d.text((M - mb[0], y), MAST, font=f_mast, fill=INK)
    mast_bot = mb[3]
    d.rectangle([M, mast_bot + s(10), W - M, mast_bot + s(14)], fill=RED)

    # ---- meta left, model right
    my = mast_bot + s(30)
    f_meta = arch(11.5, "Bold")
    for i, line in enumerate(HEAD_META):
        track(d, (M, my + i * s(19)), line, f_meta, INK_2, spacing=s(1.6))

    # Archivo Black rather than Anton here: Anton's zero is a plain oval, so
    # "370Z" read as "37OZ". Archivo's zero is unambiguous.
    model_max = inner_w * 0.52
    msize = s(50)
    while msize > s(20) and font(ARCHIVO, msize, "Black").getlength(MODEL) > model_max:
        msize -= s(1)
    f_model = font(ARCHIVO, msize, "Black")
    mdw = d.textlength(MODEL, font=f_model)
    mdb = d.textbbox((0, my - s(8)), MODEL, font=f_model)
    d.text((W - M - mdw, my - s(8)), MODEL, font=f_model, fill=INK)
    f_msub = arch(14, "Bold")
    msw = track_w(d, MODEL_SUB, f_msub, s(5))
    track(d, (W - M - msw, mdb[3] + s(3)), MODEL_SUB, f_msub, RED, spacing=s(5))

    head_bot = max(my + len(HEAD_META) * s(19), mdb[3] + s(24))

    # ================================================ GEOMETRY (bottom-up)
    bar_h = s(206)
    bar_top = H - M - bar_h
    parts_h = s(96)
    parts_top = bar_top - s(22) - parts_h
    det_h = s(292)
    det_top = parts_top - s(22) - det_h
    band_top = head_bot + s(20)
    band_h = det_top - s(22) - band_top

    # ================================================ BAND: main plate + specs
    col_gap = s(22)
    main_w = int(inner_w * 0.555)
    spec_x = M + main_w + col_gap
    spec_w = W - M - spec_x

    main = load(MAIN, main_w, band_h)
    canvas.paste(main, (M, band_top))
    d = ImageDraw.Draw(canvas)
    keyline(d, (M, band_top, M + main_w, band_top + band_h))

    cap = "FEATURED CAR"
    f_cap = arch(11, "Bold")
    cw = track_w(d, cap, f_cap, s(2)) + s(22)
    d.rectangle([M, band_top, M + cw, band_top + s(27)], fill=INK)
    track(d, (M + s(11), band_top + s(8)), cap, f_cap, PAPER, spacing=s(2))

    # vertical Japanese accent, set in a dark chip so it stays readable over
    # whatever falls behind it - at near-white it was invisible
    f_jp = njp(14)
    jx, jy = M + main_w - s(30), band_top + s(40)
    chip_h = s(20) * len(JP_ACCENT) + s(14)
    d.rectangle([jx - s(7), jy - s(7), jx + s(21), jy + chip_h - s(7)],
                fill=(20, 20, 22))
    for chx in JP_ACCENT:
        d.text((jx, jy), chx, font=f_jp, fill=(242, 242, 240))
        jy += s(20)

    # ---- technical column
    f_sh = arch(12, "Bold")
    track(d, (spec_x, band_top + s(2)), "TECHNICAL DATA", f_sh, INK,
          spacing=s(2.4))
    f_shjp = njp(12)
    track(d, (spec_x, band_top + s(20)), "主要諸元", f_shjp, RED, spacing=s(3))
    d.rectangle([spec_x, band_top + s(40), W - M, band_top + s(43)], fill=INK)

    # Label and value share one baseline, label left / value right, rule under
    # each row. Staggering them onto separate lines read as a zigzag and wasted
    # most of the column's vertical space.
    rows_top = band_top + s(52)
    rows_h = band_h - s(52)
    row_h = rows_h / len(SPECS)
    f_k = arch(10, "Bold")
    f_v = osw(18, "SemiBold")
    for i, (k, v) in enumerate(SPECS):
        ry = rows_top + row_h * i
        cy = ry + row_h / 2
        kb = d.textbbox((0, 0), k, font=f_k)
        vb = d.textbbox((0, 0), v, font=f_v)
        track(d, (spec_x, cy - (kb[3] - kb[1]) / 2 - kb[1]), k, f_k, INK_3,
              spacing=s(1.5))
        vw = track_w(d, v, f_v, s(0.4))
        track(d, (W - M - vw, cy - (vb[3] - vb[1]) / 2 - vb[1]), v, f_v, INK,
              spacing=s(0.4))
        if i < len(SPECS) - 1:
            d.line([(spec_x, ry + row_h), (W - M, ry + row_h)],
                   fill=RULE_L, width=max(1, s(1)))

    # ================================================ DETAIL PLATES
    n = len(PLATES)
    dgap = s(14)
    pw = (inner_w - dgap * (n - 1)) // n
    for i, p in enumerate(PLATES):
        px = M + (pw + dgap) * i
        img = load(p, pw, det_h)
        canvas.paste(img, (px, det_top))
        d = ImageDraw.Draw(canvas)
        keyline(d, (px, det_top, px + pw, det_top + det_h))
        strip_y = det_top + det_h - s(24)
        d.rectangle([px, strip_y, px + pw, det_top + det_h], fill=INK)
        d.rectangle([px, strip_y, px + s(30), det_top + det_h], fill=RED)
        f_ix = arch(10.5, "Bold")
        track(d, (px + s(9), strip_y + s(6)), f"{i + 1:02d}", f_ix, PAPER,
              spacing=s(1))
        track(d, (px + s(40), strip_y + s(6)), p["cap"], f_ix, PAPER,
              spacing=s(1.6))

    # ================================================ PARTS INDEX
    d.rectangle([M, parts_top, W - M, parts_top + s(3)], fill=INK)
    f_pi = arch(10.5, "Bold")
    track(d, (M, parts_top + s(12)), "PARTS INDEX", f_pi, INK, spacing=s(2.4))
    track(d, (M + s(120), parts_top + s(12)), "取扱カテゴリー", njp(11), RED,
          spacing=s(2))
    pn = len(PARTS_INDEX)
    pgap = s(12)
    cwid = (inner_w - pgap * (pn - 1)) / pn
    py = parts_top + s(38)
    f_pjp = njp(13)
    f_pen = arch(10, "Bold")
    for i, (jp_, en) in enumerate(PARTS_INDEX):
        cx = M + (cwid + pgap) * i
        d.rectangle([cx, py, cx + cwid, py + s(46)], fill=PAPER_2)
        d.rectangle([cx, py, cx + s(4), py + s(46)], fill=RED)
        track(d, (cx + s(12), py + s(7)), jp_, f_pjp, INK, spacing=s(1))
        track(d, (cx + s(12), py + s(28)), en, f_pen, INK_3, spacing=s(1.4))

    # ================================================ INFORMATION BAR
    d.rectangle([M, bar_top, W - M, bar_top + bar_h], fill=BAR)
    d.rectangle([M, bar_top, W - M, bar_top + s(5)], fill=RED)

    c1 = M + s(24)
    c2 = M + int(inner_w * 0.46)
    c3 = W - M - s(24)
    by = bar_top + s(28)

    f_ft = arch(16, "Bold")
    f_fb = rob(14.5, "Regular")
    track(d, (c1, by), FOOT_TITLE, f_ft, PAPER, spacing=s(1.4))
    for i, line in enumerate(FOOT_BODY):
        d.text((c1, by + s(28) + i * s(20)), line, font=f_fb,
               fill=(190, 190, 193))

    # middle column: brand lockup
    f_bd = font(ANTON, s(34))
    d.text((c2, by - s(4)), FOOT_BRAND, font=f_bd, fill=PAPER)
    d.text((c2, by + s(36)), FOOT_HANDLE, font=rob(15, "Bold"), fill=RED)
    f_tag = arch(11, "Bold")
    track(d, (c2, by + s(60)), FOOT_TAG, f_tag, (170, 170, 173), spacing=s(2))

    # right column: figures, right aligned
    ry2 = by
    for i, line in enumerate(FOOT_RIGHT):
        f = arch(14, "Bold") if i == 0 else f_fb
        col = PAPER if i == 0 else (185, 185, 188)
        lw = d.textlength(line, font=f)
        d.text((c3 - lw, ry2), line, font=f, fill=col)
        ry2 += s(22)

    # sheet code + rule along the base of the bar
    d.line([(c1, bar_top + bar_h - s(44)), (c3, bar_top + bar_h - s(44))],
           fill=(52, 52, 56), width=max(1, s(1)))
    f_sc = arch(10, "Bold")
    track(d, (c1, bar_top + bar_h - s(32)), SHEET_CODE, f_sc, (140, 140, 144),
          spacing=s(2))

    # barcode block, bottom right of the bar
    bw_total = s(150)
    bx0 = c3 - bw_total
    byy = bar_top + bar_h - s(34)
    seed = 0
    for chx in SHEET_CODE:
        seed = (seed * 31 + ord(chx)) & 0xFFFF
    xcur = bx0
    while xcur < c3 - s(2):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        bwid = s(1) + (seed >> 16) % s(3)
        if (seed >> 8) % 3:
            d.rectangle([xcur, byy, xcur + bwid, byy + s(22)], fill=(214, 214, 216))
        xcur += bwid + s(2)

    out = OUT / (f"spec@{W}.png" if W != 1654 else "spec.png")
    canvas.save(out, "PNG")
    print(f"wrote {out}  ({W}x{H})  main={MAIN['src']}  "
          f"plates={[p['src'] for p in PLATES]}")
    return out


if __name__ == "__main__":
    build_spec()
