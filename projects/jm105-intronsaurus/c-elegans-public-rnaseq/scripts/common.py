#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

import numpy as np

PIPELINE_VERSION = "2026-07-22.3"
BOUNDARY_FLANK = 8
MIN_INTRON_LENGTH = 30
MIN_TOTAL_EE = 10
MIN_SAMPLE_EE = 3
PSEUDOCOUNT = 0.5

# Definitions carried forward from JM105.
# NMD_hidden = IR(NMD off) - IR(matched NMD on)
# candidate_score = min(aging_effect, CR_suppression)
# Worm datasets do not contain the full age x DR x NMD x rnp-2 factorial.


def open_text(path: Path, mode: str = "rt"):
    return gzip.open(path, mode, encoding="utf-8", newline="") if path.suffix == ".gz" else path.open(mode, encoding="utf-8", newline="")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with open_text(path) as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open_text(path, "wt") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def bh_fdr(pvalues: Iterable[float]) -> np.ndarray:
    values = np.asarray(list(pvalues), dtype=float)
    result = np.full(values.shape, np.nan, dtype=float)
    finite = np.isfinite(values)
    if not finite.any():
        return result
    p = values[finite]
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0.0, 1.0)
    back = np.empty_like(adjusted)
    back[order] = adjusted
    result[finite] = back
    return result


def hedges_g(a: Iterable[float], b: Iterable[float]) -> float:
    x = np.asarray(list(a), dtype=float)
    y = np.asarray(list(b), dtype=float)
    x = x[np.isfinite(x)]
    y = y[np.isfinite(y)]
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    pooled_df = len(x) + len(y) - 2
    pooled_var = (((len(x) - 1) * np.var(x, ddof=1)) + ((len(y) - 1) * np.var(y, ddof=1))) / pooled_df
    if pooled_var <= 0:
        return 0.0
    d = (np.mean(y) - np.mean(x)) / math.sqrt(pooled_var)
    correction = 1.0 - (3.0 / (4.0 * pooled_df - 1.0)) if pooled_df > 1 else 1.0
    return float(d * correction)


def parse_gtf_attributes(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in text.strip().strip(";").split(";"):
        item = item.strip()
        if not item:
            continue
        match = re.match(r'([^\s]+)\s+"([^"]*)"', item)
        if match:
            attrs[match.group(1)] = match.group(2)
        else:
            parts = item.split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs


@dataclass(frozen=True)
class Intron:
    intron_id: str
    gene_id: str
    gene_name: str
    transcript_id: str
    chrom: str
    start0: int
    end0: int
    strand: str
    intron_length: int


def build_representative_introns(gtf_path: Path) -> list[Intron]:
    transcript_exons: dict[str, list[tuple[str, int, int, str]]] = {}
    transcript_gene: dict[str, str] = {}
    transcript_gene_name: dict[str, str] = {}
    transcript_biotype: dict[str, str] = {}
    transcript_cds_length: dict[str, int] = {}
    gene_biotype: dict[str, str] = {}

    with open_text(gtf_path) as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                continue
            chrom, _, feature, start, end, _, strand, _, attr_text = fields
            attrs = parse_gtf_attributes(attr_text)
            gene_id = attrs.get("gene_id", "")
            transcript_id = attrs.get("transcript_id", "")
            if gene_id:
                gene_biotype[gene_id] = attrs.get("gene_biotype", attrs.get("gene_type", gene_biotype.get(gene_id, "")))
            if not transcript_id:
                continue
            transcript_gene[transcript_id] = gene_id
            transcript_gene_name[transcript_id] = attrs.get("gene_name", gene_id)
            transcript_biotype[transcript_id] = attrs.get("transcript_biotype", attrs.get("transcript_type", ""))
            if feature == "exon":
                transcript_exons.setdefault(transcript_id, []).append((chrom, int(start) - 1, int(end), strand))
            elif feature == "CDS":
                transcript_cds_length[transcript_id] = transcript_cds_length.get(transcript_id, 0) + (int(end) - int(start) + 1)

    gene_to_transcripts: dict[str, list[str]] = {}
    for transcript_id, gene_id in transcript_gene.items():
        if transcript_id not in transcript_exons:
            continue
        if gene_biotype.get(gene_id) != "protein_coding" and transcript_biotype.get(transcript_id) != "protein_coding":
            continue
        gene_to_transcripts.setdefault(gene_id, []).append(transcript_id)

    chosen: list[str] = []
    for gene_id, transcripts in gene_to_transcripts.items():
        ranked = []
        for transcript_id in transcripts:
            exons = transcript_exons[transcript_id]
            exonic_length = sum(end - start for _, start, end, _ in exons)
            span = max(end for _, _, end, _ in exons) - min(start for _, start, _, _ in exons)
            ranked.append((transcript_cds_length.get(transcript_id, 0), exonic_length, span, transcript_id))
        chosen.append(max(ranked)[3])

    introns: list[Intron] = []
    seen: set[tuple[str, int, int, str, str]] = set()
    for transcript_id in sorted(chosen):
        exons = transcript_exons[transcript_id]
        strand = exons[0][3]
        chrom = exons[0][0]
        exons_sorted = sorted(exons, key=lambda item: (item[1], item[2]))
        gene_id = transcript_gene[transcript_id]
        gene_name = transcript_gene_name.get(transcript_id, gene_id)
        for left, right in zip(exons_sorted, exons_sorted[1:]):
            start0 = left[2]
            end0 = right[1]
            if end0 <= start0:
                continue
            length = end0 - start0
            if length < MIN_INTRON_LENGTH:
                continue
            key = (chrom, start0, end0, strand, gene_id)
            if key in seen:
                continue
            seen.add(key)
            intron_id = f"{chrom}:{start0}-{end0}:{strand}:{gene_id}"
            introns.append(Intron(intron_id, gene_id, gene_name, transcript_id, chrom, start0, end0, strand, length))
    return introns
