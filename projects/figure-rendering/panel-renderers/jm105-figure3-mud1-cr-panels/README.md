# JM105 Figure 3 Mud1/CR Panel Renderer

Recovered canonical renderer for JM105 Figure 3: “Mud1 is required for full caloric restriction suppression of selected retained introns.”

## Source clue

Recovered from the JM105 Figure 3 rendering/debugging chat. The final accepted large-text run on Euler was:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316
```

That run reported:

```text
TEXT_OVERLAPS_TOTAL=0
TEXT_CLIPPED_TOTAL=0
B/C gene labels = 8.5 pt
B/C ticks = 8.0 pt
B/C axis title = 9.0 pt
D gene labels = 8.5 pt
D ticks = 8.0 pt
D axis title = 9.0 pt
APPROVED_SYSTEMATIC_FALLBACK_LABELS=3
UNAPPROVED_SYSTEMATIC_LABELS=0
```

## Files

| File | Purpose |
|---|---|
| `figure3_base_renderer.py` | Shared renderer utilities, data loading, audit/output helpers, and panel functions from the recovered v21 package. |
| `Figure_3_render_all_v21.py` | Final v21 orchestration script for rendering and auditing Figure 3 panels. |
| `run_figure3_v21_on_euler.sh` | Euler runner that creates a timestamped run directory, copies the renderer, prechecks inputs, and submits the Slurm job. |

## Expected real-data inputs on Euler

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/101_INTRONSAURUS_LEAKAGE_FIRST_EXPRESSION_FIXED/tables/JM105_replicate_stats_by_intron_condition.csv
```

## Scientific/data status

- Uses real JM105 total/rRNA-depleted RNA-seq summary tables.
- Does not use poly-A, P-versus-T, mRNA-like, or P−T construct data.
- Does not fabricate biological data.
- Systematic ORF fallbacks are allowed only when common names are missing and are audited.
- SVG/PDF text is configured to remain editable text.
- Fixed-canvas export contract: transparent SVG/PDF/PNG plus white preview PNG.
- `bbox_inches="tight"` is not used.

## Run

On Euler, from this directory:

```bash
bash run_figure3_v21_on_euler.sh
```

The script prints the `RUN_DIR` and `JOBID`.
