# JM105 Figure 2 rendering incident: complete failure and recovery record

Date: 2026-07-14
Final successful workflow: Figure 2 v4.1

## Outcome

The final v4.1 workflow completed successfully on Euler and downloaded the six rendered panels to Windows. Earlier attempts wasted substantial time because they combined unverified source assumptions, panel-identity drift, incomplete scope, wrapper failures, ineffective visual audits, and environment-specific font differences.

This document records every material failure and the proven correction so later figure chats do not rediscover them.

## Failure chronology

| Failure | What happened | Why it was unacceptable | Proven correction |
|---|---|---|---|
| Panel identity drift | Panel A was replaced by an experimental-design schematic although the current PowerPoint defined A as a lifespan panel. Panel C was simplified away from the full four-quadrant explanation. | The renderer changed the biological job of the panels. | Lock identity from the current composite, acceptance matrix, source deck, and metric before code. Panel A used `Panel2A_Jm104_AnalysisJordan.xlsx`; C retained the full quadrant structure. |
| Incomplete figure scope | Only A, B, and C were rendered after a request to rerender Figure 2. | A full-figure request was silently converted into a convenient subset. | Write the A-F scope lock first and fail if any requested panel output is absent. |
| Missing retrieval instructions | Render responses omitted the exact PowerShell command to download and open the panels. | A remote render is not a delivered artifact. | The same response must include direct `scp -r`, local verification, and preview opening. |
| Unsigned PowerShell script | The downloaded `.ps1` was blocked under enforced `RemoteSigned`. | The script never started. | Use `Unblock-File`; do not repeatedly attempt to override institutional execution policy. Prefer direct Euler when practical. |
| Nonexistent downloaded filename/path | A corrected filename was given before the file existed locally. | The user was instructed to run a path that could not exist. | Discover the actual downloaded file with `Get-ChildItem`, verify it, then run it. Never infer local existence. |
| Archive/extraction overengineering | Tar/ZIP/extraction layers failed and downstream commands printed false completion. | Added failure surfaces and misleading success. | Use direct `scp -r` unless a transfer limitation specifically requires an archive. Fail immediately after external-command errors. |
| Legacy tight-crop preflight failure | Recovered scripts contained `bbox_inches='tight'`, and the wrapper stopped without creating a patched executable copy. | A known legacy defect was treated as an unrecoverable run failure. | Copy and patch the run-specific script, preserve the original, then AST-audit actual `savefig()` calls. |
| Raw-text audit false positive | The audit matched a documentation sentence containing the forbidden text. | The audit failed on a statement saying the option was absent. | Audit Python semantics with AST, not raw substring search. |
| Moved-script path risk | Legacy renderers were run from a different directory even though they used `__file__`-relative paths. | Source lookup behavior changed. | Run a temporary patched copy in the original renderer directory or normalize paths explicitly. |
| Nested SSH | The user was already on Euler and was told to SSH to Euler again. | Unnecessary friction and confusion. | Detect the current prompt/context and use direct Euler commands when already connected. |
| Giant pasted shell block | A long interactive paste was mangled. | Interactive transport became another source of syntax corruption. | Upload a checked shell file or use a small, focused command. |
| Missing CLI arguments | A recovered renderer requiring `<STRICT_ROOT> <OUTDIR>` was launched with no arguments. | The launcher did not inspect the renderer's usage. | Inspect CLI/usage before execution; run one renderer at a time until outputs are confirmed. |
| Name-audit bug | An audit omitted `standard_gene_name` and incorrectly claimed common labels did not match. | The audit contradicted the actual schema and undermined trust. | Include all resolved alias fields; inspect actual visible SVG text separately from provenance columns. |
| Candidate-count terminology error | Threshold-passing rows were confused with the complete strict selected set. | Different gates were conflated. | Name each count by its exact predicate and export the predicate columns. |
| Excel `UsedRange` error | Formatting extended two blank rows, so the runner exported 152 rows instead of 150. | Excel layout metadata was mistaken for biological data. | Use `UsedRange` only as a scan boundary; filter fully blank required fields, fail on partial rows, and validate parsed group counts. |
| PowerShell `$Row:` parser error | Two error strings used `$Row:` instead of `${Row}:`. | The script failed before execution. | Parse the exact `.ps1` before delivery and brace variables followed by punctuation. |
| Raw/enriched schema mismatch | The renderer required `standard_gene_name` and `systematic_orf`, but the selected raw table had `display_gene` and `systematic_gene`. | Local testing used a different schema from Euler. | Declare raw versus enriched status, validate required columns, normalize aliases or use the confirmed enriched 284-row source. |
| Panel A/B/C/D/E/F visible overlaps | The generated panels had legend-data overlap, axis-label spill, text collisions, oversized points, merged points, column spill, subplot-title/tick collisions, and a mangled gate panel. | The output was a downgrade from the PowerPoint and visibly unpublishable. | Rebuild geometry from dedicated lanes, smaller B points/thinner axes, fixed label slots, restored C/F visual identity, widened D columns, and separated E legend/tick/title lanes. |
| False clean audit | The audit reported zero overlaps despite obvious visible collisions. | It measured an inadequate representation rather than the final rendered objects. | Run a post-draw hard gate on actual text extents, label boxes, plotted points, legend bounds, clipping, and visible systematic IDs. |
| Font mismatch | Local validation used Liberation Sans; Euler resolved DejaVu Sans. The wider DejaVu legend clipped in Panel A and the hard gate stopped v4. | The code was not tested in the target environment/font. | v4.1 uses fixed two-row legends and was rendered completely under both Liberation Sans and DejaVu Sans before delivery. Record actual resolved font. |
| Restarting instead of resuming | Multiple fresh wrappers and run directories were created after isolated failures. | Increased time, password prompts, and failure opportunities. | Preserve the failed remote directory and use a resume-in-place repair when inputs are already uploaded. |

## What finally worked

1. The current PowerPoint/composite was treated as the panel-identity baseline.
2. The Google Drive acceptance matrix supplied the required changes but was not allowed to silently change panel type.
3. Panel A used the verified JM104 workbook source: 150 cells; 52 control; 98 CR; log-rank p approximately 5.50e-04.
4. B/D/F used the declared enriched 284-row strict source with common-name aliases and exact gate columns.
5. Panel E used the accepted PowerPoint SVG vector source rather than simulated values.
6. Every panel had a fixed lane map and explicit collision inventory.
7. The renderer used fixed canvases, no automatic tight crop, editable SVG text, and complete output formats.
8. The hard collision gate measured the final rendered objects and failed closed.
9. The complete A-F renderer was tested under Liberation Sans and DejaVu Sans.
10. The failed v4 Euler run was repaired in place with the v4.1 payload.
11. The PowerShell runner uploaded, rendered, retrieved with direct `scp -r`, verified every panel file, checked the audit pass text, and opened the white contact sheet.
12. The user confirmed the v4.1 workflow worked.

## Required behavior in future new chats

- Read the project `START_HERE_FOR_FIGURE_RENDERING.md`, `AGENTS.md`, and reliability standard before writing code.
- Search the repository for an accepted renderer and source lock before inventing one.
- Treat a full-figure request as all panels.
- Never change panel identity without explicit approval.
- Validate source schema and exact target environment before delivery.
- Produce a real target-environment render in every rendering response, not only code.
- Include retrieval instructions in the same response.
- Record every meaningful failure and successful correction in the Drive Action Log and GitHub.
- Commit only the accepted canonical renderer, not the failed intermediates.