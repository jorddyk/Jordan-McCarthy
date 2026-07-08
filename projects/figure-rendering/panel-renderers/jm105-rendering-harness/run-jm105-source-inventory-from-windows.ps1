# run-jm105-source-inventory-from-windows.ps1
# Purpose: no-prompt Windows runner for JM105/Euler source discovery before figure rendering.
# This runner avoids C:\WINDOWS\system32, converts CRLF to LF on Euler, and retrieves all outputs.

$ErrorActionPreference = "Stop"

$EulerUserHost = "jmccarthy@euler.ethz.ch"
$ProjectRoot = "/cluster/scratch/jmccarthy/JM105_RNAseq"
$RemoteRoot = "/cluster/home/jmccarthy/JM105_source_inventory_harness"
$RemoteOut = "$RemoteRoot/out"
$LocalWorkDir = "C:\Users\jmccarthy\Downloads\JM105_Source_Inventory_Harness"
$LocalOut = Join-Path $LocalWorkDir "out"

New-Item -ItemType Directory -Force -Path $LocalWorkDir | Out-Null
Set-Location $LocalWorkDir

$RemotePython = @'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import os
from pathlib import Path
from typing import List

TABLE_SUFFIXES = {".csv", ".tsv", ".txt"}
SOURCE_SUFFIXES = {".py", ".R", ".r", ".sh", ".bash", ".html", ".js", ".json", ".md"}
TABLE_NAME_TERMS = ["jm105", "intron", "retention", "retained", "nmd", "upf1", "leak", "direct", "detector", "atlas", "intronsaurus"]
HEADER_TERMS = ["intron_id", "gene", "standard_name", "systematic_name", "young", "old", "age", "nmd", "upf1", "mud1", "glucose", "retention", "retained", "ir", "detector", "nmd_revealed", "direct_old_minus_young"]
SOURCE_TERMS = ["read_csv", "read.table", "fread", "JM105_", "intron_id", "retention", "retained", "NMD", "upf1", "Mud1", "sample_level_retained_intron_burden", "direct_old_more_leakage", "paired_gene_body"]


def open_text(path: Path):
    if str(path).lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")


def sniff_delimiter(line: str) -> str:
    return "\t" if line.count("\t") > line.count(",") else ","


def is_table_path(path: Path) -> bool:
    lower = path.name.lower()
    return lower.endswith(".csv.gz") or lower.endswith(".tsv.gz") or path.suffix.lower() in TABLE_SUFFIXES


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
    fields = []
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
    row = {"path": str(path), "relative_path": relative(project, path), "size_bytes": path.stat().st_size, "score": 0, "n_columns": "", "header": "", "first_data_rows_blob": "", "error": ""}
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
            score = 0
            for term in HEADER_TERMS:
                if term.lower() in lower_header:
                    score += 10
            if "intron_id" in lower_header:
                score += 100
            if any(term in lower_header for term in ["young", "old", "age"]):
                score += 30
            if any(term in lower_header for term in ["nmd", "upf1"]):
                score += 30
            if "mud1" in lower_header:
                score += 20
            if any(term in lower_header for term in ["retention", "retained", "ir"]):
                score += 30
            if any(term in lower_header for term in ["direct_old_minus_young", "detector", "nmd_revealed"]):
                score += 60
            lower_path = str(path).lower()
            if "per_intron" in lower_path:
                score += 50
            if "direct" in lower_path or "leak" in lower_path or "detector" in lower_path:
                score += 40
            if "sample_level" in lower_path:
                score -= 80
            if "burden" in lower_path:
                score -= 30
            preview = []
            for i, line in enumerate(handle):
                if i >= 8:
                    break
                preview.append(line.rstrip("\n")[:800])
            row.update({"score": score, "n_columns": len(header), "header": header_blob[:4000], "first_data_rows_blob": " || ".join(preview)[:4000]})
            return row
    except Exception as exc:
        row["error"] = repr(exc)
        return row


