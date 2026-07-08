# 2026-07-08 Figure 4 Panel E Backfill

## Canonical paths

```text
projects/figure-rendering/panel-renderers/render-figure4-panel-e-external-context.py
projects/figure-rendering/panel-renderers/run-figure4-panel-e-external-context-euler.sh
projects/figure-rendering/panel-renderers/retrieve-figure4-panel-e-external-context.ps1
projects/figure-rendering/docs/2026-07-08-figure4-panel-e-backfill.md
```

## Human purpose

Recover the useful Figure 4 Panel E layout-fix workflow from the JM105 Figure 4 V17D/V17E2 repair conversation and save it under stable, human-readable figure-rendering paths.

## Source clues

```text
Figure4_RENDER_V17D_PPTSAFE_EXPORT_20260706_155050/render_figure4_v17d_pptsafe.py
Figure4_PANEL_E_LAYOUT_FIX_V17E2_20260706_161136
Figure4_panel_E_v17e2_clean.svg
Figure4_panel_E_v17e2_clean.preview_white.png
```

## Data/scientific status

- The imported renderer reads `Figure4E_source_values.tsv` from the previous V17D render directory.
- The optional locked fallback reproduces audited values from the repair thread and is off unless explicitly requested.
- No fake data are generated.
- The script is a layout repair for Panel E only.

## Remaining target

Recover the exact complete full-page V17D Figure 4 renderer from Euler and import it later as a full Figure 4 renderer, not as a reconstructed approximation.
