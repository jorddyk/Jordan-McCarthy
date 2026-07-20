#!/usr/bin/env python3
"""
JM105 HGPS + metazoan dietary-restriction conservation pipeline.

Human purpose
-------------
Test two complementary conservation arms without equating physiological aging
with damage or disease:

1. Nuclear-architecture arm:
   Do HGPS fibroblasts expose more intron-containing / incompletely processed RNA,
   and do progerin-linked interventions move that state toward control?

2. Intervention arm:
   Does bona fide metazoan caloric restriction reduce the same prespecified
   pre-mRNA exposure metric?

This is an analysis pipeline. It produces panel-ready tables and a written gate
report. It deliberately does not render a manuscript figure before real data
have passed the gates.

Scientific scope fence
----------------------
Figure 2 remains restricted to total / rRNA-depleted JM105 only. This script
does not read or modify JM105 Figure 2 data. It does not introduce poly-A,
P-versus-T, mRNA-like, or P-minus-T constructs into Figure 2.

JM105 definitions retained for manuscript consistency
------------------------------------------------------
NMD_hidden = IR(upf1Δ) - IR(UPF1+)
candidate_score = min(aging_effect, CR_suppression)
Panel F contrast = computed (+MUD1 CR-suppression) vs
                   (mud1Δ CR-suppression), with y-limits derived from computed
                   values rather than hardcoded.

Those definitions are documentation only here: this public human/mouse pipeline
does not contain matched UPF1 perturbations and must not call PEI "NMD-hidden
leakage."

Data policy
-----------
- No simulated biological data.
- Missing or inaccessible public data are reported as NO DATA.
- Raw FASTQ, BAM, STAR indices, logs, and caches stay under the Euler project
  directory and are never intended for GitHub.
"""

from __future__ import annotations

import argparse
import gzip
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import pysam
from scipy import stats


PIPELINE_VERSION = "2026-07-20.1"
PSEUDOCOUNT = 0.5
MIN_TOTAL_SPLICED = 10
MIN_SAMPLE_SPLICED = 3
BOUNDARY_FLANK = 8
INTERIOR_TRIM = 20

GENCODE = {
    "human": {
        "release": "50",
        "fasta_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/GRCh38.primary_assembly.genome.fa.gz",
        "gtf_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.primary_assembly.annotation.gtf.gz",
        "fasta_name": "GRCh38.primary_assembly.genome.fa",
        "gtf_name": "gencode.v50.primary_assembly.annotation.gtf",
    },
    "mouse": {
        "release": "M39",
        "fasta_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M39/GRCm39.primary_assembly.genome.fa.gz",
        "gtf_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M39/gencode.vM39.primary_assembly.annotation.gtf.gz",
        "fasta_name": "GRCm39.primary_assembly.genome.fa",
        "gtf_name": "gencode.vM39.primary_assembly.annotation.gtf",
    },
}


@dataclass(frozen=True)
class DatasetSpec:
    accession: str
    species: str
    role: str
    expected_groups: Dict[str, int]
    include_groups: Tuple[str, ...]


DATASETS: Dict[str, DatasetSpec] = {
    "GSE118633": DatasetSpec(
        accession="GSE118633",
        species="human",
        role="HGPS discovery / independent total-RNA validation",
        expected_groups={"control": 3, "hgps": 3},
        include_groups=("control", "hgps"),
    ),
    "GSE137083": DatasetSpec(
        accession="GSE137083",
        species="human",
        role="HGPS intervention-direction test",
        expected_groups={
            "normal_control": 3,
            "hgps_control": 3,
            "hgps_pan_pml_kd": 3,
            "hgps_pml2_kd": 3,
            "hgps_fti": 3,
        },
        include_groups=(
            "normal_control",
            "hgps_control",
            "hgps_pan_pml_kd",
            "hgps_pml2_kd",
            "hgps_fti",
        ),
    ),
    "GSE222163": DatasetSpec(
        accession="GSE222163",
        species="mouse",
        role="Public metazoan caloric-restriction arm",
        expected_groups={
            "bat_control": 3,
            "bat_cr": 3,
            "skm_control": 3,
            "skm_cr": 3,
        },
        include_groups=("bat_control", "bat_cr", "skm_control", "skm_cr"),
    ),
}


