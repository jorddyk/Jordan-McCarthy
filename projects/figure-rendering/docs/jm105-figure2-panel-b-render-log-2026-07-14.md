# JM105 Figure 2B Euler render log — 2026-07-14

## Status

The recovered Figure 2 hero-scatter renderer successfully executed on Euler after its actual CLI contract was respected.

Renderer copy used:

```text
/cluster/home/jmccarthy/JM105_Figure2_v2_render_20260714_133954/work/patched_renderers/figure2_panelB_v6_fixed_canvas.py
```

Strict-root argument:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE
```

Output directory:

```text
/cluster/home/jmccarthy/JM105_Figure2_v2_render_20260714_133954/out/B_retry_with_arguments
```

Confirmed invocation:

```bash
python3 \
  "$B_SCRIPT" \
  "$STRICT_ROOT" \
  "$B_OUT"
```

Confirmed result:

```text
panel_B_exit=0
```

The renderer produced SVG, PDF, transparent PNG, white-preview PNG, plot-source TSV, label-position TSV, common-name audit TSV, JSON summary, and run summary.

## Important: successful execution does not mean accepted biology

The renderer reported these six visible labels:

```text
SRB2, YSF3, BET1, RPL42B, ATG38, RPS24A
```

Earlier Figure 2 source forensics found that the 402-row strict annotated table contained only two rows with `candidate_passed_strict=True`:

```text
SRB2 / YHR041C
YNL138W-A
```

Therefore the rendered panel is not accepted yet. Before using it in a manuscript, inspect `Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv` and the renderer code to establish which gate defines the six labeled candidates. Do not assume that a directory name containing `STRICT` means the plotted candidate set uses `candidate_passed_strict`.

## Font warning

Euler emitted repeated:

```text
findfont: Font family 'Arial' not found.
```

The renderer's run summary says `MATPLOTLIB_FONT_FAMILY_USED=Arial`, but that only records the requested family; it does not prove Arial glyphs were used. The actual output likely used Matplotlib's fallback sans-serif font. Future accepted rendering must either:

1. use an installed Arial-compatible font and document the exact resolved font, or
2. configure a valid installed fallback deliberately while preserving editable SVG text.

Do not distribute font files.

## Output files confirmed

```text
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.candidate_common_name_audit.tsv
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.label_positions.tsv
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.plot_source.tsv
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.preview_white.png
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.RUN_SUMMARY.txt
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.summary.json
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.transparent.pdf
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.transparent.png
Figure_2A_Age_CR_candidate_map_LABEL_COLUMN_FINAL.transparent.svg
```

## Future-chat guardrail

Run success is only an execution milestone. A panel is not publication-ready until:

- the candidate/gating source is reconciled with the strict forensic audit;
- the actual resolved font is verified;
- the white preview and SVG are inspected for clipping and collisions;
- the plotted-source table is archived with the accepted renderer;
- the exact accepted source is committed under `projects/figure-rendering/panel-renderers/jm105-figure2-public-final/`.
