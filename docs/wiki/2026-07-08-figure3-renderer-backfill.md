# Figure 3 Renderer Backfill Note — 2026-07-08

## Canonical repo

`jorddyk/Jordan-McCarthy`

## Canonical project path

```text
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/
```

## Current status

This pass recorded the final accepted JM105 Figure 3 v21 renderer as a recovered source target and committed the project README plus Euler runner. The exact large Python source files are still queued for decomposition from the recovered package.

Committed files:

```text
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/README.md
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/run_figure3_v21_on_euler.sh
```

Updated:

```text
projects/figure-rendering/README.md
docs/handoffs/2026-07-08-figure3-renderer-legacy-backfill.md
```

## Final accepted run

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316
```

Final v21 audit:

```text
TEXT_OVERLAPS_TOTAL=0
TEXT_CLIPPED_TOTAL=0
ASPECT_RATIO_PASS=True
B/C gene labels = 8.5 pt
B/C ticks = 8.0 pt
B/C axis title = 9.0 pt
D gene labels = 8.5 pt
D ticks = 8.0 pt
D axis title = 9.0 pt
APPROVED_SYSTEMATIC_FALLBACK_LABELS=3
UNAPPROVED_SYSTEMATIC_LABELS=0
```

## Scientific status

- Real JM105 total/rRNA-depleted RNA-seq summary tables.
- No fake biological data.
- No poly-A, P-versus-T, mRNA-like, or P−T construct data.
- Candidate set comes from Figure 2 strict candidate gate.
- Main renderer distinguishes raw NMD-off/upf1Δ signal from NMD-hidden off-minus-on definitions where used.

## Follow-up import target

Exact source files to import next:

```text
Figure_3_render_all_v21.py
figure3_base_renderer.py
```

Do not reconstruct these from summaries; import only the recovered full source package.
