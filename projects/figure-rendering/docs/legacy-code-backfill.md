# Figure Rendering Legacy Code Backfill

This file tracks historical figure-rendering and manuscript-mockup code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue.

## Search/backfill results from this pass

File Library returned several uploaded prompt fragments documenting the exact rendering invariants for Figure 5 / Nature Aging-style panel production: lane maps before code, collision inventory before patching, data-provenance manifests, fixed-dimension transparent SVG/PDF/PNG plus white-preview PNG, editable SVG text, and explicit `NO DATA — experiment pending` placeholders. These are prompt/spec artifacts, not runnable source code, so no figure-rendering script was imported in this pass.

## Priority code to recover

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `nature-aging-mockups/render-main-figure-layouts.py` | Recent Nature Aging / Yves-compatible figure mockup rendering conversations | Render drag-and-drop main-figure layout mockups for JM105/Intronsaurus while preserving existing panel aspect ratios and avoiding whitespace/text overlap | Exact full source not yet recovered |
| 2 | `nature-aging-mockups/score-figure-story-architecture.py` | Requested scoring model for humanized/Yves-compatible/Nature Aging-likely figures | Score figure layouts across acceptance-likelihood, Yves compatibility, and human/non-AI design | Exact full source not yet recovered |
| 3 | `panel-renderers/render-no-data-placeholder.py` | Figure 5 placeholder/NO DATA renderer | Render placeholders for experiments not yet done without fabricating data | Exact full source not yet recovered |
| 4 | `nature-aging-mockups/figure-5-layout-renderer.py` | Figure 5 rendering from PowerShell/Euler using uploaded Fig5 docs/PPT | Render Figure 5 mockup from existing panels and NO DATA placeholders, matching style of other panels | Exact full source not yet recovered |
| 5 | `panel-renderers/avoid-label-overlap-audit.py` | JM134/JM133 label-audit and rerender conversations | Audit plotted gene labels for completeness/overlap and preserve label counts | Exact full source not yet recovered |
| 6 | `nature-aging-mockups/render-synopsis-aligned-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Render normal all-intron/all-gene RNA-seq panels required by the synopsis; may live under JM105 figures rather than generic rendering. | Full current source visible in project chat but not imported in this pass; next target. |

## Figure-rendering guardrails

- Do not fake data.
- Preserve original panel aspect ratios unless resizing is explicitly allowed.
- Do not shrink text as the default crowding solution; crop canvas, reduce nonessential text, move text to captions, or expand plot lanes.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- Clearly distinguish existing panels from newly required panels.
- If data are absent, mark the panel as `NO DATA`.
- Figure 2 must stay total/rRNA-depleted only unless Jordan explicitly changes it.
- SVG text should remain editable text, not outlined/path-converted.
- Do not use `bbox_inches="tight"` in fixed-canvas figure exports.

## Backfill method

1. Search old ChatGPT/project context by exact project names and figure numbers.
2. Search File Library and Drive for associated `.pptx`, `.docx`, `.py`, `.R`, `.ps1`, `.sh`, and generated-script artifacts.
3. Recover the latest complete code only.
4. Commit recovered code under human-purpose names, not chat/date names.
5. Keep obsolete or partial code out of the repo unless it is explicitly documented as deprecated reference material.
