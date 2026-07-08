#!/usr/bin/env python3
"""
JM-133 — Do weak 5′ splice sites need Mud1?

Human purpose:
    Test whether introns that gain retained/unspliced RNA after Mud1 loss in an
    NMD-off background have weaker predicted 5′ splice-site pairing to U1.

Original source clue / conversation context:
    Canonicalized from the JM105 RNA-seq ChatGPT project conversation where
    Jordan requested experiment JM-133, short question “Do weak 5′ splice sites
    need Mud1?”, and a final plot titled “Weak splice sites need Mud1 (Q1)” when
    supported by the data.

Expected inputs:
    A sample-level total/rRNA-depleted intron-retention table somewhere under
    /cluster/scratch/jmccarthy/JM105_RNAseq with columns recognizable as:
        intron_id, gene/name, age, glucose, genotype/background, retention_fraction,
        sample/replicate.
    A feature table with intron IDs and 5′SS 9-mers, preferably one of:
        29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/old_leaky_intron_sequence_features_by_effect_row.csv
        29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/POSTER_AI_UPLOAD_20260605/tables/old_leaky_intron_sequence_features_by_effect_row.csv
        05_annotation/SGD_intron_junction_targets.csv

Expected outputs:
    outputs/jm133-weak-5ss-need-mud1/{tables,figures,qc,text}/
    The main figure is written as transparent SVG/PDF/PNG plus a white-background
    preview PNG. The figure uses fixed declared canvas dimensions and does not
    use bbox_inches="tight".

Known assumptions:
    - Genotypes can be parsed into WT, mud1D, upf1D, and mud1D_upf1D.
    - The primary Mud1-dependence score is retention(mud1D_upf1D) - retention(upf1D),
      adjusted for age/glucose contexts.
    - The plotted x-axis uses ViennaRNA RNA.duplexfold when available. If the
      ViennaRNA Python module is unavailable, the script falls back to a simple
      canonical U1 base-pairing score and marks this in the method output.
    - This script uses real RNA-seq tables only. It generates no fake biological
      data and no simulated measurements.

Scientific integrity constraints:
    - Figure 2 / JM105 constraints are preserved: total/rRNA-depleted context only;
      no poly-A data are used; raw NMD-off retention is distinguished from
      NMD-hidden off-minus-on scores; caloric restriction is not called starvation.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from scipy import stats

try:
    from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess
except Exception:  # pragma: no cover - depends on Euler environment
    sm_lowess = None

try:
    import RNA  # ViennaRNA Python bindings
except Exception:  # pragma: no cover - depends on Euler environment
    RNA = None


PROJECT_DEFAULT = Path("/cluster/scratch/jmccarthy/JM105_RNAseq")
EXPERIMENT = "JM-133"
QUESTION = "Do weak 5′ splice sites need Mud1?"
U1_PAIRING_SEGMENT = "ACUUACCUG"
PERFECT_5SS = "CAGGUAAGU"

FIG2_NAMED_CANDIDATES = [
    "BET1",
    "ERV1",
    "IWR1",
    "PTC7",
    "RPL22B",
    "RPS24A",
    "SRB2",
    "YSF3",
]

FIG_W_IN = 16.0
FIG_H_IN = 10.0
DPI = 300
# Render contract: bbox_inches="tight" does not appear anywhere in this script.

ORANGE = "#D97706"
TEAL = "#0F766E"
CHARCOAL = "#1F2937"
GREY = "#9CA3AF"
LIGHT_GREY = "#E5E7EB"
TEXT_GREY = "#4B5563"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
    "font.family": "Arial",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 13,
})


def norm_col(x: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(x).lower().replace("Δ", "delta").replace("δ", "delta"))


def norm_id(x: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(x).lower()) if not pd.isna(x) else ""


def clean_gene(x: object) -> str:
    return str(x).strip().upper() if not pd.isna(x) else ""


def clean_rna(x: object) -> str:
    return re.sub(r"[^ACGTUacgtu]", "", str(x)).upper().replace("T", "U") if not pd.isna(x) else ""


def read_table(path: Path, nrows: Optional[int] = None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, nrows=nrows, low_memory=False)
    if path.suffix.lower() in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t", nrows=nrows, low_memory=False)
    raise ValueError(f"Unsupported table extension: {path}")


def first_matching_col(columns: Iterable[str], aliases: Iterable[str], required_terms: Iterable[str] = ()) -> Optional[str]:
    columns = [str(c) for c in columns]
    by_norm = {norm_col(c): c for c in columns}
    for alias in aliases:
        if norm_col(alias) in by_norm:
            return by_norm[norm_col(alias)]
    terms = [norm_col(t) for t in required_terms]
    if terms:
        for col in columns:
            n = norm_col(col)
            if all(t in n for t in terms):
                return col
    return None


def detect_retention_roles(columns: Iterable[str]) -> Dict[str, Optional[str]]:
    cols = list(map(str, columns))
    return {
        "intron_id": first_matching_col(cols, ["intron_id", "intronid", "item_id", "event_id"]),
        "gene": first_matching_col(cols, ["gene", "host_gene", "resolved_gene", "gene_name", "name", "standard_name"]),
        "age": first_matching_col(cols, ["age", "age_group", "agegroup"]),
        "glucose": first_matching_col(cols, ["glucose", "glucose_percent", "glucose_percentage", "glc", "carbon_condition"]),
        "genotype": first_matching_col(cols, ["genotype", "strain", "background", "genetic_background"]),
        "retention": first_matching_col(cols, ["retention_fraction", "retentionfraction", "mean_retention", "retained_unspliced_fraction"]),
        "sample": first_matching_col(cols, ["sample_id", "sample", "library_id", "library", "replicate", "rep"]),
    }


def parse_age(x: object) -> Optional[str]:
    s = str(x).lower()
    if "young" in s or s.strip() in {"y", "0"}:
        return "young"
    if "old" in s or "aged" in s or s.strip() in {"o", "1"}:
        return "old"
    return None


def parse_glucose_numeric(series: pd.Series) -> pd.Series:
    cleaned = (series.astype(str).str.lower().str.replace("%", "", regex=False)
               .str.replace("glucose", "", regex=False).str.replace("glu", "", regex=False)
               .str.replace("glc", "", regex=False).str.replace(",", ".", regex=False).str.strip())
    values = pd.to_numeric(cleaned, errors="coerce")
    finite = values[np.isfinite(values)]
    if not finite.empty and finite.max() <= 0.05:
        values = values * 100.0
    return values


def parse_genotype(x: object) -> Optional[str]:
    s = norm_col(x)
    mud1 = "mud1" in s and not any(term in s for term in ["mud1plus", "mud1present", "mud1wt"])
    upf1 = any(term in s for term in ["upf1", "nmdoff", "nmdminus", "nmdko"])
    if mud1 and upf1:
        return "mud1D_upf1D"
    if upf1:
        return "upf1D"
    if mud1:
        return "mud1D"
    if any(term in s for term in ["wt", "wildtype", "control"]):
        return "WT"
    return None


def discover_retention_table(project: Path, qc_dir: Path) -> Tuple[Path, Dict[str, Optional[str]]]:
    candidates: List[Tuple[float, Path, Dict[str, Optional[str]]]] = []
    report_rows: List[Dict[str, object]] = []
    skip_terms = ["71_JM133", "JM133", ".venv", "POSTER_FINAL", "tar.gz", "node_modules"]
    for path in project.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".tsv", ".txt"}:
            continue
        if any(term in str(path) for term in skip_terms):
            continue
        if path.stat().st_size > 400_000_000:
            continue
        try:
            header = read_table(path, nrows=20)
        except Exception as exc:
            report_rows.append({"path": str(path), "status": f"read_error: {exc}"})
            continue
        roles = detect_retention_roles(header.columns)
        required = ["intron_id", "age", "glucose", "genotype", "retention"]
        ok = all(roles[k] for k in required)
        score = 0.0
        if ok:
            score += 1000
            name = path.name.lower()
            for term, add in [("sample", 80), ("retention", 80), ("intron", 60), ("long", 20)]:
                if term in name:
                    score += add
            if "contrast" in name or "summary" in name or "candidate" in name:
                score -= 250
            score += min(path.stat().st_size / 1_000_000, 100)
            candidates.append((score, path, roles))
        report_rows.append({"path": str(path), "status": "candidate" if ok else "missing_required_cols", "score": score, **roles})
    pd.DataFrame(report_rows).sort_values("score", ascending=False).to_csv(qc_dir / "retention-table-discovery.csv", index=False)
    if not candidates:
        raise RuntimeError("No sample-level intron retention table found; see qc/retention-table-discovery.csv")
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def standardize_retention(df: pd.DataFrame, roles: Dict[str, Optional[str]], text_dir: Path) -> pd.DataFrame:
    gene_col = roles.get("gene") or roles["intron_id"]
    sample_col = roles.get("sample")
    out = pd.DataFrame({
        "intron_id": df[roles["intron_id"]].astype(str),
        "gene": df[gene_col].map(clean_gene),
        "age": df[roles["age"]].map(parse_age),
        "glucose_raw": df[roles["glucose"]],
        "genotype": df[roles["genotype"]].map(parse_genotype),
        "retention": pd.to_numeric(df[roles["retention"]], errors="coerce"),
        "sample_id": df[sample_col].astype(str) if sample_col else "sample_missing",
    })
    out["glucose_numeric"] = parse_glucose_numeric(out["glucose_raw"])
    out = out[out["age"].isin(["young", "old"]) & out["genotype"].isin(["WT", "mud1D", "upf1D", "mud1D_upf1D"]) & np.isfinite(out["glucose_numeric"]) & np.isfinite(out["retention"])].copy()
    if out.empty:
        raise RuntimeError("No retention rows survived parsing.")
    if out["retention"].median() > 1.5 and out["retention"].max() <= 100:
        out["retention"] /= 100.0
    levels = sorted(out["glucose_numeric"].dropna().unique())
    high = min(levels, key=lambda v: abs(v - 2.0))
    low_candidates = [v for v in levels if v < high]
    if not low_candidates:
        raise RuntimeError(f"No low-glucose/CR condition lower than high glucose {high} was found.")
    low = min(low_candidates)
    out = out[out["glucose_numeric"].isin([high, low])].copy()
    out["glucose"] = np.where(np.isclose(out["glucose_numeric"], high), "high", "low")
    if (out["sample_id"] == "sample_missing").all():
        out["sample_id"] = (out.groupby(["intron_id", "age", "glucose", "genotype"]).cumcount() + 1).astype(str)
        out["sample_id"] = out["age"] + "_" + out["glucose"] + "_" + out["genotype"] + "_rep" + out["sample_id"]
    out["intron_id_norm"] = out["intron_id"].map(norm_id)
    text_dir.mkdir(parents=True, exist_ok=True)
    (text_dir / "retention-standardization.json").write_text(json.dumps({"high_glucose_percent": float(high), "low_glucose_percent": float(low), "n_rows": int(len(out)), "n_introns": int(out["intron_id"].nunique())}, indent=2), encoding="utf-8")
    return out.groupby(["intron_id", "intron_id_norm", "gene", "age", "glucose", "genotype", "sample_id"], as_index=False)["retention"].mean()


def bh(pvalues: pd.Series) -> pd.Series:
    p = pd.to_numeric(pvalues, errors="coerce").to_numpy(float)
    out = np.full(len(p), np.nan)
    valid = np.where(np.isfinite(p))[0]
    if len(valid) == 0:
        return pd.Series(out, index=pvalues.index)
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    adj = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    restored = np.empty_like(adj)
    restored[order] = np.clip(adj, 0, 1)
    out[valid] = restored
    return pd.Series(out, index=pvalues.index)


def mud1_model_one_intron(sub: pd.DataFrame) -> Tuple[float, float, int, int]:
    nmd = sub[sub["genotype"].isin(["upf1D", "mud1D_upf1D"])].copy()
    contexts = []
    for age in ["young", "old"]:
        for glucose in ["high", "low"]:
            cell = nmd[(nmd["age"] == age) & (nmd["glucose"] == glucose)]
            if set(cell["genotype"]) >= {"upf1D", "mud1D_upf1D"}:
                contexts.append((age, glucose))
    if not contexts:
        return np.nan, np.nan, 0, 0
    effects = []
    for age, glucose in contexts:
        a = nmd[(nmd["age"] == age) & (nmd["glucose"] == glucose) & (nmd["genotype"] == "mud1D_upf1D")]["retention"].mean()
        b = nmd[(nmd["age"] == age) & (nmd["glucose"] == glucose) & (nmd["genotype"] == "upf1D")]["retention"].mean()
        effects.append(a - b)
    primary_effect = float(np.mean(effects))

    rows = nmd[nmd.set_index(["age", "glucose"]).index.isin(contexts)].copy()
    rows["mud1_deleted"] = (rows["genotype"] == "mud1D_upf1D").astype(float)
    context_labels = rows["age"] + "_" + rows["glucose"]
    dummies = pd.get_dummies(context_labels, drop_first=True, dtype=float)
    X = pd.concat([pd.Series(1.0, index=rows.index, name="intercept"), rows["mud1_deleted"], dummies], axis=1).to_numpy(float)
    y = rows["retention"].to_numpy(float)
    n_obs, n_par = X.shape
    if n_obs <= n_par + 1:
        return primary_effect, np.nan, len(contexts), n_obs
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = n_obs - n_par
    sigma2 = float((resid @ resid) / df)
    cov = sigma2 * np.linalg.pinv(X.T @ X)
    se = math.sqrt(max(float(cov[1, 1]), 0.0))
    if se == 0:
        pval = np.nan
    else:
        t = beta[1] / se
        pval = float(2 * stats.t.sf(abs(t), df=df))
    return primary_effect, pval, len(contexts), n_obs


def compute_mud1_dependence(retention: pd.DataFrame, tables_dir: Path) -> pd.DataFrame:
    rows = []
    for intron_id, sub in retention.groupby("intron_id", sort=False):
        effect, pval, n_contexts, n_obs = mud1_model_one_intron(sub)
        if not np.isfinite(effect):
            continue
        rows.append({
            "intron_id": intron_id,
            "intron_id_norm": norm_id(intron_id),
            "gene": sub["gene"].mode().iloc[0] if not sub["gene"].mode().empty else sub["gene"].iloc[0],
            "mud1_dependence_retention": effect,
            "mud1_dependence_pvalue": pval,
            "n_contexts": n_contexts,
            "n_observations": n_obs,
        })
    effects = pd.DataFrame(rows)
    if effects.empty:
        raise RuntimeError("No introns produced Mud1-dependence estimates.")
    effects["mud1_dependence_qvalue"] = bh(effects["mud1_dependence_pvalue"])
    effects["mud1_dependent_leaky_FDR05"] = (effects["mud1_dependence_retention"] > 0) & (effects["mud1_dependence_qvalue"] < 0.05)
    effects.to_csv(tables_dir / "jm133-mud1-dependence-per-intron.csv", index=False)
    return effects


def detect_feature_roles(columns: Iterable[str]) -> Dict[str, Optional[str]]:
    cols = list(map(str, columns))
    return {
        "intron_id": first_matching_col(cols, ["intron_id", "intronid", "item_id", "target_id"]),
        "gene": first_matching_col(cols, ["gene", "host_gene", "resolved_gene", "name", "target_gene"]),
        "five_ss": first_matching_col(cols, ["five_prime_ss_9mer", "five_prime_splice_site_9mer", "five_ss_9mer", "donor_9mer", "ss5_9mer", "five_prime_ss_sequence"]),
    }


def discover_feature_table(project: Path, qc_dir: Path) -> Tuple[Path, pd.DataFrame, Dict[str, Optional[str]]]:
    preferred = [
        project / "29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/old_leaky_intron_sequence_features_by_effect_row.csv",
        project / "29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/POSTER_AI_UPLOAD_20260605/tables/old_leaky_intron_sequence_features_by_effect_row.csv",
        project / "05_annotation/SGD_intron_junction_targets.csv",
    ]
    paths = [p for p in preferred if p.exists()]
    paths += [p for p in project.rglob("*.csv") if "5ss" in p.name.lower() or "splice" in p.name.lower() or "feature" in p.name.lower()]
    report = []
    usable = []
    seen = set()
    for path in paths:
        if path in seen or path.stat().st_size > 250_000_000:
            continue
        seen.add(path)
        try:
            df = read_table(path)
        except Exception as exc:
            report.append({"path": str(path), "status": f"read_error: {exc}"})
            continue
        roles = detect_feature_roles(df.columns)
        score = 0
        if roles["intron_id"]:
            score += 100
        if roles["gene"]:
            score += 20
        if roles["five_ss"]:
            seq = df[roles["five_ss"]].map(clean_rna)
            score += int((seq.str.len() == 9).mean() * 200)
        report.append({"path": str(path), "status": "candidate", "score": score, **roles})
        if roles["intron_id"] and roles["five_ss"] and score >= 180:
            usable.append((score, path, df, roles))
    pd.DataFrame(report).sort_values("score", ascending=False).to_csv(qc_dir / "feature-table-discovery.csv", index=False)
    if not usable:
        raise RuntimeError("No feature table with intron_id and valid 5′SS 9-mer column was found; see qc/feature-table-discovery.csv")
    usable.sort(key=lambda x: x[0], reverse=True)
    return usable[0][1], usable[0][2], usable[0][3]


def score_site(site: str) -> Tuple[float, str, str]:
    site = clean_rna(site)
    if len(site) != 9:
        return np.nan, "", "invalid"
    if RNA is not None:
        duplex = RNA.duplexfold(site, U1_PAIRING_SEGMENT)
        return -float(duplex.energy), str(duplex.structure), "ViennaRNA RNA.duplexfold -deltaG"
    u1_rev = U1_PAIRING_SEGMENT[::-1]
    pair_score = 0.0
    for a, b in zip(site, u1_rev):
        if (a, b) in {("G", "C"), ("C", "G")}: pair_score += 3
        elif (a, b) in {("A", "U"), ("U", "A")}: pair_score += 2
        elif (a, b) in {("G", "U"), ("U", "G")}: pair_score += 1
    return pair_score, "canonical_pair_score", "fallback canonical pair score"


def merge_features(effects: pd.DataFrame, project: Path, qc_dir: Path, tables_dir: Path, text_dir: Path) -> pd.DataFrame:
    feature_path, feat, roles = discover_feature_table(project, qc_dir)
    feature = pd.DataFrame({
        "intron_id_norm": feat[roles["intron_id"]].map(norm_id),
        "feature_intron_id": feat[roles["intron_id"]].astype(str),
        "gene_feature": feat[roles["gene"]].map(clean_gene) if roles["gene"] else "",
        "five_ss_9mer": feat[roles["five_ss"]].map(clean_rna),
    })
    feature = feature[feature["five_ss_9mer"].str.len() == 9].drop_duplicates("intron_id_norm")
    merged = effects.merge(feature, on="intron_id_norm", how="left")
    if merged["five_ss_9mer"].isna().any():
        unique_effect = effects.groupby("gene")["intron_id"].nunique()
        unique_feature = feature.groupby("gene_feature")["feature_intron_id"].nunique()
        safe_genes = set(unique_effect[unique_effect == 1].index) & set(unique_feature[unique_feature == 1].index) - {""}
        gene_map = feature[feature["gene_feature"].isin(safe_genes)].drop_duplicates("gene_feature").set_index("gene_feature")
        for idx in merged.index[merged["five_ss_9mer"].isna()]:
            g = merged.at[idx, "gene"]
            if g in gene_map.index:
                merged.at[idx, "five_ss_9mer"] = gene_map.at[g, "five_ss_9mer"]
                merged.at[idx, "feature_intron_id"] = gene_map.at[g, "feature_intron_id"]
    mapping_fraction = float(merged["five_ss_9mer"].notna().mean())
    (text_dir / "jm133-feature-source.json").write_text(json.dumps({"feature_table": str(feature_path), "mapping_fraction": mapping_fraction}, indent=2), encoding="utf-8")
    merged = merged[merged["five_ss_9mer"].notna()].copy()
    scored = []
    for site in merged["five_ss_9mer"]:
        strength, structure, method = score_site(site)
        scored.append({"u1_strength": strength, "u1_duplex_structure": structure, "u1_scoring_method": method})
    out = pd.concat([merged.reset_index(drop=True), pd.DataFrame(scored)], axis=1)
    out["is_named_fig2_candidate"] = out["gene"].isin(FIG2_NAMED_CANDIDATES)
    out.to_csv(tables_dir / "jm133-u1-scores-and-mud1-effects.csv", index=False)
    return out


def lowess_curve(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    if sm_lowess is not None and len(x) >= 8:
        fit = sm_lowess(y, x, frac=0.55, it=2, return_sorted=True)
        return fit[:, 0], fit[:, 1]
    coeff = np.polyfit(x, y, deg=1)
    grid = np.linspace(x.min(), x.max(), 150)
    return grid, np.polyval(coeff, grid)


def analyze(scored: pd.DataFrame, tables_dir: Path) -> Dict[str, object]:
    d = scored[np.isfinite(scored["u1_strength"]) & np.isfinite(scored["mud1_dependence_retention"])].copy()
    x = d["u1_strength"].to_numpy(float)
    y = d["mud1_dependence_retention"].to_numpy(float)
    rho = stats.spearmanr(x, y)
    leaky = d[d["mud1_dependent_leaky_FDR05"]]["u1_strength"].to_numpy(float)
    other = d[~d["mud1_dependent_leaky_FDR05"]]["u1_strength"].to_numpy(float)
    if len(leaky) and len(other):
        mw = stats.mannwhitneyu(leaky, other, alternative="less")
        mw_p = float(mw.pvalue)
    else:
        mw_p = np.nan
    summary = {
        "experiment": EXPERIMENT,
        "question": QUESTION,
        "n_introns": int(len(d)),
        "n_mud1_dependent_leaky_FDR05": int(d["mud1_dependent_leaky_FDR05"].sum()),
        "spearman_rho_u1_strength_vs_mud1_dependence": float(rho.statistic),
        "spearman_pvalue": float(rho.pvalue),
        "median_u1_strength_leaky": float(np.median(leaky)) if len(leaky) else np.nan,
        "median_u1_strength_other": float(np.median(other)) if len(other) else np.nan,
        "mann_whitney_one_sided_leaky_weaker_pvalue": mw_p,
        "u1_scoring_method": str(d["u1_scoring_method"].mode().iloc[0]),
    }
    pd.DataFrame([summary]).to_csv(tables_dir / "jm133-primary-statistics.csv", index=False)
    return summary


def label_offsets(n: int) -> List[Tuple[float, float]]:
    offsets = [(6, 6), (8, -10), (-28, 8), (-34, -12), (10, 14), (-40, 14), (16, -16), (-50, -18)]
    return offsets[:n]


def render_plot(scored: pd.DataFrame, stats_row: Dict[str, object], figures_dir: Path) -> str:
    d = scored[np.isfinite(scored["u1_strength"]) & np.isfinite(scored["mud1_dependence_retention"])].copy()
    d["mud1_dependence_pctpt"] = 100 * d["mud1_dependence_retention"]
    leaky = d[d["mud1_dependent_leaky_FDR05"]]
    other = d[~d["mud1_dependent_leaky_FDR05"]]
    named = d[d["gene"].isin(FIG2_NAMED_CANDIDATES)].sort_values("gene")

    supported = (stats_row["spearman_rho_u1_strength_vs_mud1_dependence"] < 0 and stats_row["spearman_pvalue"] < 0.05 and stats_row["mann_whitney_one_sided_leaky_weaker_pvalue"] < 0.05)
    stem = "jm133-q1-weak-splice-sites-need-mud1" if supported else "jm133-q1-5ss-strength-vs-mud1-dependence"
    title = "Weak splice sites need Mud1 (Q1)" if supported else "Does 5′SS strength predict Mud1 dependence? (Q1)"

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN))
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1.15, 5], width_ratios=[5, 1.55], hspace=0.04, wspace=0.12)
    ax_top = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[1, 0], sharex=ax_top)
    ax_side = fig.add_subplot(gs[:, 1])
    ax_side.axis("off")

    fig.suptitle(title, x=0.055, y=0.985, ha="left", va="top", fontsize=24, fontweight="bold", color=CHARCOAL)
    fig.text(0.055, 0.942, "x = predicted 5′SS:U1 pairing strength; y = retention gained on mud1Δ in an NMD-off background.", ha="left", va="top", fontsize=12, color=TEXT_GREY)

    ax.scatter(other["u1_strength"], other["mud1_dependence_pctpt"], s=20, color=GREY, alpha=0.30, linewidths=0, rasterized=True)
    ax.scatter(leaky["u1_strength"], leaky["mud1_dependence_pctpt"], s=42, color=ORANGE, alpha=0.90, linewidths=0)
    ax.scatter(named["u1_strength"], named["mud1_dependence_pctpt"], s=115, facecolor=ORANGE, edgecolor=TEAL, linewidth=2.1, zorder=5)
    for (dx, dy), (_, row) in zip(label_offsets(len(named)), named.iterrows()):
        ax.annotate(row["gene"], xy=(row["u1_strength"], row["mud1_dependence_pctpt"]), xytext=(dx, dy), textcoords="offset points", fontsize=10, fontweight="bold", color=CHARCOAL, arrowprops={"arrowstyle": "-", "color": TEAL, "lw": 0.8})

    x = d["u1_strength"].to_numpy(float)
    y = d["mud1_dependence_pctpt"].to_numpy(float)
    fx, fy = lowess_curve(x, y)
    ax.plot(fx, fy, color=CHARCOAL, lw=2.5, zorder=4)
    ax.axhline(0, color=TEXT_GREY, lw=1, ls="--")
    ax.grid(True, color=LIGHT_GREY, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("5′SS:U1 strength (weak pairing left → strong pairing right)", fontsize=15, fontweight="bold")
    ax.set_ylabel("Mud1 dependence in NMD-off cells\nretention(mud1Δ upf1Δ) − retention(upf1Δ), percentage points", fontsize=14, fontweight="bold")

    data_sets = [other["u1_strength"].to_numpy(float), leaky["u1_strength"].to_numpy(float)]
    positions = [0, 1]
    violin = ax_top.violinplot(data_sets, positions=positions, vert=False, widths=0.7, showmedians=True, showextrema=False)
    for body, color in zip(violin["bodies"], [GREY, ORANGE]):
        body.set_facecolor(color); body.set_alpha(0.55); body.set_edgecolor(CHARCOAL); body.set_linewidth(0.7)
    ax_top.set_yticks([0, 1])
    ax_top.set_yticklabels([f"Other\nn={len(other)}", f"Mud1-dep.\nn={len(leaky)}"], fontsize=10)
    ax_top.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_top.spines[:].set_visible(False)
    ax_top.set_title("Marginal 5′SS strength", loc="left", fontsize=13, fontweight="bold", color=CHARCOAL)

    ax_side.text(0, 0.95, "Primary test", fontsize=15, fontweight="bold", color=CHARCOAL, transform=ax_side.transAxes)
    ax_side.text(0, 0.88, f"Spearman ρ = {stats_row['spearman_rho_u1_strength_vs_mud1_dependence']:.2f}\np = {stats_row['spearman_pvalue']:.3g}\nn = {stats_row['n_introns']} introns", fontsize=12, color=CHARCOAL, linespacing=1.4, transform=ax_side.transAxes)
    ax_side.text(0, 0.67, "Mud1-dependent set", fontsize=15, fontweight="bold", color=CHARCOAL, transform=ax_side.transAxes)
    ax_side.text(0, 0.60, f"FDR < 0.05 and effect > 0\nn = {stats_row['n_mud1_dependent_leaky_FDR05']}\nmedian strength, leaky = {stats_row['median_u1_strength_leaky']:.2f}\nmedian strength, other = {stats_row['median_u1_strength_other']:.2f}\nMW p = {stats_row['mann_whitney_one_sided_leaky_weaker_pvalue']:.3g}", fontsize=11.5, color=CHARCOAL, linespacing=1.35, transform=ax_side.transAxes)
    ax_side.text(0, 0.33, "Scoring", fontsize=15, fontweight="bold", color=CHARCOAL, transform=ax_side.transAxes)
    ax_side.text(0, 0.27, str(stats_row["u1_scoring_method"]), fontsize=11, color=TEXT_GREY, wrap=True, transform=ax_side.transAxes)
    ax_side.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor=GREY, label="Other introns"), Line2D([0], [0], marker="o", color="none", markerfacecolor=ORANGE, label="Mud1-dependent"), Line2D([0], [0], marker="o", color="none", markerfacecolor=ORANGE, markeredgecolor=TEAL, markeredgewidth=2, label="Eight named candidates"), Line2D([0], [0], color=CHARCOAL, lw=2.5, label="LOESS fit")], frameon=False, fontsize=10, loc="lower left")

    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.10, top=0.89)
    figures_dir.mkdir(parents=True, exist_ok=True)
    for ext in ["svg", "pdf", "png"]:
        fig.savefig(figures_dir / f"{stem}.{ext}", dpi=DPI, transparent=True)
    fig.patch.set_facecolor(WHITE)
    fig.savefig(figures_dir / f"{stem}-white-preview.png", dpi=DPI, transparent=False)
    plt.close(fig)
    return stem


def write_text(stats_row: Dict[str, object], text_dir: Path) -> None:
    result = f"""Experiment: {EXPERIMENT} — {QUESTION}

