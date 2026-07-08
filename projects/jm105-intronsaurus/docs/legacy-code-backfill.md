# JM105 / Intronsaurus Legacy Code Backfill

This file tracks historical JM105 / JM101 / Intronsaurus code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue.

## Imported canonical code

| Canonical path | Original source clue / context | Purpose | Status |
|---|---|---|---|
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | JM105 poster/RNA-seq chat; Euler draft `scripts/29_old_cell_leaky_intron_determinants.py`; depends on `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST` | Classifies old-selective NMD-revealed introns and compares cellular module, 5′SS, branchpoint, branchpoint-to-3′SS spacing, 3′SS, and PPT features. | Imported as canonical runnable script. Uses real JM105 tables only; no fake biological data. |
| `intronsaurus-browser/check-intronsaurus-explore-restored-data-fix-v3i-status.sh` | `check_intronsaurus_explore_restored_DATA_fix_v3I_status.sh` from current Intronsaurus vNext3I repair chat | Checks Euler Slurm status/logs for the Explore-tab restoration build. | Imported exact helper source. Administrative only; no biological data modified. |
| `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.sbatch` | `127_intronsaurus_explore_restored_DATA_fix_v3I.sbatch` | Slurm wrapper for vNext3I, which restores the original total/rRNA-depleted Explore graph behavior and adds poly-A views. | Imported exact helper source. Requires the full v3I Python builder and patch-chain dependencies on Euler. |
| `intronsaurus-browser/upload-submit-intronsaurus-explore-restored-data-fix-v3i.ps1` | `upload_submit_intronsaurus_explore_restored_DATA_fix_v3I.ps1` | Uploads vNext3I bundle to Euler and submits the build job. | Imported exact helper source. |
| `intronsaurus-browser/retrieve-intronsaurus-explore-restored-data-fix-v3i.ps1` | `retrieve_intronsaurus_explore_restored_DATA_fix_v3I.ps1` | Retrieves and opens the completed vNext3I archive from Euler. | Imported exact helper source. |
| `intronsaurus-browser/run-integrate-sun-matched-rna-protein-gene-stories.sbatch` | vNext3Y bundle `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.sbatch` | Slurm wrapper for the single-entry Gene Stories build that groups JM105 RNA/rRNA-depleted data with Sun et al. 2021 protein abundance by comparison. | Imported exact helper source. Requires the vNext3Y Python builder source and input archive/workbook on Euler. |
| `intronsaurus-browser/upload-submit-intronsaurus-matched-rna-protein-gene-stories.ps1` | vNext3Y bundle upload helper | Uploads vNext3Y builder/source archive/Sun workbook to Euler and submits the job. | Imported exact helper source. |
| `intronsaurus-browser/retrieve-intronsaurus-matched-rna-protein-gene-stories.ps1` | vNext3Y bundle retrieval helper | Retrieves vNext3Y HTML, validation JSON, Sun tables, and archive from Euler. | Imported exact helper source. |
| `intronsaurus-browser/check-intronsaurus-matched-rna-protein-gene-stories.sh` | vNext3Y bundle status checker | Uses timeout-wrapped `squeue`/`sacct` plus stdout/stderr tails to check the vNext3Y Slurm job. | Imported exact helper source. |
| `intronsaurus-browser/patches/vnext3ah-fix28-gene-story-sources-patch.html` | Current-session standalone artifact `/mnt/data/intronsaurus_fix28_gene_story_sources/Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html`; source marker `fix28: Gene stories duplicate-row labels + provenance note` | Late browser patch layer that collapses duplicate Gene Stories evidence labels and adds a provenance drawer for stored RNA/protein values and log2 ratio calculations. | Imported exact CSS/JavaScript patch layer. UI/provenance only; does not create biological values. |

## Recovered exact code staged outside `main`

| Path / branch | Original source clue / context | Purpose | Status |
|---|---|---|---|
| PR #1 branch `legacy-code-backfill-2026-07-08`: `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py` | JM-133 project: “Do weak 5′ splice sites need Mud1?”; source clue `/cluster/scratch/jmccarthy/JM105_RNAseq/scripts/71_JM133_weak_5SS_need_Mud1.py` | Tests whether Mud1-dependent retained/unspliced introns in an NMD-off background have weaker predicted 5′SS:U1 pairing. Writes real-data tables, statistics, transparent/white-preview figures, and hard checks. | Exact full source is recovered in GitHub PR #1 but not on `main`; PR is open and connector-visible as non-mergeable. Do not duplicate or reconstruct unless manually rebasing/importing from the PR branch. |
| PR #1 branch `legacy-code-backfill-2026-07-08`: `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch` | JM-133 Euler launcher for job `JM133_5SS_Mud1` | Slurm wrapper for the JM-133 weak-5SS/Mud1 analysis. | Exact full source is recovered in PR #1 but not on `main`. |

## Search/backfill results from this pass

