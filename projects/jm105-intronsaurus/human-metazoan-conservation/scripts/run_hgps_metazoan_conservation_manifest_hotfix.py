#!/usr/bin/env python3
"""
Evidence-backed metadata corrections for the JM105 HGPS + metazoan CR workflow.

Corrections confirmed from public GEO/SRA metadata:
- GSE118633 contains 2 control and 3 HGPS RNA-seq runs.
- GSE222163 resolves through BioProject PRJNA918398.
- GSE222163 control titles are replicate-suffixed (control1, control2, ...).

The module is intentionally importable: importing it applies the metadata
corrections to the canonical core module without executing the monolithic run.
"""
from __future__ import annotations

import re
from typing import Optional

import run_hgps_metazoan_conservation as core

core.DATASETS["GSE118633"] = core.DatasetSpec(
    accession="GSE118633",
    species="human",
    role="HGPS discovery / independent total-RNA validation",
    expected_groups={"control": 2, "hgps": 3},
    include_groups=("control", "hgps"),
)

_original_runinfo = core.runinfo


def _runinfo_with_bioproject_fallback(study_or_geo, cache_dir):
    resolved = "PRJNA918398" if study_or_geo == "GSE222163" else study_or_geo
    return _original_runinfo(resolved, cache_dir)


_original_classify_group = core.classify_group


def _classify_group_with_replica_controls(
    accession: str,
    sample: dict,
) -> Optional[str]:
    if accession != "GSE222163":
        return _original_classify_group(accession, sample)

    blob = core.normalize_blob(sample)
    if re.search(r"exercise|treadmill|combined|\bce\d*\b", blob):
        return None

    is_cr = bool(re.search(r"calori(?:c|e) restriction|\bcr\d*\b", blob))
    is_control = bool(
        re.search(r"\b(?:control|ctrl)\d*\b|ad libitum|\bal\d*\b", blob)
        or re.search(
            r"\b(?:bat|skm)[_ -]?(?:c|ctrl|control)\d+\b",
            blob,
        )
    )
    if not (is_cr or is_control):
        return None
    if re.search(r"brown adipose|\bbat\b", blob):
        return "bat_cr" if is_cr else "bat_control"
    if re.search(r"skeletal muscle|gastrocnemius|\bskm\b", blob):
        return "skm_cr" if is_cr else "skm_control"
    return None


core.runinfo = _runinfo_with_bioproject_fallback
core.classify_group = _classify_group_with_replica_controls
core.PIPELINE_VERSION = "2026-07-20.5-distributed"

if __name__ == "__main__":
    core.main()
