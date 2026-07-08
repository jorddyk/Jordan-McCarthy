#!/usr/bin/env python3
"""
Human purpose
-------------
Classify JM105 introns by old-cell NMD-revealed leakage and test which
functional modules and splice-architecture features separate old-selective
leakers from nonleakers.

Original source clue / conversation context
-------------------------------------------
Backfilled from the JM105 RNA-seq / Mud1 / caloric-restriction poster thread
where Jordan asked: "Which types of introns do and don't leak in the old cells?"
The Euler draft was named `scripts/29_old_cell_leaky_intron_determinants.py` and
used output from `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST`.

Expected inputs
---------------
Run on Euler from `/cluster/scratch/jmccarthy/JM105_RNAseq` or pass `--project`.
Required files:
- `02_reference/SGD_S288C_current/saccharomyces_cerevisiae_R64-5-1_20240529.gff`
- a genome FASTA somewhere under `02_reference/SGD_S288C_current/`
- `07_primary_intron_analysis/JM105_nuclear_mRNA_ORF_introns_FILTERED_for_primary_analysis.csv`
- `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST/tables/JM105_direct_old_more_leakage_paired_gene_body_normalized_per_intron.csv`

Expected outputs
----------------
- `29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/JM105_old_cell_leaky_intron_determinant_table.csv`
- `29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/JM105_module_enrichment_old_selective_leakers.csv`
- `29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/JM105_splice_architecture_numeric_features_leaker_vs_nonleaker.csv`
- `29_OLD_CELL_LEAKY_INTRON_DETERMINANTS/tables/SGD_all_annotated_introns_splice_site_features.csv`
- `JM105_OLD_CELL_LEAKY_INTRON_DETERMINANTS.tar.gz`

Known assumptions
-----------------
- This is a determinant-discovery analysis, not the final paper claim.
- Old-selective leakage is defined as: (Old NMD-off - Old NMD-on) -
  (Young NMD-off - Young NMD-on), using 2% glucose Mud1-present contrasts.
- NMD-off/upf1Δ is a detector of unstable intron-containing RNAs, not proof of
  cytosolic localization by itself.
- Sequence motif detection is a rapid genome-feature screen and should be
  confirmed before paper-level claims.
- Uses real JM105 tables only; it does not generate fake biological data.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import shutil
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

BP_CONSENSUS = "TACTAAC"  # DNA equivalent of yeast UACUAAC branchpoint
FIVE_SS_CONSENSUS = "GTATGT"  # simple yeast-like 5' splice-site reference
OLD_LEAKER_RETENTION_CUTOFF = 0.05
OLD_DETECTOR_CUTOFF = 0.05
BOUNDARY_DIRECT_CUTOFF = 0.0

CHR_ALIAS = {
    "chrI": "ref|NC_001133|",
    "chrII": "ref|NC_001134|",
    "chrIII": "ref|NC_001135|",
    "chrIV": "ref|NC_001136|",
    "chrV": "ref|NC_001137|",
    "chrVI": "ref|NC_001138|",
    "chrVII": "ref|NC_001139|",
    "chrVIII": "ref|NC_001140|",
    "chrIX": "ref|NC_001141|",
    "chrX": "ref|NC_001142|",
    "chrXI": "ref|NC_001143|",
    "chrXII": "ref|NC_001144|",
    "chrXIII": "ref|NC_001145|",
    "chrXIV": "ref|NC_001146|",
    "chrXV": "ref|NC_001147|",
    "chrXVI": "ref|NC_001148|",
    "chrM": "ref|NC_001224|",
    "chrmt": "ref|NC_001224|",
}


def safe_float(x: object) -> Optional[float]:
    try:
        if x is None:
            return None
        s = str(x).strip()
        if not s or s.lower() in {"na", "nan", "none"}:
            return None
        return float(s.replace(",", ""))
    except Exception:
        return None


def mean(xs: Iterable[Optional[float]]) -> Optional[float]:
    vals = [x for x in xs if x is not None and math.isfinite(x)]
    return None if not vals else sum(vals) / len(vals)


def median(xs: Iterable[Optional[float]]) -> Optional[float]:
    vals = sorted(x for x in xs if x is not None and math.isfinite(x))
    if not vals:
        return None
    n = len(vals)
    return vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])


def fmt(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.8g}"
    return str(x)


def read_csv(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: fmt(row.get(k)) for k in fields})


def parse_attrs(s: str) -> Dict[str, str]:
    out = {}
    for part in s.strip().split(";"):
        if "=" in part:
            key, val = part.split("=", 1)
            out[key] = val
    return out


def gene_from_text(*fields: object) -> str:
    text_blob = ";".join(str(x or "") for x in fields)
    match = re.search(r"Y[A-P][LR]\d{3}[WC](?:-[A-Z])?", text_blob)
    if match:
        return match.group(0)
    match = re.search(r"Q\d{4}", text_blob)
    if match:
        return match.group(0)
    return ""


def reverse_complement(seq: str) -> str:
    return seq.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1].upper()


def find_reference_fasta(ref_dir: Path) -> Path:
    candidates: List[Path] = []
    for pattern in ("*.fa", "*.fasta", "*.fna"):
        candidates.extend(ref_dir.rglob(pattern))
    candidates = [p for p in candidates if not any(x in p.name.lower() for x in ["cds", "rna", "protein", "pep"])]
    if not candidates:
        raise FileNotFoundError(f"No genome FASTA found under {ref_dir}")
    return sorted(candidates, key=lambda p: (("genome" not in p.name.lower()), len(str(p))))[0]


def read_fasta(path: Path) -> Dict[str, str]:
    seqs: Dict[str, str] = {}
    name: Optional[str] = None
    chunks: List[str] = []
    with path.open() as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if name is not None:
                    seqs[name] = "".join(chunks).upper()
                name = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(line.strip())
    if name is not None:
        seqs[name] = "".join(chunks).upper()
    return seqs


def get_chrom_seq(seqs: Dict[str, str], chrom: str) -> Optional[str]:
    if chrom in seqs:
        return seqs[chrom]
    alias = CHR_ALIAS.get(chrom)
    if alias and alias in seqs:
        return seqs[alias]
    for key in seqs:
        if key == chrom or key.endswith(chrom) or chrom.endswith(key):
            return seqs[key]
    return None


def extract_seq(seqs: Dict[str, str], chrom: str, start_1: int, end_1: int, strand: str) -> str:
    chrom_seq = get_chrom_seq(seqs, chrom)
    if chrom_seq is None:
        return ""
    seq = chrom_seq[start_1 - 1 : end_1].upper()
    return reverse_complement(seq) if strand == "-" else seq


def hamming(a: str, b: str) -> Optional[int]:
    if len(a) != len(b):
        return None
    return sum(1 for x, y in zip(a.upper(), b.upper()) if x != y)


def frac_pyrimidine(seq: str) -> Optional[float]:
    seq = seq.upper()
    if not seq:
        return None
    return sum(1 for ch in seq if ch in {"C", "T"}) / len(seq)


def longest_pyrimidine_run(seq: str) -> int:
    best = 0
    cur = 0
    for ch in seq.upper():
        if ch in {"C", "T"}:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def best_branchpoint(seq: str) -> dict:
    seq = seq.upper()
    if len(seq) < 7:
        return {
            "branchpoint_best_seq": "",
            "branchpoint_mismatches_to_TACTAAC": "",
            "branchpoint_pos_from_5ss_1based": "",
            "branchpoint_distance_to_3ss_nt": "",
            "branchpoint_exact_TACTAAC": "no",
        }
    start = 10 if len(seq) > 30 else 0
    end = len(seq) - 7 - 3 if len(seq) > 20 else len(seq) - 7
    if end < start:
        start, end = 0, len(seq) - 7
    best: Optional[Tuple[Tuple[int, int], int, str, int]] = None
    for i in range(start, end + 1):
        win = seq[i : i + 7]
        mism = hamming(win, BP_CONSENSUS)
        assert mism is not None
        score = (mism, len(seq) - (i + 7))
        if best is None or score < best[0]:
            best = (score, i, win, mism)
    assert best is not None
    _, i, win, mism = best
    return {
        "branchpoint_best_seq": win,
        "branchpoint_mismatches_to_TACTAAC": mism,
        "branchpoint_pos_from_5ss_1based": i + 1,
        "branchpoint_distance_to_3ss_nt": len(seq) - (i + 7),
        "branchpoint_exact_TACTAAC": "yes" if win == BP_CONSENSUS else "no",
    }


def annotate_splice_features(seq: str) -> dict:
    seq = seq.upper()
    bp = best_branchpoint(seq)
    bp_pos = safe_float(bp.get("branchpoint_pos_from_5ss_1based"))
    bp_end_idx = int(bp_pos - 1 + 7) if bp_pos is not None else None
    region_bp_to_3ss = seq[bp_end_idx:-3] if bp_end_idx is not None and bp_end_idx < len(seq) - 3 else ""
    last10 = seq[max(0, len(seq) - 13) : max(0, len(seq) - 3)]
    last20 = seq[max(0, len(seq) - 23) : max(0, len(seq) - 3)]
    last30 = seq[max(0, len(seq) - 33) : max(0, len(seq) - 3)]
    five6 = seq[:6]
    last3 = seq[-3:] if len(seq) >= 3 else seq
    out = {
        "intron_length_nt": len(seq),
        "intron_gc_fraction": ((seq.count("G") + seq.count("C")) / len(seq)) if seq else None,
        "five_ss_6nt": five6,
        "five_ss_9nt": seq[:9],
        "five_ss_starts_GT": "yes" if seq.startswith("GT") else "no",
        "five_ss_mismatches_to_GTATGT": hamming(five6, FIVE_SS_CONSENSUS) if len(five6) == 6 else "",
        "three_ss_last3": last3,
        "three_ss_ends_AG": "yes" if seq[-2:] == "AG" else "no",
        "three_ss_YAG": "yes" if len(last3) == 3 and last3[1:] == "AG" and last3[0] in {"C", "T"} else "no",
        "ppt_last10_pyrimidine_fraction": frac_pyrimidine(last10),
        "ppt_last20_pyrimidine_fraction": frac_pyrimidine(last20),
        "ppt_last30_pyrimidine_fraction": frac_pyrimidine(last30),
        "ppt_longest_run_bp_to_3ss": longest_pyrimidine_run(region_bp_to_3ss),
        "bp_to_3ss_region_length": len(region_bp_to_3ss),
        "bp_to_3ss_pyrimidine_fraction": frac_pyrimidine(region_bp_to_3ss),
    }
    out.update(bp)
    return out


def module_from_annotation(systematic: str, standard: str, desc: str) -> str:
    s = f"{systematic} {standard} {desc}".lower()
    std = (standard or "").upper()
    if std.startswith(("RPL", "RPS")) or "ribosomal protein" in s or "cytosolic ribosome" in s:
        return "cytosolic_ribosomal_translation"
    mito_words = ["mitochond", "respiration", "respiratory", "cytochrome", "electron transport", "oxidative phosphorylation", "atp synthase", "inner membrane"]
    if std.startswith(("COX", "QCR", "ATP", "COR", "CYT", "COB", "COI", "MRP", "MRPL", "MRPS")) or any(w in s for w in mito_words):
        if any(w in s for w in ["respiration", "respiratory", "cytochrome", "electron transport", "oxidative phosphorylation", "atp synthase"]):
            return "mitochondrial_respiration"
        return "mitochondrial_other"
    if any(w in s for w in ["splice", "splicing", "spliceosome", "rna processing", "mrna processing", "ribonucleoprotein"]):
        return "RNA_splicing_processing"
    if any(w in s for w in ["chromosome", "chromatin", "centromere", "kinetochore", "cell cycle", "dna replication", "mitosis"]):
        return "cell_cycle_chromosome"
    if any(w in s for w in ["proteasome", "chaperone", "stress", "heat shock", "ubiquitin", "protein folding"]):
        return "stress_proteostasis"
    if any(w in s for w in ["metabolic", "metabolism", "biosynthesis", "catabolic", "synthetase"]):
        return "metabolism_other"
    return "other_unclassified"


def fisher_exact_greater(a: int, b: int, c: int, d: int) -> Optional[float]:
    n = a + b + c + d
    if n == 0:
        return None
    row1 = a + b
    col1 = a + c
    denom = math.comb(n, row1)
    if denom == 0:
        return None
    def hypergeom(x: int) -> float:
        return math.comb(col1, x) * math.comb(n - col1, row1 - x) / denom
    return sum(hypergeom(x) for x in range(a, min(row1, col1) + 1))


def load_gene_annotation(gff: Path) -> Dict[str, dict]:
    annotations: Dict[str, dict] = {}
    with gff.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 9 or parts[2] != "gene":
                continue
            attrs = parse_attrs(parts[8])
            systematic = gene_from_text(attrs.get("ID", ""), attrs.get("Name", ""), parts[8])
            if not systematic:
                continue
            standard = attrs.get("Name", "") or attrs.get("gene", "") or attrs.get("Alias", "")
            desc = attrs.get("Note", "") or attrs.get("description", "") or parts[8]
            annotations[systematic] = {
                "systematic": systematic,
                "standard_name": standard,
                "description": desc,
                "primary_module": module_from_annotation(systematic, standard, desc),
            }
    return annotations


def load_all_gff_introns(gff: Path, seqs: Dict[str, str], gene_annotation: Dict[str, dict]) -> List[dict]:
    rows: List[dict] = []
    with gff.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 9 or parts[2].lower() != "intron":
                continue
            chrom, _, _, start, end, _, strand, _, attr_text = parts
            attrs = parse_attrs(attr_text)
            gene = gene_from_text(attrs.get("Parent", ""), attrs.get("Name", ""), attr_text)
            seq = extract_seq(seqs, chrom, int(start), int(end), strand)
            if not seq:
                continue
            ann = gene_annotation.get(gene, {})
            rows.append({
                "source": "GFF_all_annotated_introns",
                "chrom": chrom,
                "start": start,
                "end": end,
                "strand": strand,
                "gene": gene,
                "standard_name": ann.get("standard_name", ""),
                "description": ann.get("description", ""),
                "primary_module": ann.get("primary_module", "other_unclassified"),
                "name": attrs.get("Name", "") or f"{gene}_intron",
                "sequence": seq,
                **annotate_splice_features(seq),
            })
    return rows


def build_determinant_table(project: Path) -> Tuple[List[dict], List[dict]]:
    ref_dir = project / "02_reference" / "SGD_S288C_current"
    gff = ref_dir / "saccharomyces_cerevisiae_R64-5-1_20240529.gff"
    intron_table = project / "07_primary_intron_analysis" / "JM105_nuclear_mRNA_ORF_introns_FILTERED_for_primary_analysis.csv"
    effects_table = project / "26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST" / "tables" / "JM105_direct_old_more_leakage_paired_gene_body_normalized_per_intron.csv"

    fasta = find_reference_fasta(ref_dir)
    seqs = read_fasta(fasta)
    gene_annotation = load_gene_annotation(gff)
    all_gff_introns = load_all_gff_introns(gff, seqs, gene_annotation)

    intron_rows = read_csv(intron_table)
    effect_rows = read_csv(effects_table)

    measured: Dict[str, dict] = {}
    for row in intron_rows:
        intron_id = row.get("intron_id", "")
        if not intron_id or intron_id in measured:
            continue
        gene = gene_from_text(row.get("gene", ""), row.get("name", ""), row.get("parent", ""), intron_id)
        chrom = row.get("gff_chrom") or row.get("star_chrom") or ""
        try:
            seq = extract_seq(seqs, chrom, int(row.get("intron_start_1based", "0")), int(row.get("intron_end_1based", "0")), row.get("strand", "+"))
        except Exception:
            seq = ""
        ann = gene_annotation.get(gene, {})
        measured[intron_id] = {
            "intron_id": intron_id,
            "gene": gene,
            "standard_name": ann.get("standard_name", gene),
            "description": ann.get("description", ""),
            "primary_module": ann.get("primary_module", "other_unclassified"),
            "name": row.get("name", ""),
            "parent": row.get("parent", ""),
            "chrom": chrom,
            "start": row.get("intron_start_1based", ""),
            "end": row.get("intron_end_1based", ""),
            "strand": row.get("strand", ""),
            "sequence": seq,
            **(annotate_splice_features(seq) if seq else {}),
        }

    effects_by: Dict[str, Dict[Tuple[str, str], dict]] = defaultdict(dict)
    for row in effect_rows:
        if row.get("glucose") != "2%":
            continue
        intron = row.get("intron_id", "")
        key = (row.get("metric", ""), row.get("background", ""))
        effects_by[intron][key] = {
            "young_detector": safe_float(row.get("young_detector")),
            "old_detector": safe_float(row.get("old_detector")),
            "direct": safe_float(row.get("DIRECT_old_minus_young_NMD_revealed")),
            "young_NMD_on": safe_float(row.get("young_NMD_on")),
            "young_NMD_off": safe_float(row.get("young_NMD_off")),
            "old_NMD_on": safe_float(row.get("old_NMD_on")),
            "old_NMD_off": safe_float(row.get("old_NMD_off")),
        }

    determinant_rows: List[dict] = []
    for intron_id, meta in measured.items():
        ret_present = effects_by[intron_id].get(("retention_fraction", "Mud1_present"), {})
        bound_present = effects_by[intron_id].get(("boundary_per_10k_gene_body_fragments", "Mud1_present"), {})
        ret_absent = effects_by[intron_id].get(("retention_fraction", "Mud1_absent"), {})
        bound_absent = effects_by[intron_id].get(("boundary_per_10k_gene_body_fragments", "Mud1_absent"), {})
        direct_ret = ret_present.get("direct")
        old_detector = ret_present.get("old_detector")
        direct_bound = bound_present.get("direct")
        if direct_ret is None:
            old_leak_class = "not_tested"
        elif direct_ret >= OLD_LEAKER_RETENTION_CUTOFF and (old_detector or 0) >= OLD_DETECTOR_CUTOFF and (direct_bound is None or direct_bound > BOUNDARY_DIRECT_CUTOFF):
            old_leak_class = "old_selective_leaker"
        elif old_detector is not None and old_detector >= OLD_DETECTOR_CUTOFF and direct_ret < OLD_LEAKER_RETENTION_CUTOFF:
            old_leak_class = "NMD_revealed_but_not_old_selective"
        elif direct_ret <= 0:
            old_leak_class = "old_nonleaker_or_young_skewed"
        else:
            old_leak_class = "intermediate"

        old_upf1_rows = [
            r for r in intron_rows
            if r.get("intron_id") == intron_id
            and str(r.get("age")) == "Old"
            and "upf1" in str(r.get("genotype", "")).lower().replace("_", " ")
            and "mud1" not in str(r.get("genotype", "")).lower().replace("_", " ")
            and "2" in str(r.get("glucose"))
        ]
        ei = mean([(safe_float(r.get("EI_count")) or 0.0) for r in old_upf1_rows])
        ie = mean([(safe_float(r.get("IE_count")) or 0.0) for r in old_upf1_rows])
        if ei is not None and ie is not None and ei + ie > 0:
            ei_fraction = ei / (ei + ie)
            if ei_fraction >= 0.65:
                boundary_bias = "5prime_EI_dominant"
            elif ei_fraction <= 0.35:
                boundary_bias = "3prime_IE_dominant"
            else:
                boundary_bias = "both_boundaries"
        else:
            ei_fraction = ""
            boundary_bias = "none"

        determinant_rows.append({
            **meta,
            "old_leak_class": old_leak_class,
            "old_selective_leaker_binary": "yes" if old_leak_class == "old_selective_leaker" else "no",
            "retention_young_detector_Mud1_present": ret_present.get("young_detector"),
            "retention_old_detector_Mud1_present": old_detector,
            "retention_DIRECT_old_minus_young_Mud1_present": direct_ret,
            "boundary_DIRECT_old_minus_young_Mud1_present": direct_bound,
            "retention_DIRECT_old_minus_young_Mud1_absent": ret_absent.get("direct"),
            "boundary_DIRECT_old_minus_young_Mud1_absent": bound_absent.get("direct"),
            "old_upf1_mean_EI_count": ei,
            "old_upf1_mean_IE_count": ie,
            "old_upf1_EI_fraction_of_EI_plus_IE": ei_fraction,
            "old_upf1_boundary_bias": boundary_bias,
        })
    return determinant_rows, all_gff_introns


def summarize_modules(rows: Sequence[dict]) -> List[dict]:
    leakers = [r for r in rows if r.get("old_leak_class") == "old_selective_leaker"]
    nonleakers = [r for r in rows if r.get("old_leak_class") in {"old_nonleaker_or_young_skewed", "NMD_revealed_but_not_old_selective"}]
    out = []
    for module in sorted({r.get("primary_module", "other_unclassified") for r in rows}):
        a = sum(1 for r in leakers if r.get("primary_module") == module)
        b = len(leakers) - a
        c = sum(1 for r in nonleakers if r.get("primary_module") == module)
        d = len(nonleakers) - c
        out.append({
            "primary_module": module,
            "old_selective_leakers": a,
            "nonleakers_or_not_old_selective": c,
            "fraction_of_leakers": a / len(leakers) if leakers else "",
            "fraction_of_nonleakers": c / len(nonleakers) if nonleakers else "",
            "fisher_p_enriched_in_leakers": fisher_exact_greater(a, b, c, d) if leakers and nonleakers else "",
        })
    return out


def summarize_numeric(rows: Sequence[dict]) -> List[dict]:
    leakers = [r for r in rows if r.get("old_leak_class") == "old_selective_leaker"]
    nonleakers = [r for r in rows if r.get("old_leak_class") in {"old_nonleaker_or_young_skewed", "NMD_revealed_but_not_old_selective"}]
    features = [
        "intron_length_nt",
        "intron_gc_fraction",
        "five_ss_mismatches_to_GTATGT",
        "branchpoint_mismatches_to_TACTAAC",
        "branchpoint_distance_to_3ss_nt",
        "ppt_last10_pyrimidine_fraction",
        "ppt_last20_pyrimidine_fraction",
        "ppt_last30_pyrimidine_fraction",
        "ppt_longest_run_bp_to_3ss",
        "bp_to_3ss_pyrimidine_fraction",
        "old_upf1_EI_fraction_of_EI_plus_IE",
    ]
    out = []
    for feat in features:
        lv = [safe_float(r.get(feat)) for r in leakers]
        nv = [safe_float(r.get(feat)) for r in nonleakers]
        lm = median(lv)
        nm = median(nv)
        out.append({
            "feature": feat,
            "n_leakers": len([x for x in lv if x is not None]),
            "n_nonleakers": len([x for x in nv if x is not None]),
            "leaker_mean": mean(lv),
            "nonleaker_mean": mean(nv),
            "leaker_median": lm,
            "nonleaker_median": nm,
            "difference_leaker_minus_nonleaker_median": (lm - nm) if lm is not None and nm is not None else "",
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="JM105 old-cell leaky intron determinant screen")
    parser.add_argument("--project", default="/cluster/scratch/jmccarthy/JM105_RNAseq", help="JM105 project root")
    parser.add_argument("--out", default="29_OLD_CELL_LEAKY_INTRON_DETERMINANTS", help="output folder name or absolute path")
    args = parser.parse_args()

    project = Path(args.project)
    outroot = Path(args.out) if Path(args.out).is_absolute() else project / args.out
    tables = outroot / "tables"
    if outroot.exists():
        shutil.rmtree(outroot)
    tables.mkdir(parents=True, exist_ok=True)

    determinant_rows, all_gff_introns = build_determinant_table(project)
    module_rows = summarize_modules(determinant_rows)
    numeric_rows = summarize_numeric(determinant_rows)
    top_leakers = sorted(
        determinant_rows,
        key=lambda r: (
            safe_float(r.get("retention_DIRECT_old_minus_young_Mud1_present")) or -999,
            safe_float(r.get("boundary_DIRECT_old_minus_young_Mud1_present")) or -999,
        ),
        reverse=True,
    )[:40]

    write_csv(tables / "JM105_old_cell_leaky_intron_determinant_table.csv", determinant_rows)
    write_csv(tables / "SGD_all_annotated_introns_splice_site_features.csv", all_gff_introns)
    write_csv(tables / "JM105_module_enrichment_old_selective_leakers.csv", module_rows)
    write_csv(tables / "JM105_splice_architecture_numeric_features_leaker_vs_nonleaker.csv", numeric_rows)
    write_csv(tables / "JM105_top_old_selective_leaky_introns_ranked.csv", top_leakers)

    leakers = [r for r in determinant_rows if r.get("old_leak_class") == "old_selective_leaker"]
    comparison = [r for r in determinant_rows if r.get("old_leak_class") in {"old_nonleaker_or_young_skewed", "NMD_revealed_but_not_old_selective"}]
    readme = outroot / "00_READ_FIRST_old_cell_leaky_intron_determinants.txt"
    readme.write_text(
        "JM105 old-cell leaky intron determinant screen\n"
        "==============================================\n\n"
        "Question: Which introns leak in old cells, and what determines that behavior?\n\n"
        "Leakage definition:\n"
        "  Old detector   = Old upf1Δ - Old WT\n"
        "  Young detector = Young upf1Δ - Young WT\n"
        "  Old-selective leakage = Old detector - Young detector\n\n"
        f"Measured introns: {len(determinant_rows)}\n"
        f"Old-selective leakers: {len(leakers)}\n"
        f"Comparison/nonleaker set: {len(comparison)}\n"
        f"All annotated GFF introns with sequence: {len(all_gff_introns)}\n\n"
        "This is determinant discovery. Full paper claims require target validation and a stricter exon-normalized implementation.\n"
    )

    tarout = project / "JM105_OLD_CELL_LEAKY_INTRON_DETERMINANTS.tar.gz"
    if tarout.exists():
        tarout.unlink()
    with tarfile.open(tarout, "w:gz") as tar:
        tar.add(outroot, arcname=outroot.name)

    print(readme.read_text())
    print(f"Output folder: {outroot}")
    print(f"Tarball: {tarout}")
    print("Top old-selective leaker targets:")
    for row in top_leakers[:15]:
        print(
            row.get("standard_name") or row.get("gene") or row.get("intron_id"),
            row.get("intron_id"),
            "class=", row.get("old_leak_class"),
            "module=", row.get("primary_module"),
            "direct_ret=", fmt(safe_float(row.get("retention_DIRECT_old_minus_young_Mud1_present"))),
            "bp=", row.get("branchpoint_best_seq"),
            "bp_mism=", row.get("branchpoint_mismatches_to_TACTAAC"),
            "3SS=", row.get("three_ss_last3"),
        )


if __name__ == "__main__":
    main()
