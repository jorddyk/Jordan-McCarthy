# JM105 Fig4B/C sequence-architecture lessons for future rendering

Date recorded: 2026-07-09 Europe/Zurich

This reusable template distills the accepted JM105 Figure 4B/C repair session into future rendering rules. Use it alongside `chatgpt-jm105-rendering-operating-standard.md` before rendering any similar selected-vs-background architecture panel.

## Data/provenance rules

1. Do not use value-only derived plotting tables as provenance when full-ID source tables exist.
2. For Figure 4B/C, selected/background labels come from RNA-seq source-derived candidate/background logic; sequence features come from annotation/feature tables.
3. Main Fig4B/C background is `clean_spliceosomal_background`, not old grey/orange `No age-linked leakage increase` condition-specific complements.
4. Render only if selected `n=49` and background `n=232` survive the join.
5. Preserve full IDs in `*_values_with_ids.tsv`, but show no IDs on these small distribution panels.

## U1 metric rule

Show U1 complementarity as integer paired bases:

```text
u1_paired_bases = u1_best_WC_pairs + u1_best_GU_pairs
```

Keep `u1_complementarity_percent_paired` in audit only. The percent y-axis creates an artificial staircase and is less interpretable for this panel.

## Statistics placement rule

Do not place bracket, stars/ns, and exact p-value into one shared collision-prone band.

Use three separate objects:

```text
bracket: x=data coordinates, y=axes-fraction coordinates
stars/ns: centered above bracket with small white backing
p-value: ax.transAxes upper-right white-space anchor with small white backing
```

Critical transform warning:

```python
# Correct for bracket:
blend = transforms.blended_transform_factory(ax.transData, ax.transAxes)

# Correct for p-value:
ax.text(x, y, p_text, transform=ax.transAxes)
```

Do **not** use `ax.get_yaxis_transform()` for p-values while thinking y is an axes fraction. That transform uses y in data coordinates and caused `p = 0.66` / `p = 0.72` to fall onto the x-axis.

## Axis/gridline beauty rule

Use sparse, interpretable major ticks only:

```text
5′SS MaxEnt: -10, 0, 10
U1 paired bases: 5, 7, 9
Intron length: 0, 500, 1000
BP–3′SS distance: 0, 100, 200
```

Avoid every-integer y-ticks and dense gridlines even when the data are discrete. Major gridlines only.

## Footer/provenance rule

Small panels should not carry visible footer prose. Move counts/source notes to:

```text
source_manifest.tsv
join_audit.tsv
stats_audit.tsv
u1_metric_audit.tsv
final_self_audit.tsv
figure caption
```

## Euler environment rule

Load the plotting module before rendering:

```bash
module purge || true
module load fast_python_workshop_cpu/2025.0.0
```

Then smoke-test:

```python
import matplotlib
import PIL
```

`/usr/bin/python3` alone did not have `matplotlib` during the Fig4B/C session.

## Visual sequence rule

For distribution panels with overlaid points and summary geometry:

1. Draw points first.
2. Draw box/whisker/median above points.
3. Draw significance bracket/text last.
4. Use white backing boxes sparingly for stat text in plot regions.

## Renderer location

Canonical implementation:

```text
projects/figure-rendering/panel-renderers/jm105-fig4bc-sequence-architecture/
```