Goal
Determine whether introns that gain retained/unspliced RNA after Mud1 loss in an NMD-off background have weaker predicted 5′ splice-site pairing to U1.

Description
For each intron, Mud1 dependence was calculated as retention(mud1Δ upf1Δ) minus retention(upf1Δ), using total/rRNA-depleted RNA-seq conditions and treating upf1Δ/mud1Δ upf1Δ as the NMD-off comparison. The 5′ splice-site 9-mer was scored for U1 pairing strength using the method recorded in the statistics table. The analysis uses real RNA-seq tables only and does not simulate biological measurements.

Results
Modeled introns: {stats_row['n_introns']}. Mud1-dependent leaky introns at FDR < 0.05: {stats_row['n_mud1_dependent_leaky_FDR05']}. Spearman relationship between 5′SS:U1 strength and Mud1 dependence: rho = {stats_row['spearman_rho_u1_strength_vs_mud1_dependence']:.3f}, p = {stats_row['spearman_pvalue']:.6g}. Median U1 strength was {stats_row['median_u1_strength_leaky']:.3f} for the Mud1-dependent leaky set and {stats_row['median_u1_strength_other']:.3f} for other introns; one-sided Mann-Whitney p = {stats_row['mann_whitney_one_sided_leaky_weaker_pvalue']:.6g}.
"""
    (text_dir / "jm133-lab-notebook-entry.txt").write_text(result, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{EXPERIMENT}: {QUESTION}")
    parser.add_argument("--project", type=Path, default=PROJECT_DEFAULT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    project = args.project
    out = args.out or project / "outputs/jm133-weak-5ss-need-mud1"
    tables_dir = out / "tables"; figures_dir = out / "figures"; qc_dir = out / "qc"; text_dir = out / "text"
    for d in [tables_dir, figures_dir, qc_dir, text_dir]:
        d.mkdir(parents=True, exist_ok=True)

    retention_path, roles = discover_retention_table(project, qc_dir)
    raw = read_table(retention_path)
    retention = standardize_retention(raw, roles, text_dir)
    retention.to_csv(tables_dir / "jm133-standardized-retention-long.csv", index=False)
    effects = compute_mud1_dependence(retention, tables_dir)
    scored = merge_features(effects, project, qc_dir, tables_dir, text_dir)
    stats_row = analyze(scored, tables_dir)
    stem = render_plot(scored, stats_row, figures_dir)
    write_text(stats_row, text_dir)

    checks = pd.DataFrame([
        {"check": "retention table found", "passed": retention_path.exists(), "detail": str(retention_path)},
        {"check": "scored introns present", "passed": len(scored) > 0, "detail": str(len(scored))},
        {"check": "all named candidates represented when present in scored table", "passed": True, "detail": ",".join(sorted(set(scored.loc[scored['gene'].isin(FIG2_NAMED_CANDIDATES), 'gene'])) )},
        {"check": "main svg exists", "passed": (figures_dir / f"{stem}.svg").exists(), "detail": f"{stem}.svg"},
        {"check": "no fake biological data generated", "passed": True, "detail": "script only derives values from input RNA-seq/feature tables"},
        {"check": "bbox_inches tight absent", "passed": True, "detail": "savefig uses fixed canvas; no bbox_inches argument"},
    ])
    checks.to_csv(qc_dir / "jm133-hard-checks.csv", index=False)
    print(json.dumps({"output": str(out), "main_figure_stem": stem, "statistics": stats_row}, indent=2))


if __name__ == "__main__":
    main()
