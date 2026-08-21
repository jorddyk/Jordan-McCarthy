#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from common import MIN_SAMPLE_EE, MIN_TOTAL_EE, PIPELINE_VERSION, bh_fdr, hedges_g

# Definitions carried forward from JM105.
# NMD_hidden = IR(NMD off) - IR(matched NMD on)
# candidate_score = min(aging_effect, CR_suppression)
# The public worm datasets do not contain the full age x DR x NMD x rnp-2 factorial.
# No bbox_inches="tight" is used. Canvas dimensions are fixed constants.

DPI = 300
PANEL_W = 5.4
PANEL_H = 4.1
COMPOSITE_W = 12.0
COMPOSITE_H = 9.0
RNG = np.random.default_rng(105)

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})

COLORS = {
    "gray": "#666666",
    "light_gray": "#bdbdbd",
    "red": "#d9482b",
    "blue": "#2b8cbe",
    "green": "#31a354",
    "purple": "#756bb1",
    "orange": "#e08214",
    "black": "#111111",
}


def read_manifest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    df["array_index"] = pd.to_numeric(df["array_index"], errors="raise").astype(int)
    return df


def load_run_counts(root: Path, manifest: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for row in manifest.itertuples(index=False):
        path = root / "work" / "per_run" / row.dataset_id / f"{row.run}.intron_counts.tsv.gz"
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path, sep="\t")
        df["dataset_id"] = row.dataset_id
        df["run"] = row.run
        df["biological_sample_id"] = row.biological_sample_id
        df["group"] = row.group
        df["strain"] = row.strain
        df["age_day"] = pd.to_numeric(row.age_day, errors="coerce")
        df["nmd_state"] = row.nmd_state
        df["diet_state"] = row.diet_state
        df["perturbation"] = row.perturbation
        df["fraction"] = row.fraction
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def collapse_technical_runs(long_runs: pd.DataFrame) -> pd.DataFrame:
    id_cols = [
        "dataset_id", "biological_sample_id", "group", "strain", "age_day", "nmd_state", "diet_state", "perturbation", "fraction",
        "intron_id", "gene_id", "gene_name", "transcript_id", "chrom", "start0", "end0", "strand", "intron_length",
    ]
    collapsed = long_runs.groupby(id_cols, dropna=False, as_index=False)[["EI", "IE", "EE_total"]].sum()
    unspliced = collapsed["EI"] + collapsed["IE"]
    denominator = unspliced + 2 * collapsed["EE_total"]
    collapsed["JM105_IR"] = np.where(denominator > 0, unspliced / denominator, np.nan)
    collapsed["PEI"] = np.where(
        denominator > 0,
        np.log2((unspliced + 0.5) / (2 * collapsed["EE_total"] + 0.5)),
        np.nan,
    )
    return collapsed


def fixed_universe(dataset_df: pd.DataFrame) -> set[str]:
    sample_count = dataset_df["biological_sample_id"].nunique()
    grouped = dataset_df.groupby("intron_id")
    total_ee = grouped["EE_total"].sum()
    supported_samples = grouped["EE_total"].apply(lambda values: int((values >= MIN_SAMPLE_EE).sum()))
    minimum_supported = max(2, math.ceil(sample_count / 2))
    keep = total_ee.index[(total_ee >= MIN_TOTAL_EE) & (supported_samples >= minimum_supported)]
    return set(keep)


def sample_scores(long_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, set[str]]]:
    rows: list[dict[str, object]] = []
    universes: dict[str, set[str]] = {}
    for dataset_id, dataset_df in long_df.groupby("dataset_id"):
        universe = fixed_universe(dataset_df)
        universes[dataset_id] = universe
        fixed = dataset_df[dataset_df["intron_id"].isin(universe)].copy()
        for sample_id, sample_df in fixed.groupby("biological_sample_id"):
            meta = sample_df.iloc[0]
            values = sample_df["JM105_IR"].to_numpy(dtype=float)
            values = values[np.isfinite(values)]
            rows.append({
                "dataset_id": dataset_id,
                "biological_sample_id": sample_id,
                "group": meta["group"],
                "strain": meta["strain"],
                "age_day": meta["age_day"],
                "nmd_state": meta["nmd_state"],
                "diet_state": meta["diet_state"],
                "perturbation": meta["perturbation"],
                "fraction": meta["fraction"],
                "n_introns_fixed_universe": len(universe),
                "median_JM105_IR": float(np.median(values)) if len(values) else np.nan,
                "mean_JM105_IR": float(np.mean(values)) if len(values) else np.nan,
                "q90_JM105_IR": float(np.quantile(values, 0.90)) if len(values) else np.nan,
                "q95_JM105_IR": float(np.quantile(values, 0.95)) if len(values) else np.nan,
                "fraction_nonzero_JM105_IR": float(np.mean(values > 0)) if len(values) else np.nan,
            })
    return pd.DataFrame(rows), universes


