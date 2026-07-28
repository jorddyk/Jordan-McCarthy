# JM105 Figure 4 v2 Panel D fallback-font collision

## Observed failure

Euler job `8888031` reached the renderer and failed during the explicit DejaVu Sans fallback audit. The exact collision was:

- `gate_name_0.1% suppression`
- `gate_count_0.1% suppression`

No panel output was promoted or retrieved as accepted.

## Root cause

Panel D placed retained-count text at a minimum x-position of 0.12 even when the final proportional gate bar was narrow. Under DejaVu Sans metrics, the right-anchored count extended left into the group-label text.

## Surgical resolution

1. Wide gate bars retain count text inside the bar.
2. Narrow gate bars place count text immediately to the right of the bar, left anchored.
3. Dropped-count spurs move into a vertically offset right-stat sub-lane so the spur cannot cross retained-count text.
4. No gate, count, spur, label, legend, or footer object is removed.
5. The Panel D canvas remains fixed at 4.55 × 3.55 inches.

## Regression test

The v3 PowerShell runner performs a DejaVu Sans Panel D audit before submitting Slurm. It reproduces the failed final-stage label with a narrow `53 / 240` final gate and requires:

- zero clipped registered text;
- zero registered text overlaps;
- all five bars, all drop spurs, and all category rows present.

## Promotion state

v3 is a candidate patch only. It is not canonical until it passes the exact real-data Euler render, retrieval, local white-preview inspection, and Jordan acceptance.
