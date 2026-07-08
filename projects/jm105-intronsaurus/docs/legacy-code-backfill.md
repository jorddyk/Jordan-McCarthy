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

## Search/backfill results from this pass

| Source searched | What was found | Action |
|---|---|---|
| GitHub repo `jorddyk/Jordan-McCarthy` | Repo exists, is private, and authenticated user has admin/push access. Existing project docs and Intronsaurus browser README were present. | Added vNext3I helper scripts and updated Intronsaurus browser docs. |
| Active project sandbox | Found exact current vNext3I bundle helpers and the large Python builder `127_intronsaurus_explore_restored_DATA_fix_v3I.py`. | Imported helper scripts; documented full Python builder as recovered but still needing text-source import if this older v3I path is needed again. |
| File Library / project conversation context | Existing recovery notes identify many historical JM101/JM105 scripts and figure prompts; this pass focused on the active Intronsaurus Explore-tab repair sequence. | Did not invent missing code; unrecovered targets remain listed below. |

## Highest-priority code to recover

| Priority | Proposed canonical path | Historical name / source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `analysis/jm101-jm105-integrate-intronsaurus.py` | `110_JM101_JM105_integrate_intronsaurus.py` | Integrate JM101/JM105 data into Intronsaurus; known context included remote project `/cluster/scratch/jmccarthy/JM105_RNAseq`, metadata `Y:\Jordan\JM101\metadata_filtered.csv`, BAM folder `Y:\Jordan\JM101\RSUBREAD_bam`, and job `3574398` | Exact full source recovered in active sandbox but not yet committed in this pass |
| 2 | `alignment/jm101-star-align-array.sbatch` | `113_JM101_STAR_align_array_LOAD_STACK.sbatch` | STAR alignment array job for JM101/JM105 rebuild path using Euler `stack/2024-06`, `gcc/12.2.0`, `star/2.7.10b`, and `samtools/1.17` | Exact full source recovered in active sandbox but not yet committed in this pass |
| 3 | `analysis/jm101-integrate-after-star-load-stack.sbatch` | `114_JM101_integrate_after_STAR_LOAD_STACK.sbatch` | Post-STAR integration step for Intronsaurus after verified BAM creation | Exact full source recovered in active sandbox but not yet committed in this pass |
| 4 | `intronsaurus-browser/intronsaurus-explore-restored-data-fix-v3i.py` | `127_intronsaurus_explore_restored_DATA_fix_v3I.py` | Current Explore-tab repair: reads lexical `DATA.explorePanels`, restores total/rRNA-depleted graphs, adds poly-A graph view, preserves other tabs. | Exact full source recovered in active sandbox; import still pending because it is a large patch-chain builder with legacy dependencies |
| 5 | `reader/intronsaurus-reader-first-rna-fate-vnext3/` | `Intronsaurus_Reader_First_RNA_Fate_vNext3.html` | Interactive reader with Overview front door, Gene Stories tab, Explore poly-A/total slope graph, rebuilt retained-RNA burden, common-gene mapping, capture tooltips, observer disabler, Mud1 pill fix | Exact full HTML/source bundle not yet recovered |
| 6 | `reader/intronsaurus-mrna-like-premrna-v3ae/` | `Intronsaurus_mRNA_Like_Pre_mRNAs_vNext3AE_code_bundle.zip`, `retrieve_intronsaurus_mrna_like_premrna_model_v3AE.ps1` | vNext3AE mRNA-like pre-mRNA model; expected restored Explore HTML; known checks include `SCATTER_POINT_COUNT=402`, `CANDIDATE_TABLE_ROWCOUNT=40`, `JOIN_KEY_IS_INTRON_ID_EVERYWHERE=True` | Exact full bundle not yet recovered |
| 7 | `analysis/jm101-rsubread-step2-reclassify-hard-resume.R` | STEP 2 `RECLASSIFY + HARD-RESUME` R script from 2025-08-15 | Rsubread alignment/counting workflow with `base_dir <- "Y:/Jordan/JM101/RNA seq GC files"`, `RSUBREAD_bam`, `sample_sheet.step1.csv`, outputs `gene_counts_matrix.tsv`, `gene_annotation.tsv`, `sample_metadata.tsv` | Exact full source not yet recovered |
| 8 | `analysis/jm101-rsubread-step2-throughput-turbo.R` | STEP 2 `THROUGHPUT TURBO` R script from 2025-08-15 | Rsubread throughput/SSD staging workflow | Exact full source not yet recovered |
| 9 | `analysis/jm101-deseq2-step3.R` | Step 3 DESeq2 script from 2025-08-15 | Differential expression analysis from Rsubread counts/annotations | Exact full source not yet recovered |
| 10 | `analysis/jm101-irfinder-draft-workflow.R` | Draft R/WSL IRFinder workflow from 2025-08-11 | IRFinder/DESeq2 intron-retention draft using `metadata_filtered.csv` and `Y:/Jordan/JM101/RNA seq GC files` | Exact full source not yet recovered |
| 11 | `analysis/jm105-paired-gene-body-normalized-leakage-test.py` | Euler script `scripts/26_paired_gene_body_normalized_leakage_test.py`; output `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST` | Tests old-vs-young NMD-revealed leakage with retention fraction and paired-fragment gene-body-normalized boundary reads. | Full current source was visible in project chat but not imported in this pass; next target. |
| 12 | `figures/jm105-synopsis-aligned-all-intron-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Renders normal all-intron/all-gene RNA-seq plots required by the synopsis, including 2×2 NMD-detector scatter panels and volcano audits. | Full current source was visible in project chat but not imported in this pass; next target. |

## File Library source clues captured

- `JM101_RNAseq_Protocol_and_Provenance.docx` documents JM101 QuasR intron/exon counting, `IRratio = (intron + 1)/(exon + 1)`, `IRfraction`, volcano outputs, Rsubread/featureCounts expression workflow, CPM, and historical troubleshooting.
- `JM105_ProjectDescription.docx` documents JM105 as total RNA-seq on MAD-isolated young/aged cells with Mud1/NMD/CR perturbations to quantify spliced vs unspliced ratios genome-wide.
- Several uploaded prompt text files document figure-rendering invariants, PowerShell/Euler job expectations, fixed canvas exports, lane maps, collision inventories, and `NO DATA` placeholder rules.

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
