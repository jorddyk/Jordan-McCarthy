# JM105 Figure 3 Mud1/CR Panel Renderer

Publication-code area for JM105 Figure 3: “Mud1 is required for caloric restriction to suppress age-linked intron leakage.”

## Current status

The exact historical v21 source was recovered from the successful Euler run on 20 July 2026. The recovered pair is the proven raw/source-table parser and renderer lineage for the RNA panels:

```text
Figure_3_render_all_v21.py  2595f23d89c0b040d861f95d3b26139c1856eb00103625c05e4498d21d4de8a4
figure3_base_renderer.py     9a8e87fdccd5509eb33328a6177350e442078c78be3025721975f504d97ddce1
```

The earlier `Figure3_improved` run successfully assembled source-locked PowerPoint assets into a composite, but it did not rerender panel internals and is not the publication renderer.

The targeted `render_figure3_ADG_v22.py` renderer now uses the exact recovered v21 computation functions and changes only Panels A, D and G:

- A: graphical Cox proportional-hazards display from `JM100.xlsx`;
- D: correct quantitative-axis semantics and explicit condition-marker legend;
- G: data-driven limits showing all finite host-abundance observations.

## Current PowerPoint panel identities

- A: lifespan relevance;
- B: set-level Mud1 dependence;
- C: candidate-level comparison;
- D: candidate-by-candidate paired responses;
- E: ranking;
- F: representative examples;
- G: host RNA abundance control;
- H: cell-cycle control.

Historical v21 mapping remains:

```text
current C <- v21 A
current D <- v21 B
current E <- v21 C
current F <- v21 D
current G <- v21 E
```

## Targeted corrections

### Panel A

- Rerender from `JM100.xlsx`, sheet `Results`.
- Preserve four survival curves and exact cohorts.
- Replace the text-heavy statistics boxes with a colour-coded Cox forest display.
- Show WT CR versus WT 2%, mud1Δ CR versus mud1Δ 2%, and the CR × genotype interaction.
- Retain hazard ratios, 95% confidence intervals, p-values, group sizes, model note and source assumptions.

### Panel D

Horizontal position is measured quantitative NMD-hidden IR. It does not encode condition identity.

Recovered exact marker rule:

- **open circle = old 2% glucose**;
- **filled circle = old 0.1% glucose CR**;
- line = the same intron paired across conditions.

The targeted renderer removes the misleading positional `2%`/`CR` labels and adds numerical NMD-hidden IR scales.

### Panel G

The recovered v21 code proves that edge triangles represented observations outside a robust 96th-percentile display limit. The targeted renderer:

- retains the exact v21 host-abundance computation;
- shows all finite observations;
- uses a shared data-driven symmetric limit plus 8% padding;
- removes clipping triangles;
- writes a range audit documenting the old limit, formerly clipped count, full raw ranges and new limit.

Local recovered-source preflight found 402 finite pairs, 22 outside the prior limit, and zero points clipped in v22.

## Scientific/data contract

- Figure 3 RNA panels use real JM105 total/rRNA-depleted RNA-seq sources only.
- No poly-A, P-versus-T, mRNA-like or P−T data are loaded.
- No biological values are fabricated.
- `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`.
- `candidate_score = min(aging_effect, CR_suppression)`.
- Panel F contrast is computed (+MUD1 CR-suppression) versus (mud1Δ CR-suppression); Panel F is not recomputed by the A/D/G targeted renderer.
- Host RNA abundance is not protein abundance.

## Output contract

Each rerendered panel exports:

- transparent SVG with editable Arial-requested text;
- transparent PDF;
- transparent PNG;
- white-background preview PNG;
- plot-source and statistics/range audit TSV files.

Canvas dimensions are fixed. `bbox_inches="tight"` is not used. No information is removed to relieve crowding.

## Euler raw-mode inputs

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES/
/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES/JM105_replicate_stats_by_intron_condition.csv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv
```

`JM100.xlsx` is an execution input and is not stored in GitHub.

## Run

```bash
JOB_ID="$(sbatch --parsable render_figure3_ADG_v22.sbatch)"
echo "JOB_ID=${JOB_ID}"
```

A successful raw-mode run must end with:

```text
OUTPUT_VALIDATION=PASS
FIGURE3_ADG_V22_RENDER=PASS
OUTPUT_DIR=/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_ADG_v22_<timestamp>
```

## Publication-code rule

Only complete code that regenerates panel internals from the declared workbook/raw/source tables is publication-canonical. Composite-only scripts and failed intermediate patches remain provenance, not accepted paper code.
