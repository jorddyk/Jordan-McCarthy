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
  docs/legacy-code-backfill.md
    Source-of-truth recovery ledger for unrecovered historical renderers.
  docs/jm105-figure2-euler-rendering-runbook.md
    Figure 2 Euler workflow, failure postmortem, and anti-repeat guardrails.
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
- For JM105/Intronsaurus panel rendering, read `templates/chatgpt-jm105-rendering-operating-standard.md` before writing new code.
- For JM105 Figure 2 Euler work, read `docs/jm105-figure2-euler-rendering-runbook.md` before launching or wrapping any renderer.

## Canonical code status

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `panel-renderers/render-figure1ef-total-rrna-print.ps1` | canonical | JM105 Figure 1E/F print panel workflow | Real total/rRNA-depleted inputs; no fake data or poly-A. |
| `panel-renderers/jm105-figure3-mud1-cr-panels/` | partial exact-source import | Recovered runner/README; complete Python package still pending | Real JM105 summary tables. |
| `panel-renderers/render-figure4-panel-e-external-context.py` | canonical | Corrected Figure 4E external-context renderer | Uses audited source values; layout repair only. |
| `panel-renderers/run-figure4-panel-e-external-context-euler.sh` | canonical | Euler wrapper for Figure 4E | Administrative wrapper. |
| `panel-renderers/retrieve-figure4-panel-e-external-context.ps1` | canonical | Retrieval helper for Figure 4E outputs | No biological values generated. |
| `panel-renderers/jm105-rendering-harness/` | canonical infrastructure | Source-discovery and fail-fast rendering harness | Infrastructure only. |
| `panel-renderers/jm105-fig4bc-sequence-architecture/` | canonical | Figure 4B/C selected-vs-background sequence architecture | Real selected/background data; no fake data. |
| `panel-renderers/jm105-figure4-secondary-structure-accessibility/` | canonical exploratory/control renderer | Figure 4G predicted splice-signal accessibility and RNAlib MFE-derived structure proxy | Real locked Figure 4 selected/background data; selected n=49; sequence extraction and method caveats audited. |

## Backfilled prompt/spec artifacts

The `prompts/` directory contains exact rendering contracts for Figure 5, manuscript-figure redesign, lane/collision auditing, and artifact packaging. These are specifications, not substitutes for missing runnable source.

## Current recovery focus

`docs/legacy-code-backfill.md` is the single source of truth for missing historical figure code. Highest-priority targets are the JM134 label-audit/rerender workflow, JM133 weak-5′SS/Mud1 renderer, main-figure layout renderer, story-scoring model, Figure 5 renderer, and reusable `NO DATA` renderer.

A 2026-07-13 evening File Library pass located exact uploaded files for the current Figure 5 C/D/E renderer and its Euler launcher, plus evidence that the corrected Figure 2 public-final renderer ran successfully after the `threshold_c` → `threshold_cr` fix. The complete Python files are present in File Library, but the current connector exposed only indexed excerpts rather than retrievable full file bytes, so they remain `PARTIAL / SOURCE LOCATED` and were not reconstructed or committed. The next import must use the exact uploaded `.py` files or the verified Euler paths, not snippet assembly.

The 2026-07-14 Figure 2 runbook records the failed archive, PowerShell policy, raw-text audit, moved-script, nested-SSH, and missing-positional-argument workflows. Future chats must inspect each recovered renderer's CLI before execution and run one panel renderer at a time on Euler before building an all-panel launcher.
