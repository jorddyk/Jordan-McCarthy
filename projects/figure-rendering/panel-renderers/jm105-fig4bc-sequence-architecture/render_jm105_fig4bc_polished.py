#!/usr/bin/env python3
"""Polished JM105 Figure 4B/C selected-vs-background architecture renderer.

This script renders the accepted Figure 4B/C panels from real Euler source tables.
It writes transparent SVG/PDF/PNG, white-preview PNGs, derived TSVs, and audits.

Scope fence:
- total/rRNA-depleted JM105 selected/background logic only
- no poly-A, P-vs-T, mRNA-like, or P-T sources
- no fake biological data

Important implementation lessons preserved here:
- U1 is shown as integer paired bases, not percent.
- p-values use ax.transAxes, never data-coordinate y placement.
- bracket uses x=data, y=axes-fraction via a blended transform.
- no bbox_inches='tight'; canvas dimensions are fixed constants.
"""

import csv
import json
import math
import random
import statistics
import sys
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import transforms
from PIL import Image

# ============================================================
# Fixed render contract
# ============================================================
PANEL_B_WIDTH_IN = 2.19201990376203
PANEL_B_HEIGHT_IN = 2.67464457567804
PANEL_C_WIDTH_IN = 2.159055118110236
PANEL_C_HEIGHT_IN = 2.6988188976377954
DPI = 360

# IMPORTANT: bbox_inches="tight" does not appear in this script.
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "Liberation Sans", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

PROJECT_ROOT = Path("/cluster/scratch/jmccarthy/JM105_RNAseq")

SELECTED_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V1_20260703_110602/01_LOCKED_CANDIDATES_WITH_RECOMPUTED_SCORE.tsv",
    PROJECT_ROOT / "Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050/derived_data/Figure4A_all49_candidate_table.tsv",
    PROJECT_ROOT / "Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv",
]

BACKGROUND_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V2_20260703_111531/05B_CLEAN_SPLICEOSOMAL_BACKGROUND.tsv",
    PROJECT_ROOT / "Figure4_COMPUTE_SEQUENCE_ARCHITECTURE_FEATURES_V1_20260703_140709/04_BACKGROUND_SEQUENCE_ARCHITECTURE.tsv",
]

FEATURE_B_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "Figure4_PATCH_BIOCONDA_MAXENTSCAN_GATE_V9_20260706_103936/10_PANEL_B_MAXENT_U1_SOURCE_TABLE_LOCKED.tsv",
    PROJECT_ROOT / "Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/10_PANEL_B_MAXENT_U1_SOURCE_TABLE.tsv",
]

FEATURE_C_SOURCE_CANDIDATES = [
    PROJECT_ROOT / "Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv",
    PROJECT_ROOT / "Figure4_TARGETED_MOCKUP_SOURCE_LOCK_V3_20260706_095126/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv",
]

OUT_DIR = Path("out")
PANEL_DIR = OUT_DIR / "panels"
AUDIT_DIR = OUT_DIR / "audits"
DATA_DIR = OUT_DIR / "derived_data"

SELECTED_COLOR = "#7C5AA3"
BACKGROUND_COLOR = "#BDBDBD"
EDGE_COLOR = "#595959"
GRID_COLOR = "#D6D6D6"
TEXT_COLOR = "#222222"

RNG = random.Random(20260709)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def choose_existing(paths, role: str) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise RuntimeError(f"No existing file found for role: {role}")


def read_table(path: Path):
    delimiter = "," if path.suffix.lower() == ".csv" else "\t"
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = [dict(row) for row in reader]
        header = list(reader.fieldnames or [])
    return rows, header


def write_tsv(path: Path, rows, fieldnames=None) -> None:
    ensure_dir(path.parent)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def parse_float(value):
    text = str(value).strip()
    if text == "" or text.lower() in {"na", "nan", "none", "null", "inf", "-inf"}:
        return None
    try:
        val = float(text)
    except Exception:
        return None
    if not math.isfinite(val):
        return None
    return val


