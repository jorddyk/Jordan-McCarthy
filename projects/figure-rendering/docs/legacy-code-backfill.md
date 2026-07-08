# Figure Rendering Legacy Code Backfill

This file tracks historical figure-rendering and manuscript-mockup code that should be recovered from old ChatGPT conversations, uploaded files, Drive artifacts, or local/Euler paths and then saved under project-first human file names.

Do not treat this file as code. It is a recovery queue and import audit.

## Imported exact runnable source

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/panel-renderers/render-figure1ef-total-rrna-print.ps1` | Recovered from the 2026-06-30 JM105 Figure 1E/F panel-rendering chat; latest useful V9 PRINT PowerShell/Python workflow after the layout/text-size repair sequence | Windows PowerShell orchestration that writes and runs a Python renderer for JM105 Figure 1E/F content-only print panels. Produces transparent SVG/PNG/3x PNG, white-preview PNG, TSV panel data, and JSON audit/provenance. | Imported runnable source. Uses real local JM105 total/rRNA-depleted tables if present. No fake data. No poly-A. Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR. Panel F is explicitly a raw NMD-off candidate/category set, not off-minus-on NMD-hidden IR. |

## Imported prompt/spec artifacts

File Library returned several uploaded prompt/spec artifacts documenting the exact rendering invariants for Figure 5 / Nature Aging-style panel production: lane maps before code, collision inventory before patching, data-provenance manifests, fixed-dimension transparent SVG/PDF/PNG plus white-preview PNG, editable SVG text, and explicit `NO DATA — experiment pending` placeholders.

| Canonical path | Source clue | Purpose | Status |
|---|---|---|---|
| `projects/figure-rendering/prompts/render-jm105-figure5-powershell-euler.md` | `Pasted text (3).txt`, 2026-07-07 JM105 Figure 5 render prompt | Reusable exact contract for rendering Figure 5 from PowerShell + Euler without fake data and with lane/collision/provenance audits | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/redesign-jm105-manuscript-figure-sequence.md` | `Pasted text.txt`, 2026-07-07 manuscript figure-redesign prompt | Reusable exact contract for redesigning the main/supplemental figure sequence around Yves/Nature Aging claim architecture | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md` | 2026-07-01/02 Figure 2 Panel F repair and postmortem conversation | Reusable lane-first figure-generation contract: define biological purpose, data transformation, forbidden claims, lane map, collision inventory, transparent outputs, editable SVG text, footer/descriptor axes, and semantic visual QA before code/patching | Imported as prompt/spec; not runnable code |
| `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md` | 2026-07-02 Figure 4 artifact-package discussion | Reusable artifact workflow contract: one downloadable ZIP package plus one PowerShell runner that uploads/runs on Euler and retrieves outputs, with strict data-integrity hard-stop behavior by default | Imported as prompt/spec; not runnable code |

## Priority code to recover

| Priority | Proposed canonical path | Historical/source clue | Purpose | Current status |
|---|---|---|---|---|
| 1 | `nature-aging-mockups/render-main-figure-layouts.py` | Recent Nature Aging / Yves-compatible figure mockup rendering conversations | Render drag-and-drop main-figure layout mockups for JM105/Intronsaurus while preserving existing panel aspect ratios and avoiding whitespace/text overlap | Exact full source not yet recovered |
| 2 | `nature-aging-mockups/score-figure-story-architecture.py` | Requested scoring model for humanized/Yves-compatible/Nature Aging-likely figures | Score figure layouts across acceptance-likelihood, Yves compatibility, and human/non-AI design | Exact full source not yet recovered |
| 3 | `panel-renderers/render-no-data-placeholder.py` | Figure 5 placeholder/NO DATA renderer | Render placeholders for experiments not yet done without fabricating data | Exact full source not yet recovered |
| 4 | `nature-aging-mockups/figure-5-layout-renderer.py` | Figure 5 rendering from PowerShell/Euler using uploaded Fig5 docs/PPT | Render Figure 5 mockup from existing panels and NO DATA placeholders, matching style of other panels | Exact full source not yet recovered |
| 5 | `panel-renderers/avoid-label-overlap-audit.py` | JM134/JM133 label-audit and rerender conversations | Audit plotted gene labels for completeness/overlap and preserve label counts | Exact full source not yet recovered |
| 6 | `nature-aging-mockups/render-synopsis-aligned-rnaseq-plots.py` | Euler script `scripts/28_make_synopsis_aligned_all_intron_RNAseq_plots.py`; output `28_SYNOPSIS_ALIGNED_ALL_INTRON_RNASEQ_PLOTS` | Render normal all-intron/all-gene RNA-seq panels required by the synopsis; may live under JM105 figures rather than generic rendering. | Full current source visible in project chat but not imported in this pass; next target. |
| 7 | `panel-renderers/render-figure2-panel-f-mud1-dependence.py` | Euler folders `PanelF_render_v7_TRANSPARENT_NO_BORDER_FOOTER_FIXED`, `PanelF_render_v8_FOOTER_SPACING_BEAUTIFUL`, and `PanelF_render_v9_TOP_DESCRIPTOR_SPACING_FIXED` under `Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE` | Render Figure 2F set-level Mud1-dependence panel with computed NMD-hidden IR, data-driven y-limits, transparent outputs, dedicated descriptor/footer axes, and separated x-tick/genotype/right-stat lanes | Exact final complete source not recovered in this pass; only patch sequence and lane contract were recovered, so do not reconstruct as code yet |

## Mockup/image-generation artifacts deliberately not committed as code

- The generated Figure 2–5 Nature Aging-style mockup PNGs from the recent image-generation round were not committed as runnable source.
- The prompts can be preserved later as prompt artifacts if needed, but generated PNGs are not canonical code and contain schematic/mock values rather than manuscript data.

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

1. Search old ChatGPT/project context by exact project names and figure numbers.
2. Search File Library and Drive for associated `.pptx`, `.docx`, `.py`, `.R`, `.ps1`, `.sh`, and generated-script artifacts.
3. Recover the latest complete code only.
4. Commit recovered code under human-purpose names, not chat/date names.
5. Keep obsolete or partial code out of the repo unless it is explicitly documented as deprecated reference material.

## Current continuation pass — 2026-07-08 figure-generation prompt/spec recovery

- Verified `jorddyk/Jordan-McCarthy` is private and writable with admin/push permissions.
- Searched available project memory/current conversation for the Figure 2 Panel F repair sequence and Figure 4 artifact-package workflow.
- Searched Google Drive for `Fig2 PanelF Mud1 dependence` and `Figure2 McCarthy`; no usable Drive source file was returned in this pass.
- Imported two exact prompt/spec artifacts from the current project chat:
  - `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md`
  - `projects/figure-rendering/prompts/figure-render-artifact-package-workflow.md`
- Did not commit the Figure 2F v7/v8/v9 patch code as runnable source because the available recovered material in this pass was a patch sequence that depended on prior scripts; the exact complete final script remains a recovery target.
- Updated `projects/figure-rendering/README.md`, this legacy backfill file, and the code wiki/addendum documentation.
