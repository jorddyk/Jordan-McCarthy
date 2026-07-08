# Code Handoff — Figure 1E/F Renderer Backfill

Date: 2026-07-08 Europe/Zurich

## Repo

`jorddyk/Jordan-McCarthy`

## Project area

`projects/figure-rendering/`

## Human purpose

Recover the newest useful complete figure-panel rendering code from the JM105 Figure 1E/F repair conversation and store it under a human-readable canonical path.

## Files created/updated

Created:

- `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1`
- `projects/figure-rendering/panel-renderers/README.md`
- `docs/handoffs/2026-07-08-code-handoff-figure1ef-renderer.md`

Updated:

- `projects/figure-rendering/README.md`
- `projects/figure-rendering/docs/legacy-code-backfill.md`
- `docs/wiki/Jordan-McCarthy-Code-Wiki.md`
- `docs/legacy-code-backfill.md`

## Code imported

`render-figure1ef-total-rrna-print.ps1` is a complete Windows PowerShell orchestration script. It writes and runs an embedded Python renderer for Figure 1E/F content-only print panels.

Expected local inputs:

- `JM105_primary53_intron_EI_IE_EE_counts_LONG.csv`
- `JM105_intron_retained_RNA_burden_by_condition.csv`
- `Figure_1D_AUDIT_provenance.json`

Expected outputs:

- `Figure_1E_CONTENTONLY_NATURE_PRINT.svg`
- `Figure_1E_CONTENTONLY_NATURE_PRINT.png`
- `Figure_1E_CONTENTONLY_NATURE_PRINT_3x.png`
- `Figure_1E_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png`
- `Figure_1F_CONTENTONLY_NATURE_PRINT.svg`
- `Figure_1F_CONTENTONLY_NATURE_PRINT.png`
- `Figure_1F_CONTENTONLY_NATURE_PRINT_3x.png`
- `Figure_1F_CONTENTONLY_NATURE_PRINT_WHITE_PREVIEW.png`
- TSV panel data and JSON audit/provenance files.

## Files deliberately not committed

- Generated Figure 2–5 mockup PNGs from image generation. They are visual artifacts with schematic/mock values, not source code.
- Old failed Figure 1E/F intermediate scripts and outputs.
- Raw JM105 data tables, generated figure outputs, tarballs, and local/Euler scratch folders.

## Scientific/data status

- Uses real local JM105 total/rRNA-depleted source tables if present.
- No fake biological data.
- No poly-A data.
- Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR.
- Panel F uses an explicitly audited raw NMD-off candidate/category set definition and does not claim off-minus-on NMD-hidden IR.
- CR definition is guarded as 0.1% glucose in the provenance check.

## Implementation notes

- Fixed canvas sizes are declared in Python.
- `bbox_inches="tight"` is not used.
- SVG text remains editable through `plt.rcParams["svg.fonttype"] = "none"`.
- The script fails if required inputs are missing or if the raw IR recomputation audit fails.

## Remaining source-recovery targets

- `projects/figure-rendering/nature-aging-mockups/render-main-figure-layouts.py`
- `projects/figure-rendering/nature-aging-mockups/score-figure-story-architecture.py`
- `projects/figure-rendering/panel-renderers/render-no-data-placeholder.py`
- `projects/figure-rendering/nature-aging-mockups/figure-5-layout-renderer.py`
- `projects/figure-rendering/panel-renderers/avoid-label-overlap-audit.py`
