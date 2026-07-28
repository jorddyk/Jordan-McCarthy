# JM105 / Intronsaurus Legacy Code Backfill

This is the recovery queue for historical JM105, JM101, Intronsaurus, JM133, JM134, and related RNA-seq code. It is documentation, not code.

## Recovery rule

A file is canonical only when its complete source body is accessible and verified. A summary, provenance document, filename, job ID, output list, or recollection that a source once existed is only a recovery clue.

## Imported canonical code

| Canonical path | Purpose | Status |
|---|---|---|
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | Tests old-selective NMD-revealed intron determinants and splice architecture. | Complete runnable source imported; real JM105 inputs only. |
| `transformation-protocol-rnaseq/resolve-fastq-files.py` | Resolves transformation-protocol FASTQs from sample aliases. | Complete runnable source imported. |
| `transformation-protocol-rnaseq/run-transformation-expression.sbatch` | Euler launcher for transformation-protocol expression workflow. | Complete helper imported. |
| `transformation-protocol-rnaseq/check-transformation-job.ps1` | Windows/Euler status helper. | Complete helper imported. |
| `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | Runs the vNext3I Explore restoration build. | Complete helper imported; builder dependency still unrecovered. |
| `intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | Uploads/submits vNext3I. | Complete helper imported. |
| `intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | Retrieves vNext3I outputs. | Complete helper imported. |
| `intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | Checks vNext3I Slurm status/logs. | Complete helper imported. |
| `intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | Runs vNext3Y matched JM105 RNA/Sun protein Gene Stories. | Complete helper imported; Python builder still unrecovered. |
| `intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | Uploads/submits vNext3Y. | Complete helper imported. |
| `intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | Retrieves vNext3Y outputs. | Complete helper imported. |
| `intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh` | Checks vNext3Y status/logs. | Complete helper imported. |
| `intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | Deduplicates Gene Stories labels and adds provenance UI. | Exact patch imported; no biological values generated. |

## Exact code staged outside `main`

PR #1 historically contains complete JM133 weak-5′SS/Mud1 Python and sbatch source on branch `legacy-code-backfill-2026-07-08`. Do not duplicate it from memory. Reconcile or rebase that branch when the exact branch content is accessible and mergeable.

## Current priority queue

