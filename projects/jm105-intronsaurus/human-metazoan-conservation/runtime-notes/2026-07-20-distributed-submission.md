# Distributed Euler submission — 2026-07-20

## Status

Real public RNA-seq analysis submitted on Euler on 2026-07-20 (Europe/Zurich).
No biological result is recorded here until the aggregate job completes.

## Submitted dependency graph

| Stage | Slurm job | State at handoff |
|---|---:|---|
| Human GENCODE 50 reference | `7873443` | Pending (Priority) |
| Mouse GENCODE M39 reference | `7873444` | Pending (Priority) |
| 34-task sample array, maximum 6 concurrent | `7873466` | Pending (Dependency) |
| Aggregate/statistical report | `7873467` | Pending (Dependency) |

Dependency chain: both reference jobs must complete successfully before the sample array starts; every array task must complete successfully before the aggregate job starts.

## Canonical metric

```text
JM105_IR = (EI + IE) / ((EI + IE) + 2 * EE_total)
```

- No pseudocount is used in the primary metric.
- Zero informative denominator is `NA`.
- `PEI` with a 0.5 continuity correction is secondary only.
- The public human/mouse studies do not permit `NMD_hidden` because they lack matched `UPF1+` and `upf1Δ` conditions.

## Exact submitted source provenance

The submitted files came from `JM105_HGPS_Metazoan_Distributed_2026-07-20.zip`.

Bundle SHA-256:

```text
223b0aacce75be7d9b275ea845c41a4c028d82e6460ba6be31c2e59c1667f47d
```

Canonical source files and individual SHA-256 values are recorded in the code handoff audit for this run. Raw FASTQ, SRA objects, BAM/BAI files, STAR indices, logs, caches and generated result tables remain on Euler and are not committed.

## Data status

`REAL PUBLIC DATA — RUNNING`.

The result remains `NO DATA` for manuscript purposes until job `7873467` finishes successfully and the gate report is reviewed.
