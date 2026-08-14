# JM-136 Provenance Policy

## Purpose

JM-136 is scientific software. A source-history mistake can become a scientific-history mistake if it changes the code believed to have produced a biological result. Provenance therefore has higher priority than cosmetic repository cleanliness.

## Core rule

> **No placeholder is code. No description of missing code is code. No successful-looking filename is proof.**

A file is recorded as preserved source only when its actual source body is available and its identity can be checked. If a file is missing, record it as missing and request the original rather than reconstructing a plausible implementation.

This rule is a direct response to the earlier Fable/source-recovery failure, where a reconstructed-looking artifact was at risk of being treated as recovered code. JM-136 must make that failure mode structurally difficult.

## Source ingestion protocol

For each source file:

1. Preserve the supplied source before refactoring.
2. Record the user-facing/original filename and the canonical repository filename.
3. Record the original SHA-256 when available.
4. Syntax-check Python source (`python -m py_compile`) where dependencies are not required at compile time.
5. Commit the source into a dated source snapshot.
6. Verify the committed Git blob against the expected normalized source content.
7. Mark any line-ending normalization explicitly rather than calling byte-different files identical.
8. Do not silently edit hard-coded paths, comments, formatting, scientific rules, or version labels during the preservation step.

The source snapshot exists to answer: **what source did we actually have at this decision point?** A later refactor is a different artifact and should be reviewable as a semantic change.

## Line endings

Several Windows files use CRLF. Git commonly stores text with LF. Both identities matter:

- original SHA-256 fingerprints the supplied file bytes;
- normalized Git blob SHA fingerprints the exact text committed after CRLF→LF normalization.

The inventory records both where known. A line-ending normalization is acceptable; an unrecorded code rewrite is not.

## Scientific semantic changes

Changes to these areas require explicit review and a benchmark rerun:

- trap/chip identity keys;
- extraction/frame-number mapping;
- coordinate-space conversion;
- state ontology;
- completed-division definition;
- gap-bridging logic;
- death definition;
- censoring policy;
- event collapse/decoder behavior;
- train/calibration/test split construction;
- endpoint metrics.

A change can be only one line and still alter an RLS survival curve.

## Model provenance

A trained model is not adequately identified by a filename such as `aging_chip_classifier.keras`.

A reproducible model record should bind:

- source-code Git commit and source SHA;
- trainer/config version;
- model file SHA-256;
- annotation/data snapshot identity;
- experiment/chip/position inclusion list;
- split definition and random seed;
- biological event/death/censoring semantics;
- preprocessing/input format;
- dependency/runtime environment;
- calibration parameters;
- endpoint metrics and stratified diagnostics;
- export/promotion decision.

Generated model binaries should normally live in controlled scientific/artifact storage rather than source Git. Git stores the metadata and hashes needed to identify them.

## Data boundary

Do not commit raw or extracted TIFF/ND2 stacks, mutable annotation workbooks, large trained models, or other large/sensitive scientific data merely to make the repository self-contained. The repository should instead point to approved storage and record stable identifiers/hashes where practical.

GitHub is the source/provenance record; OpenBIS and approved Barral/ETH storage remain scientific data/experimental records.

## Current versus experimental versus historical

Status must be explicit:

- **operational/current**: presently used component with demonstrated value;
- **candidate/experimental**: under evaluation and not authoritative;
- **rejected experiment**: failed the declared endpoint gate but retained for negative knowledge;
- **historical/superseded**: no longer active, retained through Git history/archive.

Never infer status from filename chronology (`v7` > `v6`) or modification date.

## Refactoring rule

Do not deduplicate duplicated scientific helper functions until regression fixtures capture current behavior. The desired end state is one canonical implementation, but an untested cleanup can silently redefine the phenotype.

The correct sequence is:

```text
preserve exact source
    -> write semantic fixtures/tests
    -> establish benchmark baseline
    -> refactor
    -> prove regression equivalence
    -> intentionally version any changed semantics
```

## Claims rule

Repository documentation must distinguish:

- observed benchmark result;
- inference about why a model failed;
- design hypothesis for a candidate;
- deployment decision;
- future aspiration.

Do not describe a candidate as “better,” “production,” “superhuman,” or “validated” until the relevant held-out evidence exists.
