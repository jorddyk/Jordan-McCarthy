# Figure Rendering and Manuscript Mockups

Human goal: preserve reusable code for figure-panel rendering, figure-layout mockups, and manuscript visual planning.

This project is separate from JM105-specific analysis. Code belongs here when its main purpose is layout/rendering rather than calculating biological metrics.

## Start here for every new figure chat

Read these files before writing code or rendering:

```text
projects/figure-rendering/START_HERE_FOR_FIGURE_RENDERING.md
projects/figure-rendering/AGENTS.md
projects/figure-rendering/docs/figure-rendering-reliability-standard.md
projects/figure-rendering/templates/figure-rendering-new-chat-checklist.md
projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md
```

The reliability standard is cross-figure. It requires panel-identity and full-scope locks, verified source schemas and renderer CLIs, exact target-Euler execution, cross-font collision testing, direct retrieval, local verification, and Drive/GitHub logging. The complete Figure 2 incident chronology is in `docs/jm105-figure2-2026-07-14-complete-incident-postmortem.md`.

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
- A complete-figure request means every panel unless Jordan explicitly authorizes a staged subset.
- Current PowerPoint/composite panel identity cannot be changed because a different source or renderer is easier.
- Local preflight is not acceptance; the exact renderer must run in the target Euler environment.
- Record the actually resolved font and run the post-draw collision gate under the target font and an expected fallback.
- A remote render is incomplete until the same delivery includes direct Windows retrieval, local existence checks, and opening the white preview.
- For JM105/Intronsaurus panel rendering, read `templates/chatgpt-jm105-rendering-operating-standard.md` before writing new code.
- For JM105 Figure 2 Euler work, read `docs/jm105-figure2-euler-rendering-runbook.md` and the complete incident postmortem before launching or wrapping any renderer.

## Canonical code status

| Path | Status | Purpose | Data status |
|---|---|---|---|
| `panel-renderers/jm105-figure2-v4_1/` | canonical accepted execution reference | Complete Figure 2 A-F cross-font-safe renderer and Windows/Euler workflow | Real JM104 Panel A source; enriched strict Figure 2 source; accepted Panel E vector source; user-confirmed end-to-end success. |
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

The 2026-07-14 Figure 2 incident produced the accepted v4.1 execution pattern after failures involving archive layers, execution policy, missing files, raw-text audits, moved scripts, nested SSH, missing CLI arguments, Excel `UsedRange`, PowerShell interpolation, raw/enriched schemas, false visual audits, and cross-font clipping. Future figure chats must use the new reliability standard rather than repeat that discovery process.