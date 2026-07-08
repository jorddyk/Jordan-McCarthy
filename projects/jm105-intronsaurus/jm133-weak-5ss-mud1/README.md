# JM-133 — Weak 5′ splice sites and Mud1 dependence

## Human purpose

This project asks whether introns that gain retained/unspliced RNA after Mud1 loss in an NMD-off background have weaker predicted 5′ splice-site pairing to U1.

## Scientific/data status

- Real-data analysis only.
- Intended source data: total/rRNA-depleted JM105 RNA-seq and intron feature tables under `/cluster/scratch/jmccarthy/JM105_RNAseq`.
- No fake biological data should be generated.
- Preserve JM105 constraints: Figure 2 is total/rRNA-depleted only unless explicitly reversed; do not use poly-A for Figure 2; distinguish raw NMD-off/upf1Δ retained signal from NMD-hidden off-minus-on; distinguish RNA/host transcript abundance from protein abundance; do not call caloric restriction starvation.

## Recovered exact source

Exact source for the JM-133 Python analysis and Euler sbatch launcher was recovered into GitHub PR #1 on branch `legacy-code-backfill-2026-07-08`:

```text
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.py
projects/jm105-intronsaurus/analysis/jm133-weak-5ss-need-mud1.sbatch
```

Connector-visible PR status during the 2026-07-08 continuation audit:

```text
PR #1: Legacy code backfill: JM133 and recovery docs
state: open
mergeable: false
branch: legacy-code-backfill-2026-07-08
```

Because the PR is open and non-mergeable from the connector context, this directory records the canonical project location but does not duplicate a partial or reconstructed Python script on `main`.

## Canonical target paths once reconciled

```text
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.py
projects/jm105-intronsaurus/jm133-weak-5ss-mud1/jm133-weak-5ss-need-mud1.sbatch
```

## Original source clues

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/scripts/71_JM133_weak_5SS_need_Mud1.py
/cluster/scratch/jmccarthy/JM105_RNAseq/71_JM133_DO_WEAK_5SS_NEED_MUD1/
Y:\Jordan\JM133 Do weak 5′ splice sites need Mud1
```

## Import rule

Do not reconstruct this analysis from summaries. Import only the exact full Python and sbatch source from PR #1, the Euler path, or another complete recovered source.
