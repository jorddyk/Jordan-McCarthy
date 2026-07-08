# 2026-07-08 Legacy Code Backfill

## Repo

`jorddyk/Jordan-McCarthy`

## Scope

One-time beginning-of-repo backfill focused on project-organized canonical code, not a daily chronological dump.

## Project areas searched from accessible context

- JM105 / Intronsaurus conversation context and uploaded-file snippets.
- Figure rendering / Nature Aging / Figure 5 prompt and spec files.
- ImageJ/Fiji aging-chip macro source clues already documented in repo README.
- Language-learning source clues already documented in the code wiki.
- Personal intelligence agency prompt/rubric text supplied by Jordan in the current request.

## Files created or updated on branch `legacy-code-backfill-2026-07-08`

| Path | Action | Purpose |
|---|---|---|
| `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py` | Created | Canonicalized runnable JM-133 analysis: 5′SS:U1 strength vs Mud1-dependence in NMD-off total/rRNA-depleted RNA-seq. |
| `projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch` | Created | Euler sbatch launcher for JM-133. |
| `projects/jm105-intronsaurus/docs/legacy-code-backfill.md` | Updated | Added recovered/current JM-133 code and expanded remaining JM105 recovery queue. |
| `projects/figure-rendering/docs/legacy-code-backfill.md` | Updated | Added Figure 5 renderer/source-spec recovery status and noted that exact runnable source was not recovered. |
| `projects/personal-intelligence-agency/prompts/legacy-code-backfill-to-github.md` | Created | Saved Jordan's reusable legacy-code-backfill prompt/rubric. |
| `docs/wiki/Jordan-McCarthy-Code-Wiki.md` | Updated | Added canonical JM-133 paths, prompt path, remaining recovery targets, and guardrails. |
| `docs/handoffs/2026-07-08-legacy-code-backfill.md` | Created | Audit trail for this one-time backfill pass. |

## Files deliberately not committed

- Failed/diagnostic Figure 2 scripts `68_REBUILD_FIG2C_SHARED8_FROM_REAL_DATA_AND_COLLECT_ALL.py`, `69_DISCOVER_FIG2_CANDIDATES_REBUILD_FIG2C_AND_COLLECT.py`, and `70_DIAGNOSE_FIG2C_REAL_SOURCE_FAST.py` were not committed as canonical runnable analyses because the source table shape was not resolved and the rebuild did not complete.
- Older JM101/JM105 scripts were not reconstructed from memory. Their source clues remain in `projects/jm105-intronsaurus/docs/legacy-code-backfill.md`.
- ImageJ/Fiji macros were not reconstructed from summaries. Their source clues remain in `projects/imagej-fiji-aging-chips/README.md`.
- Language-learning HTML apps were not committed because complete HTML source was not recovered in this run.
- Raw sequencing, BAM/SAM/CRAM, ND2/TIFF stacks, generated render outputs, and SLURM logs were not committed.

## Scientific/data status

- The committed JM-133 analysis uses real total/rRNA-depleted RNA-seq tables discovered under `/cluster/scratch/jmccarthy/JM105_RNAseq` and does not fabricate biological data.
- Figure 2 constraints were preserved: total/rRNA-depleted only unless explicitly reversed, no poly-A data, distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on signal, and do not call caloric restriction starvation.
- The JM-133 script records whether U1 scoring used ViennaRNA or fallback canonical base-pair scoring.

## Remaining source-recovery targets

1. Exact JM101/JM105 integration scripts: `110_JM101_JM105_integrate_intronsaurus.py`, `111_JM101_STAR_align_array.sbatch`, `112_JM101_integrate_after_STAR.sbatch`.
2. Intronsaurus reader bundles: `Intronsaurus_Reader_First_RNA_Fate_vNext3.html`, `Intronsaurus_mRNA_Like_Pre_mRNAs_vNext3AE_code_bundle.zip`.
3. JM101 Rsubread/DESeq2/IRFinder R scripts from August 2025.
4. Figure rendering Python/PowerShell sources, especially Figure 5 NO DATA renderer.
5. Fiji/ImageJ JM128/JM129 macros and Groovy scripts.
6. Complete language-learning HTML apps.
