# JM105 Figure 3 CR-selectivity diagnostic renderer

## Status: noncanonical diagnostic

`JM105_figure3_render_v2_1_20260728.py` renders a six-panel CR-selectivity figure titled “Caloric restriction selectively suppresses an age-associated retained-intron program.”

It is retained as a diagnostic/reference implementation, not as the canonical Figure 3 renderer. The repository’s 2026-07-28 incident record establishes that the locked Figure 3 is the Mud1-dependence figure and publicly uses Mud1-dependent CR suppression. This script instead centers CR selectivity and an internal candidate-scoring architecture, so it must not silently replace the accepted Figure 3 crosswalk.

Useful engineering retained here includes:

- fixed-canvas, lane-locked layout;
- visible common-name enforcement;
- literal-NaN rejection;
- editable SVG/PDF text;
- transparent SVG/PDF/PNG plus white-preview PNG;
- collision and geometry audits;
- refusal of synthetic/mock input paths.

Promotion requires a formal panel crosswalk, real-Euler render, target-font and fallback-font collision gates, retrieval, visual review, and Jordan acceptance. Until then, use this only as a diagnostic or source of reusable rendering patterns.

The file passed `python -m py_compile` before import.
