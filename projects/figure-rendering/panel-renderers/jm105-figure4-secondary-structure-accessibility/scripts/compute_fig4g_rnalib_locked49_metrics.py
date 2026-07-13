#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM105 Figure 4G metric builder.

Builds the locked-49 Figure 4G secondary-structure/accessibility metric table.
This script stores the computational/provenance layer, not the final visual layer.

Scope fence:
- Uses total/rRNA-depleted JM105-derived Figure 2/Figure 4 tables only.
- Does not touch poly-A, P-versus-T, mRNA-like, or P−T construct logic.

Definitions echoed here for drift control:
- NMD_hidden = IR(upf1Δ) − IR(UPF1+)
- candidate_score = min(aging_effect, CR_suppression)
- Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression); not computed here.

Method caveat:
- This uses Python ViennaRNA/RNAlib RNA.fold and derives an MFE-dot-bracket
  accessibility proxy. It is not RNAplfold ensemble accessibility.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

try:
    import RNA
except Exception as exc:
    raise RuntimeError(
        "Python ViennaRNA/RNAlib binding is not importable. The Euler runner should install "
        "the ViennaRNA Python package into vendor_py before this script runs. "
        f"Import error: {repr(exc)}"
    )

PROJECT_ROOT = Path("/cluster/scratch/jmccarthy/JM105_RNAseq")
SEARCH_ROOTS = [
    Path("/cluster/scratch/jmccarthy/JM105_RNAseq"),
    Path("/cluster/scratch/jmccarthy"),
    Path("/cluster/home/jmccarthy"),
]

OUT_DIR = Path("out")
AUDIT_DIR = OUT_DIR / "audits"
DATA_DIR = OUT_DIR / "derived_data"

SELECTED_SOURCE = PROJECT_ROOT / "Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V1_20260703_110602/01_LOCKED_CANDIDATES_WITH_RECOMPUTED_SCORE.tsv"
BACKGROUND_SOURCE = PROJECT_ROOT / "Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V2_20260703_111531/05B_CLEAN_SPLICEOSOMAL_BACKGROUND.tsv"

FIG2_CANDIDATE_PATHS = [
    PROJECT_ROOT / "Figure2_stage1_audit_20260630_145204/Figure_2_candidate_metrics_all.tsv",
    PROJECT_ROOT / "Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_metrics_all.tsv",
    PROJECT_ROOT / "Figure2_stage1_audit_20260630_145204/Figure_2_panel_data_A.tsv",
    PROJECT_ROOT / "Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_panel_data_A.tsv",
]

ARCHITECTURE_PRIORITIES = [
    PROJECT_ROOT / "Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv",
    PROJECT_ROOT / "Figure4_render_v5_FIX1_FIND_DERIVED_INPUTS_20260703_102648/derived_data/Figure4_v5_sequence_architecture_features.tsv",
]

ID_COLS = ["join_key", "audit_intron_key", "intron_id_std", "intron_id", "intron_label", "feature_key"]
DISPLAY_COLS = ["display_gene", "gene_label", "gene", "standard_gene_name", "common_name", "orf", "systematic_gene"]
SYSTEMATIC_COLS = ["systematic_gene", "orf", "systematic_name", "systematic_orf"]
BOOL_COLS = [
    "pass_annotation_gate",
    "pass_required_conditions_gate",
    "pass_count_gate",
    "pass_floor_gate",
    "pass_age_gate",
    "pass_cr_gate",
    "pass_old2_nmd_sensitive_gate",
    "candidate_passed",
]
BP_POS_COLS = ["bp_position", "branchpoint_position", "bp_index", "branchpoint_index", "bp_from_5ss", "branchpoint_from_5ss"]
BP_DIST_COLS = ["bp_to_3ss_distance_nt", "bp_to_3ss_distance", "branchpoint_to_3ss_distance", "bp_3ss_distance"]
LENGTH_COLS = ["intron_length_nt_computed", "intron_length_nt", "intron_length", "length_nt", "length"]

