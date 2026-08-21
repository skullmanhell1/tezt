# JDM YARD hero image

Flat PNG of the JDM-themed category-grid hero, rendered from the six car photos
in the repo root.

| File | Size | Use |
|---|---|---|
| `jdmyard-hero.png` | 1600 × 889 | web |
| `jdmyard-hero@2x.png` | 3200 × 1779 | retina / print |

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

`SHOW_CHROME = True` stacks a Chrome-style toolbar above the page, so the
render reads as a live site. `URL_TEXT` sets the address shown. Set
`SHOW_CHROME = False` for a clean hero with no browser frame.

## Notes

- Copy corrected from the original mockup: `LOAYS RETURN` → `EASY RETURNS`,
  `SECUBE PAYMENT` → `SECURE PAYMENT`, `Afterpey / Zio` → `Afterpay / Zip`.
- The browser toolbar is drawn, not screenshotted — so the address reads
  cleanly at any export size. Toggle it with `SHOW_CHROME`.


---

# Poster (`poster.py`)

A4-proportioned magazine-style cover poster.

```sh
python3 poster.py              # 1654 x 2339  (A4 @ 200dpi)
POSTER_W=2480 python3 poster.py   # A4 @ 300dpi, for print
```

Output: `poster.png` / `poster@2480.png`.

## Structure

Top strip → masthead block (wordmark, stars, MAGAZINE, tagline, 日本車専門誌)
→ full-bleed hero with round badge, outlined headline and gold script subhead
→ feature strip (owner name in script) → three owner cards → bottom social bar.

Hero height is derived from whatever is left over after the fixed blocks, so
changing `mast_h`, `bot_h` or the card sizes never leaves dead space above the
bottom bar. The masthead is measured at render time and prints a clearance
check — if content would slide under the hero, the script warns with the exact
number of pixels to add to `mast_h`.

## Variants

```sh
python3 poster.py                     # A: hero 1.jpg, cards 7/8/9
POSTER_VARIANT=b python3 poster.py    # B: hero 7.jpg, cards 8/9/3
```

Variant B promotes the golden-hour shot to the hero. `1.jpg` is a tight crop of
spoiler and taillight — it does not read as a car at cover size, and the poster
lives or dies on its hero. `7.jpg` is the only full-car shot dramatic enough to
carry the page, so it moves up and the wheel shot backfills the third card.

## Swapping photos

`HERO` and the three entries in `CARDS` each take a `src` filename from
`assets/`, plus `bias_y`, `zoom` and `expo` with the same meaning as in
`build.py`. To use a new photo, drop it in `assets/` and change `src`.

The plate is legible in `8.jpg` as well as `2.jpg`; `PLATE_8` pixelates it.

## Japanese-magazine treatment

Density devices borrowed from Japanese car-magazine convention:

- marker-separated cover lines in the top strip, gold Latin against white kana
- stacked kanji headline (`STACK`) in white with a red outline and hard offset
  shadow, over a gold year chip
- rotated corner flash (`BANNER_JP`)
- marker-led cover lines down the right of the hero (`COVER_LINES`), gold Latin
  above white Japanese
- gold issue box with number, Japanese date and Latin month
- `print_pass()` finishes with a halftone dot screen, grain and a warm tint so
  it reads as printed stock rather than a flat digital export

## Copy

All text sits in named constants at the top of the file: `STRIP`, `MAST_1`,
`MAST_2`, `SUBHEAD`, `TAGLINE`, `JP_TAGLINE`, `BADGE`, `HEAD_1`, `HEAD_2`,
`FEATURE`, `CARDS`, and the `BOT_*` values. Owner names and handles are
placeholders.

## Note on the reference

The layout language follows newsstand car-magazine convention. The masthead,
wordmark and all copy are JDM Yard's own — no third-party magazine name, logo
or trade dress is reproduced.
