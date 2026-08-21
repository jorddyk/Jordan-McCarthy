# 2026-07-20 manifest-gate hotfix

## Observed Euler failure

Job `7867637` passed environment creation and entered the public-data pipeline, then stopped at the manifest gate before raw-read download.

Observed failures:

- `GSE118633 control`: expected 3, observed 2.
- `GSE222163 bat_control`: expected 3, observed 0.
- `GSE222163 skm_control`: expected 3, observed 0.

## Evidence-backed correction

- The public GSE118633 series contains 2 control RNA-seq samples and 3 HGPS RNA-seq samples.
- GSE222163 links to BioProject `PRJNA918398`; RunInfo must be resolved through that accession rather than the GEO accession.
- GSE222163 retains the original inclusion fence: BAT control/CR and SkM control/CR only; exercise and combined groups remain excluded.

## Implementation

- Added `scripts/run_hgps_metazoan_conservation_manifest_hotfix.py`.
- Updated the Slurm launcher to execute the wrapper.
- Updated the PowerShell uploader to transfer the wrapper.
- Updated the README with the evidence-backed replicate counts and BioProject mapping.

No PEI definition, contrast, reference build, Figure 2 scope rule, or biological inclusion criterion was changed.