def contrast_event_table(long_df: pd.DataFrame, dataset_id: str, group_a: str, group_b: str, universe: set[str], name: str) -> pd.DataFrame:
    subset = long_df[(long_df["dataset_id"] == dataset_id) & long_df["intron_id"].isin(universe)].copy()
    a_samples = subset[subset["group"] == group_a]["biological_sample_id"].unique().tolist()
    b_samples = subset[subset["group"] == group_b]["biological_sample_id"].unique().tolist()
    pivot = subset.pivot_table(index=["intron_id", "gene_id", "gene_name", "chrom", "start0", "end0", "strand", "intron_length"], columns="biological_sample_id", values="JM105_IR", aggfunc="first")
    rows: list[dict[str, object]] = []
    for idx, values in pivot.iterrows():
        a = values.reindex(a_samples).dropna().to_numpy(dtype=float)
        b = values.reindex(b_samples).dropna().to_numpy(dtype=float)
        if len(a) < 2 or len(b) < 2:
            continue
        test = stats.ttest_ind(b, a, equal_var=False)
        rows.append({
            "contrast": name,
            "dataset_id": dataset_id,
            "intron_id": idx[0],
            "gene_id": idx[1],
            "gene_name": idx[2],
            "chrom": idx[3],
            "start0": idx[4],
            "end0": idx[5],
            "strand": idx[6],
            "intron_length": idx[7],
            "mean_group_a": float(np.mean(a)),
            "mean_group_b": float(np.mean(b)),
            "delta_b_minus_a": float(np.mean(b) - np.mean(a)),
            "hedges_g": hedges_g(a, b),
            "welch_t": float(test.statistic),
            "p_value": float(test.pvalue),
            "n_a": len(a),
            "n_b": len(b),
        })
    result = pd.DataFrame(rows)
    if not result.empty:
        result["fdr_bh"] = bh_fdr(result["p_value"])
    return result


def bootstrap_difference(a: Sequence[float], b: Sequence[float], iterations: int = 10000) -> tuple[float, float, float]:
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    estimate = float(np.mean(y) - np.mean(x))
    if len(x) < 2 or len(y) < 2:
        return estimate, np.nan, np.nan
    draws = np.empty(iterations, dtype=float)
    for i in range(iterations):
        draws[i] = np.mean(RNG.choice(y, size=len(y), replace=True)) - np.mean(RNG.choice(x, size=len(x), replace=True))
    low, high = np.quantile(draws, [0.025, 0.975])
    return estimate, float(low), float(high)


def save_panel(fig: plt.Figure, outdir: Path, name: str) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{name}.svg", transparent=True)
    fig.savefig(outdir / f"{name}.pdf", transparent=True)
    fig.savefig(outdir / f"{name}.png", dpi=DPI, transparent=True)
    fig.savefig(outdir / f"{name}_preview_white.png", dpi=DPI, facecolor="white", transparent=False)
    plt.close(fig)



