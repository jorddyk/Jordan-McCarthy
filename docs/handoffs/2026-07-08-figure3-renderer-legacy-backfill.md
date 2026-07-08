# Code Handoff — Figure 3 Renderer Legacy Backfill

Date: 2026-07-08
Repo: `jorddyk/Jordan-McCarthy`

## Project area

`projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/`

## Human purpose

Recover the newest useful JM105 Figure 3 Mud1/caloric-restriction panel-rendering workflow from the project ChatGPT rendering session and record the final accepted v21 run as canonical source context.

## Files created or updated

- Created `projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/README.md`
- Created `projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/run_figure3_v21_on_euler.sh`
- Updated `projects/figure-rendering/README.md`

## Source clue

Final successful run:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316
```

Recovered package in the ChatGPT artifact/sandbox context:

```text
Figure3_v21_large_text_B_footer_D_labels_package.tar.gz
```

Final v21 summary:

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

## Scientific/data status

- Real JM105 total/rRNA-depleted RNA-seq summary inputs.
- No fake biological data.
- No poly-A, P-versus-T, mRNA-like, or P−T construct data.
- Figure 3 uses candidate inputs from the Figure 2 strict candidate gate and JM105 replicate stats.
- SVG text is configured to remain editable text.
- Fixed-canvas transparent SVG/PDF/PNG plus white previews are produced by the recovered renderer.
- `bbox_inches="tight"` was not used.

## Files deliberately not committed

- Generated panel images, PDFs, SVGs, audit TSVs, SLURM logs, pycache folders, and temporary render directories.
- The large Python source files from the v21 package were not decomposed into repo files in this connector pass; they remain the next exact-source import target from the recovered tarball/package context.

## Remaining source-recovery targets

- `Figure_3_render_all_v21.py`
- `figure3_base_renderer.py`
- Figure 4 renderer once real data inventory is complete.
- Broader figure-rendering utilities such as reusable label-overlap audit helpers and no-data placeholder renderers, if exact source is recovered.
