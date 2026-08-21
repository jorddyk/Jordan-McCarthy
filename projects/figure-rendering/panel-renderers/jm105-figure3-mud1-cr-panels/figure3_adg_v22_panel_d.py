#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel D: exact-v21-derived paired JM105 retained-intron responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MaxNLocator

from figure3_adg_v22_common import (
    BLUE,
    DARK,
    FS_AXIS,
    FS_GENE,
    FS_GROUP,
    FS_SUBTITLE,
    FS_TICK,
    FS_TITLE,
    GRAY,
    ORANGE,
    PANEL_D_SIZE_MM,
    cross_font_text_audit,
    mm_to_inches,
    save_figure,
)


def load_preflight_pair_tables(source_dir: Path):
    """Reconstruct the D pairing table from exact recovered v21 plot sources."""

    source = pd.read_csv(source_dir / "Figure_3B_plot_source.tsv", sep="\t")
    nmd_hidden = source[
        ["intron_id", "visible_label", "genotype", "medium", "NMD_hidden"]
    ].drop_duplicates()

    paired_rows = []
    for intron_id, group in nmd_hidden.groupby("intron_id", sort=False):
        pivot = group.pivot(
            index="intron_id",
            columns=["genotype", "medium"],
            values="NMD_hidden",
        )
        plus_mud1_suppression = float(
            pivot[("+MUD1", "2pct")].iloc[0]
            - pivot[("+MUD1", "CR")].iloc[0]
        )
        mud1_delta_suppression = float(
            pivot[("mud1Δ", "2pct")].iloc[0]
            - pivot[("mud1Δ", "CR")].iloc[0]
        )
        paired_rows.append(
            {
                "intron_id": intron_id,
                "visible_label": group["visible_label"].iloc[0],
                "mud1_dependent_CR_suppression": (
                    plus_mud1_suppression - mud1_delta_suppression
                ),
            }
        )
    return nmd_hidden, pd.DataFrame(paired_rows)


