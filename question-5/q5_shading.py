"""
Question 5 - 68-95-99.7 rule refined to the nearest 1/2 sigma.
Generates the four shaded normal-curve diagrams (left-tailed, right-tailed,
centred, bounded) using the z-scores calculated in Question 4.

Q4:  mu = 3.9 bushels, sigma = 0.45 bushels,  z = (X - mu) / sigma
  (i)   X = 4.125  ->  z =  0.5
  (ii)  X = 4.35   ->  z =  1.0
  (iii) X = 3.675  ->  z = -0.5
  (iv)  X = 4.575  ->  z =  1.5
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# ---------------------------------------------------------------- band values
# Proportion of the distribution inside each 1/2-sigma band, -3.5 -> +3.5.
EDGES = np.arange(-3.5, 4.0, 0.5)
BANDS = [0.1, 0.5, 1.7, 4.4, 9.2, 15.0, 19.1, 19.1, 15.0, 9.2, 4.4, 1.7, 0.5, 0.1]

# Cumulative proportion below each 1/2-sigma mark, keyed by z.
CUMULATIVE = {-4.0: 0.0, -3.5: 0.0}
_running = 0.0
for _edge, _band in zip(EDGES[:-1], BANDS):
    _running += _band
    CUMULATIVE[round(_edge + 0.5, 1)] = round(_running, 1)
CUMULATIVE[4.0] = 100.0

# Q4 results: z-score -> the X-score (bushels) it came from.
X4 = {-0.5: 3.675, 0.5: 4.125, 1.0: 4.35, 1.5: 4.575}


def phi(x):
    """Standard normal probability density."""
    return np.exp(-0.5 * x**2) / np.sqrt(2 * np.pi)


def band_sum(lo, hi):
    """Sum the printed band percentages between two 1/2-sigma marks."""
    total = 0.0
    for edge, band in zip(EDGES[:-1], BANDS):
        if lo - 1e-9 <= edge and edge + 0.5 <= hi + 1e-9:
            total += band
    return round(total, 1)


# ------------------------------------------------------------------- plotting
def draw(ax, title, shade_from, shade_to, statement, workings, compact=False,
         scale=None, show_bands=True, show_ticks=True):
    if scale is None:
        scale = 0.8 if compact else 1.0
    x = np.linspace(-4, 4, 2000)
    y = phi(x)
    peak = phi(0.0)

    # Shaded region.
    xs = np.linspace(shade_from, shade_to, 1000)
    ax.fill_between(xs, phi(xs), color="#4a7fb5", alpha=0.55, zorder=1)

    # The curve itself.
    ax.plot(x, y, color="black", linewidth=1.6, zorder=4)

    # 1/2-sigma grid lines up to the curve.
    for edge in EDGES:
        ax.plot(
            [edge, edge], [0, phi(edge)],
            color="black", linewidth=0.7, zorder=3,
        )

    # Mean / centre line.
    ax.plot([0, 0], [0, peak], color="black", linewidth=0.9,
            linestyle=(0, (3, 3)), zorder=3)

    # Band percentage labels sitting just above the curve.
    if show_bands:
        for edge, band in zip(EDGES[:-1], BANDS):
            mid = edge + 0.25
            inner = edge if abs(edge) < abs(edge + 0.5) else edge + 0.5
            ax.text(
                mid, phi(inner) + 0.007, f"{band}%",
                ha="center", va="bottom", fontsize=7.5 * scale,
                fontweight="bold", zorder=5,
            )

    # Baseline and ticks.
    ax.axhline(0, color="black", linewidth=1.2, zorder=4)
    ticks = np.arange(-4, 4.5, 0.5) if show_ticks else np.arange(-4, 5, 1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks], fontsize=7.5 * scale)
    if show_ticks:
        ax.text(0.0, -0.030, r"$\mu=0\sigma$", ha="center", fontsize=8 * scale)
    ax.set_xlabel("z-score", fontsize=9 * scale, labelpad=6)

    ax.set_xlim(-4.35, 4.35)
    ax.set_ylim(-0.045, peak + 0.075)
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=4, pad=2)

    ax.set_title(title, fontsize=11 * scale, fontweight="bold", loc="left", pad=8)
    ax.text(
        -4.3, peak + 0.052, statement,
        fontsize=10 * scale, va="top", ha="left", fontweight="bold",
        color="#0b6623",
    )
    ax.text(
        4.3, peak + 0.052, workings,
        fontsize=8.5 * scale, va="top", ha="right", color="#1f4e79",
    )


PARTS = [
    dict(
        title="(a)  \u201cLeft-tailed\u201d   \u2014  z = \u22120.5   (X = 3.675 bushels)",
        shade_from=-4.0,
        shade_to=-0.5,
        statement=r"$P(Z < -0.5) = 30.9\%$",
        workings="0.1 + 0.5 + 1.7 + 4.4 + 9.2 + 15.0 = 30.9%",
        fname="q5a_left_tailed.png",
    ),
    dict(
        title="(b)  \u201cRight-tailed\u201d   \u2014  z = 1.5   (X = 4.575 bushels)",
        shade_from=1.5,
        shade_to=4.0,
        statement=r"$P(Z > 1.5) = 6.7\%$",
        workings="4.4 + 1.7 + 0.5 + 0.1 = 6.7%",
        fname="q5b_right_tailed.png",
    ),
    dict(
        title="(c)  \u201cCentred\u201d   \u2014  z = \u00b10.5   (X = 3.675 & 4.125 bushels)",
        shade_from=-0.5,
        shade_to=0.5,
        statement=r"$P(-0.5 < Z < 0.5) = 38.2\%$",
        workings="19.1 + 19.1 = 38.2%",
        fname="q5c_centred.png",
    ),
    dict(
        title="(d)  \u201cBounded\u201d   \u2014  1.0 < z < 1.5   (X = 4.35 & 4.575 bushels)",
        shade_from=1.0,
        shade_to=1.5,
        statement=r"$P(1 < Z < 1.5) = 9.2\%$",
        workings="93.3% \u2212 84.1% = 9.2%",
        fname="q5d_bounded.png",
    ),
]

# ---------------------------------------------------------------- part (e)
# Two crop yields with z = -1 and z = 1.5.
PARTS_E = [
    dict(
        title="(e)(i)  a harvest yield of z-score < \u22121   "
              "(X = 3.45 bushels)",
        shade_from=-4.0,
        shade_to=-1.0,
        statement=r"$P(Z < -1) = 15.9\%$",
        workings="0.1 + 0.5 + 1.7 + 4.4 + 9.2 = 15.9%",
        fname="q5e_i_below_minus1.png",
    ),
    dict(
        title="(e)(ii)  a harvest yield of z-score > 1.5   "
              "(X = 4.575 bushels)",
        shade_from=1.5,
        shade_to=4.0,
        statement=r"$P(Z > 1.5) = 6.7\%$",
        workings="4.4 + 1.7 + 0.5 + 0.1 = 6.7%",
        fname="q5e_ii_above_1p5.png",
    ),
    dict(
        title="(e)(iii)  a harvest yield with \u22121 < z-score < 1.5   "
              "(X between 3.45 and 4.575 bushels)",
        shade_from=-1.0,
        shade_to=1.5,
        statement=r"$P(-1 < Z < 1.5) = 77.4\%$",
        workings="93.3% \u2212 15.9% = 77.4%",
        fname="q5e_iii_bounded.png",
    ),
]


def main():
    # Individual figures.
    for part in PARTS + PARTS_E:
        fig, ax = plt.subplots(figsize=(9, 3.4))
        draw(ax, part["title"], part["shade_from"], part["shade_to"],
             part["statement"], part["workings"])
        fig.tight_layout()
        fig.savefig(part["fname"], dpi=170, facecolor="white")
        plt.close(fig)
        print(f"wrote {part['fname']}")

    # Combined sheet.
    fig, axes = plt.subplots(4, 1, figsize=(9.5, 13.6))
    for ax, part in zip(axes, PARTS):
        draw(ax, part["title"], part["shade_from"], part["shade_to"],
             part["statement"], part["workings"])
    fig.suptitle(
        "Question 5 \u2014 shading & stating the proportions ("
        "\u00bd\u03c3 refinement of the 68-95-99.7 rule)",
        fontsize=12, fontweight="bold", y=0.997,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig("q5_all_parts.png", dpi=160, facecolor="white")
    plt.close(fig)
    print("wrote q5_all_parts.png")

    # Combined sheet for part (e).
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 10.4))
    for ax, part in zip(axes, PARTS_E):
        draw(ax, part["title"], part["shade_from"], part["shade_to"],
             part["statement"], part["workings"])
    fig.suptitle(
        "Question 5(e) \u2014 two crop yields with z = \u22121 and z = 1.5",
        fontsize=12, fontweight="bold", y=0.997,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig("q5e_all_parts.png", dpi=160, facecolor="white")
    plt.close(fig)
    print("wrote q5e_all_parts.png")

    # -------------------------------------------------------------- PDF build
    A4 = (8.27, 11.69)
    with PdfPages("Question5_shaded_graphs.pdf") as pdf:
        # Page 1 - all four parts on one A4 sheet.
        fig, axes = plt.subplots(4, 1, figsize=A4)
        for ax, part in zip(axes, PARTS):
            draw(ax, part["title"], part["shade_from"], part["shade_to"],
                 part["statement"], part["workings"], compact=True)
        fig.suptitle(
            "Question 5 \u2014 Shade & state the proportion of the distribution\n"
            "(68-95-99.7 rule refined to the nearest \u00bd\u03c3)",
            fontsize=11.5, fontweight="bold", y=0.988,
        )
        fig.tight_layout(rect=[0, 0.01, 1, 0.955])
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)

        # Pages 2-5 - one large diagram per part.
        for part in PARTS:
            fig, ax = plt.subplots(figsize=(A4[1], A4[0] * 0.72))
            draw(ax, part["title"], part["shade_from"], part["shade_to"],
                 part["statement"], part["workings"])
            fig.tight_layout()
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)

        # Final page - worked answers.
        fig = plt.figure(figsize=A4)
        fig.text(0.5, 0.955, "Questions 4 & 5 \u2014 Worked answers",
                 ha="center", fontsize=14, fontweight="bold")

        lines = [
            ("h", "Question 4"),
            ("b", "(a)   Standardising formula:"),
            ("m", r"          $z = \dfrac{X - \mu}{\sigma}$"),
            ("b", r"(b)   Using $\mu = 3.9$ bushels and $\sigma = 0.45$ bushels:"),
            ("t", r"          (i)     $X = 4.125 \Rightarrow z = (4.125-3.9)/0.45 = 0.225/0.45 = +0.5$"),
            ("t", r"          (ii)    $X = 4.35\ \ \Rightarrow z = (4.35-3.9)/0.45 = 0.45/0.45 = +1.0$"),
            ("t", r"          (iii)   $X = 3.675 \Rightarrow z = (3.675-3.9)/0.45 = -0.225/0.45 = -0.5$"),
            ("t", r"          (iv)   $X = 4.575 \Rightarrow z = (4.575-3.9)/0.45 = 0.675/0.45 = +1.5$"),
            ("s", ""),
            ("h", "Question 5"),
            ("b", r"(a)   Left-tailed   \u2014   $z = -0.5$   ($X = 3.675$ bushels)"),
            ("t", "          Bands from the left tail up to $-0.5$:"),
            ("t", "          $0.1 + 0.5 + 1.7 + 4.4 + 9.2 + 15.0$"),
            ("a", r"          $P(Z < -0.5) = 30.9\%$"),
            ("s", ""),
            ("b", r"(b)   Right-tailed   \u2014   $z = 1.5$   ($X = 4.575$ bushels)"),
            ("t", "          Bands from $1.5$ out to the right tail:"),
            ("t", "          $4.4 + 1.7 + 0.5 + 0.1$"),
            ("a", r"          $P(Z > 1.5) = 6.7\%$"),
            ("s", ""),
            ("b", r"(c)   Centred   \u2014   $z = \pm 0.5$   ($X = 3.675$ & $4.125$ bushels)"),
            ("t", r"          The two central bands either side of $\mu$:"),
            ("t", "          $19.1 + 19.1$"),
            ("a", r"          $P(-0.5 < Z < 0.5) = 38.2\%$"),
            ("s", ""),
            ("b", r"(d)   Bounded   \u2014   $1.0 < z < 1.5$   ($X = 4.35$ & $4.575$ bushels)"),
            ("t", "          The single band between the two marks:"),
            ("t", r"          $93.3\% - 84.1\%$"),
            ("a", r"          $P(1 < Z < 1.5) = 9.2\%$"),
            ("s", ""),
            ("h", "Cumulative reference table (area to the left of each \u00bd\u03c3 mark)"),
        ]

        style = {
            "h": dict(fontsize=11.5, fontweight="bold", color="#1f4e79"),
            "b": dict(fontsize=10, fontweight="bold"),
            "m": dict(fontsize=12),
            "t": dict(fontsize=9.5),
            "a": dict(fontsize=11, fontweight="bold", color="#0b6623"),
            "s": dict(fontsize=9.5),
        }
        y = 0.915
        for kind, text in lines:
            if kind == "s":
                y -= 0.011
                continue
            fig.text(0.07, y, text.replace("\\u2014", "\u2014"),
                     ha="left", va="top", **style[kind])
            y -= {"h": 0.0235, "m": 0.040}.get(kind, 0.0205)

        # Reference table.
        marks = [m for m in sorted(CUMULATIVE) if -3.5 <= m <= 3.5]
        y -= 0.006
        col_x = np.linspace(0.09, 0.91, len(marks))
        for xpos, m in zip(col_x, marks):
            fig.text(xpos, y, f"{m:g}", ha="center", fontsize=8,
                     fontweight="bold")
            cum = CUMULATIVE[m]
            label = "\u22480%" if cum == 0 else ("\u2248100%" if cum >= 100
                                                 else f"{cum:g}%")
            fig.text(xpos, y - 0.019, label, ha="center", fontsize=7.5)
        fig.text(0.07, y - 0.048,
                 "Top row: $z$        Bottom row: area to the left, as a percentage",
                 fontsize=8.5, style="italic", color="#555555")
        fig.text(0.07, y - 0.075,
                 "Note: because each band is rounded to 1 d.p., totals may differ "
                 "from calculator values by about 0.1%.",
                 fontsize=8.5, style="italic", color="#555555")
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)

        # ------------------------------------------------------- part (e) pages
        fig, axes = plt.subplots(3, 1, figsize=A4)
        for ax, part in zip(axes, PARTS_E):
            draw(ax, part["title"], part["shade_from"], part["shade_to"],
                 part["statement"], part["workings"], scale=0.78)
        fig.suptitle(
            "Question 5(e) \u2014 Two crop yields with z = \u22121 and z = 1.5",
            fontsize=11.5, fontweight="bold", y=0.985,
        )
        fig.tight_layout(rect=[0, 0.01, 1, 0.955])
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)

        for part in PARTS_E:
            fig, ax = plt.subplots(figsize=(A4[1], A4[0] * 0.72))
            draw(ax, part["title"], part["shade_from"], part["shade_to"],
                 part["statement"], part["workings"])
            fig.tight_layout()
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)

        # Part (e) worked answers.
        fig = plt.figure(figsize=A4)
        fig.text(0.5, 0.955, "Question 5(e) \u2014 Worked answers",
                 ha="center", fontsize=14, fontweight="bold")
        e_lines = [
            ("h", "Given"),
            ("t", r"          Two crop yields with $z_1 = -1$ and $z_2 = 1.5$,"
                  r"  where $\mu = 3.9$ and $\sigma = 0.45$ bushels."),
            ("s", ""),
            ("h", "Probabilities"),
            ("b", r"(i)    A harvest yield with $z < -1$"),
            ("t", "          Bands from the left tail up to $-1$:"),
            ("t", "          $0.1 + 0.5 + 1.7 + 4.4 + 9.2$"),
            ("a", r"          $P(Z < -1) = 15.9\%$"),
            ("s", ""),
            ("b", r"(ii)   A harvest yield with $z > 1.5$"),
            ("t", "          Bands from $1.5$ out to the right tail:"),
            ("t", "          $4.4 + 1.7 + 0.5 + 0.1$"),
            ("a", r"          $P(Z > 1.5) = 6.7\%$"),
            ("s", ""),
            ("b", r"(iii)  A harvest yield with $-1 < z < 1.5$"),
            ("t", "          The bands between the two marks:"),
            ("t", "          $15.0 + 19.1 + 19.1 + 15.0 + 9.2$"),
            ("t", r"          or  $93.3\% - 15.9\%$"),
            ("a", r"          $P(-1 < Z < 1.5) = 77.4\%$"),
            ("s", ""),
            ("t", r"          Check:  $15.9\% + 6.7\% + 77.4\% = 100\%$  "
                  r"\u2014 the three regions tile the whole distribution."),
            ("s", ""),
            ("h", "Actual yields (X-scores)"),
            ("b", r"          Rearranging  $z = \dfrac{X-\mu}{\sigma}$  gives"
                  r"  $X = \mu + z\sigma$"),
            ("s", ""),
            ("t", r"          $z = -1:$    $X = 3.9 + (-1)(0.45) = 3.9 - 0.45$"),
            ("a", r"                          $X = 3.45$ bushels"),
            ("s", ""),
            ("t", r"          $z = 1.5:$   $X = 3.9 + (1.5)(0.45) = 3.9 + 0.675$"),
            ("a", r"                          $X = 4.575$ bushels"),
            ("s", ""),
            ("t", r"          So the two crop yields were $3.45$ bushels "
                  r"(one S.D. below $\mu$)"),
            ("t", r"          and $4.575$ bushels (one and a half S.D. above "
                  r"$\mu$)."),
        ]
        y = 0.905
        for kind, text in e_lines:
            if kind == "s":
                y -= 0.011
                continue
            fig.text(0.07, y, text.replace("\\u2014", "\u2014"),
                     ha="left", va="top", **style[kind])
            y -= {"h": 0.0235, "m": 0.040}.get(kind, 0.0205)
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)

        # ------------------------------------------------- appendix: all pairings
        def appendix_page(heading, subtitle, items):
            n = len(items)
            fig, axes = plt.subplots(n, 1, figsize=A4)
            axes = np.atleast_1d(axes)
            sc = 0.78 if n <= 4 else 0.62
            for ax, it in zip(axes, items):
                draw(ax, it["title"], it["lo"], it["hi"], it["statement"],
                     it["workings"], scale=sc, show_bands=(n <= 4))
            fig.suptitle(f"{heading}\n{subtitle}", fontsize=11.5,
                         fontweight="bold", y=0.988)
            fig.tight_layout(rect=[0, 0.01, 1, 0.945])
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)

        def fmt(z):
            return f"{z:g}".replace("-", "\u2212")

        def pct(v):
            """Always 1 decimal place, matching the worksheet's band labels."""
            return f"{v:.1f}"

        def left_item(z):
            return dict(
                title=f"z = {fmt(z)}   (X = {X4[z]:g} bushels)",
                lo=-4.0, hi=z,
                statement=rf"$P(Z < {z:g}) = {pct(CUMULATIVE[z])}\%$",
                workings=f"sum of bands from \u22123.5 to {fmt(z)}",
            )

        def right_item(z):
            v = round(100 - CUMULATIVE[z], 1)
            return dict(
                title=f"z = {fmt(z)}   (X = {X4[z]:g} bushels)",
                lo=z, hi=4.0,
                statement=rf"$P(Z > {z:g}) = {pct(v)}\%$",
                workings=f"100% \u2212 {pct(CUMULATIVE[z])}% = {pct(v)}%",
            )

        def centred_item(z):
            v = round(CUMULATIVE[z] - CUMULATIVE[-z], 1)
            return dict(
                title=f"z = \u00b1{z:g}",
                lo=-z, hi=z,
                statement=rf"$P({-z:g} < Z < {z:g}) = {pct(v)}\%$",
                workings=f"{pct(CUMULATIVE[z])}% \u2212 {pct(CUMULATIVE[-z])}%"
                         f" = {pct(v)}%",
            )

        def bounded_item(lo, hi):
            v = round(CUMULATIVE[hi] - CUMULATIVE[lo], 1)
            return dict(
                title=f"{fmt(lo)} < z < {fmt(hi)}   "
                      f"(X = {X4[lo]:g} & {X4[hi]:g} bushels)",
                lo=lo, hi=hi,
                statement=rf"$P({lo:g} < Z < {hi:g}) = {pct(v)}\%$",
                workings=f"{pct(CUMULATIVE[hi])}% \u2212 {pct(CUMULATIVE[lo])}%"
                         f" = {pct(v)}%",
            )

        zs = [-0.5, 0.5, 1.0, 1.5]
        pairs = [(a, b) for i, a in enumerate(zs) for b in zs[i + 1:]]

        appendix_page(
            "APPENDIX A \u2014 \u201cLeft-tailed\u201d for every Q4 z-score",
            "The pairing used in the main answer is z = \u22120.5",
            [left_item(z) for z in zs],
        )
        appendix_page(
            "APPENDIX B \u2014 \u201cRight-tailed\u201d for every Q4 z-score",
            "The pairing used in the main answer is z = 1.5",
            [right_item(z) for z in zs],
        )
        appendix_page(
            "APPENDIX C \u2014 \u201cCentred\u201d for every Q4 magnitude",
            "The pairing used in the main answer is z = \u00b10.5",
            [centred_item(z) for z in (0.5, 1.0, 1.5)],
        )
        appendix_page(
            "APPENDIX D \u2014 \u201cBounded\u201d, all 6 pairs of Q4 z-scores (1 of 2)",
            "The pairing used in the main answer is 1 < z < 1.5",
            [bounded_item(a, b) for a, b in pairs[:3]],
        )
        appendix_page(
            "APPENDIX D \u2014 \u201cBounded\u201d, all 6 pairs of Q4 z-scores (2 of 2)",
            "The pairing used in the main answer is 1 < z < 1.5",
            [bounded_item(a, b) for a, b in pairs[3:]],
        )

        # Master lookup page.
        fig = plt.figure(figsize=A4)
        fig.text(0.5, 0.955, "APPENDIX E \u2014 Master table of every option",
                 ha="center", fontsize=14, fontweight="bold")
        fig.text(0.5, 0.928,
                 "Q4 z-scores:  \u22120.5,  +0.5,  +1.0,  +1.5    "
                 "(\u2605 = used in the main answer)",
                 ha="center", fontsize=9.5, style="italic", color="#555555")

        yy = 0.885
        blocks = [
            ("Left-tailed  $P(Z < z)$",
             [(f"z = {fmt(z)}", f"{pct(CUMULATIVE[z])}%", z == -0.5)
              for z in zs]),
            ("Right-tailed  $P(Z > z)$",
             [(f"z = {fmt(z)}", f"{pct(100 - CUMULATIVE[z])}%", z == 1.5)
              for z in zs]),
            ("Centred  $P(-|z| < Z < |z|)$",
             [(f"z = \u00b1{z:g}",
               f"{pct(CUMULATIVE[z] - CUMULATIVE[-z])}%", z == 0.5)
              for z in (0.5, 1.0, 1.5)]),
            ("Bounded  $P(z_1 < Z < z_2)$",
             [(f"{fmt(a)} < z < {fmt(b)}",
               f"{pct(CUMULATIVE[b] - CUMULATIVE[a])}%",
               (a, b) == (1.0, 1.5)) for a, b in pairs]),
        ]
        for heading, rows in blocks:
            fig.text(0.10, yy, heading, fontsize=11, fontweight="bold",
                     color="#1f4e79")
            yy -= 0.030
            for label, value, starred in rows:
                mark = "\u2605  " if starred else "     "
                colour = "#0b6623" if starred else "black"
                weight = "bold" if starred else "normal"
                fig.text(0.13, yy, f"{mark}{label}", fontsize=10,
                         color=colour, fontweight=weight)
                fig.text(0.62, yy, value, fontsize=10, ha="right",
                         color=colour, fontweight=weight)
                yy -= 0.0225
            yy -= 0.016

        fig.text(0.10, yy - 0.01,
                 "All values read from the \u00bd\u03c3 bands printed on the "
                 "worksheet curve, so they carry ~0.1% rounding.",
                 fontsize=8.5, style="italic", color="#555555")
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)

    print("wrote Question5_shaded_graphs.pdf")

    # Cross-check the arithmetic against the band table.
    checks = [
        ("a", band_sum(-3.5, -0.5), 30.9),
        ("b", band_sum(1.5, 3.5), 6.7),
        ("c", band_sum(-0.5, 0.5), 38.2),
        ("d", band_sum(1.0, 1.5), 9.2),
    ]
    print("\nband-sum verification")
    for name, got, expect in checks:
        flag = "OK " if abs(got - expect) < 1e-9 else "BAD"
        print(f"  ({name}) {flag} band sum = {got}%  expected {expect}%")

    print("\ncumulative-difference verification")
    print(f"  (a) cum[-0.5]            = {CUMULATIVE[-0.5]}%")
    print(f"  (b) 100 - cum[1.5]       = {round(100 - CUMULATIVE[1.5], 1)}%")
    print(f"  (c) cum[0.5] - cum[-0.5] = {round(CUMULATIVE[0.5] - CUMULATIVE[-0.5], 1)}%")
    print(f"  (d) cum[1.5] - cum[1.0]  = {round(CUMULATIVE[1.5] - CUMULATIVE[1.0], 1)}%")

    e_checks = [
        ("e i", band_sum(-3.5, -1.0), 15.9),
        ("e ii", band_sum(1.5, 3.5), 6.7),
        ("e iii", band_sum(-1.0, 1.5), 77.4),
    ]
    print("\npart (e) band-sum verification")
    for name, got, expect in e_checks:
        flag = "OK " if abs(got - expect) < 1e-9 else "BAD"
        print(f"  ({name}) {flag} band sum = {got}%  expected {expect}%")
    e_total = round(sum(g for _, g, _ in e_checks), 1)
    print(f"  (e) regions tile the distribution: total = {e_total}% "
          f"{'OK' if abs(e_total - 100.0) < 1e-9 else 'BAD'}")

    print("\npart (e) X-scores  (X = mu + z*sigma = 3.9 + z*0.45)")
    for z in (-1.0, 1.5):
        print(f"  z = {z:+.1f}  ->  X = {3.9 + z * 0.45:.3f} bushels")

    print("\nQ4 z-scores  (z = (X - 3.9) / 0.45)")
    for label, X in [("i", 4.125), ("ii", 4.35), ("iii", 3.675), ("iv", 4.575)]:
        print(f"  ({label}) X = {X:>5} bushels  ->  z = {(X - 3.9) / 0.45:+.1f}")


if __name__ == "__main__":
    main()