def parse_int(value):
    val = parse_float(value)
    if val is None:
        return None
    if abs(val - round(val)) < 1e-8:
        return int(round(val))
    return None


def choose_text(row, cols):
    for col in cols:
        if col in row:
            value = str(row.get(col, "")).strip()
            if value:
                return value
    return ""


def count_groups(rows):
    counts = {"Background": 0, "Selected": 0}
    for row in rows:
        counts[row["group"]] = counts.get(row["group"], 0) + 1
    return counts


def quantiles(values):
    vals = sorted(float(v) for v in values)
    if not vals:
        return {"n": 0}

    def q(p):
        if len(vals) == 1:
            return vals[0]
        pos = p * (len(vals) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return vals[lo]
        frac = pos - lo
        return vals[lo] * (1 - frac) + vals[hi] * frac

    return {
        "n": len(vals),
        "min": vals[0],
        "q1": q(0.25),
        "median": q(0.50),
        "q3": q(0.75),
        "max": vals[-1],
        "mean": statistics.mean(vals),
    }


def mean_rank(values):
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg
        i = j + 1
    return ranks


def mann_whitney_u_two_sided(x, y):
    x = [float(v) for v in x]
    y = [float(v) for v in y]
    if len(x) == 0 or len(y) == 0:
        return {"u": "", "p": "", "method": "not_computable"}
    try:
        from scipy.stats import mannwhitneyu
        result = mannwhitneyu(x, y, alternative="two-sided", method="auto")
        return {"u": float(result.statistic), "p": float(result.pvalue), "method": "scipy_mannwhitneyu_two_sided_auto"}
    except Exception:
        combined = x + y
        ranks = mean_rank(combined)
        n1 = len(x)
        n2 = len(y)
        r1 = sum(ranks[:n1])
        u1 = r1 - n1 * (n1 + 1) / 2.0
        mean_u = n1 * n2 / 2.0
        var_u = n1 * n2 * (n1 + n2 + 1) / 12.0
        z = (u1 - mean_u) / math.sqrt(var_u)
        p = math.erfc(abs(z) / math.sqrt(2.0))
        return {"u": u1, "p": p, "method": "normal_approx_no_tie_correction"}


def p_to_stars(p):
    if p == "" or p is None:
        return "n/a"
    p = float(p)
    if p < 0.0001:
        return "****"
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def format_p(p):
    if p == "" or p is None:
        return "p = n/a"
    p = float(p)
    if p < 0.0001:
        return "p < 1e-4"
    if p < 0.001:
        return f"p = {p:.1e}"
    if p < 0.01:
        return f"p = {p:.3f}"
    if p < 0.1:
        return f"p = {p:.2f}"
    return f"p = {p:.2f}"


def find_match(source_row, feature_rows):
    src_audit = str(source_row.get("audit_intron_key", "")).strip()
    src_join = str(source_row.get("join_key", "")).strip()
    src_orf = str(source_row.get("orf", "")).strip()
    src_gene = str(source_row.get("gene_label", "")).strip()

    if src_audit:
        hits = [row for row in feature_rows if str(row.get("audit_intron_key", "")).strip() == src_audit]
        if len(hits) == 1:
            return hits[0], "audit_intron_key"

    if src_join:
        hits = [row for row in feature_rows if str(row.get("join_key", "")).strip() == src_join]
        if len(hits) == 1:
            return hits[0], "join_key"

    hits = [
        row for row in feature_rows
        if str(row.get("orf", "")).strip() == src_orf and str(row.get("gene_label", "")).strip() == src_gene
    ]
    if len(hits) == 1:
        return hits[0], "orf_gene_label"

    if src_orf:
        hits = [row for row in feature_rows if str(row.get("orf", "")).strip() == src_orf]
        if len(hits) == 1:
            return hits[0], "orf_only"

    return None, "no_match"


def load_grouped_source_rows():
    selected_path = choose_existing(SELECTED_SOURCE_CANDIDATES, "selected_source")
    background_path = choose_existing(BACKGROUND_SOURCE_CANDIDATES, "background_source")
    selected_rows, _ = read_table(selected_path)
    background_rows, _ = read_table(background_path)

    if len(selected_rows) != 49:
        raise RuntimeError(f"Selected source must contain 49 rows; found {len(selected_rows)} in {selected_path}")
    if len(background_rows) != 232:
        raise RuntimeError(f"Background source must contain 232 rows; found {len(background_rows)} in {background_path}")

    grouped = []
    for row in background_rows:
        grouped.append({"group": "Background", "row": row, "source_path": str(background_path)})
    for row in selected_rows:
        grouped.append({"group": "Selected", "row": row, "source_path": str(selected_path)})

    manifest = [
        {"role": "selected_source", "path": str(selected_path), "row_count": len(selected_rows)},
        {"role": "background_source", "path": str(background_path), "row_count": len(background_rows)},
    ]
    return grouped, manifest


def build_panel_tables():
    grouped, manifest = load_grouped_source_rows()
    feature_b_path = choose_existing(FEATURE_B_SOURCE_CANDIDATES, "feature_b_source")
    feature_c_path = choose_existing(FEATURE_C_SOURCE_CANDIDATES, "feature_c_source")
    feature_b_rows, _ = read_table(feature_b_path)
    feature_c_rows, _ = read_table(feature_c_path)

    manifest.extend([
        {"role": "feature_b_source", "path": str(feature_b_path), "row_count": len(feature_b_rows)},
        {"role": "feature_c_source", "path": str(feature_c_path), "row_count": len(feature_c_rows)},
    ])

    panel_b_rows = []
    panel_c_rows = []
    join_audit = []
    u1_metric_audit = []

    for item in grouped:
        src = item["row"]
        group = item["group"]

        b_row, b_method = find_match(src, feature_b_rows)
        c_row, c_method = find_match(src, feature_c_rows)

        gene_label = choose_text(src, ["gene_label"])
        orf = choose_text(src, ["orf"])
        audit_intron_key = choose_text(src, ["audit_intron_key", "join_key"])

        if b_row is not None:
            maxent = parse_float(b_row.get("five_prime_ss_maxent"))
            wc = parse_int(b_row.get("u1_best_WC_pairs"))
            gu = parse_int(b_row.get("u1_best_GU_pairs"))
            pct = parse_float(b_row.get("u1_complementarity_percent_paired"))
            if maxent is not None and wc is not None and gu is not None:
                paired = wc + gu
                panel_b_rows.append({
                    "group": group,
                    "gene_label": gene_label,
                    "orf": orf,
                    "audit_intron_key": audit_intron_key,
                    "feature_5ss_maxent": maxent,
                    "feature_u1_paired_bases": paired,
                    "u1_best_WC_pairs": wc,
                    "u1_best_GU_pairs": gu,
                    "u1_complementarity_percent_paired_hidden_audit": pct if pct is not None else "",
                    "feature_match_method": b_method,
                    "feature_source_path": str(feature_b_path),
                })
                u1_metric_audit.append({
                    "group": group,
                    "gene_label": gene_label,
                    "orf": orf,
                    "audit_intron_key": audit_intron_key,
                    "u1_best_WC_pairs": wc,
                    "u1_best_GU_pairs": gu,
                    "visible_u1_paired_bases": paired,
                    "hidden_percent_audit": pct if pct is not None else "",
                    "consistency_check": "PASS" if pct is not None and abs(pct - (100.0 * paired / 9.0)) < 0.25 else "CHECK",
                })

        if c_row is not None:
            intron_len = parse_float(c_row.get("intron_length_nt_computed"))
            bp3 = parse_float(c_row.get("bp_to_3ss_distance_nt"))
            if intron_len is not None and bp3 is not None:
                panel_c_rows.append({
                    "group": group,
                    "gene_label": gene_label,
                    "orf": orf,
                    "audit_intron_key": audit_intron_key,
                    "feature_intron_length_nt": intron_len,
                    "feature_bp_to_3ss_nt": bp3,
                    "feature_match_method": c_method,
                    "feature_source_path": str(feature_c_path),
                })

        join_audit.append({
            "group": group,
            "gene_label": gene_label,
            "orf": orf,
            "audit_intron_key": audit_intron_key,
            "feature_b_join_method": b_method,
            "feature_c_join_method": c_method,
            "feature_b_found": "yes" if b_row is not None else "no",
            "feature_c_found": "yes" if c_row is not None else "no",
        })

    b_counts = count_groups(panel_b_rows)
    c_counts = count_groups(panel_c_rows)
    blockers = []
    if b_counts.get("Selected", 0) != 49 or b_counts.get("Background", 0) != 232:
        blockers.append(f"Panel 4B counts failed after join: {b_counts}")
    if c_counts.get("Selected", 0) != 49 or c_counts.get("Background", 0) != 232:
        blockers.append(f"Panel 4C counts failed after join: {c_counts}")
    if blockers:
        write_tsv(AUDIT_DIR / "RENDER_BLOCKERS.tsv", [{"blocker": blocker} for blocker in blockers], ["blocker"])
        raise RuntimeError("; ".join(blockers))

    return panel_b_rows, panel_c_rows, join_audit, manifest, u1_metric_audit


def feature_values(rows, key, group):
    return [float(row[key]) for row in rows if row["group"] == group]


def collect_stats(panel_name, rows, feature_specs):
    out = []
    for spec in feature_specs:
        bg = feature_values(rows, spec["key"], "Background")
        sel = feature_values(rows, spec["key"], "Selected")
        mw = mann_whitney_u_two_sided(sel, bg)
        q_bg = quantiles(bg)
        q_sel = quantiles(sel)
        out.append({
            "panel": panel_name,
            "feature_key": spec["key"],
            "feature_label": spec["label"],
            "background_n": q_bg["n"],
            "selected_n": q_sel["n"],
            "background_median": q_bg["median"],
            "selected_median": q_sel["median"],
            "background_q1": q_bg["q1"],
            "background_q3": q_bg["q3"],
            "selected_q1": q_sel["q1"],
            "selected_q3": q_sel["q3"],
            "mann_whitney_u": mw["u"],
            "mann_whitney_p": mw["p"],
            "significance_symbol": p_to_stars(mw["p"]),
            "stat_method": mw["method"],
        })
    return out


def jittered_x(center, n):
    return [center + RNG.uniform(-0.10, 0.10) for _ in range(n)]


def draw_significance(ax, spec, stats_row):
    blend = transforms.blended_transform_factory(ax.transData, ax.transAxes)

    bracket_y = spec["bracket_y_axes"]
    bracket_drop = spec["bracket_drop_axes"]
    symbol_y = spec["symbol_y_axes"]

    ax.plot(
        [1.0, 1.0, 2.0, 2.0],
        [bracket_y - bracket_drop, bracket_y, bracket_y, bracket_y - bracket_drop],
        transform=blend,
        color=EDGE_COLOR,
        linewidth=0.9,
        zorder=8,
        clip_on=False,
    )

    ax.text(
        1.5,
        symbol_y,
        stats_row["significance_symbol"],
        transform=blend,
        ha="center",
        va="center",
        fontsize=7.4,
        fontweight="bold",
        color=TEXT_COLOR,
        zorder=9,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.7},
        clip_on=False,
    )

    ax.text(
        spec["p_x_axes"],
        spec["p_y_axes"],
        format_p(stats_row["mann_whitney_p"]),
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=6.4,
        color=TEXT_COLOR,
        zorder=9,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.0},
        clip_on=False,
    )


