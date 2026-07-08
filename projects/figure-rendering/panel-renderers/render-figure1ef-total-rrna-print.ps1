# Human purpose: render JM105 Figure 1E/F content-only panels from real total/rRNA-depleted source tables for manuscript compositing.
# Original source clue / conversation context: recovered from the 2026-06-30 JM105 Figure 1E/F panel-rendering chat after multiple layout repairs; canonicalized from the latest V9 PRINT PowerShell/Python workflow.
# Expected inputs: local copies of JM105_primary53_intron_EI_IE_EE_counts_LONG.csv, JM105_intron_retained_RNA_burden_by_condition.csv, and Figure_1D_AUDIT_provenance.json under Y:\Jordan\JM101 or a descendant folder.
# Expected outputs: transparent SVG/PNG/3x PNG and white-preview PNG for Figure 1E and Figure 1F, plus TSVs and JSON audit/provenance in the output folder.
# Known assumptions: Python is available as python or py -3; pandas/numpy/matplotlib may be installed by pip --user; data columns match the recovered JM105/Intronsaurus schema.
# Data status: uses real JM105 total/rRNA-depleted source tables if present. It does not generate fake biological data. It does not use poly-A data. It distinguishes raw NMD-off retained-intron IR from NMD-hidden off-minus-on; this renderer uses raw +MUD1 NMD-off/upf1D IR profiles for panel E and a precisely audited NMD-off candidate set for panel F.
# Render contract: fixed canvas sizes are declared in Python. This script does not use bbox_inches="tight".

$ErrorActionPreference = "Stop"

$SearchRoot = "Y:\Jordan\JM101"
$OutDir = "Y:\Jordan\JM101\Figure1EF_CONTENTONLY_NATURE_PRINT"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Resolve-InputFile {
    param([string]$FileName)

    $PreferredDirs = @(
        "Y:\Jordan\JM101\Figure1EF_EXACT_RAW_FILES\162_FIG1EF_EXACT_RAW_FILES",
        "Y:\Jordan\JM101\Figure1EF_CONTENTONLY_NATURE_V9_PRINT",
        "Y:\Jordan\JM101\Figure1EF_CONTENTONLY_NATURE_V8_SIXGENE",
        "Y:\Jordan\JM101\Figure1EF_CONTENTONLY_NATURE_V7_SAFE",
        "Y:\Jordan\JM101\Figure1EF_CONTENTONLY_NATURE_V5",
        "Y:\Jordan\JM101\Figure1EF_TOTAL_RRNA_PANELS_CODED",
        "Y:\Jordan\JM101\Figure1EF_RAW_FAST_TARGETED\package\known_good",
        "Y:\Jordan\JM101\Figure1EF_RAW_FAST_TARGETED\package",
        "Y:\Jordan\JM101\Figure1EF_RAW_FAST_TARGETED",
        "Y:\Jordan\JM101"
    )

    foreach ($Dir in $PreferredDirs) {
        $Candidate = Join-Path $Dir $FileName
        if (Test-Path $Candidate) {
            return (Resolve-Path $Candidate).Path
        }
    }

    $Found = Get-ChildItem -Path $SearchRoot -Recurse -Filter $FileName -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($null -eq $Found) {
        throw "Could not find required input file: $FileName under $SearchRoot"
    }

    return $Found.FullName
}

$CountsCsv      = Resolve-InputFile "JM105_primary53_intron_EI_IE_EE_counts_LONG.csv"
$BurdenCsv      = Resolve-InputFile "JM105_intron_retained_RNA_burden_by_condition.csv"
$ProvenanceJson = Resolve-InputFile "Figure_1D_AUDIT_provenance.json"

Write-Host ""
Write-Host "Using input files:"
Write-Host "COUNTS:     $CountsCsv"
Write-Host "BURDEN:     $BurdenCsv"
Write-Host "PROVENANCE: $ProvenanceJson"
Write-Host "OUT:        $OutDir"

$env:COUNTS_CSV = $CountsCsv
$env:BURDEN_CSV = $BurdenCsv
$env:PROV_JSON  = $ProvenanceJson
$env:OUT_DIR    = $OutDir

$PythonCmd = $null
$PythonArgs = @()

