# Figure Rendering and Manuscript Mockups

Human goal: preserve reusable code for figure-panel rendering, figure-layout mockups, and manuscript visual planning.

This project is separate from JM105-specific analysis. Code belongs here when its main purpose is layout/rendering rather than calculating biological metrics.

## Intended structure

```text
projects/figure-rendering/
  nature-aging-mockups/
    Reusable figure-layout and journal-style mockup scripts.
  panel-renderers/
    Standalone panel rendering utilities.
  templates/
    Style/layout templates and reusable configuration files.
  prompts/
    Reusable prompt/spec artifacts for figure redesign and rendering.
```

## Guardrails

- Do not fake data.
- Preserve original panel aspect ratios unless resizing is explicitly allowed.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- Clearly distinguish existing panels from newly required panels.
- If data are absent, mark the panel as `NO DATA`.
- SVG text should remain editable text.
- Fixed-canvas rendering scripts should not use a tight-crop save option.
- For JM105 Figure 2-related rendering, do not use poly-A / P-versus-T / mRNA-like logic unless Jordan explicitly restores it.
- Before patching a bad panel, name the exact colliding objects and reallocate lanes rather than locally nudging text.
- Final transparent SVG/PDF/PNG outputs must remain transparent unless an opaque background is explicitly requested; white previews are separate review artifacts.
- For JM105/Intronsaurus panel rendering, read `templates/chatgpt-jm105-rendering-operating-standard.md` before writing new code. Do not reinvent the renderer workflow from scratch.

## Canonical code status

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `panel-renderers/render-figure1ef-total-rrna-print.ps1` | imported from current project chat | PowerShell orchestration that writes and runs the recovered Python renderer for JM105 Figure 1E/F content-only, print-typography panels; outputs transparent SVG/PNG/3x PNG, white preview PNG, TSVs, and JSON audit. | Uses real local JM105 total/rRNA-depleted source tables if present. No fake biological data. No poly-A data. Panel E uses raw +MUD1 NMD-off/upf1D IR; Panel F uses an audited raw NMD-off set definition, not off-minus-on NMD-hidden IR. |
| `panel-renderers/jm105-figure3-mud1-cr-panels/` | partial exact-source import from current project chat | Recovered final v21 JM105 Figure 3 Mud1/CR panel-renderer package. README and Euler runner are committed; the complete Python source package remains a follow-up exact-source decomposition target from the recovered tarball. | Uses real JM105 total/rRNA-depleted summary tables. No fake biological data. No poly-A / P-versus-T / mRNA-like / P−T construct data. Final recovered run had `TEXT_OVERLAPS_TOTAL=0` and `TEXT_CLIPPED_TOTAL=0`. |
| `panel-renderers/render-figure4-panel-e-external-context.py` | imported from the 2026-07-06 JM105 Figure 4 V17D/V17E2 repair thread | Standalone Python renderer for the corrected Figure 4 Panel E external splice/stress-context panel after V17D label collisions. Emits editable SVG, PDF, transparent PNG, white-preview PNG, locked-values TSV, and layout/transparency audits. | Uses real V17D derived values from `Figure4E_source_values.tsv` when present; optional fallback reproduces the audited locked values from the repair thread. No fake data. Layout repair only. |
| `panel-renderers/run-figure4-panel-e-external-context-euler.sh` | imported from the 2026-07-06 JM105 Figure 4 V17E2 Euler workflow | Euler wrapper for running the Panel E external-context renderer and packaging outputs. | Administrative wrapper; does not generate biological values. |
| `panel-renderers/retrieve-figure4-panel-e-external-context.ps1` | imported from the 2026-07-06 JM105 Figure 4 V17E2 retrieval workflow | Retrieves and opens the fixed Panel E output archive from Euler without accidentally selecting the `.tar.gz` as a directory. | Retrieval helper only. |
| `panel-renderers/jm105-rendering-harness/` | added after repeated Figure 1D rendering failures and prior-chat postmortems | Reusable JM105 source-discovery/rendering harness rules and scripts; forces source inventory before deriving panel TSVs and prevents rendering after data-source failure. | Infrastructure only; reads headers/previews for discovery; no fake biological values. |

## Backfilled prompt/spec artifacts

| Path | Status | Purpose |
|---|---|---|
| `prompts/render-jm105-figure5-powershell-euler.md` | imported exact prompt/spec | Defines the Figure 5 PowerShell + Euler rendering contract, NO DATA rules, lane-map/collision/provenance workflow, and fixed-canvas export requirements. |
| `prompts/redesign-jm105-manuscript-figure-sequence.md` | imported exact prompt/spec | Defines the Nature Aging / Yves-compatible figure-sequence redesign task, confidence tags, panel inventory, claim architecture, and execution checklist. |
| `prompts/figure-panel-generation-lane-audit-contract.md` | imported exact prompt/spec from Figure 2 Panel F postmortem | Defines the lane-first, collision-inventory, transparency, footer, descriptor-axis, and data-provenance rules needed to prevent Figure 2-style layout whack-a-mole. |
| `prompts/figure-render-artifact-package-workflow.md` | imported exact prompt/spec from artifact workflow discussion | Defines the preferred one-ZIP-plus-one-PowerShell-runner workflow for generating downloadable figure-rendering packages and running them on Euler from Windows. |
| `templates/chatgpt-jm105-rendering-operating-standard.md` | added as persistent criticism ledger and operating standard | Converts repeated Jordan corrections into reusable JM105 rendering rules: source discovery first, one runnable PowerShell/Euler route, fixed canvas, large text, editable SVG, lane/collision audit, and fail-fast behavior. |
