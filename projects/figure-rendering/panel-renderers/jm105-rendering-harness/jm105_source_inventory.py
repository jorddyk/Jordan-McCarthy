#!/usr/bin/env python3
"""
JM105 source inventory harness.

Purpose
-------
Find candidate JM105/Intronsaurus source tables and source scripts before a
figure-panel renderer guesses paths. This is a reusable preflight step for
JM105 figure rendering on Euler.

Expected use on Euler
---------------------
python3 jm105_source_inventory.py \
  --project /cluster/scratch/jmccarthy/JM105_RNAseq \
  --out /cluster/home/jmccarthy/JM105_source_inventory_out

Outputs
-------
- candidate_table_inventory.tsv
- best_per_intron_table_candidates.tsv
- candidate_source_script_hits.tsv
- top_candidate_preview.txt
- inventory_summary.txt

Data status
-----------
Reads file headers and short previews only. It does not modify data and does
not generate biological values.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
import re
from pathlib import Path
from typing import Iterable, List

TABLE_SUFFIXES = {".csv", ".tsv", ".txt"}
SOURCE_SUFFIXES = {".py", ".R", ".r", ".sh", ".bash", ".html", ".js", ".json", ".md"}

TABLE_NAME_TERMS = [
    "jm105",
    "intron",
    "retention",
    "retained",
    "nmd",
    "upf1",
    "leak",
    "direct",
    "detector",
    "atlas",
    "intronsaurus",
]

HEADER_TERMS = [
    "intron_id",
    "gene",
    "standard_name",
    "systematic_name",
    "young",
    "old",
    "age",
    "nmd",
    "upf1",
    "mud1",
    "glucose",
    "retention",
    "retained",
    "ir",
    "detector",
    "nmd_revealed",
    "direct_old_minus_young",
]

SOURCE_TERMS = [
    "read_csv",
    "read.table",
    "fread",
    "JM105_",
    "intron_id",
    "retention",
    "retained",
    "NMD",
    "upf1",
    "Mud1",
    "sample_level_retained_intron_burden",
    "direct_old_more_leakage",
    "paired_gene_body",
]


def open_text(path: Path):
    if str(path).lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")


def sniff_delimiter(line: str) -> str:
    return "\t" if line.count("\t") > line.count(",") else ","


def is_table_path(path: Path) -> bool:
    lower = path.name.lower()
    if lower.endswith(".csv.gz") or lower.endswith(".tsv.gz"):
        return True
    return path.suffix.lower() in TABLE_SUFFIXES


def is_probably_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(2048)
    except OSError:
        return True


def relative(project: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


def write_tsv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fields.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: str(row.get(key, "")) for key in fields})


def inspect_table(project: Path, path: Path) -> dict:
    row = {
        "path": str(path),
        "relative_path": relative(project, path),
        "size_bytes": path.stat().st_size if path.exists() else "",
        "score": 0,
        "n_columns": "",
        "has_intron_id_header": "no",
        "has_age_header": "no",
        "has_nmd_header": "no",
        "has_mud1_header": "no",
        "has_retention_header": "no",
        "has_direct_or_detector_header": "no",
        "header": "",
        "first_data_rows_blob": "",
        "error": "",
    }
    try:
        with open_text(path) as handle:
            first = handle.readline()
            if not first:
                row["error"] = "empty"
                return row
            delimiter = sniff_delimiter(first)
            header = next(csv.reader([first], delimiter=delimiter), [])
            header_blob = " | ".join(h.strip() for h in header)
            lower_header = header_blob.lower()
            row["header"] = header_blob[:4000]
            row["n_columns"] = len(header)

            score = 0
            for term in HEADER_TERMS:
                if term.lower() in lower_header:
                    score += 10

            if "intron_id" in lower_header:
                row["has_intron_id_header"] = "yes"
                score += 100
            if any(term in lower_header for term in ["young", "old", "age"]):
                row["has_age_header"] = "yes"
                score += 30
            if any(term in lower_header for term in ["nmd", "upf1"]):
                row["has_nmd_header"] = "yes"
                score += 30
            if "mud1" in lower_header:
                row["has_mud1_header"] = "yes"
                score += 20
            if any(term in lower_header for term in ["retention", "retained", "ir"]):
                row["has_retention_header"] = "yes"
                score += 30
            if any(term in lower_header for term in ["direct_old_minus_young", "detector", "nmd_revealed"]):
                row["has_direct_or_detector_header"] = "yes"
                score += 60

            preview_lines = []
            for idx, line in enumerate(handle):
                if idx >= 8:
                    break
                preview_lines.append(line.rstrip("\n")[:800])
            first_blob = " || ".join(preview_lines)
            row["first_data_rows_blob"] = first_blob[:4000]
            lower_preview = first_blob.lower()
            for term in HEADER_TERMS:
                if term.lower() in lower_preview:
                    score += 4

            lower_path = str(path).lower()
            if "per_intron" in lower_path:
                score += 50
            if "direct" in lower_path or "leak" in lower_path or "detector" in lower_path:
                score += 40
            if "intronsaurus" in lower_path:
                score += 15
            if "sample_level" in lower_path:
                score -= 80
            if "burden" in lower_path:
                score -= 30

            row["score"] = score
            return row
    except Exception as exc:  # noqa: BLE001
        row["error"] = repr(exc)
        return row


def scan_source(project: Path, path: Path) -> List[dict]:
    hits: List[dict] = []
    if is_probably_binary(path):
        return hits
    try:
        with open_text(path) as handle:
            for lineno, line in enumerate(handle, start=1):
                lower = line.lower()
                if any(term.lower() in lower for term in SOURCE_TERMS):
                    hits.append(
                        {
                            "path": str(path),
                            "relative_path": relative(project, path),
                            "line": lineno,
                            "text": line.rstrip("\n")[:1000],
                        }
                    )
    except Exception:
        return hits
    return hits


def iter_candidate_paths(project: Path, max_depth: int | None = None) -> tuple[List[Path], List[Path]]:
    table_paths: List[Path] = []
    source_paths: List[Path] = []
    project_parts = len(project.parts)

    skip_terms = ["/fastq", "/fastqs", "/raw_fastq", "/star_index", "/genome_index"]
    for root, dirs, files in os.walk(project):
        root_path = Path(root)
        if max_depth is not None and len(root_path.parts) - project_parts > max_depth:
            dirs[:] = []
            continue
        lower_root = str(root_path).lower()
        if any(term in lower_root for term in skip_terms):
            dirs[:] = []
            continue
        for name in files:
            path = root_path / name
            lower_name = name.lower()
            lower_path = str(path).lower()
            if is_table_path(path) and any(term in lower_path for term in TABLE_NAME_TERMS):
                table_paths.append(path)
            if path.suffix.lower() in SOURCE_SUFFIXES and any(term in lower_path for term in ["jm105", "intronsaurus", "figure", "fig", "retention", "leak"]):
                source_paths.append(path)
    return table_paths, source_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory JM105/Intronsaurus source files for figure rendering.")
    parser.add_argument("--project", default="/cluster/scratch/jmccarthy/JM105_RNAseq")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-depth", type=int, default=10)
    args = parser.parse_args()

    project = Path(args.project)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not project.exists():
        raise FileNotFoundError(f"Project root not found: {project}")

    table_paths, source_paths = iter_candidate_paths(project, args.max_depth)
    table_rows = sorted((inspect_table(project, path) for path in table_paths), key=lambda r: int(r.get("score") or 0), reverse=True)

    source_hits: List[dict] = []
    for path in source_paths:
        source_hits.extend(scan_source(project, path))

    write_tsv(out / "candidate_table_inventory.tsv", table_rows)
    write_tsv(out / "best_per_intron_table_candidates.tsv", [row for row in table_rows if int(row.get("score") or 0) >= 100][:200])
    write_tsv(out / "candidate_source_script_hits.tsv", source_hits[:10000])

    preview = out / "top_candidate_preview.txt"
    with preview.open("w", encoding="utf-8") as handle:
        handle.write("Top JM105/Intronsaurus table candidates\n")
        handle.write("=====================================\n\n")
        for idx, row in enumerate(table_rows[:40], start=1):
            handle.write(f"#{idx} score={row.get('score')} size={row.get('size_bytes')}\n")
            handle.write(f"path: {row.get('path')}\n")
            handle.write(f"header: {row.get('header')}\n")
            handle.write(f"first rows: {row.get('first_data_rows_blob')}\n")
            handle.write("\n---\n\n")

    summary = out / "inventory_summary.txt"
    summary.write_text(
        "JM105 source inventory complete\n"
        "===============================\n\n"
        f"Project root: {project}\n"
        f"Tables inspected: {len(table_rows)}\n"
        f"Source-script hits: {len(source_hits)}\n\n"
        "Primary files to inspect next:\n"
        "  candidate_table_inventory.tsv\n"
        "  best_per_intron_table_candidates.tsv\n"
        "  candidate_source_script_hits.tsv\n"
        "  top_candidate_preview.txt\n",
        encoding="utf-8",
    )

    print(summary.read_text())
    print(f"Output directory: {out}")


if __name__ == "__main__":
    main()
