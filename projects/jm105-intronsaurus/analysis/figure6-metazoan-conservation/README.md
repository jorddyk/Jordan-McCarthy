# Figure 6 metazoan-conservation analysis

Analysis and fail-closed gate scripts supporting the proposed Figure 6 comparison across worm aging, HGPS fibroblasts, mammalian interventions, and mouse caloric restriction.

These files are analysis code only. They do not contain raw sequencing data, generated biological values, or rendered figure outputs.

## File roles and precedence

| File | Role | Status / interpretation rule |
|---|---|---|
| `JM105_figure6_discovery_20260729.py` | Exploratory discovery analyses designed to be immune to global expression shifts by using within-sample ratios, within-sample ranks, or expression-matched controls. Includes SMG-2 association, rank-based aging, detection-versus-magnitude, and responder-feature analyses. | Exploratory. It proposes candidate signals; downstream gates decide whether they survive. |
| `JM105_figure6_aging_expression_confounder_20260729.py` | Worm aging expression-confounder gate. Tests depth, PEI-versus-expression coupling, residualized aging effects, and a depth-invariant IR endpoint. | Fail-closed gate for whether the worm aging panel may be rendered. |
| `JM105_figure6_human_gate_20260729.py` | Initial cross-cohort HGPS and intervention gate using signature validation, intervention reversal, combined effects, and leave-one-out checks. | Historical analytical stage. Two permissive rules in this script are explicitly withdrawn by `JM105_figure6_human_expression_20260729.py`; do not cite its PASS labels alone. |
| `JM105_figure6_human_expression_20260729.py` | Corrective human/mammalian expression-confounder analysis. Replaces the weak cross-cohort and combined-intervention rules with per-intron concordance and difference-of-differences gates, and adds rank-based and depth-invariant checks. | Current stricter interpretation layer for the human arm. It takes precedence over the two withdrawn rules in `JM105_figure6_human_gate_20260729.py`. |

## Scientific boundaries

- Human and mouse datasets do not contain matched UPF1-on/off samples; their endpoint is steady-state retained-intron exposure, never `NMD_hidden`.
- HGPS is treated as a progeroid perturbation, not normal aging.
- Cohorts and library preparations are analyzed within dataset and are not pooled.
- The human cohorts are small; effect sizes, intervals, concordance, and fail-closed gates are more informative than isolated nominal P values.
- No script in this directory should be treated as a figure claim until its stated gate passes on the real source data.

## Validation performed before import

All four Python files passed `python -m py_compile` on 2026-07-30. Their data-dependent analyses were not executed because the required Euler source trees are not present in this repository.
