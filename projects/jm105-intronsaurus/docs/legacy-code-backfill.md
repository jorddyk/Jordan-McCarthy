# JM105 / Intronsaurus Legacy Code Backfill

This file tracks historical JM105 / JM101 / Intronsaurus code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue.

## Recovered / canonicalized code now in repo

| Canonical path | Historical name / source clue | Purpose | Current status |
|---|---|---|---|
| `analysis/jm133-weak-5ss-need-mud1.py` | Current JM-133 ChatGPT/Euler setup; job clue `JM133_5SS_Mud1`; user question: “Do weak 5′ splice sites need Mud1?” | Test whether Mud1-dependent leaky introns have weak predicted 5′SS:U1 pairing. Produces fixed-canvas SVG/PDF/PNG plus white preview and real-data QC tables. | Canonicalized runnable source committed on branch `legacy-code-backfill-2026-07-08`; not an old hidden file recovered from disk. It was saved from the current complete code conversation. |
| `analysis/jm133-weak-5ss-need-mud1.sbatch` | Euler launch wrapper for JM-133 | Submit the JM133 5′SS analysis on Euler from `/cluster/scratch/jmccarthy/JM105_RNAseq`. | Canonicalized launcher committed on branch `legacy-code-backfill-2026-07-08`. |

## Highest-priority code still to recover

| Priority | Proposed canonical path | Historical name / source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `analysis/jm101-jm105-integrate-intronsaurus.py` | `110_JM101_JM105_integrate_intronsaurus.py` | Integrate JM101/JM105 data into Intronsaurus; known context included remote project `/cluster/scratch/jmccarthy/JM105_RNAseq`, metadata `Y:\Jordan\JM101\metadata_filtered.csv`, BAM folder `Y:\Jordan\JM101\RSUBREAD_bam`, and job `3574398` | Exact full source not yet recovered in this run |
| 2 | `alignment/jm101-star-align-array.sbatch` | `111_JM101_STAR_align_array.sbatch` | STAR alignment array job for JM101/JM105 rebuild path | Exact full source not yet recovered in this run |
| 3 | `analysis/jm101-integrate-after-star.sbatch` | `112_JM101_integrate_after_STAR.sbatch` | Post-STAR integration step for Intronsaurus | Exact full source not yet recovered in this run |
| 4 | `scripts/upload-submit-jm101-jm105-intronsaurus.ps1` | `upload_submit_JM...` PowerShell script | Windows-to-Euler upload/submit helper | Exact full source not yet recovered in this run |
| 5 | `reader/intronsaurus-reader-first-rna-fate-vnext3/` | `Intronsaurus_Reader_First_RNA_Fate_vNext3.html` | Interactive reader with Overview front door, Gene Stories tab, Explore poly-A/total slope graph, rebuilt retained-RNA burden, common-gene mapping, capture tooltips, observer disabler, Mud1 pill fix | Exact full HTML/source bundle not yet recovered in this run |
| 6 | `reader/intronsaurus-mrna-like-premrna-v3ae/` | `Intronsaurus_mRNA_Like_Pre_mRNAs_vNext3AE_code_bundle.zip`, `retrieve_intronsaurus_mrna_like_premrna_model_v3AE.ps1` | vNext3AE mRNA-like pre-mRNA model; expected restored Explore HTML; known checks include `SCATTER_POINT_COUNT=402`, `CANDIDATE_TABLE_ROWCOUNT=40`, `JOIN_KEY_IS_INTRON_ID_EVERYWHERE=True` | Exact full bundle not yet recovered in this run |
| 7 | `analysis/jm101-rsubread-step2-reclassify-hard-resume.R` | STEP 2 `RECLASSIFY + HARD-RESUME` R script from 2025-08-15 | Rsubread alignment/counting workflow with `base_dir <- "Y:/Jordan/JM101/RNA seq GC files"`, `RSUBREAD_bam`, `sample_sheet.step1.csv`, outputs `gene_counts_matrix.tsv`, `gene_annotation.tsv`, `sample_metadata.tsv` | Exact full source not yet recovered in this run |
| 8 | `analysis/jm101-rsubread-step2-throughput-turbo.R` | STEP 2 `THROUGHPUT TURBO` R script from 2025-08-15 | Rsubread throughput/SSD staging workflow | Exact full source not yet recovered in this run |
| 9 | `analysis/jm101-deseq2-step3.R` | Step 3 DESeq2 script from 2025-08-15 | Differential expression analysis from Rsubread counts/annotations | Exact full source not yet recovered in this run |
| 10 | `analysis/jm101-irfinder-draft-workflow.R` | Draft R/WSL IRFinder workflow from 2025-08-11 | IRFinder/DESeq2 intron-retention draft using `metadata_filtered.csv` and `Y:/Jordan/JM101/RNA seq GC files` | Exact full source not yet recovered in this run |
| 11 | `analysis/jm105-figure-2-cr-suppression-audit.py` | Script clues `68_REBUILD_FIG2C_SHARED8_FROM_REAL_DATA_AND_COLLECT_ALL.py`, `69_DISCOVER_FIG2_CANDIDATES_REBUILD_FIG2C_AND_COLLECT.py`, and `70_DIAGNOSE_FIG2C_REAL_SOURCE_FAST.py` | Audit/rebuild Figure 2 candidate-set consistency and CR-suppression source tables. Earlier attempts were diagnostic or failed because the source table shape was not matched. | Do not commit as canonical yet; exact successful source and real source table not yet recovered/proven |
| 12 | `analysis/jm105-poster-final-bundle-collector.py` | Bundle clues `63_POSTER_FINAL_ALL_LATEST_ORIGINAL_JM100_SURVIVAL_FIXED_20260607` and later 68/69 attempts | Collect poster-ready PDFs/PNGs/SVGs and exclude legacy Fig2C. | Exact successful source not recovered; do not commit partial/failing variants |

## Current project constraints to preserve during import

- JM105 / Intronsaurus is an active project.
- Figure 2 should remain total/rRNA-depleted only unless Jordan explicitly reverses this.
- Poly-A data should not be used or shown for Figure 2 unless explicitly restored.
- Experiments not yet done must be marked `NO DATA`.
- Do not fake biological data.
- Distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal.
- Distinguish RNA/host transcript abundance from protein abundance.
- Do not claim caloric restriction is starvation.

## Backfill method

1. Search old ChatGPT/project context by exact file name first.
2. Search File Library and Google Drive by exact file name and key strings.
3. Search local/source artifact names if surfaced in conversation.
4. If full exact code is recovered, commit it under the proposed canonical path or a better human path.
5. If only a summary is recovered, keep it here and do not pretend it is the source code.

## Current run notes — 2026-07-08

- Repo verified as `jorddyk/Jordan-McCarthy`, private, with admin/push permission.
- Exact historical source for the older JM101/JM105 R/Python/PowerShell scripts was not recovered from accessible uploaded/project context in this run.
- The current complete JM-133 analysis code was available in the conversation and was saved under a human project path.
- Failed/diagnostic Figure 2 rebuild scripts were deliberately not committed as canonical code because their outputs did not complete and the real source table still needs source-shape resolution.