def draw_box_strip(ax, rows, spec, stats_row):
    bg_vals = feature_values(rows, spec["key"], "Background")
    sel_vals = feature_values(rows, spec["key"], "Selected")

    ax.set_xlim(0.45, 2.55)
    ax.set_ylim(*spec["ylim"])
    ax.set_yticks(spec["yticks"])

    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.45)
    ax.xaxis.grid(False)

    ax.scatter(jittered_x(1.0, len(bg_vals)), bg_vals, s=25, facecolor=BACKGROUND_COLOR, edgecolor=EDGE_COLOR, linewidth=0.33, alpha=0.82, zorder=2)
    ax.scatter(jittered_x(2.0, len(sel_vals)), sel_vals, s=25, facecolor=SELECTED_COLOR, edgecolor=EDGE_COLOR, linewidth=0.33, alpha=0.82, zorder=2)

    bp = ax.boxplot(
        [bg_vals, sel_vals],
        positions=[1, 2],
        widths=0.46,
        patch_artist=True,
        showfliers=False,
        whis=(5, 95),
        boxprops={"facecolor": "white", "edgecolor": EDGE_COLOR, "linewidth": 1.0, "alpha": 0.42, "zorder": 5},
        whiskerprops={"color": EDGE_COLOR, "linewidth": 0.95, "zorder": 6},
        capprops={"color": EDGE_COLOR, "linewidth": 0.95, "zorder": 6},
        medianprops={"color": EDGE_COLOR, "linewidth": 1.35, "zorder": 7},
    )
    bp["boxes"][0].set_facecolor(BACKGROUND_COLOR)
    bp["boxes"][1].set_facecolor(SELECTED_COLOR)

    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Background", "Selected"], fontsize=6.9)
    ax.set_ylabel(spec["ylabel"], fontsize=7.8, labelpad=4)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.tick_params(axis="y", labelsize=6.9, length=2.3, width=0.5, pad=2)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(0.7)
        ax.spines[spine].set_color(EDGE_COLOR)

    draw_significance(ax, spec, stats_row)


