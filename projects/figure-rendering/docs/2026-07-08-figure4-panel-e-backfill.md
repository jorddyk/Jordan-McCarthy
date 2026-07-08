# Figure 4 Panel E Backfill Addendum

Status date: 2026-07-08

## Imported runnable source

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py` | 2026-07-06 JM105 Figure 4 V17D/V17E2 repair thread; Euler output clue `Figure4_PANEL_E_LAYOUT_FIX_V17E2_20260706_161136` | Render corrected Figure 4 Panel E external splice/stress context panel after label-collision repairs. | Imported runnable Python source. |
| `projects/figure-rendering/panel-renderers/run-figure4-panel-e-external-context-euler.sh` | Same repair thread | Run the Panel E renderer on Euler and package outputs. | Imported runnable helper. |
| `projects/figure-rendering/panel-renderers/retrieve-figure4-panel-e-external-context.ps1` | Same repair thread | Retrieve the fixed Panel E archive from Euler using explicit paths, avoiding the prior `.tar.gz`-as-directory failure. | Imported runnable helper. |

## Scientific/data status

- The renderer reads real derived values from `derived_data/Figure4E_source_values.tsv` in the previous V17D render directory.
- The optional locked fallback reproduces the audited V17D/V17E2 repair-thread values only when explicitly requested.
- No fake biological data are generated.
- This is a layout repair only; it does not recompute the biological comparison and does not alter Panels A/B/C/D/F.

## What was deliberately not committed

- Generated SVG/PDF/PNG outputs and tar archives were not committed.
- The complete full-page V17D Figure 4 renderer was not imported because the exact source file exists on Euler as `Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050/render_figure4_v17d_pptsafe.py` but was not recovered as a complete source text in this session.
- Older V10-V17C failed/intermediate figure scripts were not promoted as canonical code.

## Remaining source-recovery target

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050/render_figure4_v17d_pptsafe.py
```

Likely canonical path once exact full source is recovered:

```text
projects/figure-rendering/nature-aging-mockups/render-figure4-fullpage-atlas.py
```
