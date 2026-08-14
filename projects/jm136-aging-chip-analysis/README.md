# JM-136: Automating Aging Chip Analysis

**OpenBIS experiment:** [JM-136: Automating Aging Chip Analysis](https://openbis-barral.ethz.ch/openbis/webapp/eln-lims/?menuUniqueId=%7B%22type%22:%22PROJECT%22,%22id%22:%2220231030105747925-233308%22%7D&viewName=showExperimentPageFromIdentifier&viewData=/JMCCARTHY/MICROSCOPY/JM-136)

This private project preserves and develops the code used to turn Barral-lab microfluidic yeast aging-chip time-lapse data into trap-resolved cell-state annotations, division events, death/censoring calls, and replicative lifespan (RLS).

The filesystem path is `projects/jm136-aging-chip-analysis/` rather than the literal human title because `:` is not a legal Windows filename character. The exact OpenBIS title is preserved here.

## Current engineering rule

Do not replace a working component merely because a newer model is more sophisticated. New components must add value under grouped endpoint validation. The operational UI and the best demonstrated RLS baseline remain preserved while experimental models are evaluated beside them.

## What is canonical right now?

The repository first preserves an **exact source snapshot** of the code supplied on 14 August 2026. Source bodies are not reformatted or refactored during ingestion. This avoids destroying provenance while the pipeline is still changing quickly.

Within that snapshot:

- `human_classifier_ui.py` is the working human/AI annotation interface and defines the current annotation workflow and RLS semantics.
- `train_classifier.py` is the strongest demonstrated direct-event RLS baseline from the current development sequence (held-out test MAE approximately 2.44 divisions; death-call agreement approximately 93.8% in the recorded run).
- `train_oracle_only.py` is the prospective remaining-lifespan oracle trainer.
- `train_rls_supermodel_v7_1_embedded_gold.py` is an **experimental candidate**, not production. It adds trap-domain self-supervised pretraining, an 11-frame temporal event model, position-grouped validation, and an embedded snapshot of manual JM135 RLS gold. It must not be described as better until its held-out results exist.
- v6, the sequence refiner, v7, and the temporal residual trainer are retained as experimental history because their failures contain useful negative knowledge and prevent repetition of dead ends.
- `P3_tracking.py` is preserved as a tracking-related source supplied with the project. It is not silently rewritten into the newer extracted-trap pipeline.

See [`docs/benchmark-history.md`](docs/benchmark-history.md) for model status and [`docs/source-inventory.md`](docs/source-inventory.md) for exact hashes and ingestion completeness.

## Pipeline boundary

Conceptually, JM-136 is an acquisition-to-phenotype analysis pipeline:

```text
raw aging-chip time lapse
        |
        v
trap detection / stabilized extraction
        |
        v
trap identity + spatial anchor / mother tracking
        |
        +----------------------+
        |                      |
        v                      v
human annotation UI       learned image/event models
        |                      |
        +----------+-----------+
                   v
        explicit biological event semantics
        division / death / censoring
                   |
                   v
              per-trap RLS
                   |
                   v
       grouped benchmark + review queue
                   |
                   v
      experiment-level survival analysis
```

The durable interface is not a specific CNN. It is the combination of traceable trap identity, reproducible preprocessing, explicit biological semantics, versioned model/rule provenance, machine-readable outputs, benchmark performance, and bounded human QC.

## Biological contract

A completed division is currently registered when `Late Bud` resolves to `Mother` or `Early Bud`, with the documented look-back across contiguous `No Cell` / `Out of Focus / Blurry` observations. Death and censoring are separate endpoint concepts. These definitions are scientific interfaces: changing them can change survival results and therefore requires an explicit versioned decision and re-analysis.

The analysis system must never be allowed to manufacture a genotype/media effect. Validation must therefore be stratified by biologically relevant condition, position/chip/batch, and late-life morphology whenever metadata permit.

## Repository layout

```text
jm136-aging-chip-analysis/
  README.md
  .gitignore
  code/
    source-snapshot-2026-08-14/   exact supplied source; no cleanup edits
  docs/
    architecture.md
    benchmark-history.md
    provenance-policy.md
    source-inventory.md
    HEARTH-socratic-review.md
```

A package-style `src/` refactor should happen only after the exact snapshot is complete and semantic regression tests exist. Refactoring first would make it harder to distinguish organizational cleanup from scientific behavior change.

## Inputs

Runtime inputs live outside GitHub unless explicitly approved:

- extracted `Pos*_trap_*.tif` stacks;
- `annotation/master_human_annotations.xlsx`;
- manual RLS gold / experiment metadata;
- trained `.keras` / `.h5` artifacts when generated;
- raw OME-TIFF / ND2 acquisition data.

The code should accept paths through environment variables or explicit arguments rather than rely permanently on one workstation or NAS mount.

## Outputs

Depending on the component:

- per-frame state/event predictions;
- per-trap division events and RLS;
- death/censoring calls;
- concordance/audit CSVs;
- model metadata and run manifests;
- candidate model artifacts;
- human-review targets.

Generated binaries, raw images, annotations, Slurm logs, and large scientific data are not source code and are ignored by default.

## Validation standard

A model is not promoted by frame accuracy alone. At minimum report:

- whole-trap and, where possible, whole-position/chip/biological-replicate holdout;
- trap-level RLS MAE and exact / ±1 / ±2 agreement;
- missed and false division events;
- death and censoring performance;
- condition/batch-stratified error;
- full-experiment inference runtime;
- fraction of traps automatically accepted versus routed to review;
- human review minutes versus manual scoring;
- source code, annotation snapshot, split definition, biological rules, and model hash.

The scientifically dangerous failure is not necessarily the ugliest confusion matrix; it is a condition-specific scoring error large enough to change an inferred biological effect.

## Data and disclosure boundary

This is kept in the private canonical repository. Raw TIFF/ND2 stacks and large/sensitive scientific data do not belong in GitHub. Exact runnable code and bounded documentation do. Before any public release, benchmark dataset, external model sharing, or commercial disclosure, resolve the applicable ETH/software/data/know-how ownership and publication/IP boundaries.

## Provenance rule

**No placeholder is code. No description of missing code is code. No successful-looking filename is proof.** A source is recorded as present only when the exact source body is available, hashed, syntax-checked where applicable, and committed. Missing local files are named explicitly in the source inventory instead of reconstructed from memory.
