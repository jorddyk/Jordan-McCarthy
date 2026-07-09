# JM132 Figure 3H successful renderer

Status: **successful / final code** after panel-by-panel PowerPoint audit.

Panel: Figure 3H, `mud1Δ does not cause gross cell-cycle slowing`.

Source workbook:

```text
Y:\Jordan\JM132 Does caloric restriction change cell cycle length in WT and Mud1 Delete backgrounds\JM132 Cell Cycle Length CR.xlsx
```

Final data interpretation rules:

- Each row is one mother cell.
- Excel column G onward contains ordered division-event frame numbers for that row/cell.
- Each additional column to the right is the next division event for the same cell.
- Division interval `i` is computed as adjacent subtraction within the row: `frame[i+1] - frame[i]`.
- Convert frames to minutes with `10 minutes/frame`.
- A cell with `k` contiguous frame values from column G contributes exactly `k - 1` division intervals, numbered `1..k-1`.
- Include all cells regardless of `Dies on chip?`.
- Use positive adjacent deltas only; nonpositive deltas are audited.
- Do not skip or winsorize high values. Values above the visible axis are audited, not removed.
- Visible y-axis is fixed at `0–400 minutes` for both glucose subplots.
- Error bars are SEM.
- Primary statistic uses mother cell as the unit for d1–10 cell-level mean, not interval-level pseudoreplication.

Final runnable script:

```text
projects/figure-rendering/panel-renderers/jm132-cell-cycle-fig3h/run_jm132_fig3h_g_column_10min_y400.ps1
```

Expected outputs include transparent SVG/PDF/PNG, white preview PNG, source manifest, row/adjacent-pair audits, y-axis audit, values-above-visible-axis audit, group counts, and text layout audit.