| Priority | Proposed canonical path | Historical source clue | Status |
|---|---|---|---|
| 1 | `../figure-rendering/panel-renderers/jm105-figure4-mud1-host-transcript/` | Current 2026-07-28 Jordan authority: `Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response`. | **PARTIAL / AUTHORITY LOCKED; CURRENT RENDERER UNRECOVERED.** Recover current notebook/Drive panel authority, exact raw/source-table renderer, style module, launcher, environment, hashes and successful Euler proof. |
| 2 | `figures/jm105-figure2-measurement-validity/` | Exact same-day Figure 2 renderer objects exist in File Library; Drive register names v10 lane-locked source and warns real-data Euler validation remains pending. | **PARTIAL / EXACT SOURCE LOCATED.** Do not select a canonical winner by filename or snippet; transfer byte-complete source after real-data adjudication. |
| 3 | `metadata/jm105-denominator-source-crosswalk.tsv` and provenance | Current Figure 2 validity work requires exact Novogene clean-read/effective-fragment denominator files and one-to-one JM105 sample crosswalk. | **UNRECOVERED / HIGH PRIORITY.** No denominator values may be invented. |
| 4 | `analysis/jm101-jm105-integrate-intronsaurus.py` | `110_JM101_JM105_integrate_intronsaurus.py`; project `/cluster/scratch/jmccarthy/JM105_RNAseq`; metadata `Y:/Jordan/JM101/metadata_filtered.csv`; BAMs `Y:/Jordan/JM101/RSUBREAD_bam`; historical job `3574398`. | **Exact full source not yet recovered in an accessible source.** A prior ephemeral-sandbox note is not sufficient. |
| 5 | `alignment/jm101-star-align-array.sbatch` | `111_JM101_STAR_align_array.sbatch`; later clue `113_JM101_STAR_align_array_LOAD_STACK.sbatch`; modules `stack/2024-06`, `gcc/12.2.0`, `star/2.7.10b`, `samtools/1.17`. | **Exact full source not yet recovered.** |
| 6 | `analysis/jm101-integrate-after-star.sbatch` | `112_JM101_integrate_after_STAR.sbatch`; later clue `114_JM101_integrate_after_STAR_LOAD_STACK.sbatch`. | **Exact full source not yet recovered.** |
| 7 | `analysis/jm101-rsubread-step2-reclassify-hard-resume.R` | Step 2 `RECLASSIFY + HARD-RESUME`; `base_dir <- "Y:/Jordan/JM101/RNA seq GC files"`; outputs `gene_counts_matrix.tsv`, `gene_annotation.tsv`, `sample_metadata.tsv`. | **Exact full source not yet recovered.** |
| 8 | `analysis/jm101-rsubread-step2-throughput-turbo.R` | Step 2 `THROUGHPUT TURBO`, 2025-08-15. | **Exact full source not yet recovered.** |
| 9 | `analysis/jm101-deseq2-step3.R` | Step 3 DESeq2 from Rsubread counts/annotations. | **Exact full source not yet recovered.** |
| 10 | `analysis/jm101-irfinder-draft-workflow.R` | Draft R/WSL IRFinder workflow; `metadata_filtered.csv`; `Y:/Jordan/JM101/RNA seq GC files`. | **Exact full source not yet recovered.** |
| 11 | `intronsaurus-browser/integrate-sun-matched-rna-protein-gene-stories.py` | `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py`. | **Exact full source not currently accessible.** Imported helpers do not substitute for the builder. |
| 12 | `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.py` | `127_intronsaurus_explore_restored_DATA_fix_v3I.py`. | **Exact full source not currently accessible.** |
| 13 | `reader/intronsaurus-reader-first-rna-fate-vnext3/` | `Intronsaurus_Reader_First_RNA_Fate_vNext3.html`; vNext3AE reader/builder variants. | **Exact complete source bundle not yet recovered.** |
| 14 | `analysis/jm105-paired-gene-body-normalized-leakage-test.py` | `scripts/26_paired_gene_body_normalized_leakage_test.py`; output `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST`. | Full source was previously visible in project context but is not accessible now; do not reconstruct. |
| 15 | `figures/jm105-synopsis-aligned-all-intron-rnaseq-plots.py` | `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS`. | Full source was previously visible in project context but is not accessible now; do not reconstruct. |
| 16 | `jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.py` | PR #1 / `scripts/71_JM133_weak_5SS_need_Mud1.py`. | Exact source reportedly staged in PR #1; not yet canonical on `main`. |
| 17 | `jm134-starvation-switch/` analysis and label-audit scripts | JM134 Euler jobs `3101802`, `3104275`, `3106256`, `3109225`. | Exact full source not yet recovered. |
| 18 | `figure2-candidate-gate/` scripts | Total/rRNA-depleted JM105 Figure 2 candidate-gate workflow. | Exact full source not yet recovered except items explicitly canonical elsewhere. |

## 2026-07-28 Figure 4 authority reset and deprecated lineage

Jordan's later same-day instruction supersedes the CR-selectivity six-panel architecture as current Figure 4. The governing title is now:

```text
Figure 4 | Mud1 couples intron retention and host-transcript abundance in the caloric-restriction response
```

The obsolete v1 package is exact source-located with these verified hashes:

```text
94c389a97e15e6c4e4be3d80c9516591eb5796628c7c00acbdee06d950a657e1  JM105_figure4_cr_selectivity_panels_v1_20260728.py
c32c3d05818455af985331dfd82ec4af251d5c6a4b4e5aad90b85b0aaaf01299  paper_style.py
9f0a9fb2ff1c6718e15f147c60628806bc5a6cc94327aca18fe1a6d7e1695798  JM105_Figure4_CR_selectivity_v1.sbatch
6f9dbeba23ff55037d30dfe7e168f4e1ca3dfe61bb783694b4750aa15a61ecb6  run_JM105_Figure4_CR_selectivity_v1_from_PowerShell.ps1
815ce45ff0109796db279db73a23e945b0986041d82b879307217d0d1bc03103  README_JM105_Figure4_CR_selectivity_v1.md
a6c2501bd5a7439b6aceb6c1c39853b335e66ae335ee51b4aa24587276b50a6f  Figure4_panel_contract.tsv
8e97f37c072d1c6e8a388dcb8dc8d587e9cd56181301d0f81034ca7b69e892a4  Figure4_meeting_grounding.md
```

