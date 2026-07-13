# JM105 Figure 4G secondary-structure accessibility

Purpose: preserve the reusable code and lessons from the 2026-07-13 Figure 4G development pass. This folder intentionally stores **rendering code, source-discovery logic, provenance notes, and failure lessons**, not rendered figure images.

## Panel identity lock

```text
requested_panel: Figure 4G
source_deck_or_doc: Figure 4 composite / updated Figure 4 manuscript spec
source_status: newly added explanatory/control panel, not a replacement for B/C/E/F
current_authoritative_spec: Mud1-dependent CR protection is enriched in architecturally demanding introns
biological_metric: predicted splice-signal accessibility / folding proxy for locked Figure 4 intron groups
allowed_data_subset: total/rRNA-depleted JM105-derived Figure 2/4 tables only
forbidden_substitutions: poly-A, P-versus-T, mRNA-like, P−T constructs, broad Figure 2 candidate_passed as selected set
```

## Canonical current visual

Final accepted visual direction as of 2026-07-13:

- individual introns shown as small, semi-transparent dots;
- larger outlined dots show group medians;
- horizontal bars show IQR;
- groups are ordered to match the legend: **Background → Aging-only → Mud1/CR**;
- metrics are displayed on a within-metric percentile scale so accessibility and folding-strength metrics can share one axis;
- exact raw RNAlib values, Mann-Whitney statistics, q-values, and point positions are exported as TSVs.

The final panel is best interpreted as an **exploratory negative-control / substrate-context panel**: MFE-derived secondary-structure accessibility does not obviously explain the locked Mud1/CR-sensitive set.

## Files

```text
run_jm105_fig4g_from_windows.ps1
  Windows/Euler runner. Uploads the Python scripts to Euler, installs Python ViennaRNA locally if needed, computes RNAlib metrics, rerenders the final intron-dot/median/IQR panel, retrieves out/.

scripts/compute_fig4g_rnalib_locked49_metrics.py
  Builds the locked Figure 4G metric table: locked selected n=49, locked background pool n=232, Figure 2 pass_age_gate annotation for aging-only/background split, FASTA/GFF intron-sequence extraction, RNAlib RNA.fold metrics.

scripts/rerender_fig4g_introns_median_order_label_fix.py
  Final visual renderer from the metric table. Does not recompute biology; handles layout, group order, label lanes, right-stat lane, SVG/PDF/PNG/white preview outputs.

docs/figure4g-development-lessons.md
  Detailed failure/repair ledger from the development pass.
```

## Critical source paths used on Euler

```text
Locked selected source, expected n=49:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V1_20260703_110602/01_LOCKED_CANDIDATES_WITH_RECOMPUTED_SCORE.tsv

Locked background source, expected n=232:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V2_20260703_111531/05B_CLEAN_SPLICEOSOMAL_BACKGROUND.tsv

Figure 2 metric annotation candidates:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure_2_candidate_metrics_all.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_metrics_all.tsv

Architecture/BP-distance source candidates:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_render_v5_FIX1_FIND_DERIVED_INPUTS_20260703_102648/derived_data/Figure4_v5_sequence_architecture_features.tsv
```

## Important method caveat

The ideal reviewer-grade structure workflow would use ViennaRNA `RNAplfold` local ensemble unpaired probabilities. Euler did not expose `RNAfold`/`RNAplfold` CLI tools or a ViennaRNA module in the active stack during this pass. The reproducible workaround stored here uses the Python `ViennaRNA` package / RNAlib `RNA.fold()` and derives an **MFE-structure accessibility proxy** from dot-bracket unpaired positions.

That is acceptable for an exploratory panel or Extended Data control, but the caption must not call it RNAplfold ensemble accessibility unless the pipeline is upgraded.

## Required outputs

The runner produces fixed-canvas outputs:

```text
out/panels/Figure4G_introns_median_order_label_fix.svg
out/panels/Figure4G_introns_median_order_label_fix.pdf
out/panels/Figure4G_introns_median_order_label_fix.png
out/panels/Figure4G_introns_median_order_label_fix_white_preview.png
```

and audit/data tables:

```text
out/derived_data/Figure4G_locked49_RNAlib_structure_metric_table.tsv
out/derived_data/Figure4G_order_label_fix_stats.tsv
out/derived_data/Figure4G_introns_median_order_label_fix_summary.tsv
out/audits/Figure4G_group_count_audit.tsv
out/audits/Figure4G_sequence_extraction_audit.tsv
out/audits/Figure4G_structure_failures.tsv
out/audits/Figure4G_order_label_fix_final_self_audit.tsv
```

## Visual and implementation rules preserved

- No fake data.
- No `bbox_inches="tight"`.
- Fixed canvas dimensions are declared constants.
- SVG text stays editable via `svg.fonttype = "none"`.
- Transparent SVG/PDF/PNG plus separate white preview PNG.
- Lane allocation before collision patching: title, legend, label, plot, right-stat, x-tick, footer.
- Selected group is locked Figure 4 selected n=49, not broad Figure 2 `candidate_passed`.
