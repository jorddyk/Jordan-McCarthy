# JM105 Figure 3 Mud1/CR Panel Renderer

Recovered canonical renderer area for JM105 Figure 3: “Mud1 is required for full caloric restriction suppression of selected retained introns.”

## Current status

The historical v21 renderer remains the proven raw/source-table renderer for the RNA panels. The exact Python pair is present on Euler but is not yet committed to this folder. The 20 July 2026 `Figure3_improved` run successfully assembled source-locked PowerPoint assets into a composite, but it did **not** rerender panel internals and is therefore not the publication-canonical improved renderer.

Do not describe an asset-only composite as a panel rerender.

## Figure Acceptance Matrix

The authoritative panel-by-panel planning artifact is the Google Sheet `JM105 Intronsaurus Figure Acceptance Matrix`. For Figure 3 it locks the claims, source families, vocabulary and next action for A–H. It is a decision/provenance matrix, not a substitute for raw-data inspection or exact renderer source.

The current PowerPoint panel identities are:

- A: lifespan relevance;
- B: set-level Mud1 dependence;
- C: candidate-level comparison;
- D: candidate-by-candidate paired responses;
- E: ranking;
- F: representative examples;
- G: host RNA abundance control;
- H: cell-cycle control.

## Immediate panel corrections under review

### Panel A

Rerender from `JM100.xlsx`. Replace the text-heavy `Key tests` and `Interaction` boxes with a graphical, colour-coded hazard-ratio display. Retain WT CR versus WT 2%, mud1Δ CR versus mud1Δ 2%, the CR-by-genotype interaction, exact sample sizes and exact p-values.

### Panel D

The x coordinate is a quantitative NMD-hidden IR value. Left/right position is not condition identity. Remove categorical `2%` and `CR` x-axis labels. Add an explicit marker legend: filled circle = old 2% glucose; open circle = old CR; line = the same intron connected across conditions.

### Panel G

The current triangles must not be interpreted or redrawn from the image alone. Recover `Figure_3E_plot_source.tsv`, `Figure_3E_statistics_audit.tsv`, the exact v21 code and the raw JM105 source chain. Determine whether the triangles are deliberate out-of-range indicators. The default rerender should show every finite point with data-driven x/y limits and padding.

## Source clue

The final accepted large-text historical v21 run on Euler was:

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

| File | Purpose | Status |
|---|---|---|
| `figure3_base_renderer.py` | Shared v21 renderer utilities, data loading, audit/output helpers and panel functions. | Exact source located on Euler; not yet committed. |
| `Figure_3_render_all_v21.py` | Final v21 orchestration script for rendering and auditing Figure 3 panels. | Exact source located on Euler; not yet committed. |
| `run_figure3_v21_on_euler.sh` | Historical Euler runner. | Canonical existing launcher. |
| `recover-figure3-v21-and-provenance.sh` | Recover exact v21 source bytes, successful plot-source tables, audits and raw-source hashes into one archive. | Added on branch `agent/canonicalize-jm105-figure3-improved-renderer`. |
| `prepare-figure3-assets-from-pptx.py` | Extract current panel assets from `Fig3_McCarthy.pptx`. | Assembly/provenance utility only; not a raw-data renderer. |

## Expected real-data inputs on Euler

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_gate_passed.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES/JM105_replicate_stats_by_intron_condition.csv
/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES/JM105_primary53_intron_EI_IE_EE_counts_LONG.csv
/cluster/scratch/jmccarthy/JM105_RNAseq/162_FIG1EF_EXACT_RAW_FILES/JM105_rebuilt_annotation_sample_audit_FIXED.tsv
```

## Scientific/data status

- Uses real JM105 total/rRNA-depleted RNA-seq summary or raw count tables.
- Does not use poly-A, P-versus-T, mRNA-like or P−T construct data.
- Does not fabricate biological data.
- `NMD_hidden = IR(upf1Δ) − IR(UPF1+)`.
- `candidate_score = min(aging_effect, CR_suppression)`.
- Panel F contrast is computed (+MUD1 CR-suppression) versus (mud1Δ CR-suppression).
- Host RNA abundance must not be called protein abundance.
- SVG/PDF text remains editable text.
- Fixed-canvas export contract: transparent SVG/PDF/PNG plus white-background preview PNG for every panel and the composite.
- `bbox_inches="tight"` is not used.

## Source recovery on Euler

```bash
bash recover-figure3-v21-and-provenance.sh
```

The script prints `RECOVERY_ARCHIVE=...`. That archive is the required input for the next raw-grounded A/D/G renderer patch.

## Publication-code rule

Only a complete renderer that regenerates panel internals from the declared workbook/raw/source tables can become publication-canonical. Composite-only scripts and failed intermediate patches remain provenance, not the accepted paper code.
