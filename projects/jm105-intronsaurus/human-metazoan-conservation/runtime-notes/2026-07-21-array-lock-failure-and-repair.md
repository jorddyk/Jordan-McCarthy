# Array completion failure and lock-free repair — 2026-07-21

## Observed state

The first distributed sample array was Slurm job `7873466`. Thirty-one of 34
sample tasks completed and wrote valid completion markers. Tasks `1`, `5`, and
`33` failed with exit code `1:0`. Aggregate job `7873467` was cancelled without
running because it had an `afterok` dependency on the complete array.

## Exact failure

Each failed task exited within 48 seconds, before SRA download, STAR alignment,
BAM quantification, or any biological calculation. The stderr for all three
tasks reported a libmamba process-lock failure under:

```text
/cluster/home/jmccarthy/.cache/mamba/proc
```

Concurrent array tasks invoked `micromamba run` against the same home-directory
process lock. The resulting stale-file-handle/resource-unavailable errors were
an execution-wrapper concurrency defect, not a data or biological-analysis
failure.

## Repair

The repaired Slurm sample and aggregate launchers call the existing environment
executables directly:

```text
/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/software/
micromamba-root/envs/jm105-hgps-conservation/bin/python
```

The repair workflow:

1. validates that 31 completion markers are present;
2. validates the exact missing tasks `1,5,33`;
3. submits only those three array tasks;
4. submits a new aggregate job with `afterok` on the repair array;
5. leaves all 31 completed sample outputs unchanged.

## Scientific integrity

The repair does not change:

- public accessions or sample assignments;
- reference genomes or annotations;
- STAR parameters;
- representative transcript or intron definitions;
- EI, IE, or EE_total counting;
- the primary `JM105_IR` equation;
- statistical contrasts or biological values.

## Canonical repair source

- `repair-failed-array.sh`
- `upload-repair-failed-array.ps1`
- `slurm/10_process_sample_array.sbatch`
- `slurm/20_aggregate.sbatch`
- `watch-distributed.sh`

Data status: real public RNA-seq; aggregate biological results remain `NO DATA`
until the repaired aggregate job finishes and its gate report is reviewed.
