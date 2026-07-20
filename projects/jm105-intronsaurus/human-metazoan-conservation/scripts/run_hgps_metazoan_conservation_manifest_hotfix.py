#!/usr/bin/env python3
"""
Evidence-backed manifest corrections for the JM105 HGPS + metazoan CR pipeline.

This wrapper preserves the full analysis implementation while applying only
metadata corrections confirmed from the public GEO records:

- GSE118633 contains 2 control RNA-seq samples and 3 HGPS RNA-seq samples.
- GSE222163 raw runs resolve through BioProject PRJNA918398.
- GSE222163 control titles are replicate-suffixed (for example,
  "BAT control1" and "SkM control4"), so the classifier must accept
  controlN/ctrlN rather than requiring a terminal word boundary after control.

No biological inclusion criteria, contrasts, PEI definitions, reference builds,
or Figure 2 scope rules are changed.
"""

from __future__ import annotations

import re
from typing import Optional

import run_hgps_metazoan_conservation as core


# Evidence-backed public design: 2 control RNA-seq and 3 HGPS RNA-seq samples.
core.DATASETS["GSE118633"] = core.DatasetSpec(
    accession="GSE118633",
    species="human",
    role="HGPS discovery / independent total-RNA validation",
    expected_groups={"control": 2, "hgps": 3},
    include_groups=("control", "hgps"),
)


# GSE222163 exposes BioProject PRJNA918398 rather than an SRP relation in GEO.
_original_runinfo = core.runinfo


def _runinfo_with_bioproject_fallback(study_or_geo, cache_dir):
    resolved = "PRJNA918398" if study_or_geo == "GSE222163" else study_or_geo
    return _original_runinfo(resolved, cache_dir)


core.runinfo = _runinfo_with_bioproject_fallback


# Public titles use BAT control1-control3 and SkM control1-control4. Python's
# \bcontrol\b does not match control1 because the following digit is a word
# character. Reproduce the prespecified GSE222163 classifier with that one
# evidence-backed naming correction.
_original_classify_group = core.classify_group


def _classify_group_with_replica_controls(
    accession: str,
    sample: dict,
) -> Optional[str]:
    if accession != "GSE222163":
        return _original_classify_group(accession, sample)

    blob = core.normalize_blob(sample)

    # Exercise and combined CR+exercise groups remain explicitly out of scope.
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


core.classify_group = _classify_group_with_replica_controls
core.PIPELINE_VERSION = "2026-07-20.3"


if __name__ == "__main__":
    core.main()
