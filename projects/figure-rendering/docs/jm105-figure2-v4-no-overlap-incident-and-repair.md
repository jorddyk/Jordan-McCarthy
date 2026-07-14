# JM105 Figure 2 v4 no-overlap incident and repair

Date: 2026-07-14

## Incident

A Figure 2 rerender was delivered with obvious visual regressions despite an audit claiming zero overlaps. The defects included:

- Panel A legend covering survival curves.
- Panel B axis labels colliding with other elements and leaving the panel; axes too heavy; points too large and visually merged.
- Panel C widespread text collisions and failure to preserve the accepted PowerPoint quadrant layout.
- Panel D candidate text entering the aging-effect column.
- Panel E subplot-title/x-tick and legend collisions.
- Panel F a funnel layout that departed too far from the accepted checklist-style PowerPoint panel.

The prior audit was inadequate because it did not make acceptance conditional on the final rendered extents and did not test semantic collisions such as legend versus data or labels versus points.

## Permanent rule

A JM105 renderer must not print success, package outputs, or present a panel for review unless a hard post-draw/pre-save gate passes on the actual final geometry.

Required checks:

1. every visible text bounding box is inside the fixed canvas;
2. every pair of visible text boxes has a positive separation;
3. public text contains no systematic yeast ORF identifiers;
4. labelled scatter panels have zero points inside any label bounding box;
5. legends assigned to a separate lane do not intersect the data axes;
6. panel-specific lane geometry is explicit and exported;
7. collision inventory is explicit and exported;
8. the complete A-F contact sheet is rendered and inspected after the individual panels;
9. no automatic tight-crop save call is permitted;
10. a claim of “zero overlap” is invalid unless derived from measured renderer extents.

Reusable implementation:

`projects/figure-rendering/qa/hard_collision_gate.py`

## Figure 2 v4 repair strategy

- Panel A: move the cohort legend to a dedicated lane above the KM axes.
- Panel B: use thinner axes, smaller points, an independent legend lane, expanded axis-label lanes, and a right label column.
- Panel C: restore the accepted four-quadrant PowerPoint logic with distinct heading/body/direction/footer lanes.
- Panel D: shorten visible candidate entries to common names and allocate fixed, non-overlapping columns for rank, candidate, two bars, two values, and score.
- Panel E: recover the exact replicate values from the accepted Matplotlib SVG vector coordinates and rerender them in a 2x2 grid; top-row x-tick labels are removed so they cannot touch bottom-row gene titles.
- Panel F: return to the accepted numbered checklist visual language while retaining only the four informative validated transitions and the corrected n=49 final set.

## Source locks

- Panel A: 150 JM104 cell records, 52 at 2% glucose and 98 at 0.5% glucose CR; log-rank p approximately 5.50e-04.
- B/D/F: enriched strict eligible source with counts 284 -> 64 -> 53 -> 49.
- E: exact point coordinates from the accepted PowerPoint SVG, not raster digitization and not simulated values.

## Acceptance status

The v4 renderer is a review candidate, not the canonical accepted renderer. Do not place the full renderer in the canonical package until Jordan explicitly accepts the visual result. The hard collision gate itself is canonical infrastructure and must be used in future figure work.
