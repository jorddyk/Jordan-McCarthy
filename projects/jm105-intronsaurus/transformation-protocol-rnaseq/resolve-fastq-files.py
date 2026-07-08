#!/usr/bin/env python3
"""
Purpose: Resolve FASTQ files for the 12 JM105 transformation-protocol RNA-seq samples.
Original source clue: recovered from uploaded folder `/mnt/data/JM105_Transformation_Protocol_Pipeline/JM105_resolve_fastqs.py` during legacy code backfill.
Expected inputs: tab-separated sample manifest with sample_id, condition, replicate, aliases; recursive FASTQ root directory.
Expected outputs: tab-separated FASTQ resolution table with sample_id, condition, replicate, layout, read1, read2, matched_files.
Known assumptions: sample aliases are semicolon-separated; index FASTQs I1/I2 are ignored; paired-end files must have matched R1/R2 lane counts.
Data status: uses real FASTQ filenames/metadata; does not generate or simulate biological data.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

FASTQ_SUFFIXES = (".fastq.gz", ".fq.gz", ".fastq", ".fq")
R1_RE = re.compile(r"(?:^|[._-])R1(?:[._-]|$)", re.IGNORECASE)
R2_RE = re.compile(r"(?:^|[._-])R2(?:[._-]|$)", re.IGNORECASE)
INDEX_RE = re.compile(r"(?:^|[._-])I[12](?:[._-]|$)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--fastq-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def strip_fastq_suffix(name: str) -> str:
    lower = name.lower()
    for suffix in FASTQ_SUFFIXES:
        if lower.endswith(suffix):
            return name[: -len(suffix)]
    return name


def alias_regex(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias)
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def find_candidates(files: list[Path], aliases: list[str]) -> list[Path]:
    regexes = [alias_regex(a) for a in aliases if a]
    matches = []
    for path in files:
        stem = strip_fastq_suffix(path.name)
        if INDEX_RE.search(stem):
            continue
        if any(rx.search(stem) for rx in regexes):
            matches.append(path)
    return sorted(set(matches))


def classify(candidates: list[Path]) -> tuple[str, list[Path], list[Path]]:
    r1, r2, unclassified = [], [], []
    for path in candidates:
        stem = strip_fastq_suffix(path.name)
        if R1_RE.search(stem):
            r1.append(path)
        elif R2_RE.search(stem):
            r2.append(path)
        else:
            unclassified.append(path)

    if r1 or r2:
        if not r1 or not r2:
            raise RuntimeError(
                f"Found only one mate direction. R1={len(r1)}, R2={len(r2)}, files={candidates}"
            )
        if len(r1) != len(r2):
            raise RuntimeError(
                f"Unequal lane counts. R1={len(r1)}, R2={len(r2)}, files={candidates}"
            )
        return "paired", sorted(r1), sorted(r2)

    if unclassified:
        return "single", sorted(unclassified), []

    raise RuntimeError("No usable FASTQ files found")


def main() -> int:
    args = parse_args()
    if not args.fastq_root.exists():
        raise FileNotFoundError(f"FASTQ root does not exist: {args.fastq_root}")

    manifest = pd.read_csv(args.manifest, sep="\t", dtype=str)
    required = {"sample_id", "condition", "replicate", "aliases"}
    missing = required.difference(manifest.columns)
    if missing:
        raise RuntimeError(f"Manifest missing columns: {sorted(missing)}")

    files = sorted(
        path
        for path in args.fastq_root.rglob("*")
        if path.is_file() and path.name.lower().endswith(FASTQ_SUFFIXES)
    )
    if not files:
        raise RuntimeError(f"No FASTQ files found under {args.fastq_root}")

    rows = []
    errors = []
    for row in manifest.itertuples(index=False):
        aliases = [str(row.sample_id)]
        aliases.extend([a.strip() for a in str(row.aliases).split(";") if a.strip()])
        candidates = find_candidates(files, aliases)
        try:
            layout, read1, read2 = classify(candidates)
        except Exception as exc:
            errors.append(f"{row.sample_id}: {exc}")
            continue

        rows.append(
            {
                "sample_id": row.sample_id,
                "condition": row.condition,
                "replicate": row.replicate,
                "layout": layout,
                "read1": ",".join(str(p.resolve()) for p in read1),
                "read2": ",".join(str(p.resolve()) for p in read2),
                "matched_files": len(candidates),
            }
        )

    if errors:
        listing = "\n".join(str(p) for p in files[:300])
        message = "\n".join(errors)
        raise RuntimeError(
            "FASTQ resolution failed for one or more samples:\n"
            f"{message}\n\nFirst FASTQ files seen under the root:\n{listing}"
        )

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, sep="\t", index=False)
    print(output.to_string(index=False))
    print(f"Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