CHROM_SYNONYMS = {
    "chrI": ["chrI", "I", "chromosomeI", "NC_001133.9", "NC_001133"],
    "chrII": ["chrII", "II", "chromosomeII", "NC_001134.8", "NC_001134"],
    "chrIII": ["chrIII", "III", "chromosomeIII", "NC_001135.5", "NC_001135"],
    "chrIV": ["chrIV", "IV", "chromosomeIV", "NC_001136.10", "NC_001136"],
    "chrV": ["chrV", "V", "chromosomeV", "NC_001137.3", "NC_001137"],
    "chrVI": ["chrVI", "VI", "chromosomeVI", "NC_001138.5", "NC_001138"],
    "chrVII": ["chrVII", "VII", "chromosomeVII", "NC_001139.9", "NC_001139"],
    "chrVIII": ["chrVIII", "VIII", "chromosomeVIII", "NC_001140.6", "NC_001140"],
    "chrIX": ["chrIX", "IX", "chromosomeIX", "NC_001141.2", "NC_001141"],
    "chrX": ["chrX", "X", "chromosomeX", "NC_001142.9", "NC_001142"],
    "chrXI": ["chrXI", "XI", "chromosomeXI", "NC_001143.9", "NC_001143"],
    "chrXII": ["chrXII", "XII", "chromosomeXII", "NC_001144.5", "NC_001144"],
    "chrXIII": ["chrXIII", "XIII", "chromosomeXIII", "NC_001145.3", "NC_001145"],
    "chrXIV": ["chrXIV", "XIV", "chromosomeXIV", "NC_001146.8", "NC_001146"],
    "chrXV": ["chrXV", "XV", "chromosomeXV", "NC_001147.6", "NC_001147"],
    "chrXVI": ["chrXVI", "XVI", "chromosomeXVI", "NC_001148.4", "NC_001148"],
    "chrM": ["chrM", "Mito", "Mitochondrion", "mitochondrion", "NC_001224.1", "NC_001224"],
}

METRIC_KEYS = ["five_ss_access", "bp_access", "three_ss_access", "occlusion_score", "mfe_per_nt"]


def ensure_dirs() -> None:
    for path in [OUT_DIR, AUDIT_DIR, DATA_DIR]:
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


def open_text(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "rt", encoding="utf-8", errors="replace")


def guess_sep(path: Path) -> str:
    with open_text(path) as handle:
        first = handle.readline()
    return "\t" if first.count("\t") >= first.count(",") else ","


