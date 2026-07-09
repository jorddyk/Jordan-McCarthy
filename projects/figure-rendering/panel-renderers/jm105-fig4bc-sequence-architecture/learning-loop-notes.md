# JM105 Figure 4B/C rendering learning-loop notes

Date: 2026-07-09 Europe/Zurich

Purpose: preserve the operational lessons from the JM105 Figure 4B/C provenance and layout-repair session so future renderers repeat what worked and avoid the same failures.

## Final accepted direction

Use a selected-vs-background architecture comparison for the main Figure 4B/C panels.

```text
selected = selected Mud1/CR-sensitive aging introns, n=49
background = clean high-confidence spliceosomal background introns, n=232
```

The old grey/orange panels were not the same analysis. They compared condition-specific `Age-linked leakage increase` versus `No age-linked leakage increase` groups. That is useful historical context, but it is not the main Figure 4B/C selected/background background pool.

## Source provenance that worked

The useful source-chain split was:

1. RNA-seq/source-derived labels decide selected vs background.
2. Sequence/annotation feature tables provide 5′SS/U1/length/BP features.
3. Rendering joins labels to features and fails if counts are not preserved.

Final locked source paths:

```text
selected source:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V1_20260703_110602/01_LOCKED_CANDIDATES_WITH_RECOMPUTED_SCORE.tsv

background source:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_POSTER_ALIGNED_PROVENANCE_AUDIT_V2_20260703_111531/05B_CLEAN_SPLICEOSOMAL_BACKGROUND.tsv

4B feature source:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_PATCH_BIOCONDA_MAXENTSCAN_GATE_V9_20260706_103936/10_PANEL_B_MAXENT_U1_SOURCE_TABLE_LOCKED.tsv

4C feature source:
/cluster/scratch/jmccarthy/JM105_RNAseq/Figure4_MAXENT_PANELD_PANELE_REPAIR_V4_20260706_095741/12_PANEL_C_ARCHITECTURE_SOURCE_TABLE.tsv
```

The V17D `derived_data/Figure4B_source_values.tsv` and `Figure4C_source_values.tsv` are useful visual-value mirrors but not good provenance sources because they dropped full intron IDs. Do not use them as the canonical source for future provenance-sensitive rendering.

## What worked

### Provenance/workflow

- Running a source-chain audit before final rendering worked.
- Narrowing Euler discovery to JM105 scratch and specific renderer/provenance folders worked better than broad recursive scans.
- Selected/background counts were the best fail-fast invariant: render only if selected `n=49` and background `n=232` survive the feature join.
- Preserving V17D only as a comparison audit prevented confusing stripped plot values with biological source tables.
- Writing `source_manifest`, `join_audit`, `stats_audit`, `u1_metric_audit`, `collision_audit`, and `final_self_audit` made the learning process explicit.

### Data/metric choices

- Showing U1 as **integer paired bases** worked better than showing percent paired, because the underlying values are discrete.
- The visible U1 metric should be:

```text
u1_paired_bases = u1_best_WC_pairs + u1_best_GU_pairs
```

- Keep `u1_complementarity_percent_paired` only in audit/provenance tables.
- Use selected/background labels rebuilt from RNA-seq source-derived files; do not rely on feature-table `set_name` alone except as an audit comparison.

### Visual/layout choices

- Removing visible footer prose improved the panel substantially. Counts/provenance belong in audit/manifest/caption unless explicitly requested on-panel.
- Sparse y-ticks looked better:

```text
5′SS MaxEnt: -10, 0, 10
U1 paired bases: 5, 7, 9
Intron length: 0, 500, 1000
BP–3′SS distance: 0, 100, 200
```

- Major gridlines only; no per-integer U1 gridlines.
- Draw dots first, then box/whisker/median above dots.
- Put bracket, stars/ns, and p-value in separated lanes.
- Use small white backing boxes for statistics text where text sits over the plot region.

### Euler environment

- `/usr/bin/python3` failed because it lacked `matplotlib`.
- The working Euler path was:

```bash
module purge || true
module load fast_python_workshop_cpu/2025.0.0
```

- Future bash wrappers should smoke-test `matplotlib`, `PIL`, and optionally `scipy` before running the renderer.

## What did not work

### Over-broad source search

The first provenance search walked too much of `/cluster/home/jmccarthy` and looked frozen. Future source-discovery scripts should avoid broad home-directory recursion unless absolutely necessary, and should print progress or use targeted path allowlists.

### Missing Python plotting stack

Using `/usr/bin/python3` directly failed:

```text
ModuleNotFoundError: No module named 'matplotlib'
```

Future wrappers must load the known module or explicitly discover a working Python before executing panel code.

### U1 as percent

The percent y-axis created a staircase pattern and an awkward interpretation. The integer-paired-bases view is better for the final panel.

### Footer inside small panels

Footer text below the graph caused crowding/clipping and should not be used in these small panel assets. Store that information in audits and figure caption instead.

### Dense y-axis and gridlines

Printing every integer for U1 and drawing every horizontal line made the panel ugly and crowded. Use sparse major ticks only.

### Broken statistic placement

A key bug was using `ax.get_yaxis_transform()` while treating y as an axes-fraction value. That transform uses x in axes coordinates and y in data coordinates, which caused p-values like `p = 0.66` and `p = 0.72` to appear on the x-axis.

Correct rule:

```python
# bracket: x=data, y=axes-fraction
blend = transforms.blended_transform_factory(ax.transData, ax.transAxes)

# p-value: x=axes-fraction, y=axes-fraction
ax.text(x, y, text, transform=ax.transAxes, ...)
```

### Stars/ns overlapping brackets

The `ns`/stars text must have deliberate vertical separation from the bracket and ideally a modest white backing. Do not put p-value, stars, and bracket into the same visual band.

## Future implementation rules copied from this experience

1. For small panel stats, place bracket, significance symbol, and exact p-value as three separate objects.
2. Never use a mixed transform for p-values unless the coordinate semantics are explicitly checked.
3. Give stat text at least a few pixels of separation from bracket lines, points, and axis lines.
4. Use sparse y-axis intervals chosen for readability, not merely because the data are integer-valued.
5. Move provenance/count prose to audits/manifests/captions when the panel is small.
6. Treat value-only `derived_data` tables as render mirrors, not provenance sources, unless IDs and source gates are preserved.
7. Euler wrappers should load `fast_python_workshop_cpu/2025.0.0` and run import smoke tests before plotting.
8. If Jordan says a panel is visually good enough, save the final runnable source and the postmortem immediately rather than continuing to tweak.

## Do not commit from this workflow

Do not commit generated PNG/SVG/PDF panel outputs by default. They are Euler render artifacts and can be regenerated. Commit source code, README, and learning notes.
