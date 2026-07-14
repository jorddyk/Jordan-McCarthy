# Figure Rendering Reliability Standard

Status: mandatory for every manuscript figure and panel rendered in this repository.

This standard applies to JM105, Intronsaurus, Nature Aging figures, adjacent JM132/JM133/JM134 work, and any later figure project that uses PowerPoint, Excel, Euler, Python, R, Bash, or PowerShell. It exists because a figure can be biologically correct yet still waste time if panel identity drifts, source schemas are guessed, the code has not been executed in the target environment, or the final render contains clipping and overlap.

## Definition of done

A figure-rendering response is complete only when all of the following are true:

1. The requested panel identities are locked to the current authoritative PowerPoint/composite and the current Google Drive acceptance matrix.
2. Every requested panel is rendered. A request for a complete figure means all panels, not a convenient subset.
3. Source files, sheet names, tables, required columns, row counts, cohort counts, aliases, and renderer CLI arguments are verified before rendering.
4. The exact PowerShell, Bash, and Python files have passed syntax checks.
5. The renderer has run in the exact target Euler environment, not only locally.
6. The final target-environment render has passed the hard collision gate using the font actually resolved on Euler.
7. Transparent SVG/PDF/PNG, white preview PNG, source tables, manifest, lane map, collision inventory, and audit files exist and are non-empty.
8. The same response includes the exact Windows retrieval command or runner and verifies the downloaded files before printing success.
9. The user has been shown the white preview or contact sheet. Transparent PNGs are never judged in a black-background viewer.
10. Success is reported only after the complete end-to-end route has succeeded: Windows source/export -> upload -> Euler render -> output verification -> direct retrieval -> local verification -> preview open.

Local preflight is useful but is not acceptance.

## Mandatory pre-code locks

### Panel identity lock

Record for every panel:

- requested figure/panel;
- authoritative composite/deck and slide;
- biological job;
- source data file/table;
- source status: data source, accepted visual reference, starting point, or final accepted panel;
- aspect ratio and intended composite slot;
- text supplied externally by the composite;
- allowed and forbidden data subsets;
- forbidden substitutions.

A renderer may not replace a survival panel with a design schematic, reduce a four-quadrant panel to a simplified inset, or change any other panel type without explicit approval.

### Full-scope lock

Write the requested panel list before code. If the user asks for Figure N, the default scope is every panel in Figure N. A staged subset requires explicit authorization.

### Source/schema lock

Before writing plotting logic, record:

- exact path;
- file type;
- workbook sheet or table name;
- raw versus enriched table status;
- delimiter;
- required columns;
- row count after parsing;
- biological unit represented by each row;
- expected group/cohort counts;
- alias columns and name-resolution method;
- CLI signature of any recovered renderer.

Do not infer enriched aliases such as `standard_gene_name` or `systematic_orf` from a raw table that only contains `display_gene` or `systematic_gene`. Normalize explicitly or use a declared enriched source.

### Excel rule

Excel `UsedRange` is only a scan boundary. It is never a biological row count. Blank formatted rows must be removed using required biological fields; partially populated rows must hard-fail with the worksheet row number. Parsed record counts and group counts must be validated before upload.

## Lane and collision contract

Before code, assign every visible object to exactly one lane:

- descriptor/title;
- plot;
- label;
- legend;
- x-tick;
- group label;
- right-stat;
- footer.

Before patching, enumerate exact collision pairs and the geometric resolution. No object may be dropped merely to relieve crowding.

Legends must not float over data unless the collision audit proves zero intersection and the accepted reference intentionally uses that placement. The default is a dedicated legend lane.

## Hard collision gate

A panel cannot be accepted from visual intuition or planned coordinates. After the final draw, the renderer must measure the actual rendered objects and stop when any of these occur:

- text extends outside the fixed figure canvas;
- text bounding boxes overlap beyond the declared tolerance;
- legend bounds intersect plotted data or required labels;
- data points intersect direct-label boxes;
- axis titles collide with ticks, adjacent panels, labels, statistics, or footers;
- subplot titles collide with neighboring tick labels;
- visible systematic ORF identifiers appear where common names are required;
- required objects are absent;
- the occupied design footprint is implausibly small relative to the canvas.

The gate must inspect the final renderer/figure, not merely the lane specification. A report of zero collisions is invalid if the preview visibly overlaps.

## Cross-font rule

Font metrics are part of the layout. Before delivery:

1. record the requested font and the actually resolved font;
2. render using the font available in the target Euler environment;
3. also test at least one expected fallback when the requested font is unavailable;
4. run the full collision gate for each tested font;
5. prefer fixed manual legend rows and fixed label slots over width-sensitive automatic legend layouts.

A local Liberation Sans pass does not predict a DejaVu Sans pass. The target-environment render is authoritative.

## PowerShell and Euler preflight

### PowerShell

- Run the PowerShell parser on the exact `.ps1` before delivery.
- Brace a variable when punctuation immediately follows it: `${Row}:`, not `$Row:`.
- Do not rely on changing execution policy. Use `Unblock-File` for downloaded scripts when required.
- Do not execute from `C:\WINDOWS\system32`; set a user-owned working directory.
- Verify every downloaded/extracted file actually exists before running it.
- Never print success after a failed external command.

### Bash/Euler

- Run `bash -n` on the exact shell file.
- Run `python3 -m py_compile` on the exact Python file.
- Load the known Euler module/environment before imports.
- Inspect each recovered renderer's actual CLI/usage and pass all positional or named arguments.
- Do not move legacy scripts if they use `__file__`-relative paths unless all paths are normalized.
- Do not nest `ssh` after the prompt already shows an Euler login node.
- Avoid giant interactive paste blocks when a small uploaded script is safer.

### Workflow

Prefer the least complicated proven route:

1. validate source locally;
2. upload exact source and exact scripts;
3. render on Euler;
4. verify outputs on Euler;
5. retrieve the complete output with direct `scp -r`;
6. verify locally;
7. open the white preview.

Do not add tar/ZIP/archive/extraction layers unless there is a demonstrated transfer problem that requires them.

## Failure handling

When a run fails:

1. classify the exact failure: execution policy, parsing, source path, source schema, CLI, dependency/environment, rendering, collision gate, serialization, retrieval, or local verification;
2. preserve the remote run directory and log;
3. patch only the exact failing stage;
4. resume the existing run when possible;
5. do not rewrite unrelated panels or create another wrapper layer;
6. do not claim a path or artifact exists until verified;
7. record the failure and proven fix in GitHub and the Drive Action Log.

## Required output and retrieval contract

Every successful render response must provide:

- complete runnable renderer/package;
- exact Euler output path;
- exact PowerShell retrieval block or runner;
- local destination path;
- local existence and non-empty checks for every panel's SVG/PDF/PNG/preview;
- local existence check for contact sheet and audit;
- automatic opening of the white preview and output directory;
- no success message until all checks pass.

## Canonical successful example

The first complete workflow to satisfy these rules in the 2026-07-14 incident was JM105 Figure 2 v4.1:

- all six panels rendered;
- panel identity preserved;
- real Panel A workbook source;
- enriched strict source schema used deliberately;
- Panel E source preserved from the accepted vector panel;
- dedicated lanes repaired visible overlaps;
- hard post-draw collision gate;
- Liberation Sans and DejaVu Sans full-render tests;
- resume-in-place repair of the failed Euler run;
- direct retrieval and local verification.

Use the canonical v4.1 renderer folder as an implementation reference, not as permission to reuse Figure 2 biology in another figure.