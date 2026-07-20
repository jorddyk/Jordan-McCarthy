# Figure 3 panel-level correction specification — 2026-07-20

This specification supersedes the asset-only `Figure3_improved` composite as the definition of an improved Figure 3 render.

## Panel A

- Keep the four survival curves and exact cohorts from `JM100.xlsx`.
- Replace text-heavy statistical boxes with a colour-coded hazard-ratio graphic.
- Show WT CR versus WT 2%, mud1Δ CR versus mud1Δ 2%, and the CR-by-genotype interaction.
- Retain exact sample sizes, p-values, confidence intervals and source assumptions.

## Panel D

- The x coordinate is quantitative NMD-hidden IR, not categorical condition position.
- Remove the categorical `2%` and `CR` labels from the x-axis.
- Add a marker legend: filled circle = old 2% glucose; open circle = old CR.
- A line connects the same intron across the two conditions.
- Keep +MUD1 and mud1Δ headings in a separate group-label lane.

## Panel G

- Recover the exact v21 code, `Figure_3E_plot_source.tsv`, statistics audit and raw source hashes before changing the plot.
- Determine whether triangles are deliberate out-of-range indicators.
- Default to data-driven x/y limits that display all finite values with padding.
- Do not retain clipping triangles merely because they appear in the current image.
- Any transformation, broken axis or retained overrange marker requires a written justification and source-table audit.

## Export contract

Every panel and the composite must export:

- transparent SVG with editable text;
- transparent PDF;
- transparent PNG;
- white-background preview PNG.

No `bbox_inches="tight"` is allowed. No information may be dropped to relieve crowding.

## Provenance rule

The accepted publication renderer must regenerate panel internals from the declared workbook/raw/source tables. A script that only extracts or rearranges PowerPoint assets is an assembly utility, not a panel renderer.
