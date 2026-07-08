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

## Canonical code status

No verified canonical runnable JM105/Intronsaurus script has been imported yet.

When imported, scripts should have human names such as:

- `analysis/calculate-nmd-hidden-intron-retention.py`
- `analysis/compare-mud1-cr-aging-effects.R`
- `figures/render-figure-2-total-rna-intron-module.py`
- `figures/render-nature-aging-layout-mockups.py`