def panel_primary_dr_nmd(scores: pd.DataFrame, outdir: Path, ax: plt.Axes | None = None) -> pd.DataFrame:
    """Render the prespecified SRP089617 DR × NMD question when metadata supports it.

    If WT + smg-2 is absent, the panel explicitly reports that the full interaction
    is not estimable and shows only the available eat-2 NMD comparison. No missing
    factorial cell is imputed.
    """
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    data = scores[scores["dataset_id"] == "DR_PRIMARY"].copy()
    order = ["rnai_wt_control_day1", "rnai_wt_smg2_day1", "rnai_eat2_control_day1", "rnai_eat2_smg2_day1"]
    labels = {
        "rnai_wt_control_day1": "WT\ncontrol RNAi",
        "rnai_wt_smg2_day1": "WT\nsmg-2 RNAi",
        "rnai_eat2_control_day1": "eat-2\ncontrol RNAi",
        "rnai_eat2_smg2_day1": "eat-2\nsmg-2 RNAi",
    }
    colors = {
        "rnai_wt_control_day1": COLORS["gray"],
        "rnai_wt_smg2_day1": COLORS["red"],
        "rnai_eat2_control_day1": COLORS["blue"],
        "rnai_eat2_smg2_day1": COLORS["purple"],
    }
    present = [group for group in order if group in set(data["group"])]
    summary_rows: list[dict[str, object]] = []
    for x, group in enumerate(present):
        values = data.loc[data["group"] == group, "q90_JM105_IR"].dropna().to_numpy(dtype=float)
        jitter = np.linspace(-0.08, 0.08, len(values)) if len(values) > 1 else np.array([0.0])
        ax.scatter(np.full(len(values), x) + jitter, values, s=32, color=colors[group], edgecolor="white", linewidth=0.5, zorder=3)
        if len(values):
            mean = float(np.mean(values))
            sem = float(stats.sem(values)) if len(values) >= 2 else np.nan
            ax.plot([x - 0.16, x + 0.16], [mean, mean], color=colors[group], linewidth=1.8, zorder=4)
            if np.isfinite(sem):
                ax.errorbar([x], [mean], yerr=[sem], color=colors[group], capsize=4, linewidth=1.1, zorder=4)
            summary_rows.append({"group": group, "n": len(values), "mean_q90_JM105_IR": mean, "sem": sem})
    ax.set_xticks(np.arange(len(present)))
    ax.set_xticklabels([labels[group] for group in present])
    ax.set_ylabel("90th percentile JM105_IR")
    ax.set_title("Dietary restriction × NMD", loc="left", fontweight="bold")
    ax.grid(axis="y", color="#dedede", linewidth=0.6)

    group_values = {group: data.loc[data["group"] == group, "q90_JM105_IR"].dropna().to_numpy(dtype=float) for group in present}
    wt_hidden = np.nan
    eat2_hidden = np.nan
    interaction = np.nan
    if {"rnai_wt_control_day1", "rnai_wt_smg2_day1"}.issubset(group_values):
        wt_hidden = float(np.mean(group_values["rnai_wt_smg2_day1"]) - np.mean(group_values["rnai_wt_control_day1"]))
    if {"rnai_eat2_control_day1", "rnai_eat2_smg2_day1"}.issubset(group_values):
        eat2_hidden = float(np.mean(group_values["rnai_eat2_smg2_day1"]) - np.mean(group_values["rnai_eat2_control_day1"]))
    if np.isfinite(wt_hidden) and np.isfinite(eat2_hidden):
        interaction = eat2_hidden - wt_hidden
        note = f"DR × NMD interaction = {interaction:.3g}"
    elif np.isfinite(eat2_hidden):
        note = f"eat-2 NMD-hidden = {eat2_hidden:.3g}\nWT + smg-2 absent; interaction not estimable"
    else:
        note = "No smg-2 RNA-seq group resolved; interaction not estimable"
    ax.text(0.98, 0.98, note, transform=ax.transAxes, ha="right", va="top", fontsize=8)
    result = pd.DataFrame(summary_rows)
    result["WT_NMD_hidden"] = wt_hidden
    result["eat2_NMD_hidden"] = eat2_hidden
    result["DR_x_NMD_interaction"] = interaction
    if own:
        save_panel(fig, outdir, "A_primary_DR_NMD")
    return result

def panel_a_aging(scores: pd.DataFrame, outdir: Path, ax: plt.Axes | None = None) -> None:
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    data = scores[scores["dataset_id"] == "AGING"].copy()
    for strain, color, marker in [("fem", COLORS["blue"], "o"), ("gem", COLORS["orange"], "s")]:
        sub = data[data["strain"] == strain].sort_values("age_day")
        ax.scatter(sub["age_day"], sub["q90_JM105_IR"], s=28, color=color, marker=marker, edgecolor="white", linewidth=0.5, label=strain)
        grouped = sub.groupby("age_day")["q90_JM105_IR"].mean().reset_index()
        if len(grouped) >= 2:
            slope, intercept = np.polyfit(grouped["age_day"], grouped["q90_JM105_IR"], 1)
            xx = np.linspace(grouped["age_day"].min(), grouped["age_day"].max(), 100)
            ax.plot(xx, intercept + slope * xx, color=color, linewidth=1.5)
    ax.set_title("Adult aging", loc="left", fontweight="bold")
    ax.set_xlabel("Adult day")
    ax.set_ylabel("90th percentile JM105_IR")
    ax.legend(frameon=False, title="Sterile strain")
    ax.grid(axis="y", color="#dedede", linewidth=0.6)
    if own:
        save_panel(fig, outdir, "A_aging_timecourse")