try {
    python -c "import sys; print(sys.executable)" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $PythonCmd = "python"
        $PythonArgs = @()
    }
} catch {}

if ($null -eq $PythonCmd) {
    try {
        py -3 -c "import sys; print(sys.executable)" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = "py"
            $PythonArgs = @("-3")
        }
    } catch {}
}

if ($null -eq $PythonCmd) {
    throw "Could not find Python. Run 'python --version' and paste the output."
}

$CheckPy = @'
import sys
import subprocess
required = ["pandas", "numpy", "matplotlib"]
missing = []
for mod in required:
    try:
        __import__(mod)
    except Exception:
        missing.append(mod)
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user"] + missing)
'@

$CheckPath = Join-Path $env:TEMP "check_fig1ef_print_packages.py"
Set-Content -Path $CheckPath -Value $CheckPy -Encoding UTF8

Write-Host ""
Write-Host "Checking Python packages..."
& $PythonCmd @PythonArgs $CheckPath
if ($LASTEXITCODE -ne 0) {
    throw "Python package check/install failed."
}

$Py = @'
from __future__ import annotations

import os
import json
import math
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import ticker

COUNTS_CSV = Path(os.environ["COUNTS_CSV"])
BURDEN_CSV = Path(os.environ["BURDEN_CSV"])
PROV_JSON  = Path(os.environ["PROV_JSON"])
OUT_DIR    = Path(os.environ["OUT_DIR"])
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT = "Arial"
plt.rcParams["font.family"] = FONT
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["axes.linewidth"] = 1.25

BLUE   = "#2F6FAE"
ORANGE = "#E66F2E"
TEXT   = "#111111"
MUTED  = "#40556A"
GRID   = "#D8E2EA"
AXIS   = "#25384A"
HEADER = "#EEF5F9"
BORDER = "#7F93A3"

# Fixed canvas sizes. Do not infer canvas from rendered artists.
FIG1E_CANVAS_IN = (5.35, 6.00)
FIG1F_CANVAS_IN = (5.35, 5.35)
# bbox_inches="tight" is intentionally not used anywhere in this script.


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_glucose(x):
    s = str(x)
    if s in {"CR", "0.1pct", "0.1%", "0.1"}:
        return "CR"
    return s


def norm_mud1(x):
    s = str(x)
    return {
        "WT_MUD1": "MUD1",
        "+MUD1": "MUD1",
        "MUD1": "MUD1",
        "mud1D": "mud1D",
        "mud1Δ": "mud1D",
    }.get(s, s)


def norm_nmd(x):
    s = str(x)
    return {
        "WT_UPF1": "on",
        "UPF1": "on",
        "on": "on",
        "upf1D": "off",
        "upf1Δ": "off",
        "off": "off",
    }.get(s, s)


def bh_adjust(pvals):
    p = np.asarray(list(pvals), dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = ranked * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    out = np.empty(n)
    out[order] = adj
    return out


def hypergeom_right_tail(a: int, bg_n: int, K: int, N: int) -> float:
    lo = max(a, 0)
    hi = min(bg_n, K)
    if lo > hi:
        return 1.0
    log_den = math.lgamma(N + 1) - math.lgamma(K + 1) - math.lgamma(N - K + 1)
    logs = []
    for i in range(lo, hi + 1):
        if K - i > N - bg_n:
            continue
        logs.append(
            math.lgamma(bg_n + 1) - math.lgamma(i + 1) - math.lgamma(bg_n - i + 1)
            + math.lgamma(N - bg_n + 1) - math.lgamma(K - i + 1)
            - math.lgamma(N - bg_n - (K - i) + 1) - log_den
        )
    if not logs:
        return 1.0
    m = max(logs)
    return min(1.0, float(math.exp(m) * sum(math.exp(v - m) for v in logs)))


def short_category_label(s):
    return (
        str(s)
        .replace("Splicing / RNA processing", "Splicing /\nRNA processing")
        .replace("Cell wall / cytoskeleton / polarity", "Cell wall /\ncytoskeleton /\npolarity")
        .replace("Mitochondrial / respiration", "Mitochondrial /\nrespiration")
        .replace("Stress / protein quality", "Stress /\nprotein quality")
        .replace("Trafficking / ER-Golgi", "Trafficking /\nER-Golgi")
        .replace("Metabolism / carbon / lipid", "Metabolism /\ncarbon / lipid")
        .replace("Other annotated protein", "Other annotated\nprotein")
    )


def add_pill(fig, x, y, w, h, label, fontsize=11.0, color="#1F4E7A", face=HEADER):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.005,rounding_size=0.012",
        transform=fig.transFigure,
        facecolor=face,
        edgecolor="none",
        zorder=0.2,
    )
    fig.add_artist(patch)
    fig.text(x + w / 2, y + h / 2, label, ha="center", va="center",
             fontsize=fontsize, fontweight="bold", color=color)


