#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM105 Figure 4G final visual renderer.

Renders individual introns + median/IQR for RNAlib-predicted structure metrics.
This script expects the metric table from compute_fig4g_rnalib_locked49_metrics.py.

Scope fence:
- Figure 4G uses total/rRNA-depleted JM105-derived Figure 2/4 tables only.
- Poly-A, P-versus-T, mRNA-like, and P−T constructs are out of scope.

Definitions echoed for drift control:
- NMD_hidden = IR(upf1Δ) − IR(UPF1+)
- candidate_score = min(aging_effect, CR_suppression)
- Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression); not used here.

Render contract:
- fixed-dimension transparent SVG/PDF/PNG plus white-background preview PNG;
- editable SVG text via svg.fonttype = "none";
- no tight-crop save option is used.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import mannwhitneyu

CANVAS_WIDTH_PX = 2400
CANVAS_HEIGHT_PX = 1800
DPI = 200
FIG_W_IN = CANVAS_WIDTH_PX / DPI
FIG_H_IN = CANVAS_HEIGHT_PX / DPI

matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "Liberation Sans", "DejaVu Sans"]

OUT_DIR = Path("out")
PANELS_DIR = OUT_DIR / "panels"
AUDIT_DIR = OUT_DIR / "audits"
DATA_DIR = OUT_DIR / "derived_data"
PANEL_STEM = "Figure4G_introns_median_order_label_fix"

COLOR_TEXT = "#14203a"
COLOR_AX = "#4f5968"
COLOR_GUIDE = "#d7dbe3"
COLOR_ZERO = "#9aa3af"
COLOR_BACKGROUND = "#bfc5cd"
COLOR_AGING = "#e28a23"
COLOR_SELECTED = "#8a63b8"

GROUP_ORDER = ["background", "aging_only", "selected"]
GROUP_LABELS = {"background": "Background", "aging_only": "Aging-only", "selected": "Mud1/CR"}
GROUP_COLORS = {"background": COLOR_BACKGROUND, "aging_only": COLOR_AGING, "selected": COLOR_SELECTED}

# Top-to-bottom within each metric row matches legend order.
GROUP_OFFSETS = {"background": 0.20, "aging_only": 0.00, "selected": -0.20}

PLOT_METRICS = [
    ("five_ss_access", "5′SS accessibility", "higher = more accessible"),
    ("bp_access", "Branchpoint accessibility", "higher = more accessible"),
    ("three_ss_access", "3′SS accessibility", "higher = more accessible"),
    ("occlusion_score", "Splice-signal occlusion", "higher = more occluded"),
    ("folding_strength_per_nt", "Folding strength per nt", "-MFE per nt; higher = stronger predicted folding"),
]
CONTRASTS = [("A/bg", "aging_only", "background"), ("M/A", "selected", "aging_only")]
RNG = np.random.default_rng(20260713)


