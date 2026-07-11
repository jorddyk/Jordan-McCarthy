# CODE HANDOFF — 2026-07-11

## Repo

`jorddyk/Jordan-McCarthy` — verified private and writable. Authenticated permissions include admin and push. Default branch: `main`.

## Project area

`projects/jm105-intronsaurus/`

## Human purpose

Advance the initial legacy-code backfill without inventing source: search for the priority JM101/JM105 integration, STAR, Rsubread, DESeq2, and IRFinder scripts; record newly verified provenance and exact search keys; keep canonical code status accurate.

## Branch name

`main`

Markdown-only project documentation and audit maintenance were committed directly to the default branch.

## PR title

No PR created. Proposed title if this documentation batch had required a branch: `Document JM101 provenance and correct legacy recovery status`.

## Commit message

- `Document JM101 provenance recovery clue`
- `Update JM105 legacy recovery queue`
- `Refresh code wiki for JM101 provenance backfill`
- `Add 2026-07-11 code handoff`

## Project files created/updated

- Updated `projects/jm105-intronsaurus/README.md`.
  - Added `alignment/` to the intended project structure.
  - Recorded `JM101_RNAseq_Protocol_and_Provenance.docx` as a verified provenance clue.
  - Preserved the distinction between provenance and runnable source.
  - Clarified that inaccessible prior ephemeral-sandbox claims are not sufficient for canonical import.
- Updated `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`.
  - Rebuilt the priority queue around exact accessible-source status.
  - Added exact paths, filenames, outputs, and code strings from the JM101 provenance document.
  - Marked `110`, `111`, `112`, Rsubread Step 2, Step 3 DESeq2, IRFinder, and Intronsaurus builders as `exact full source not yet recovered` where appropriate.

## Handoff/audit files created/updated

- Updated `docs/wiki/Jordan-McCarthy-Code-Wiki.md`.
- Created `docs/handoffs/2026-07-11-code-handoff.md`.

## Files not to commit

No raw or generated data were committed. Specifically excluded:

- FASTQ, BAM, SAM, CRAM, BAI, bigWig.
- ND2 and TIFF stacks.
- Generated Intronsaurus HTML sites and archives.
- SLURM logs, caches, scratch folders, temporary figures, and Euler output clutter.
- The uploaded DOCX itself; its useful exact clues were recorded in project documentation instead.
- Any reconstructed approximation of the missing scripts.

## Scientific/data status

- No fake biological data were generated.
- No new analysis was run.
- No unsupported experiment or panel was represented as completed.
- JM105 Figure 2 remains total/rRNA-depleted only.
- Poly-A / P-versus-T / mRNA-like framing remains excluded from Figure 2 unless Jordan explicitly restores it.
- Raw NMD-off/upf1Δ retained signal remains distinct from NMD-hidden off-minus-on signal.
- RNA/host transcript abundance remains distinct from protein abundance.
- Caloric restriction is not labeled starvation.

## Implementation notes

Repository access was verified before writes. The repository is private, uses `main`, and the authenticated account has admin/push access.

File Library searches used the exact priority names and related search strings:

- `110_JM101_JM105_integrate_intronsaurus.py`
- `111_JM101_STAR_align_array.sbatch`
- `112_JM101_integrate_after_STAR.sbatch`
- JM101/JM105 STAR integration
- Rsubread Step 2 `RECLASSIFY + HARD-RESUME`
- Rsubread Step 2 `THROUGHPUT TURBO`
- Step 3 DESeq2
- IRFinder draft workflow

The searches did not return any complete script body. They returned `JM101_RNAseq_Protocol_and_Provenance.docx`, which verifies historical workflow details including:

- `Y:/Jordan/JM101`
- `C:/rna_seq/quasr_bam`
- `metadata_clean.csv`
- `yeast_introns_sacCer3.rds`
- `SGD_features.tab`
- QuasR intron/exon counting
- DESeq2 exon-derived size factors
- `IRratio = (intron + 1)/(exon + 1)`
- intron-fraction outputs
- Rsubread/featureCounts gene counts and CPM
- genotype×age interaction and ratio-of-ratios cross-check
- named `ir_outputs/` and `expression_outputs/` deliverables

These are now exact future search keys.

## Final code or candidate imports

Actual canonical code imported this run: **none**.

Candidate imports still pending:

1. `projects/jm105-intronsaurus/analysis/jm101-jm105-integrate-intronsaurus.py`
2. `projects/jm105-intronsaurus/alignment/jm101-star-align-array.sbatch`
3. `projects/jm105-intronsaurus/analysis/jm101-integrate-after-star.sbatch`
4. `projects/jm105-intronsaurus/analysis/jm101-rsubread-step2-reclassify-hard-resume.R`
5. `projects/jm105-intronsaurus/analysis/jm101-rsubread-step2-throughput-turbo.R`
6. `projects/jm105-intronsaurus/analysis/jm101-deseq2-step3.R`
7. `projects/jm105-intronsaurus/analysis/jm101-irfinder-draft-workflow.R`
8. Full Intronsaurus vNext3/vNext3AE/vNext3I/vNext3Y builders/readers
9. JM133/JM134 and Figure 2 candidate-gate scripts

## Legacy-backfill progress

Progress this run was documentation-grade rather than code-grade:

- Exact runnable source recovery: no new file.
- New verified provenance source: yes.
- Search-key quality: materially improved.
- Recovery-state accuracy: corrected.
- Queue prioritization: maintained.

Code-focused internal execution risk detected: prior documentation said some exact source had been recovered in an active sandbox, but that source body is not currently accessible. This creates false confidence and can cause a future run to skip recovery or claim code exists when it does not.

Containment action: the JM105 README, backfill queue, and wiki now require an accessible complete source body before a file is treated as recovered or canonical.