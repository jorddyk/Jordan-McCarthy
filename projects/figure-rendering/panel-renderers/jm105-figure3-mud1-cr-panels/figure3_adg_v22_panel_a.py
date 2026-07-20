#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel A: raw JM100 lifespan curves plus graphical Cox estimates."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from figure3_adg_v22_common import (
    BLUE,
    DARK,
    GRAY,
    LIGHT,
    ORANGE,
    PANEL_A_SIZE_MM,
    cross_font_text_audit,
    mm_to_inches,
    save_figure,
)


def normal_two_sided_p(z_value: float) -> float:
    return math.erfc(abs(float(z_value)) / math.sqrt(2.0))


def fit_cox_breslow(times, events, design) -> dict[str, Any]:
    """Fit a small Cox PH model using Newton-Raphson and Breslow ties."""

    time = np.asarray(times, dtype=float)
    event = np.asarray(events, dtype=int)
    x = np.asarray(design, dtype=float)
    if x.ndim == 1:
        x = x[:, None]

    parameter_count = x.shape[1]
    beta = np.zeros(parameter_count, dtype=float)
    event_times = np.sort(np.unique(time[event == 1]))

    def objective(candidate):
        eta = x @ candidate
        shift = float(eta.max())
        weights = np.exp(eta - shift)
        log_likelihood = 0.0
        score = np.zeros(parameter_count, dtype=float)
        information = np.zeros((parameter_count, parameter_count), dtype=float)

        for event_time in event_times:
            deaths = (time == event_time) & (event == 1)
            death_count = int(deaths.sum())
            if death_count == 0:
                continue

            risk = time >= event_time
            x_risk = x[risk]
            weights_risk = weights[risk]
            s0 = float(weights_risk.sum())
            s1 = (weights_risk[:, None] * x_risk).sum(axis=0)
            s2 = np.einsum("i,ij,ik->jk", weights_risk, x_risk, x_risk)
            mean = s1 / s0

            log_likelihood += float((x[deaths] @ candidate).sum())
            log_likelihood -= death_count * (math.log(s0) + shift)
            score += x[deaths].sum(axis=0) - death_count * mean
            information += death_count * (s2 / s0 - np.outer(mean, mean))

        return log_likelihood, score, information

    iteration = 0
    for iteration in range(1, 101):
        log_likelihood, score, information = objective(beta)
        step = np.linalg.solve(
            information + 1e-10 * np.eye(parameter_count),
            score,
        )
        scale = 1.0
        while scale > 1e-8:
            proposed = beta + scale * step
            if objective(proposed)[0] >= log_likelihood:
                beta = proposed
                break
            scale *= 0.5

        if np.max(np.abs(scale * step)) < 1e-10:
            break

    _, _, information = objective(beta)
    covariance = np.linalg.inv(
        information + 1e-10 * np.eye(parameter_count)
    )
    standard_error = np.sqrt(np.diag(covariance))
    z_value = beta / standard_error

    return {
        "beta": beta,
        "standard_error": standard_error,
        "hazard_ratio": np.exp(beta),
        "ci_low": np.exp(beta - 1.96 * standard_error),
        "ci_high": np.exp(beta + 1.96 * standard_error),
        "p_value": np.array([normal_two_sided_p(value) for value in z_value]),
        "iterations": iteration,
    }


