# ChatGPT JM105 Figure Rendering Operating Standard

Purpose: persistent project rulebook for future ChatGPT sessions that render JM105/Intronsaurus/Nature Aging figure panels. This file exists because Jordan repeatedly had to restate the same requirements after failed render attempts: complete runnable PowerShell/Euler code, real data provenance, source discovery before plotting, large text, fixed lanes, no clipping, and proper artifact outputs.

Scope: all JM105 / Intronsaurus / Nature Aging figure-panel rendering work in this repository. Treat this as an allowlist-style operating contract, not a suggestion list.

## Closed criticism ledger

| Repeated criticism from Jordan | Permanent implementation rule |
|---|---|
| “Give me PowerShell and Euler code.” | Every rendering task must provide either one no-prompt PowerShell runner that installs/runs the Euler code, or a direct Euler block plus retrieval command. Do not provide only Python unless explicitly requested. |
| “No, give me code I can copy and paste.” | Provide one complete runnable block or downloadable runnable package. No fragments, no “same as above,” no placeholders. |
| “Why did it not render anything?” | Rendering may only run after input TSV validation succeeds. If the data TSV is missing, write a failure audit and stop; do not call the renderer. |
| “Maybe see which files are actually on Euler.” | Always run source discovery / manifest before assuming Euler paths. Do not guess `07_primary_intron_analysis` or any old path unless verified in the current run. |
| “Which files is Intronsaurus actually using?” | For Intronsaurus-derived panels, first inventory source scripts/tables and write a source manifest listing table path, columns, row count, and selected panel input table. |
| “This is too small / text is unreadable.” | Default final-equivalent text should start around 8.5–9 pt for dense labels and not be shrunk below readability to solve collisions. Solve collisions with lanes, canvas geometry, direct labeling, or label omission only when scientifically nonessential and documented. |
| “Do not use bbox_inches='tight'.” | Final render scripts must not contain `bbox_inches='tight'`. Fixed canvas dimensions must be declared as constants. |
| “SVG text must stay editable.” | Set `matplotlib.rcParams['svg.fonttype']='none'`, `pdf.fonttype=42`, `ps.fonttype=42`; request Arial or nearest sans-serif. |
| “I need SVG/PDF/PNG plus preview.” | Required outputs: transparent SVG, transparent PDF, transparent PNG, white-background preview PNG, source TSV, manifest, and render audit. |
| “You are playing layout whack-a-mole.” | Emit lane map before code and collision inventory before patching. Patch exact named collisions by reallocating lane geometry, not random nudges. |
| “It has too much white space / does not fill the canvas.” | The occupied plot/design footprint must be audited against the declared canvas. Use the panel canvas efficiently while preserving aspect ratio and lanes. |
| “Preserve panel aspect ratios.” | Existing rendered/PPT panel aspect ratios are constraints unless Jordan explicitly allows shrinking. Mud1-deck panels may be shrinkable only when explicitly stated. |
| “This looks AI-generated.” | Figure titles/panels must use human manuscript wording: claim-first, concise, Yves-compatible, and Nature Aging-style. Avoid generic labels like “state-space” unless the manuscript actually argues that. |
| “No fake data.” | No simulated biology. If a data source is missing, write `NO DATA` or fail with an audit. Do not fabricate a panel to satisfy the render. |
| “Figure 2 must not use poly-A/P-vs-T/mRNA-like/P−T.” | For JM105 Figure 2 and adjacent candidate-gate panels, only touch total/rRNA-depleted JM105 data unless Jordan explicitly reverses this. Enforce by allowlisting the allowed subset, not by post-hoc exclusion. |
| “Distinguish NMD-off from NMD-hidden.” | Do not call a value NMD-hidden unless computed as `IR(upf1Δ) - IR(UPF1+)` matched by intron, age, glucose, genotype, capture. Raw NMD-off/upf1Δ IR must be labeled raw NMD-off. |
| “Panel F lanes overlap.” | x-ticks, genotype/group labels, right-stat text, and footer must occupy separate lanes. y-limits must be data-driven for computed Panel F contrast. |
| “PowerShell failed because of execution policy / system32 / CRLF.” | Prefer paste-in PowerShell blocks over unsigned `.ps1` when possible; set working directory under `C:\Users\jmccarthy\Downloads\...`; convert CRLF to LF before `sbatch`; do not write under `C:\WINDOWS\system32`. |
| “The job failed but the script kept going.” | Every runner must fail-fast on missing TSVs/log errors and print exact log paths. Never print success paths for nonexistent files. |
| “This should have been found from previous successful chats.” | Before new rendering code, inspect existing repo contracts under `projects/figure-rendering/` and relevant recovered previous runs; reuse harness rules rather than inventing a one-off. |

## Mandatory sequence for future ChatGPT figure-panel rendering

1. **Recover prior constraints first.** Read this standard plus `figure-panel-generation-lane-audit-contract.md` before writing renderer code.
2. **State the biological job in one sentence.** Include exact metric definitions and forbidden data subsets.
3. **Emit lane map.** Every object gets exactly one lane.
4. **Emit collision inventory.** Name exact likely collisions and geometry resolutions.
5. **Discover data sources.** On Euler, inventory candidate source tables/scripts and write `source_manifest.tsv` before deriving panel TSV.
6. **Build panel TSV.** Validate required columns and write `panel_input.tsv`; stop if absent.
7. **Render only after validation.** Generate fixed-canvas transparent SVG/PDF/PNG plus white preview.
8. **Audit outputs.** Write text clipping/overlap audit, manifest, run summary, transparency check, and `DATA_CHANGED=False` unless intentionally modified.
9. **Retrieve outputs.** PowerShell runner copies the entire output folder to a user-owned Windows directory and prints the exact files to open.
10. **If failure occurs, classify it.** Data discovery, data coverage, syntax, scheduler, renderer, serialization, or retrieval. Do not guess.

## Required constants/comments in figure code where applicable

```text
NMD_hidden = IR(upf1Δ) - IR(UPF1+)
candidate_score = min(aging_effect, CR_suppression)
Panel F contrast = computed (+MUD1 CR-suppression) vs (mud1Δ CR-suppression); y-limits data-driven from computed values, not hardcoded.
Figure 2 data subset = total/rRNA-depleted JM105 only; no poly-A, P-versus-T, mRNA-like, or P−T construct data.
```

## Minimum render contract

- Declared fixed canvas dimensions.
- No `bbox_inches='tight'` in final code.
- Editable SVG text.
- Transparent SVG/PDF/PNG outputs.
- White preview PNG only as preview.
- Complete runnable code: imports, entry point, no undefined variables, no placeholders.
- Euler and PowerShell compatibility.
- Source manifest and run audit.
- Output existence checks before success message.

## Default output folder convention

Use a new user-owned folder per run:

```text
C:\Users\jmccarthy\Downloads\<project_or_panel>_<timestamp_or_version>\
```

Remote Euler folders should be under either:

```text
/cluster/home/jmccarthy/<panel_run_name>/
/cluster/scratch/jmccarthy/JM105_RNAseq/<analysis_run_name>/
```

Do not use `C:\WINDOWS\system32` as a work directory.
