#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import json
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator

import pysam

from common import BOUNDARY_FLANK, PIPELINE_VERSION, PSEUDOCOUNT, read_tsv


def run(command: list[str], cwd: Path | None = None) -> None:
    print("[RUN] " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def select_manifest_row(path: Path, array_index: int) -> dict[str, str]:
    rows = read_tsv(path)
    matches = [row for row in rows if int(row["array_index"]) == array_index]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one manifest row for array index {array_index}; found {len(matches)}")
    return matches[0]


def load_introns(path: Path) -> tuple[list[dict[str, object]], dict[str, list[int]], dict[str, dict[int, list[tuple[int, str]]]], dict[str, dict[tuple[int, int], list[int]]]]:
    introns: list[dict[str, object]] = []
    boundary_map: dict[str, dict[int, list[tuple[int, str]]]] = defaultdict(lambda: defaultdict(list))
    junction_map: dict[str, dict[tuple[int, int], list[int]]] = defaultdict(lambda: defaultdict(list))
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for index, row in enumerate(reader):
            record: dict[str, object] = {
                "intron_id": row["intron_id"],
                "gene_id": row["gene_id"],
                "gene_name": row["gene_name"],
                "transcript_id": row["transcript_id"],
                "chrom": row["chrom"],
                "start0": int(row["start0"]),
                "end0": int(row["end0"]),
                "strand": row["strand"],
                "intron_length": int(row["intron_length"]),
            }
            introns.append(record)
            chrom = str(record["chrom"])
            start0 = int(record["start0"])
            end0 = int(record["end0"])
            boundary_map[chrom][start0].append((index, "EI"))
            boundary_map[chrom][end0].append((index, "IE"))
            junction_map[chrom][(start0, end0)].append(index)
    boundary_positions = {chrom: sorted(position_map) for chrom, position_map in boundary_map.items()}
    return introns, boundary_positions, boundary_map, junction_map


def iter_qname_groups(bam: pysam.AlignmentFile) -> Iterator[list[pysam.AlignedSegment]]:
    current_name: str | None = None
    group: list[pysam.AlignedSegment] = []
    for read in bam.fetch(until_eof=True):
        name = read.query_name
        if current_name is None:
            current_name = name
        if name != current_name:
            yield group
            group = []
            current_name = name
        group.append(read)
    if group:
        yield group


def count_events(name_sorted_bam: Path, intron_path: Path) -> tuple[list[dict[str, object]], dict[str, int]]:
    introns, boundary_positions, boundary_map, junction_map = load_introns(intron_path)
    ei = [0] * len(introns)
    ie = [0] * len(introns)
    ee = [0] * len(introns)
    qc = {
        "query_names_seen": 0,
        "query_names_with_primary_alignment": 0,
        "primary_alignments_seen": 0,
    }

    with pysam.AlignmentFile(name_sorted_bam, "rb") as bam:
        for reads in iter_qname_groups(bam):
            qc["query_names_seen"] += 1
            fragment_ei: set[int] = set()
            fragment_ie: set[int] = set()
            fragment_ee: set[int] = set()
            primary_seen = False
            for read in reads:
                if read.is_unmapped or read.is_secondary or read.is_supplementary:
                    continue
                primary_seen = True
                qc["primary_alignments_seen"] += 1
                chrom = bam.get_reference_name(read.reference_id)
                positions = boundary_positions.get(chrom, [])
                if positions:
                    for block_start, block_end in read.get_blocks():
                        low = block_start + BOUNDARY_FLANK
                        high = block_end - BOUNDARY_FLANK
                        if high < low:
                            continue
                        left = bisect.bisect_left(positions, low)
                        right = bisect.bisect_right(positions, high)
                        for boundary in positions[left:right]:
                            for intron_index, kind in boundary_map[chrom][boundary]:
                                if kind == "EI":
                                    fragment_ei.add(intron_index)
                                else:
                                    fragment_ie.add(intron_index)

                reference_position = read.reference_start
                for operation, length in read.cigartuples or []:
                    if operation == 3:  # CIGAR N: exact exon-exon splice junction
                        donor = reference_position
                        acceptor = reference_position + length
                        for intron_index in junction_map.get(chrom, {}).get((donor, acceptor), []):
                            fragment_ee.add(intron_index)
                        reference_position += length
                    elif operation in {0, 2, 7, 8}:  # M, D, =, X consume reference
                        reference_position += length
            if primary_seen:
                qc["query_names_with_primary_alignment"] += 1
            for index in fragment_ei:
                ei[index] += 1
            for index in fragment_ie:
                ie[index] += 1
            for index in fragment_ee:
                ee[index] += 1

    rows: list[dict[str, object]] = []
    for index, intron in enumerate(introns):
        unspliced = ei[index] + ie[index]
        denominator = unspliced + 2 * ee[index]
        jm105_ir = unspliced / denominator if denominator > 0 else None
        pei = None
        if denominator > 0:
            import math
            pei = math.log2((unspliced + PSEUDOCOUNT) / (2 * ee[index] + PSEUDOCOUNT))
        rows.append({
            **intron,
            "EI": ei[index],
            "IE": ie[index],
            "EE_total": ee[index],
            "JM105_IR": "" if jm105_ir is None else f"{jm105_ir:.10g}",
            "PEI": "" if pei is None else f"{pei:.10g}",
        })
    return rows, qc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--array-index", required=True, type=int)
    parser.add_argument("--env-prefix", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--tmp-root", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    row = select_manifest_row(args.manifest, args.array_index)
    run_accession = row["run"]
    dataset_id = row["dataset_id"]
    env = args.env_prefix.resolve()
    prefetch = env / "bin" / "prefetch"
    fasterq = env / "bin" / "fasterq-dump"
    star = env / "bin" / "STAR"
    samtools = env / "bin" / "samtools"
    for tool in [prefetch, fasterq, star, samtools]:
        if not tool.exists():
            raise FileNotFoundError(tool)

    ref = root / "work" / "reference" / "WBcel235_Ensembl113"
    intron_path = ref / "representative_protein_coding_introns.tsv.gz"
    star_index = ref / "STAR_index"
    gtf = ref / "Caenorhabditis_elegans.WBcel235.113.gtf"
    if not (ref / "REFERENCE_COMPLETE.txt").exists():
        raise RuntimeError("Reference is incomplete")

    output_dir = root / "work" / "alignment" / dataset_id / run_accession
    result_dir = root / "work" / "per_run" / dataset_id
    marker_dir = root / "work" / "complete_markers"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker = marker_dir / f"{args.array_index:04d}_{run_accession}.complete.json"
    if marker.exists():
        print(f"Already complete: {marker}")
        return

    tmp = args.tmp_root.resolve() / f"{dataset_id}_{run_accession}"
    if tmp.exists():
        shutil.rmtree(tmp)
    fastq_dir = tmp / "fastq"
    fasterq_tmp = tmp / "fasterq_tmp"
    fastq_dir.mkdir(parents=True, exist_ok=True)
    fasterq_tmp.mkdir(parents=True, exist_ok=True)

    sra_root = root / "work" / "raw" / "sra"
    sra_root.mkdir(parents=True, exist_ok=True)
    run([str(prefetch), "--max-size", "u", "--output-directory", str(sra_root), run_accession])
    sra_path = sra_root / run_accession / f"{run_accession}.sra"
    if not sra_path.exists():
        candidates = list((sra_root / run_accession).glob("*.sra"))
        if len(candidates) != 1:
            raise FileNotFoundError(f"Could not identify SRA file for {run_accession}")
        sra_path = candidates[0]

    run([
        str(fasterq), "--split-files", "--threads", str(args.threads),
        "--temp", str(fasterq_tmp), "--outdir", str(fastq_dir), str(sra_path),
    ])

    r1 = fastq_dir / f"{run_accession}_1.fastq"
    r2 = fastq_dir / f"{run_accession}_2.fastq"
    single = fastq_dir / f"{run_accession}.fastq"
    if r1.exists() and r2.exists():
        read_files = [str(r1), str(r2)]
    elif single.exists():
        read_files = [str(single)]
    elif r1.exists() and not r2.exists():
        read_files = [str(r1)]
    else:
        found = sorted(fastq_dir.glob("*.fastq"))
        raise RuntimeError(f"Unexpected FASTQ layout for {run_accession}: {found}")

    prefix = str(output_dir) + "/"
    star_tmp = tmp / "STARtmp"
    command = [
        str(star),
        "--runThreadN", str(args.threads),
        "--genomeDir", str(star_index),
        "--sjdbGTFfile", str(gtf),
        "--readFilesIn", *read_files,
        "--outFileNamePrefix", prefix,
        "--outTmpDir", str(star_tmp),
        "--outSAMtype", "BAM", "SortedByCoordinate",
        "--outSAMstrandField", "intronMotif",
        "--outFilterMultimapNmax", "20",
        "--alignSJoverhangMin", "8",
        "--alignSJDBoverhangMin", "1",
        "--outFilterMismatchNoverReadLmax", "0.04",
        "--quantMode", "GeneCounts",
        "--limitBAMsortRAM", "12000000000",
    ]
    run(command)
    coord_bam = output_dir / "Aligned.sortedByCoord.out.bam"
    run([str(samtools), "index", "-@", str(args.threads), str(coord_bam)])
    name_bam = tmp / f"{run_accession}.name_sorted.bam"
    run([str(samtools), "sort", "-n", "-@", str(args.threads), "-m", "2G", "-o", str(name_bam), str(coord_bam)])

    event_rows, quant_qc = count_events(name_bam, intron_path)
    event_path = result_dir / f"{run_accession}.intron_counts.tsv.gz"
    fields = ["intron_id", "gene_id", "gene_name", "transcript_id", "chrom", "start0", "end0", "strand", "intron_length", "EI", "IE", "EE_total", "JM105_IR", "PEI"]
    with gzip.open(event_path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(event_rows)

    qc = {
        "pipeline_version": PIPELINE_VERSION,
        "array_index": args.array_index,
        "dataset_id": dataset_id,
        "run": run_accession,
        "group": row["group"],
        "biological_sample_id": row["biological_sample_id"],
        "event_output": str(event_path),
        "coordinate_bam": str(coord_bam),
        **quant_qc,
    }
    qc_path = result_dir / f"{run_accession}.qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    marker.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Completed {run_accession}")


if __name__ == "__main__":
    main()
