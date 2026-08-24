# APEX PREDATOR MMA — Marketing Booklet

Subculture: **MMA (mixed martial arts)**.

A 16-page print-ready A4 booklet covering the research, semiotic analysis, ideation and
marketing plan for **APEX PREDATOR MMA** — a fight-wear brand aimed at the MMA subculture.
Branded to match the existing `mma-coverpage/` cover page (same lockup, palette and typefaces).

**Output:** `APEX-MMA-Marketing-Booklet.pdf`

## How it answers the brief

### Research

| Brief requirement | Where it is |
|---|---|
| A definition of the group — what it is, and what makes it different from the wider culture | p4 §02 — definition plus six explicit points of difference |
| Demographics — age, gender, nationality, cultural identity | p5 §03 — one block per question, plus an indicative stats strip |
| Shared interests — hobbies and activities, values and beliefs | p6 §04 |
| Shared interests — lifestyle and attitudes | p7 §05, plus a training-week diagram |
| Semiotics — what the signifiers are | p8 §06 — 10 signifiers in a table |
| Semiotics — denotation and connotation, defined and applied | p8 §06 — both terms defined, then a denotation and a connotation column for every signifier |
| Semiotics — could anyone misinterpret the symbols? | p9 §07 — an "inside the subculture / misread by everyone else" table, then the design decisions that follow from it |
| Marketability — who in the subculture would buy it, specifically | p14 §12 — three named buyer profiles ranked by credibility, plus the B2B gym channel and an explicit "who we are not chasing" |
| Marketability — how you will reach them | p15 §13 — six channels, a year-one budget split, and three non-negotiable rules |

### Ideation and production

| Brief requirement | Where it is |
|---|---|
| Mood board | p10 §08 |
| Mind map | p11 §09 — maps each researched signifier onto a usable design device |
| Brainstorm | p11 §09 |
| Thumbnail sketches | p11 §09 — five layout options with the selected one marked |
| `.pdf` final product | `APEX-MMA-Marketing-Booklet.pdf` |
| **Photography must be used** | 20 photographic frames throughout, with the full plan and contact sheet on p13 §11. See "Photography" below. |

## Contents

| Page | Section |
|---:|---|
| 1 | Cover |
| 2 | Contents |
| 3 | 01 Introduction / About the brand |
| 4 | 02 The subculture — definition |
| 5 | 03 The subculture — demographics |
| 6 | 04 Shared interests, activities & values |
| 7 | 05 Shared lifestyle & attitudes |
| 8 | 06 Semiotics — signs & symbols |
| 9 | 07 Semiotics — meaning & misreading |
| 10 | 08 Mood board |
| 11 | 09 Ideation — mind map, thumbnails, brainstorm |
| 12 | 10 The product — design system |
| 13 | 11 Photography plan & contact sheet |
| 14 | 12 Marketability — who would buy it |
| 15 | 13 Marketing plan — how we reach them |
| 16 | 14 Conclusion / back cover |

## Photography

The brief requires photography, and these have to be **your own** photographs — so the booklet
ships with all 20 frames as *placeholder slots* rather than stock images.

Each slot is drawn as a labelled frame showing the shot brief, so the booklet is fully laid out
before you shoot. To fill one:

1. Take the shot (briefs are in **[SHOT-LIST.md](SHOT-LIST.md)**, and printed in the booklet on p13).
2. Save it as `photos/<slot-code>.jpg` — for example `photos/hero-01.jpg`.
3. Re-run the build. The image is centre-cropped to fit, so the aspect ratio does not matter.

Accepted extensions: `.jpg`, `.jpeg`, `.png`. The build prints which slots are still empty, and
p13's contact sheet shows the whole set at a glance.

## Building

```bash
pip install reportlab pillow
python3 build_mma_booklet.py
```

Writes `APEX-MMA-Marketing-Booklet.pdf` and regenerates `SHOT-LIST.md`.

## Editing

Everything is in `build_mma_booklet.py`, one clearly commented block per page.

| To change | Edit |
|---|---|
| Colours | the palette constants at the top (`INK`, `RED`, `SILVER`, …) |
| Typefaces | `DISP` / `LBL` / `REG`, and the files in `fonts/` |
| Shot briefs and slot codes | the `SHOTS` dict — this drives the placeholders, the contact sheet and `SHOT-LIST.md` |
| Any page's copy | the strings in that page's block |
| Page furniture | the `Book` class (`section_head`, `bullets`, `table`, `photo`, `footer`, `tab`) |

`Book.bullets()` wraps text measuring each word in the font it is actually drawn in, so a bold
lead-in cannot push a line past the column edge. `Book.table()` measures every column in its own
font before setting the row height, so cells cannot clip.

## Files

| File | Use |
|---|---|
| `APEX-MMA-Marketing-Booklet.pdf` | the final product — 16pp, A4, print-ready |
| `build_mma_booklet.py` | the source that generates it |
| `SHOT-LIST.md` | the 20 photography briefs (generated) |
| `photos/` | drop your own photographs here |
| `brand/APEX-MMA-poster.png` | the existing cover artwork, placed on p10 |
| `brand/hero-fighter.png` | silhouette, used as the p16 watermark |
| `fonts/` | Anton and Barlow Condensed |

## Credits

- **Anton** and **Barlow Condensed** — Google Fonts, [SIL Open Font License 1.1](https://openfontlicense.org/).
- **Hero fighter silhouette** — derived from a public-domain (CC0) Muay Thai silhouette from
  Openclipart: <https://openclipart.org/detail/72421/muaythai003>. Carried over from
  `mma-coverpage/`; no attribution is legally required, this note is courtesy.
- All other artwork — crest, claw mark, cage mesh, glows, diagrams, mockups — is generated by
  `build_mma_booklet.py`.

Demographic figures are presented in the booklet as **indicative ranges** drawn from gym-level
observation and published audience profiles, and are labelled as such on p5. They are not survey
data. Pricing is indicative RRP for a fictional brand.
