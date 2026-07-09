# JM132 Cell-Cycle Rendering Rules

Scope: JM132 cell-cycle panels, especially Figure 3H / `JM132 Cell Cycle Length CR.xlsx`.

## Non-negotiable parsing rule

- The workbook contains division frame numbers, not precomputed cell-cycle lengths.
- Each row is one mother cell.
- Starting at Excel column **G**, each additional column to the right is the frame number for the next observed division event for that same cell.
- For division interval `i`, compute `frames_i = frame_column_(i+1) - frame_column_i` within the same row.
- Convert to minutes as `cell_cycle_length_minutes = frames_i * 10` for the JM132 Figure 3H workbook.
- Do not sort frame values.
- Do not infer timepoints from arbitrary numeric cells.
- Do not use metadata columns, glucose percentage, cell number, position, or any numeric fields before column G as division frames.
- A row with `k` contiguous numeric frame columns from G contributes exactly `k - 1` division intervals, numbered `1..k-1`. It is impossible for a cell to contribute intervals to the right of its last numeric frame column.
- The maximum plotted division interval must equal the maximum contiguous-frame-count minus one across rows; fail if a renderer creates division intervals beyond that.
- Do not skip or winsorize outlier intervals by default. Plot the data honestly and audit extremes rather than removing them.
- Preserve adjacent column order and audit every adjacent pair.
- If the start column or frame interval is ambiguous, ask Jordan before rendering.

## Error bars and statistics

- Plot line means with SEM error bars unless a source plot explicitly states SD.
- Primary statistics must not treat every division interval as independent.
- Use mother cell as the primary statistical unit or use a mixed/repeated-measures model.
- Record the exact statistical unit, test, endpoint, and inclusion/exclusion rules in `source_manifest.tsv`.

## Y-axis rule

For JM132 Figure 3H final-style panels:

1. Use a fixed shared visible y-axis of **0–400 minutes** for both glucose-condition subplots, matching the intended Figure 3H display.
2. Plot all positive adjacent intervals; do not filter outliers to make the plot prettier.
3. Write `values_above_visible_y_axis_audit.tsv` if any raw point or mean ± SEM bound is above 400 minutes, so clipping/visibility is explicit and not silent.
4. Write `y_axis_audit.tsv` containing raw min/max, SEM min/max, chosen limits, tick step, clipping count, and whether both panels share the scale.
5. If a value exceeds 400, do not pretend it was removed; state in the manifest that the visible axis is fixed to 0–400 and above-axis values are audited.

## Visual/layout rule

- For the square Figure 3H slot, stack the two same-style plots vertically.
- Do not render panel letter/title if the composite supplies them.
- Use a white preview PNG for inspection; transparent PNGs can look broken in black-background viewers.
- Keep text large enough for the final square panel.