def ensure_dirs() -> None:
    for path in [OUT_DIR, PANELS_DIR, AUDIT_DIR, DATA_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_tsv(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def locate_metric_table() -> Path:
    env_path = os.environ.get("FIG4G_METRIC_TABLE", "").strip()
    if env_path and Path(env_path).exists():
        return Path(env_path)

    source_run_dir = os.environ.get("SOURCE_RUN_DIR", "").strip()
    candidates: List[Path] = []
    if source_run_dir:
        candidates.append(Path(source_run_dir) / "out" / "derived_data" / "Figure4G_locked49_RNAlib_structure_metric_table.tsv")

    candidates.append(DATA_DIR / "Figure4G_locked49_RNAlib_structure_metric_table.tsv")

    home = Path("/cluster/home/jmccarthy")
    if home.exists():
        candidates.extend(
            sorted(
                home.glob("JM105_Figure4G_locked49_extract_sequence_*/out/derived_data/Figure4G_locked49_RNAlib_structure_metric_table.tsv"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        )
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Could not find Figure4G_locked49_RNAlib_structure_metric_table.tsv. Searched: " + json.dumps([str(p) for p in candidates], indent=2))


def bh_adjust(pvals: List[float]) -> List[float]:
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adjusted_ranked = np.empty(n, dtype=float)
    running = 1.0
    for idx in range(n - 1, -1, -1):
        running = min(running, ranked[idx] * n / (idx + 1))
        adjusted_ranked[idx] = min(running, 1.0)
    adjusted = np.empty(n, dtype=float)
    adjusted[order] = adjusted_ranked
    return adjusted.tolist()


def sig_label(q: float) -> str:
    if not math.isfinite(float(q)):
        return "na"
    if q < 0.001:
        return "***"
    if q < 0.01:
        return "**"
    if q < 0.05:
        return "*"
    return "ns"


def rank_biserial(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if len(x) == 0 or len(y) == 0:
        return float("nan"), float("nan"), float("nan")
    result = mannwhitneyu(x, y, alternative="two-sided")
    u = float(result.statistic)
    p = float(result.pvalue)
    effect = (2.0 * u / (len(x) * len(y))) - 1.0
    return effect, p, u


def add_percentile_columns(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "mfe_per_nt" not in data.columns:
        raise RuntimeError("Metric table lacks mfe_per_nt.")
    data["folding_strength_per_nt"] = -pd.to_numeric(data["mfe_per_nt"], errors="coerce")
    for metric_key, _metric_label, _direction in PLOT_METRICS:
        values = pd.to_numeric(data[metric_key], errors="coerce")
        ranks = values.rank(method="average", na_option="keep")
        finite_n = int(values.notna().sum())
        if finite_n <= 1:
            data[f"{metric_key}_percentile"] = np.nan
        else:
            data[f"{metric_key}_percentile"] = ((ranks - 1.0) / (finite_n - 1.0)) * 100.0
    return data


def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for contrast_label, group_1, group_2 in CONTRASTS:
        for metric_key, metric_label, direction_note in PLOT_METRICS:
            plot_key = f"{metric_key}_percentile"
            x = pd.to_numeric(df.loc[df["group"] == group_1, plot_key], errors="coerce").to_numpy()
            y = pd.to_numeric(df.loc[df["group"] == group_2, plot_key], errors="coerce").to_numpy()
            raw_x = pd.to_numeric(df.loc[df["group"] == group_1, metric_key], errors="coerce").to_numpy()
            raw_y = pd.to_numeric(df.loc[df["group"] == group_2, metric_key], errors="coerce").to_numpy()
            effect, p_value, u_stat = rank_biserial(x, y)
            rows.append({
                "contrast_label": contrast_label,
                "group_1": group_1,
                "group_2": group_2,
                "metric_key": metric_key,
                "metric_label": metric_label,
                "direction_note": direction_note,
                "n_group_1": int(np.isfinite(x).sum()),
                "n_group_2": int(np.isfinite(y).sum()),
                "median_percentile_group_1": float(np.nanmedian(x)),
                "median_percentile_group_2": float(np.nanmedian(y)),
                "median_raw_group_1": float(np.nanmedian(raw_x)),
                "median_raw_group_2": float(np.nanmedian(raw_y)),
                "rank_biserial_effect_size": effect,
                "mannwhitney_u": u_stat,
                "p_value": p_value,
            })
    stats = pd.DataFrame(rows)
    stats["q_value"] = bh_adjust(stats["p_value"].tolist())
    stats["sig_label"] = stats["q_value"].map(sig_label)
    return stats


def render_panel(df: pd.DataFrame, stats: pd.DataFrame, metric_table_path: Path) -> Dict[str, str]:
    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    fig.patch.set_alpha(0.0)

    fig.text(0.040, 0.948, "G", ha="left", va="top", fontsize=33, fontweight="bold", color=COLOR_TEXT)
    fig.text(0.510, 0.940, "Predicted splice-signal accessibility", ha="center", va="center", fontsize=28, fontweight="bold", color=COLOR_TEXT)

    legend_ax = fig.add_axes([0.255, 0.820, 0.600, 0.070])
    legend_ax.axis("off")
    handles = []
    for group in GROUP_ORDER:
        n = int((df["group"] == group).sum())
        handles.append(Line2D([0], [0], marker="o", linestyle="none", markersize=8, markerfacecolor=GROUP_COLORS[group], markeredgecolor=COLOR_AX, alpha=0.85, label=f"{GROUP_LABELS[group]} n={n}"))
    legend_ax.legend(handles=handles, loc="center", ncol=3, frameon=False, fontsize=14, handletextpad=0.45, columnspacing=1.5)

    label_x = 0.245
    ax = fig.add_axes([0.265, 0.195, 0.555, 0.600])
    stat_ax = fig.add_axes([0.845, 0.195, 0.105, 0.600], sharey=ax)
    stat_ax.axis("off")

    y_positions = np.arange(len(PLOT_METRICS))[::-1]
    y_lookup = {metric_key: y_positions[index] for index, (metric_key, _metric_label, _direction) in enumerate(PLOT_METRICS)}

    for y in y_positions:
        ax.hlines(y, 0, 100, color=COLOR_GUIDE, linewidth=0.85, zorder=0)
    ax.axvline(50.0, color=COLOR_ZERO, linewidth=1.15, zorder=1)

    point_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for metric_key, metric_label, direction_note in PLOT_METRICS:
        plot_key = f"{metric_key}_percentile"
        center_y = y_lookup[metric_key]
        _x_display, y_display = ax.transData.transform((0, center_y))
        fig_y = fig.transFigure.inverted().transform((0, y_display))[1]
        fig.text(label_x, fig_y, metric_label, ha="right", va="center", fontsize=15, color=COLOR_TEXT)

        for group in GROUP_ORDER:
            values = pd.to_numeric(df.loc[df["group"] == group, plot_key], errors="coerce").dropna().to_numpy()
            raw_values = pd.to_numeric(df.loc[df["group"] == group, metric_key], errors="coerce").dropna().to_numpy()
            y_base = center_y + GROUP_OFFSETS[group]
            if len(values) == 0:
                continue
            jitter = RNG.normal(loc=0.0, scale=0.024, size=len(values))
            point_y = y_base + jitter
            ax.scatter(values, point_y, s=17 if group == "background" else 22, color=GROUP_COLORS[group], alpha=0.24 if group == "background" else 0.36, edgecolor="none", zorder=2)

            q25 = float(np.nanpercentile(values, 25))
            med = float(np.nanmedian(values))
            q75 = float(np.nanpercentile(values, 75))
            raw_med = float(np.nanmedian(raw_values))
            ax.plot([q25, q75], [y_base, y_base], color=GROUP_COLORS[group], linewidth=2.0, alpha=0.95, solid_capstyle="round", zorder=4)
            ax.scatter([med], [y_base], s=92, color=GROUP_COLORS[group], edgecolor=COLOR_AX, linewidth=1.15, alpha=1.0, zorder=5)
            summary_rows.append({"metric_key": metric_key, "metric_label": metric_label, "group": group, "n": len(values), "percentile_q25": q25, "percentile_median": med, "percentile_q75": q75, "raw_median": raw_med, "direction_note": direction_note, "row_order_within_metric": "1_background_top_2_aging_middle_3_mud1cr_bottom"})
            for i, val in enumerate(values):
                point_rows.append({"metric_key": metric_key, "metric_label": metric_label, "group": group, "plot_percentile": float(val), "plot_y": float(point_y[i])})

    stat_ax.set_ylim(ax.get_ylim())
    stat_ax.text(0.20, y_positions[0] + 0.42, "A/bg", ha="center", va="bottom", fontsize=12, fontweight="bold", color=COLOR_TEXT)
    stat_ax.text(0.72, y_positions[0] + 0.42, "M/A", ha="center", va="bottom", fontsize=12, fontweight="bold", color=COLOR_TEXT)
    for metric_key, _metric_label, _direction in PLOT_METRICS:
        y = y_lookup[metric_key]
        row_abg = stats.loc[(stats["contrast_label"] == "A/bg") & (stats["metric_key"] == metric_key)]
        row_ma = stats.loc[(stats["contrast_label"] == "M/A") & (stats["metric_key"] == metric_key)]
        stat_ax.text(0.20, y, row_abg["sig_label"].iloc[0] if len(row_abg) else "na", ha="center", va="center", fontsize=13, fontweight="bold", color=COLOR_TEXT)
        stat_ax.text(0.72, y, row_ma["sig_label"].iloc[0] if len(row_ma) else "na", ha="center", va="center", fontsize=13, fontweight="bold", color=COLOR_TEXT)

    ax.set_xlim(-2, 102)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Within-metric percentile", fontsize=16, color=COLOR_TEXT)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(["" for _ in y_positions])
    ax.tick_params(axis="x", labelsize=13, colors=COLOR_TEXT, width=1.1, length=5)
    ax.tick_params(axis="y", length=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_AX)
    ax.spines["bottom"].set_color(COLOR_AX)
    ax.spines["left"].set_linewidth(1.2)
    ax.spines["bottom"].set_linewidth(1.2)

    fig.text(0.500, 0.070, "Small dots = introns; large dots = median; bars = IQR. Raw RNAlib values and exact statistics are exported.", ha="center", va="center", fontsize=11.5, color=COLOR_AX)

    outputs = {
        "svg": str(PANELS_DIR / f"{PANEL_STEM}.svg"),
        "pdf": str(PANELS_DIR / f"{PANEL_STEM}.pdf"),
        "png": str(PANELS_DIR / f"{PANEL_STEM}.png"),
        "white_preview": str(PANELS_DIR / f"{PANEL_STEM}_white_preview.png"),
    }
    fig.savefig(outputs["svg"], transparent=True)
    fig.savefig(outputs["pdf"], transparent=True)
    fig.savefig(outputs["png"], dpi=DPI, transparent=True)
    fig.patch.set_alpha(1.0)
    fig.patch.set_facecolor("white")
    for axis in fig.axes:
        axis.set_facecolor("white")
    fig.savefig(outputs["white_preview"], dpi=DPI, transparent=False)
    plt.close(fig)

    write_tsv(DATA_DIR / "Figure4G_introns_median_order_label_fix_summary.tsv", summary_rows)
    write_tsv(DATA_DIR / "Figure4G_introns_median_order_label_fix_point_positions.tsv", point_rows)
    return outputs


def write_audits(metric_table_path: Path, outputs: Dict[str, str], df: pd.DataFrame, stats: pd.DataFrame) -> None:
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_lane_audit.tsv", [
        {"object": "Panel letter G", "lane": "descriptor/title", "anchor": "upper-left"},
        {"object": "Panel title", "lane": "descriptor/title", "anchor": "top centered"},
        {"object": "Legend", "lane": "legend", "anchor": "dedicated lane below title, order Background > Aging-only > Mud1/CR"},
        {"object": "Metric labels", "lane": "label", "anchor": "dedicated left label lane, right-aligned"},
        {"object": "Individual intron dots", "lane": "plot", "anchor": "main plot lane"},
        {"object": "IQR bars", "lane": "plot", "anchor": "main plot lane"},
        {"object": "Median dots", "lane": "plot", "anchor": "main plot lane"},
        {"object": "Right stats", "lane": "right-stat", "anchor": "separate stat columns"},
        {"object": "Footer", "lane": "footer", "anchor": "bottom centered"},
    ])
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_collision_audit.tsv", [
        {"collision": "left metric labels x canvas edge", "resolution": "labels moved from y-axis tick labels into fixed left label lane"},
        {"collision": "group order x legend order", "resolution": "row offsets changed to Background top, Aging-only middle, Mud1/CR bottom"},
        {"collision": "footer x canvas edge", "resolution": "footer shortened and centered within fixed footer lane"},
        {"collision": "stats x data", "resolution": "stats remain in separate right-stat lane"},
        {"collision": "legend x title", "resolution": "legend remains in its own lane below title"},
        {"collision": "individual dots x median/IQR", "resolution": "small dots semi-transparent; median dots larger/outlined"},
    ])
    png_rows: List[Dict[str, object]] = []
    for kind, path_string in outputs.items():
        path = Path(path_string)
        if path.suffix.lower() == ".png" and path.exists():
            image = Image.open(path)
            png_rows.append({"kind": kind, "path": str(path), "width_px": image.size[0], "height_px": image.size[1], "expected_width_px": CANVAS_WIDTH_PX, "expected_height_px": CANVAS_HEIGHT_PX, "matches_expected": image.size[0] == CANVAS_WIDTH_PX and image.size[1] == CANVAS_HEIGHT_PX})
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_png_size_audit.tsv", png_rows)

    counts = df["group"].value_counts().to_dict()
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_group_count_audit.tsv", [{"group": group, "n": int(counts.get(group, 0)), "visual_order": idx + 1} for idx, group in enumerate(GROUP_ORDER)])
    stats.to_csv(DATA_DIR / "Figure4G_order_label_fix_stats.tsv", sep="\t", index=False)
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_source_manifest.tsv", [
        {"role": "input_metric_table", "path": str(metric_table_path), "notes": "successful locked-49 RNAlib structure metric table"},
        {"role": "panel_svg", "path": outputs["svg"], "notes": "transparent SVG, editable text"},
        {"role": "panel_pdf", "path": outputs["pdf"], "notes": "transparent PDF"},
        {"role": "panel_png", "path": outputs["png"], "notes": "transparent PNG"},
        {"role": "panel_white_preview", "path": outputs["white_preview"], "notes": "white-background preview PNG"},
    ])
    write_tsv(AUDIT_DIR / "Figure4G_order_label_fix_final_self_audit.tsv", [
        {"check": "input table", "finding": f"loaded {len(df)} intron metric rows from {metric_table_path}"},
        {"check": "group counts", "finding": json.dumps(counts, sort_keys=True)},
        {"check": "visual group order", "finding": "within each metric: Background top, Aging-only middle, Mud1/CR bottom"},
        {"check": "left label lane", "finding": "metric labels are fig.text objects in a dedicated left lane, not axis tick labels"},
        {"check": "footer lane", "finding": "footer shortened and centered; no intentional text beyond canvas"},
        {"check": "individual dots", "finding": "all finite intron metric values plotted as small jittered dots"},
        {"check": "summary overlay", "finding": "group medians plotted as large dots; IQR plotted as horizontal bars"},
        {"check": "right-stat lane", "finding": "two comparison-stat columns placed outside data region"},
        {"check": "SVG text", "finding": "svg.fonttype='none'; text remains editable"},
        {"check": "fixed canvas", "finding": "canvas constants used; no tight-crop save option is used"},
        {"check": "exact rendered extents", "finding": "not numerically measured; lane geometry used to avoid known collisions"},
    ])


def main() -> None:
    ensure_dirs()
    metric_table_path = locate_metric_table()
    df = pd.read_csv(metric_table_path, sep="\t")
    required = ["group", "five_ss_access", "bp_access", "three_ss_access", "occlusion_score", "mfe_per_nt"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"Input metric table is missing required columns: {missing}")
    df = add_percentile_columns(df)
    stats = compute_stats(df)
    outputs = render_panel(df, stats, metric_table_path)
    write_audits(metric_table_path, outputs, df, stats)
    summary = {"input_metric_table": str(metric_table_path), "rows": int(len(df)), "group_counts": {k: int(v) for k, v in df["group"].value_counts().to_dict().items()}, "visual_group_order_top_to_bottom": GROUP_ORDER, "outputs": outputs, "canvas_px": [CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX]}
    (OUT_DIR / "Figure4G_order_label_fix_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SUCCESS Figure 4G order/label rerender")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
