# Figure Rendering Legacy Code Backfill

This file tracks historical figure-rendering and manuscript-mockup code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue.

## Priority code to recover

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `nature-aging-mockups/render-main-figure-layouts.py` | Recent Nature Aging / Yves-compatible figure mockup rendering conversations | Render drag-and-drop main-figure layout mockups for JM105/Intronsaurus while preserving existing panel aspect ratios and avoiding whitespace/text overlap | Exact full source not yet recovered in this run |
| 2 | `nature-aging-mockups/score-figure-story-architecture.py` | Requested scoring model for humanized/Yves-compatible/Nature Aging-likely figures | Score figure layouts across acceptance-likelihood, Yves compatibility, and human/non-AI design | Exact full source not yet recovered in this run |
| 3 | `panel-renderers/render-no-data-placeholder.py` | Figure 5 placeholder/NO DATA renderer; source-spec clue in uploaded/project text: A–D default to `NO_DATA_PLACEHOLDER`, E `MODEL_ONLY`, F `CAVEAT_ONLY`; fixed 13.333333 × 7.5 inch canvas; output transparent SVG/PDF/PNG and white preview PNG; no `bbox_inches="tight"` | Render placeholders for experiments not yet done without fabricating data | Exact full renderer not recovered; specification recovered only |
| 4 | `nature-aging-mockups/figure-5-layout-renderer.py` | Figure 5 rendering from PowerShell/Euler using uploaded Fig5 docs/PPT; prompt/spec states Fig5_McCarthy.docx is authoritative, Fig5_McCarthy.pptx is visual mockup only, A–D should be `NO DATA — experiment pending` unless real sources are found | Render Figure 5 mockup from existing panels and NO DATA placeholders, matching style of other panels | Exact full source not recovered; source-spec/prompt recovered only |
| 5 | `panel-renderers/avoid-label-overlap-audit.py` | JM134/JM133 label-audit and rerender conversations | Audit plotted gene labels for completeness/overlap and preserve label counts | Exact full source not yet recovered in this run |
| 6 | `nature-aging-mockups/render-figure-5-from-euler-and-powershell.ps1` | Figure 5 prompt required a complete PowerShell script to create remote folder, upload renderer/manifests, submit/run Euler job, and retrieve SVG/PDF/PNG/white preview/logs/audits | End-to-end Windows↔Euler Figure 5 render orchestration | Exact full PowerShell source not recovered; prompt/spec recovered only |

## Figure-rendering guardrails

- Do not fake data.
- Preserve original panel aspect ratios unless resizing is explicitly allowed.
- Do not shrink text as the default crowding solution; crop canvas, reduce nonessential text, move text to captions, or expand plot lanes.
- Avoid text overlap, spillover, irrelevant panels, and unused whitespace.
- Clearly distinguish existing panels from newly required panels.
- If data are absent, mark the panel as `NO DATA`.
- Figure 2 must stay total/rRNA-depleted only unless Jordan explicitly changes it.
- SVG text must remain editable text, not paths.
- Canvas dimensions must be explicit; do not infer canvas from content.

## Backfill method

1. Search old ChatGPT/project context by exact project names and figure numbers.
2. Search File Library and Drive for associated `.pptx`, `.docx`, `.py`, `.R`, `.ps1`, `.sh`, and generated-script artifacts.
3. Recover the latest complete code only.
4. Commit recovered code under human-purpose names, not chat/date names.
5. Keep obsolete or partial code out of the repo unless it is explicitly documented as deprecated reference material.

## Current run notes — 2026-07-08

- Recovered detailed Figure 5 rendering requirements/specifications from project files, but not the exact full renderer source.
- No figure-rendering Python/PowerShell files were committed as runnable code in this run because only prompt/spec text was available, not complete exact source.
- Failed or incomplete panel renderers should remain uncommitted until exact full source is recovered or a new canonical renderer is intentionally written and labeled as newly authored.
