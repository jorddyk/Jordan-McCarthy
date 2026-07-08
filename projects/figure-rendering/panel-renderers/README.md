# Figure Panel Renderers

Reusable, source-preserved figure-panel rendering workflows. These scripts are kept here when their primary purpose is rendering/layout rather than biological discovery analysis.

## Imported canonical renderers

| Path | Purpose | Data status |
|---|---|---|
| `render-figure1ef-total-rrna-print.ps1` | Windows PowerShell orchestration that writes and runs the recovered Python renderer for JM105 Figure 1E/F content-only, print-typography panels. It renders transparent SVG/PNG/3x PNG and white-preview PNG outputs plus TSV/JSON audit files. | Uses real local JM105 total/rRNA-depleted source tables if present. No fake biological data. No poly-A data. Panel E uses raw +MUD1 NMD-off/upf1D retained-intron IR; Panel F uses an explicitly audited raw NMD-off set definition and does not claim off-minus-on NMD-hidden IR. |

## Rendering guardrails

- Use fixed canvas sizes and explicit axes geometry.
- Do not use `bbox_inches="tight"` in fixed-canvas renderers.
- Preserve editable SVG text with `plt.rcParams["svg.fonttype"] = "none"`.
- Do not silently change biological definitions to solve layout problems.
- Do not generate fake data. If input files are missing, fail rather than simulate.
- For JM105 Figure 2 and related figure-rendering work, do not introduce poly-A/P-versus-T/mRNA-like logic unless Jordan explicitly restores it.
