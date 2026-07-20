#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel G: exact-v21-derived host-RNA abundance control."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator

from figure3_adg_v22_common import (
    BLUE,
    GRAY,
    LIGHT,
    ORANGE,
    PANEL_G_SIZE_MM,
    cross_font_text_audit,
    mm_to_inches,
    save_figure,
)


def render_panel_g(host_changes, output_root: Path):
    """Render all finite host-abundance changes without clipping triangles."""

    figure = plt.figure(figsize=mm_to_inches(PANEL_G_SIZE_MM))
    title_axis = figure.add_axes([0.07, 0.84, 0.86, 0.10])
    title_axis.axis("off")
    title_axis.text(
        0.5,
        0.5,
        "Host RNA abundance does not explain\nthe intron effect",
        ha="center",
        va="center",
        fontsize=9.0,
        fontweight="bold",
        linespacing=1.0,
    )

    plot_axis = figure.add_axes([0.205, 0.29, 0.695, 0.47])
    x_all = host_changes["+MUD1"].to_numpy(float)
    y_all = host_changes["mud1Δ"].to_numpy(float)
    finite = np.isfinite(x_all) & np.isfinite(y_all)
    x_values = x_all[finite]
    y_values = y_all[finite]
    if not len(x_values):
        raise RuntimeError("Panel G contains no finite host-abundance pairs.")

    combined_absolute = np.abs(np.concatenate([x_values, y_values]))
    old_robust_limit = float(np.nanquantile(combined_absolute, 0.96))
    old_robust_limit = max(1.2, min(2.0, old_robust_limit * 1.08))
    formerly_outside = (
        (np.abs(x_values) > old_robust_limit)
        | (np.abs(y_values) > old_robust_limit)
    )
    new_limit = max(1.0, float(np.nanmax(combined_absolute)) * 1.08)

    plot_axis.scatter(
        x_values,
        y_values,
        s=11,
        color=GRAY,
        alpha=0.72,
        edgecolors="none",
    )
    plot_axis.set_xlim(-new_limit, new_limit)
    plot_axis.set_ylim(-new_limit, new_limit)
    plot_axis.set_aspect("equal", adjustable="box")
    plot_axis.plot(
        [-new_limit, new_limit],
        [-new_limit, new_limit],
        linestyle=(0, (4, 3)),
        color=LIGHT,
        linewidth=0.9,
    )
    plot_axis.axvline(0.0, color=LIGHT, linewidth=0.8)
    plot_axis.axhline(0.0, color=LIGHT, linewidth=0.8)
    plot_axis.spines[["top", "right"]].set_visible(False)
    plot_axis.tick_params(labelsize=7.6, pad=1.5)
    plot_axis.xaxis.set_major_locator(MaxNLocator(nbins=5, prune="both"))
    plot_axis.yaxis.set_major_locator(MaxNLocator(nbins=5, prune="both"))
    plot_axis.set_xlabel(
        "Δ host abundance in +MUD1\n(log₂ old CR / old 2%)",
        fontsize=8.4,
        color=BLUE,
        labelpad=2,
    )
    plot_axis.set_ylabel(
        "Δ host abundance in mud1Δ\n(log₂ old CR / old 2%)",
        fontsize=8.4,
        color=ORANGE,
        labelpad=2,
    )

    correlation = float(np.corrcoef(x_values, y_values)[0, 1])
    plot_axis.text(
        0.06,
        0.94,
        f"R = {correlation:.2f}\nn = {len(x_values)} introns\nall finite points shown",
        transform=plot_axis.transAxes,
        ha="left",
        va="top",
        fontsize=7.0,
        bbox={"boxstyle": "round,pad=.15", "fc": "white", "ec": "none"},
    )

    footer_axis = figure.add_axes([0.055, 0.055, 0.89, 0.105])
    footer_axis.axis("off")
    footer_axis.add_patch(
        FancyBboxPatch(
            (0.02, 0.08),
            0.96,
            0.84,
            boxstyle="round,pad=.02",
            facecolor="#F7F7F7",
            edgecolor=LIGHT,
            linewidth=0.8,
            transform=footer_axis.transAxes,
        )
    )
    footer_axis.text(
        0.5,
        0.5,
        "Host-RNA changes are a control; they do not define\nthe Mud1-dependent retained-intron effect.",
        ha="center",
        va="center",
        fontsize=6.0,
        fontstyle="italic",
        linespacing=1.0,
    )

    text_audit = cross_font_text_audit(figure, "G")
    if not text_audit["passed"]:
        raise RuntimeError(
            "Panel G text audit failed:\n" + json.dumps(text_audit, indent=2)
        )

    panel_dir = output_root / "panels" / "G"
    panel_dir.mkdir(parents=True, exist_ok=True)
    host_changes.to_csv(
        panel_dir / "Figure_3G_plot_source.tsv", sep="\t", index=False
    )
    range_audit = {
        "n_total_rows": int(len(host_changes)),
        "n_finite_pairs": int(len(x_values)),
        "x_min": float(x_values.min()),
        "x_max": float(x_values.max()),
        "y_min": float(y_values.min()),
        "y_max": float(y_values.max()),
        "old_robust_limit": old_robust_limit,
        "n_points_outside_old_limit": int(formerly_outside.sum()),
        "new_shared_symmetric_limit": new_limit,
        "points_clipped_in_v22": 0,
    }
    pd.DataFrame([range_audit]).to_csv(
        panel_dir / "Figure_3G_range_audit.tsv", sep="\t", index=False
    )
    paths = save_figure(figure, panel_dir, "Figure_3G_host_abundance")
    return paths, range_audit, text_audit
