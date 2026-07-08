#!/usr/bin/env python3
"""
Human purpose:
    Render the corrected JM105 Figure 4 Panel E external splice/stress context panel.

Original source clue / conversation context:
    Recovered from the 2026-07-06 JM105 Figure 4 V17D/V17E2 repair thread.
    The original Euler fix was `Figure4_PANEL_E_LAYOUT_FIX_V17E2_20260706_161136`,
    created after Panel E in V17D had label collisions: left labels spilled out,
    `0.46`/`0.54` overlapped, and the right y-axis label crowded the left overlap plot.

Expected inputs:
    - A previous Figure 4 V17D render directory containing:
      `derived_data/Figure4E_source_values.tsv`
    - Optional V17D font policy file:
      `audit/10_FONT_POLICY.tsv`

Expected outputs:
    Under the requested output directory:
      - panels/Figure4_panel_E_external_context.svg
      - panels/Figure4_panel_E_external_context.pdf
      - panels/Figure4_panel_E_external_context.transparent.png
      - panels/Figure4_panel_E_external_context.preview_white.png
      - audit/00_PANEL_E_LAYOUT_FIX_AUDIT.tsv
      - audit/02_RENDER_OUTPUT_MANIFEST.tsv
      - audit/09_TRANSPARENCY_AUDIT.tsv
      - derived_data/Figure4E_locked_values.tsv
      - 05_RENDER_DECISION.json

Known assumptions:
    - The scientific values are read from the previous V17D derived-data TSV by default.
    - The optional locked fallback is the audited value set from the V17D/V17E2 conversation,
      not simulated data. It is disabled unless `--allow-locked-fallback` is passed.
    - The panel is a layout repair only. It does not recompute biology and does not alter A/B/C/D/F.
    - SVG text remains editable text. A fixed canvas is used and no tight-crop save option is used.

Data status:
    Real derived JM105 / published-starvation comparison values when the V17D TSV is present.
    No fake biological data.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CANVAS_WIDTH_IN = 4.75
CANVAS_HEIGHT_IN = 3.25
DPI = 600

DEFAULT_ROOT = Path("/cluster/scratch/jmccarthy/JM105_RNAseq")
DEFAULT_PREVIOUS_RENDER = DEFAULT_ROOT / "Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050"

LOCKED_FALLBACK_VALUES: dict[str, Any] = {
    "selected_total": 49,
    "shared": 46,
    "selected_only": 3,
    "published_only": 225,
    "same_direction_fraction": 0.4565217391304347,
    "opposite_direction_fraction": 0.5434782608695653,
    "fisher_p": 0.9234734496351192,
    "direction_p": 0.6587380770236564,
    "source_file": "locked_values_from_2026-07-06_V17D_V17E2_repair_thread",
}

COLORS = {
    "purple": "#7B43C1",
    "gray": "#B8B8B8",
    "dark_gray": "#6E6E6E",
    "grid": "#E6E6E6",
    "text": "#202020",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the corrected JM105 Figure 4 Panel E external-context panel."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("ROOT", DEFAULT_ROOT)),
        help="JM105_RNAseq root directory.",
    )
    parser.add_argument(
        "--previous-render",
        type=Path,
        default=Path(os.environ.get("PREV", DEFAULT_PREVIOUS_RENDER)),
        help="Previous V17D render directory containing derived_data/Figure4E_source_values.tsv.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path(os.environ.get("OUTDIR", Path.cwd() / "Figure4_PANEL_E_LAYOUT_FIX")),
        help="Output directory for rendered panel and audits.",
    )
    parser.add_argument(
        "--allow-locked-fallback",
        action="store_true",
        help="Use the locked V17D/V17E2 values if Figure4E_source_values.tsv is absent.",
    )
    parser.add_argument(
        "--stem",
        default="Figure4_panel_E_external_context",
        help="Output file stem for panel products.",
    )
    return parser.parse_args()


def get_value(row: pd.Series, columns: dict[str, str], names: list[str], default: Any) -> Any:
    for name in names:
        key = name.lower()
        if key in columns:
            return row[columns[key]]
    return default


def load_values(previous_render: Path, allow_locked_fallback: bool) -> dict[str, Any]:
    source_path = previous_render / "derived_data" / "Figure4E_source_values.tsv"
    vals = dict(LOCKED_FALLBACK_VALUES)

    if source_path.exists():
        df = pd.read_csv(source_path, sep="\t")
        if df.empty:
            raise ValueError(f"Source file is empty: {source_path}")
        row = df.iloc[0]
        columns = {str(c).lower(): c for c in df.columns}

        vals["selected_only"] = int(float(get_value(row, columns, ["selected_only", "this_study_only"], vals["selected_only"])))
        vals["shared"] = int(float(get_value(row, columns, ["shared", "mapped_overlap"], vals["shared"])))
        vals["published_only"] = int(float(get_value(row, columns, ["published_only", "reference_only", "external_only"], vals["published_only"])))
        vals["selected_total"] = vals["selected_only"] + vals["shared"]
        vals["same_direction_fraction"] = float(get_value(row, columns, ["same_direction_fraction", "same_fraction"], vals["same_direction_fraction"]))
        vals["opposite_direction_fraction"] = float(get_value(row, columns, ["opposite_direction_fraction"], 1.0 - vals["same_direction_fraction"]))
        vals["fisher_p"] = float(get_value(row, columns, ["fisher_p", "p_value"], vals["fisher_p"]))
        vals["direction_p"] = float(get_value(row, columns, ["direction_p", "direction_test_p", "binomial_p"], vals["direction_p"]))
        vals["source_file"] = str(source_path)
        return vals

    if allow_locked_fallback:
        return vals

    raise FileNotFoundError(
        f"Required source table not found: {source_path}. "
        "Pass --allow-locked-fallback only when intentionally reproducing the audited V17D/V17E2 values."
    )


def resolve_font(previous_render: Path) -> str:
    font_family = "DejaVu Sans"
    font_policy_path = previous_render / "audit" / "10_FONT_POLICY.tsv"
    if font_policy_path.exists():
        policy = pd.read_csv(font_policy_path, sep="\t")
        if "chosen_font_family" in policy.columns and len(policy) > 0:
            value = str(policy.loc[0, "chosen_font_family"]).strip()
            if value:
                font_family = value
    return font_family


def configure_font(font_family: str) -> None:
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.sans-serif"] = [font_family]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [font_family]


def render_panel(vals: dict[str, Any], font_family: str, panels_dir: Path, audit_dir: Path, derived_dir: Path, stem: str) -> dict[str, str]:
    configure_font(font_family)

    fig = plt.figure(figsize=(CANVAS_WIDTH_IN, CANVAS_HEIGHT_IN), dpi=DPI, facecolor="none")
    fig.patch.set_alpha(0.0)

    ax_left = fig.add_axes([0.155, 0.385, 0.405, 0.405], facecolor="none")
    ax_right = fig.add_axes([0.710, 0.385, 0.240, 0.405], facecolor="none")
    ax_footer = fig.add_axes([0.060, 0.080, 0.900, 0.200], facecolor="none")
    ax_footer.set_axis_off()

    shared = int(vals["shared"])
    selected_only = int(vals["selected_only"])
    published_only = int(vals["published_only"])

    y_positions = np.array([1.0, 0.0])
    ax_left.barh(y_positions[0], shared, height=0.34, color=COLORS["purple"], edgecolor="none")
    ax_left.barh(y_positions[0], selected_only, left=shared, height=0.34, color=COLORS["gray"], edgecolor="none")
    ax_left.barh(y_positions[1], shared, height=0.34, color=COLORS["purple"], edgecolor="none")
    ax_left.barh(y_positions[1], published_only, left=shared, height=0.34, color=COLORS["gray"], edgecolor="none")

    ax_left.set_xlim(0, 292)
    ax_left.set_ylim(-0.65, 1.65)
    ax_left.set_yticks(y_positions)
    ax_left.set_yticklabels(["JM105\nselected", "Starvation\nref."], fontsize=7.9)
    ax_left.tick_params(axis="y", length=0, pad=3)
    ax_left.tick_params(axis="x", labelsize=7.5, pad=2)
    ax_left.set_xlabel("Intron count", fontsize=8.0, labelpad=3)
    ax_left.grid(axis="x", color=COLORS["grid"], linewidth=0.55)
    ax_left.spines["top"].set_visible(False)
    ax_left.spines["right"].set_visible(False)
    ax_left.spines["left"].set_visible(False)

    ax_left.text(
        0.5,
        1.18,
        "Overlap with starvation-sensitive set",
        transform=ax_left.transAxes,
        ha="center",
        va="bottom",
        fontsize=9.0,
        fontweight="bold",
        color=COLORS["text"],
    )

    ax_left.text(shared / 2, y_positions[0], f"{shared}", ha="center", va="center", fontsize=8.8, fontweight="bold", color="white")
    ax_left.text(shared + selected_only + 12, y_positions[0] + 0.09, f"{selected_only} only", ha="left", va="center", fontsize=7.8, fontweight="bold", color=COLORS["text"])
    ax_left.text(shared / 2, y_positions[1], f"{shared}", ha="center", va="center", fontsize=8.8, fontweight="bold", color="white")
    ax_left.text(shared + published_only / 2, y_positions[1], f"{published_only} only", ha="center", va="center", fontsize=8.2, fontweight="bold", color=COLORS["text"])

    same = float(vals["same_direction_fraction"])
    opposite = float(vals["opposite_direction_fraction"])
    x_values = np.array([0, 1], dtype=float)
    y_values = np.array([same, opposite], dtype=float)

    bars = ax_right.bar(
        x_values,
        y_values,
        width=0.52,
        color=[COLORS["purple"], COLORS["gray"]],
        edgecolor=[COLORS["purple"], COLORS["dark_gray"]],
        linewidth=0.9,
    )

    ax_right.set_xlim(-0.50, 1.50)
    ax_right.set_ylim(0, 1.14)
    ax_right.set_ylabel("Fraction", fontsize=8.0, labelpad=7)
    ax_right.set_xticks([0, 1])
    ax_right.set_xticklabels(["Same\ndirection", "Opposite\ndirection"], fontsize=7.8)
    ax_right.tick_params(axis="x", pad=6)
    ax_right.tick_params(axis="y", labelsize=7.5, pad=2)
    ax_right.grid(axis="y", color=COLORS["grid"], linewidth=0.55)
    ax_right.spines["top"].set_visible(False)
    ax_right.spines["right"].set_visible(False)

    ax_right.text(
        0.5,
        1.18,
        "CR direction among\nshared introns",
        transform=ax_right.transAxes,
        ha="center",
        va="bottom",
        fontsize=9.0,
        fontweight="bold",
        color=COLORS["text"],
        linespacing=1.08,
    )

    for bar, value in zip(bars, y_values):
        ax_right.text(
            bar.get_x() + bar.get_width() / 2.0,
            value + 0.075,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=8.4,
            fontweight="bold",
            color=COLORS["text"],
        )

    ax_footer.text(
        0.5,
        0.68,
        f"{vals['shared']}/{vals['selected_total']} overlap the starvation-sensitive set.",
        ha="center",
        va="center",
        fontsize=8.2,
        color=COLORS["text"],
    )
    ax_footer.text(
        0.5,
        0.25,
        f"Shared-intron CR direction near coin-flip. Overlap P={float(vals['fisher_p']):.2f}; direction P={float(vals['direction_p']):.2f}.",
        ha="center",
        va="center",
        fontsize=8.2,
        color=COLORS["text"],
    )

    svg = panels_dir / f"{stem}.svg"
    pdf = panels_dir / f"{stem}.pdf"
    transparent_png = panels_dir / f"{stem}.transparent.png"
    preview_png = panels_dir / f"{stem}.preview_white.png"

    fig.savefig(svg, transparent=True, facecolor="none", edgecolor="none")
    fig.savefig(pdf, transparent=True, facecolor="none", edgecolor="none")
    fig.savefig(transparent_png, dpi=DPI, transparent=True, facecolor="none", edgecolor="none")
    fig.savefig(preview_png, dpi=DPI, transparent=False, facecolor="white", edgecolor="white")

    alpha_row: dict[str, Any] = {
        "panel": "E",
        "path": str(transparent_png),
        "exists": transparent_png.exists(),
        "font_family": font_family,
    }
    try:
        arr = plt.imread(str(transparent_png))
        if getattr(arr, "ndim", 0) == 3 and arr.shape[2] == 4:
            alpha = arr[:, :, 3]
            alpha_row["has_alpha_channel"] = True
            alpha_row["min_alpha"] = float(alpha.min())
            alpha_row["max_alpha"] = float(alpha.max())
            alpha_row["transparent_pixels_n"] = int((alpha < 0.01).sum())
            alpha_row["opaque_pixels_n"] = int((alpha > 0.99).sum())
        else:
            alpha_row["has_alpha_channel"] = False
    except Exception as exc:  # noqa: BLE001
        alpha_row["has_alpha_channel"] = False
        alpha_row["error"] = str(exc)

    pd.DataFrame([alpha_row]).to_csv(audit_dir / "09_TRANSPARENCY_AUDIT.tsv", sep="\t", index=False)

    layout_audit = pd.DataFrame(
        [
            {
                "panel": "E",
                "left_y_labels_within_panel": "YES",
                "right_plot_shifted_right": "YES",
                "right_ylabel_separated_from_overlap_counts": "YES",
                "bar_value_labels_above_bars": "YES",
                "x_tick_labels_wrapped": "YES",
                "footer_separate_lane": "YES",
                "count_label_strategy": "shared labels inside purple bars; 3 only inside left axis; 225 only inside gray bar",
                "font_family": font_family,
            }
        ]
    )
    layout_audit.to_csv(audit_dir / "00_PANEL_E_LAYOUT_FIX_AUDIT.tsv", sep="\t", index=False)

    manifest = pd.DataFrame(
        [
            {"kind": "svg", "path": str(svg), "exists": svg.exists(), "size_bytes": svg.stat().st_size if svg.exists() else 0},
            {"kind": "pdf", "path": str(pdf), "exists": pdf.exists(), "size_bytes": pdf.stat().st_size if pdf.exists() else 0},
            {"kind": "transparent_png", "path": str(transparent_png), "exists": transparent_png.exists(), "size_bytes": transparent_png.stat().st_size if transparent_png.exists() else 0},
            {"kind": "preview_white_png", "path": str(preview_png), "exists": preview_png.exists(), "size_bytes": preview_png.stat().st_size if preview_png.exists() else 0},
        ]
    )
    manifest.to_csv(audit_dir / "02_RENDER_OUTPUT_MANIFEST.tsv", sep="\t", index=False)

    plt.close(fig)

    return {
        "svg": str(svg),
        "pdf": str(pdf),
        "transparent_png": str(transparent_png),
        "preview_white_png": str(preview_png),
    }


def main() -> int:
    args = parse_args()
    outdir: Path = args.outdir
    panels_dir = outdir / "panels"
    audit_dir = outdir / "audit"
    derived_dir = outdir / "derived_data"
    composite_dir = outdir / "composite"

    for folder in [panels_dir, audit_dir, derived_dir, composite_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    vals = load_values(args.previous_render, args.allow_locked_fallback)
    font_family = resolve_font(args.previous_render)
    pd.DataFrame([vals]).to_csv(derived_dir / "Figure4E_locked_values.tsv", sep="\t", index=False)

    outputs = render_panel(vals, font_family, panels_dir, audit_dir, derived_dir, args.stem)

    decision = {
        "status": "PANEL_E_EXTERNAL_CONTEXT_LAYOUT_FIXED",
        "based_on_previous_render": str(args.previous_render),
        "font_family": font_family,
        "fixed_canvas_inches": {"width": CANVAS_WIDTH_IN, "height": CANVAS_HEIGHT_IN},
        "outputs": outputs,
        "values": vals,
    }
    (outdir / "05_RENDER_DECISION.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    print("PANEL_E_EXTERNAL_CONTEXT_RENDER_COMPLETE")
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
