#!/usr/bin/env python3
"""
Distributed JM105-compatible HGPS + metazoan caloric-restriction analysis.

Scientific contract
-------------------
The primary retained-intron metric is the exact JM105 metric:

    JM105_IR = (EI + IE) / ((EI + IE) + 2 * EE_total)

EI and IE are unique fragment/read names spanning the two unspliced
exon-intron boundaries. EE_total is the unique fragment/read-name count
carrying the exact annotated exon-exon splice junction. No pseudocount is used
for JM105_IR. An event with zero informative denominator is NA.

PEI = log2((EI + IE + 0.5) / (2 * EE_total + 0.5)) is retained only as a
secondary numerical sensitivity measure; it is never the primary effect scale.

Important design boundary
-------------------------
These human and mouse public datasets do not contain matched UPF1/NMD-on and
NMD-off samples. Therefore this workflow measures steady-state retained-intron
or intron-containing RNA exposure. It does not compute NMD_hidden and does not
claim nuclear export, translation, or NMD degradation.

HPC design
----------
- Metadata audit: quick setup action.
- Reference preparation: one human and one mouse job in parallel.
- Sample processing: one Slurm array task per run, distributed across nodes.
- Quantification: name-sort each BAM, scan it once, and count all introns in a
  single pass. This replaces the previous one-bam-fetch-per-intron algorithm.
- Aggregation: one dependency job after every array task succeeds.

No figure is rendered by this script.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import pysam
from scipy import stats

import run_hgps_metazoan_conservation_manifest_hotfix as patched

core = patched.core

VERSION = "2026-07-20.5-distributed"
BOUNDARY_FLANK = 8
PRIMARY_MIN_MAX_SAMPLE_RAW_SUPPORT = 10
PSEUDOCOUNT_SECONDARY = 0.5

CONTRASTS = [
    {
        "dataset": "GSE118633",
        "name": "HGPS_vs_control",
        "group_a": "control",
        "group_b": "hgps",
        "expected_direction": "positive",
        "interpretation": "HGPS-associated steady-state retained-intron exposure",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_control_vs_normal_control",
        "group_a": "normal_control",
        "group_b": "hgps_control",
        "expected_direction": "positive",
        "interpretation": "HGPS-associated steady-state retained-intron exposure",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_FTI_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_fti",
        "expected_direction": "negative",
        "interpretation": "movement toward normal after lonafarnib plus zoledronate",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_PML2KD_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_pml2_kd",
        "expected_direction": "negative",
        "interpretation": "movement toward normal after PML2 knockdown",
    },
    {
        "dataset": "GSE137083",
        "name": "HGPS_panPMLKD_vs_HGPS_control",
        "group_a": "hgps_control",
        "group_b": "hgps_pan_pml_kd",
        "expected_direction": "negative",
        "interpretation": "movement toward normal after pan-PML knockdown",
    },
    {
        "dataset": "GSE222163",
        "name": "BAT_CR_vs_control",
        "group_a": "bat_control",
        "group_b": "bat_cr",
        "expected_direction": "negative",
        "interpretation": "caloric-restriction effect in brown adipose tissue",
    },
    {
        "dataset": "GSE222163",
        "name": "SkM_CR_vs_control",
        "group_a": "skm_control",
        "group_b": "skm_cr",
        "expected_direction": "negative",
        "interpretation": "caloric-restriction effect in skeletal muscle",
    },
]


def run_command(command: Sequence[str], cwd: Optional[Path] = None) -> None:
    printable = " ".join(str(x) for x in command)
    print(f"[RUN] {printable}", flush=True)
    subprocess.run([str(x) for x in command], cwd=cwd, check=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(root: Path) -> pd.DataFrame:
    frozen = root / "metadata" / "run_manifest.distributed.tsv"
    normal = root / "metadata" / "run_manifest.tsv"
    path = frozen if frozen.exists() else normal
    if not path.exists():
        raise FileNotFoundError(
            f"No run manifest found at {frozen} or {normal}. Run the audit command first."
        )
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    required = {"dataset", "species", "run", "group"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"Manifest lacks required columns: {missing}")
    return df.sort_values(["species", "dataset", "group", "run"]).reset_index(drop=True)


def command_audit(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    manifest = core.build_manifest(root)
    manifest = manifest.sort_values(
        ["species", "dataset", "group", "run"]
    ).reset_index(drop=True)
    frozen = root / "metadata" / "run_manifest.distributed.tsv"
    manifest.to_csv(frozen, sep="\t", index=False)

    counts = manifest.groupby(["dataset", "group"]).size().rename("runs")
    print(counts.to_string(), flush=True)

    expected_total = 34
    observed_total = len(manifest)
    if observed_total != expected_total:
        raise RuntimeError(
            f"Expected exactly {expected_total} prespecified runs after the evidence-backed "
            f"manifest gate, observed {observed_total}. Inspect {frozen}."
        )

    contract = {
        "pipeline_version": VERSION,
        "manifest_sha256": sha256_file(frozen),
        "n_runs": observed_total,
        "primary_metric": "JM105_IR = (EI + IE) / ((EI + IE) + 2 * EE_total)",
        "primary_pseudocount": 0,
        "zero_denominator": "NA",
        "secondary_metric": "PEI = log2((EI + IE + 0.5) / (2 * EE_total + 0.5))",
        "nmd_hidden_estimable": False,
        "reason_nmd_hidden_not_estimable": "No matched UPF1/NMD-on and NMD-off design in these public datasets.",
        "quantification": "unique query names after name sorting; one-pass BAM scan",
    }
    contract_path = root / "metadata" / "JM105_COMPATIBILITY_CONTRACT.json"
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen distributed manifest: {frozen}", flush=True)
    print(f"JM105 compatibility contract: {contract_path}", flush=True)


def reference_paths(root: Path, species: str) -> Tuple[Path, Path, Path, Path]:
    cfg = core.GENCODE[species]
    ref_dir = root / "reference" / species / f"gencode_{cfg['release']}"
    fasta = ref_dir / cfg["fasta_name"]
    gtf = ref_dir / cfg["gtf_name"]
    index_dir = ref_dir / "STAR_index"
    intron_path = ref_dir / "representative_protein_coding_introns.tsv"
    return fasta, gtf, index_dir, intron_path


def validate_star_index(index_dir: Path) -> None:
    required = ["Genome", "SA", "SAindex", "genomeParameters.txt"]
    missing = [name for name in required if not (index_dir / name).exists()]
    if missing:
        raise RuntimeError(f"Incomplete STAR index at {index_dir}; missing {missing}")


def command_prepare_reference(root: Path, species: str, threads: int) -> None:
    if species not in core.GENCODE:
        raise KeyError(f"Unsupported species: {species}")
    _, _, existing_index_dir, _ = reference_paths(root, species)
    if existing_index_dir.exists():
        required = ["Genome", "SA", "SAindex", "genomeParameters.txt"]
        if any(not (existing_index_dir / name).exists() for name in required):
            print(
                f"[REBUILD] Removing incomplete STAR index: {existing_index_dir}",
                flush=True,
            )
            shutil.rmtree(existing_index_dir)
    _, gtf, index_dir = core.prepare_reference(root, species, threads)
    validate_star_index(index_dir)
    _, _, _, intron_path = reference_paths(root, species)
    introns = core.representative_introns(gtf, intron_path)
    if introns.empty:
        raise RuntimeError(f"No representative introns generated for {species}")
    ready = {
        "species": species,
        "pipeline_version": VERSION,
        "star_index": str(index_dir),
        "representative_intron_table": str(intron_path),
        "n_introns": int(len(introns)),
        "intron_table_sha256": sha256_file(intron_path),
    }
    ready_path = index_dir.parent / "REFERENCE_READY.json"
    ready_path.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(ready, indent=2), flush=True)


def fastq_paths(directory: Path, run: str) -> Tuple[Path, Optional[Path]]:
    paired_1 = directory / f"{run}_1.fastq"
    paired_2 = directory / f"{run}_2.fastq"
    single = directory / f"{run}.fastq"
    if paired_1.exists():
        return paired_1, paired_2 if paired_2.exists() else None
    if single.exists():
        return single, None
    raise FileNotFoundError(f"fasterq-dump did not produce FASTQ for {run} in {directory}")


def download_fastq_to_tmp(root: Path, run: str, tmpdir: Path, threads: int) -> Tuple[Path, Optional[Path]]:
    sra_dir = root / "raw" / "sra"
    sra_dir.mkdir(parents=True, exist_ok=True)
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
    sra_file = sra_dir / run / f"{run}.sra"
    source = sra_file if sra_file.exists() else sra_dir / run
    fastq_dir = tmpdir / "fastq"
    fasterq_tmp = tmpdir / "fasterq_tmp"
    fastq_dir.mkdir(parents=True, exist_ok=True)
    fasterq_tmp.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "fasterq-dump",
            "--split-files",
            "--threads",
            str(max(2, min(threads, 8))),
            "--temp",
            str(fasterq_tmp),
            "--outdir",
            str(fastq_dir),
            str(source),
        ]
    )
    return fastq_paths(fastq_dir, run)


def align_sample(
    root: Path,
    row: pd.Series,
    threads: int,
    tmpdir: Path,
) -> Path:
    run = str(row["run"])
    dataset = str(row["dataset"])
    species = str(row["species"])
    _, gtf, index_dir, _ = reference_paths(root, species)
    validate_star_index(index_dir)

    output_dir = root / "alignment" / dataset / run
    output_dir.mkdir(parents=True, exist_ok=True)
    bam = output_dir / "Aligned.sortedByCoord.out.bam"
    bai = Path(str(bam) + ".bai")
    if bam.exists() and bam.stat().st_size > 0 and bai.exists():
        print(f"[SKIP] Existing aligned and indexed BAM: {bam}", flush=True)
        return bam

    r1, r2 = download_fastq_to_tmp(root, run, tmpdir, threads)
    star_tmp = tmpdir / "STARtmp"
    if star_tmp.exists():
        shutil.rmtree(star_tmp)

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
            "--outTmpDir",
            str(star_tmp),
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
            "12000000000",
        ]
    )
    run_command(command)
    run_command(["samtools", "index", "-@", str(min(threads, 8)), str(bam)])
    if not bam.exists() or not bai.exists():
        raise RuntimeError(f"STAR or samtools failed to create {bam} and its index")
    return bam


def build_event_indexes(
    introns: pd.DataFrame,
) -> Tuple[
    Dict[str, List[int]],
    Dict[str, Dict[int, List[Tuple[int, str]]]],
    Dict[str, Dict[Tuple[int, int], List[int]]],
]:
    boundary_positions: Dict[str, set[int]] = defaultdict(set)
    boundary_events: Dict[str, Dict[int, List[Tuple[int, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    junction_events: Dict[str, Dict[Tuple[int, int], List[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for idx, row in enumerate(introns.itertuples(index=False)):
        chrom = str(row.chrom)
        start0 = int(row.start0)
        end0 = int(row.end0)
        boundary_positions[chrom].add(start0)
        boundary_positions[chrom].add(end0)
        boundary_events[chrom][start0].append((idx, "EI"))
        boundary_events[chrom][end0].append((idx, "IE"))
        junction_events[chrom][(start0, end0)].append(idx)
    sorted_positions = {
        chrom: sorted(positions) for chrom, positions in boundary_positions.items()
    }
    return sorted_positions, boundary_events, junction_events


def read_junctions(read: pysam.AlignedSegment) -> Iterator[Tuple[int, int]]:
    if read.is_unmapped or not read.cigartuples:
        return
    ref = int(read.reference_start)
    for operation, length in read.cigartuples:
        if operation in {0, 2, 7, 8}:
            ref += int(length)
        elif operation == 3:
            donor = ref
            acceptor = ref + int(length)
            yield donor, acceptor
            ref = acceptor
        elif operation in {1, 4, 5, 6}:
            continue


def quantify_name_sorted_bam(
    name_bam: Path,
    introns: pd.DataFrame,
    row: pd.Series,
    output_path: Path,
) -> pd.DataFrame:
    sorted_positions, boundary_events, junction_events = build_event_indexes(introns)
    n = len(introns)
    ei = np.zeros(n, dtype=np.int64)
    ie = np.zeros(n, dtype=np.int64)
    ee = np.zeros(n, dtype=np.int64)

    current_name: Optional[str] = None
    fragment_ei: set[int] = set()
    fragment_ie: set[int] = set()
    fragment_ee: set[int] = set()
    primary_alignments = 0
    informative_fragments = 0

    def flush_fragment() -> None:
        nonlocal informative_fragments
        if fragment_ei or fragment_ie or fragment_ee:
            informative_fragments += 1
        for idx in fragment_ei:
            ei[idx] += 1
        for idx in fragment_ie:
            ie[idx] += 1
        for idx in fragment_ee:
            ee[idx] += 1

    with pysam.AlignmentFile(name_bam, "rb") as bam:
        for read in bam.fetch(until_eof=True):
            if read.is_unmapped or read.is_secondary or read.is_supplementary:
                continue
            query_name = str(read.query_name)
            if current_name is None:
                current_name = query_name
            elif query_name != current_name:
                flush_fragment()
                fragment_ei.clear()
                fragment_ie.clear()
                fragment_ee.clear()
                current_name = query_name

            primary_alignments += 1
            chrom = bam.get_reference_name(read.reference_id)
            positions = sorted_positions.get(chrom)
            if positions:
                for block_start, block_end in read.get_blocks():
                    low = int(block_start) + BOUNDARY_FLANK
                    high = int(block_end) - BOUNDARY_FLANK
                    if low > high:
                        continue
                    left_i = bisect.bisect_left(positions, low)
                    right_i = bisect.bisect_right(positions, high)
                    for boundary in positions[left_i:right_i]:
                        for intron_idx, event_type in boundary_events[chrom][boundary]:
                            if event_type == "EI":
                                fragment_ei.add(intron_idx)
                            else:
                                fragment_ie.add(intron_idx)

            chrom_junctions = junction_events.get(chrom)
            if chrom_junctions:
                for donor, acceptor in read_junctions(read):
                    for intron_idx in chrom_junctions.get((donor, acceptor), []):
                        fragment_ee.add(intron_idx)

    if current_name is not None:
        flush_fragment()

    result = introns.copy()
    result["dataset"] = str(row["dataset"])
    result["run"] = str(row["run"])
    result["group"] = str(row["group"])
    result["species"] = str(row["species"])
    result["EI"] = ei
    result["IE"] = ie
    result["EE_total"] = ee
    result["unspliced_boundary_total"] = ei + ie
    result["raw_support"] = ei + ie + ee
    result["JM105_IR_denominator"] = ei + ie + 2 * ee
    denominator = result["JM105_IR_denominator"].to_numpy(dtype=float)
    numerator = result["unspliced_boundary_total"].to_numpy(dtype=float)
    result["JM105_IR"] = np.divide(
        numerator,
        denominator,
        out=np.full(len(result), np.nan, dtype=float),
        where=denominator > 0,
    )
    result["PEI_secondary"] = np.log2(
        (numerator + PSEUDOCOUNT_SECONDARY)
        / (2.0 * ee.astype(float) + PSEUDOCOUNT_SECONDARY)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, sep="\t", index=False, compression="gzip")
    stats_path = output_path.with_suffix("").with_suffix(".scan.json")
    stats_path.write_text(
        json.dumps(
            {
                "run": str(row["run"]),
                "primary_alignments_scanned": primary_alignments,
                "informative_fragments": informative_fragments,
                "n_introns": n,
                "n_introns_with_nonzero_denominator": int((denominator > 0).sum()),
                "primary_metric": "JM105_IR",
                "pseudocount": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def parse_star_qc(log_path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if not log_path.exists():
        return result
    for line in log_path.read_text(errors="replace").splitlines():
        if "|" not in line:
            continue
        key, value = [part.strip() for part in line.split("|", 1)]
        result[key] = value
    return result


def command_process_sample(root: Path, task_index: int, threads: int, tmpdir: Path) -> None:
    manifest = load_manifest(root)
    if task_index < 1 or task_index > len(manifest):
        raise IndexError(f"Task index {task_index} is outside 1..{len(manifest)}")
    row = manifest.iloc[task_index - 1]
    run = str(row["run"])
    dataset = str(row["dataset"])
    species = str(row["species"])
    print(
        f"Processing task {task_index}/{len(manifest)}: {dataset} {run} "
        f"{row['group']} {species}",
        flush=True,
    )

    complete_dir = root / "status" / "sample_complete"
    complete_dir.mkdir(parents=True, exist_ok=True)
    complete_path = complete_dir / f"{run}.json"
    output_path = root / "quantification" / dataset / f"{run}.introns.tsv.gz"
    if complete_path.exists() and output_path.exists() and output_path.stat().st_size > 0:
        print(f"[SKIP] Complete sample marker exists: {complete_path}", flush=True)
        return

    tmpdir = tmpdir / run
    tmpdir.mkdir(parents=True, exist_ok=True)
    bam = align_sample(root, row, threads, tmpdir)

    _, _, _, intron_path = reference_paths(root, species)
    if not intron_path.exists():
        raise FileNotFoundError(intron_path)
    introns = pd.read_csv(intron_path, sep="\t")

    name_bam = tmpdir / f"{run}.queryname.bam"
    if not name_bam.exists():
        run_command(
            [
                "samtools",
                "sort",
                "-n",
                "-@",
                str(min(4, threads)),
                "-m",
                "3G",
                "-T",
                str(tmpdir / f"{run}.namesort.tmp"),
                "-o",
                str(name_bam),
                str(bam),
            ]
        )
    quantify_name_sorted_bam(name_bam, introns, row, output_path)

    qc = {
        "dataset": dataset,
        "run": run,
        "group": str(row["group"]),
        "species": species,
        **parse_star_qc(bam.parent / "Log.final.out"),
    }
    qc_path = root / "quantification" / dataset / f"{run}.alignment_qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")

    complete = {
        "pipeline_version": VERSION,
        "task_index": task_index,
        "dataset": dataset,
        "run": run,
        "group": str(row["group"]),
        "species": species,
        "bam": str(bam),
        "bam_sha256": sha256_file(bam),
        "quantification": str(output_path),
        "quantification_sha256": sha256_file(output_path),
        "primary_metric": "JM105_IR",
        "primary_pseudocount": 0,
    }
    complete_path.write_text(json.dumps(complete, indent=2) + "\n", encoding="utf-8")
    if name_bam.exists():
        name_bam.unlink()
    print(f"Sample complete: {complete_path}", flush=True)


def bh_fdr(pvalues: Sequence[float]) -> np.ndarray:
    values = np.asarray(pvalues, dtype=float)
    output = np.full(len(values), np.nan, dtype=float)
    valid = np.isfinite(values)
    if not valid.any():
        return output
    p = values[valid]
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0.0, 1.0)
    restored = np.empty(len(ranked), dtype=float)
    restored[order] = adjusted
    output[np.flatnonzero(valid)] = restored
    return output


def hedges_g(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled_num = (len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)
    pooled_den = len(a) + len(b) - 2
    if pooled_den <= 0 or pooled_num <= 0:
        return 0.0
    pooled_sd = math.sqrt(pooled_num / pooled_den)
    d = (float(np.mean(b)) - float(np.mean(a))) / pooled_sd
    correction = 1.0 - 3.0 / (4.0 * (len(a) + len(b)) - 9.0)
    return d * correction


def safe_welch(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float]:
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    aa = aa[np.isfinite(aa)]
    bb = bb[np.isfinite(bb)]
    if len(aa) < 2 or len(bb) < 2:
        return float("nan"), float("nan")
    statistic, pvalue = stats.ttest_ind(aa, bb, equal_var=False, nan_policy="omit")
    return float(statistic), float(pvalue)


def safe_mannwhitney(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float]:
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    aa = aa[np.isfinite(aa)]
    bb = bb[np.isfinite(bb)]
    if len(aa) < 1 or len(bb) < 1:
        return float("nan"), float("nan")
    statistic, pvalue = stats.mannwhitneyu(aa, bb, alternative="two-sided")
    return float(statistic), float(pvalue)


def read_all_quantifications(root: Path, manifest: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    missing: List[str] = []
    for row in manifest.itertuples(index=False):
        path = root / "quantification" / row.dataset / f"{row.run}.introns.tsv.gz"
        if not path.exists() or path.stat().st_size == 0:
            missing.append(str(path))
            continue
        frame = pd.read_csv(path, sep="\t", compression="gzip")
        frames.append(frame)
    if missing:
        raise RuntimeError(
            "Aggregation cannot start because sample outputs are missing:\n"
            + "\n".join(missing)
        )
    return pd.concat(frames, ignore_index=True)


def event_table_for_contrast(
    all_data: pd.DataFrame,
    contrast: dict,
    sample_score_rows: List[dict],
) -> Tuple[pd.DataFrame, dict]:
    subset = all_data.loc[
        (all_data["dataset"] == contrast["dataset"])
        & (all_data["group"].isin([contrast["group_a"], contrast["group_b"]]))
    ].copy()
    if subset.empty:
        raise RuntimeError(f"No rows for contrast {contrast['name']}")

    pivot_ir = subset.pivot(index="intron_id", columns="run", values="JM105_IR")
    pivot_raw = subset.pivot(index="intron_id", columns="run", values="raw_support")
    metadata = subset.drop_duplicates("intron_id").set_index("intron_id")
    runs_a = sorted(subset.loc[subset["group"] == contrast["group_a"], "run"].unique())
    runs_b = sorted(subset.loc[subset["group"] == contrast["group_b"], "run"].unique())

    required_runs = runs_a + runs_b
    matched = pivot_ir[required_runs].notna().all(axis=1)
    support = pivot_raw[required_runs].max(axis=1) >= PRIMARY_MIN_MAX_SAMPLE_RAW_SUPPORT
    universe_ids = pivot_ir.index[matched & support]
    if len(universe_ids) == 0:
        raise RuntimeError(
            f"Zero introns passed the matched-value and support gates for {contrast['name']}"
        )

    for run in required_runs:
        run_group = contrast["group_a"] if run in runs_a else contrast["group_b"]
        values = pivot_ir.loc[universe_ids, run].to_numpy(dtype=float)
        pei_values = subset.loc[
            (subset["run"] == run) & subset["intron_id"].isin(universe_ids),
            "PEI_secondary",
        ].to_numpy(dtype=float)
        sample_score_rows.append(
            {
                "contrast": contrast["name"],
                "dataset": contrast["dataset"],
                "run": run,
                "group": run_group,
                "n_introns_in_fixed_universe": len(universe_ids),
                "median_JM105_IR": float(np.nanmedian(values)),
                "mean_JM105_IR": float(np.nanmean(values)),
                "median_PEI_secondary": float(np.nanmedian(pei_values)),
            }
        )

    records: List[dict] = []
    for intron_id in universe_ids:
        values_a = pivot_ir.loc[intron_id, runs_a].to_numpy(dtype=float)
        values_b = pivot_ir.loc[intron_id, runs_b].to_numpy(dtype=float)
        t_stat, p_value = safe_welch(values_a, values_b)
        base = metadata.loc[intron_id]
        records.append(
            {
                "intron_id": intron_id,
                "gene_id": base.get("gene_id", ""),
                "gene_name": base.get("gene_name", ""),
                "transcript_id": base.get("transcript_id", ""),
                "chrom": base.get("chrom", ""),
                "start0": base.get("start0", ""),
                "end0": base.get("end0", ""),
                "strand": base.get("strand", ""),
                "n_group_a": len(values_a),
                "n_group_b": len(values_b),
                "mean_JM105_IR_group_a": float(np.mean(values_a)),
                "mean_JM105_IR_group_b": float(np.mean(values_b)),
                "delta_JM105_IR_b_minus_a": float(np.mean(values_b) - np.mean(values_a)),
                "hedges_g": hedges_g(values_a, values_b),
                "welch_t": t_stat,
                "p_value": p_value,
                "max_sample_raw_support": int(pivot_raw.loc[intron_id, required_runs].max()),
            }
        )
    event_df = pd.DataFrame(records)
    event_df["fdr_bh"] = bh_fdr(event_df["p_value"].to_numpy(dtype=float))
    ascending_effect = contrast["expected_direction"] != "positive"
    event_df = event_df.sort_values(
        ["fdr_bh", "delta_JM105_IR_b_minus_a"],
        ascending=[True, ascending_effect],
    )

    scores = pd.DataFrame(sample_score_rows)
    this_scores = scores.loc[scores["contrast"] == contrast["name"]]
    sample_a = this_scores.loc[
        this_scores["group"] == contrast["group_a"], "median_JM105_IR"
    ].to_numpy(dtype=float)
    sample_b = this_scores.loc[
        this_scores["group"] == contrast["group_b"], "median_JM105_IR"
    ].to_numpy(dtype=float)
    t_stat, p_value = safe_welch(sample_a, sample_b)
    mw_stat, mw_p = safe_mannwhitney(sample_a, sample_b)
    delta = float(np.mean(sample_b) - np.mean(sample_a))
    direction_pass = delta > 0 if contrast["expected_direction"] == "positive" else delta < 0
    summary = {
        **contrast,
        "n_group_a": len(sample_a),
        "n_group_b": len(sample_b),
        "n_introns_fixed_universe": len(universe_ids),
        "mean_sample_median_JM105_IR_group_a": float(np.mean(sample_a)),
        "mean_sample_median_JM105_IR_group_b": float(np.mean(sample_b)),
        "delta_sample_median_JM105_IR_b_minus_a": delta,
        "welch_t_sample_score": t_stat,
        "welch_p_sample_score": p_value,
        "mannwhitney_u_sample_score": mw_stat,
        "mannwhitney_p_sample_score": mw_p,
        "hedges_g_sample_score": hedges_g(sample_a, sample_b),
        "direction_gate_pass": bool(direction_pass),
        "n_event_fdr_lt_0_05": int((event_df["fdr_bh"] < 0.05).sum()),
    }
    return event_df, summary


def gather_alignment_qc(root: Path, manifest: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []
    for row in manifest.itertuples(index=False):
        path = root / "quantification" / row.dataset / f"{row.run}.alignment_qc.json"
        if path.exists():
            rows.append(json.loads(path.read_text(encoding="utf-8")))
    return pd.DataFrame(rows)


def gather_host_gene_counts(root: Path, manifest: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for row in manifest.itertuples(index=False):
        path = root / "alignment" / row.dataset / row.run / "ReadsPerGene.out.tab"
        if not path.exists():
            continue
        table = pd.read_csv(
            path,
            sep="\t",
            header=None,
            names=["gene_id", "unstranded", "forward", "reverse"],
        )
        table = table.loc[~table["gene_id"].astype(str).str.startswith("N_")].copy()
        table["dataset"] = row.dataset
        table["run"] = row.run
        table["group"] = row.group
        table["species"] = row.species
        frames.append(table)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def gate_status(summary_df: pd.DataFrame) -> Dict[str, bool]:
    by_name = summary_df.set_index("name")["direction_gate_pass"].to_dict()
    discovery = bool(
        by_name.get("HGPS_vs_control", False)
        and by_name.get("HGPS_control_vs_normal_control", False)
    )
    intervention = any(
        bool(by_name.get(name, False))
        for name in [
            "HGPS_FTI_vs_HGPS_control",
            "HGPS_PML2KD_vs_HGPS_control",
            "HGPS_panPMLKD_vs_HGPS_control",
        ]
    )
    metazoan_cr = any(
        bool(by_name.get(name, False))
        for name in ["BAT_CR_vs_control", "SkM_CR_vs_control"]
    )
    return {
        "HGPS direction replicated": discovery,
        "At least one HGPS intervention moves toward normal": intervention,
        "At least one mouse CR tissue reduces JM105_IR": metazoan_cr,
        "All three main-figure gates": discovery and intervention and metazoan_cr,
    }


def write_gate_report(
    root: Path,
    manifest: pd.DataFrame,
    summary_df: pd.DataFrame,
) -> None:
    results_dir = root / "results"
    statuses = gate_status(summary_df)
    lines: List[str] = [
        "# HGPS + metazoan CR JM105-compatible retained-intron report",
        "",
        f"Pipeline version: `{VERSION}`",
        "",
        "## Primary metric",
        "",
        "`JM105_IR = (EI + IE) / ((EI + IE) + 2 × EE_total)`",
        "",
        "The primary metric has no pseudocount. Zero-denominator events are NA. "
        "EI, IE and EE_total are unique query-name counts after query-name sorting.",
        "",
        "PEI with a 0.5 continuity correction is retained only as a secondary "
        "sensitivity measure and does not drive the gates.",
        "",
        "## JM105 similarity and boundary",
        "",
        "The EI/IE/EE_total counting logic, sample-level IR preservation and IR formula "
        "match the JM105 figure specification. These public mammalian datasets lack "
        "matched UPF1/NMD-on and NMD-off conditions, so NMD_hidden cannot be calculated. "
        "The result is steady-state retained-intron exposure, not direct proof of export, "
        "translation or NMD degradation.",
        "",
        "## Manifest",
        "",
        manifest.groupby(["dataset", "group"]).size().rename("runs").reset_index().to_markdown(index=False),
        "",
        "## Sample-level contrast results",
        "",
        summary_df[
            [
                "name",
                "interpretation",
                "n_group_a",
                "n_group_b",
                "n_introns_fixed_universe",
                "delta_sample_median_JM105_IR_b_minus_a",
                "welch_p_sample_score",
                "hedges_g_sample_score",
                "direction_gate_pass",
                "n_event_fdr_lt_0_05",
            ]
        ].to_markdown(index=False),
        "",
        "Direction gates test the prespecified sign. P values and effect sizes are reported "
        "separately; a sign gate is not presented as statistical significance.",
        "",
        "## Main-figure gates",
        "",
    ]
    for label, passed in statuses.items():
        lines.append(f"- **{label}: {'PASS' if passed else 'FAIL'}**")
    lines.extend(
        [
            "",
            "## Render status",
            "",
            "No manuscript figure was rendered. Descriptor/title, plot, label, legend, "
            "x-tick, group-label, right-stat and footer lanes remain empty until the "
            "numerical results are reviewed.",
            "",
            "## Output inventory",
            "",
            "- `all_intron_measurements.parquet`",
            "- `sample_JM105_IR_scores.tsv`",
            "- `contrast_summary.tsv`",
            "- `contrasts/*.per_intron.tsv.gz`",
            "- `alignment_qc.tsv`",
            "- `host_gene_counts.tsv.gz`",
        ]
    )
    (results_dir / "GATE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def command_aggregate(root: Path) -> None:
    manifest = load_manifest(root)
    all_data = read_all_quantifications(root, manifest)
    results_dir = root / "results"
    contrast_dir = results_dir / "contrasts"
    results_dir.mkdir(parents=True, exist_ok=True)
    contrast_dir.mkdir(parents=True, exist_ok=True)

    all_data.to_parquet(results_dir / "all_intron_measurements.parquet", index=False)
    sample_score_rows: List[dict] = []
    summaries: List[dict] = []
    for contrast in CONTRASTS:
        event_df, summary = event_table_for_contrast(
            all_data,
            contrast,
            sample_score_rows,
        )
        event_df.to_csv(
            contrast_dir / f"{contrast['name']}.per_intron.tsv.gz",
            sep="\t",
            index=False,
            compression="gzip",
        )
        summaries.append(summary)

    sample_scores = pd.DataFrame(sample_score_rows)
    sample_scores.to_csv(results_dir / "sample_JM105_IR_scores.tsv", sep="\t", index=False)
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(results_dir / "contrast_summary.tsv", sep="\t", index=False)

    qc = gather_alignment_qc(root, manifest)
    qc.to_csv(results_dir / "alignment_qc.tsv", sep="\t", index=False)
    host_counts = gather_host_gene_counts(root, manifest)
    if not host_counts.empty:
        host_counts.to_csv(
            results_dir / "host_gene_counts.tsv.gz",
            sep="\t",
            index=False,
            compression="gzip",
        )
    write_gate_report(root, manifest, summary_df)
    complete = {
        "pipeline_version": VERSION,
        "manifest_runs": len(manifest),
        "quantification_files": len(manifest),
        "results_dir": str(results_dir),
        "gate_status": gate_status(summary_df),
    }
    (results_dir / "AGGREGATION_COMPLETE.json").write_text(
        json.dumps(complete, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Aggregation complete: {results_dir / 'GATE_REPORT.md'}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit")
    audit.add_argument("--root", type=Path, required=True)

    reference = sub.add_parser("prepare-reference")
    reference.add_argument("--root", type=Path, required=True)
    reference.add_argument("--species", choices=sorted(core.GENCODE), required=True)
    reference.add_argument("--threads", type=int, required=True)

    sample = sub.add_parser("process-sample")
    sample.add_argument("--root", type=Path, required=True)
    sample.add_argument("--task-index", type=int, required=True)
    sample.add_argument("--threads", type=int, required=True)
    sample.add_argument("--tmpdir", type=Path, required=True)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--root", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = args.root.resolve()
    if args.command == "audit":
        command_audit(root)
    elif args.command == "prepare-reference":
        command_prepare_reference(root, args.species, max(2, args.threads))
    elif args.command == "process-sample":
        command_process_sample(
            root,
            args.task_index,
            max(2, args.threads),
            args.tmpdir.resolve(),
        )
    elif args.command == "aggregate":
        command_aggregate(root)
    else:
        raise AssertionError(args.command)


if __name__ == "__main__":
    main()
