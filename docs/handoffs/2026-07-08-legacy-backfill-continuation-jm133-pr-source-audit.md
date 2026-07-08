# CODE HANDOFF — 2026-07-08 — JM133 PR/source audit continuation

## Repo

`jorddyk/Jordan-McCarthy`

## Project area

JM105 / Intronsaurus legacy code backfill, with spillover source checks for figure rendering, ImageJ/Fiji aging-chip macros, language-learning apps, and personal-intelligence prompts.

## Human purpose

Continue the one-time beginning-of-repo backfill without clutter: recover exact source when available, document exact source clues when not, and avoid reconstructing missing biological or microscopy code from summaries.

## Files created/updated

Updated:

```text
projects/jm105-intronsaurus/docs/legacy-code-backfill.md
```

Created:

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/README.md
docs/handoffs/2026-07-08-legacy-backfill-continuation-jm133-pr-source-audit.md
```

## Files deliberately not committed

- Did not duplicate the full JM-133 Python script onto `main`, because exact source already exists in open PR #1 on branch `legacy-code-backfill-2026-07-08`, while the PR is connector-visible as open and non-mergeable.
- Did not reconstruct ImageJ/Fiji `.ijm`, Groovy, language-learning HTML, or Figure 5 renderer code from summaries or snippets.
- Did not commit raw ND2/TIFF/FASTQ/BAM data, generated plots, tarballs, Word/PowerPoint manuscript artifacts, or transient logs.

## Scientific/data status

- The JM-133 exact source in PR #1 is real-data-only code for total/rRNA-depleted JM105 RNA-seq and intron feature tables.
- No fake biological data were generated or committed in this continuation.
- Missing experiments and figure panels remain governed by the `NO DATA — experiment pending` rule.
- JM105 constraints remain active: Figure 2 total/rRNA-depleted only unless explicitly reversed; no poly-A for Figure 2; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on; distinguish RNA/host transcript abundance from protein abundance; do not call CR starvation.

## Implementation notes

GitHub audit found PR #1:

```text
PR #1: Legacy code backfill: JM133 and recovery docs
branch: legacy-code-backfill-2026-07-08
state: open
mergeable: false
files:
  projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py
  projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch
```

Google Drive searches in this continuation:

```text
MitoSOX macro -> found Lab Notebook complete copy and paste text dump, which names JM-076 macro paths but not macro bodies
Step1_DetectAdjustConvertResize -> same lab-notebook clue
kartoffel_vocabulary_active_recall_WORKING -> no complete HTML source recovered
german-drill-6 -> no complete HTML source recovered
```

Current uploaded-file search found Figure 5 prompt/spec text and manuscript planning artifacts, not new runnable renderer code.

## Final code paths / source status

Exact recovered but staged outside `main`:

```text
PR #1 branch legacy-code-backfill-2026-07-08:
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch
```

Canonical project folder reserved on `main`:

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/
```

## Legacy-backfill progress

This pass upgraded the JM-133 state from “source clue” to “exact source exists in PR #1 but needs reconciliation onto `main` or rebasing.”

Still pending exact-source recovery/import:

```text
141_intronsaurus_matched_rna_protein_gene_stories_v3Y.py
scripts/26_paired_gene_body_normalized_leakage_test.py
scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py
JM134 beta-binomial / final layout repair scripts
JM128/JM129 Fiji/Groovy microscopy macros
language-learning complete HTML apps
runnable Figure 5 PowerShell/Bash/Python renderer source
personal-intelligence scoring rubric/report templates
```
