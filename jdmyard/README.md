# JDM YARD hero image

Flat PNG of the JDM-themed category-grid hero, rendered from the six car photos
in the repo root.

| File | Size | Use |
|---|---|---|
| `jdmyard-hero.png` | 1600 × 843 | web |
| `jdmyard-hero@2x.png` | 3200 × 1686 | retina / print |

## Tile mapping

| Tile | Category | Photo |
|---|---|---|
| 1 | EXHAUST & EXTERIOR | `6.jpg` |
| 2 | INTERIOR PARTS | `5.jpg` |
| 3 | LIGHTING | `1.jpg` |
| 4 | AERO PARTS | `2.jpg` |
| 5 | WHEELS & ACCESSORIES | `3.JPG` |
| 6 | PERFORMANCE | `4.jpg` |

## Regenerating

```sh
pip install Pillow

mkdir -p assets fonts out
cp ../[1-6].* assets/          # source photos from repo root

# fonts (both SIL OFL 1.1)
curl -sSL -o "fonts/NotoSansJP[wght].ttf" \
  "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
curl -sSL -o "fonts/Oswald[wght].ttf" \
  "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf"
curl -sSL -o "fonts/RobotoCondensed.ttf" \
  "https://github.com/google/fonts/raw/main/ofl/robotocondensed/RobotoCondensed%5Bwght%5D.ttf"

python3 build.py               # 1600px
JDM_W=3200 python3 build.py    # 2x
```

## Tuning

Per-tile settings live in the `tiles` list in `build.py`:

- `bias_y` — which slice of the frame survives the crop. `0.0` keeps the top
  edge, `1.0` the bottom. Four of the six photos are portrait (0.75) being
  cropped to a 1.92 tile, so this does most of the compositional work.
- `zoom` — tightens in on the subject before cropping; useful for pushing
  distracting background (grass, parked cars) out of frame.
- `exposure` — per-tile brightness trim. The photos were shot handheld at
  different angles to the sun, so this is what keeps the grid looking even.

Global look lives in `jdm_grade()`: desaturation, contrast, teal shadow push,
black-point crush, vignette, grain.

`BLUR_PLATE = True` pixelates the number plate in `2.jpg`. Set it to `False`
to leave the plate legible.

## Notes

- Copy corrected from the original mockup: `LOAYS RETURN` → `EASY RETURNS`,
  `SECUBE PAYMENT` → `SECURE PAYMENT`, `Afterpey / Zio` → `Afterpay / Zip`.
- Browser chrome from the mockup screenshot is intentionally not reproduced.
