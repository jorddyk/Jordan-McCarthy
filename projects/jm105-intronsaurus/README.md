# JM105 / Intronsaurus Analysis

Human goal: preserve canonical code supporting Jordan's JM105 RNA-seq, intron
retention, NMD-hidden leakage, Mud1/CR, aging, and manuscript figure workflows.

This project is for complete analysis code, reusable figure-generation/browser
code, methods, and provenance—not raw sequencing data.

## Intended structure

```text
projects/jm105-intronsaurus/
  analysis/
  alignment/
  figures/
  transformation-protocol-rnaseq/
  jm134-starvation-switch/
  jm133-weak-5ss-mud1/
  figure2-candidate-gate/
  human-metazoan-conservation/
  intronsaurus-browser/
  metadata/
  docs/
  README.md
```

## Current scientific guardrails

- Never generate fake biological data.
- Use `NO DATA` for experiments or panels that have not been performed.
- Figure 2 uses total/rRNA-depleted JM105 only unless Jordan explicitly changes it.
- Poly-A, P-versus-T, mRNA-like and P−T constructs remain outside Figure 2.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host-transcript abundance from protein abundance.
- Caloric restriction is not automatically starvation.
- Do not equate physiological aging with damage, abnormality, HGPS, or disease.
- Whole-cell human or mouse RNA-seq may establish intron-containing RNA exposure,
  not nuclear export, translation, or NMD degradation.

## Canonical code imported

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | canonical | Old-selective NMD-revealed intron determinants. | Real JM105 tables on Euler. |
| `human-metazoan-conservation/scripts/run_hgps_metazoan_conservation.py` | canonical lineage; exact v2 byte import pending | GEO/SRA metadata, GENCODE references, representative transcripts, and aggregate contrasts. | Real public RNA-seq. |
| `human-metazoan-conservation/scripts/run_hgps_metazoan_conservation_manifest_hotfix.py` | canonical metadata layer | Evidence-backed replicate counts, BioProject fallback, and replicate-suffixed control classification. | Real public metadata. |
| `human-metazoan-conservation/scripts/jm105_metazoan_distributed.py` | exact source verified locally; GitHub byte import pending | Multi-node stages and one-pass fragment-level EI/IE/EE_total quantification. | Real public RNA-seq. |
| `human-metazoan-conservation/slurm/*.sbatch` | canonical Euler launchers | Parallel references, 34-task sample array, and dependent aggregation. | Administrative/analysis code. |
| `human-metazoan-conservation/submit-distributed.sh` | canonical orchestrator | Freezes the manifest and submits the dependency graph. | Administrative helper. |
| `human-metazoan-conservation/upload-submit-distributed.ps1` | canonical Windows helper | Uploads and submits the full distributed source. | Administrative helper. |
| `human-metazoan-conservation/repair-failed-array.sh` | canonical repair | Reruns only failed tasks after the micromamba lock incident. | No biological values changed. |
| `human-metazoan-conservation/upload-repair-failed-array.ps1` | canonical Windows repair helper | Uploads the lock-free launchers and starts the selective repair. | Administrative helper. |
| `human-metazoan-conservation/watch-distributed.sh` | canonical status helper | Reports references, array completion, aggregation, and gate report. | Read-only status. |
| `human-metazoan-conservation/MATERIALS_AND_METHODS.md` | canonical methods | Panel-by-panel Figure 5 methods and exact EI/IE/EE counting rules. | Documentation grounded in executed code. |

Raw FASTQ/SRA, BAM/BAI, STAR indexes, logs, cache, scratch, archives and unreviewed
generated biological results are excluded from GitHub.

## Human/metazoan primary metric

```text
JM105_IR = (EI + IE) / ((EI + IE) + 2 * EE_total)
```

The primary metric has no pseudocount; zero denominator is `NA`. PEI with a 0.5
continuity correction is secondary only. Public mammalian data cannot compute
`NMD_hidden` without matched UPF1/NMD-on and NMD-off conditions.

## Provenance

The initial distributed sample array completed 31/34 tasks. Tasks 1, 5 and 33
failed before biological work because concurrent `micromamba run` calls contended
for one home-directory process lock. The selective lock-free repair and exact
source are recorded under `human-metazoan-conservation/runtime-notes/`.

## Backfilled scientific/context documents

- `docs/what-data-shows-summary.md`
- `docs/legacy-code-backfill.md`

Historical descriptions and filenames are recovery clues, not substitutes for
exact complete source.

## Exact-source import status — 2026-07-21

The complete v2 source bundle was syntax-validated locally and its SHA-256 manifest is preserved. All methods, provenance, manifests, repair code and small execution helpers are present on draft PR #6. The two large Python files remain explicitly `PARTIAL / EXACT SOURCE VERIFIED LOCALLY` until connector-safe byte-for-byte import is completed; this status must not be upgraded based on descriptions or snippets.
