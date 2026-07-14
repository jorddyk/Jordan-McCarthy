# Known working renderer starting points

This file is an anti-drift index for renderer code in this repository that actually rendered figure outputs successfully, or is marked as canonical infrastructure for doing so. New figure work should start by inspecting these files before inventing a new one-off script.

## Why this exists

The JM105 / Intronsaurus figure work has repeatedly lost time to fragile one-off renderers, bad heredocs, missing source discovery, clipped labels, and PowerShell/Euler transfer mistakes. The purpose of this file is to point future chats to working implementation patterns that can be adapted across figures.

Do not copy a biological metric blindly. Copy the **engineering pattern**: source validation, local PowerShell runner, remote Euler runner, fail-fast behavior, fixed canvas, output retrieval, audit tables, and explicit panel identity comments.

## Known working / canonical renderer references

### 1. JM132 Figure 3H cell-cycle renderer

Path:

```text
projects/figure-rendering/panel-renderers/jm132-cell-cycle-fig3h/run_jm132_fig3h_g_column_10min_y400.ps1
```

Why it is useful:

- It is a complete paste-and-run PowerShell launcher.
- It writes an embedded Python renderer and shell runner.
- It uploads inputs to Euler and runs remotely.
- It encodes panel identity and source-status comments at the top of the Python payload.
- It parses a real measured Excel workbook instead of assuming a precomputed table.
- It exports audit tables describing exactly how source rows became plotted records.
- It uses explicit fixed-canvas constants.
- It fails with named errors instead of silently producing empty plots.

Use it as a starting point for other figures when a panel needs:

- robust source parsing from a nontrivial local file;
- an end-to-end PowerShell to Euler workflow;
- row/record-level audit outputs;
- explicit panel identity locks;
- reproducible plot generation from measured source data.

Do **not** copy its biological assumptions into RNA-seq figures. Its biological metric is JM132 cell-cycle interval length, not JM105 intron retention.

### 2. JM105 rendering harness

Paths:

```text
projects/figure-rendering/panel-renderers/jm105-rendering-harness/README.md
projects/figure-rendering/panel-renderers/jm105-rendering-harness/jm105_source_inventory.py
projects/figure-rendering/panel-renderers/jm105-rendering-harness/run-jm105-source-inventory-from-windows.ps1
```

Why it is useful:

- It is the canonical source-discovery pattern for JM105/Intronsaurus rendering.
- It prevents guessing old paths.
- It inventories tables before plotting.
- It is especially important before Figure 2, Figure 3, Figure 4, or Figure 5 rendering, where multiple historical outputs can contain similarly named metrics.

Use it as a starting point when a figure needs:

- source discovery across `/cluster/scratch/jmccarthy/JM105_RNAseq`;
- column/header inventory;
- source manifest generation;
- fail-fast source selection.

### 3. Figure 4 and other canonical renderers listed in the figure-rendering README

Path:

```text
projects/figure-rendering/README.md
```

The README lists currently canonical or partially recovered renderers, including Figure 1E/F, Figure 4E, Figure 4B/C, Figure 4 secondary structure/accessibility, and JM105 rendering harness entries.

Use this README before starting a new figure to avoid duplicating or contradicting already recovered code.

## How this helps with Figure 3 next

Figure 3 should not begin from a blank script. The new chat should:

1. Read this file.
2. Read `projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md`.
3. Search GitHub for Figure 3 / Mud1 / CR_suppression / mud1D / panel-renderers.
4. Use the JM105 rendering harness/source-inventory pattern to locate Figure 3 input tables.
5. Use the JM132 successful PowerShell/Euler structure as the engineering template for the runner.
6. Only then write Figure 3-specific code.

## Non-negotiable adaptation rule

Working code is a starting point, not a permission to drift.

For a new figure, always replace:

- biological metric definitions;
- input source paths;
- panel identity lock;
- lane map;
- collision inventory;
- labels and public-facing terms;
- audit tables;
- output file names.

Never reuse a working renderer by changing only the title.