def save_outputs(fig, stem):
    svg = OUT_DIR / f"{stem}.svg"
    png = OUT_DIR / f"{stem}.png"
    png3 = OUT_DIR / f"{stem}_3x.png"
    preview = OUT_DIR / f"{stem}_WHITE_PREVIEW.png"
    fig.savefig(svg, transparent=True)
    fig.savefig(png, dpi=300, transparent=True)
    fig.savefig(png3, dpi=900, transparent=True)
    fig.patch.set_facecolor("white")
    fig.savefig(preview, dpi=220, facecolor="white")
    plt.close(fig)
    return [svg, png, png3, preview]


for path in [COUNTS_CSV, BURDEN_CSV, PROV_JSON]:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(path)

prov = json.loads(PROV_JSON.read_text(encoding="utf-8"))
if prov.get("synthetic_data_used") is not False:
    raise RuntimeError("Provenance does not state synthetic_data_used=false.")
if prov.get("CR_definition") != "CR means 0.1% glucose":
    raise RuntimeError(f"CR definition mismatch: {prov.get('CR_definition')}")

counts = pd.read_csv(COUNTS_CSV)
burden = pd.read_csv(BURDEN_CSV)

for col in ["EI_count", "IE_count", "EE_total", "retention_fraction_numeric"]:
    counts[col] = pd.to_numeric(counts[col], errors="coerce")

counts["IR_from_raw"] = (counts["EI_count"] + counts["IE_count"]) / (
    counts["EI_count"] + counts["IE_count"] + 2.0 * counts["EE_total"]
)

raw_ir_max_diff = (counts["IR_from_raw"] - counts["retention_fraction_numeric"]).abs().max(skipna=True)
if raw_ir_max_diff > 1e-6:
    raise RuntimeError(f"Raw IR audit failed: max diff = {raw_ir_max_diff}")

counts["age_norm"] = counts["age"].astype(str)
counts["glucose_norm"] = counts["glucose"].map(norm_glucose)
counts["mud1_norm"] = counts["mud1_status"].map(norm_mud1)
counts["nmd_norm"] = counts["upf1_status"].map(norm_nmd)

for col in ["is_spliceosomal_mrna", "high_confidence_display"]:
    if col in burden.columns:
        burden[col] = burden[col].astype(str).str.lower().isin(["true", "1", "yes"])
    else:
        burden[col] = True

meta = burden[[
    "intron_id", "display_gene", "common_gene", "systematic_gene", "category", "description",
    "is_spliceosomal_mrna", "high_confidence_display"
]].drop_duplicates("intron_id")

# Panel E: +MUD1, total/rRNA-depleted source counts, NMD-off/upf1D.
e_raw = counts[
    (counts["mud1_norm"] == "MUD1")
    & (counts["nmd_norm"] == "off")
    & (counts["age_norm"].isin(["Young", "Old"]))
    & (counts["glucose_norm"].isin(["2pct", "CR"]))
].copy()

e_raw = e_raw.merge(meta, on="intron_id", how="left")
e_raw = e_raw[(e_raw["is_spliceosomal_mrna"]) & (e_raw["high_confidence_display"])].copy()
if e_raw.empty:
    raise RuntimeError("Panel E data empty after filtering.")