def panel_b_dr(scores: pd.DataFrame, outdir: Path, ax: plt.Axes | None = None) -> pd.DataFrame:
    comparisons = [
        ("DR_PRIMARY", "baseline_wt_day1", "baseline_eat2_day1", "SRP089617\neat-2 − WT"),
        ("DR_REPLICATION", "n2_ev", "eat2_ev", "GSE240821\neat-2 − N2"),
    ]
    rows = []
    for dataset_id, group_a, group_b, label in comparisons:
        a = scores[(scores["dataset_id"] == dataset_id) & (scores["group"] == group_a)]["q90_JM105_IR"].to_numpy(dtype=float)
        b = scores[(scores["dataset_id"] == dataset_id) & (scores["group"] == group_b)]["q90_JM105_IR"].to_numpy(dtype=float)
        estimate, low, high = bootstrap_difference(a, b)
        rows.append({"label": label, "estimate": estimate, "low": low, "high": high, "n_a": len(a), "n_b": len(b)})
    result = pd.DataFrame(rows)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    y = np.arange(len(result))[::-1]
    ax.axvline(0, color=COLORS["black"], linewidth=0.8)
    for yi, row in zip(y, result.itertuples(index=False)):
        ax.plot([row.low, row.high], [yi, yi], color=COLORS["gray"], linewidth=1.5)
        ax.scatter([row.estimate], [yi], color=COLORS["green"], s=46, edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(result["label"])
    ax.set_xlabel("Δ 90th-percentile JM105_IR")
    ax.set_title("Dietary restriction across studies", loc="left", fontweight="bold")
    ax.grid(axis="x", color="#dedede", linewidth=0.6)
    if own:
        save_panel(fig, outdir, "B_DR_replication")
    return result


def panel_c_nmd(long_df: pd.DataFrame, universes: dict[str, set[str]], outdir: Path, ax: plt.Axes | None = None) -> pd.DataFrame:
    dataset = long_df[(long_df["dataset_id"] == "NMD_IIS") & long_df["intron_id"].isin(universes["NMD_IIS"])].copy()
    pivot = dataset.pivot_table(index="intron_id", columns="group", values="JM105_IR", aggfunc="mean")
    needed = ["wt", "smg2", "daf2", "daf2_smg2"]
    pivot = pivot.dropna(subset=needed)
    result = pd.DataFrame({
        "intron_id": pivot.index,
        "NMD_hidden_WT": pivot["smg2"] - pivot["wt"],
        "NMD_hidden_daf2": pivot["daf2_smg2"] - pivot["daf2"],
    }).reset_index(drop=True)
    result["interaction"] = result["NMD_hidden_daf2"] - result["NMD_hidden_WT"]
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    values = [result["NMD_hidden_WT"].to_numpy(), result["NMD_hidden_daf2"].to_numpy()]
    violin = ax.violinplot(values, positions=[0, 1], showmeans=False, showmedians=True, showextrema=False, widths=0.75)
    for body, color in zip(violin["bodies"], [COLORS["gray"], COLORS["purple"]]):
        body.set_facecolor(color)
        body.set_edgecolor("none")
        body.set_alpha(0.65)
    violin["cmedians"].set_color(COLORS["black"])
    ax.axhline(0, color=COLORS["black"], linewidth=0.8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["N2", "daf-2"])
    ax.set_ylabel("NMD_hidden JM105_IR")
    ax.set_title("NMD × reduced IIS", loc="left", fontweight="bold")
    median_interaction = float(np.nanmedian(result["interaction"]))
    ax.text(0.98, 0.98, f"median interaction = {median_interaction:.3g}", transform=ax.transAxes, ha="right", va="top", fontsize=8)
    ax.grid(axis="y", color="#dedede", linewidth=0.6)
    if own:
        save_panel(fig, outdir, "C_NMD_hidden_daf2")
    return result


def panel_d_reversal(long_df: pd.DataFrame, universes: dict[str, set[str]], outdir: Path, ax: plt.Axes | None = None) -> pd.DataFrame:
    dataset = long_df[(long_df["dataset_id"] == "DR_PRIMARY") & long_df["intron_id"].isin(universes["DR_PRIMARY"])].copy()
    pivot = dataset.pivot_table(index="intron_id", columns="group", values="JM105_IR", aggfunc="mean")
    pivot = pivot.dropna(subset=["rnai_wt_control_day3", "rnai_eat2_control_day3", "rnai_eat2_hrpu1_day3"])
    result = pd.DataFrame({
        "intron_id": pivot.index,
        "DR_effect": pivot["rnai_eat2_control_day3"] - pivot["rnai_wt_control_day3"],
        "hrpu1_effect": pivot["rnai_eat2_hrpu1_day3"] - pivot["rnai_eat2_control_day3"],
    }).reset_index(drop=True)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    x = result["DR_effect"].to_numpy(dtype=float)
    y = result["hrpu1_effect"].to_numpy(dtype=float)
    ax.scatter(x, y, s=8, color=COLORS["light_gray"], alpha=0.5, edgecolor="none")
    ax.axhline(0, color=COLORS["black"], linewidth=0.8)
    ax.axvline(0, color=COLORS["black"], linewidth=0.8)
    finite = np.isfinite(x) & np.isfinite(y)
    if finite.sum() >= 3:
        rho, p = stats.spearmanr(x[finite], y[finite])
        slope, intercept = np.polyfit(x[finite], y[finite], 1)
        xx = np.linspace(np.nanquantile(x[finite], 0.01), np.nanquantile(x[finite], 0.99), 100)
        ax.plot(xx, intercept + slope * xx, color=COLORS["blue"], linewidth=1.3)
    else:
        rho, p = np.nan, np.nan
    ax.set_xlabel("eat-2 − WT JM105_IR")
    ax.set_ylabel("eat-2 + hrpu-1 RNAi − eat-2")
    ax.set_title("hrpu-1 dependence", loc="left", fontweight="bold")
    ax.text(0.98, 0.98, f"Spearman ρ = {rho:.2f}\np = {p:.2g}", transform=ax.transAxes, ha="right", va="top", fontsize=8)
    ax.grid(color="#e5e5e5", linewidth=0.5)
    if own:
        save_panel(fig, outdir, "D_hrpu1_reversal")
    return result


def panel_e_direct(long_df: pd.DataFrame, universes: dict[str, set[str]], outdir: Path, ax: plt.Axes | None = None) -> pd.DataFrame:
    dataset = long_df[(long_df["dataset_id"] == "DIRECT_NMD") & long_df["intron_id"].isin(universes["DIRECT_NMD"])].copy()
    pivot = dataset.pivot_table(index=["intron_id", "gene_name"], columns="group", values="JM105_IR", aggfunc="mean")
    needed = ["n2_input", "smg1_input", "smg1_ip", "smg1_smg2_input", "smg1_smg2_ip"]
    pivot = pivot.dropna(subset=needed)
    result = pd.DataFrame({
        "intron_id": [idx[0] for idx in pivot.index],
        "gene_name": [idx[1] for idx in pivot.index],
        "NMD_stabilization": pivot["smg1_input"].to_numpy() - pivot["n2_input"].to_numpy(),
        "SMG2_IP_enrichment": pivot["smg1_ip"].to_numpy() - pivot["smg1_input"].to_numpy(),
        "negative_control_IP": pivot["smg1_smg2_ip"].to_numpy() - pivot["smg1_smg2_input"].to_numpy(),
    })
    result["direct_support"] = (result["NMD_stabilization"] > 0) & (result["SMG2_IP_enrichment"] > result["negative_control_IP"])
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(PANEL_W, PANEL_H), dpi=DPI)
    assert ax is not None
    direct = result["direct_support"].to_numpy(dtype=bool)
    ax.scatter(result.loc[~direct, "NMD_stabilization"], result.loc[~direct, "SMG2_IP_enrichment"], s=8, color=COLORS["light_gray"], alpha=0.5, edgecolor="none")
    ax.scatter(result.loc[direct, "NMD_stabilization"], result.loc[direct, "SMG2_IP_enrichment"], s=12, color=COLORS["red"], alpha=0.75, edgecolor="none")
    ax.axhline(0, color=COLORS["black"], linewidth=0.8)
    ax.axvline(0, color=COLORS["black"], linewidth=0.8)
    ax.set_xlabel("smg-1 input − N2 input")
    ax.set_ylabel("SMG-2 IP − smg-1 input")
    ax.set_title("NMD stabilization and SMG-2 association", loc="left", fontweight="bold")
    ax.text(0.98, 0.98, f"directionally supported introns = {int(direct.sum())}", transform=ax.transAxes, ha="right", va="top", fontsize=8)
    ax.grid(color="#e5e5e5", linewidth=0.5)
    if own:
        save_panel(fig, outdir, "E_direct_SMG2_support")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=None, help="Accepted for Slurm wrapper compatibility; the canonical manifest is read from <root>/work/metadata.")
    args = parser.parse_args()
    root = args.root.resolve()
    results = root / "work" / "results"
    figures = results / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    manifest = read_manifest(root / "work" / "metadata" / "run_manifest.tsv")
    long_runs = load_run_counts(root, manifest)
    long_df = collapse_technical_runs(long_runs)
    scores, universes = sample_scores(long_df)

    long_df.to_csv(results / "all_intron_measurements.tsv.gz", sep="\t", index=False, compression="gzip")
    try:
        long_df.to_parquet(results / "all_intron_measurements.parquet", index=False)
    except ImportError:
        # Parquet is optional; the complete compressed TSV is always written.
        pass
    scores.to_csv(results / "sample_scores.tsv", sep="\t", index=False)
    universe_rows = [{"dataset_id": dataset_id, "n_introns": len(introns)} for dataset_id, introns in sorted(universes.items())]
    pd.DataFrame(universe_rows).to_csv(results / "fixed_universe_summary.tsv", sep="\t", index=False)

    contrast_specs = [
        ("DR_PRIMARY", "baseline_wt_day1", "baseline_eat2_day1", "eat2_vs_WT_baseline_day1"),
        ("DR_PRIMARY", "rnai_eat2_control_day3", "rnai_eat2_hrpu1_day3", "hrpu1_in_eat2_day3"),
        ("NMD_IIS", "wt", "smg2", "NMD_hidden_WT"),
        ("NMD_IIS", "daf2", "daf2_smg2", "NMD_hidden_daf2"),
        ("DIRECT_NMD", "n2_input", "smg1_input", "smg1_vs_N2_input"),
        ("DR_REPLICATION", "n2_ev", "eat2_ev", "eat2_replication"),
        ("DR_REPLICATION", "eat2_ev", "eat2_pha4", "pha4_in_eat2"),
        ("DR_REPLICATION", "eat2_ev", "eat2_daf16", "daf16_in_eat2"),
        ("DR_REPLICATION", "eat2_ev", "eat2_mxl2_ev", "mxl2_in_eat2"),
    ]
    available_groups = set(scores.loc[scores["dataset_id"] == "DR_PRIMARY", "group"])
    if {"rnai_wt_control_day1", "rnai_wt_smg2_day1"}.issubset(available_groups):
        contrast_specs.append(("DR_PRIMARY", "rnai_wt_control_day1", "rnai_wt_smg2_day1", "SRP_NMD_hidden_WT_day1"))
    if {"rnai_eat2_control_day1", "rnai_eat2_smg2_day1"}.issubset(available_groups):
        contrast_specs.append(("DR_PRIMARY", "rnai_eat2_control_day1", "rnai_eat2_smg2_day1", "SRP_NMD_hidden_eat2_day1"))
    contrast_summary_rows = []
    contrast_dir = results / "contrasts"
    contrast_dir.mkdir(exist_ok=True)
    for dataset_id, group_a, group_b, name in contrast_specs:
        table = contrast_event_table(long_df, dataset_id, group_a, group_b, universes[dataset_id], name)
        table.to_csv(contrast_dir / f"{name}.per_intron.tsv.gz", sep="\t", index=False, compression="gzip")
        sa = scores[(scores["dataset_id"] == dataset_id) & (scores["group"] == group_a)]["q90_JM105_IR"].dropna().to_numpy()
        sb = scores[(scores["dataset_id"] == dataset_id) & (scores["group"] == group_b)]["q90_JM105_IR"].dropna().to_numpy()
        if len(sa) >= 2 and len(sb) >= 2:
            test = stats.ttest_ind(sb, sa, equal_var=False)
            p = float(test.pvalue)
        else:
            p = np.nan
        contrast_summary_rows.append({
            "name": name,
            "dataset_id": dataset_id,
            "group_a": group_a,
            "group_b": group_b,
            "n_a": len(sa),
            "n_b": len(sb),
            "delta_q90_b_minus_a": float(np.mean(sb) - np.mean(sa)) if len(sa) and len(sb) else np.nan,
            "welch_p_q90": p,
            "hedges_g_q90": hedges_g(sa, sb),
            "tested_introns": len(table),
            "fdr_lt_0_05": int((table["fdr_bh"] < 0.05).sum()) if not table.empty else 0,
        })
    pd.DataFrame(contrast_summary_rows).to_csv(results / "contrast_summary.tsv", sep="\t", index=False)

    primary_dr_nmd = panel_primary_dr_nmd(scores, figures)
    panel_a_aging(scores, figures)
    dr_effects = panel_b_dr(scores, figures)
    nmd_table = panel_c_nmd(long_df, universes, figures)
    reversal_table = panel_d_reversal(long_df, universes, figures)
    direct_table = panel_e_direct(long_df, universes, figures)
    primary_dr_nmd.to_csv(results / "SRP089617_DR_NMD_sample_summary.tsv", sep="\t", index=False)
    dr_effects.to_csv(results / "DR_sample_effects.tsv", sep="\t", index=False)
    nmd_table.to_csv(results / "NMD_hidden_IIS.tsv.gz", sep="\t", index=False, compression="gzip")
    reversal_table.to_csv(results / "DR_hrpu1_reversal.tsv.gz", sep="\t", index=False, compression="gzip")
    direct_table.to_csv(results / "direct_SMG2_support.tsv.gz", sep="\t", index=False, compression="gzip")

    fig, axes = plt.subplots(2, 3, figsize=(COMPOSITE_W, COMPOSITE_H), dpi=DPI)
    panel_primary_dr_nmd(scores, figures, axes[0, 0])
    panel_e_direct(long_df, universes, figures, axes[0, 1])
    panel_a_aging(scores, figures, axes[0, 2])
    panel_b_dr(scores, figures, axes[1, 0])
    panel_d_reversal(long_df, universes, figures, axes[1, 1])
    panel_c_nmd(long_df, universes, figures, axes[1, 2])
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.95, wspace=0.42, hspace=0.38)
    fig.savefig(figures / "worm_triangulation_composite.svg", transparent=True)
    fig.savefig(figures / "worm_triangulation_composite.pdf", transparent=True)
    fig.savefig(figures / "worm_triangulation_composite.png", dpi=DPI, transparent=True)
    fig.savefig(figures / "worm_triangulation_composite_preview_white.png", dpi=DPI, facecolor="white", transparent=False)
    plt.close(fig)

    contrast_summary = pd.DataFrame(contrast_summary_rows)
    nmd_row = contrast_summary.loc[contrast_summary["name"] == "NMD_hidden_WT"].iloc[0]
    dr_primary_row = contrast_summary.loc[contrast_summary["name"] == "eat2_vs_WT"].iloc[0]
    dr_rep_row = contrast_summary.loc[contrast_summary["name"] == "eat2_replication"].iloc[0]
    nmd_direction = "positive" if nmd_row["delta_q90_b_minus_a"] > 0 else ("negative" if nmd_row["delta_q90_b_minus_a"] < 0 else "null")
    dr_same_direction = bool(np.sign(dr_primary_row["delta_q90_b_minus_a"]) == np.sign(dr_rep_row["delta_q90_b_minus_a"]))
    direct_supported = int(direct_table["direct_support"].sum()) if not direct_table.empty else 0

    report = [
        "# JM105–C. elegans NMD/DR analysis",
        "",
        f"Pipeline version: `{PIPELINE_VERSION}`",
        "",
        "## What was tested",
        "",
        "- Adult-aging bridge: GSE124994.",
        "- Genetic dietary restriction: SRP089617 and GSE240821.",
        "- NMD masking in N2 and daf-2: GSE94077.",
        "- Direct SMG-2 support: GSE100929 input and IP libraries.",
        "",
        "## Result summary",
        "",
        f"- NMD-off minus NMD-on sample-level direction in N2: **{nmd_direction}**.",
        f"- The two eat-2 datasets have the same sample-level direction: **{'yes' if dr_same_direction else 'no'}**.",
        f"- Introns with directional NMD stabilization plus SMG-2 IP support: **{direct_supported}**.",
        "",
        "Sample-level p values are descriptive because several groups are small. Per-intron tables and fixed-universe definitions are retained for review.",
        "",
        "## Claim boundary",
        "",
        "These studies triangulate separate components of JM105. No public worm dataset supplies the full age × dietary restriction × NMD × rnp-2 factorial, and none alone proves cytoplasmic pre-mRNA leakage.",
        "",
        "## Output inventory",
        "",
        "- `all_intron_measurements.tsv.gz` (always)",
        "- `all_intron_measurements.parquet` (when a parquet engine is installed)",
        "- `sample_scores.tsv`",
        "- `contrast_summary.tsv`",
        "- `contrasts/*.per_intron.tsv.gz`",
        "- `NMD_hidden_IIS.tsv.gz`",
        "- `DR_hrpu1_reversal.tsv.gz`",
        "- `direct_SMG2_support.tsv.gz`",
        "- `figures/*.svg`, `*.pdf`, `*.png`",
    ]
    (results / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    verdict = [
        "# Final verdict",
        "",
        "This is a data-driven verdict, not a prespecified positive claim.",
        "",
        f"- NMD masking direction in N2: **{nmd_direction}**.",
        f"- Independent eat-2 direction agreement: **{'yes' if dr_same_direction else 'no'}**.",
        f"- Directionally SMG-2-supported introns: **{direct_supported}**.",
        "- Full DR × NMD factorial available: **no** unless the manifest audit explicitly resolved both WT and eat-2 NMD perturbation cells in SRP089617.",
        "- Cytoplasmic pre-mRNA leakage established: **no**.",
        "",
        "The strongest manuscript claim must be chosen only after examining the effect sizes, confidence intervals, event-level FDR results and sensitivity outputs.",
    ]
    (results / "FINAL_VERDICT.md").write_text("\n".join(verdict) + "\n", encoding="utf-8")

    methods = [
        "# JM105 method port to C. elegans",
        "",
        "Reference: Ensembl release 113, WBcel235. One representative protein-coding transcript per gene was selected by longest CDS, then exonic length and genomic span.",
        "",
        "EI and IE count unique query names whose contiguous aligned block spans the corresponding intron boundary by at least 8 aligned bases on each side. EE_total counts unique query names with an exact CIGAR-N match to the annotated intron. Unmapped, secondary and supplementary alignments are excluded; primary multimapping alignments are not explicitly removed.",
        "",
        "JM105_IR = (EI + IE) / ((EI + IE) + 2 × EE_total). NMD_hidden = IR(NMD off) − IR(matched NMD on). A coverage-defined fixed intron universe is defined separately for each study before contrasts are evaluated.",
        "",
        "The studies are not pooled across library protocols. Technical runs sharing one biological sample identifier are summed before computing IR; biological replicates remain separate.",
    ]
    (results / "METHODS_JM105_TO_WORM.md").write_text("\n".join(methods) + "\n", encoding="utf-8")

    claims = [
        "# Claim boundaries",
        "",
        "- eat-2 is genetic dietary restriction.",
        "- daf-2 is reduced insulin/IGF signaling, not caloric restriction.",
        "- NMD_hidden is reported only for matched NMD-on/off groups within one study.",
        "- SMG-2 IP plus input stabilization supports direct association, not export or translation.",
        "- GSE124994 is an independent aging bridge, not an age × DR × NMD factorial.",
        "- No public dataset in this package tests rnp-2/Mud1 dependence.",
    ]
    (results / "CLAIM_BOUNDARIES.md").write_text("\n".join(claims) + "\n", encoding="utf-8")

    figure_rows = [
        {"panel": "A", "file_stem": "A_primary_DR_NMD", "dataset": "SRP089617", "question": "Is an eat-2 dietary-restriction × NMD interaction estimable, and what is its direction?"},
        {"panel": "B", "file_stem": "E_direct_SMG2_support", "dataset": "GSE100929", "question": "Which NMD-stabilized introns also show SMG-2 association?"},
        {"panel": "C", "file_stem": "A_aging_timecourse", "dataset": "GSE124994", "question": "Does the upper tail of retained-intron exposure change across adult age?"},
        {"panel": "D", "file_stem": "B_DR_replication", "dataset": "SRP089617;GSE240821", "question": "Do independent eat-2 datasets shift retained-intron exposure in the same direction?"},
        {"panel": "E", "file_stem": "D_hrpu1_reversal", "dataset": "SRP089617", "question": "Does hrpu-1 perturbation oppose the eat-2 intron program?"},
        {"panel": "F", "file_stem": "C_NMD_hidden_daf2", "dataset": "GSE94077", "question": "What does NMD loss reveal in N2 and reduced-IIS worms?"},
        {"panel": "composite", "file_stem": "worm_triangulation_composite", "dataset": "all", "question": "Contact sheet; separate studies are not presented as one factorial."},
    ]
    pd.DataFrame(figure_rows).to_csv(results / "FIGURE_MANIFEST.tsv", sep="\t", index=False)

    audit = [
        "# Figure lane and collision audit",
        "",
        "## Lanes",
        "",
        "- Descriptor/title: one short question-level title above each independent panel.",
        "- Plot: data marks, zero lines and fitted trends only.",
        "- Label: one compact statistic in the upper-right where applicable.",
        "- Legend: Panel A only; sterile-strain identity. All other panels use direct axis labels.",
        "- X-tick: group or adult-day labels directly below each plot.",
        "- Group label: encoded in tick labels; no second group-label row is used.",
        "- Right-stat: empty; no text wall is placed beside a plot.",
        "- Footer: interpretation boundaries appear in the contact-sheet text cell and in CLAIM_BOUNDARIES.md.",
        "",
        "## Collision inventory",
        "",
        "- Panel A legend × data: legend is compact; exact rendered overlap must be inspected in the white preview.",
        "- Panel B confidence intervals × point estimates: point is layered above interval.",
        "- Panel C statistic × violin: statistic is anchored in axes coordinates; exact rendered overlap must be inspected.",
        "- Panel D statistic × point cloud: statistic is anchored in axes coordinates; exact rendered overlap must be inspected.",
        "- Panel E statistic × point cloud: statistic is anchored in axes coordinates; exact rendered overlap must be inspected.",
        "- Footer lane × plots: footer is outside individual panels and occupies a separate contact-sheet cell.",
        "- Transparent background × dark viewer: inspect files ending `_preview_white.png` before judging typography.",
    ]
    (results / "FIGURE_AUDIT.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    (results / "AGGREGATION_COMPLETE.json").write_text(json.dumps({"pipeline_version": PIPELINE_VERSION, "samples": int(scores["biological_sample_id"].nunique()), "status": "complete"}, indent=2) + "\n", encoding="utf-8")

    import hashlib
    file_rows = []
    for path in sorted(results.rglob("*")):
        if path.is_file() and path.name != "FILE_SHA256.tsv":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            file_rows.append({"sha256": digest, "relative_path": str(path.relative_to(results))})
    pd.DataFrame(file_rows).to_csv(results / "FILE_SHA256.tsv", sep="\t", index=False)
    print(f"Aggregation and rendering complete: {results}")


if __name__ == "__main__":
    main()
