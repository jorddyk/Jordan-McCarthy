"""
paper_style.py — locked visual system for the JM105 aging/CR/Mud1 manuscript.

Bible reference: JM105-FIGURE-BIBLE-v1.0-2026-07-22.
Import this at the top of EVERY panel script. Do not define colours locally.

    from paper_style import *
    set_paper_style()
    CANVAS_IN = PANEL_WD
    fig, ax = plt.subplots(figsize=CANVAS_IN)
    ...
    save_panel_outputs(fig, OUTDIR / "Fig2D", canvas_in=CANVAS_IN)

Design rule
-----------
ONE semantic diverging axis runs through the whole paper:

    WARM  (vermillion) = increased / aged / worse
    GREY               = unchanged / reference / background
    COOL  (blue)       = decreased / restricted / protected

Every variable has ONE assigned hue. When it is not colour-encoded, move it
to marker shape, fill state or facet; never assign it a second hue.

Reference levels are grey: young, 2% glucose, WT MUD1, UPF1+,
intron-present and background introns. Candidate introns have no independent
hue; they retain condition colour and receive a black outline.

Render contract
---------------
Canvas dimensions are explicit and fixed. Tight bounding-box export is forbidden.
Each render emits transparent SVG + PDF + PNG and white-background preview PNG.
SVG text remains editable (`svg.fonttype = "none"`), Arial requested.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import seaborn as sns

BIBLE_VERSION = "JM105-FIGURE-BIBLE-v1.0-2026-07-22"

C = {
    "ref": "#7F7F7F",
    "bg": "#DCDCDC",
    "bg_line": "#BFBFBF",
    "ink": "#1A1A1A",
    "young": "#7F7F7F",
    "old": "#D55E00",
    "glu2": "#7F7F7F",
    "glu05": "#56B4E9",
    "glu01": "#0072B2",
    "MUD1": "#7F7F7F",
    "mud1d": "#CC79A7",
    "UPF1": "#7F7F7F",
    "upf1d": "#009E73",
    "intron": "#7F7F7F",
    "deltai": "#E69F00",
    "up": "#D55E00",
    "down": "#0072B2",
    "stable": "#BFBFBF",
}

PAL_AGE = {"young": C["young"], "old": C["old"]}
PAL_GLUCOSE = {"2%": C["glu2"], "0.5%": C["glu05"], "0.1%": C["glu01"]}
PAL_MUD1 = {"MUD1": C["MUD1"], "mud1D": C["mud1d"]}
PAL_NMD = {"UPF1+": C["UPF1"], "upf1D": C["upf1d"]}
PAL_INTRON = {"intron": C["intron"], "deltai": C["deltai"]}
PAL_DIR = {"up": C["up"], "stable": C["stable"], "down": C["down"]}

ORDER_GLUCOSE = ["2%", "0.5%", "0.1%"]
ORDER_AGE = ["young", "old"]
ORDER_DIR = ["up", "stable", "down"]

CMAP_DIV = LinearSegmentedColormap.from_list(
    "paper_div", [C["down"], "#EDEDED", C["up"]], N=256
)
CMAP_SEQ = LinearSegmentedColormap.from_list(
    "paper_seq", ["#F7F7F7", C["glu01"]], N=256
)

MARKER_NMD = {"UPF1+": "o", "upf1D": "s"}
FILL_NMD = {"UPF1+": "none", "upf1D": "full"}
MARKER_MUD1 = {"MUD1": "o", "mud1D": "^"}

CANDIDATE_KW = dict(edgecolor=C["ink"], linewidth=0.7, alpha=1.0, s=34, zorder=3)
BACKGROUND_KW = dict(color=C["bg"], edgecolor="none", alpha=0.35, s=12, zorder=1)

# Fixed panel canvases in inches. Scripts must choose one explicitly or declare a
# panel-specific tuple; canvas is never inferred from content.
PANEL_W = (2.4, 2.1)
PANEL_WD = (4.9, 2.1)
FULL_W = (7.2, 4.5)


def set_paper_style(font_scale: float = 1.0) -> None:
    """Apply once per script, before any plotting."""
    sns.set_theme(style="ticks", context="paper", font_scale=font_scale)
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.labelsize": 7,
        "axes.titlesize": 7,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 6,
        "legend.frameon": False,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.dpi": 600,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def save_panel_outputs(
    fig: mpl.figure.Figure,
    outstem: str | Path,
    canvas_in: Tuple[float, float],
    dpi: int = 600,
) -> Mapping[str, Path]:
    """Save fixed-dimension transparent SVG/PDF/PNG plus white preview PNG.

    Tight bounding-box export is not used and must not be supplied by callers.
    """
    outstem = Path(outstem)
    outstem.parent.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(float(canvas_in[0]), float(canvas_in[1]), forward=True)

    outputs = {
        "svg": outstem.with_suffix(".svg"),
        "pdf": outstem.with_suffix(".pdf"),
        "png": outstem.with_suffix(".png"),
        "preview": outstem.parent / f"{outstem.name}_preview_white.png",
    }
    fig.savefig(outputs["svg"], format="svg", transparent=True, facecolor="none")
    fig.savefig(outputs["pdf"], format="pdf", transparent=True, facecolor="none")
    fig.savefig(outputs["png"], format="png", dpi=dpi, transparent=True, facecolor="none")
    fig.savefig(outputs["preview"], format="png", dpi=dpi, transparent=False, facecolor="white")
    return outputs


def square_identity(ax, pad: float = 0.03, line: bool = True):
    """Force identical x/y limits and optionally draw y=x."""
    lo = min(ax.get_xlim()[0], ax.get_ylim()[0])
    hi = max(ax.get_xlim()[1], ax.get_ylim()[1])
    span = hi - lo
    if span <= 0:
        span = 1.0
    lo, hi = lo - pad * span, hi + pad * span
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    if line:
        ax.plot([lo, hi], [lo, hi], ls="--", lw=0.6, color=C["bg_line"], zorder=0)
    return ax


def stable_band(ax, halfwidth: float, label: str | None = None):
    """Shade a ± band around y=x that defines unchanged."""
    lo, hi = ax.get_xlim()
    ax.fill_between(
        [lo, hi], [lo - halfwidth, hi - halfwidth], [lo + halfwidth, hi + halfwidth],
        color=C["bg_line"], alpha=0.18, lw=0, zorder=0,
    )
    if label:
        ax.text(0.97, 0.03, label, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=5.5, color=C["ref"])
    return ax


def null_band(ax, centre: float, lo: float, hi: float, orient: str = "h"):
    """Draw the reference interval as a band across the whole axis."""
    if orient == "h":
        ax.axhspan(lo, hi, color=C["bg_line"], alpha=0.22, lw=0, zorder=0)
        ax.axhline(centre, color=C["ref"], lw=0.6, ls="-", zorder=1)
    elif orient == "v":
        ax.axvspan(lo, hi, color=C["bg_line"], alpha=0.22, lw=0, zorder=0)
        ax.axvline(centre, color=C["ref"], lw=0.6, ls="-", zorder=1)
    else:
        raise ValueError("orient must be 'h' or 'v'")
    return ax


def quadrant_counts(ax, x, y, xc: float = 0.0, yc: float = 0.0, highlight: str | None = None):
    """Print n per quadrant and optionally wash the quadrant of interest."""
    x = np.asarray(x)
    y = np.asarray(y)
    ax.axvline(xc, color=C["bg_line"], lw=0.6, zorder=0)
    ax.axhline(yc, color=C["bg_line"], lw=0.6, zorder=0)
    quads = {
        "ur": ((x > xc) & (y > yc), 0.97, 0.97, "right", "top"),
        "ul": ((x < xc) & (y > yc), 0.03, 0.97, "left", "top"),
        "lr": ((x > xc) & (y < yc), 0.97, 0.03, "right", "bottom"),
        "ll": ((x < xc) & (y < yc), 0.03, 0.03, "left", "bottom"),
    }
    for key, (mask, fx, fy, ha, va) in quads.items():
        emph = key == highlight
        ax.text(fx, fy, f"{int(mask.sum())}", transform=ax.transAxes,
                ha=ha, va=va, fontsize=13 if emph else 11,
                color=C["ink"] if emph else C["bg_line"],
                alpha=0.85 if emph else 0.6, zorder=0, fontweight="bold")
    if highlight:
        if highlight not in quads:
            raise ValueError("highlight must be one of: ur, ul, lr, ll")
        xlo, xhi = ax.get_xlim()
        ylo, yhi = ax.get_ylim()
        xs = (xc, xhi) if highlight[1] == "r" else (xlo, xc)
        ys = (yc, yhi) if highlight[0] == "u" else (ylo, yc)
        ax.fill_between(xs, ys[0], ys[1], color=C["glu01"], alpha=0.06, lw=0, zorder=0)
    return ax


def gap_shade(ax, xvals, y_lo, y_hi, color: str | None = None):
    """Shade the vertical gap between two condition lines."""
    ax.fill_between(xvals, y_lo, y_hi, color=color or C["upf1d"], alpha=0.15, lw=0, zorder=0)
    return ax


def log_glucose_positions(levels: Sequence[float] = (2.0, 0.5, 0.1)):
    """Return honest log-spaced positions for 2%, 0.5% and 0.1% glucose."""
    arr = np.asarray(levels, dtype=float)
    if np.any(arr <= 0):
        raise ValueError("Glucose levels must be positive")
    return np.log10(arr), [f"{level:g}%" for level in arr]


def annotate_effect(ax, text: str, xy: Tuple[float, float] = (0.03, 0.97)):
    """Put the effect size in the panel, not the legend."""
    ax.text(xy[0], xy[1], text, transform=ax.transAxes, ha="left", va="top",
            fontsize=6, color=C["ink"])
    return ax


def row_color_strip(df, cols):
    """Build row_colors for sns.clustermap annotation strips."""
    import pandas as pd
    return pd.DataFrame(
        {name: df[name].map(mapping) for name, mapping in cols.items()},
        index=df.index,
    )


LEGEND_NOTE = (
    "Colour is fixed paper-wide: grey = reference level (young, 2% glucose, "
    "WT MUD1, UPF1+, intron present); vermillion = aged/increased; "
    "blue = glucose-restricted/suppressed; purple = mud1D; green = upf1D; "
    "amber = intron-deleted. Candidate introns carry their condition colour "
    "with a black outline."
)

__all__ = [
    "BIBLE_VERSION", "C", "PAL_AGE", "PAL_GLUCOSE", "PAL_MUD1", "PAL_NMD",
    "PAL_INTRON", "PAL_DIR", "ORDER_GLUCOSE", "ORDER_AGE", "ORDER_DIR",
    "CMAP_DIV", "CMAP_SEQ", "MARKER_NMD", "FILL_NMD", "MARKER_MUD1",
    "CANDIDATE_KW", "BACKGROUND_KW", "PANEL_W", "PANEL_WD", "FULL_W",
    "set_paper_style", "save_panel_outputs", "square_identity", "stable_band",
    "null_band", "quadrant_counts", "gap_shade", "log_glucose_positions",
    "annotate_effect", "row_color_strip", "LEGEND_NOTE", "plt", "sns", "np", "mpl",
]
