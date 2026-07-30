# JM105 Figure 4 Mud1-coupling reference renderer

`JM105_figure4_render_v11_2_20260729.py` is a complete eight-panel renderer for the question: does Mud1 coordinate retained-intron processing, host-transcript abundance, and the replicative-lifespan response under caloric restriction?

## What it renders

- lifespan survival curves and a lifespan estimation panel;
- +MUD1 versus `mud1Δ` retained-intron suppression;
- ranked Mud1 dependence;
- host-transcript abundance responses;
- coupling between host response and NMD-revealed IR suppression;
- an abundance-adjusted comparison;
- paired candidate heatmaps.

## Data and rendering safeguards

- requires real count data and an explicit common-gene-name map;
- refuses paths marked as dry-run, synthetic, fixture, fake, mock, dummy, simulated, or example;
- does not fabricate lifespan panels when lifespan input is absent;
- freezes and hashes the selected candidate list;
- emits provenance and manifest sidecars;
- uses a fixed 7.2 × 13.6 inch canvas;
- emits transparent SVG/PDF/PNG plus a white-background preview PNG;
- does not use `bbox_inches="tight"`;
- keeps SVG text editable.

## Repository status

This file is stored as a reference renderer rather than silently declared the accepted Figure 4. The repository’s current Figure 4 panel contract and acceptance records must be reconciled before promotion to a canonical renderer. Its layout, provenance, and audit machinery can be reused as a baseline for later figures.

The file passed `python -m py_compile` before import.