| Source searched | What was found | Action |
|---|---|---|
| GitHub repo `jorddyk/Jordan-McCarthy` | Repo exists, is private, and authenticated user has admin/push access. Existing project docs and Intronsaurus browser README were present. | Added vNext3Y operational helpers and updated Intronsaurus browser/JM105 docs; this continuation added the fix28 Gene Stories source/provenance patch. |
| Active project sandbox | Found exact current vNext3Y bundle `Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle`, including the large Python builder, sbatch, PowerShell upload/retrieve helpers, and safe status checker. Also found current standalone Intronsaurus fix28 artifact in `/mnt/data/intronsaurus_fix28_gene_story_sources/`. | Imported helper scripts earlier and imported the exact small fix28 Gene Stories patch layer now. Did not commit binary workbook, tar archives, generated HTML, raw data, or rejected/unstable UI experiments. |
| Personal/project context search | Confirmed vNext3Y supersedes v3P-v3X for Sun proteomics integration: single-entry Gene Stories, no right-side panel, comparison-matched JM105 RNA/rRNA-depleted and Sun protein-abundance groups, common-name mapping, RNA/protein label distinction. Current context also identified fix28 as a Gene Stories duplicate-label/source-provenance patch. | Marked vNext3Y as canonical target and intermediate v3P-v3X attempts as deliberately not committed. Imported only the exact fix28 Gene Stories patch, not the full generated HTML. |
| Personal/project context search, current continuation | Confirmed PR #1 contains exact JM-133 weak-5SS/Mud1 Python and sbatch code, while Figure 5 renderer, ImageJ/Fiji macros, language-learning HTML apps, and some JM134 scripts remain exact-source recovery targets. | Recorded PR #1 as recovered exact code staged outside `main`; did not recreate partial source. |
| Google Drive search | Searches for `Intronsaurus vNext3Y` and `Intronsaurus` returned no direct Drive code artifacts in this pass. | No Drive files committed. |
| Google Drive search, current continuation | Search for `MitoSOX macro` and `Step1_DetectAdjustConvertResize` found the lab notebook source clue document with JM-076 macro paths, but not the macro bodies. Searches for `kartoffel_vocabulary_active_recall_WORKING` and `german-drill-6` did not recover complete HTML app source. | Kept these as source-recovery targets only; no invented `.ijm`, Groovy, or HTML code committed. |
| File Search | Found uploaded Figure 5/Nature Aging prompt/spec texts and Fig1/Fig4 panel-description documents; no new complete runnable code beyond already imported prompt/spec artifacts. | No new figure-rendering code committed from these results; source clues remain in Figure rendering docs. |

## Highest-priority code to recover

