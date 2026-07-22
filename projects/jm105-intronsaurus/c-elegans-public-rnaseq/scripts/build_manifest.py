#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping

from common import PIPELINE_VERSION, read_tsv, write_tsv

NCBI_DELAY = 0.38

GSE240821_GSM_GROUPS = {
    # N2 (WT), empty-vector RNAi
    "GSM7709970": "n2_ev",
    "GSM7709971": "n2_ev",
    "GSM7709972": "n2_ev",
    # eat-2(ad465), empty-vector RNAi
    "GSM7709988": "eat2_ev",
    "GSM7709989": "eat2_ev",
    # eat-2(ad465), daf-16 RNAi
    "GSM7709990": "eat2_daf16",
    "GSM7709991": "eat2_daf16",
    # eat-2(ad465), pha-4 RNAi
    "GSM7709992": "eat2_pha4",
    "GSM7709993": "eat2_pha4",
    # eat-2(ad465);mxl-2(tm1516), empty-vector RNAi
    "GSM7709994": "eat2_mxl2_ev",
    "GSM7709995": "eat2_mxl2_ev",
    "GSM7709996": "eat2_mxl2_ev",
}


def request_text(url: str, retries: int = 5, timeout: int = 120) -> str:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": f"JM105-Celegans/{PIPELINE_VERSION} ({os.environ.get('NCBI_EMAIL', 'no-email')})",
                    "Accept": "*/*",
                },
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            return data.decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 12))
    raise RuntimeError(f"Request failed: {url}: {last_error}")


def eutils(endpoint: str, params: Mapping[str, str]) -> str:
    merged = dict(params)
    merged["tool"] = "jm105_celegans_full_pipeline"
    email = os.environ.get("NCBI_EMAIL", "").strip()
    api_key = os.environ.get("NCBI_API_KEY", "").strip()
    if email:
        merged["email"] = email
    if api_key:
        merged["api_key"] = api_key
    time.sleep(NCBI_DELAY)
    return request_text(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        + endpoint
        + "?"
        + urllib.parse.urlencode(merged)
    )


def geo_bucket(accession: str) -> str:
    digits = re.fullmatch(r"GSE(\d+)", accession.upper()).group(1)
    prefix = digits[:-3] if len(digits) > 3 else ""
    return f"GSE{prefix}nnn"


def parse_geo_soft(text: str) -> dict[str, dict[str, str]]:
    samples: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    current_id = ""
    characteristic_lines: list[str] = []
    description_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("^SAMPLE = "):
            if current is not None:
                current["characteristics"] = " | ".join(characteristic_lines)
                current["description"] = " | ".join(description_lines)
                samples[current_id] = current
            current_id = line.split("=", 1)[1].strip()
            current = {"gsm": current_id}
            characteristic_lines = []
            description_lines = []
        elif current is not None:
            if line.startswith("!Sample_title = "):
                current["title"] = line.split("=", 1)[1].strip()
            elif line.startswith("!Sample_source_name_ch1 = "):
                current["source"] = line.split("=", 1)[1].strip()
            elif line.startswith("!Sample_characteristics_ch1 = "):
                characteristic_lines.append(line.split("=", 1)[1].strip())
            elif line.startswith("!Sample_description = "):
                description_lines.append(line.split("=", 1)[1].strip())
            elif line.startswith("!Sample_relation = "):
                relation = line.split("=", 1)[1].strip()
                current.setdefault("relations", "")
                current["relations"] += " | " + relation
    if current is not None:
        current["characteristics"] = " | ".join(characteristic_lines)
        current["description"] = " | ".join(description_lines)
        samples[current_id] = current
    return samples


def fetch_geo(accession: str, raw_dir: Path) -> dict[str, dict[str, str]]:
    url = (
        f"https://ftp.ncbi.nlm.nih.gov/geo/series/{geo_bucket(accession)}/"
        f"{accession}/soft/{accession}_family.soft.gz"
    )
    text = request_text(url)
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{accession}_family.soft").write_text(text, encoding="utf-8")
    return parse_geo_soft(text)