def render_panel_d(nmd_hidden, paired_effects, output_root: Path):
    """Render quantitative paired responses with explicit condition markers.

    Proven recovered v21 encoding:
    - open marker = old 2% glucose;
    - filled marker = old 0.1% glucose CR;
    - line = the same intron paired across conditions.

    Horizontal position is measured NMD-hidden IR, not condition identity.
    """

    figure = plt.figure(figsize=mm_to_inches(PANEL_D_SIZE_MM))
    title_axis = figure.add_axes([0.035, 0.91, 0.93, 0.055])
    legend_axis = figure.add_axes([0.25, 0.855, 0.50, 0.05])
    title_axis.axis("off")
    legend_axis.axis("off")

    title_axis.text(
        0.5,
        0.5,
        "Candidate-by-candidate CR responses reveal Mud1 dependence",
        ha="center",
        va="center",
        fontsize=FS_TITLE,
        fontweight="bold",
    )
    legend_axis.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                markerfacecolor="white",
                markeredgecolor=DARK,
                markeredgewidth=0.8,
                markersize=5.2,
                label="old 2% glucose",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="none",
                markerfacecolor=DARK,
                markeredgecolor=DARK,
                markeredgewidth=0.8,
                markersize=5.2,
                label="old 0.1% glucose CR",
            ),
            Line2D(
                [0],
                [0],
                color=GRAY,
                linewidth=0.9,
                label="paired intron",
            ),
        ],
        loc="center",
        frameon=False,
        ncol=3,
        fontsize=FS_SUBTITLE,
        handletextpad=0.5,
        columnspacing=1.6,
        borderaxespad=0.0,
    )

    ordered_introns = (
        paired_effects.sort_values(
            "mud1_dependent_CR_suppression", ascending=False
        )["intron_id"]
        .astype(str)
        .tolist()
    )
    visible_labels = dict(
        zip(
            paired_effects["intron_id"].astype(str),
            paired_effects["visible_label"].astype(str),
        )
    )
    selected = nmd_hidden[
        nmd_hidden["intron_id"].astype(str).isin(ordered_introns)
    ].copy()
    selected["intron_id"] = selected["intron_id"].astype(str)

    positive_values = selected.loc[
        selected["NMD_hidden"] > 0, "NMD_hidden"
    ].to_numpy(float)
    log_values = np.log10(np.maximum(positive_values, 1e-4))
    x_min = float(log_values.min())
    x_max = float(log_values.max())
    padding = 0.08 * (x_max - x_min if x_max > x_min else 1.0)
    x_limits = (x_min - padding, x_max + padding)

    blocks = [
        {
            "label": [0.018, 0.18, 0.17, 0.65],
            "+MUD1": [0.20, 0.18, 0.165, 0.65],
            "mud1Δ": [0.385, 0.18, 0.165, 0.65],
            "scale": [0.20, 0.095, 0.35, 0.05],
            "rank": "ranks 1–25",
        },
        {
            "label": [0.55, 0.18, 0.175, 0.65],
            "+MUD1": [0.735, 0.18, 0.105, 0.65],
            "mud1Δ": [0.86, 0.18, 0.105, 0.65],
            "scale": [0.735, 0.095, 0.23, 0.05],
            "rank": "ranks 26–49",
        },
    ]
    plot_source_rows = []

    for block_index, intron_block in enumerate(
        [ordered_introns[:25], ordered_introns[25:]]
    ):
        row_count = len(intron_block)
        y_position = {
            intron_id: row_count - 1 - index
            for index, intron_id in enumerate(intron_block)
        }
        block = blocks[block_index]

        label_axis = figure.add_axes(block["label"])
        label_axis.set_axis_off()
        label_axis.set_ylim(-0.5, row_count - 0.5)
        label_axis.set_xlim(0.0, 1.0)
        label_axis.text(
            0.98,
            row_count - 0.55,
            block["rank"],
            ha="right",
            va="bottom",
            fontsize=FS_SUBTITLE,
            color=GRAY,
        )
        for intron_id in intron_block:
            label_axis.text(
                0.98,
                y_position[intron_id],
                visible_labels.get(intron_id, ""),
                ha="right",
                va="center",
                fontsize=FS_GENE,
                fontstyle="italic",
            )

        for genotype in ["+MUD1", "mud1Δ"]:
            plot_axis = figure.add_axes(block[genotype])
            color = BLUE if genotype == "+MUD1" else ORANGE

            for intron_id in intron_block:
                values = (
                    selected[
                        (selected["genotype"] == genotype)
                        & (selected["intron_id"] == intron_id)
                    ]
                    .set_index("medium")
                    .reindex(["2pct", "CR"])
                )
                if values["NMD_hidden"].isna().any():
                    continue

                raw_values = values["NMD_hidden"].astype(float).to_numpy()
                plotted_x = np.log10(np.maximum(raw_values, 1e-4))
                row_y = y_position[intron_id]
                plot_axis.plot(
                    plotted_x,
                    [row_y, row_y],
                    color=color,
                    linewidth=0.68,
                    alpha=0.95,
                )
                plot_axis.scatter(
                    plotted_x[0],
                    row_y,
                    s=15,
                    facecolors="white",
                    edgecolors=color,
                    linewidths=0.8,
                    zorder=3,
                )
                plot_axis.scatter(
                    plotted_x[1],
                    row_y,
                    s=15,
                    facecolors=color,
                    edgecolors=color,
                    linewidths=0.8,
                    zorder=3,
                )

                for medium, value, plotted_value in zip(
                    ["2pct", "CR"], raw_values, plotted_x
                ):
                    plot_source_rows.append(
                        {
                            "block": block_index + 1,
                            "intron_id": intron_id,
                            "visible_label": visible_labels.get(intron_id, ""),
                            "genotype": genotype,
                            "medium": medium,
                            "NMD_hidden": value,
                            "log10_NMD_hidden_plotted": plotted_value,
                            "row_y": row_y,
                            "marker_fill": (
                                "open" if medium == "2pct" else "filled"
                            ),
                        }
                    )

            plot_axis.set_ylim(-0.5, row_count - 0.5)
            plot_axis.set_xlim(x_limits)
            plot_axis.set_yticks([])
            plot_axis.set_xticks([])
            plot_axis.spines[
                ["top", "right", "left", "bottom"]
            ].set_visible(False)
            plot_axis.text(
                0.5,
                1.035,
                genotype,
                transform=plot_axis.transAxes,
                ha="center",
                va="bottom",
                fontsize=FS_GROUP,
                color=color,
                fontweight="bold",
                fontstyle="italic" if genotype == "mud1Δ" else "normal",
            )

        scale_axis = figure.add_axes(block["scale"])
        scale_axis.set_xlim(x_limits)
        scale_axis.set_ylim(0.0, 1.0)
        scale_axis.set_yticks([])
        scale_axis.spines[["top", "right", "left"]].set_visible(False)
        scale_axis.spines["bottom"].set_color(DARK)
        scale_axis.xaxis.set_major_locator(MaxNLocator(nbins=4))
        scale_axis.xaxis.set_major_formatter(
            FuncFormatter(lambda value, _position: f"{10**value:.3g}")
        )
        scale_axis.tick_params(
            axis="x", labelsize=FS_TICK, length=2, pad=1.5
        )

    footer_axis = figure.add_axes([0.08, 0.018, 0.84, 0.05])
    footer_axis.axis("off")
    footer_axis.text(
        0.5,
        0.5,
        "NMD-hidden IR; horizontal position is measured value. Open = old 2%; filled = old 0.1% CR.",
        ha="center",
        va="center",
        fontsize=FS_AXIS,
    )

    text_audit = cross_font_text_audit(figure, "D")
    if not text_audit["passed"]:
        raise RuntimeError(
            "Panel D text audit failed:\n" + json.dumps(text_audit, indent=2)
        )

    panel_dir = output_root / "panels" / "D"
    panel_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(plot_source_rows).to_csv(
        panel_dir / "Figure_3D_plot_source.tsv", sep="\t", index=False
    )
    paths = save_figure(
        figure, panel_dir, "Figure_3D_candidate_responses"
    )
    return paths, text_audit
