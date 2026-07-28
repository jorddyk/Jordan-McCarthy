# JM105 figure-rendering learning loop

Status: mandatory companion to the Figure Rendering Reliability Standard.

Bible reference: `JM105-FIGURE-BIBLE-v1.0-2026-07-22`, governing figure-rendering contract.

## Purpose

This loop turns every material failure into a permanent prevention rule instead of another ad hoc patch. It applies to PowerShell, upload, Euler/Slurm, Python, source/schema validation, rendering, collision QA, retrieval, and local review.

The loop is fail-closed: a failed stage blocks all later stages. A local preflight is evidence, not acceptance. A renderer is canonical only after the complete route succeeds and Jordan accepts the visual result.

## State machine

```text
SPEC_LOCKED
    -> SOURCE_LOCKED
    -> STATIC_PREFLIGHT_PASSED
    -> REAL_METADATA_PREFLIGHT_PASSED
    -> EULER_RENDER_COMPLETED
    -> HARD_QA_PASSED
    -> WINDOWS_RETRIEVED
    -> LOCAL_FILES_VERIFIED
    -> WHITE_PREVIEW_REVIEWED
    -> JORDAN_ACCEPTED
    -> CANONICAL_PROMOTED
```

Any failure moves the run to `FAILED_AT_<STAGE>`. Resume from the failed stage after a minimal patch; do not restart unrelated stages.

## Required loop for every run

### 1. Observe

Capture the exact command, job ID, stdout, stderr, exit code, remote run directory, input paths, and environment. Preserve the failed run and logs.

### 2. Classify

Assign exactly one primary failure class:

- specification or panel identity;
- source path;
- source schema;
- metadata normalization or alias resolution;
- CLI or argument contract;
- dependency or environment;
- Slurm submission or scheduling;
- plotting or serialization;
- collision or visual QA;
- retrieval;
- local verification;
- packaging or user-interface delivery.

Secondary contributing factors may be recorded, but the patch targets the primary failing stage.

### 3. Explain the invariant that was violated

Write the broken contract in one sentence. Examples:

- `upf1Δ` was normalized with an ASCII-only function that deleted `Δ` before classification.
- A visible panel label used a systematic ORF although the common-name-only rule was locked.
- A download instruction named a file that had not been verified in the user's Downloads directory.

### 4. Patch only the failing stage

Do not redesign unrelated panels, add another archive layer, create a new wrapper, or change the biological metric while repairing a parser or path failure. Preserve the original file and record the patch.

### 5. Convert the failure into a regression test

Every proven failure must become at least one executable or machine-checkable guard:

- a static test case;
- a real-table metadata preflight;
- an exact path existence check;
- a schema assertion;
- a required-output assertion;
- a hard rendered-object collision test;
- a retrieval/local-file assertion.

A prose warning alone does not close the loop.

### 6. Run the preflight ladder

In order:

1. PowerShell parser on the exact `.ps1`;
2. `bash -n` on the exact shell or Slurm file;
3. `python3 -m py_compile` on the exact renderer;
4. parser unit cases including Unicode and punctuation variants;
5. real-table unique-label normalization;
6. exact required-column and row/group-count checks;
7. alias/common-name coverage check;
8. renderer CLI inspection;
9. input and output path existence checks.

Do not submit to Slurm until every applicable preflight passes.

### 7. Execute on the target Euler environment

Record:

- Slurm job ID;
- job state and exit code;
- node;
- Python executable/environment;
- actual input paths;
- actual resolved font;
- exact output directory.

`PD (Priority)` is a scheduler wait state, not a code failure. Do not resubmit a valid pending job merely because it has not started.

### 8. Run hard post-draw QA

The final target-environment render must fail when any of these are present:

- clipped text;
- text-text overlap;
- legend-data contact;
- point-label contact;
- missing required objects;
- unexplained visual channels;
- visible systematic identifiers where common names are required;
- NaN labels or cells in a publication panel;
- implausibly unused canvas area;
- missing SVG/PDF/PNG/preview or audit artifacts.

Test the actual Euler-resolved font and at least one expected fallback.

### 9. Retrieve and verify locally

Use direct retrieval unless an archive is demonstrably necessary. Verify every expected file exists and is non-empty before printing success. Open the white preview; never judge transparent PNGs in a black-background viewer.

### 10. Accept or reject

Jordan's visual review is a required acceptance gate. A technically completed run can still be rejected for scientific ambiguity, unreadable axes, poor hierarchy, aesthetic failure, or mismatch to the locked figure architecture.

### 11. Promote only accepted code

- Commit the accepted canonical renderer and exact runner/retrieval tools.
- Do not commit a ladder of failed `v2`, `v3`, `fixed`, or `final-final` scripts.
- Record rejected attempts in one incident document with the exact failure and proven correction.
- Keep systematic identifiers and full statistics in provenance files, not visible panel labels.

### 12. Record the learning

Update:

1. the relevant incident document;
2. this learning loop when a new failure class appears;
3. the project README or canonical-code table;
4. the GitHub handoff log;
5. the Google Drive Action Log.

## Mandatory run ledger

Each material run records this table:

| Field | Value |
|---|---|
| Bible reference | |
| requested figure/panels | |
| authoritative composite/deck | |
| exact metric | |
| allowed subset | |
| forbidden substitutions | |
| renderer SHA-256 | |
| input path and SHA-256 | |
| schema and unique metadata labels | |
| Slurm job ID | |
| final state/exit code | |
| Euler Python/environment | |
| resolved font(s) | |
| remote output directory | |
| hard-QA result | |
| Windows destination | |
| local verification result | |
| white preview reviewed | |
| Jordan acceptance status | |
| GitHub commit | |
| Drive Action Log entry | |

## Promotion rule

A renderer is not canonical because it compiles, submits, or renders. It becomes canonical only after:

```text
real sources verified
+ target Euler execution completed
+ hard QA passed
+ outputs retrieved and verified locally
+ white preview reviewed
+ Jordan accepted the scientific and visual result
```
