# JM132 Cell-Cycle Rendering Rules

Scope: JM132 cell-cycle panels, especially Figure 3H / `JM132 Cell Cycle Length CR.xlsx`.

## Non-negotiable parsing rule

- The workbook contains division frame numbers, not precomputed cell-cycle lengths.
- Each row is one mother cell.
- Starting at Excel column **G**, each additional column to the right is the frame number for the next observed division event for that same cell.
- For division interval `i`, compute `frames_i = frame_column_(i+1) - frame_column_i` within the same row.
- Convert to minutes as `cell_cycle_length_minutes = frames_i * 15` for the JM132 Figure 3H workbook, matching the original analysis convention.
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

For final Nature Aging-style panels:

1. Compute candidate y-axis limits from the actual plotted quantities, including raw interval points and mean ± SEM bounds.
2. Use the same y-axis limits across glucose-condition subplots unless the panel explicitly argues for separate scales.
3. The default lower bound is 0 minutes unless negative values exist; negative values should normally trigger a data audit because cell-cycle lengths cannot be negative.
4. The upper bound must include all plotted mean+SEM bars and all raw points under the explicit inclusion rules. Do not silently omit outlier values to make the panel prettier.
5. Do not hardcode 0–400 merely because an older draft used it.
6. Snap the upper bound to a readable Nature-style tick step after adding breathing room.
7. Prefer 50-minute ticks when the upper limit is ≤250, 100-minute ticks when ≤600, 200-minute ticks when ≤1200, and 500-minute ticks above that.
8. Write `y_axis_audit.tsv` containing raw min/max, SEM min/max, chosen limits, tick step, clipping count, and whether both panels share the scale.
9. Fail before rendering if any plotted point or error bar would be clipped by the chosen axis.

## Visual/layout rule

- For the square Figure 3H slot, stack the two same-style plots vertically.
- Do not render panel letter/title if the composite supplies them.
- Use a white preview PNG for inspection; transparent PNGs can look broken in black-background viewers.
- Keep text large enough for the final square panel.
