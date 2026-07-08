# JM105 Rendering Harness

Purpose: reusable harness layer for JM105/Intronsaurus figure panels so each panel does not need to reinvent source discovery, Euler execution, PowerShell retrieval, lane maps, text-size rules, and output audits.

This folder is implementation infrastructure. It contains no raw sequencing data and is not itself a biological result.

## What this harness closes

- Guessing current Euler data paths.
- Rendering after the panel TSV failed to build.
- Dependence on unsigned local script files when a paste-in PowerShell block is safer.
- Accidental local output under `C:\WINDOWS\system32`.
- CRLF sbatch rejection.
- Tiny text as the first collision solution.
- Missing SVG/PDF/PNG/preview outputs.
- Success messages for missing files.
- Confusion between raw NMD-off and NMD-hidden off-minus-on.

## Standard harness phases

### Phase 0: Project-standard preflight

Read these before writing panel code:

- `projects/figure-rendering/templates/chatgpt-jm105-rendering-operating-standard.md`
- `projects/figure-rendering/prompts/figure-panel-generation-lane-audit-contract.md`

Then emit the lane map and collision inventory before code.

### Phase 1: Euler source discovery

A panel run must first write:

```text
source_manifest.tsv
candidate_table_inventory.tsv
candidate_source_script_hits.tsv
```

The manifest must identify the actual table/script used for panel values. For Intronsaurus-derived panels, inspect current `/cluster/scratch/jmccarthy/JM105_RNAseq` files rather than assuming old paths.

### Phase 2: Panel TSV derivation

Every renderer consumes a checked TSV, normally:

```text
panel_input.tsv
```

The derivation script must also write:

```text
panel_input_schema.tsv
panel_input_validation.tsv
run_summary.txt
```

If the input table cannot be built, stop here and write:

```text
NO_RENDER_DUE_TO_DATA_SOURCE_FAILURE.txt
```

### Phase 3: Rendering

Render only after `panel_input.tsv` passes validation.

Required outputs:

```text
<panel>.svg
<panel>.pdf
<panel>.png
<panel>_white_preview.png
text_layout_audit.tsv
text_overlap_audit.tsv
render_manifest.tsv
run_summary.txt
```

### Phase 4: Retrieval

The PowerShell runner retrieves the complete remote output directory to a user-owned local folder and prints exact files to inspect.

## Default style constants

```python
CANVAS_MM = (180.0, 118.0)
DPI = 300
FONT_FAMILY = "Arial"
MIN_BODY_PT = 8.5
MIN_LABEL_PT = 7.5
```

```python
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
```

Final code must not contain `bbox_inches="tight"`.

## Failure taxonomy

Every failure must be classified as one of:

- `source_discovery_failure`
- `data_coverage_failure`
- `schema_validation_failure`
- `syntax_or_dependency_failure`
- `scheduler_failure`
- `rendering_failure`
- `serialization_failure`
- `retrieval_failure`

Patch only the failure class that actually occurred.

## JM105 biological guardrails

- No fake data.
- Use `NO DATA` for missing experiments.
- NMD-hidden means `IR(upf1Δ) - IR(UPF1+)`, matched by intron/age/glucose/genotype/capture.
- Raw NMD-off/upf1Δ IR is not NMD-hidden.
- Figure 2 uses only total/rRNA-depleted JM105 unless Jordan explicitly changes it.
- Do not introduce poly-A, P-versus-T, mRNA-like, or P−T logic into Figure 2.
- Panel F Mud1 contrast must be computed from +MUD1 and mud1Δ CR suppression; y-limits are data-driven.

## Human response contract

When asked to render a JM105 panel, do not begin with a speculative plot. Close these steps in order:

1. Prior-constraint recovery.
2. Lane map.
3. Collision inventory.
4. Source discovery or verified source paths.
5. One complete runnable code package/block.
6. Output audit and exact retrieval/open commands.

If source discovery fails, the answer is not a render; it is the source manifest and the exact missing condition/table problem.
