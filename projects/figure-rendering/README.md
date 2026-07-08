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

## Canonical code status

No verified canonical figure-rendering script has been imported yet.

When imported, use human names such as:

- `nature-aging-mockups/render-main-figure-layouts.py`
- `nature-aging-mockups/score-figure-story-architecture.py`
- `panel-renderers/render-no-data-placeholder.py`

## Backfilled prompt/spec artifacts

| Path | Status | Purpose |
|---|---|---|
| `prompts/render-jm105-figure5-powershell-euler.md` | imported exact prompt/spec | Defines the Figure 5 PowerShell + Euler rendering contract, NO DATA rules, lane-map/collision/provenance workflow, and fixed-canvas export requirements. |
| `prompts/redesign-jm105-manuscript-figure-sequence.md` | imported exact prompt/spec | Defines the Nature Aging / Yves-compatible figure-sequence redesign task, confidence tags, panel inventory, claim architecture, and execution checklist. |
