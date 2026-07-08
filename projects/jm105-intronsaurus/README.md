# JM105 / Intronsaurus Analysis

Human goal: preserve canonical code supporting Jordan's JM105 RNA-seq, intron retention, NMD-hidden leakage, Mud1/CR, aging, and manuscript figure workflows.

This project is for analysis code and reusable figure-generation code, not raw sequencing data.

## Intended structure

```text
projects/jm105-intronsaurus/
  analysis/
    RNA-seq and intron-retention analysis scripts.
  figures/
    Scripts that generate manuscript figure panels from real inputs.
  metadata/
    Small, human-readable sample maps or schema documents only. No raw sequencing files.
  docs/
    Recovery notes and legacy-source audit trails.
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
| `analysis/jm105-old-cell-leaky-intron-determinants.py` | imported | Classifies old-selective NMD-revealed introns and compares gene module / splice-site / branchpoint / 3′SS / PPT features against nonleaker comparison introns. | Uses real JM105 tables on Euler; no simulated biological data. |

## Canonical code still targeted for recovery

See `docs/legacy-code-backfill.md` for exact historical filenames and source clues. Highest-priority unrecovered targets include the JM101/JM105 Intronsaurus integration scripts, STAR/sbatch jobs, Rsubread step 2/3 scripts, IRFinder drafts, and Intronsaurus reader bundles.
