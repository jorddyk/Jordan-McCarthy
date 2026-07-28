# Meeting grounding for current Figure 4

## Numbering resolution

The July notebook used the older deck numbering:

- the caloric-restriction analysis was still the current Figure 2 and was deferred for reanalysis;
- the Mud1-dependence analysis was Figure 3;
- the architecture/Sharif analysis was Figure 4 and Yves moved it to supplementary.

The subsequent manuscript reorganization moved the caloric-restriction selectivity analysis into the current Figure 4 slot. The current title is:

> Caloric restriction selectively suppresses an age-associated retained-intron program

The title uses **suppresses**, not **opposes**, because suppression is the measured contrast.

## Notebook decisions that govern the rebuild

1. The old architecture Figure 4 is supplementary; it is not the main figure rebuilt here.
2. The old 4D was not intuitive; this reinforces the global rule that each panel must state exactly what should be apparent.
3. In the Mud1 figure, Yves called the direct comparison panel beautiful, removed a redundant candidate-by-candidate panel, and retained the ranking panel. The CR-selectivity figure therefore keeps one hero comparison, one transparent gate audit, and one ranking; it does not duplicate the same candidate comparison in multiple full panels.
4. All graphs must be concrete: raw conditions before derived contrasts, exact subtraction directions on axes, all eligible points visible, and all visible gene labels expressed as common names.

## Recovered six-panel contract

A. CR suppression defined from matched conditions.
B. 0.1% glucose is not a uniform eraser.
C. Aging effect versus 0.1%-glucose suppression is the hero comparison.
D. Explicit gates define the candidate program.
E. Candidate rank shows both required component effects before their minimum score.
F. Representative introns expose the raw replicate-level trajectories and include a nonresponsive comparator.

## Visual implementation decision

Each panel is rendered independently at final printed size. The package intentionally does not reproduce the failed single-canvas six-panel dashboard. A review contact sheet is generated only for inspection; final assembly should use the individual SVG/PDF panel assets.

## Promotion rule

The renderer implementing this contract is not canonical until it has run on the exact JM105 Euler inputs, passed the target-font and fallback-font audits, been retrieved and checked locally, and been visually accepted by Jordan. This document records the scientific and panel architecture only.
