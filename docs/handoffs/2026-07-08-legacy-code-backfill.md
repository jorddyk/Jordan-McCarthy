# 2026-07-08 legacy code backfill handoff

## Repo

`jorddyk/Jordan-McCarthy`

Verified status:

- Private repository.
- Default branch: `main`.
- Connector has admin/maintain/push permissions.

## Project area

Primary area touched:

```text
projects/jm105-intronsaurus/
```

Documentation areas touched:

```text
docs/legacy-code-backfill.md
docs/wiki/Jordan-McCarthy-Code-Wiki.md
docs/handoffs/
```

## Human purpose

Begin the one-time legacy source-code rescue into the private GitHub repo. The repo is project-organized rather than chronological. Daily handoffs remain audit logs only.

## Files created or updated

Created:

```text
docs/legacy-code-backfill.md
projects/jm105-intronsaurus/transformation-protocol-rnaseq/README.md
projects/jm105-intronsaurus/transformation-protocol-rnaseq/resolve-fastq-files.py
projects/jm105-intronsaurus/transformation-protocol-rnaseq/transformation-protocol-samples.tsv
projects/jm105-intronsaurus/transformation-protocol-rnaseq/run-transformation-expression.sbatch
projects/jm105-intronsaurus/transformation-protocol-rnaseq/check-transformation-job.ps1
projects/jm105-intronsaurus/jm134-starvation-switch/README.md
docs/handoffs/2026-07-08-legacy-code-backfill.md
```

Updated:

```text
docs/wiki/Jordan-McCarthy-Code-Wiki.md
projects/jm105-intronsaurus/README.md
```

## Files deliberately not committed

The following were intentionally not committed in this first pass:

- Binary/generated Excel template and output workbooks.
- PNG/PDF/SVG figure renders.
- Generated tarballs.
- Slurm stdout/stderr logs.
- Raw FASTQ/BAM/BAI or other sequencing files.
- Raw microscopy images/stacks.
- Incomplete/truncated source clues.
- JM134 large scripts that are exact but still need complete source-preserving import without truncation.

## Scientific/data status

No fake biological data was generated. Imported code/config is from the real JM105 transformation-protocol workflow. JM134 documentation reflects real beta-binomial significance-recovery results from the project history, but the full canonical JM134 runnable scripts are not yet imported.

## Implementation notes

- `resolve-fastq-files.py` was imported as exact recovered source with an added provenance/purpose header.
- The transformation sample manifest was imported as small real metadata, not raw sequencing data.
- The Slurm and PowerShell helper imports preserve the Euler/Windows workflow context.
- `docs/legacy-code-backfill.md` records exact source clues for unrecovered code rather than reconstructing missing code from summaries.

## Final code paths

```text
projects/jm105-intronsaurus/transformation-protocol-rnaseq/resolve-fastq-files.py
projects/jm105-intronsaurus/transformation-protocol-rnaseq/transformation-protocol-samples.tsv
projects/jm105-intronsaurus/transformation-protocol-rnaseq/run-transformation-expression.sbatch
projects/jm105-intronsaurus/transformation-protocol-rnaseq/check-transformation-job.ps1
```

## Legacy-backfill progress

Imported exact source/config for the first slice of the JM105 transformation-protocol pipeline.

Tracked unrecovered targets include:

```text
JM105_build_relative_abundance_excel.py
JM105_run_transformation_expression.sh
01_JM105_Upload_And_Submit.ps1
02_JM105_Download_Results.ps1
JM134_matched_splicing_index.py
79_JM134_audit_and_beta_binomial.py
80_JM134_apply_beta_binomial_and_rerender.py
83_JM134_final_guide_repair.py
71_JM133_weak_5SS_need_Mud1.py
Figure2 stage-1 audit script
Intronsaurus vNext3AH fix10 browser bundle
ImageJ/Fiji/Groovy aging-chip macros
German/TELC HTML apps
Personal intelligence agency prompts/rubrics
```

## Remaining source-recovery targets

Next highest-value import is the rest of the exact `JM105_Transformation_Protocol_Pipeline` text source, followed by the JM134 matched-SI/beta-binomial scripts. Do not import generated figure renders or Excel binaries unless a later task explicitly asks for them.
