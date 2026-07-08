# JM105 Figure 3 Renderer v21 Backfill

## Purpose

Recover the newest useful complete renderer for JM105 Figure 3 Mud1/caloric-restriction panels from the project rendering chat.

## Source clue

Final successful Euler run:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure3_render_v21_20260702_161316
```

Recovered package name in current ChatGPT artifact context:

```text
Figure3_v21_large_text_B_footer_D_labels_package.tar.gz
```

## Canonical path

```text
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/
```

## Imported in this pass

```text
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/README.md
projects/figure-rendering/panel-renderers/jm105-figure3-mud1-cr-panels/run_figure3_v21_on_euler.sh
```

## Not yet imported

The following exact source files remain queued for full-source import from the recovered package:

```text
Figure_3_render_all_v21.py
figure3_base_renderer.py
```

They should not be reconstructed from memory or summaries.

## Scientific/data status

- Real JM105 total/rRNA-depleted RNA-seq summary inputs.
- No fake biological data.
- No raw FASTQ/BAM/SAM/CRAM committed.
- No generated figure images committed.
- No poly-A, P-versus-T, mRNA-like, or P−T construct data.
- Final v21 renderer was accepted after the B/C/D font-size problem was fixed: B/C gene labels 8.5 pt, D gene labels 8.5 pt, no text overlaps, no clipped text.

## Important rendering lesson preserved

The earlier Figure 3 attempts passed low font-size audits but failed human readability. For future Figure 4/Figure 5 renderers, do not treat 6–7 pt as the goal. Dense labels should start at 8.5–9 pt, ticks at about 8 pt, axis titles at about 9 pt, and layout problems must be solved by lane geometry rather than shrinking text.
