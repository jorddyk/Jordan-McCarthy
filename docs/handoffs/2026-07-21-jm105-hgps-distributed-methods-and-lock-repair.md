# Code handoff — JM105 HGPS/metazoan distributed workflow and methods

## Source searched

- exact extracted distributed bundle used for the Euler run;
- Euler accounting and stderr pasted by Jordan;
- current draft PR #6;
- canonical JM105 project README;
- live Google Drive paper structure.

## Exact code recovered and canonicalization status

The exact complete distributed workflow was verified from the extracted source bundle under:

```text
projects/jm105-intronsaurus/human-metazoan-conservation/
```

The methods, manifest, runtime provenance, repair workflow, and all small launchers/helpers are canonicalized in draft PR #6. The two large Python sources (`scripts/run_hgps_metazoan_conservation.py` and `scripts/jm105_metazoan_distributed.py`) are verified locally with recorded SHA-256 values, but byte-for-byte connector import remains pending; the branch retains the prior canonical core lineage until the exact v2 bytes are imported. No claim of complete GitHub canonicalization is made before that import.

## Failure and repair provenance

Original array `7873466` completed 31/34 tasks. Tasks 1, 5 and 33 failed before
read download or analysis because concurrent `micromamba run` processes
contended for `~/.cache/mamba/proc`. Aggregate `7873467` was cancelled by its
dependency. The canonical repair invokes the existing environment Python
directly and reruns only the missing tasks.

## Scientific contracts preserved

- Figure 2 total/rRNA-depleted scope fence.
- `NMD_hidden = IR(upf1Δ) - IR(UPF1+)`.
- `candidate_score = min(aging_effect, CR_suppression)`.
- data-derived Panel F y-limits.
- exact primary mammalian metric:
  `JM105_IR = (EI + IE) / ((EI + IE) + 2 * EE_total)`.
- no primary pseudocount; zero denominator is NA.
- PEI(+0.5) is secondary only.
- mammalian whole-cell RNA-seq is not labelled NMD-hidden leakage.

## Exclusions

No FASTQ/SRA, BAM/BAI, STAR index, log, cache, scratch folder, archive,
credential, or unreviewed generated biological result is committed.
