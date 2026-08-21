# Figure 3 panel-level correction specification — 2026-07-20

This specification supersedes the asset-only `Figure3_improved` composite as the definition of an improved Figure 3 render.

## Panel A

- Keep the four survival curves and exact cohorts from `JM100.xlsx`.
- Replace text-heavy statistical boxes with a colour-coded Cox proportional-hazards graphic.
- Show WT CR versus WT 2%, mud1Δ CR versus mud1Δ 2%, and the CR-by-genotype interaction.
- Retain exact sample sizes, p-values, 95% confidence intervals, model note and source assumptions.

## Panel D

- The x coordinate is quantitative NMD-hidden IR, not categorical condition position.
- Remove the categorical `2%` and `CR` endpoint labels from the x-axis.
- Preserve the marker encoding proved by the recovered v21 renderer and plot-source table:
  - **open circle = old 2% glucose**;
  - **filled circle = old 0.1% glucose CR**;
  - line = the same intron connected across conditions.
- Keep +MUD1 and mud1Δ headings in a separate group-label lane.
- Keep numerical NMD-hidden IR scales, rather than implying that left/right position encodes condition.

## Panel G

- Use the recovered exact v21 code, `Figure_3E_plot_source.tsv`, statistics audit and raw-source hashes.
- The recovered v21 renderer proves that triangles were generated for observations outside a robust 96th-percentile axis limit.
- Rerender with data-driven shared symmetric limits that display all finite values with padding.
- Do not retain clipping triangles merely because they appear in the previous image.
- Any future transformation, broken axis or overrange marker requires a written justification and source-table audit.

## Export contract

Every rerendered panel must export:

- transparent SVG with editable Arial-requested text;
- transparent PDF;
- transparent PNG;
- white-background preview PNG;
- plot-source and statistics/range-audit TSV files.

No `bbox_inches="tight"` is allowed. No information may be dropped to relieve crowding.

## Provenance rule

The accepted publication renderer must regenerate panel internals from the declared workbook/raw/source tables. A script that only extracts or rearranges PowerPoint assets is an assembly utility, not a panel renderer.

The exact recovered v21 source hashes are:

```text
Figure_3_render_all_v21.py  2595f23d89c0b040d861f95d3b26139c1856eb00103625c05e4498d21d4de8a4
figure3_base_renderer.py     9a8e87fdccd5509eb33328a6177350e442078c78be3025721975f504d97ddce1
```
