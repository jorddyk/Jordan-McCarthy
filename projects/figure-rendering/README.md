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
- Fixed-canvas rendering scripts should not use `bbox_inches="tight"`.
- For JM105 Figure 2-related rendering, do not use poly-A / P-versus-T / mRNA-like logic unless Jordan explicitly restores it.
- Before patching a bad panel, name the exact colliding objects and reallocate lanes rather than locally nudging text.
- Final transparent SVG/PDF/PNG outputs must remain transparent unless an opaque background is explicitly requested; white previews are separate review artifacts.

## Canonical code status

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `panel-renderers/render-figure1ef-total-rrna-print.ps1` | imported from current project chat | PowerShell orchestration that writes and runs the recovered Python renderer for JM105 Figure 1E/F content-only, print-typography panels; outputs transparent SVG/PNG/3x PNG, white preview PNG, TSVs, and JSON audit. | Uses real local JM105 total/rRNA-depleted source tables if present. No fake biological data. No poly-A data. Panel E uses raw +MUD1 NMD-off/upf1D IR; Panel F uses an audited raw NMD-off set definition, not off-minus-on NMD-hidden IR. |

## Backfilled prompt/spec artifacts

| Path | Status | Purpose |
|---|---|---|
| `prompts/render-jm105-figure5-powershell-euler.md` | imported exact prompt/spec | Defines the Figure 5 PowerShell + Euler rendering contract, NO DATA rules, lane-map/collision/provenance workflow, and fixed-canvas export requirements. |
| `prompts/redesign-jm105-manuscript-figure-sequence.md` | imported exact prompt/spec | Defines the Nature Aging / Yves-compatible figure-sequence redesign task, confidence tags, panel inventory, claim architecture, and execution checklist. |
| `prompts/figure-panel-generation-lane-audit-contract.md` | imported exact prompt/spec from Figure 2 Panel F postmortem | Defines the lane-first, collision-inventory, transparency, footer, descriptor-axis, and data-provenance rules needed to prevent Figure 2-style layout whack-a-mole. |
| `prompts/figure-render-artifact-package-workflow.md` | imported exact prompt/spec from artifact workflow discussion | Defines the preferred one-ZIP-plus-one-PowerShell-runner workflow for generating downloadable figure-rendering packages and running them on Euler from Windows. |