def load_jm100_lifespans(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and explicitly normalize the four JM100 lifespan cohorts."""

    raw = pd.read_excel(path, sheet_name="Results")
    raw = raw.rename(columns={column: str(column).strip() for column in raw})
    required = [
        "Strain",
        "Glucose percentage",
        "Cell number global",
        "Buddingcount",
    ]
    missing = [column for column in required if column not in raw.columns]
    if missing:
        raise RuntimeError(f"JM100.xlsx is missing required columns: {missing}")

    working = raw.copy()
    working["excel_row"] = np.arange(2, len(working) + 2)
    working["strain_raw"] = working["Strain"].astype("string").str.strip()
    working["glucose_raw"] = pd.to_numeric(
        working["Glucose percentage"], errors="coerce"
    )
    working["global_cell_id"] = pd.to_numeric(
        working["Cell number global"], errors="coerce"
    )
    working["lifespan"] = pd.to_numeric(
        working["Buddingcount"], errors="coerce"
    )

    def normalize_strain(value):
        if pd.isna(value):
            return None
        text = str(value).strip().lower()
        if text == "wt":
            return "WT"
        if text in {"mud1", "mud1d", "mud1delta", "mud1δ"}:
            return "mud1Δ"
        return None

    def normalize_condition(value):
        if pd.isna(value):
            return None
        numeric = float(value)
        if abs(numeric - 0.02) < 1e-9:
            return "2% glucose"
        if abs(numeric - 0.005) < 1e-9:
            return "0.5% glucose CR"
        return None

    working["strain"] = working["strain_raw"].map(normalize_strain)
    working["condition"] = working["glucose_raw"].map(normalize_condition)

    included_mask = (
        working["strain"].notna()
        & working["condition"].notna()
        & working["global_cell_id"].notna()
        & working["lifespan"].notna()
    )
    columns = [
        "excel_row",
        "global_cell_id",
        "strain",
        "condition",
        "lifespan",
        "strain_raw",
        "glucose_raw",
    ]
    included = working.loc[included_mask, columns].copy()
    excluded = working.loc[~included_mask, columns].copy()

    included["event"] = 1
    included["is_mud1"] = (included["strain"] == "mud1Δ").astype(float)
    included["is_cr"] = (
        included["condition"] == "0.5% glucose CR"
    ).astype(float)
    return included, excluded


def kaplan_meier_curve(times: np.ndarray) -> pd.DataFrame:
    """Return a simple all-events Kaplan-Meier step curve."""

    ordered = np.sort(np.asarray(times, dtype=float))
    survival = 1.0
    rows = [{"time": 0.0, "survival": 1.0}]
    for event_time in np.unique(ordered):
        at_risk = int((ordered >= event_time).sum())
        deaths = int((ordered == event_time).sum())
        survival *= 1.0 - deaths / at_risk
        rows.append(
            {"time": float(event_time), "survival": float(survival)}
        )
    rows.append(
        {"time": float(ordered.max() + 1.0), "survival": float(survival)}
    )
    return pd.DataFrame(rows)


def render_panel_a(workbook: Path, output_root: Path):
    """Render Panel A with independent title, legend, plot, stat and footer lanes."""

    source, excluded = load_jm100_lifespans(workbook)
    groups = {
        "WT 2% glucose": source.query(
            "strain == 'WT' and condition == '2% glucose'"
        ),
        "WT 0.5% glucose CR": source.query(
            "strain == 'WT' and condition == '0.5% glucose CR'"
        ),
        "mud1Δ 2% glucose": source.query(
            "strain == 'mud1Δ' and condition == '2% glucose'"
        ),
        "mud1Δ 0.5% glucose CR": source.query(
            "strain == 'mud1Δ' and condition == '0.5% glucose CR'"
        ),
    }
    empty = [name for name, frame in groups.items() if frame.empty]
    if empty:
        raise RuntimeError(f"Panel A contains empty cohorts: {empty}")

    wt = source[source["strain"] == "WT"]
    mud1 = source[source["strain"] == "mud1Δ"]
    wt_cox = fit_cox_breslow(wt["lifespan"], wt["event"], wt[["is_cr"]])
    mud1_cox = fit_cox_breslow(
        mud1["lifespan"], mud1["event"], mud1[["is_cr"]]
    )
    interaction_design = np.column_stack(
        [
            source["is_mud1"],
            source["is_cr"],
            source["is_mud1"] * source["is_cr"],
        ]
    )
    interaction_cox = fit_cox_breslow(
        source["lifespan"], source["event"], interaction_design
    )

    estimates = pd.DataFrame(
        [
            {
                "row": "WT: CR versus 2%",
                "hazard_ratio": wt_cox["hazard_ratio"][0],
                "ci_low": wt_cox["ci_low"][0],
                "ci_high": wt_cox["ci_high"][0],
                "p_value": wt_cox["p_value"][0],
                "color": BLUE,
            },
            {
                "row": "mud1Δ: CR versus 2%",
                "hazard_ratio": mud1_cox["hazard_ratio"][0],
                "ci_low": mud1_cox["ci_low"][0],
                "ci_high": mud1_cox["ci_high"][0],
                "p_value": mud1_cox["p_value"][0],
                "color": ORANGE,
            },
            {
                "row": "CR × mud1Δ interaction",
                "hazard_ratio": interaction_cox["hazard_ratio"][2],
                "ci_low": interaction_cox["ci_low"][2],
                "ci_high": interaction_cox["ci_high"][2],
                "p_value": interaction_cox["p_value"][2],
                "color": DARK,
            },
        ]
    )

    figure = plt.figure(figsize=(PANEL_A_SIZE_MM[0] / 25.4, PANEL_A_SIZE_MM[1] / 25.4))
    title_axis = figure.add_axes([0.04, 0.915, 0.92, 0.065])
    legend_axis = figure.add_axes([0.055, 0.79, 0.50, 0.095])
    survival_axis = figure.add_axes([0.09, 0.25, 0.47, 0.49])
    stat_title_axis = figure.add_axes([0.62, 0.79, 0.35, 0.065])
    stat_label_axis = figure.add_axes([0.60, 0.33, 0.15, 0.42])
    forest_axis = figure.add_axes([0.75, 0.33, 0.14, 0.42])
    stat_value_axis = figure.add_axes([0.895, 0.33, 0.10, 0.42])
    footer_axis = figure.add_axes([0.05, 0.025, 0.90, 0.10])

    for axis in [
        title_axis,
        legend_axis,
        stat_title_axis,
        stat_label_axis,
        stat_value_axis,
        footer_axis,
    ]:
        axis.axis("off")

    title_axis.text(0.0, 0.5, "A", fontsize=12.0, fontweight="bold", ha="left", va="center")
    title_axis.text(
        0.05,
        0.5,
        "mud1Δ weakens the CR lifespan benefit",
        fontsize=9.2,
        fontweight="bold",
        ha="left",
        va="center",
    )
    stat_title_axis.text(
        0.5,
        0.5,
        "Cox proportional-hazards estimates",
        fontsize=7.8,
        fontweight="bold",
        ha="center",
        va="center",
    )

    curve_styles = [
        ("WT 2% glucose", BLUE, "-", "WT 2%"),
        ("WT 0.5% glucose CR", BLUE, "--", "WT CR"),
        ("mud1Δ 2% glucose", ORANGE, "-", "mud1Δ 2%"),
        ("mud1Δ 0.5% glucose CR", ORANGE, "--", "mud1Δ CR"),
    ]
    handles = []
    maximum_lifespan = 0.0
    for key, color, linestyle, short_label in curve_styles:
        frame = groups[key]
        curve = kaplan_meier_curve(frame["lifespan"].to_numpy(float))
        survival_axis.step(
            curve["time"],
            curve["survival"],
            where="post",
            color=color,
            linestyle=linestyle,
            linewidth=1.45,
        )
        handles.append(
            Line2D(
                [0],
                [0],
                color=color,
                linestyle=linestyle,
                linewidth=1.6,
                label=f"{short_label} (n={len(frame)})",
            )
        )
        maximum_lifespan = max(maximum_lifespan, float(frame["lifespan"].max()))

    legend_axis.legend(
        handles=handles,
        frameon=False,
        loc="center left",
        ncol=2,
        fontsize=6.2,
        handlelength=2.5,
        handletextpad=0.5,
        columnspacing=1.4,
        borderaxespad=0.0,
    )

    x_upper = max(50.0, math.ceil((maximum_lifespan + 1.0) / 10.0) * 10.0)
    survival_axis.set_xlim(0.0, x_upper)
    survival_axis.set_ylim(0.0, 1.03)
    survival_axis.set_xticks(np.arange(0.0, x_upper + 0.1, 10.0))
    survival_axis.set_yticks(np.arange(0.0, 1.01, 0.2))
    survival_axis.set_xlabel("Replicative lifespan (divisions)", fontsize=7.3, labelpad=4)
    survival_axis.set_ylabel("Survival probability", fontsize=7.3, labelpad=6)
    survival_axis.tick_params(labelsize=6.6, width=0.6, length=2.5)
    survival_axis.spines[["top", "right"]].set_visible(False)

    y_positions = [2.5, 1.5, 0.5]
    stat_label_axis.set_xlim(0.0, 1.0)
    stat_label_axis.set_ylim(0.0, 3.0)
    stat_value_axis.set_xlim(0.0, 1.0)
    stat_value_axis.set_ylim(0.0, 3.0)

    for y_position, (_, row) in zip(y_positions, estimates.iterrows()):
        stat_label_axis.text(
            0.98,
            y_position,
            row["row"],
            fontsize=5.9,
            ha="right",
            va="center",
            color=row["color"],
        )
        stat_value_axis.text(
            0.02,
            y_position,
            f"HR {row['hazard_ratio']:.2f}\n[{row['ci_low']:.2f}, {row['ci_high']:.2f}]\np={row['p_value']:.2g}",
            fontsize=5.3,
            ha="left",
            va="center",
            color=row["color"],
            linespacing=1.0,
        )

    forest_lower = min(0.45, float(estimates["ci_low"].min()) * 0.9)
    forest_upper = max(3.1, float(estimates["ci_high"].max()) * 1.06)
    forest_axis.set_xlim(forest_lower, forest_upper)
    forest_axis.set_ylim(0.0, 3.0)
    forest_axis.axvline(1.0, color=LIGHT, linewidth=1.0, zorder=0)
    forest_axis.set_yticks([])
    forest_axis.set_xticks([0.5, 1.0, 2.0, 3.0])
    forest_axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _position: f"{value:g}"))
    forest_axis.tick_params(axis="x", labelsize=6.2, length=2.4)
    forest_axis.spines[["top", "right", "left"]].set_visible(False)
    forest_axis.set_xlabel("Hazard ratio", fontsize=6.5, labelpad=3)

    for y_position, (_, row) in zip(y_positions, estimates.iterrows()):
        forest_axis.plot(
            [row["ci_low"], row["ci_high"]],
            [y_position, y_position],
            color=row["color"],
            linewidth=1.6,
            solid_capstyle="round",
        )
        forest_axis.scatter(
            row["hazard_ratio"],
            y_position,
            s=30,
            color=row["color"],
            edgecolors="white",
            linewidths=0.5,
            zorder=3,
        )

    footer_axis.text(
        0.5,
        0.72,
        "JM100.xlsx / Results; 0.5% glucose CR. All non-missing Buddingcount values are observed lifespans.",
        fontsize=5.4,
        ha="center",
        va="center",
        color=GRAY,
    )
    footer_axis.text(
        0.5,
        0.40,
        "Cox model uses Breslow ties; interaction is the CR hazard-ratio ratio in mud1Δ versus WT.",
        fontsize=5.2,
        ha="center",
        va="center",
        color=GRAY,
    )
    footer_axis.text(
        0.5,
        0.12,
        "HR < 1 indicates lower division hazard under CR.",
        fontsize=5.2,
        ha="center",
        va="center",
        color=GRAY,
    )

    text_audit = cross_font_text_audit(figure, "A")
    if not text_audit["passed"]:
        raise RuntimeError(f"Panel A text audit failed: {text_audit}")

    panel_dir = output_root / "panels" / "A"
    panel_dir.mkdir(parents=True, exist_ok=True)
    source.to_csv(panel_dir / "Figure_3A_panel_source.tsv", sep="\t", index=False)
    excluded.to_csv(panel_dir / "Figure_3A_exclusion_audit.tsv", sep="\t", index=False)
    export_estimates = estimates.drop(columns="color")
    export_estimates.to_csv(
        panel_dir / "Figure_3A_cox_statistics.tsv", sep="\t", index=False
    )
    paths = save_figure(figure, panel_dir, "Figure_3A_lifespan")
    return paths, export_estimates.to_dict(orient="records"), text_audit
