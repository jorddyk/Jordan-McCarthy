# JM-136 Pipeline Architecture

## Scope

JM-136 is the software layer that converts microfluidic yeast aging-chip time-lapse data into auditable, trap-resolved replicative-lifespan phenotypes. The pipeline is broader than any individual classifier. It includes image/trap identity, spatial anchoring, human annotation, machine inference, explicit biological event semantics, endpoint extraction, grouped validation, and targeted human QA.

## End-to-end data flow

```text
aging-chip acquisition
        |
        v
raw time-lapse images
        |
        v
trap localization / extraction / stabilization
        |
        v
Pos + Trap_ID + frame identity
        |
        +-----------------------------+
        |                             |
        v                             v
human annotation UI             learned experts
state + spatial anchors          state / division / death
        |                             |
        +--------------+--------------+
                       v
          versioned biological semantics
        division / death / censoring rules
                       |
                       v
              per-trap event timeline
                       |
                       v
               per-trap observed RLS
                       |
                       v
            grouped benchmark / QA gate
                       |
             +---------+----------+
             |                    |
             v                    v
auto-accepted traps       targeted adjudication
             |                    |
             +---------+----------+
                       v
            experiment-level outputs
             survival / condition tests
```

## Stable scientific contracts

These interfaces should be treated as versioned scientific behavior, not incidental helper code.

### Trap identity

A prediction must remain traceable to the experiment/chip identity available in the source metadata, position, trap ID, and frame. Never silently collapse distinct chips that reuse a `(Position, Trap_ID)` pair.

### Frame indexing

Extraction and serving code must agree on whether saved TIFF index `0` corresponds to raw acquisition frame `0` or another acquisition frame. A one-frame offset can corrupt both event labels and spatial anchors without creating an obvious exception.

### Coordinate systems

The current annotation UI stores spatial clicks in a 460 × 460 display coordinate system while extracted trap frames are approximately 100 × 100 pixels. Pixel consumers must convert display coordinates to raw-frame coordinates before image operations. A future refactor should represent coordinate space explicitly in types/records rather than relying on comments.

### State ontology

Current learned biological/image states include:

- `Mother`
- `Early Bud`
- `Late Bud`
- `Dead Cell`
- `No Cell`
- `Out of Focus / Blurry`

Administrative/exclusion states such as escaped mothers and bad traps must remain distinct from biological death.

### Completed division

Current canonical rule: a completed division is registered when `Late Bud` resolves to `Mother` or `Early Bud`. The current rule may bridge a contiguous run of `No Cell` / `Out of Focus / Blurry` observations according to the implementation being benchmarked. Any change to gap bridging changes the phenotype definition and requires a versioned decision plus re-analysis.

### Death and censoring

Observed on-chip death is not interchangeable with disappearance, escape, bad-trap censoring, or end-of-movie censoring. Models may estimate these states, but the endpoint semantics must remain explicit and auditable.

## Replaceable implementation layers

The following may evolve aggressively as long as the contracts above and benchmark performance are preserved:

- CNN / ViT / Transformer / state-space backbone;
- temporal context length;
- image augmentation;
- self-supervised pretraining objective;
- UI implementation;
- GPU/CPU hardware;
- event proposal strategy;
- ensemble/adjudication model;
- model serialization/runtime.

This is why the repository does not define “the pipeline” as `train_classifier.py`.

## Current operational components

### Human annotation and adjudication

`human_classifier_ui.py` is a working operational surface. Even after high automation, it remains valuable as a QA/adjudication console, benchmark-creation tool, active-learning interface, and out-of-distribution inspection surface. The desired trajectory is not “delete the human UI”; it is “move human effort from broad frame-by-frame scoring to a small, high-information disagreement queue.”

### Direct event/death baseline

The direct-event trainer is the best demonstrated RLS endpoint in the current development sequence. It predicts division/death directly from the trap image context while retaining frame-state classification as auxiliary information. New models should be evaluated as additions or replacements only after grouped endpoint comparison.

### Prospective lifespan oracle

The oracle is a separate scientific question: whether the observed trajectory up to the current time predicts remaining lifespan. It must not be conflated with final RLS scoring. Prospective performance should be compared with simple baselines such as current-RLS-only and elapsed-time models.

### Experimental temporal/self-supervised models

Long-context, sequence-refiner, residual, and self-supervised/Transformer experiments are retained as R&D evidence. Larger version numbers do not imply authority.

## Positive-sum model architecture

If specialized experts provide partially independent information, the preferred future serving design is additive:

```text
working state classifier -----+
                              |
direct division detector -----+--> event adjudicator --> confirmed divisions
                              |
long-context / SSL expert -----+
                              |
trap geometry / motion --------+

strongest validated death expert -----------------------> death/censoring

confirmed events + endpoint semantics ------------------> RLS
```

This structure preserves useful existing models while allowing new experts to add information. A candidate may be rejected globally yet still contribute a validated sub-signal, such as event localization.

## Benchmark architecture

A single evaluation contract should eventually own split generation and metrics so each trainer cannot silently choose a favorable definition.

Minimum grouped reporting:

- whole-trap holdout;
- whole-position/chip/biological-replicate holdout where metadata support it;
- RLS MAE and signed bias;
- exact, ±1 and ±2 agreement;
- division-event precision/recall/F1 with a declared temporal tolerance;
- death and censoring performance;
- error stratified by genotype/media/batch/position and life stage;
- full-experiment wall-clock inference time;
- fraction of traps auto-accepted;
- minutes of human review required.

The most dangerous error is a systematic condition-specific scoring bias capable of creating, removing, or changing a biological survival effect.

## Proposed package destination

Do not rewrite the historical snapshot into this shape until semantic regression tests exist. Once they do, the desired structure is:

```text
src/aging_chip/
  domain/
    events.py
    endpoints.py
    identity.py
  geometry/
    coordinates.py
    anchors.py
    alignment.py
  io/
    annotations.py
    traps.py
    config.py
  annotation/
    adjudication.py
  models/
    interfaces.py
    state.py
    division.py
    death.py
  evaluation/
    splits.py
    metrics.py
    benchmark.py
  pipeline/
    run.py
  cli/

tests/
  fixtures/
  test_frame_mapping.py
  test_coordinates.py
  test_event_semantics.py
  test_death_censoring.py
  test_benchmark_contract.py
```

The source snapshot and Git history remain the record of what actually ran; the package becomes the maintainable implementation after behavior is frozen by tests.