agg = (
    e_raw.groupby(["intron_id", "display_gene", "category", "age_norm", "glucose_norm"], dropna=False)
    .agg(
        mean_ir=("IR_from_raw", "mean"),
        sem_ir=("IR_from_raw", lambda x: float(np.nanstd(x, ddof=1) / math.sqrt(np.sum(pd.notna(x)))) if np.sum(pd.notna(x)) > 1 else 0.0),
        n=("IR_from_raw", lambda x: int(np.sum(pd.notna(x)))),
    )
    .reset_index()
)

wide = agg.pivot_table(index=["intron_id", "display_gene", "category"],
                       columns=["age_norm", "glucose_norm"], values="mean_ir", aggfunc="first").reset_index()
wide.columns = ["_".join(c).strip("_") if isinstance(c, tuple) else c for c in wide.columns]
for col in ["Young_2pct", "Old_2pct", "Young_CR", "Old_CR"]:
    if col not in wide.columns:
        raise RuntimeError(f"Missing expected Panel E column: {col}")

burden["retained_cpm"] = pd.to_numeric(burden.get("retained_cpm"), errors="coerce")
if "age_norm" not in burden.columns:
    burden["age_norm"] = burden["age"].astype(str)
if "glucose_norm" not in burden.columns:
    burden["glucose_norm"] = burden["glucose"].map(norm_glucose)
if "mud1_norm" not in burden.columns:
    burden["mud1_norm"] = burden["mud1_status"].map(norm_mud1)
if "nmd_norm" not in burden.columns:
    burden["nmd_norm"] = burden["upf1_status"].map(norm_nmd)

bur = burden[(burden["mud1_norm"] == "MUD1") & (burden["nmd_norm"] == "off")].copy()
ret = bur.pivot_table(index="intron_id", columns=["age_norm", "glucose_norm"], values="retained_cpm", aggfunc="first").reset_index()
ret.columns = ["intron_id"] + ["retained_cpm_" + "_".join(c) for c in ret.columns[1:]]
wide = wide.merge(ret, on="intron_id", how="left")
wide["age_delta_2pct_ir"] = wide["Old_2pct"] - wide["Young_2pct"]
wide["old_cr_supp_ir"] = wide["Old_2pct"] - wide["Old_CR"]
wide["old2_retained_cpm"] = pd.to_numeric(wide.get("retained_cpm_Old_2pct"), errors="coerce")
wide["candidate_score"] = 2.0 * wide["old_cr_supp_ir"].fillna(0) + 1.5 * wide["age_delta_2pct_ir"].fillna(0) + np.log10(wide["old2_retained_cpm"].fillna(0) + 1) / 5.0

fixed_first_four = ["intron_00163", "intron_00009", "intron_00075", "intron_00304"]
candidate_pool = wide[(wide["Old_2pct"] > 0.05) & (wide["age_delta_2pct_ir"] > 0.02) & (wide["old_cr_supp_ir"] > 0.02) & (wide["old2_retained_cpm"] > 20)].copy()

selected_ids = []
for intron_id in fixed_first_four:
    if intron_id in set(wide["intron_id"]):
        selected_ids.append(intron_id)
for _, row in candidate_pool.sort_values("candidate_score", ascending=False).iterrows():
    intron_id = row["intron_id"]
    if intron_id not in selected_ids:
        selected_ids.append(intron_id)
    if len(selected_ids) >= 6:
        break
selected_ids = selected_ids[:6]
if len(selected_ids) != 6:
    raise RuntimeError("Could not select six Panel E examples.")

selected_df = wide[wide["intron_id"].isin(selected_ids)].copy()
selected_df["__order"] = selected_df["intron_id"].map({v: i for i, v in enumerate(selected_ids)})
selected_df = selected_df.sort_values("__order").drop(columns="__order").reset_index(drop=True)
selected_df["old2_gt_young2"] = selected_df["Old_2pct"] > selected_df["Young_2pct"]
selected_df["old2_gt_oldCR"] = selected_df["Old_2pct"] > selected_df["Old_CR"]
if not bool(selected_df["old2_gt_young2"].all()):
    raise RuntimeError("Panel E claim audit failed: not all examples are age-increased in 2% glucose.")
if not bool(selected_df["old2_gt_oldCR"].all()):
    raise RuntimeError("Panel E claim audit failed: not all examples are lower in old CR than old 2%.")

panelE = agg[agg["intron_id"].isin(selected_df["intron_id"])].copy()