def render_panel(panel_name, width_in, height_in, rows, feature_specs, stats_rows, stem):
    fig = plt.figure(figsize=(width_in, height_in), dpi=DPI)
    fig.patch.set_alpha(0.0)

    top_ax = fig.add_axes([0.22, 0.60, 0.66, 0.28])
    bottom_ax = fig.add_axes([0.22, 0.12, 0.66, 0.28])

    fig.text(0.53, 0.965, feature_specs[0]["title"], ha="center", va="top", fontsize=8.9, fontweight="bold", color=TEXT_COLOR)
    fig.text(0.53, 0.500, feature_specs[1]["title"], ha="center", va="top", fontsize=8.9, fontweight="bold", color=TEXT_COLOR)

    draw_box_strip(top_ax, rows, feature_specs[0], stats_rows[0])
    draw_box_strip(bottom_ax, rows, feature_specs[1], stats_rows[1])

    svg_path = PANEL_DIR / f"{stem}.svg"
    pdf_path = PANEL_DIR / f"{stem}.pdf"
    png_path = PANEL_DIR / f"{stem}.png"
    white_path = PANEL_DIR / f"{stem}_white_preview.png"

    fig.savefig(svg_path, transparent=True)
    fig.savefig(pdf_path, transparent=True)
    fig.savefig(png_path, dpi=DPI, transparent=True)
    fig.savefig(white_path, dpi=DPI, transparent=False, facecolor="white")
    plt.close(fig)

    return {"panel": panel_name, "svg": str(svg_path), "pdf": str(pdf_path), "transparent_png": str(png_path), "white_preview_png": str(white_path)}