CONTRASTS = [
    {
        "dataset": "GSE118633",
        "name": "HGPS_vs_control",
        "group_a": "control",
        "group_b": "hgps",
        "expected_direction": "positive",
        "interpretation": "HGPS-associated pre-mRNA exposure",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_control_vs_normal_control",
        "group_a": "normal_control",
        "group_b": "hgps_control",
        "expected_direction": "positive",
        "interpretation": "HGPS-associated pre-mRNA exposure",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_FTI_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_fti",
        "expected_direction": "negative",
        "interpretation": "directional movement after lonafarnib + zoledronate",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_PML2KD_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_pml2_kd",
        "expected_direction": "negative",
        "interpretation": "directional movement after PML2 knockdown",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_panPMLKD_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_pan_pml_kd",
        "expected_direction": "negative",
        "interpretation": "directional movement after pan-PML knockdown",
    },
    {
        "dataset": "GSE222163",
        "name": "BAT_CR_vs_control",
        "group_a": "bat_control",
        "group_b": "bat_cr",
        "expected_direction": "negative",
        "interpretation": "metazoan caloric-restriction suppression in brown adipose tissue",
    },
    {
        "dataset": "GSE222163",
        "name": "SkM_CR_vs_control",
        "group_a": "skm_control",
        "group_b": "skm_cr",
        "expected_direction": "negative",
        "interpretation": "metazoan caloric-restriction suppression in skeletal muscle",
    },
]


def run_command(
    command: Sequence[str],
    cwd: Optional[Path] = None,
    stdout_path: Optional[Path] = None,
) -> None:
    printable = " ".join(str(x) for x in command)
    print(f"[RUN] {printable}", flush=True)
    if stdout_path is None:
        subprocess.run(list(map(str, command)), cwd=cwd, check=True)
    else:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with stdout_path.open("w") as handle:
            subprocess.run(
                list(map(str, command)),
                cwd=cwd,
                check=True,
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
            )


def require_executables(names: Sequence[str]) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        raise RuntimeError(
            "Missing required executables: "
            + ", ".join(missing)
            + ". Activate the bundled micromamba environment."
        )


def download(url: str, destination: Path, retries: int = 4) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"[SKIP] Existing download: {destination}")
        return
    partial = destination.with_suffix(destination.suffix + ".partial")
    for attempt in range(1, retries + 1):
        try:
            print(f"[DOWNLOAD] {url} -> {destination}", flush=True)
            request = urllib.request.Request(
                url,
                headers={"User-Agent": f"JM105-HGPS-pipeline/{PIPELINE_VERSION}"},
            )
            with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
                shutil.copyfileobj(response, out)
            partial.replace(destination)
            return
        except Exception:
            if partial.exists():
                partial.unlink()
            if attempt == retries:
                raise
            time.sleep(5 * attempt)


