# JM105 Figure 4B/C sequence-architecture renderer

Purpose: canonical renderer for the final accepted JM105 Figure 4B/C selected-vs-background architecture panels.

This folder preserves the workflow that worked after the July 9, 2026 provenance and layout-debugging session. It is intentionally stored under `projects/figure-rendering/` because the code is primarily a rendering/orchestration workflow. The biological selected/background labels and feature values are read from real JM105 Euler source tables; no biological values are simulated.

## Canonical files

```text
projects/figure-rendering/panel-renderers/jm105-fig4bc-sequence-architecture/
  README.md
  render_jm105_fig4bc_polished.py
  run_jm105_fig4bc_polished_euler.sh
  run_jm105_fig4bc_polished_from_windows.ps1
  learning-loop-notes.md
```

## What the panels show

Figure 4B/C are downstream architecture panels. They do **not** re-discover candidates. They compare the selected JM105 Mud1/CR-sensitive aging-intron set against a clean high-confidence spliceosomal background.

- **Selected:** 49 introns from the RNA-seq source-derived candidate set.
- **Background:** 232 clean spliceosomal background introns from the same selected/background universe.
- **4B top:** 5′SS MaxEnt score.
- **4B bottom:** U1 complementarity shown as integer paired bases, computed as `u1_best_WC_pairs + u1_best_GU_pairs`.
- **4C top:** intron length.
- **4C bottom:** BP–3′SS distance.

## Why U1 is shown as integer paired bases

The earlier version showed `u1_complementarity_percent_paired`, which produced a staircase-looking percentage axis. The source table also contains integer pairing components:

```text
u1_best_WC_pairs
u1_best_GU_pairs
```

The visible panel now shows:

```text
u1_paired_bases = u1_best_WC_pairs + u1_best_GU_pairs
```

The percent metric is retained in `Figure4B_u1_metric_audit.tsv` for provenance but is not used as the visible y-axis.

## Euler source tables

The polished renderer expects these real source paths on Euler:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V1_20260703_110602/01_LOCKED_CANDIDATES_WITH_RECOMPUTED_SCORE.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V2_20260703_111531/05B_CLEAN_SPLICEOSOMAL_BACKGROUND.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_PATCH_BIOCONDA_MAXENTSCAN_GATE_V9_20260706_103936/10_PANEL_B_MAXENT_U1_SOURCE_TABLE_LOCKED.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv
```

Fallback candidate paths are encoded in the Python source but the run is fail-fast: it refuses to render if selected/background counts are not preserved after the feature join.

## Required runtime environment

On Euler, `/usr/bin/python3` did not have `matplotlib` or `PIL`. The successful run path loads:

```bash
module load fast_python_workshop_cpu/2025.0.0
```

The bash wrapper performs an import smoke test before rendering.

## Outputs

The renderer writes:

```text
out/panels/Figure4_panel_B_polished.svg
out/panels/Figure4_panel_B_polished.pdf
out/panels/Figure4_panel_B_polished.png
out/panels/Figure4_panel_B_polished_white_preview.png
out/panels/Figure4_panel_C_polished.svg
out/panels/Figure4_panel_C_polished.pdf
out/panels/Figure4_panel_C_polished.png
out/panels/Figure4_panel_C_polished_white_preview.png
out/panels/Figure4BC_polished_contact_sheet_white_preview.png
out/derived_data/*.tsv
out/audits/*.tsv
out/Figure4BC_polished_render_manifest.json
```

SVG text remains editable because `svg.fonttype` is set to `none`. The script does not use `bbox_inches="tight"`; the canvas dimensions are fixed constants.

## Run from Windows

From a local clone of `jorddyk/Jordan-McCarthy`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\figure-rendering\panel-renderers\jm105-fig4bc-sequence-architecture\run_jm105_fig4bc_polished_from_windows.ps1
```

The PowerShell runner uploads the sibling Python and bash files to Euler, runs the bash wrapper, retrieves `out/` and `logs/`, and opens the white contact sheet.

## Learning-loop notes

See `learning-loop-notes.md` for the preserved postmortem: what worked, what failed, and what future renderers should copy from this run.
