# JM105 / Intronsaurus Analysis

Human goal: preserve canonical code supporting Jordan's JM105 RNA-seq, intron retention, NMD-hidden leakage, Mud1/CR, aging, and manuscript figure workflows.

This project is for analysis code and reusable figure-generation code, not raw sequencing data.

## Intended structure

```text
projects/jm105-intronsaurus/
  analysis/
    RNA-seq and intron-retention analysis scripts.
  figures/
    Scripts that generate manuscript figure panels from real inputs.
  transformation-protocol-rnaseq/
    12-sample transformation-protocol RNA-seq abundance workflow.
  jm134-starvation-switch/
    JM-134 comparison with Parenteau/gkaf525 stationary-phase starvation.
  jm133-weak-5ss-mud1/
    JM-133 weak 5′SS/U1-complementarity vs Mud1-dependence analysis.
  figure2-candidate-gate/
    Total/rRNA-depleted Figure 2 candidate-gate analysis.
  intronsaurus-browser/
    Intronsaurus browser/export code.
  metadata/
    Small, human-readable sample maps or schema documents only. No raw sequencing files.
  docs/
    Recovery notes, scientific interpretation guardrails, and legacy-source audit trails.
  README.md
```

## Current scientific guardrails

- Never generate fake biological data.
- Use `NO DATA` for experiments or panels that have not been performed.
- Figure 2 should use total/rRNA-depleted data only unless Jordan explicitly changes this.
- Do not show poly-A data in Figure 2 unless Jordan explicitly restores it.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.
- Avoid claiming caloric restriction is starvation.

## Canonical code imported

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | imported before this pass | Classifies old-selective NMD-revealed introns and compares gene module / splice-site / branchpoint / 3′SS / PPT features against nonleaker comparison introns. | Uses real JM105 tables on Euler; no simulated biological data. |
| `transformation-protocol-rnaseq/resolve-fastq-files.py` | imported in legacy backfill | Resolves FASTQ files for the 12 transformation-protocol samples from sample IDs and aliases. | Real workflow metadata; no fake biological data. |
| `transformation-protocol-rnaseq/transformation-protocol-samples.tsv` | imported in legacy backfill | Sample manifest for JM62-JM73 transformation-protocol subset. | Real sample metadata; no raw reads. |
| `transformation-protocol-rnaseq/run-transformation-expression.sbatch` | imported in legacy backfill | Slurm wrapper for transformation-protocol expression workflow. | Real workflow; no fake biological data. |
| `transformation-protocol-rnaseq/check-transformation-job.ps1` | imported in legacy backfill | Windows helper to inspect Euler Slurm status and logs. | Administrative helper; no biological data modified. |

## Backfilled scientific/context documents

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `docs/what-data-shows-summary.md` | imported exact user-provided summary | Preserves current interpretation of CR/Mud1/NMD-hidden leakage, intron architecture, Mud1-GFP, RP/non-RP stratification, and Parenteau comparison guardrails. | Scientific interpretation summary only; no raw biological data. |

## Canonical code still targeted for recovery

See `docs/legacy-code-backfill.md` for exact historical filenames and source clues. Highest-priority unrecovered targets include the remaining JM105 transformation-protocol builder/downloader scripts, JM134 beta-binomial scripts, JM133 weak-5SS analysis, Figure 2 candidate-gate scripts, JM101/JM105 Intronsaurus integration scripts, STAR/sbatch jobs, Rsubread step 2/3 scripts, IRFinder drafts, and Intronsaurus reader bundles.