def gunzip_file(source: Path, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    with gzip.open(source, "rb") as src, partial.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    partial.replace(destination)


def parse_soft_samples(text: str) -> List[dict]:
    samples: List[dict] = []
    current: Optional[dict] = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("^SAMPLE = "):
            if current is not None:
                samples.append(current)
            current = {
                "gsm": line.split("=", 1)[1].strip(),
                "characteristics": [],
                "relations": [],
            }
        elif current is not None and line.startswith("!Sample_"):
            key, _, value = line.partition(" = ")
            clean_key = key.replace("!Sample_", "").lower()
            value = value.strip().strip('"')
            if clean_key == "characteristics_ch1":
                current["characteristics"].append(value)
            elif clean_key == "relation":
                current["relations"].append(value)
            else:
                current[clean_key] = value
    if current is not None:
        samples.append(current)
    return samples


def extract_srx(relations: Iterable[str]) -> str:
    for relation in relations:
        match = re.search(r"(SRX\d+)", relation)
        if match:
            return match.group(1)
    return ""


def normalize_blob(sample: dict) -> str:
    fields = [
        sample.get("title", ""),
        sample.get("source_name_ch1", ""),
        sample.get("description", ""),
        *sample.get("characteristics", []),
    ]
    return " | ".join(str(x) for x in fields).lower()


def classify_group(accession: str, sample: dict) -> Optional[str]:
    blob = normalize_blob(sample)
    title = str(sample.get("title", "")).lower()

    if accession == "GSE118633":
        if not re.search(r"rna[- ]?seq|transcript", blob):
            return None
        if re.search(r"hgps|progeria", blob):
            return "hgps"
        if re.search(r"control|healthy|normal", blob):
            return "control"
        return None

    if accession == "GSE137083":
        if re.search(r"\bhgfti\b|lonafarnib|zoledronate|\bfti\b", blob):
            return "hgps_fti"
        if re.search(r"\bhgi2si\b|pml2", blob):
            return "hgps_pml2_kd"
        if re.search(r"\bhgsi\b|hgps.*pan[- ]?pml|pan[- ]?pml.*hgps", blob):
            return "hgps_pan_pml_kd"
        if re.search(r"\bhgcon\b|hgps.*control", blob):
            return "hgps_control"
        if re.search(r"\bnfcon\b|normal.*control|nhdf.*control", blob):
            return "normal_control"
        return None

    if accession == "GSE222163":
        if re.search(r"exercise|treadmill|combined|\bce\d*\b", blob):
            return None
        is_cr = bool(re.search(r"calori(?:c|e) restriction|\bcr\d*\b", blob))
        is_control = bool(
            re.search(r"\bcontrol\b|ad libitum|\bal\d*\b", blob)
            or re.search(r"\bbat[_ -]?c\d+\b|\bskm[_ -]?c\d+\b", title)
        )
        if not (is_cr or is_control):
            return None
        if re.search(r"brown adipose|\bbat\b", blob):
            return "bat_cr" if is_cr else "bat_control"
        if re.search(r"skeletal muscle|\bskm\b", blob):
            return "skm_cr" if is_cr else "skm_control"
        return None

    raise KeyError(accession)


def find_study_accession(samples: Sequence[dict]) -> str:
    for sample in samples:
        for relation in sample.get("relations", []):
            match = re.search(r"(SRP\d+)", relation)
            if match:
                return match.group(1)
    return ""


def geo_soft(accession: str, cache_dir: Path) -> List[dict]:
    cache = cache_dir / f"{accession}_family.soft.txt"
    if not cache.exists():
        url = (
            "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
            f"?acc={accession}&targ=all&view=full&form=text"
        )
        download(url, cache)
    return parse_soft_samples(cache.read_text(errors="replace"))


def runinfo(study_or_geo: str, cache_dir: Path) -> pd.DataFrame:
    cache = cache_dir / f"{study_or_geo}_RunInfo.csv"
    if not cache.exists():
        url = (
            "https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo"
            f"?acc={study_or_geo}"
        )
        download(url, cache)
    df = pd.read_csv(cache, dtype=str).fillna("")
    if "Run" not in df.columns:
        raise RuntimeError(f"RunInfo for {study_or_geo} lacks a Run column")
    return df


def build_manifest(root: Path) -> pd.DataFrame:
    cache_dir = root / "metadata" / "cache"
    rows: List[dict] = []
    audit_rows: List[dict] = []

    for accession, spec in DATASETS.items():
        samples = geo_soft(accession, cache_dir)
        study = find_study_accession(samples)
        if not study:
            known_studies = {
                "GSE118633": "SRP155495",
                "GSE137083": "SRP221023",
            }
            study = known_studies.get(accession, accession)
        info = runinfo(study, cache_dir)
        info_by_experiment = {
            str(row.get("Experiment", "")): row
            for _, row in info.iterrows()
        }

        for sample in samples:
            group = classify_group(accession, sample)
            if group is None or group not in spec.include_groups:
                continue
            srx = extract_srx(sample.get("relations", []))
            matching: List[pd.Series] = []
            if srx and srx in info_by_experiment:
                matching = [info_by_experiment[srx]]
            elif srx:
                matching = [
                    row for _, row in info.iterrows()
                    if str(row.get("Experiment", "")) == srx
                ]
            else:
                gsm = sample["gsm"]
                matching = [
                    row for _, row in info.iterrows()
                    if gsm in " ".join(str(v) for v in row.values)
                ]

            for row in matching:
                run = str(row.get("Run", ""))
                if not run.startswith("SRR"):
                    continue
                layout = str(row.get("LibraryLayout", "")).upper()
                strategy = str(row.get("LibraryStrategy", ""))
                selection = str(row.get("LibrarySelection", ""))
                bases = pd.to_numeric(row.get("bases", ""), errors="coerce")
                size_mb = pd.to_numeric(row.get("size_MB", ""), errors="coerce")
                rows.append(
                    {
                        "dataset": accession,
                        "study": study,
                        "role": spec.role,
                        "species": spec.species,
                        "gsm": sample["gsm"],
                        "srx": srx or str(row.get("Experiment", "")),
                        "run": run,
                        "sample_title": sample.get("title", ""),
                        "source": sample.get("source_name_ch1", ""),
                        "group": group,
                        "layout": layout,
                        "library_strategy": strategy,
                        "library_selection": selection,
                        "bases": "" if pd.isna(bases) else int(bases),
                        "size_mb": "" if pd.isna(size_mb) else float(size_mb),
                        "characteristics": " || ".join(sample.get("characteristics", [])),
                    }
                )

        group_counts = pd.Series(
            [row["group"] for row in rows if row["dataset"] == accession]
        ).value_counts()
        for group, expected in spec.expected_groups.items():
            observed = int(group_counts.get(group, 0))
            audit_rows.append(
                {
                    "dataset": accession,
                    "group": group,
                    "expected_minimum": expected,
                    "observed_runs": observed,
                    "pass": observed >= expected,
                }
            )

    manifest = pd.DataFrame(rows).drop_duplicates(subset=["dataset", "run"])
    if manifest.empty:
        raise RuntimeError("No prespecified RNA-seq runs were resolved from GEO/SRA")

    metadata_dir = root / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(metadata_dir / "run_manifest.tsv", sep="\t", index=False)
    audit = pd.DataFrame(audit_rows)
    audit.to_csv(metadata_dir / "manifest_gate.tsv", sep="\t", index=False)

    failures = audit.loc[~audit["pass"]]
    if not failures.empty:
        raise RuntimeError(
            "Manifest gate failed before download:\n"
            + failures.to_string(index=False)
            + "\nInspect metadata/run_manifest.tsv and update only evidence-backed classifiers."
        )
    return manifest


def prepare_reference(root: Path, species: str, threads: int) -> Tuple[Path, Path, Path]:
    cfg = GENCODE[species]
    ref_dir = root / "reference" / species / f"gencode_{cfg['release']}"
    ref_dir.mkdir(parents=True, exist_ok=True)

    fasta_gz = ref_dir / (cfg["fasta_name"] + ".gz")
    gtf_gz = ref_dir / (cfg["gtf_name"] + ".gz")
    fasta = ref_dir / cfg["fasta_name"]
    gtf = ref_dir / cfg["gtf_name"]
    index_dir = ref_dir / "STAR_index"

    download(cfg["fasta_url"], fasta_gz)
    download(cfg["gtf_url"], gtf_gz)
    gunzip_file(fasta_gz, fasta)
    gunzip_file(gtf_gz, gtf)

    sentinel = index_dir / "Genome"
    if not sentinel.exists():
        index_dir.mkdir(parents=True, exist_ok=True)
        run_command(
            [
                "STAR",
                "--runThreadN",
                str(threads),
                "--runMode",
                "genomeGenerate",
                "--genomeDir",
                str(index_dir),
                "--genomeFastaFiles",
                str(fasta),
                "--sjdbGTFfile",
                str(gtf),
                "--sjdbOverhang",
                "149",
            ]
        )
    return fasta, gtf, index_dir


def fastq_paths(fastq_dir: Path, run: str) -> Tuple[Path, Optional[Path]]:
    r1 = fastq_dir / f"{run}_1.fastq"
    r2 = fastq_dir / f"{run}_2.fastq"
    single = fastq_dir / f"{run}.fastq"
    if r1.exists():
        return r1, r2 if r2.exists() else None
    if single.exists():
        return single, None
    raise FileNotFoundError(f"No FASTQ created for {run}")


def download_run(root: Path, run: str, threads: int) -> Tuple[Path, Optional[Path]]:
    fastq_dir = root / "raw" / "fastq"
    sra_dir = root / "raw" / "sra"
    fastq_dir.mkdir(parents=True, exist_ok=True)
    sra_dir.mkdir(parents=True, exist_ok=True)

    expected = [
        fastq_dir / f"{run}_1.fastq",
        fastq_dir / f"{run}.fastq",
    ]
    if not any(path.exists() for path in expected):
        run_command(
            [
                "prefetch",
                "--max-size",
                "u",
                "--output-directory",
                str(sra_dir),
                run,
            ]
        )
        sra_object = sra_dir / run / f"{run}.sra"
        source = sra_object if sra_object.exists() else sra_dir / run
        run_command(
            [
                "fasterq-dump",
                "--split-files",
                "--threads",
                str(max(2, min(threads, 12))),
                "--outdir",
                str(fastq_dir),
                str(source),
            ]
        )
    return fastq_paths(fastq_dir, run)


def align_run(
    root: Path,
    row: pd.Series,
    index_dir: Path,
    gtf: Path,
    threads: int,
) -> Path:
    run = str(row["run"])
    dataset = str(row["dataset"])
    output_dir = root / "alignment" / dataset / run
    output_dir.mkdir(parents=True, exist_ok=True)
    bam = output_dir / "Aligned.sortedByCoord.out.bam"
    if bam.exists() and Path(str(bam) + ".bai").exists():
        return bam

    r1, r2 = download_run(root, run, threads)
    command = [
        "STAR",
        "--runThreadN",
        str(threads),
        "--genomeDir",
        str(index_dir),
        "--sjdbGTFfile",
        str(gtf),
        "--readFilesIn",
        str(r1),
    ]
    if r2 is not None:
        command.append(str(r2))
    command.extend(
        [
            "--outFileNamePrefix",
            str(output_dir) + os.sep,
            "--outSAMtype",
            "BAM",
            "SortedByCoordinate",
            "--outSAMstrandField",
            "intronMotif",
            "--outFilterMultimapNmax",
            "20",
            "--alignSJoverhangMin",
            "8",
            "--alignSJDBoverhangMin",
            "1",
            "--outFilterMismatchNoverReadLmax",
            "0.04",
            "--quantMode",
            "GeneCounts",
            "--limitBAMsortRAM",
            "50000000000",
        ]
    )
    run_command(command)
    run_command(["samtools", "index", "-@", str(min(threads, 8)), str(bam)])
    return bam


def parse_gtf_attributes(text: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    for part in text.strip().split(";"):
        part = part.strip()
        if not part:
            continue
        match = re.match(r'(\S+)\s+"(.*)"$', part)
        if match:
            attrs[match.group(1)] = match.group(2)
    return attrs


def representative_introns(gtf: Path, cache_path: Path) -> pd.DataFrame:
    if cache_path.exists():
        return pd.read_csv(cache_path, sep="\t")

    transcript_meta: Dict[str, dict] = {}
    exons: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    cds_lengths: Dict[str, int] = defaultdict(int)

    with gtf.open() as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                continue
            chrom, _, feature, start, end, _, strand, _, attrs_text = fields
            attrs = parse_gtf_attributes(attrs_text)
            transcript_id = attrs.get("transcript_id")
            gene_id = attrs.get("gene_id")
            if not transcript_id or not gene_id:
                continue
            transcript_type = attrs.get("transcript_type", attrs.get("transcript_biotype", ""))
            gene_type = attrs.get("gene_type", attrs.get("gene_biotype", ""))
            tags = attrs.get("tag", "")
            if transcript_type != "protein_coding" or gene_type != "protein_coding":
                continue
            transcript_meta[transcript_id] = {
                "chrom": chrom,
                "strand": strand,
                "gene_id": gene_id.split(".")[0],
                "gene_name": attrs.get("gene_name", gene_id),
                "transcript_id": transcript_id.split(".")[0],
                "mane_select": "MANE_Select" in tags,
                "appris": "appris_principal" in tags,
            }
            if feature == "exon":
                exons[transcript_id].append((int(start) - 1, int(end)))
            elif feature == "CDS":
                cds_lengths[transcript_id] += int(end) - int(start) + 1

    by_gene: Dict[str, List[str]] = defaultdict(list)
    for transcript_id, meta in transcript_meta.items():
        if len(exons.get(transcript_id, [])) >= 2:
            by_gene[meta["gene_id"]].append(transcript_id)

    rows: List[dict] = []
    for gene_id, transcripts in by_gene.items():
        def score(tid: str) -> Tuple[int, int, int, str]:
            meta = transcript_meta[tid]
            exon_span = sum(e - s for s, e in exons[tid])
            return (
                1 if meta["mane_select"] else 0,
                1 if meta["appris"] else 0,
                cds_lengths.get(tid, 0) * 10_000_000 + exon_span,
                tid,
            )

        chosen = max(transcripts, key=score)
        meta = transcript_meta[chosen]
        ordered = sorted(exons[chosen], key=lambda x: x[0])
        if meta["strand"] == "-":
            ordered = list(reversed(ordered))

        for index in range(len(ordered) - 1):
            a = ordered[index]
            b = ordered[index + 1]
            if meta["strand"] == "+":
                intron_start, intron_end = a[1], b[0]
            else:
                intron_start, intron_end = b[1], a[0]
            if intron_end - intron_start < 40:
                continue
            rows.append(
                {
                    "intron_id": f"{meta['chrom']}:{intron_start}-{intron_end}:{meta['strand']}:{gene_id}:{index+1}",
                    "chrom": meta["chrom"],
                    "start0": intron_start,
                    "end0": intron_end,
                    "strand": meta["strand"],
                    "gene_id": gene_id,
                    "gene_name": meta["gene_name"],
                    "transcript_id": meta["transcript_id"],
                    "intron_number": index + 1,
                    "intron_length": intron_end - intron_start,
                }
            )

    df = pd.DataFrame(rows).drop_duplicates(subset=["intron_id"])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path, sep="\t", index=False)
    return df


def read_spans_boundary(read: pysam.AlignedSegment, boundary0: int) -> bool:
    if read.is_unmapped or read.is_secondary or read.is_supplementary:
        return False
    for start, end in read.get_blocks():
        if start <= boundary0 - BOUNDARY_FLANK and end >= boundary0 + BOUNDARY_FLANK:
            return True
    return False


def read_junctions(read: pysam.AlignedSegment) -> Iterator[Tuple[int, int]]:
    if read.is_unmapped or not read.cigartuples:
        return
    ref = read.reference_start
    for operation, length in read.cigartuples:
        if operation in {0, 2, 7, 8}:
            ref += length
        elif operation == 3:
            donor = ref
            acceptor = ref + length
            yield donor, acceptor
            ref += length
        elif operation in {1, 4, 5, 6}:
            continue


def count_one_intron(
    bam: pysam.AlignmentFile,
    chrom: str,
    start0: int,
    end0: int,
) -> Tuple[int, int, int, int]:
    left_names: set[str] = set()
    right_names: set[str] = set()
    splice_names: set[str] = set()
    interior_names: set[str] = set()

    fetch_start = max(0, start0 - 300)
    fetch_end = end0 + 300
    try:
        iterator = bam.fetch(chrom, fetch_start, fetch_end)
    except ValueError:
        return 0, 0, 0, 0

    interior_start = start0 + INTERIOR_TRIM
    interior_end = end0 - INTERIOR_TRIM
    for read in iterator:
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            continue
        name = read.query_name
        if read_spans_boundary(read, start0):
            left_names.add(name)
        if read_spans_boundary(read, end0):
            right_names.add(name)
        for donor, acceptor in read_junctions(read):
            if donor == start0 and acceptor == end0:
                splice_names.add(name)
        if interior_end > interior_start:
            for block_start, block_end in read.get_blocks():
                if block_start < interior_end and block_end > interior_start:
                    interior_names.add(name)
                    break
    return len(left_names), len(right_names), len(splice_names), len(interior_names)


def quantify_bam(
    bam_path: Path,
    introns: pd.DataFrame,
    output_path: Path,
) -> pd.DataFrame:
    if output_path.exists():
        return pd.read_csv(output_path, sep="\t")

    rows: List[dict] = []
    with pysam.AlignmentFile(bam_path, "rb") as bam:
        references = set(bam.references)
        for record in introns.itertuples(index=False):
            if record.chrom not in references:
                continue
            left, right, spliced, interior = count_one_intron(
                bam,
                record.chrom,
                int(record.start0),
                int(record.end0),
            )
            boundary_mean = 0.5 * (left + right)
            pei = math.log2((left + right + PSEUDOCOUNT) / (2 * spliced + PSEUDOCOUNT))
            interior_density = interior / max(1.0, (int(record.intron_length) - 2 * INTERIOR_TRIM) / 1000.0)
            rows.append(
                {
                    **record._asdict(),
                    "left_boundary_reads": left,
                    "right_boundary_reads": right,
                    "spliced_junction_reads": spliced,
                    "interior_overlap_reads": interior,
                    "boundary_mean": boundary_mean,
                    "PEI": pei,
                    "interior_reads_per_kb": interior_density,
                }
            )

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)
    return df


