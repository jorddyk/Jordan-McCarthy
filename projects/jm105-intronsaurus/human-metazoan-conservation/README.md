# JM105 HGPS + metazoan CR distributed Euler workflow

## Purpose

This package replaces the superseded one-node monolithic job with a Slurm
dependency workflow designed for Euler:

1. Human and mouse reference jobs run in parallel.
2. A 34-task Slurm array processes one public RNA-seq run per task.
3. At most six sample tasks run concurrently, normally across multiple nodes.
4. A final aggregation job runs only after every sample task succeeds.

The peak sample-array request is 48 CPUs and 288 GB RAM across six independent
jobs, rather than 24 CPUs on one node processing all 34 samples serially.

## Exact JM105 cross-check

The authoritative JM105 figure specification defines:

```text
IR = (EI + IE) / (EI + IE + 2 * EE_total)
```

This distributed workflow uses that exact formula as `JM105_IR`:

- `EI`: unique query names spanning the first unspliced exon-intron boundary.
- `IE`: unique query names spanning the second unspliced intron-exon boundary.
- `EE_total`: unique query names carrying the exact annotated exon-exon splice junction.
- no pseudocount in the primary metric;
- zero informative denominator becomes `NA`;
- sample-level values are saved before condition averaging;
- host-gene STAR counts are retained separately.

The BAM is name-sorted and scanned once. All alignments belonging to one query
name are combined before an event is incremented, preventing paired reads from
being counted twice for the same intron event.

`PEI = log2((EI + IE + 0.5)/(2*EE_total + 0.5))` is retained only as a secondary
sensitivity metric. It never drives the biological gates.

## Necessary difference from JM105

JM105 has matched `UPF1+` and `upf1Δ`, enabling:

```text
NMD_hidden = IR(upf1Δ) - IR(UPF1+)
```

The selected human and mouse public studies have no matched NMD perturbation.
This package therefore measures steady-state retained-intron exposure only. It
does not calculate `NMD_hidden` and does not claim nuclear export, translation,
or NMD degradation.

## Biological comparisons

- GSE118633: HGPS versus control fibroblasts.
- GSE137083: HGPS versus normal fibroblasts; FTI, PML2 knockdown and pan-PML
  knockdown versus HGPS control.
- GSE222163 / PRJNA918398: caloric restriction versus control in brown adipose
  tissue and skeletal muscle; exercise-containing groups remain excluded.

## Resource layout

### Reference jobs, two jobs concurrently

- 16 CPUs each
- 96 GB RAM each
- 4-hour limit

Existing complete reference indexes are reused.

### Sample array

- 34 tasks
- maximum six concurrent tasks
- 8 CPUs and 48 GB RAM per task
- 250 GB node-local temporary disk per task
- 24-hour task limit

Each task downloads/converts one run, aligns it, query-name sorts the BAM, scans
that BAM once, and writes one compressed intron table.

### Aggregate job

- 4 CPUs
- 32 GB RAM
- 8-hour limit

## Windows submission

Extract the ZIP and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\upload-submit-distributed.ps1
```

The uploader preserves the existing environment and any completed reference or
sample outputs. It cancels only superseded monolithic job `7869397` if that job
is still active.

## Monitoring

The submission command prints four job IDs and records them in:

```text
/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/submission/latest.env
```

On Euler, use the five-second watcher:

```bash
bash /cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/code/watch-distributed.sh
```

Or inspect the job IDs directly:

```bash
source /cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/submission/latest.env
squeue -j "$HUMAN_REFERENCE_JOB,$MOUSE_REFERENCE_JOB,$SAMPLE_ARRAY_JOB,$AGGREGATE_JOB"
```

The final report is:

```text
/cluster/scratch/jmccarthy/JM105_HGPS_Metazoan_Conservation/work/results/GATE_REPORT.md
```

## Figure scope and rendering

No figure is rendered. JM105 Figure 2 remains limited to total/rRNA-depleted
JM105 data. No poly-A, P-versus-T, mRNA-like, or P-minus-T construct is touched.
No tight bounding-box export is used in this analysis package.

## Concurrency-lock repair

Array launchers call the environment Python executable directly and prepend the environment `bin` directory to `PATH`. They do not use concurrent `micromamba run` processes, avoiding shared `~/.cache/mamba/proc` lock failures. The companion `repair-failed-array.sh` reruns only failed tasks and submits a new dependent aggregate job.
