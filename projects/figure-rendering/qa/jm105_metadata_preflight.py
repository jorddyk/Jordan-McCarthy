#!/usr/bin/env python3
"""Fail-closed metadata preflight for JM105 figure renderers.

This tool validates the exact real-table metadata labels before a renderer is
submitted to Euler. It deliberately ignores opaque sample IDs when classifying
age, glucose, MUD1 or UPF1 status.

It does not calculate biological metrics and does not create simulated data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

REQUIRED_COLUMNS = (
    "sample",
    "age",
    "glucose",
    "mud1_status",
    "upf1_status",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_token(value: object) -> str:
    """Transliterate genotype symbols before removing punctuation."""
    token = str(value).strip().lower()
    token = (
        token.replace("Δ", "delta")
        .replace("δ", "delta")
        .replace("∆", "delta")
        .replace("+", "plus")
        .replace("−", "minus")
        .replace("–", "minus")
    )
    return re.sub(r"[^a-z0-9]+", "", token)


def normalize_nmd(value: object) -> str:
    token = normalize_token(value)

    deletion_tokens = {
        "upf1d",
        "upf1delta",
        "deltaupf1",
        "upf1deletion",
        "upf1knockout",
        "upf1ko",
        "nmdoff",
    }
    intact_tokens = {
        "wtupf1",
        "wtupf1plus",
        "upf1",
        "upf1plus",
        "upf1intact",
        "nmdon",
    }

    if token in deletion_tokens:
        return "upf1Δ"
    if token in intact_tokens:
        return "UPF1+"
    if "upf1" in token:
        if any(marker in token for marker in ("delta", "deletion", "knockout", "ko")):
            return "upf1Δ"
        if token.endswith("d"):
            return "upf1Δ"
        return "UPF1+"

    raise ValueError(
        f"Unrecognized UPF1/NMD label: raw={value!r}, normalized={token!r}"
    )


def normalize_mud1(value: object) -> str:
    token = normalize_token(value)
    deletion_tokens = {
        "mud1d",
        "mud1delta",
        "deltamud1",
        "mud1deletion",
        "mud1knockout",
        "mud1ko",
    }
    intact_tokens = {
        "wtmud1",
        "wtmud1plus",
        "mud1",
        "mud1plus",
        "mud1intact",
    }
    if token in deletion_tokens:
        return "mud1Δ"
    if token in intact_tokens:
        return "WT"
    if "mud1" in token:
        if any(marker in token for marker in ("delta", "deletion", "knockout", "ko")):
            return "mud1Δ"
        if token.endswith("d"):
            return "mud1Δ"
        return "WT"
    raise ValueError(
        f"Unrecognized MUD1 label: raw={value!r}, normalized={token!r}"
    )


def normalize_age(value: object) -> str:
    token = normalize_token(value)
    if token in {"young", "y", "log", "logphase"}:
        return "young"
    if token in {"old", "o", "aged", "age"}:
        return "old"
    raise ValueError(f"Unrecognized age label: raw={value!r}, normalized={token!r}")


def normalize_glucose(value: object) -> str:
    raw = str(value).strip().lower().replace(",", ".")
    token = normalize_token(raw)

    if raw in {"2", "2%", "2.0", "2.0%"} or token in {
        "2pct",
        "2percent",
        "2glucose",
        "highglucose",
    }:
        return "2%"
    if raw in {"0.1", "0.1%", ".1", ".1%"} or token in {
        "01pct",
        "01percent",
        "0p1",
        "01glucose",
        "lowglucose",
        "cr",
    }:
        return "0.1%"
    if raw in {"0.5", "0.5%", ".5", ".5%"} or token in {
        "05pct",
        "05percent",
        "0p5",
        "05glucose",
    }:
        return "0.5%"
    raise ValueError(
        f"Unrecognized glucose label: raw={value!r}, normalized={token!r}"
    )


def unique_mapping(values: Iterable[object], normalizer) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in sorted({str(item) for item in values if pd.notna(item)}):
        mapping[value] = normalizer(value)
    return mapping


def parse_required_cell(text: str) -> tuple[str, str, str, str]:
    parts = [part.strip() for part in text.split("|")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            "--require-cell must be AGE|GLUCOSE|MUD1|NMD, for example "
            "old|2%|WT|UPF1+"
        )
    return (
        normalize_age(parts[0]),
        normalize_glucose(parts[1]),
        normalize_mud1(parts[2]),
        normalize_nmd(parts[3]),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", required=True, type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument(
        "--require-cell",
        action="append",
        default=[],
        type=parse_required_cell,
        metavar="AGE|GLUCOSE|MUD1|NMD",
    )
    args = parser.parse_args()

    if not args.counts.is_file():
        raise FileNotFoundError(f"Counts table not found: {args.counts}")

    frame = pd.read_csv(args.counts, usecols=lambda name: name in REQUIRED_COLUMNS)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise RuntimeError(f"Missing required metadata columns: {missing}")
    if frame.empty:
        raise RuntimeError("Counts table contains no rows")

    mappings = {
        "age": unique_mapping(frame["age"], normalize_age),
        "glucose": unique_mapping(frame["glucose"], normalize_glucose),
        "mud1_status": unique_mapping(frame["mud1_status"], normalize_mud1),
        "upf1_status": unique_mapping(frame["upf1_status"], normalize_nmd),
    }

    normalized = pd.DataFrame(
        {
            "age": frame["age"].map(normalize_age),
            "glucose": frame["glucose"].map(normalize_glucose),
            "mud1": frame["mud1_status"].map(normalize_mud1),
            "nmd": frame["upf1_status"].map(normalize_nmd),
        }
    )

    observed_cells = (
        normalized.value_counts(dropna=False)
        .rename("row_count")
        .reset_index()
        .sort_values(["age", "glucose", "mud1", "nmd"])
    )
    observed_set = {
        tuple(row)
        for row in observed_cells[["age", "glucose", "mud1", "nmd"]].itertuples(
            index=False, name=None
        )
    }

    missing_cells = [cell for cell in args.require_cell if cell not in observed_set]
    if missing_cells:
        rendered = ["|".join(cell) for cell in missing_cells]
        raise RuntimeError(f"Required metadata cells are absent: {rendered}")

    manifest = {
        "status": "PASS",
        "counts_path": str(args.counts.resolve()),
        "counts_sha256": sha256_file(args.counts),
        "row_count": int(len(frame)),
        "unique_sample_count": int(frame["sample"].nunique(dropna=True)),
        "mappings": mappings,
        "observed_cells": observed_cells.to_dict(orient="records"),
        "required_cells": ["|".join(cell) for cell in args.require_cell],
    }

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