def extract_sra_experiments(
    geo_samples: Mapping[str, Mapping[str, str]],
) -> list[str]:
    experiments: set[str] = set()
    for metadata in geo_samples.values():
        relations = str(metadata.get("relations", "") or "")
        experiments.update(
            match.upper()
            for match in re.findall(r"\b(?:SRX|ERX|DRX)\d+\b", relations, flags=re.I)
        )
    return sorted(experiments)


def fetch_runinfo(
    accession: str,
    raw_dir: Path,
    geo_samples: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    raw_dir.mkdir(parents=True, exist_ok=True)

    if accession.upper().startswith("GSE"):
        queries = extract_sra_experiments(geo_samples or {})
        if not queries:
            audit = {
                "query_accession": accession,
                "resolved_experiments": [],
                "idlist": [],
                "problem": "No SRX/ERX/DRX relations were present in the GEO family SOFT file.",
            }
            (raw_dir / f"{accession}_esearch.json").write_text(
                json.dumps(audit, indent=2) + "\n",
                encoding="utf-8",
            )
            return []
    else:
        queries = [accession]

    all_ids: list[str] = []
    audit_rows: list[dict[str, object]] = []
    for query_accession in queries:
        search_text = eutils(
            "esearch.fcgi",
            {
                "db": "sra",
                "term": query_accession,
                "retmode": "json",
                "retmax": "10000",
            },
        )
        parsed = json.loads(search_text)
        ids = parsed.get("esearchresult", {}).get("idlist", [])
        audit_rows.append({"query_accession": query_accession, "idlist": ids})
        all_ids.extend(str(value) for value in ids)

    unique_ids = list(dict.fromkeys(all_ids))
    (raw_dir / f"{accession}_esearch.json").write_text(
        json.dumps(
            {
                "query_accession": accession,
                "resolved_experiments": queries,
                "queries": audit_rows,
                "idlist": unique_ids,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if not unique_ids:
        return []

    runinfo = eutils(
        "efetch.fcgi",
        {
            "db": "sra",
            "id": ",".join(unique_ids),
            "rettype": "runinfo",
            "retmode": "text",
        },
    )
    (raw_dir / f"{accession}_runinfo.csv").write_text(runinfo, encoding="utf-8")
    return list(csv.DictReader(io.StringIO(runinfo.lstrip("\ufeff\r\n "))))

def first(row: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = str(row.get(key, "") or "").strip()
        if value:
            return value
    return ""


def normalized_text(*parts: str) -> str:
    text = " | ".join(part for part in parts if part)
    text = text.lower().replace("Δ", "delta")
    return re.sub(r"\s+", " ", text)


def parse_replicate(text: str) -> str:
    patterns = [r"rep(?:licate)?\s*[-_ ]?(\d+)", r"(?:^|[-_ ])r(\d+)(?:$|[-_ ])", r"(?:in|ip)(\d+)$"]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(1)
    return ""


def classify(dataset_id: str, text: str, gsm: str = "") -> dict[str, str] | None:
    low = text.lower()
    result = {
        "group": "",
        "strain": "",
        "age_day": "",
        "nmd_state": "unknown",
        "diet_state": "unknown",
        "perturbation": "none",
        "fraction": "input",
    }

    if dataset_id == "NMD_IIS":
        if "smg-2" in low and "daf-2" in low:
            result.update(group="daf2_smg2", strain="daf-2(e1370);smg-2(qd101)", age_day="1", nmd_state="off", diet_state="IIS")
        elif "daf-2" in low:
            result.update(group="daf2", strain="daf-2(e1370)", age_day="1", nmd_state="on", diet_state="IIS")
        elif "smg-2" in low:
            result.update(group="smg2", strain="smg-2(qd101)", age_day="1", nmd_state="off", diet_state="control")
        elif "wild-type" in low or "wild type" in low or re.search(r"\bn2\b", low):
            result.update(group="wt", strain="N2", age_day="1", nmd_state="on", diet_state="control")
        else:
            return None
        return result

    if dataset_id == "DIRECT_NMD":
        compact = re.sub(r"[^a-z0-9]", "", low)
        if "n2in" in compact:
            result.update(group="n2_input", strain="N2", nmd_state="on", fraction="input")
        elif "s1in" in compact:
            result.update(group="smg1_input", strain="smg-1(r910)", nmd_state="off", fraction="input")
        elif "s1ip" in compact:
            result.update(group="smg1_ip", strain="smg-1(r910)", nmd_state="off", fraction="SMG-2_IP")
        elif "s2in" in compact:
            result.update(group="smg1_smg2_input", strain="smg-1(r910);smg-2(r915)", nmd_state="off", fraction="input")
        elif "s2ip" in compact:
            result.update(group="smg1_smg2_ip", strain="smg-1(r910);smg-2(r915)", nmd_state="off", fraction="SMG-2_IP_negative_control")
        else:
            return None
        return result

    if dataset_id == "AGING":
        strain_match = re.search(r"(?:^|[-_ ])(fem|gem)(?:[-_ ]|$)", low)
        day_match = re.search(r"day\s*[-_ ]?(\d{1,2})", low)
        if not strain_match or not day_match:
            return None
        strain = strain_match.group(1)
        day = day_match.group(1)
        result.update(group=f"{strain}_day{day}", strain=strain, age_day=day, nmd_state="on", diet_state="control")
        return result

    if dataset_id == "DR_REPLICATION":
        # GSE240821 is assigned from exact GEO sample accessions. This prevents
        # descriptive text shared across the series from moving a run into the
        # wrong genotype/RNAi group. Only the prespecified five groups enter the
        # JM105 worm analysis; all other GSE240821 combinations remain excluded.
        exact_group = GSE240821_GSM_GROUPS.get(gsm.upper())
        if exact_group == "n2_ev":
            result.update(
                group="n2_ev",
                strain="N2",
                age_day="2",
                nmd_state="on",
                diet_state="control",
                perturbation="empty_vector_RNAi",
            )
            return result
        if exact_group == "eat2_ev":
            result.update(
                group="eat2_ev",
                strain="eat-2(ad465)",
                age_day="2",
                nmd_state="on",
                diet_state="DR",
                perturbation="empty_vector_RNAi",
            )
            return result
        if exact_group == "eat2_daf16":
            result.update(
                group="eat2_daf16",
                strain="eat-2(ad465)",
                age_day="2",
                nmd_state="on",
                diet_state="DR",
                perturbation="daf-16_RNAi",
            )
            return result
        if exact_group == "eat2_pha4":
            result.update(
                group="eat2_pha4",
                strain="eat-2(ad465)",
                age_day="2",
                nmd_state="on",
                diet_state="DR",
                perturbation="pha-4_RNAi",
            )
            return result
        if exact_group == "eat2_mxl2_ev":
            result.update(
                group="eat2_mxl2_ev",
                strain="eat-2(ad465);mxl-2(tm1516)",
                age_day="2",
                nmd_state="on",
                diet_state="DR",
                perturbation="mxl-2",
            )
            return result
        return None

        # The text classifier below is retained as unreachable documentation of
        # the superseded heuristic and is intentionally not used for GSE240821.
        is_eat2 = "eat-2" in low or "eat2" in low
        is_mxl2 = "mxl-2" in low or "mxl2" in low
        if "pha-4" in low or "pha4" in low:
            rnai = "pha4"
        elif "daf-16" in low or "daf16" in low:
            rnai = "daf16"
        elif "ev rnai" in low or "empty" in low or "vector" in low:
            rnai = "ev"
        else:
            rnai = "unknown"
        if is_eat2 and is_mxl2 and rnai == "ev":
            result.update(group="eat2_mxl2_ev", strain="eat-2(ad465);mxl-2(tm1516)", age_day="2", diet_state="DR", perturbation="mxl-2")
        elif is_eat2 and not is_mxl2 and rnai == "ev":
            result.update(group="eat2_ev", strain="eat-2(ad465)", age_day="2", diet_state="DR")
        elif is_eat2 and not is_mxl2 and rnai == "pha4":
            result.update(group="eat2_pha4", strain="eat-2(ad465)", age_day="2", diet_state="DR", perturbation="pha-4_RNAi")
        elif is_eat2 and not is_mxl2 and rnai == "daf16":
            result.update(group="eat2_daf16", strain="eat-2(ad465)", age_day="2", diet_state="DR", perturbation="daf-16_RNAi")
        elif not is_eat2 and not is_mxl2 and rnai == "ev" and ("n2" in low or "wild" in low):
            result.update(group="n2_ev", strain="N2", age_day="2", diet_state="control")
        else:
            return None
        return result

    if dataset_id == "DR_PRIMARY":
        is_eat2 = "eat-2" in low or "eat2" in low
        is_wt = bool(
            re.search(r"(?:^|[^a-z0-9])wt(?:[^a-z0-9]|$)", low)
            or "wild-type" in low
            or "wild type" in low
            or re.search(r"(?:^|[^a-z0-9])n2(?:[^a-z0-9]|$)", low)
        )
        has_hrpu1 = any(token in low for token in ["hrpu-1", "hrpu1", "y41e3.11"])
        has_smg2 = "smg-2" in low or "smg2" in low
        has_control = any(
            token in low
            for token in [
                "control rnai",
                "vector rnai",
                "empty vector",
                "l4440",
                "_control_",
                " control ",
            ]
        )
        day_match = re.search(r"day\s*[-_ ]?(\d+)", low)
        age_day = day_match.group(1) if day_match else "1"

        if not is_wt and not is_eat2:
            return None

        if age_day == "1" and not has_control and not has_smg2 and not has_hrpu1:
            if is_wt:
                result.update(group="baseline_wt_day1", strain="N2", age_day="1", nmd_state="on", diet_state="control")
            else:
                result.update(group="baseline_eat2_day1", strain="eat-2(ad1116)", age_day="1", nmd_state="on", diet_state="DR")
            return result

        if age_day == "1" and has_smg2:
            if is_wt:
                result.update(group="rnai_wt_smg2_day1", strain="N2", age_day="1", nmd_state="off", diet_state="control", perturbation="smg-2_RNAi")
            else:
                result.update(group="rnai_eat2_smg2_day1", strain="eat-2(ad1116)", age_day="1", nmd_state="off", diet_state="DR", perturbation="smg-2_RNAi")
            return result

        if age_day == "1" and has_control:
            if is_wt:
                result.update(group="rnai_wt_control_day1", strain="N2", age_day="1", nmd_state="on", diet_state="control", perturbation="control_RNAi")
            else:
                result.update(group="rnai_eat2_control_day1", strain="eat-2(ad1116)", age_day="1", nmd_state="on", diet_state="DR", perturbation="control_RNAi")
            return result

        if age_day == "3" and is_eat2 and has_hrpu1:
            result.update(group="rnai_eat2_hrpu1_day3", strain="eat-2(ad1116)", age_day="3", nmd_state="on", diet_state="DR", perturbation="hrpu-1_RNAi")
            return result

        if age_day == "3" and has_control:
            if is_wt:
                result.update(group="rnai_wt_control_day3", strain="N2", age_day="3", nmd_state="on", diet_state="control", perturbation="control_RNAi")
            else:
                result.update(group="rnai_eat2_control_day3", strain="eat-2(ad1116)", age_day="3", nmd_state="on", diet_state="DR", perturbation="control_RNAi")
            return result

        return None

    return None


def merge_geo_text(
    run: Mapping[str, str],
    geo_samples: Mapping[str, Mapping[str, str]],
) -> tuple[str, str]:
    sample_name = first(run, "SampleName", "Sample")
    biosample = first(run, "BioSample")
    experiment = first(run, "Experiment")

    matches: list[Mapping[str, str]] = []
    if sample_name in geo_samples:
        matches.append(geo_samples[sample_name])

    for metadata in geo_samples.values():
        relations = str(metadata.get("relations", "") or "")
        if biosample and biosample in relations:
            matches.append(metadata)
            continue
        if experiment and experiment in relations:
            matches.append(metadata)

    if not matches:
        return "", ""

    metadata = matches[0]
    text = " | ".join(
        [
            str(metadata.get("title", "") or ""),
            str(metadata.get("source", "") or ""),
            str(metadata.get("characteristics", "") or ""),
            str(metadata.get("description", "") or ""),
        ]
    )
    return str(metadata.get("gsm", "") or ""), text

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    output = args.output_dir.resolve()
    raw_dir = output / "raw_metadata"
    output.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    dataset_rows = [row for row in read_tsv(args.datasets) if row.get("include", "yes").lower() == "yes"]

    manifest: list[dict[str, object]] = []
    excluded: list[dict[str, str]] = []
    dataset_summary: list[dict[str, object]] = []

    for dataset in dataset_rows:
        dataset_id = dataset["dataset_id"]
        accession = dataset["accession"]
        geo_samples: dict[str, dict[str, str]] = {}
        if accession.upper().startswith("GSE"):
            geo_samples = fetch_geo(accession, raw_dir)
        run_rows = fetch_runinfo(accession, raw_dir, geo_samples)
        included_count = 0
        for run in run_rows:
            gsm, geo_text = merge_geo_text(run, geo_samples)
            run_text = normalized_text(
                first(run, "SampleName"),
                first(run, "LibraryName"),
                first(run, "Experiment"),
                first(run, "SRAStudy"),
                first(run, "BioSample"),
                geo_text,
            )
            class_info = classify(dataset_id, run_text, gsm)
            if class_info is None:
                excluded.append({
                    "dataset_id": dataset_id,
                    "accession": accession,
                    "run": first(run, "Run"),
                    "sample_name": first(run, "SampleName"),
                    "reason": "not in the prespecified analysis groups or metadata could not be classified",
                    "metadata_text": run_text,
                })
                continue
            run_accession = first(run, "Run")
            if not run_accession:
                continue
            biological_sample_id = first(run, "BioSample") or first(run, "Sample") or gsm or first(run, "Experiment") or run_accession
            replicate = parse_replicate(run_text)
            manifest.append({
                "dataset_id": dataset_id,
                "accession": accession,
                "run": run_accession,
                "experiment": first(run, "Experiment"),
                "biosample": first(run, "BioSample"),
                "biological_sample_id": biological_sample_id,
                "gsm": gsm,
                "sample_name": first(run, "SampleName"),
                "group": class_info["group"],
                "strain": class_info["strain"],
                "age_day": class_info["age_day"],
                "nmd_state": class_info["nmd_state"],
                "diet_state": class_info["diet_state"],
                "perturbation": class_info["perturbation"],
                "fraction": class_info["fraction"],
                "replicate": replicate,
                "library_layout": first(run, "LibraryLayout"),
                "library_selection": first(run, "LibrarySelection"),
                "library_strategy": first(run, "LibraryStrategy"),
                "platform": first(run, "Platform"),
                "instrument": first(run, "Model"),
                "spots": first(run, "spots"),
                "bases": first(run, "bases"),
                "metadata_text": run_text,
            })
            included_count += 1
        dataset_summary.append({
            "dataset_id": dataset_id,
            "accession": accession,
            "role": dataset["role"],
            "resolved_runs": len(run_rows),
            "included_runs": included_count,
            "excluded_runs": len(run_rows) - included_count,
        })

    manifest.sort(key=lambda row: (str(row["dataset_id"]), str(row["group"]), str(row["biological_sample_id"]), str(row["run"])))
    for index, row in enumerate(manifest, start=1):
        row["array_index"] = index

    fields = [
        "array_index", "dataset_id", "accession", "run", "experiment", "biosample", "biological_sample_id", "gsm", "sample_name",
        "group", "strain", "age_day", "nmd_state", "diet_state", "perturbation", "fraction", "replicate",
        "library_layout", "library_selection", "library_strategy", "platform", "instrument", "spots", "bases", "metadata_text",
    ]
    write_tsv(output / "run_manifest.tsv", manifest, fields)
    write_tsv(output / "excluded_runs.tsv", excluded, ["dataset_id", "accession", "run", "sample_name", "reason", "metadata_text"])
    write_tsv(output / "dataset_summary.tsv", dataset_summary, ["dataset_id", "accession", "role", "resolved_runs", "included_runs", "excluded_runs"])

    group_counts: dict[tuple[str, str], int] = {}
    for row in manifest:
        key = (str(row["dataset_id"]), str(row["group"]))
        group_counts[key] = group_counts.get(key, 0) + 1
    count_rows = [{"dataset_id": key[0], "group": key[1], "runs": value} for key, value in sorted(group_counts.items())]
    write_tsv(output / "group_counts.tsv", count_rows, ["dataset_id", "group", "runs"])

    required = {
        "NMD_IIS": {"wt", "smg2", "daf2", "daf2_smg2"},
        "DIRECT_NMD": {"n2_input", "smg1_input", "smg1_ip", "smg1_smg2_input", "smg1_smg2_ip"},
        "AGING": set(),
        "DR_REPLICATION": {"n2_ev", "eat2_ev", "eat2_pha4", "eat2_daf16", "eat2_mxl2_ev"},
        "DR_PRIMARY": {
            "baseline_wt_day1",
            "baseline_eat2_day1",
            "rnai_wt_control_day1",
            "rnai_wt_smg2_day1",
            "rnai_eat2_control_day1",
            "rnai_eat2_smg2_day1",
            "rnai_wt_control_day3",
            "rnai_eat2_control_day3",
            "rnai_eat2_hrpu1_day3",
        },
    }
    problems: list[str] = []
    for dataset_id, groups in required.items():
        observed = {group for (ds, group), count in group_counts.items() if ds == dataset_id and count > 0}
        missing = sorted(groups.difference(observed))
        if missing:
            problems.append(f"{dataset_id}: missing groups {', '.join(missing)}")
    aging_days = sorted({int(row["age_day"]) for row in manifest if row["dataset_id"] == "AGING" and str(row["age_day"]).isdigit()})
    if len(aging_days) < 4:
        problems.append(f"AGING: only {len(aging_days)} distinct adult days were classified")

    report_lines = [
        "# C. elegans public RNA-seq manifest gate",
        "",
        f"Pipeline version: `{PIPELINE_VERSION}`",
        "",
        "The full JM105 age × dietary restriction × NMD × rnp-2 factorial is not present in public worm RNA-seq. This manifest intentionally triangulates separate studies.",
        "",
        "## Group counts",
        "",
        "| dataset | group | runs |",
        "|---|---|---:|",
    ]
    report_lines.extend(f"| {row['dataset_id']} | {row['group']} | {row['runs']} |" for row in count_rows)
    report_lines.extend(["", "## Gate", ""])
    if problems:
        report_lines.extend(["**FAIL**", ""] + [f"- {problem}" for problem in problems])
    else:
        report_lines.append("**PASS** — all prespecified primary groups were resolved.")
    report_lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "- `eat-2` is genetic dietary restriction.",
        "- `daf-2` is reduced insulin/IGF signaling, not caloric restriction.",
        "- GSE100929 SMG-2 IP supports direct association; input stabilization and IP enrichment are evaluated separately.",
        "- None of these datasets alone proves cytoplasmic pre-mRNA leakage.",
    ])
    (output / "MANIFEST_GATE.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    (output / "manifest_status.json").write_text(json.dumps({"pipeline_version": PIPELINE_VERSION, "n_runs": len(manifest), "problems": problems}, indent=2) + "\n", encoding="utf-8")
    if problems:
        raise SystemExit("Manifest gate failed: " + " | ".join(problems))
    print(f"Manifest gate passed with {len(manifest)} runs.")


if __name__ == "__main__":
    main()
