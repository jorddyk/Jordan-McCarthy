# JM105 / Intronsaurus Analysis

Human goal: preserve canonical code supporting Jordan's JM105 RNA-seq, intron retention, NMD-hidden leakage, Mud1/CR, aging, and manuscript figure workflows.

This project is for analysis code and reusable figure-generation/browser code, not raw sequencing data.

## Intended structure

```text
projects/jm105-intronsaurus/
  analysis/
    RNA-seq and intron-retention analysis scripts.
  alignment/
    STAR and other alignment launchers.
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
    Intronsaurus browser/export code and Windows/Euler helpers.
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
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | canonical | Classifies old-selective NMD-revealed introns and compares gene module / splice-site / branchpoint / 3′SS / PPT features against nonleaker comparison introns. | Uses real JM105 tables on Euler; no simulated biological data. |
| `transformation-protocol-rnaseq/resolve-fastq-files.py` | canonical | Resolves FASTQ files for the 12 transformation-protocol samples from sample IDs and aliases. | Real workflow metadata; no fake biological data. |
| `transformation-protocol-rnaseq/transformation-protocol-samples.tsv` | canonical | Sample manifest for JM62-JM73 transformation-protocol subset. | Real sample metadata; no raw reads. |
| `transformation-protocol-rnaseq/run-transformation-expression.sbatch` | canonical | Slurm wrapper for transformation-protocol expression workflow. | Real workflow; no fake biological data. |
| `transformation-protocol-rnaseq/check-transformation-job.ps1` | canonical | Windows helper to inspect Euler Slurm status and logs. | Administrative helper; no biological data modified. |
| `intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | canonical helper | Slurm wrapper for Intronsaurus vNext3Y single-entry Gene Stories with matched JM105 RNA and Sun protein-abundance groups. | Real JM105/Sun workflow; no raw data committed. |
| `intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | canonical helper | Uploads and submits the vNext3Y build to Euler. | Administrative helper; no raw data committed. |
| `intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | canonical helper | Retrieves vNext3Y generated outputs. | Generated HTML/archive remain excluded by default. |
| `intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh` | canonical helper | Safe Euler status checker. | Administrative helper. |
| `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | canonical helper | Runs the vNext3I Explore-tab restoration workflow. | Depends on unrecovered builder/patch-chain source. |
| `intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | canonical helper | Uploads and submits vNext3I. | Administrative helper. |
| `intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | canonical helper | Retrieves vNext3I outputs. | Generated outputs excluded. |
| `intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | canonical helper | Checks vNext3I status/logs. | Administrative helper. |
| `intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | canonical patch | Deduplicates Gene Stories evidence labels and adds source/provenance notes. | UI/provenance only; no biological values generated. |

## Backfilled scientific/context documents

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `docs/what-data-shows-summary.md` | canonical context | Current interpretation guardrail for CR/Mud1/NMD-hidden leakage, intron architecture, Mud1-GFP, RP/non-RP stratification, and Parenteau comparison logic. | Documentation only. |
| `docs/legacy-code-backfill.md` | active recovery queue | Tracks exact historical filenames, paths, outputs, source clues, and whether full source has actually been recovered. | Documentation only; never treat as code. |

## Verified external recovery clue added 2026-07-11

File Library contains `JM101_RNAseq_Protocol_and_Provenance.docx`. It verifies the historical JM101 workflow structure and output names, including:

- Windows project root `Y:/Jordan/JM101`.
- QuasR-compatible BAMs under `C:/rna_seq/quasr_bam`.
- `metadata_clean.csv`, `yeast_introns_sacCer3.rds`, and `SGD_features.tab` as historical inputs.
- QuasR intron/exon counting, DESeq2 exon-derived size factors, `IRratio = (intron + 1)/(exon + 1)`, and intron fraction outputs.
- Rsubread/featureCounts gene-level counting, CPM, interaction/ratio-of-ratios checks, and output folders under `ir_outputs/` and `expression_outputs/`.

This document is a provenance source, not the exact R/Python/Bash source. No script was reconstructed from it.

## Verified external recovery clue added 2026-07-29

Google Drive folder `06 Current Figure Rendering Code` contains a register document, "CURRENT — JM105 Figure 2 v10 lane-locked renderer register," describing `JM105_figure2_render_v10_lane_locked_20260728.py` (supersedes `JM105_figure2_render_v9_FINAL_20260728.py`; SHA-256 `fbd47169d0320e04c0eaf41692b9500be4b1cfa8f862e089b891507c497bd00e`). The register documents six scientific corrections (retained-junction framing, `effective_fragments` denominator labeling, NMD-compression wording, length-sensitivity diagnostics, independent host-gene-body log2FC, and nuclear mRNA/ORF-set wording) and a fixed inch-based lane layout that fails closed on clipping/collision.

This is a provenance/register document, not the exact Python source. No `.py` file object was found elsewhere in Drive. See `docs/legacy-code-backfill.md` for the full recorded clue and next recovery action.

## Canonical code still targeted for recovery

See `docs/legacy-code-backfill.md` for exact historical filenames and source clues. Highest-priority unrecovered targets remain:

1. `110_JM101_JM105_integrate_intronsaurus.py`.
2. `111_JM101_STAR_align_array.sbatch` / later load-stack STAR variant.
3. `112_JM101_integrate_after_STAR.sbatch` / later load-stack integration variant.
4. Rsubread Step 2 hard-resume/turbo scripts, Step 3 DESeq2, and IRFinder drafts.
5. Full Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y builders/readers.
6. JM133/JM134 and Figure 2 candidate-gate source.

`Exact full source not yet recovered` means exactly that. Historical claims that a source existed in a prior ephemeral sandbox are not sufficient for canonical import unless the source body is accessible and reverified in the current run.