def bh_fdr(pvalues: Sequence[float]) -> np.ndarray:
    p = np.asarray(pvalues, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    out = np.empty(n)
    out[order] = adjusted
    return out


def hedges_g(a: Sequence[float], b: Sequence[float]) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled_num = (len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)
    pooled_den = len(a) + len(b) - 2
    if pooled_den <= 0 or pooled_num <= 0:
        return 0.0
    pooled = math.sqrt(pooled_num / pooled_den)
    d = (np.mean(b) - np.mean(a)) / pooled
    correction = 1 - 3 / (4 * (len(a) + len(b)) - 9)
    return float(d * correction)


def read_star_qc(bam: Path) -> dict:
    log = bam.parent / "Log.final.out"
    result: Dict[str, object] = {}
    if not log.exists():
        return result
    for line in log.read_text(errors="replace").splitlines():
        if "|" not in line:
            continue
        key, value = [x.strip() for x in line.split("|", 1)]
        result[key] = value
    return result


def analyse(root: Path, manifest: pd.DataFrame) -> None:
    quant_dir = root / "quantification"
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_long: List[pd.DataFrame] = []
    sample_rows: List[dict] = []
    qc_rows: List[dict] = []

    for row in manifest.itertuples(index=False):
        quant_path = quant_dir / row.dataset / f"{row.run}.introns.tsv"
        if not quant_path.exists():
            raise FileNotFoundError(quant_path)
        df = pd.read_csv(quant_path, sep="\t")
        df["dataset"] = row.dataset
        df["run"] = row.run
        df["group"] = row.group
        df["species"] = row.species
        all_long.append(df)

        detectable = df.loc[df["spliced_junction_reads"] >= MIN_SAMPLE_SPLICED].copy()
        sample_rows.append(
            {
                "dataset": row.dataset,
                "run": row.run,
                "group": row.group,
                "species": row.species,
                "n_introns_detectable": len(detectable),
                "median_PEI": detectable["PEI"].median() if len(detectable) else np.nan,
                "median_interior_reads_per_kb": detectable["interior_reads_per_kb"].median() if len(detectable) else np.nan,
            }
        )
        bam = root / "alignment" / row.dataset / row.run / "Aligned.sortedByCoord.out.bam"
        qc = read_star_qc(bam)
        qc_rows.append(
            {
                "dataset": row.dataset,
                "run": row.run,
                "group": row.group,
                "uniquely_mapped_reads_percent": qc.get("% of reads mapped uniquely", ""),
                "multimapped_reads_percent": qc.get("% of reads mapped to multiple loci", ""),
                "input_reads": qc.get("Number of input reads", ""),
            }
        )

    long_df = pd.concat(all_long, ignore_index=True)
    sample_df = pd.DataFrame(sample_rows)
    qc_df = pd.DataFrame(qc_rows)
    long_df.to_parquet(results_dir / "all_intron_measurements.parquet", index=False)
    sample_df.to_csv(results_dir / "sample_pre_mrna_exposure_scores.tsv", sep="\t", index=False)
    qc_df.to_csv(results_dir / "alignment_qc.tsv", sep="\t", index=False)

    contrast_summary: List[dict] = []

    for contrast in CONTRASTS:
        dataset = contrast["dataset"]
        subset = long_df.loc[long_df["dataset"] == dataset].copy()
        group_a = contrast["group_a"]
        group_b = contrast["group_b"]
        a_runs = sample_df.loc[
            (sample_df["dataset"] == dataset) & (sample_df["group"] == group_a),
            "run",
        ].tolist()
        b_runs = sample_df.loc[
            (sample_df["dataset"] == dataset) & (sample_df["group"] == group_b),
            "run",
        ].tolist()

        sample_a = sample_df.loc[
            (sample_df["dataset"] == dataset) & (sample_df["group"] == group_a),
            "median_PEI",
        ].dropna().to_numpy()
        sample_b = sample_df.loc[
            (sample_df["dataset"] == dataset) & (sample_df["group"] == group_b),
            "median_PEI",
        ].dropna().to_numpy()

        if len(sample_a) >= 2 and len(sample_b) >= 2:
            t_stat, sample_p = stats.ttest_ind(sample_b, sample_a, equal_var=False)
            mw_stat, sample_mw_p = stats.mannwhitneyu(sample_b, sample_a, alternative="two-sided")
        else:
            t_stat = sample_p = mw_stat = sample_mw_p = np.nan

        sample_delta = float(np.mean(sample_b) - np.mean(sample_a)) if len(sample_a) and len(sample_b) else np.nan
        direction_pass = (
            sample_delta > 0
            if contrast["expected_direction"] == "positive"
            else sample_delta < 0
        )

        pivot_pei = subset.pivot_table(
            index=[
                "intron_id",
                "gene_id",
                "gene_name",
                "chrom",
                "start0",
                "end0",
                "strand",
                "intron_length",
            ],
            columns="run",
            values="PEI",
            aggfunc="first",
        )
        pivot_spliced = subset.pivot_table(
            index="intron_id",
            columns="run",
            values="spliced_junction_reads",
            aggfunc="first",
        ).fillna(0)

        rows: List[dict] = []
        for idx, values in pivot_pei.iterrows():
            va = values.reindex(a_runs).dropna().to_numpy(dtype=float)
            vb = values.reindex(b_runs).dropna().to_numpy(dtype=float)
            if len(va) < 2 or len(vb) < 2:
                continue
            intron_id = idx[0]
            selected_runs = [r for r in dict.fromkeys(a_runs + b_runs) if r in pivot_spliced.columns]
            total_junction = float(
                pivot_spliced.loc[intron_id, selected_runs].sum()
            ) if intron_id in pivot_spliced.index and selected_runs else 0.0
            if total_junction < MIN_TOTAL_SPLICED:
                continue
            t, p = stats.ttest_ind(vb, va, equal_var=False)
            rows.append(
                {
                    "contrast": contrast["name"],
                    "dataset": dataset,
                    "intron_id": intron_id,
                    "gene_id": idx[1],
                    "gene_name": idx[2],
                    "chrom": idx[3],
                    "start0": idx[4],
                    "end0": idx[5],
                    "strand": idx[6],
                    "intron_length": idx[7],
                    "mean_group_a": float(np.mean(va)),
                    "mean_group_b": float(np.mean(vb)),
                    "delta_PEI_b_minus_a": float(np.mean(vb) - np.mean(va)),
                    "hedges_g": hedges_g(va, vb),
                    "welch_t": float(t),
                    "p_value": float(p),
                    "total_spliced_junction_reads": total_junction,
                }
            )

        event_df = pd.DataFrame(rows)
        if not event_df.empty:
            event_df["fdr_bh"] = bh_fdr(event_df["p_value"].to_numpy())
            event_df = event_df.sort_values(
                ["fdr_bh", "delta_PEI_b_minus_a"],
                ascending=[True, contrast["expected_direction"] != "positive"],
            )
            event_path = results_dir / "contrasts" / f"{contrast['name']}.per_intron.tsv"
            event_path.parent.mkdir(parents=True, exist_ok=True)
            event_df.to_csv(event_path, sep="\t", index=False)

        contrast_summary.append(
            {
                **contrast,
                "n_group_a": len(sample_a),
                "n_group_b": len(sample_b),
                "mean_sample_score_group_a": np.mean(sample_a) if len(sample_a) else np.nan,
                "mean_sample_score_group_b": np.mean(sample_b) if len(sample_b) else np.nan,
                "delta_sample_score_b_minus_a": sample_delta,
                "welch_t_sample_score": t_stat,
                "welch_p_sample_score": sample_p,
                "mannwhitney_u_sample_score": mw_stat,
                "mannwhitney_p_sample_score": sample_mw_p,
                "hedges_g_sample_score": hedges_g(sample_a, sample_b),
                "direction_gate_pass": bool(direction_pass),
                "n_tested_introns": len(event_df),
                "n_fdr_lt_0_05": int((event_df["fdr_bh"] < 0.05).sum()) if not event_df.empty else 0,
            }
        )

    summary_df = pd.DataFrame(contrast_summary)
    summary_df.to_csv(results_dir / "contrast_summary.tsv", sep="\t", index=False)
    write_gate_report(root, manifest, summary_df)


def write_gate_report(
    root: Path,
    manifest: pd.DataFrame,
    summary_df: pd.DataFrame,
) -> None:
    results_dir = root / "results"
    lines: List[str] = []
    lines.append("# HGPS + metazoan CR pre-mRNA exposure gate report")
    lines.append("")
    lines.append(f"Pipeline version: `{PIPELINE_VERSION}`")
    lines.append("")
    lines.append("## Claim boundary")
    lines.append("")
    lines.append(
        "This analysis tests intron-containing / incompletely processed RNA exposure. "
        "It does not prove nuclear export, translation, or NMD degradation in human or mouse samples."
    )
    lines.append("")
    lines.append(
        "HGPS is treated as a sensitized perturbation of nuclear organization, not as a synonym "
        "for physiological aging and not as evidence that aging is damage."
    )
    lines.append("")
    lines.append("## Dataset manifest")
    lines.append("")
    manifest_counts = (
        manifest.groupby(["dataset", "group"]).size().rename("runs").reset_index()
    )
    lines.append(manifest_counts.to_markdown(index=False))
    lines.append("")
    lines.append("## Sample-level contrasts")
    lines.append("")
    report_columns = [
        "name",
        "interpretation",
        "delta_sample_score_b_minus_a",
        "welch_p_sample_score",
        "hedges_g_sample_score",
        "direction_gate_pass",
        "n_tested_introns",
        "n_fdr_lt_0_05",
    ]
    lines.append(summary_df[report_columns].to_markdown(index=False))
    lines.append("")
    lines.append("## Main-figure gates")
    lines.append("")

    required = {
        "HGPS discovery": ["HGPS_vs_control", "HGPS_control_vs_normal_control"],
        "HGPS intervention": [
            "HGPS_FTI_vs_HGPS_control",
            "HGPS_PML2KD_vs_HGPS_control",
        ],
        "Metazoan CR": ["BAT_CR_vs_control", "SkM_CR_vs_control"],
    }
    for gate_name, contrast_names in required.items():
        rows = summary_df.loc[summary_df["name"].isin(contrast_names)]
        passed = bool(len(rows) and rows["direction_gate_pass"].all())
        lines.append(f"- **{gate_name}: {'PASS' if passed else 'NO DATA / FAIL'}**")
    lines.append("")
    lines.append(
        "Main Figure 5 is justified only if the HGPS direction replicates, at least one "
        "HGPS intervention moves the score toward control, and at least one bona fide "
        "metazoan CR tissue reduces the prespecified score."
    )
    lines.append("")
    lines.append("## Render status")
    lines.append("")
    lines.append(
        "No manuscript figure was rendered. Plot, label, legend, x-tick, group-label, "
        "right-stat and footer lanes remain intentionally empty until the numerical gates pass."
    )
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append("- `sample_pre_mrna_exposure_scores.tsv`")
    lines.append("- `contrast_summary.tsv`")
    lines.append("- `contrasts/*.per_intron.tsv`")
    lines.append("- `alignment_qc.tsv`")
    lines.append("- `all_intron_measurements.parquet`")
    (results_dir / "GATE_REPORT.md").write_text("\n".join(lines) + "\n")


def execute(root: Path, threads: int, audit_only: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "metadata").mkdir(exist_ok=True)
    manifest = build_manifest(root)
    print(manifest.groupby(["dataset", "group"]).size())

    if audit_only:
        print(
            f"Metadata audit complete: {root / 'metadata' / 'run_manifest.tsv'}",
            flush=True,
        )
        return

    require_executables(["STAR", "samtools", "prefetch", "fasterq-dump"])

    references: Dict[str, Tuple[Path, Path, Path]] = {}
    introns_by_species: Dict[str, pd.DataFrame] = {}
    for species in sorted(manifest["species"].unique()):
        references[species] = prepare_reference(root, species, threads)
        _, gtf, _ = references[species]
        intron_cache = (
            root
            / "reference"
            / species
            / f"gencode_{GENCODE[species]['release']}"
            / "representative_protein_coding_introns.tsv"
        )
        introns_by_species[species] = representative_introns(gtf, intron_cache)

    for row in manifest.itertuples(index=False):
        _, gtf, index_dir = references[row.species]
        bam = align_run(root, pd.Series(row._asdict()), index_dir, gtf, threads)
        output_path = root / "quantification" / row.dataset / f"{row.run}.introns.tsv"
        quantify_bam(bam, introns_by_species[row.species], output_path)

    analyse(root, manifest)
    print(f"Complete. Gate report: {root / 'results' / 'GATE_REPORT.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run public HGPS and metazoan CR pre-mRNA exposure analysis."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Euler project root for metadata, raw data, alignments and results.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=max(2, os.cpu_count() or 2),
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Resolve and validate metadata without downloading raw reads.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    execute(args.root.resolve(), max(2, args.threads), args.audit_only)


if __name__ == "__main__":
    main()
