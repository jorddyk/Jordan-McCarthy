# Daily code handoff — Figure 1 and worm final-figure runtime proof

Date: 2026-07-26 Europe/Zurich

## Sources searched

- File Library uploads from 2026-07-23 through 2026-07-26.
- Recent Gmail code/attachment search.
- Private repository `jorddyk/Jordan-McCarthy`, including open draft PRs #6 and #7.
- Current JM105 README, JM105 legacy-backfill ledger and code wiki.

## Material successful-run evidence

### JM105 Figure 1

Verified from the uploaded Euler transcript:

```text
job: 8286585
state: COMPLETED
exit: 0:0
elapsed: 00:00:29
renderer root: /cluster/scratch/jmccarthy/JM105_RNAseq/figure1_renderer_v1
output: /cluster/scratch/jmccarthy/JM105_RNAseq/figure1_renderer_v1/outputs/Figure1_v12_20260723_131022_8286585
```

The completion output records:

- exact six-sample cohort gate passed;
- old samples `JM18|JM30|JM7`;
- young samples `JM12|JM24|JM54`;
- 307 nuclear spliceosomal-mRNA introns;
- 6,585 nuclear chromosomal genes;
- verified common names or blank labels only;
- `synthetic_data_used: false`.

Status: `PARTIAL / SUCCESSFUL SOURCE LOCATED`.

The transcript contains execution evidence and fragments, not the complete exact source bodies. No source was reconstructed. Exact next intake:

```text
/cluster/scratch/jmccarthy/JM105_RNAseq/figure1_renderer_v1/materialize_figure1_exact_inputs.py
/cluster/scratch/jmccarthy/JM105_RNAseq/figure1_renderer_v1/render_figure1_panels.py
exact v12 run and submit scripts
paper_style.py
source SHA-256 manifest
environment/dependency record
input provenance and validation outputs
```

### C. elegans final figure

Verified from the uploaded Euler transcript:

```text
job: 8291829
state: COMPLETED
exit: 0:0
elapsed: 00:02:37
output: /cluster/scratch/jmccarthy/JM105_CELEGANS_WORM_ANALYSIS/work/final_figure
final_figure_version: 2026-07-23.final-figure.2
source_pipeline_version: 2026-07-22.3
manifest_rows: 158
biological_samples: 108
```

All reported gates passed:

- main-figure audit;
- extended-figure audit;
- combined figure audits;
- PNG dimension checks;
- editable SVG text check.

Status: `PARTIAL / SUCCESSFUL SOURCE LOCATED`.

Draft PR #6 preserves the complete base v3 worm pipeline. It does not currently contain a separately identified exact final-figure v2 renderer/launcher used by job `8291829`. No inference was made from `aggregate_and_render.py`. Exact next intake:

```text
final-figure v2 Python renderer
exact sbatch/launcher
style/helper modules
source SHA-256 manifest
completion JSON and figure manifest
concise reproduction command
```

## Scientific constraints preserved

- No values were inferred from rendered figures or terminal summaries.
- Figure 2 remains total/rRNA-depleted JM105 only.
- Raw NMD-off/upf1Δ retained signal remains distinct from matched NMD-hidden off-minus-on signal.
- Worm studies remain separate; no cross-study subtraction manufactures a missing JM105 factorial.
- `eat-2` remains dietary restriction; `daf-2` remains reduced insulin/IGF signalling.
- Host transcript abundance remains distinct from protein abundance.
- No raw reads, alignments, generated figures, logs, caches or scratch data were committed.
