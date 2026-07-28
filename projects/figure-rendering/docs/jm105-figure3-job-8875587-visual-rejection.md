# JM105 Figure 3 job 8875587 — visual rejection

Date: 2026-07-28
Status: REJECTED

The Euler job completed technically, but the retrieved figure is not visually acceptable and must not be promoted or used as a manuscript figure.

## Exact visual failures

- Overall title is clipped at the right edge.
- Panel A title collides with the Panel B letter/title region.
- Panel A subtitle collides with the Panel B subtitle.
- Panel A y-axis title is clipped and visually duplicated into the left margin.
- Panel B y-axis title occupies the A/B gutter and collides with adjacent text.
- Panel B title is clipped at the right edge.
- Panel C title/subtitle collides with Panel D title/subtitle.
- Panel C count labels and stage labels collide with bars, connecting line, and adjacent text.
- Panel D row labels spill left into Panel C.
- Panel D exposes systematic intron identifiers rather than clean reader-facing common names.
- Panel D heatmap and colourbar are compressed into an unreadable footprint.
- Panel E title collides with Panel F title.
- Panel E left labels are clipped off-canvas.
- Panel E direct labels overlap points, lines, one another, and the legend.
- Panel F title/subtitle collides with Panel E and with its own legend.
- Panel F representative labels overlap traces and neighboring small multiples.
- Footer text is far below readable publication size.
- The six-panel equal-dashboard layout has no useful visual hierarchy and allocates insufficient plot area to text-heavy panels.
- The black-background transparent preview makes the failure more dramatic, but the white preview independently confirms the same collisions.

## Root cause

The renderer treated a nominal lane map as proof of collision safety. It did not fail closed after measuring the final rendered text and data objects. Technical Slurm completion was incorrectly conflated with figure completion.

## Required recovery

1. Freeze v7/v8/v9 as rejected incident evidence only.
2. Do not patch this composite with local text nudges.
3. Recover the exact mature Figure 3 source/output lineage from the prior v21 run and later source-bearing build directories.
4. Restore separate panel canvases and compose them only after each panel passes its own clipping, text-overlap, legend-data, and point-label audits.
5. Re-establish the current authoritative panel/scientific crosswalk before rendering.
6. Use common names only on visible panels.
7. Require a true post-draw hard collision gate to stop the run when any of the failures above occur.
8. Do not report success until Jordan has inspected the white preview and accepted it.