def read_table(path: Path, usecols: Optional[List[str]] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    return pd.read_csv(path, sep=guess_sep(path), usecols=usecols, nrows=nrows, low_memory=False)


def normalize_key(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower().replace("−", "-")
    return re.sub(r"\s+", "", text)


def normalize_name(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower().replace("−", "-")
    return re.sub(r"[^a-z0-9]+", "", text)


def truthy(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "pass", "passed"}


def clean_rna(value: object) -> str:
    text = str(value).upper().replace("T", "U")
    return re.sub(r"[^ACGUN]", "", text)


def clean_dna(value: object) -> str:
    text = str(value).upper().replace("U", "T")
    return re.sub(r"[^ACGTN]", "", text)


def choose_column(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    lower = {col.lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def first_value(row: pd.Series, columns: Iterable[str]) -> str:
    for col in columns:
        if col in row and pd.notna(row[col]):
            text = str(row[col]).strip()
            if text and text.lower() not in {"nan", "na", "none", "null"}:
                return text
    return ""


def revcomp(seq: str) -> str:
    table = str.maketrans("ACGTUNacgtun", "TGCAANtgcaan")
    return seq.translate(table)[::-1].upper()


def row_id_keys(row: pd.Series) -> List[str]:
    keys: List[str] = []
    for col in ID_COLS + SYSTEMATIC_COLS + DISPLAY_COLS:
        if col in row and pd.notna(row[col]):
            value = str(row[col]).strip()
            if value and value.lower() not in {"nan", "na", "none", "null"}:
                keys.extend([normalize_key(value), normalize_name(value)])
    return sorted(set([key for key in keys if key]))


def preferred_join_key(row: pd.Series) -> str:
    for col in ID_COLS:
        if col in row and pd.notna(row[col]):
            value = normalize_key(row[col])
            if value:
                return value
    return normalize_key(first_value(row, SYSTEMATIC_COLS + DISPLAY_COLS))


def pick_fig2_metrics() -> Path:
    for path in FIG2_CANDIDATE_PATHS:
        if path.exists():
            return path
    found = sorted(PROJECT_ROOT.rglob("Figure_2_candidate_metrics_all.tsv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not found:
        raise RuntimeError("No Figure_2_candidate_metrics_all.tsv found under JM105 root.")
    return found[0]


def make_metric_index(metrics: pd.DataFrame) -> Dict[str, List[int]]:
    index: Dict[str, List[int]] = {}
    for idx, row in metrics.iterrows():
        for key in row_id_keys(row):
            index.setdefault(key, []).append(idx)
    return index


def match_metric_row(row: pd.Series, metrics: pd.DataFrame, metric_index: Dict[str, List[int]]) -> Tuple[Optional[pd.Series], str]:
    preferred = preferred_join_key(row)
    if preferred in metric_index and len(metric_index[preferred]) == 1:
        return metrics.loc[metric_index[preferred][0]], "preferred_key_unique"
    for key in row_id_keys(row):
        hits = metric_index.get(key, [])
        if len(hits) == 1:
            return metrics.loc[hits[0]], f"unique_key:{key}"
    for key in row_id_keys(row):
        hits = metric_index.get(key, [])
        if len(hits) > 1:
            return metrics.loc[hits[0]], f"ambiguous_key_first_hit:{key}:n={len(hits)}"
    return None, "no_metric_match"


def load_locked_universe(fig2_metrics: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object], List[Dict[str, object]]]:
    if not SELECTED_SOURCE.exists() or not BACKGROUND_SOURCE.exists():
        raise RuntimeError("Locked Figure 4 selected/background source files are missing.")
    selected_raw = read_table(SELECTED_SOURCE)
    background_raw = read_table(BACKGROUND_SOURCE)
    if len(selected_raw) != 49:
        raise RuntimeError(f"Locked selected source must be n=49; found {len(selected_raw)}")
    if len(background_raw) != 232:
        raise RuntimeError(f"Locked background source must be n=232; found {len(background_raw)}")

    metrics = fig2_metrics.copy()
    for col in BOOL_COLS:
        if col in metrics.columns:
            metrics[col] = metrics[col].map(truthy)
    metric_index = make_metric_index(metrics)

    rows: List[Dict[str, object]] = []
    audit: List[Dict[str, object]] = []
    for locked_source, raw_df, locked_group in [
        ("locked_selected", selected_raw, "selected"),
        ("locked_background", background_raw, "background_pool"),
    ]:
        for source_idx, raw_row in raw_df.iterrows():
            raw_row = raw_row.copy()
            metric_row, method = match_metric_row(raw_row, metrics, metric_index)
            display_gene = first_value(raw_row, DISPLAY_COLS)
            systematic_gene = first_value(raw_row, SYSTEMATIC_COLS)
            intron_id_std = first_value(raw_row, ID_COLS)
            join_key = preferred_join_key(raw_row)
            pass_age_gate = False
            aging_effect = np.nan
            cr_suppression = np.nan
            metric_intron_id = ""
            metric_candidate_passed = ""
            if metric_row is not None:
                pass_age_gate = truthy(metric_row.get("pass_age_gate", False))
                aging_effect = pd.to_numeric(pd.Series([metric_row.get("aging_effect", np.nan)]), errors="coerce").iloc[0]
                cr_suppression = pd.to_numeric(pd.Series([metric_row.get("CR_suppression", np.nan)]), errors="coerce").iloc[0]
                metric_intron_id = first_value(metric_row, ID_COLS)
                metric_candidate_passed = metric_row.get("candidate_passed", "")
                display_gene = display_gene or first_value(metric_row, DISPLAY_COLS)
                systematic_gene = systematic_gene or first_value(metric_row, SYSTEMATIC_COLS)
                intron_id_std = intron_id_std or first_value(metric_row, ID_COLS)
            final_group = "selected" if locked_group == "selected" else ("aging_only" if pass_age_gate else "background")
            candidate_score = min(float(aging_effect), float(cr_suppression)) if pd.notna(aging_effect) and pd.notna(cr_suppression) else np.nan
            row = {
                "locked_source": locked_source,
                "locked_source_idx": int(source_idx),
                "join_key": join_key,
                "intron_id_std": intron_id_std,
                "display_gene": display_gene,
                "systematic_gene": systematic_gene,
                "group": final_group,
                "locked_group": locked_group,
                "pass_age_gate_from_fig2": pass_age_gate,
                "aging_effect": aging_effect,
                "CR_suppression": cr_suppression,
                "candidate_score": candidate_score,
                "metric_match_method": method,
                "metric_intron_id": metric_intron_id,
                "metric_candidate_passed_broad_fig2": metric_candidate_passed,
            }
            rows.append(row)
            audit.append(row.copy())
    out = pd.DataFrame(rows)
    counts = out["group"].value_counts().to_dict()
    summary = {
        "universe_spec": "locked_Figure4_selected49_background232_with_Figure2_pass_age_annotation",
        "total_n": int(out.shape[0]),
        "background_n": int(counts.get("background", 0)),
        "aging_only_n": int(counts.get("aging_only", 0)),
        "selected_n": int(counts.get("selected", 0)),
        "fig2_metric_unmatched_rows": int(sum(1 for row in audit if row["metric_match_method"] == "no_metric_match")),
    }
    if summary["selected_n"] != 49 or summary["background_n"] <= 0 or summary["aging_only_n"] <= 0:
        raise RuntimeError(f"Invalid locked Figure 4 group summary: {summary}")
    if summary["fig2_metric_unmatched_rows"] > 0:
        raise RuntimeError(f"Locked rows unmatched to Figure 2 metrics: {summary['fig2_metric_unmatched_rows']}")
    return out, summary, audit


def table_header(path: Path) -> Optional[List[str]]:
    try:
        return list(read_table(path, nrows=0).columns)
    except Exception:
        return None


def scan_table_paths() -> List[Path]:
    paths: List[Path] = [p for p in ARCHITECTURE_PRIORITIES if p.exists()]
    for root in SEARCH_ROOTS:
        if root.exists():
            paths.extend(root.rglob("*.tsv"))
            paths.extend(root.rglob("*.csv"))
    seen = set()
    out: List[Path] = []
    for path in paths:
        text = str(path)
        if text not in seen:
            seen.add(text)
            out.append(path)
    return out


def score_architecture_source(path: Path, columns: List[str]) -> Tuple[int, Dict[str, Optional[str]]]:
    id_col = choose_column(columns, ID_COLS)
    bp_pos_col = choose_column(columns, BP_POS_COLS)
    bp_dist_col = choose_column(columns, BP_DIST_COLS)
    length_col = choose_column(columns, LENGTH_COLS)
    score = 0
    if id_col:
        score += 50
    if bp_pos_col:
        score += 60
    if bp_dist_col:
        score += 50
    if length_col:
        score += 20
    for token in ["architecture", "branch", "bp", "panel_c", "figure4"]:
        if token in str(path).lower():
            score += 5
    if not id_col or (not bp_pos_col and not bp_dist_col):
        score = -1
    return score, {"id_col": id_col, "bp_pos_col": bp_pos_col, "bp_dist_col": bp_dist_col, "length_col": length_col}


def discover_architecture_source() -> Tuple[Path, Dict[str, Optional[str]]]:
    candidates: List[Dict[str, object]] = []
    for path in scan_table_paths():
        columns = table_header(path)
        if columns is None:
            continue
        score, mapping = score_architecture_source(path, columns)
        if score >= 0:
            candidates.append({"path": str(path), "score": score, "columns": "|".join(columns), **mapping})
    candidates.sort(key=lambda row: int(row["score"]), reverse=True)
    write_tsv(AUDIT_DIR / "Figure4G_architecture_source_candidates.tsv", candidates[:200])
    if not candidates:
        raise RuntimeError("No architecture source with intron ID and branchpoint position/distance was found.")
    chosen = candidates[0]
    mapping = {"id_col": chosen["id_col"], "bp_pos_col": chosen.get("bp_pos_col") or None, "bp_dist_col": chosen.get("bp_dist_col") or None, "length_col": chosen.get("length_col") or None}
    return Path(str(chosen["path"])), mapping


def prepare_architecture_table(path: Path, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
    cols = [mapping["id_col"]]
    for key in ["bp_pos_col", "bp_dist_col", "length_col"]:
        if mapping.get(key):
            cols.append(str(mapping[key]))
    raw = read_table(path, usecols=list(dict.fromkeys(cols)))
    out = pd.DataFrame({"join_key": raw[str(mapping["id_col"])].map(normalize_key)})
    out["bp_pos"] = pd.to_numeric(raw[mapping["bp_pos_col"]], errors="coerce") if mapping.get("bp_pos_col") else np.nan
    out["bp_to_3ss_distance"] = pd.to_numeric(raw[mapping["bp_dist_col"]], errors="coerce") if mapping.get("bp_dist_col") else np.nan
    out["intron_length_from_arch"] = pd.to_numeric(raw[mapping["length_col"]], errors="coerce") if mapping.get("length_col") else np.nan
    return out.loc[out["join_key"] != ""].drop_duplicates("join_key", keep="first")


def file_looks_like_fasta(path: Path) -> bool:
    name = path.name.lower()
    if any(token in name for token in ["fastq", ".fq", "reads", "adapter", "trimmed"]):
        return False
    return name.endswith((".fa", ".fasta", ".fna", ".fas", ".fa.gz", ".fasta.gz", ".fna.gz"))


def file_looks_like_annotation(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".gff", ".gff3", ".gtf", ".gff.gz", ".gff3.gz", ".gtf.gz"))


def discover_reference_files() -> Tuple[Path, Path]:
    fasta_candidates: List[Dict[str, object]] = []
    annotation_candidates: List[Dict[str, object]] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                size = path.stat().st_size
            except Exception:
                continue
            if size <= 0:
                continue
            lower = str(path).lower()
            score = sum(10 for token in ["saccharomyces", "s_cerevisiae", "cerevisiae", "r64", "sgd", "reference"] if token in lower)
            if file_looks_like_fasta(path):
                fasta_candidates.append({"path": str(path), "score": score + (20 if size > 1_000_000 else 0), "size": size})
            elif file_looks_like_annotation(path):
                annotation_candidates.append({"path": str(path), "score": score + (10 if size > 100_000 else 0), "size": size})
    fasta_candidates.sort(key=lambda row: (int(row["score"]), int(row["size"])), reverse=True)
    annotation_candidates.sort(key=lambda row: (int(row["score"]), int(row["size"])), reverse=True)
    write_tsv(AUDIT_DIR / "Figure4G_fasta_candidates.tsv", fasta_candidates[:200])
    write_tsv(AUDIT_DIR / "Figure4G_annotation_candidates.tsv", annotation_candidates[:200])
    if not fasta_candidates:
        raise RuntimeError("No genome FASTA candidate found under JM105 scratch/home search roots.")
    if not annotation_candidates:
        raise RuntimeError("No GFF/GTF annotation candidate found under JM105 scratch/home search roots.")
    return Path(str(fasta_candidates[0]["path"])), Path(str(annotation_candidates[0]["path"]))


def read_fasta(path: Path) -> Dict[str, str]:
    sequences: Dict[str, str] = {}
    current: Optional[str] = None
    chunks: List[str] = []
    with open_text(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current is not None:
                    sequences[current] = "".join(chunks).upper()
                current = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(clean_dna(line))
    if current is not None:
        sequences[current] = "".join(chunks).upper()
    if not sequences:
        raise RuntimeError(f"No sequences read from FASTA: {path}")
    return sequences


def chrom_alias_map(fasta: Dict[str, str]) -> Dict[str, str]:
    alias: Dict[str, str] = {}
    for key in fasta:
        alias[normalize_name(key)] = key
        alias[normalize_key(key)] = key
        for canon, variants in CHROM_SYNONYMS.items():
            names = [canon] + variants
            if normalize_name(key) in [normalize_name(v) for v in names] or normalize_key(key) in [normalize_key(v) for v in names]:
                for variant in names:
                    alias[normalize_name(variant)] = key
                    alias[normalize_key(variant)] = key
    return alias


def parse_gff_attributes(text: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    if "=" in text:
        for part in text.split(";"):
            if "=" in part:
                key, value = part.split("=", 1)
                attrs[key.strip()] = value.strip()
    else:
        for part in text.split(";"):
            bits = part.strip().split(None, 1)
            if len(bits) == 2:
                attrs[bits[0].strip()] = bits[1].strip().strip('"')
    return attrs


def build_annotation_index(path: Path) -> Tuple[List[Dict[str, object]], Dict[str, List[int]]]:
    records: List[Dict[str, object]] = []
    index: Dict[str, List[int]] = {}
    with open_text(path) as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9:
                continue
            chrom, source, feature_type, start, end, score, strand, phase, attr_text = fields[:9]
            attr_blob = " ".join([feature_type, attr_text]).lower()
            if "intron" not in attr_blob:
                continue
            try:
                start_i, end_i = int(start), int(end)
            except Exception:
                continue
            attrs = parse_gff_attributes(attr_text)
            key_values = [feature_type, chrom, attr_text] + list(attrs.keys()) + list(attrs.values())
            keys = sorted(set([k for value in key_values for k in [normalize_name(value), normalize_key(value)] if k]))
            record = {"chrom": chrom, "start": start_i, "end": end_i, "strand": strand if strand in ["+", "-"] else "+", "feature_type": feature_type, "attributes": attr_text, "keys": keys}
            idx = len(records)
            records.append(record)
            for key in keys:
                index.setdefault(key, []).append(idx)
    if not records:
        raise RuntimeError(f"No intron-like annotation records found in {path}")
    return records, index


def parse_coordinate_from_intron_id(text: object) -> Optional[Tuple[str, int, int, str]]:
    if pd.isna(text):
        return None
    s = str(text)
    patterns = [
        r"(chr[ivx]+|chrm|[ivx]+|nc_\d+\.\d+|nc_\d+)[:_](\d+)[:_-](\d+)[:_]?([+-])?",
        r"(chr[ivx]+|chrm|[ivx]+|nc_\d+\.\d+|nc_\d+).+?(\d+).+?(\d+).+?([+-])",
    ]
    for pattern in patterns:
        match = re.search(pattern, s, flags=re.IGNORECASE)
        if match:
            chrom, start, end = match.group(1), int(match.group(2)), int(match.group(3))
            strand = match.group(4) if match.lastindex and match.group(4) in ["+", "-"] else "+"
            if start > end:
                start, end = end, start
            return chrom, start, end, strand
    return None


def candidate_keys_for_annotation(row: pd.Series) -> List[str]:
    values = [row.get("intron_id_std", ""), row.get("join_key", ""), row.get("display_gene", ""), row.get("systematic_gene", "")]
    keys = [key for value in values if pd.notna(value) for key in [normalize_name(value), normalize_key(value)] if key]
    return sorted(set(keys))


def match_annotation(row: pd.Series, records: List[Dict[str, object]], index: Dict[str, List[int]]) -> Optional[Dict[str, object]]:
    coord = parse_coordinate_from_intron_id(row.get("intron_id_std", "")) or parse_coordinate_from_intron_id(row.get("join_key", ""))
    if coord is not None:
        chrom, start, end, strand = coord
        return {"chrom": chrom, "start": start, "end": end, "strand": strand, "feature_type": "parsed_from_id", "attributes": str(row.get("intron_id_std", row.get("join_key", ""))), "match_method": "coordinate_parse_from_id"}
    candidate_indices: List[int] = []
    for key in candidate_keys_for_annotation(row):
        candidate_indices.extend(index.get(key, []))
    if not candidate_indices:
        return None
    counts: Dict[int, int] = {}
    for idx in candidate_indices:
        counts[idx] = counts.get(idx, 0) + 1
    best_idx, score = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0]
    out = dict(records[best_idx])
    out["match_method"] = f"annotation_key_overlap_score_{score}"
    return out


def extract_sequence(fasta: Dict[str, str], alias: Dict[str, str], chrom: str, start: int, end: int, strand: str) -> Optional[str]:
    chrom_key = alias.get(normalize_name(chrom)) or alias.get(normalize_key(chrom)) or (chrom if chrom in fasta else None)
    if chrom_key is None:
        return None
    seq = fasta[chrom_key]
    start_i, end_i = max(1, int(start)), min(len(seq), int(end))
    if end_i < start_i:
        return None
    out = seq[start_i - 1:end_i]
    if strand == "-":
        out = revcomp(out)
    return out.upper()


def parse_bp_center(row: pd.Series, seq_len: int) -> Optional[int]:
    bp_pos = row.get("bp_pos", np.nan)
    bp_dist = row.get("bp_to_3ss_distance", np.nan)
    if pd.notna(bp_pos):
        try:
            pos = int(round(float(bp_pos)))
            if 1 <= pos <= seq_len:
                return pos
        except Exception:
            pass
    if pd.notna(bp_dist):
        try:
            dist = int(round(float(bp_dist)))
            pos = seq_len - dist
            if 1 <= pos <= seq_len:
                return pos
        except Exception:
            pass
    return None


def mean_window(values: np.ndarray, start_1based: int, end_1based: int) -> float:
    n = len(values)
    start = max(1, start_1based)
    end = min(n, end_1based)
    if end < start:
        return float("nan")
    return float(np.mean(values[start - 1:end]))


def rnalib_metrics(seq: str, bp_center: int) -> Dict[str, object]:
    rna_seq = clean_rna(seq)
    if len(rna_seq) < 12:
        raise RuntimeError("sequence shorter than 12 nt after cleaning")
    structure, mfe = RNA.fold(rna_seq)
    unpaired = np.array([1.0 if char == "." else 0.0 for char in structure], dtype=float)
    n = len(rna_seq)
    five_ss = mean_window(unpaired, 1, min(8, n))
    bp = mean_window(unpaired, bp_center - 4, bp_center + 4)
    three_ss = mean_window(unpaired, max(1, n - 10), n)
    access = [value for value in [five_ss, bp, three_ss] if math.isfinite(value)]
    occlusion = float(np.mean([1.0 - value for value in access])) if access else float("nan")
    return {
        "sequence_used": rna_seq,
        "sequence_length_used": n,
        "bp_center_used": bp_center,
        "mfe_structure": structure,
        "mfe": float(mfe),
        "mfe_per_nt": float(mfe / n),
        "five_ss_access": five_ss,
        "bp_access": bp,
        "three_ss_access": three_ss,
        "occlusion_score": occlusion,
        "structure_engine": "ViennaRNA Python RNAlib RNA.fold MFE-derived accessibility proxy",
    }


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


def bh_adjust(pvals: List[float]) -> List[float]:
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted_ranked = np.empty(len(p), dtype=float)
    running = 1.0
    for idx in range(len(p) - 1, -1, -1):
        running = min(running, ranked[idx] * len(p) / (idx + 1))
        adjusted_ranked[idx] = min(running, 1.0)
    adjusted = np.empty(len(p), dtype=float)
    adjusted[order] = adjusted_ranked
    return adjusted.tolist()


def compute_stats(metric_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    contrasts = [("A/bg", "aging_only", "background"), ("M/A", "selected", "aging_only")]
    for contrast, g1, g2 in contrasts:
        for metric in METRIC_KEYS:
            x = pd.to_numeric(metric_df.loc[metric_df["group"] == g1, metric], errors="coerce").to_numpy()
            y = pd.to_numeric(metric_df.loc[metric_df["group"] == g2, metric], errors="coerce").to_numpy()
            effect, pval, u = rank_biserial(x, y)
            rows.append({
                "contrast_label": contrast,
                "group_1": g1,
                "group_2": g2,
                "metric_key": metric,
                "n_group_1": int(np.isfinite(x).sum()),
                "n_group_2": int(np.isfinite(y).sum()),
                "median_group_1": float(np.nanmedian(x)),
                "median_group_2": float(np.nanmedian(y)),
                "rank_biserial_effect_size": effect,
                "mannwhitney_u": u,
                "p_value": pval,
            })
    stats = pd.DataFrame(rows)
    stats["q_value"] = bh_adjust(stats["p_value"].tolist())
    return stats


def main() -> None:
    ensure_dirs()
    fig2_path = pick_fig2_metrics()
    fig2 = read_table(fig2_path)
    locked_universe, group_summary, match_audit = load_locked_universe(fig2)
    write_tsv(AUDIT_DIR / "Figure4G_locked_metric_match_audit.tsv", match_audit)

    architecture_path, architecture_map = discover_architecture_source()
    architecture_df = prepare_architecture_table(architecture_path, architecture_map)
    locked_universe["join_key"] = locked_universe["join_key"].map(normalize_key)
    merged = locked_universe.merge(architecture_df, how="left", on="join_key")

    fasta_path, annotation_path = discover_reference_files()
    fasta = read_fasta(fasta_path)
    alias = chrom_alias_map(fasta)
    annotation_records, annotation_index = build_annotation_index(annotation_path)

    metric_records: List[Dict[str, object]] = []
    failure_records: List[Dict[str, object]] = []
    extraction_records: List[Dict[str, object]] = []

    for _, row in merged.iterrows():
        ann = match_annotation(row, annotation_records, annotation_index)
        if ann is None:
            failure_records.append({"join_key": row.get("join_key", ""), "intron_id_std": row.get("intron_id_std", ""), "display_gene": row.get("display_gene", ""), "group": row.get("group", ""), "reason": "no_annotation_or_coordinate_match"})
            continue
        seq = extract_sequence(fasta, alias, str(ann["chrom"]), int(ann["start"]), int(ann["end"]), str(ann["strand"]))
        if seq is None:
            failure_records.append({"join_key": row.get("join_key", ""), "intron_id_std": row.get("intron_id_std", ""), "display_gene": row.get("display_gene", ""), "group": row.get("group", ""), "reason": f"sequence_extraction_failed_chrom_{ann['chrom']}"})
            continue
        bp_center = parse_bp_center(row, len(seq))
        if bp_center is None:
            failure_records.append({"join_key": row.get("join_key", ""), "intron_id_std": row.get("intron_id_std", ""), "display_gene": row.get("display_gene", ""), "group": row.get("group", ""), "reason": "missing_or_invalid_branchpoint_position"})
            continue
        try:
            metrics = rnalib_metrics(seq, bp_center)
        except Exception as exc:
            failure_records.append({"join_key": row.get("join_key", ""), "intron_id_std": row.get("intron_id_std", ""), "display_gene": row.get("display_gene", ""), "group": row.get("group", ""), "reason": f"RNAlib_failed:{repr(exc)}"})
            continue
        record = {
            "join_key": row.get("join_key", ""),
            "intron_id_std": row.get("intron_id_std", ""),
            "display_gene": row.get("display_gene", ""),
            "systematic_gene": row.get("systematic_gene", ""),
            "group": row.get("group", ""),
            "locked_group": row.get("locked_group", ""),
            "pass_age_gate_from_fig2": row.get("pass_age_gate_from_fig2", ""),
            "aging_effect": row.get("aging_effect", np.nan),
            "CR_suppression": row.get("CR_suppression", np.nan),
            "candidate_score": row.get("candidate_score", np.nan),
            "annotation_chrom": ann["chrom"],
            "annotation_start": ann["start"],
            "annotation_end": ann["end"],
            "annotation_strand": ann["strand"],
            "annotation_match_method": ann.get("match_method", ""),
            "metric_match_method": row.get("metric_match_method", ""),
        }
        record.update(metrics)
        metric_records.append(record)
        extraction_records.append({"join_key": row.get("join_key", ""), "intron_id_std": row.get("intron_id_std", ""), "display_gene": row.get("display_gene", ""), "group": row.get("group", ""), "chrom": ann["chrom"], "start": ann["start"], "end": ann["end"], "strand": ann["strand"], "match_method": ann.get("match_method", ""), "sequence_length": len(seq), "bp_center": bp_center})

    write_tsv(AUDIT_DIR / "Figure4G_sequence_extraction_audit.tsv", extraction_records)
    write_tsv(AUDIT_DIR / "Figure4G_structure_failures.tsv", failure_records)

    metric_df = pd.DataFrame(metric_records)
    if metric_df.empty:
        raise RuntimeError("No rows survived genome-sequence extraction + branchpoint + RNAlib computation.")
    survival = metric_df["group"].value_counts().to_dict()
    if survival.get("selected", 0) < 10 or survival.get("aging_only", 0) < 3 or survival.get("background", 0) < 20:
        raise RuntimeError(f"Too few rows survived structure calculation: {survival}")

    metric_df.to_csv(DATA_DIR / "Figure4G_locked49_RNAlib_structure_metric_table.tsv", sep="\t", index=False)
    compute_stats(metric_df).to_csv(DATA_DIR / "Figure4G_locked49_RNAlib_stats.tsv", sep="\t", index=False)

    group_rows = [{"metric": key, "value": value} for key, value in group_summary.items()]
    for key, value in survival.items():
        group_rows.append({"metric": f"survived_{key}", "value": int(value)})
    group_rows.append({"metric": "failed_rows", "value": len(failure_records)})
    write_tsv(AUDIT_DIR / "Figure4G_group_count_audit.tsv", group_rows)

    write_tsv(AUDIT_DIR / "Figure4G_source_manifest.tsv", [
        {"role": "locked_selected_source", "path": str(SELECTED_SOURCE), "notes": "locked Figure 4 selected source, expected n=49"},
        {"role": "locked_background_source", "path": str(BACKGROUND_SOURCE), "notes": "locked Figure 4 background source, expected n=232"},
        {"role": "fig2_metrics_annotation_source", "path": str(fig2_path), "notes": "used only for pass_age_gate, aging_effect, CR_suppression"},
        {"role": "architecture_source", "path": str(architecture_path), "notes": json.dumps(architecture_map, sort_keys=True)},
        {"role": "genome_fasta", "path": str(fasta_path), "notes": "source for extracted intron sequences"},
        {"role": "annotation_gff_gtf", "path": str(annotation_path), "notes": "source for intron coordinates"},
        {"role": "structure_engine", "path": "Python package ViennaRNA / import RNA", "notes": f"RNA module path: {getattr(RNA, '__file__', 'unknown')}"},
    ])

    summary = {
        "selected_source": str(SELECTED_SOURCE),
        "background_source": str(BACKGROUND_SOURCE),
        "fig2_metric_annotation_path": str(fig2_path),
        "architecture_path": str(architecture_path),
        "architecture_map": architecture_map,
        "fasta_path": str(fasta_path),
        "annotation_path": str(annotation_path),
        "group_audit": group_summary,
        "surviving_groups": {key: int(value) for key, value in survival.items()},
        "failure_n": len(failure_records),
        "RNA_module_file": getattr(RNA, "__file__", "unknown"),
    }
    (OUT_DIR / "Figure4G_metric_build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SUCCESS Figure 4G locked-49 RNAlib metric build")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
