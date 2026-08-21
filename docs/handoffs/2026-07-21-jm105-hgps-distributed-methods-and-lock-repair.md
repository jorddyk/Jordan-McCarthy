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

The complete exact distributed workflow is canonicalized in draft PR #6. The two large Python sources were reconstructed from checksum-gated source chunks, verified against their recorded SHA-256 values, compiled successfully, and committed; the temporary importer removed itself in the same commit.

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