Do not import this package as current Figure 4 code. v1 job `8886490` failed common-name resolution and then emitted misleading post-failure success text. v2 job `8888031` passed real-GFF label preflight but failed closed on a measured DejaVu Sans Panel D collision between `gate_name_0.1% suppression` and `gate_count_0.1% suppression`. Exact v2 bytes were not exposed. A described v3 geometry patch is not complete source and has no verified full successful run.

Classification:

- v1: `DEPRECATED / EXACT SOURCE LOCATED`;
- v2: `PARTIAL / FAILED SOURCE LOCATED`;
- described v3 patch: `UNRECOVERED / DIAGNOSTIC ONLY`;
- current Mud1/host-transcript Figure 4 renderer: `UNRECOVERED`.

## Verified File Library clues

### `JM101_RNAseq_Protocol_and_Provenance.docx`

This document verifies the historical workflow and output conventions but does not contain the complete canonical scripts.

Verified clues:

- Project root: `Y:/Jordan/JM101`.
- QuasR-compatible BAMs: `C:/rna_seq/quasr_bam`.
- Reference files: `Y:/Jordan/JM101/reference`, `yeast_introns_sacCer3.rds`, `SGD_features.tab`.
- Curated metadata: `Y:/Jordan/JM101/metadata_clean.csv`.
- Historical groups: old/young × WT/upf1Δ with the documented sample IDs.
- QuasR intron and exon counting; exons reduced per gene.
- DESeq2 size factors estimated from exon counts.
- `IRratio = (intron + 1)/(exon + 1)` and intron fraction outputs.
- Output examples: `IRratio_gene_by_sample.csv`, `IRfraction_gene_by_sample.csv`, `IRratio_fraction_long_withNames.csv`, contrast tables, volcano plots.
- Rsubread/featureCounts gene-level counts, CPM, `log2Expr ~ genotype * age`, and explicit ratio-of-ratios cross-check with Pearson correlation approximately 0.999.
- Expression outputs under `Y:/Jordan/JM101/expression_outputs/`, including `UPF1_ratio_of_ratios_EXPRESSION_fromBAM_results.csv` and the associated workbook/volcano/sanity checks.

Action: retain these strings as exact search keys. Do not synthesize the missing R/Python code from the protocol narrative.

### Other source clues

- `JM105_ProjectDescription.docx`: JM105 total RNA-seq from MAD-isolated young/aged cells under Mud1/NMD/CR perturbations.
- Generated Intronsaurus HTML artifacts are outputs, not canonical builders.
- Figure prompt/spec documents are reusable non-runnable contracts only.

## 2026-07-11 search result

File Library searches used exact names for `110`, `111`, `112`, STAR, Rsubread hard-resume/turbo, Step 3 DESeq2, and IRFinder. No complete code body was returned. `JM101_RNAseq_Protocol_and_Provenance.docx` was the only material new source and was recorded as a provenance clue.

## Scientific and repository constraints

- Figure 2 remains total/rRNA-depleted only unless Jordan explicitly reverses this.
- Poly-A data remain excluded from Figure 2.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish intron retention from host-transcript abundance.
- Distinguish RNA/host transcript abundance from protein abundance.
- Do not call caloric restriction starvation.
- Never generate fake biological data.
- Unperformed experiments and unsupported panels remain `NO DATA`.
- Do not commit FASTQ, BAM, SAM, CRAM, BAI, bigWig, archives, generated Intronsaurus sites, SLURM logs, caches, or scratch outputs.

## Backfill method

1. Search exact historical filename.
2. Search exact paths, output names, job IDs, and distinctive code strings.
3. Open promising File Library/Drive artifacts when snippets are incomplete.
4. Import only complete verified source under a human-purpose filename.
5. Record summaries and provenance documents as clues, never as recovered code.
