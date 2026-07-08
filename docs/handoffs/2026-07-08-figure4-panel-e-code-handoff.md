# Code Handoff — Figure 4 Panel E Backfill

Date: 2026-07-08
Repo: `jorddyk/Jordan-McCarthy`
Project area: `projects/figure-rendering/`

## Human purpose

Recovered and committed the useful JM105 Figure 4 Panel E layout-fix workflow from the V17D/V17E2 repair sequence.

## Files created

```text
projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py
projects/figure-rendering/panel-renderers/run-figure4-panel-e-external-context-euler.sh
projects/figure-rendering/panel-renderers/retrieve-figure4-panel-e-external-context.ps1
projects/figure-rendering/docs/2026-07-08-figure4-panel-e-backfill.md
docs/wiki/2026-07-08-figure4-panel-e-backfill.md
```

## Files updated

```text
projects/figure-rendering/README.md
```

## Files deliberately not committed

- Rendered SVG/PDF/PNG outputs and archives.
- Failed/intermediate V10-V17C scripts.
- The full V17D Figure 4 renderer, because the exact full source still needs to be recovered from Euler before import.

## Scientific/data status

- No fake biological data.
- Panel E values are read from `Figure4E_source_values.tsv` when available.
- Optional locked fallback reproduces audited V17D/V17E2 values only when explicitly requested.
- Layout repair only; no biological recomputation.

## Remaining recovery targets

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050/render_figure4_v17d_pptsafe.py
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_RENDER_V16B_NATIVE_LABELS_20260706_150031/render_figure4_v16b.py
```