def png_size_audit(rendered):
    rows = []
    for item in rendered:
        for kind in ["transparent_png", "white_preview_png"]:
            path = Path(item[kind])
            if not path.exists():
                rows.append({"panel": item["panel"], "kind": kind, "exists": "no", "path": str(path)})
                continue
            with Image.open(path) as img:
                rows.append({"panel": item["panel"], "kind": kind, "exists": "yes", "path": str(path), "width_px": img.size[0], "height_px": img.size[1], "mode": img.mode})
    return rows


def make_contact_sheet(rendered):
    images = []
    for item in rendered:
        with Image.open(Path(item["white_preview_png"])).convert("RGB") as img:
            images.append(img.copy())
    gap = 40
    total_w = sum(image.size[0] for image in images) + gap * (len(images) + 1)
    max_h = max(image.size[1] for image in images) + 2 * gap
    sheet = Image.new("RGB", (total_w, max_h), "white")
    x = gap
    for image in images:
        sheet.paste(image, (x, gap))
        x += image.size[0] + gap
    out = PANEL_DIR / "Figure4BC_polished_contact_sheet_white_preview.png"
    sheet.save(out)
    return str(out)


def main():
    ensure_dir(OUT_DIR)
    ensure_dir(PANEL_DIR)
    ensure_dir(AUDIT_DIR)
    ensure_dir(DATA_DIR)

    panel_b_rows, panel_c_rows, join_audit, manifest_rows, u1_metric_audit = build_panel_tables()
    b_counts = count_groups(panel_b_rows)
    c_counts = count_groups(panel_c_rows)

    b_specs = [
        {"key": "feature_5ss_maxent", "label": "5′SS strength", "title": "5′SS strength", "ylabel": "MaxEnt score", "ylim": (-12.0, 16.0), "yticks": [-10, 0, 10], "bracket_y_axes": 0.915, "bracket_drop_axes": 0.040, "symbol_y_axes": 0.975, "p_x_axes": 0.965, "p_y_axes": 0.500},
        {"key": "feature_u1_paired_bases", "label": "U1 complementarity", "title": "U1 complementarity", "ylabel": "Paired bases (n)", "ylim": (4.5, 10.5), "yticks": [5, 7, 9], "bracket_y_axes": 0.865, "bracket_drop_axes": 0.035, "symbol_y_axes": 0.940, "p_x_axes": 0.965, "p_y_axes": 0.710},
    ]

    c_specs = [
        {"key": "feature_intron_length_nt", "label": "Intron length", "title": "Intron length", "ylabel": "Length (nt)", "ylim": (0.0, 1220.0), "yticks": [0, 500, 1000], "bracket_y_axes": 0.900, "bracket_drop_axes": 0.040, "symbol_y_axes": 0.960, "p_x_axes": 0.965, "p_y_axes": 0.690},
        {"key": "feature_bp_to_3ss_nt", "label": "BP–3′SS distance", "title": "BP–3′SS distance", "ylabel": "Distance (nt)", "ylim": (0.0, 205.0), "yticks": [0, 100, 200], "bracket_y_axes": 0.900, "bracket_drop_axes": 0.040, "symbol_y_axes": 0.960, "p_x_axes": 0.965, "p_y_axes": 0.690},
    ]

    b_stats = collect_stats("4B", panel_b_rows, b_specs)
    c_stats = collect_stats("4C", panel_c_rows, c_specs)

    rendered = []
    rendered.append(render_panel("4B", PANEL_B_WIDTH_IN, PANEL_B_HEIGHT_IN, panel_b_rows, b_specs, b_stats, "Figure4_panel_B_polished"))
    rendered.append(render_panel("4C", PANEL_C_WIDTH_IN, PANEL_C_HEIGHT_IN, panel_c_rows, c_specs, c_stats, "Figure4_panel_C_polished"))
    contact_sheet = make_contact_sheet(rendered)

    write_tsv(DATA_DIR / "Figure4B_polished_values_with_ids.tsv", panel_b_rows)
    write_tsv(DATA_DIR / "Figure4C_polished_values_with_ids.tsv", panel_c_rows)
    write_tsv(AUDIT_DIR / "Figure4BC_source_manifest.tsv", manifest_rows)
    write_tsv(AUDIT_DIR / "Figure4BC_join_audit.tsv", join_audit)
    write_tsv(AUDIT_DIR / "Figure4B_u1_metric_audit.tsv", u1_metric_audit)
    write_tsv(AUDIT_DIR / "Figure4B_stats_audit.tsv", b_stats)
    write_tsv(AUDIT_DIR / "Figure4C_stats_audit.tsv", c_stats)

    lane_audit = [
        {"panel": "4B", "object": "5′SS strength title", "lane": "descriptor/title", "anchor": "(0.53,0.965)"},
        {"panel": "4B", "object": "U1 complementarity title", "lane": "descriptor/title", "anchor": "(0.53,0.500)"},
        {"panel": "4B", "object": "top distribution", "lane": "plot", "anchor": "[0.22,0.60,0.66,0.28]"},
        {"panel": "4B", "object": "bottom distribution", "lane": "plot", "anchor": "[0.22,0.12,0.66,0.28]"},
        {"panel": "4B", "object": "y labels", "lane": "label", "anchor": "left of axes"},
        {"panel": "4B", "object": "Background/Selected", "lane": "x-tick", "anchor": "x=1,2"},
        {"panel": "4B", "object": "bracket", "lane": "right-stat", "anchor": "x=data, y=axes fraction"},
        {"panel": "4B", "object": "stars/ns", "lane": "right-stat", "anchor": "above bracket with white backing"},
        {"panel": "4B", "object": "p-value", "lane": "right-stat", "anchor": "upper-right ax.transAxes white patch"},
        {"panel": "4B", "object": "footer provenance/counts", "lane": "footer", "anchor": "not drawn; moved to audits"},
        {"panel": "4C", "object": "Intron length title", "lane": "descriptor/title", "anchor": "(0.53,0.965)"},
        {"panel": "4C", "object": "BP–3′SS distance title", "lane": "descriptor/title", "anchor": "(0.53,0.500)"},
        {"panel": "4C", "object": "top distribution", "lane": "plot", "anchor": "[0.22,0.60,0.66,0.28]"},
        {"panel": "4C", "object": "bottom distribution", "lane": "plot", "anchor": "[0.22,0.12,0.66,0.28]"},
        {"panel": "4C", "object": "y labels", "lane": "label", "anchor": "left of axes"},
        {"panel": "4C", "object": "Background/Selected", "lane": "x-tick", "anchor": "x=1,2"},
        {"panel": "4C", "object": "bracket", "lane": "right-stat", "anchor": "x=data, y=axes fraction"},
        {"panel": "4C", "object": "stars/ns", "lane": "right-stat", "anchor": "above bracket with white backing"},
        {"panel": "4C", "object": "p-value", "lane": "right-stat", "anchor": "upper-right ax.transAxes white patch"},
        {"panel": "4C", "object": "footer provenance/counts", "lane": "footer", "anchor": "not drawn; moved to audits"},
    ]
    write_tsv(AUDIT_DIR / "Figure4BC_lane_audit.tsv", lane_audit)

    collision_audit = [
        {"panel": "4B", "collision": "p-value × x-axis", "resolution": "p-value uses ax.transAxes y; cannot fall onto data baseline"},
        {"panel": "4B", "collision": "stars/ns × bracket", "resolution": "symbol_y_axes separated from bracket_y_axes and white backing added"},
        {"panel": "4B", "collision": "stars/ns × p-value", "resolution": "stars centered above bracket; p-value anchored separately"},
        {"panel": "4B", "collision": "p-value × data", "resolution": "p-value placed in right-side white space with white backing"},
        {"panel": "4B", "collision": "footer lane", "resolution": "no visible footer objects"},
        {"panel": "4C", "collision": "p-value × x-axis", "resolution": "p-value uses ax.transAxes y; cannot fall onto data baseline"},
        {"panel": "4C", "collision": "ns × bracket", "resolution": "ns placed above bracket with white backing and vertical gap"},
        {"panel": "4C", "collision": "p-value × data", "resolution": "p-value placed in upper-right white space with white backing"},
        {"panel": "4C", "collision": "footer lane", "resolution": "no visible footer objects"},
        {"panel": "4C", "collision": "dense gridlines", "resolution": "major gridlines only"},
    ]
    write_tsv(AUDIT_DIR / "Figure4BC_collision_audit.tsv", collision_audit)

    write_tsv(AUDIT_DIR / "Figure4BC_png_size_audit.tsv", png_size_audit(rendered))

    output_audit = []
    for item in rendered:
        for kind in ["svg", "pdf", "transparent_png", "white_preview_png"]:
            p = Path(item[kind])
            output_audit.append({"panel": item["panel"], "kind": kind, "path": str(p), "exists": "yes" if p.exists() else "no", "size_bytes": p.stat().st_size if p.exists() else ""})
    cp = Path(contact_sheet)
    output_audit.append({"panel": "4B_4C", "kind": "contact_sheet_white_preview", "path": str(cp), "exists": "yes" if cp.exists() else "no", "size_bytes": cp.stat().st_size if cp.exists() else ""})
    write_tsv(AUDIT_DIR / "Figure4BC_output_file_audit.tsv", output_audit)

    final_self_audit = [
        {"check": "descriptor/title lane", "finding": "titles placed outside axes at fixed anchors"},
        {"check": "plot lane", "finding": "all points retained; box/whisker drawn above dots"},
        {"check": "label lane", "finding": "y-labels retained; sparse y-ticks used"},
        {"check": "legend lane", "finding": "checked; no legend object used"},
        {"check": "x-tick lane", "finding": "Background/Selected retained on all subplots"},
        {"check": "right-stat lane", "finding": "bracket, stars/ns, and p-value use separated anchors; p-value uses ax.transAxes"},
        {"check": "footer lane", "finding": "no visible footer; information saved to audits/manifests"},
        {"check": "p-value transform bug", "finding": "fixed; p-value no longer uses data-coordinate y placement"},
        {"check": "ns-bracket spacing", "finding": "symbol placed above bracket with white backing"},
        {"check": "text-level collisions", "finding": "patched p-value × x-axis and ns × bracket collisions; exact rendered glyph extents not programmatically measured"},
        {"check": "semantic/visual collisions", "finding": "major gridlines only; summary geometry above dots"},
        {"check": "U1 visible metric", "finding": "integer paired bases; percent retained only in audit"},
        {"check": "selected/background counts", "finding": f"4B counts={b_counts}; 4C counts={c_counts}"},
        {"check": "SVG text", "finding": "svg.fonttype=none; text remains editable"},
        {"check": "bbox_inches tight", "finding": "bbox_inches='tight' does not appear"},
    ]
    write_tsv(AUDIT_DIR / "Figure4BC_final_self_audit.tsv", final_self_audit)

    with open(OUT_DIR / "Figure4BC_polished_render_manifest.json", "w", encoding="utf-8") as handle:
        json.dump({
            "selected_n": 49,
            "background_n": 232,
            "visible_u1_metric": "u1_best_WC_pairs + u1_best_GU_pairs",
            "p_value_transform": "ax.transAxes",
            "bracket_transform": "blended x=data, y=axes-fraction",
            "panel_b_canvas_inches": [PANEL_B_WIDTH_IN, PANEL_B_HEIGHT_IN],
            "panel_c_canvas_inches": [PANEL_C_WIDTH_IN, PANEL_C_HEIGHT_IN],
            "dpi": DPI,
            "no_bbox_inches_tight": True,
            "outputs": rendered,
            "contact_sheet": contact_sheet,
        }, handle, indent=2)

    print("SUCCESS: Figure 4B/C polished rerender complete")
    print(f"Output directory: {OUT_DIR.resolve()}")
    print(f"Contact sheet: {contact_sheet}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
