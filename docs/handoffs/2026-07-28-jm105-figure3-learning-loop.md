# 2026-07-28 JM105 Figure 3 learning-loop handoff

Repository: `jorddyk/Jordan-McCarthy`  
Project: JM105 / Intronsaurus / Nature Aging figure rendering

## Work completed

1. Read the repository root instructions and mandatory figure-rendering standards before modifying the repository.
2. Added the permanent learning loop:

```text
projects/figure-rendering/templates/jm105-figure-rendering-learning-loop.md
```

3. Added the complete active incident/learning record:

```text
projects/figure-rendering/docs/jm105-figure3-2026-07-28-rendering-incident-and-learning-record.md
```

4. Added fail-closed metadata normalization infrastructure and regression tests:

```text
projects/figure-rendering/qa/jm105_metadata_preflight.py
projects/figure-rendering/qa/test_jm105_metadata_preflight.py
```

5. Updated:

```text
projects/figure-rendering/START_HERE_FOR_FIGURE_RENDERING.md
projects/figure-rendering/AGENTS.md
projects/figure-rendering/README.md
```

## Permanent lessons encoded

- Never infer biological metadata or replicate pairing from opaque sample names such as `JM1`.
- Transliterate Unicode genotype symbols before punctuation stripping.
- Regression-test `WT_UPF1`, `UPF1+`, plain `UPF1`, `upf1Δ`, `upf1D`, and `upf1delta`.
- Visible figure labels use common gene names only; systematic IDs stay in provenance.
- Literal `NaN` cells are a hard publication-QA failure.
- Axis labels must state the exact metric, condition and subtraction direction.
- `PD (Priority)` is a scheduler wait state, not a code failure; do not resubmit a valid pending job.
- Download paths must be real clickable artifact links; local filenames must be discovered and verified rather than assumed.
- A renderer is not canonical until Euler execution, hard QA, Windows retrieval, local verification, white-preview review and Jordan acceptance all pass.
- The locked Figure 3 is the Mud1-dependence figure. `candidate_score` is not a public Figure 3 concept. The current exploratory CR-selectivity renderer must not be promoted as canonical Figure 3.

## Current run status at handoff

```text
Slurm job: 8875587
Last observed state: PD (Priority)
Real metadata preflight: PASS
Canonical acceptance: NO
```

The job may be inspected as incident evidence after completion. Do not commit its renderer as canonical Figure 3 without restoring the locked Figure 3 A-H architecture and obtaining Jordan's visual acceptance.

## Next actions

1. Inspect `sacct`, stdout and stderr after job `8875587` leaves the scheduler.
2. Preserve outputs/logs and retrieve the white preview.
3. Review the output as exploratory only.
4. Restore the locked Figure 3 source crosswalk and Mud1-dependent CR-suppression metric.
5. Run the new metadata preflight before the next Slurm submission.
6. Promote only the accepted final renderer.
