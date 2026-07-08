# JM105 / Intronsaurus Legacy Code Backfill

This file tracks historical JM105 / JM101 / Intronsaurus code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue.

## Imported canonical code

| Canonical path | Original source clue / context | Purpose | Status |
|---|---|---|---|
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | JM105 poster/RNA-seq chat; Euler draft `scripts/29_old_cell_leaky_intron_determinants.py`; depends on `26_PAIRED_GENE_BODY_NORMALIZED_LEAKAGE_TEST` | Classifies old-selective NMD-revealed introns and compares cellular module, 5′SS, branchpoint, branchpoint-to-3′SS spacing, 3′SS, and PPT features. | Imported as canonical runnable script. Uses real JM105 tables only; no fake biological data. |

## Search/backfill results from this pass

| Source searched | What was found | Action |
|---|---|---|
| GitHub repo `jorddyk/Jordan-McCarthy` | Repo exists, is private, and authenticated user has admin/push access. Existing project docs were already present. | Updated existing docs using SHA; committed imported JM105 determinant script. |
| File Library | Found JM101/JM105 protocol/provenance docs and figure-rendering prompt fragments. JM101 provenance documents contain historical code fragments and output paths but not complete runnable source for most scripts. | Preserved as source clues below; did not reconstruct missing full source. |
| Google Drive keyword searches | Searches for `JM105 script` and `Intronsaurus` returned no direct code artifacts in this pass. | No Drive code committed. |
| Project conversation context | Recent exact JM105 code was visible in the active project chat; older code surfaced mostly as filenames/source clues in memory and docs. | Imported only the determinant script whose complete current source was available. |

## Highest-priority code to recover

| Priority | Proposed canonical path | Historical name / source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `analysis/jm101-jm105-integrate-intronsaurus.py` | `110_JM101_JM105_integrate_intronsaurus.py` | Integrate JM101/JM105 data into Intronsaurus; known context included remote project `/cluster/scratch/jmccarthy/JM105_RNAseq`, metadata `Y:\Jordan\JM101\metadata_filtered.csv`, BAM folder `Y:\Jordan\JM101\RSUBREAD_bam`, and job `3574398` | Exact full source not yet recovered |
| 2 | `alignment/jm101-star-align-array.sbatch` | `111_JM101_STAR_align_array.sbatch` | STAR alignment array job for JM101/JM105 rebuild path | Exact full source not yet recovered |
| 3 | `analysis/jm101-integrate-after-star.sbatch` | `112_JM101_integrate_after_STAR.sbatch` | Post-STAR integration step for Intronsaurus | Exact full source not yet recovered |
| 4 | `scripts/upload-submit-jm101-jm105-intronsaurus.ps1` | `upload_submit_JM...` PowerShell script | Windows-to-Euler upload/submit helper | Exact full source not yet recovered |
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
