#!/usr/bin/env python3
"""Step 1: audit public C. elegans datasets for a JM105-style analysis.

This script is metadata-only. It resolves GEO/SRA/BioProject/DDBJ accessions,
records run-level sequencing architecture, grades junction-read usability, and
reports which contrasts can be estimated within each study. It does not
retrieve FASTQ or BAM files.

Scientific sign conventions used downstream, not calculated in this step:
    IRratio = (intron_count + 1) / (host_exon_count + 1)
    NMD_hidden = IR(NMD off) - IR(matched NMD on)
    age_linked_NMD_hidden = NMD_hidden(old) - NMD_hidden(young)
    CR_suppression = age_linked_NMD_hidden(control diet)
                     - age_linked_NMD_hidden(DR)
    RNP2_dependent_CR_suppression = CR_suppression(RNP-2+)
                                    - CR_suppression(rnp-2 perturbed)
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "1.1.0"
NCBI_INTERVAL_SECONDS = 0.36
RUN_FIELDS = [
    "dataset_id", "query_accession", "resolved_via", "run_accession",
    "experiment_accession", "study_accession", "bioproject", "biosample",
    "sample_accession", "sample_title", "sample_description", "library_name",
    "library_strategy", "library_source", "library_selection", "library_layout",
    "platform", "instrument_model", "read_count", "base_count",
    "avg_read_length", "fastq_bytes", "fastq_md5", "fastq_ftp",
    "first_public", "last_updated", "raw_reads_available", "junction_grade",
    "junction_grade_reason", "inferred_age", "inferred_stage",
    "inferred_nmd_state", "inferred_diet_state", "inferred_rnp2_state",
    "inferred_rnp3_state", "inferred_fraction", "manual_review_required",
    "metadata_text",
]


@dataclass(frozen=True)
class Candidate:
    dataset_id: str
    accession: str
    priority: int
    role: str
    expected_design: str
    why_included: str


class AuditError(RuntimeError):
    pass


class Client:
    def __init__(self, email: str, api_key: str, timeout: int, retries: int) -> None:
        self.email = email.strip()
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.retries = retries
        self.last_ncbi_request = 0.0

    def _wait(self, url: str) -> None:
        if "ncbi.nlm.nih.gov" not in url:
            return
        elapsed = time.monotonic() - self.last_ncbi_request
        if elapsed < NCBI_INTERVAL_SECONDS:
            time.sleep(NCBI_INTERVAL_SECONDS - elapsed)
        self.last_ncbi_request = time.monotonic()

    def get_bytes(self, url: str) -> bytes:
        error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            self._wait(url)
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": f"JM105-Celegans-Audit/{VERSION} ({self.email or 'no-email'})",
                    "Accept": "*/*",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = response.read()
                if not data:
                    raise AuditError(f"Empty response: {url}")
                return data
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, AuditError) as exc:
                error = exc
                if attempt < self.retries:
                    time.sleep(min(2 ** (attempt - 1), 8))
        raise AuditError(f"Request failed after {self.retries} attempts: {url}: {error}")

    def get_text(self, url: str) -> str:
        data = self.get_bytes(url)
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        return data.decode("utf-8", errors="replace")

    def eutils(self, endpoint: str, params: Mapping[str, str]) -> str:
        merged = dict(params)
        merged["tool"] = "jm105_celegans_metadata_audit"
        if self.email:
            merged["email"] = self.email
        if self.api_key:
            merged["api_key"] = self.api_key
        url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{endpoint}?"
            + urllib.parse.urlencode(merged)
        )
        return self.get_text(url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--email", default=os.environ.get("NCBI_EMAIL", ""))
    parser.add_argument("--api-key", default=os.environ.get("NCBI_API_KEY", ""))
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def read_candidates(path: Path) -> list[Candidate]:
    if not path.is_file():
        raise FileNotFoundError(path)
    required = {
        "dataset_id", "accession", "priority", "role", "expected_design",
        "why_included",
    }
    candidates: list[Candidate] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Candidate table missing columns: {sorted(missing)}")
        for row in reader:
            candidates.append(
                Candidate(
                    dataset_id=row["dataset_id"].strip(),
                    accession=row["accession"].strip(),
                    priority=int(row["priority"]),
                    role=row["role"].strip(),
                    expected_design=row["expected_design"].strip(),
                    why_included=row["why_included"].strip(),
                )
            )
    if not candidates:
        raise ValueError("Candidate table is empty")
    ids = [candidate.dataset_id for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("dataset_id values must be unique")
    return candidates


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def parse_delimited(text: str, delimiter: str = ",") -> list[dict[str, str]]:
    stripped = text.lstrip("\ufeff\r\n ")
    if not stripped:
        return []
    return [dict(row) for row in csv.DictReader(io.StringIO(stripped), delimiter=delimiter)]


def first(row: Mapping[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = str(row.get(key, "")).strip()
        if value:
            return value
    return ""


def integer(value: Any) -> int | None:
    text = str(value or "").replace(",", "").strip()
    try:
        return int(float(text)) if text else None
    except ValueError:
        return None


def average_read_length(row: Mapping[str, Any]) -> float | None:
    direct = first(row, ["avgLength", "avg_read_length", "read_length"])
    if direct:
        try:
            return float(direct)
        except ValueError:
            pass
    bases = integer(first(row, ["bases", "base_count"])); reads = integer(first(row, ["spots", "read_count"]));
    layout = first(row, ["LibraryLayout", "library_layout"]).upper()
    if bases and reads and reads > 0:
        divisor = reads * (2 if layout == "PAIRED" else 1)
        return bases / divisor
    return None


def combined_text(row: Mapping[str, Any]) -> str:
    keys = [
        "SampleName", "sample_name", "Sample", "sample_title", "sample_description",
        "LibraryName", "library_name", "source_name", "characteristics",
        "BioSampleModel", "Experiment", "experiment_title", "Title",
    ]
    values = [first(row, [key]) for key in keys]
    values.extend(str(value) for value in row.values() if value)
    return " | ".join(dict.fromkeys(value.strip() for value in values if value.strip()))


def infer_states(text: str) -> dict[str, str]:
    low = text.lower().replace("Δ", "delta")

    age = "unknown"
    stage = "unknown"
    if re.search(r"\b(l4|larval|larva)\b", low):
        stage = "larval"
    if re.search(r"\b(day|adult day|ad)\s*[-_ ]?0?1\b|young adult|day[-_ ]?1", low):
        age, stage = "young", "adult"
    old_match = re.search(r"\b(day|adult day|ad)\s*[-_ ]?(\d{1,2})\b", low)
    if old_match and int(old_match.group(2)) >= 5:
        age, stage = "old", "adult"
    elif re.search(r"\bold\b|aged", low):
        age, stage = "old", "adult"

    if re.search(r"smg[-_ ]?2|smg[-_ ]?1|nmd[-_ ]?(off|null|deficient)|nonsense.mediated.*(loss|deficient)", low):
        nmd = "off"
    elif re.search(r"wild.?type|\bn2\b|control", low):
        nmd = "on"
    else:
        nmd = "unknown"

    if re.search(r"eat[-_ ]?2|dietary restriction|calori[ce] restriction|\bdr\b|bacterial dilution", low):
        diet = "DR"
    elif re.search(r"ad libitum|control diet|normal diet|well.?fed|wild.?type|\bn2\b", low):
        diet = "control"
    else:
        diet = "unknown"

    if re.search(r"rnp[-_ ]?2.*(mut|del|tm\d+|rna[ -]?i|kd|deplet)|rnp[-_ ]?2\([^)]*\)", low):
        rnp2 = "perturbed"
    elif re.search(r"rnp[-_ ]?2|wild.?type|\bn2\b|control", low):
        rnp2 = "plus"
    else:
        rnp2 = "unknown"

    if re.search(r"rnp[-_ ]?3.*(mut|del|tm\d+|rna[ -]?i|kd|deplet)|rnp[-_ ]?3\([^)]*\)", low):
        rnp3 = "perturbed"
    elif re.search(r"rnp[-_ ]?3|wild.?type|\bn2\b|control", low):
        rnp3 = "plus"
    else:
        rnp3 = "unknown"

    if re.search(r"cytoplasm|cytosol|cytoplasmic", low):
        fraction = "cytoplasmic"
    elif re.search(r"nuclear|nucleus", low):
        fraction = "nuclear"
    elif re.search(r"whole.?worm|total rna|input", low):
        fraction = "whole_or_input"
    else:
        fraction = "unknown"

    return {
        "inferred_age": age,
        "inferred_stage": stage,
        "inferred_nmd_state": nmd,
        "inferred_diet_state": diet,
        "inferred_rnp2_state": rnp2,
        "inferred_rnp3_state": rnp3,
        "inferred_fraction": fraction,
    }


def grade_junction(row: Mapping[str, Any]) -> tuple[str, str, str]:
    strategy = first(row, ["LibraryStrategy", "library_strategy"]).upper()
    layout = first(row, ["LibraryLayout", "library_layout"]).upper()
    raw = bool(first(row, ["download_path", "fastq_ftp", "fastq_bytes", "Run", "run_accession"]))
    length = average_read_length(row)
    if strategy and "RNA-SEQ" not in strategy:
        return "UNSUITABLE", f"Library strategy is {strategy}, not RNA-Seq", "yes"
    if not raw:
        return "UNRESOLVED", "No raw-read path or run accession resolved", "yes"
    if length is None:
        return "REVIEW", f"{layout or 'unknown'} layout; read length unresolved", "yes"
    if layout == "PAIRED" and length >= 75:
        return "HIGH", f"Paired-end RNA-seq, mean read length {length:.1f} nt", "no"
    if layout == "PAIRED" and length >= 50:
        return "MEDIUM", f"Paired-end RNA-seq, mean read length {length:.1f} nt", "no"
    if layout == "SINGLE" and length >= 75:
        return "MEDIUM", f"Single-end RNA-seq, mean read length {length:.1f} nt", "no"
    if layout == "SINGLE" and length >= 50:
        return "LOW", f"Single-end RNA-seq, mean read length {length:.1f} nt", "yes"
    return "UNSUITABLE", f"Read length {length:.1f} nt is too short for primary junction analysis", "yes"


def geo_bucket(accession: str) -> str:
    match = re.fullmatch(r"GSE(\d+)", accession.upper())
    if not match:
        raise ValueError(accession)
    digits = match.group(1)
    prefix = digits[:-3] if len(digits) > 3 else ""
    return f"GSE{prefix}nnn"


def fetch_geo_soft(client: Client, accession: str, raw_dir: Path) -> tuple[str, list[str]]:
    url = (
        f"https://ftp.ncbi.nlm.nih.gov/geo/series/{geo_bucket(accession)}/"
        f"{accession}/soft/{accession}_family.soft.gz"
    )
    text = client.get_text(url)
    (raw_dir / f"{accession}_family.soft").write_text(text, encoding="utf-8")
    relations = sorted(set(re.findall(r"\b(?:SRP\d+|PRJNA\d+|PRJEB\d+|PRJDB\d+)\b", text)))
    return text, relations


def fetch_sra_runinfo(client: Client, accession: str, raw_dir: Path) -> list[dict[str, str]]:
    search = client.eutils(
        "esearch.fcgi",
        {"db": "sra", "term": accession, "retmode": "json", "retmax": "10000"},
    )
    (raw_dir / f"{safe_name(accession)}_sra_esearch.json").write_text(search, encoding="utf-8")
    payload = json.loads(search)
    ids = payload.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    runinfo = client.eutils(
        "efetch.fcgi",
        {"db": "sra", "id": ",".join(ids), "rettype": "runinfo", "retmode": "text"},
    )
    (raw_dir / f"{safe_name(accession)}_sra_runinfo.csv").write_text(runinfo, encoding="utf-8")
    return parse_delimited(runinfo)


def fetch_ena_runs(client: Client, accession: str, raw_dir: Path) -> list[dict[str, str]]:
    fields = ",".join([
        "run_accession", "experiment_accession", "study_accession", "secondary_study_accession",
        "sample_accession", "secondary_sample_accession", "scientific_name", "sample_title",
        "experiment_title", "library_name", "library_strategy", "library_source",
        "library_selection", "library_layout", "instrument_platform", "instrument_model",
        "read_count", "base_count", "fastq_bytes", "fastq_md5", "fastq_ftp",
        "first_public", "last_updated",
    ])
    queries = [
        f'study_accession="{accession}"',
        f'secondary_study_accession="{accession}"',
        f'experiment_accession="{accession}"',
    ]
    rows: list[dict[str, str]] = []
    for index, query in enumerate(queries, start=1):
        url = "https://www.ebi.ac.uk/ena/portal/api/search?" + urllib.parse.urlencode({
            "result": "read_run", "query": query, "fields": fields,
            "format": "tsv", "limit": "0",
        })
        try:
            text = client.get_text(url)
        except AuditError:
            continue
        (raw_dir / f"{safe_name(accession)}_ena_{index}.tsv").write_text(text, encoding="utf-8")
        rows.extend(parse_delimited(text, delimiter="\t"))
    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        key = first(row, ["run_accession"]) or json.dumps(row, sort_keys=True)
        unique[key] = row
    return list(unique.values())


def normalize_run(candidate: Candidate, row: Mapping[str, Any], via: str) -> dict[str, str]:
    text = combined_text(row)
    states = infer_states(text)
    layout = first(row, ["LibraryLayout", "library_layout"]).upper()
    length = average_read_length(row)
    grade, reason, review = grade_junction(row)
    normalized: dict[str, str] = {
        "dataset_id": candidate.dataset_id,
        "query_accession": candidate.accession,
        "resolved_via": via,
        "run_accession": first(row, ["Run", "run_accession"]),
        "experiment_accession": first(row, ["Experiment", "experiment_accession"]),
        "study_accession": first(row, ["SRAStudy", "study_accession", "secondary_study_accession"]),
        "bioproject": first(row, ["BioProject", "bioproject"]),
        "biosample": first(row, ["BioSample", "secondary_sample_accession"]),
        "sample_accession": first(row, ["Sample", "sample_accession"]),
        "sample_title": first(row, ["SampleName", "sample_title", "sample_name"]),
        "sample_description": first(row, ["sample_description", "experiment_title", "Title"]),
        "library_name": first(row, ["LibraryName", "library_name"]),
        "library_strategy": first(row, ["LibraryStrategy", "library_strategy"]),
        "library_source": first(row, ["LibrarySource", "library_source"]),
        "library_selection": first(row, ["LibrarySelection", "library_selection"]),
        "library_layout": layout,
        "platform": first(row, ["Platform", "instrument_platform"]),
        "instrument_model": first(row, ["Model", "instrument_model"]),
        "read_count": first(row, ["spots", "read_count"]),
        "base_count": first(row, ["bases", "base_count"]),
        "avg_read_length": "" if length is None else f"{length:.3f}",
        "fastq_bytes": first(row, ["size_MB", "fastq_bytes"]),
        "fastq_md5": first(row, ["fastq_md5"]),
        "fastq_ftp": first(row, ["download_path", "fastq_ftp"]),
        "first_public": first(row, ["ReleaseDate", "first_public"]),
        "last_updated": first(row, ["LoadDate", "last_updated"]),
        "raw_reads_available": "yes" if first(row, ["Run", "run_accession", "download_path", "fastq_ftp"]) else "unknown",
        "junction_grade": grade,
        "junction_grade_reason": reason,
        "manual_review_required": review,
        "metadata_text": text,
    }
    normalized.update(states)
    return {field: normalized.get(field, "") for field in RUN_FIELDS}


def write_tsv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def values(rows: Sequence[Mapping[str, str]], field: str) -> set[str]:
    return {row.get(field, "") for row in rows if row.get(field, "") not in {"", "unknown"}}


def count_grade(rows: Sequence[Mapping[str, str]], grade: str) -> int:
    return sum(row.get("junction_grade") == grade for row in rows)


def summarize(candidate: Candidate, rows: Sequence[Mapping[str, str]], errors: Sequence[str], geo_text: str) -> dict[str, str]:
    layouts = values(rows, "library_layout")
    strategies = values(rows, "library_strategy")
    selections = values(rows, "library_selection")
    lengths = [float(row["avg_read_length"]) for row in rows if row.get("avg_read_length")]
    return {
        "dataset_id": candidate.dataset_id,
        "accession": candidate.accession,
        "priority": str(candidate.priority),
        "role": candidate.role,
        "expected_design": candidate.expected_design,
        "why_included": candidate.why_included,
        "resolved_runs": str(len(rows)),
        "raw_runs": str(sum(row.get("raw_reads_available") == "yes" for row in rows)),
        "high_junction_runs": str(count_grade(rows, "HIGH")),
        "medium_junction_runs": str(count_grade(rows, "MEDIUM")),
        "low_junction_runs": str(count_grade(rows, "LOW")),
        "unsuitable_runs": str(count_grade(rows, "UNSUITABLE")),
        "layouts": ";".join(sorted(layouts)),
        "strategies": ";".join(sorted(strategies)),
        "library_selections": ";".join(sorted(selections)),
        "minimum_read_length": f"{min(lengths):.1f}" if lengths else "",
        "maximum_read_length": f"{max(lengths):.1f}" if lengths else "",
        "ages": ";".join(sorted(values(rows, "inferred_age"))),
        "nmd_states": ";".join(sorted(values(rows, "inferred_nmd_state"))),
        "diet_states": ";".join(sorted(values(rows, "inferred_diet_state"))),
        "rnp2_states": ";".join(sorted(values(rows, "inferred_rnp2_state"))),
        "fractions": ";".join(sorted(values(rows, "inferred_fraction"))),
        "geo_soft_retrieved": "yes" if geo_text else "no",
        "audit_status": "resolved" if rows else "unresolved",
        "errors": " | ".join(errors),
    }


def capability(dataset_summary: Mapping[str, str], rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    age = values(rows, "inferred_age")
    nmd = values(rows, "inferred_nmd_state")
    diet = values(rows, "inferred_diet_state")
    rnp2 = values(rows, "inferred_rnp2_state")
    fraction = values(rows, "inferred_fraction")
    usable = any(row.get("junction_grade") in {"HIGH", "MEDIUM"} for row in rows)
    checks = [
        ("junction_IR", usable, "At least one HIGH or MEDIUM junction-grade RNA-seq run"),
        ("NMD_hidden", usable and {"on", "off"}.issubset(nmd), "Matched NMD-on and NMD-off states"),
        ("age_linked_NMD_hidden", usable and {"young", "old"}.issubset(age) and {"on", "off"}.issubset(nmd), "Young/old and NMD-on/off states within study"),
        ("DR_suppression_of_NMD_hidden", usable and {"control", "DR"}.issubset(diet) and {"on", "off"}.issubset(nmd), "Control/DR and NMD-on/off states within study"),
        ("RNP2_dependency", usable and {"control", "DR"}.issubset(diet) and {"on", "off"}.issubset(nmd) and {"plus", "perturbed"}.issubset(rnp2), "Diet, NMD, and RNP-2 states within study"),
        ("cytoplasmic_localization", usable and "cytoplasmic" in fraction and bool({"nuclear", "whole_or_input"}.intersection(fraction)), "Cytoplasmic plus nuclear or whole/input RNA"),
        ("complete_JM105_worm_factorial", usable and {"young", "old"}.issubset(age) and {"control", "DR"}.issubset(diet) and {"on", "off"}.issubset(nmd) and {"plus", "perturbed"}.issubset(rnp2), "Age × diet × NMD × RNP-2 states within study"),
    ]
    return [
        {
            "dataset_id": dataset_summary["dataset_id"],
            "accession": dataset_summary["accession"],
            "contrast": name,
            "estimable_from_inferred_metadata": "yes" if passed else "no",
            "criterion": criterion,
            "manual_confirmation_required": "yes",
        }
        for name, passed, criterion in checks
    ]


def markdown_table(rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> str:
    if not rows:
        return "_No rows._\n"
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "\\|") for field in fields) + " |")
    return "\n".join(lines) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    candidates = read_candidates(args.datasets)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    raw_dir = output / "raw_metadata"; raw_dir.mkdir()
    client = Client(args.email, args.api_key, args.timeout, args.retries)

    all_runs: list[dict[str, str]] = []
    summaries: list[dict[str, str]] = []
    capabilities: list[dict[str, str]] = []
    unresolved: list[str] = []

    for candidate in candidates:
        dataset_raw = raw_dir / safe_name(candidate.dataset_id); dataset_raw.mkdir()
        errors: list[str] = []
        geo_text = ""
        accessions = [candidate.accession]
        if candidate.accession.upper().startswith("GSE"):
            try:
                geo_text, relations = fetch_geo_soft(client, candidate.accession.upper(), dataset_raw)
                accessions.extend(relations)
            except Exception as exc:
                errors.append(f"GEO SOFT: {exc}")
        run_rows: list[dict[str, str]] = []
        seen_runs: set[str] = set()
        for accession in dict.fromkeys(accessions):
            ncbi_rows: list[dict[str, str]] = []
            try:
                ncbi_rows = fetch_sra_runinfo(client, accession, dataset_raw)
            except Exception as exc:
                errors.append(f"SRA {accession}: {exc}")
            for raw in ncbi_rows:
                normalized = normalize_run(candidate, raw, f"NCBI_SRA:{accession}")
                key = normalized["run_accession"] or json.dumps(normalized, sort_keys=True)
                if key not in seen_runs:
                    run_rows.append(normalized); seen_runs.add(key)
            if ncbi_rows:
                continue
            try:
                ena_rows = fetch_ena_runs(client, accession, dataset_raw)
            except Exception as exc:
                errors.append(f"ENA {accession}: {exc}")
                ena_rows = []
            for raw in ena_rows:
                normalized = normalize_run(candidate, raw, f"ENA:{accession}")
                key = normalized["run_accession"] or json.dumps(normalized, sort_keys=True)
                if key not in seen_runs:
                    run_rows.append(normalized); seen_runs.add(key)

        summary = summarize(candidate, run_rows, errors, geo_text)
        summaries.append(summary)
        capabilities.extend(capability(summary, run_rows))
        all_runs.extend(run_rows)
        if not run_rows:
            unresolved.append(candidate.dataset_id)

    summary_fields = list(summaries[0].keys()) if summaries else []
    capability_fields = list(capabilities[0].keys()) if capabilities else []
    write_tsv(output / "run_manifest.tsv", all_runs, RUN_FIELDS)
    write_tsv(output / "dataset_summary.tsv", summaries, summary_fields)
    write_tsv(output / "contrast_capability.tsv", capabilities, capability_fields)

    pilot_rows = [
        row for row in all_runs
        if row["junction_grade"] in {"HIGH", "MEDIUM"} and row["raw_reads_available"] == "yes"
    ]
    pilot_fields = [
        "dataset_id", "query_accession", "run_accession", "library_layout",
        "avg_read_length", "library_selection", "junction_grade", "fastq_ftp",
        "fastq_md5", "fastq_bytes",
    ]
    write_tsv(output / "pilot_download_candidates.tsv", pilot_rows, pilot_fields)

    report = [
        "# JM105–C. elegans Step 1 metadata audit",
        "",
        f"Generated UTC: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"Script version: {VERSION}",
        "",
        "This step does not download sequencing reads. Inferred biological labels are screening aids and must be manually confirmed against sample-level metadata and publications before modelling.",
        "",
        "## Dataset resolution",
        "",
        markdown_table(summaries, ["dataset_id", "accession", "priority", "resolved_runs", "high_junction_runs", "medium_junction_runs", "audit_status"]),
        "## JM105 contrast capability",
        "",
        markdown_table(capabilities, ["dataset_id", "contrast", "estimable_from_inferred_metadata", "criterion"]),
        "## Interpretation boundary",
        "",
        "A study can support NMD-hidden retained introns without proving cytoplasmic leakage. The strongest leakage claim requires cytoplasmic enrichment or matched fractionated RNA in addition to NMD-dependent stabilization.",
        "",
        "RNP-2 perturbation tests whether dietary-restriction suppression depends on the worm U1A genetic handle. It is not assumed that deleting rnp-2 itself suppresses leakage.",
        "",
    ]
    if unresolved:
        report.extend(["## Unresolved candidates", "", "\n".join(f"- {item}" for item in unresolved), ""])
    (output / "AUDIT_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    spec = {
        "script_version": VERSION,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "candidate_count": len(candidates),
        "resolved_run_count": len(all_runs),
        "unresolved_dataset_ids": unresolved,
        "sign_conventions": {
            "IRratio": "(intron_count + 1) / (host_exon_count + 1)",
            "NMD_hidden": "IR(NMD off) - IR(matched NMD on)",
            "age_linked_NMD_hidden": "NMD_hidden(old) - NMD_hidden(young)",
            "CR_suppression": "age_linked_NMD_hidden(control diet) - age_linked_NMD_hidden(DR)",
            "RNP2_dependent_CR_suppression": "CR_suppression(RNP-2+) - CR_suppression(rnp-2 perturbed)",
        },
    }
    (output / "audit_specification.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")

    checksum_rows = []
    for path in sorted(file for file in output.rglob("*") if file.is_file()):
        checksum_rows.append({"sha256": sha256(path), "relative_path": str(path.relative_to(output))})
    write_tsv(output / "FILE_SHA256.tsv", checksum_rows, ["sha256", "relative_path"])

    print(f"Resolved {len(all_runs)} runs across {len(candidates)} candidate datasets.")
    print(f"Unresolved candidate datasets: {len(unresolved)}")
    print(f"Outputs: {output}")
    if args.strict and unresolved:
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        raise