def scan_source(project: Path, path: Path) -> List[dict]:
    hits = []
    try:
        with open_text(path) as handle:
            for lineno, line in enumerate(handle, start=1):
                if any(term.lower() in line.lower() for term in SOURCE_TERMS):
                    hits.append({"path": str(path), "relative_path": relative(project, path), "line": lineno, "text": line.rstrip("\n")[:1000]})
    except Exception:
        pass
    return hits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    project = Path(args.project)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not project.exists():
        raise FileNotFoundError(project)

    table_paths = []
    source_paths = []
    for root, dirs, files in os.walk(project):
        low_root = root.lower()
        if any(x in low_root for x in ["/fastq", "/fastqs", "/raw_fastq", "/star_index", "/genome_index"]):
            dirs[:] = []
            continue
        for name in files:
            path = Path(root) / name
            low_path = str(path).lower()
            if is_table_path(path) and any(term in low_path for term in TABLE_NAME_TERMS):
                table_paths.append(path)
            if path.suffix.lower() in SOURCE_SUFFIXES and any(term in low_path for term in ["jm105", "intronsaurus", "figure", "fig", "retention", "leak"]):
                source_paths.append(path)

    table_rows = sorted([inspect_table(project, p) for p in table_paths], key=lambda r: int(r.get("score") or 0), reverse=True)
    source_hits = []
    for path in source_paths:
        source_hits.extend(scan_source(project, path))

    write_tsv(out / "candidate_table_inventory.tsv", table_rows)
    write_tsv(out / "best_per_intron_table_candidates.tsv", [r for r in table_rows if int(r.get("score") or 0) >= 100][:200])
    write_tsv(out / "candidate_source_script_hits.tsv", source_hits[:10000])
    with (out / "top_candidate_preview.txt").open("w", encoding="utf-8") as handle:
        for i, row in enumerate(table_rows[:40], start=1):
            handle.write(f"#{i} score={row.get('score')}\npath: {row.get('path')}\nheader: {row.get('header')}\nfirst rows: {row.get('first_data_rows_blob')}\n\n---\n")
    (out / "inventory_summary.txt").write_text(f"Tables inspected: {len(table_rows)}\nSource hits: {len(source_hits)}\nOutput: {out}\n", encoding="utf-8")
    print((out / "inventory_summary.txt").read_text())


if __name__ == "__main__":
    main()
'@

Write-Host "Installing and running JM105 source inventory on Euler..." -ForegroundColor Cyan
ssh $EulerUserHost "mkdir -p '$RemoteRoot' '$RemoteOut'"
$RemotePython | ssh $EulerUserHost "cat > '$RemoteRoot/jm105_source_inventory.py' && tr -d '\r' < '$RemoteRoot/jm105_source_inventory.py' > '$RemoteRoot/jm105_source_inventory.fixed.py' && python3 '$RemoteRoot/jm105_source_inventory.fixed.py' --project '$ProjectRoot' --out '$RemoteOut'"

Write-Host "Retrieving inventory outputs..." -ForegroundColor Cyan
if (Test-Path $LocalOut) {
    Remove-Item -Recurse -Force $LocalOut
}
New-Item -ItemType Directory -Force -Path $LocalOut | Out-Null
scp -r "${EulerUserHost}:$RemoteOut/*" "$LocalOut\"

Write-Host "Retrieved files:" -ForegroundColor Green
Get-ChildItem -Path $LocalOut | Format-Table Name,Length,LastWriteTime
Write-Host "Primary files:" -ForegroundColor Green
Write-Host "$LocalOut\candidate_table_inventory.tsv"
Write-Host "$LocalOut\best_per_intron_table_candidates.tsv"
Write-Host "$LocalOut\candidate_source_script_hits.tsv"
Write-Host "$LocalOut\top_candidate_preview.txt"