| Priority | Proposed canonical path | Historical name / source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `intronsaurus-browser/integrate-sun-matched-rna-protein-gene-stories.py` | `141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py` in `/mnt/data/Intronsaurus_MatchedRNAProteinGeneStories_vNext3Y_code_bundle/` | Current canonical Intronsaurus Gene Stories builder: starts from precise v3M base; removes right-side gene panel; groups aging, old-cell CR, young-cell CR, and JM105 regulatory evidence; maps Sun ORF IDs to common names; distinguishes JM105 RNA/host abundance from Sun protein abundance. | Exact full source recovered in active sandbox but large text-source import remains pending; do not reconstruct from summary. |
| 2 | `analysis/jm101-jm105-integrate-intronsaurus.py` | `110_JM101_JM105_integrate_intronsaurus.py` | Integrate JM101/JM105 data into Intronsaurus; known context included remote project `/cluster/scratch/jmccarthy/JM105_RNAseq`, metadata `Y:\Jordan\JM101\metadata_filtered.csv`, BAM folder `Y:\Jordan\JM101\RSUBREAD_bam`, and job `3574398` | Exact full source recovered in active sandbox but not yet committed in this pass |
| 3 | `alignment/jm101-star-align-array.sbatch` | `113_JM101_STAR_align_array_LOAD_STACK.sbatch` | STAR alignment array job for JM101/JM105 rebuild path using Euler `stack/2024-06`, `gcc/12.2.0`, `star/2.7.10b`, and `samtools/1.17` | Exact full source recovered in active sandbox but not yet committed in this pass |
| 4 | `analysis/jm101-integrate-after-star-load-stack.sbatch` | `114_JM101_integrate_after_STAR_LOAD_STACK.sbatch` | Post-STAR integration step for Intronsaurus after verified BAM creation | Exact full source recovered in active sandbox but not yet committed in this pass |
| 5 | `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.py` | `127_intronsaurus_explore_restored_DATA_fix_v3I.py` | Current Explore-tab repair: reads lexical `DATA.explorePanels`, restores total/rRNA-depleted graphs, adds poly-A graph view, preserves other tabs. | Exact full source recovered in active sandbox; import still pending because it is a large patch-chain builder with legacy dependencies |
| 6 | `reader/intronsaurus-reader-first-rna-fate-vnext3/` | `Intronsaurus_Reader_First_RNA_Fate_vNext3.html` | Interactive reader with Overview front door, Gene Stories tab, Explore poly-A/total slope graph, rebuilt retained-RNA burden, common-gene mapping, capture tooltips, observer disabler, Mud1 pill fix | Exact full HTML/source bundle not yet recovered |
| 7 | `analysis/jm101-rsubread-step2-reclassify-hard-resume.R` | STEP 2 `RECLASSIFY + HARD-RESUME` R script from 2025-08-15 | Rsubread alignment/counting workflow with `base_dir <- "Y:/Jordan/JM101/RNA seq GC files"`, `RSUBREAD_bam`, `sample_sheet.step1.csv`, outputs `gene_counts_matrix.tsv`, `gene_annotation.tsv`, `sample_metadata.tsv` | Exact full source not yet recovered |
| 8 | `analysis/jm101-rsubread-step2-throughput-turbo.R` | STEP 2 `THROUGHPUT TURBO` R script from 2025-08-15 | Rsubread throughput/SSD staging workflow | Exact full source not yet recovered |
| 9 | `analysis/jm101-deseq2-step3.R` | Step 3 DESeq2 script from 2025-08-15 | Differential expression analysis from Rsubread counts/annotations | Exact full source not yet recovered |
| 10 | `analysis/jm101-irfinder-draft-workflow.R` | Draft R/WSL IRFinder workflow from 2025-08-11 | IRFinder/DESeq2 intron-retention draft using `metadata_filtered.csv` and `Y:/Jordan/JM101/RNA seq GC files` | Exact full source not yet recovered |
| 11 | `analysis/jm105-paired-gene-body-normalized-leakage-test.py` | Euler script `scripts/26_paired_gene_body_normalized_leakage_test.py`; output `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST` | Tests old-vs-young NMD-revealed leakage with retention fraction and paired-fragment gene-body-normalized boundary reads. | Full current source was visible in project chat but not imported in this pass; next target. |
| 12 | `figures/jm105-synopsis-aligned-all-intron-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Renders normal all-intron/all-gene RNA-seq plots required by the synopsis, including 2×2 NMD-detector scatter panels and volcano audits. | Full current source was visible in project chat but not imported in this pass; next target. |
| 13 | `jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.py` | PR #1 copy of `analysis/jm133-weak-5ss-need-mud1.py` / Euler clue `scripts/71_JM133_weak_5SS_need_Mud1.py` | Canonical project-folder copy of JM-133 once PR #1 is rebased or manually reconciled. | Exact source recovered in PR #1; not yet copied to `main` project folder. |
| 14 | `intronsaurus-browser/patches/vnext3ah-current-gene-story-source-provenance.patch.html` or integrated builder source | `Intronsaurus_Explore_Restored_vNext3AH_fix28_gene_story_sources.html` and `fix28: Gene stories duplicate-row labels + provenance note` | Preserve the Gene Stories source/provenance behavior in the proper Intronsaurus builder rather than as a late standalone patch. | Small exact patch imported as `patches/vnext3ah-fix28-gene-story-sources-patch.html`; full generated HTML not committed. Next step is to fold this behavior into the canonical builder once the builder source is imported. |

## File Library source clues captured

- `JM101_RNAseq_Protocol_and_Provenance.docx` documents JM101 QuasR intron/exon counting, `IRratio = (intron + 1)/(exon + 1)`, `IRfraction`, volcano outputs, Rsubread/featureCounts expression workflow, CPM, and historical troubleshooting.
- `JM105_ProjectDescription.docx` documents JM105 as total RNA-seq on MAD-isolated young/aged cells with Mud1/NMD/CR perturbations to quantify spliced vs unspliced ratios genome-wide.
- Several uploaded prompt text files document figure-rendering invariants, PowerShell/Euler job expectations, fixed canvas exports, lane maps, collision inventories, and `NO DATA` placeholder rules.
- Current-session Intronsaurus standalone website artifacts from fix11–fix28 are generated outputs, not canonical builders. The only imported source from this chain in this pass is the exact fix28 Gene Stories duplicate-label/provenance patch layer.

## Current project constraints to preserve during import

- JM105 / Intronsaurus is an active project.
- Figure 2 should remain total/rRNA-depleted only unless Jordan explicitly reverses this.
- Poly-A data should not be used or shown for Figure 2 unless explicitly restored.
- Experiments not yet done must be marked `NO DATA`.
- Do not fake biological data.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.
- Do not call caloric restriction starvation.

## Backfill method

1. Search old ChatGPT/project context by exact file name first.
2. Search File Library and Google Drive by exact file name and key strings.
3. Search local/source artifact names if surfaced in conversation.
4. If full exact code is recovered, commit it under the proposed canonical path or a better human path.
5. If only a summary is recovered, keep it here and do not pretend it is the source code.