# Panel F: functional-category enrichment of host genes/introns from the same raw NMD-off logic.
background = wide.dropna(subset=["category"]).copy()
selected_set = background[(background["Old_2pct"] > 0.05) & (background["age_delta_2pct_ir"] > 0.02) & (background["old_cr_supp_ir"] > 0.02)].copy()
N = len(background)
K = len(selected_set)
if N == 0 or K == 0:
    raise RuntimeError("Panel F selected set or background is empty.")

enrichment_rows = []
for category, bg_n in background["category"].value_counts().items():
    a = int((selected_set["category"] == category).sum())
    p = hypergeom_right_tail(a, int(bg_n), int(K), int(N))
    fold = (a / K) / (bg_n / N) if K and bg_n else np.nan
    enrichment_rows.append({"category": category, "gene_count": a, "background_count": int(bg_n), "fold_enrichment": float(fold), "fisher_p": float(p)})

enrichment = pd.DataFrame(enrichment_rows)
enrichment["p_adjust_BH"] = bh_adjust(enrichment["fisher_p"])
plot_enrichment = enrichment[(enrichment["gene_count"] >= 2) & (enrichment["fold_enrichment"] > 1.0)].copy()
plot_enrichment = plot_enrichment.sort_values(["fold_enrichment", "p_adjust_BH"], ascending=[True, True]).tail(5).sort_values("fold_enrichment").reset_index(drop=True)
if plot_enrichment.empty:
    raise RuntimeError("Panel F plot enrichment table is empty.")


def draw_panel_e_print():
    fig = plt.figure(figsize=FIG1E_CANVAS_IN, facecolor="none")
    add_pill(fig, 0.08, 0.947, 0.56, 0.038, "Total / rRNA-depleted · NMD-off/upf1D", fontsize=10.4)
    leg_y = 0.966
    fig.add_artist(Line2D([0.705, 0.742], [leg_y, leg_y], transform=fig.transFigure, color=BLUE, lw=2.4, marker="o", ms=4.6, markerfacecolor="white", markeredgewidth=1.35, clip_on=False))
    fig.text(0.750, leg_y, "Young", color=BLUE, fontsize=9.8, fontweight="bold", va="center", ha="left")
    fig.add_artist(Line2D([0.845, 0.882], [leg_y, leg_y], transform=fig.transFigure, color=ORANGE, lw=2.4, marker="o", ms=4.6, markerfacecolor="white", markeredgewidth=1.35, clip_on=False))
    fig.text(0.890, leg_y, "Old", color=ORANGE, fontsize=9.8, fontweight="bold", va="center", ha="left")

    positions = [
        [0.110, 0.705, 0.385, 0.165], [0.575, 0.705, 0.385, 0.165],
        [0.110, 0.405, 0.385, 0.165], [0.575, 0.405, 0.385, 0.165],
        [0.110, 0.105, 0.385, 0.165], [0.575, 0.105, 0.385, 0.165],
    ]

    for i, row in enumerate(selected_df.to_dict("records")):
        ax = fig.add_axes(positions[i])
        intron_id = row["intron_id"]
        sub = panelE[panelE["intron_id"] == intron_id]
        values_for_limits = []
        for age in ["Young", "Old"]:
            for glucose in ["2pct", "CR"]:
                r = sub[(sub["age_norm"] == age) & (sub["glucose_norm"] == glucose)]
                if len(r):
                    mean = float(r["mean_ir"].iloc[0])
                    sem = float(r["sem_ir"].iloc[0])
                    values_for_limits.append(max(1e-5, mean - sem))
                    values_for_limits.append(mean + sem)
        ymin = max(0.01, min(values_for_limits) * 0.45)
        ymax = min(1.25, max(1.02, max(values_for_limits) * 1.45))
        ax.set_facecolor("white")
        ax.set_yscale("log")
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(-0.22, 1.22)
        ax.grid(axis="y", color=GRID, lw=0.85)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color(BORDER)
            spine.set_linewidth(1.15)
        if i >= 4:
            ax.set_xticks([0, 1], ["2%", "0.1% CR"])
            ax.tick_params(axis="x", labelsize=9.6, colors=AXIS, length=3, pad=3)
        else:
            ax.set_xticks([0, 1], ["", ""])
            ax.tick_params(axis="x", length=3, pad=2)
        ytick_candidates = [0.03, 0.1, 0.3, 1.0]
        yticks = [v for v in ytick_candidates if ymin < v < ymax]
        labels = ["1" if abs(v - 1.0) < 1e-8 else "0.3" if abs(v - 0.3) < 1e-8 else "0.1" if abs(v - 0.1) < 1e-8 else "0.03" if abs(v - 0.03) < 1e-8 else f"{v:g}" for v in yticks]
        ax.yaxis.set_major_locator(ticker.FixedLocator(yticks))
        ax.yaxis.set_major_formatter(ticker.FixedFormatter(labels))
        ax.yaxis.set_minor_locator(ticker.NullLocator())
        ax.yaxis.set_minor_formatter(ticker.NullFormatter())
        if i % 2 == 0:
            ax.tick_params(axis="y", labelsize=9.6, colors=AXIS, length=0, pad=2)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)
        x0, y0, w, h = positions[i]
        fig.text(x0, y0 + h + 0.022, str(row["display_gene"]), fontsize=10.8, fontstyle="italic", fontweight="bold", color=TEXT, ha="left", va="bottom")
        for age, color in [("Young", BLUE), ("Old", ORANGE)]:
            ys, sems = [], []
            for glucose in ["2pct", "CR"]:
                r = sub[(sub["age_norm"] == age) & (sub["glucose_norm"] == glucose)]
                if len(r):
                    ys.append(float(r["mean_ir"].iloc[0]))
                    sems.append(float(r["sem_ir"].iloc[0]))
                else:
                    ys.append(np.nan)
                    sems.append(0.0)
            ax.plot([0, 1], ys, color=color, lw=2.2, marker="o", ms=4.8, markerfacecolor="white", markeredgewidth=1.35, zorder=3, clip_on=True)
            ax.errorbar([0, 1], ys, yerr=sems, fmt="none", ecolor=color, elinewidth=1.2, capsize=2.3, capthick=1.1, zorder=2, clip_on=True)
    fig.text(0.030, 0.50, "IR (retained-intron ratio)", rotation=90, ha="center", va="center", fontsize=10.8, fontweight="bold", color=TEXT)
    return fig


