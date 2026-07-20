#!/usr/bin/env python3
"""
Evidence-backed manifest hotfix for the JM105 HGPS + metazoan CR pipeline.

This wrapper preserves the full canonical analysis implementation while applying
only two metadata corrections confirmed from the public GEO records:

- GSE118633 contains 2 control RNA-seq samples and 3 HGPS RNA-seq samples.
- GSE222163 raw runs resolve through BioProject PRJNA918398.

No biological inclusion criteria, contrasts, PEI definitions, reference builds,
or Figure 2 scope rules are changed.
"""

from __future__ import annotations

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
core.PIPELINE_VERSION = "2026-07-20.2"


if __name__ == "__main__":
    core.main()
