# Figure Rendering Legacy Code Backfill

This file tracks historical figure-rendering and manuscript-mockup code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue and import audit.

## Imported exact runnable source

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Recovered from the 2026-06-30 JM105 Figure 1E/F panel-rendering chat; latest useful V9 PRINT PowerShell/Python workflow after the layout/text-size repair sequence | Windows PowerShell orchestration that writes and runs a Python renderer for JM105 Figure 1E/F content-only print panels. Produces transparent SVG/PNG/3x PNG, white-preview PNG, TSV panel data, and JSON audit/provenance. | Imported runnable source. Uses real local JM105 total/rRNA-depleted tables if present. No fake data. No poly-A. Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR. Panel F is explicitly a raw NMD-off candidate/category set, not off-minus-on NMD-hidden IR. |

## Imported prompt/spec artifacts

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md` | `Pasted text (3).txt`, 2026-07-07 JM105 Figure 5 render prompt | Reusable exact contract for rendering Figure 5 from PowerShell + Euler without fake data and with lane/collision/provenance audits | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md` | `Pasted text.txt`, 2026-07-07 manuscript figure-redesign prompt | Reusable exact contract for redesigning the main/supplemental figure sequence around Yves/Nature Aging claim architecture | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md` | 2026-07-01/02 Figure 2 Panel F repair and postmortem conversation | Reusable lane-first figure-generation contract: define biological purpose, data transformation, forbidden claims, lane map, collision inventory, transparent outputs, editable SVG text, footer/descriptor axes, and semantic visual QA before code/patching | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md` | 2026-07-02 Figure 4 artifact-package discussion | Reusable artifact workflow contract: one downloadable ZIP package plus one PowerShell runner that uploads/runs on Euler and retrieves outputs, with strict data-integrity hard-stop behavior by default | Imported as prompt/spec; not runnable code |

## Priority code to recover

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `panel-renderers/jm134-starvation-switch-label-audit.py` | JM134 final layout and gene-labelled rerender workflow; Euler jobs `3101802`, `3104275`, `3106256`, `3109225` | Audit and rerender significant-in-both, JM105-only, and same-direction labels without overlap | Exact full source not yet recovered |
| 2 | `panel-renderers/jm133-weak-5ss-mud1-scatter.py` | JM133 weak 5-prime splice-site/Mud1 scatter with LOESS, highlighted leaky set, eight ringed candidates, and marginal violin | Render the final JM133 relationship panel while preserving exact candidate and label logic | Exact full source not yet recovered |
| 3 | `nature-aging-mockups/render-main-figure-layouts.py` | Recent Nature Aging / Yves-compatible figure mockup rendering conversations | Render drag-and-drop main-figure layout mockups for JM105/Intronsaurus while preserving existing panel aspect ratios and avoiding whitespace/text overlap | Exact full source not yet recovered |
| 4 | `nature-aging-mockups/score-figure-story-architecture.py` | Requested scoring model for humanized/Yves-compatible/Nature Aging-likely figures | Score figure layouts across acceptance-likelihood, Yves compatibility, and human/non-AI design | Exact full source not yet recovered |
| 5 | `panel-renderers/render-no-data-placeholder.py` | Figure 5 placeholder/NO DATA renderer | Render placeholders for experiments not yet done without fabricating data | Exact full source not yet recovered |
| 6 | `nature-aging-mockups/figure-5-layout-renderer.py` | Figure 5 rendering from PowerShell/Euler using uploaded Fig5 docs/PPT | Render Figure 5 mockup from existing panels and NO DATA placeholders, matching style of other panels | Exact full source not yet recovered |
| 7 | `nature-aging-mockups/render-synopsis-aligned-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Render normal all-intron/all-gene RNA-seq panels required by the synopsis; may live under JM105 figures rather than generic rendering | Full current source was previously reported visible in project chat but is not currently accessible as a complete source body; exact full source not yet recovered |
| 8 | `panel-renderers/render-figure2-panel-f-mud1-dependence.py` | Euler folders `PanelF_render_v7_TRANSPARENT_NO_BORDER_FOOTER_FIXED`, `PanelF_render_v8_FOOTER_SPACING_BEAUTIFUL`, and `PanelF_render_v9_TOP_DESCRIPTOR_SPACING_FIXED` | Render Figure 2F with computed NMD-hidden IR, data-driven y-limits, transparent outputs, dedicated descriptor/footer axes, and separated label lanes | Exact final complete source not yet recovered; patch sequence is not sufficient |

## 2026-07-13 recovery pass

File Library was searched with exact and combined clues for JM133, JM134, the four Euler job IDs, Figure 5, Nature Aging mockups, `NO DATA`, LOESS, marginal violin, and likely renderer filenames.

No complete Python, R, Bash, or PowerShell source body was recovered. Returned files were unrelated language/scientific documents or non-code project material and were excluded. Existing prompt/spec files remain valid implementation contracts but are not runnable substitutes.

## Mockup/image-generation artifacts deliberately not committed as code

- Generated Nature Aging-style mockup PNGs are not runnable source.
- Prompt assets may be canonical specifications, but schematic/mock values must never be represented as real manuscript data.

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
- Before patching a figure, list exact colliding objects by name and resolve by lane geometry, not by deleting required information.
- Final transparent SVG/PDF/PNG outputs must stay transparent; white previews are separate.

## Backfill method

1. Search old ChatGPT/project context by exact project names, job IDs, filenames, and output folders.
2. Search File Library and authorized sources for associated `.py`, `.R`, `.ps1`, `.sh`, `.sbatch`, and complete generated-script artifacts.
3. Recover the latest complete code only.
4. Commit recovered code under human-purpose names, not chat/date names.
5. Keep obsolete or partial code out of the repo unless explicitly documented as deprecated reference material.

## Containment action

This ledger is the single source of truth for unrecovered figure-rendering code. Historical job success, remembered outputs, prompt specifications, and patch sequences do not qualify as canonical runnable source.