def draw_panel_f_print():
    fig = plt.figure(figsize=FIG1F_CANVAS_IN, facecolor="none")
    ax = fig.add_axes([0.39, 0.155, 0.405, 0.805])
    df = plot_enrichment.copy()
    y = np.arange(len(df))
    x = df["fold_enrichment"].astype(float).to_numpy()
    q = df["p_adjust_BH"].astype(float).to_numpy()
    counts_arr = df["gene_count"].astype(float).to_numpy()
    sizes = 115 + 52 * np.sqrt(counts_arr)
    qlog = -np.log10(np.maximum(q, 1e-12))
    if np.nanmax(qlog) - np.nanmin(qlog) < 1e-9:
        t = np.ones_like(qlog) * 0.5
    else:
        t = (qlog - np.nanmin(qlog)) / (np.nanmax(qlog) - np.nanmin(qlog))
    cmap = LinearSegmentedColormap.from_list("custom_q", ["#4C1D95", "#C0267E", "#F59E0B"])
    colors = [cmap(v) for v in t]
    ax.scatter(x, y, s=sizes, c=colors, edgecolor="white", linewidth=1.15, zorder=3)
    ax.axvline(1, color="#7B8794", lw=1.05, ls="--")
    ax.grid(axis="x", color=GRID, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([short_category_label(c) for c in df["category"]], fontsize=11.8, color=TEXT)
    ax.tick_params(axis="y", length=0, pad=7)
    ax.tick_params(axis="x", labelsize=10.8, colors=AXIS, pad=3)
    ax.set_xlabel("Enrichment fold", fontsize=12.3, fontweight="bold", labelpad=8)
    ax.set_xlim(0, max(3.0, float(np.nanmax(x)) * 1.18))
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(1.1)
    lx = 0.825
    fig.text(lx, 0.76, "Gene count", fontsize=11.2, fontweight="bold", color=TEXT, ha="left")
    for j, count in enumerate([5, 10, 20]):
        yy = 0.70 - j * 0.074
        ms = math.sqrt(115 + 52 * math.sqrt(count))
        fig.add_artist(Line2D([lx + 0.035], [yy], marker="o", markersize=ms, color="#333333", lw=0, transform=fig.transFigure))
        fig.text(lx + 0.087, yy - 0.007, str(count), fontsize=9.8, color=TEXT, ha="left")
    fig.text(lx, 0.41, "q value", fontsize=11.2, fontweight="bold", color=TEXT, ha="left")
    cax = fig.add_axes([lx, 0.35, 0.145, 0.038])
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    cax.imshow(grad, aspect="auto", cmap=cmap, origin="lower")
    cax.set_xticks([0, 127, 255])
    cax.set_xticklabels([f"{np.nanmax(q):.2f}", f"{np.nanmedian(q):.2f}", f"{np.nanmin(q):.2f}"], fontsize=8.2)
    cax.set_yticks([])
    for spine in cax.spines.values():
        spine.set_visible(False)
    return fig


outputs = []
outputs += save_outputs(draw_panel_e_print(), "Figure_1E_CONTENTONLY_NATURE_PRINT")
outputs += save_outputs(draw_panel_f_print(), "Figure_1F_CONTENTONLY_NATURE_PRINT")

selected_df.to_csv(OUT_DIR / "Figure_1E_selected_six_introns_audited.tsv", sep="\t", index=False)
panelE.to_csv(OUT_DIR / "Figure_1E_plotted_values_raw_total_rRNA.tsv", sep="\t", index=False)
enrichment.to_csv(OUT_DIR / "Figure_1F_functional_category_enrichment.tsv", sep="\t", index=False)
plot_enrichment.to_csv(OUT_DIR / "Figure_1F_plotted_categories.tsv", sep="\t", index=False)
selected_set.to_csv(OUT_DIR / "Figure_1F_selected_set_introns.tsv", sep="\t", index=False)

audit = {
    "data_changed": False,
    "synthetic_data_used": False,
    "polyA_data_used": False,
    "capture_used": "total/rRNA-depleted",
    "titles_removed": True,
    "content_only": True,
    "font": FONT,
    "render_contract": "fixed canvas; transparent SVG/PNG/3x PNG plus white preview PNG; no bbox_inches='tight'",
    "panel_E_metric": "+MUD1 total/rRNA-depleted raw NMD-off/upf1D retained-intron IR, not off-minus-on NMD-hidden IR",
    "panel_F_exact_definition": (
        "Functional-category enrichment of host genes/introns from +MUD1 total/rRNA-depleted NMD-off/upf1D samples "
        "where old 2% IR > 0.05, old 2% IR exceeds young 2% IR by >0.02, and old 2% IR exceeds old 0.1% CR IR by >0.02. "
        "This is not mud1D, not poly-A, and not off-minus-on NMD-hidden IR."
    ),
    "panel_E_examples": selected_df[["display_gene", "intron_id", "category", "Old_2pct", "Young_2pct", "Old_CR", "age_delta_2pct_ir", "old_cr_supp_ir"]].to_dict(orient="records"),
    "panel_E_claim_audit": {
        "all_examples_old_2pct_gt_young_2pct": bool(selected_df["old2_gt_young2"].all()),
        "all_examples_old_2pct_gt_old_CR": bool(selected_df["old2_gt_oldCR"].all()),
        "claim_allowed": "Examples are age-increased in 2% glucose and lower in old CR than old 2%."
    },
    "panel_F_selected_set_size": int(K),
    "panel_F_background_size": int(N),
    "raw_IR_formula": "IR = (EI_count + IE_count) / (EI_count + IE_count + 2 * EE_total)",
    "raw_IR_max_abs_diff_vs_retention_fraction_numeric": float(raw_ir_max_diff),
    "source_provenance": prov,
    "inputs": {"counts_csv": str(COUNTS_CSV), "burden_csv": str(BURDEN_CSV), "provenance_json": str(PROV_JSON)},
    "input_sha256": {"counts_csv": sha256(COUNTS_CSV), "burden_csv": sha256(BURDEN_CSV), "provenance_json": sha256(PROV_JSON)},
    "outputs": [str(p) for p in outputs],
}

(OUT_DIR / "Figure1EF_CONTENTONLY_NATURE_PRINT_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

print("DONE=True")
print("OUT_DIR=" + str(OUT_DIR))
print("DATA_CHANGED=False")
print("POLYA_DATA_USED=False")
print("CAPTURE_USED=total/rRNA-depleted")
print("NMD_HIDDEN_COMPUTED=False")
print("RAW_NMDOFF_IR_USED=True")
print("CR_DEFINITION=0.1% glucose")
print("SYNTHETIC_DATA_USED=False")
print("RAW_IR_AUDIT_MAX_DIFF=" + str(raw_ir_max_diff))
print("PANEL_E_SELECTED=" + ", ".join(selected_df["display_gene"].astype(str) + " " + selected_df["intron_id"].astype(str)))
print("PANEL_E_CLAIM_AUDIT_OLD2_GT_YOUNG2=" + str(bool(selected_df["old2_gt_young2"].all())))
print("PANEL_E_CLAIM_AUDIT_OLD2_GT_OLDCR=" + str(bool(selected_df["old2_gt_oldCR"].all())))
print("PANEL_F_SET_SIZE=" + str(K))
print("PANEL_F_BACKGROUND_SIZE=" + str(N))
print("OUTPUT_E=" + str(OUT_DIR / "Figure_1E_CONTENTONLY_NATURE_PRINT_3x.png"))
print("OUTPUT_F=" + str(OUT_DIR / "Figure_1F_CONTENTONLY_NATURE_PRINT_3x.png"))
'@

$ScriptPath = Join-Path $OutDir "make_fig1EF_contentonly_nature_print.py"
$LogPath = Join-Path $OutDir "RUN_LOG_Figure1EF_CONTENTONLY_NATURE_PRINT.txt"
Set-Content -Path $ScriptPath -Value $Py -Encoding UTF8

Write-Host ""
Write-Host "Running print-typography Figure 1E/F generator..."
& $PythonCmd @PythonArgs $ScriptPath *> $LogPath
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Python failed. Last 200 log lines:"
    Get-Content $LogPath -Tail 200
    throw "Figure 1E/F generation failed. Log: $LogPath"
}

Write-Host ""
Write-Host "Python completed. Tail of log:"
Get-Content $LogPath -Tail 100

$Expected = @(
    "Figure_1E_CONTENTONLY_NATURE_PRINT.svg",
    "Figure_1E_CONTENTONLY_NATURE_PRINT.png",
    "Figure_1E_CONTENTONLY_NATURE_PRINT_3x.png",
    "Figure_1E_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png",
    "Figure_1F_CONTENTONLY_NATURE_PRINT.svg",
    "Figure_1F_CONTENTONLY_NATURE_PRINT.png",
    "Figure_1F_CONTENTONLY_NATURE_PRINT_3x.png",
    "Figure_1F_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png",
    "Figure1EF_CONTENTONLY_NATURE_PRINT_audit.json"
)

$Missing = @()
foreach ($File in $Expected) {
    $Path = Join-Path $OutDir $File
    if (!(Test-Path $Path)) {
        $Missing += $File
    }
}

if ($Missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing outputs:"
    $Missing | ForEach-Object { Write-Host $_ }
    throw "Script ran but did not create all expected outputs."
}

Write-Host ""
Write-Host "Created outputs:"
Get-ChildItem -Path $OutDir | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

Write-Host ""
Write-Host "Use these two in your composite:"
Write-Host "$OutDir\Figure_1E_CONTENTONLY_NATURE_PRINT_3x.png"
Write-Host "$OutDir\Figure_1F_CONTENTONLY_NATURE_PRINT_3x.png"

Write-Host ""
Write-Host "Preview these first:"
Write-Host "$OutDir\Figure_1E_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png"
Write-Host "$OutDir\Figure_1F_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png"

Write-Host ""
Write-Host "Audit file:"
Write-Host "$OutDir\Figure1EF_CONTENTONLY_NATURE_PRINT_audit.json"

Write-Host ""
Write-Host "Opening folder:"
Write-Host $OutDir
explorer.exe $OutDir
